'''
Created on 2011-7-1

@author: Feng.Zhang
'''
import sys
import os
import http.client
import M3u8FileReader
import Utils
import threading
import time

class HlsplayerDownloader:
    __stopped = False
    __lock = threading.Lock()
    __subThread = []
    downloadfilepath = "./playertemp/hls/"

    def downloadHttpFile(self, server, url):
        print("server:%s, url:%s"%(server,url))
        self.__lock.acquire()
        self.__connect.request("GET", url)
        res = self.__connect.getresponse()
        filelocalname = self.downloadfilepath+url
        if not os.path.isdir(Utils.getfilepath(filelocalname)):
            os.makedirs(Utils.getfilepath(filelocalname))
        if 200 == res.status:
            m3u8file = open(filelocalname, "wb")
            m3u8file.write(res.read())
            m3u8file.close()
        else:
            print("status code:%d, url:%s"%(res.status, url))
        self.__connect.close()
        self.__lock.release()

    def downloadM3u8Proc(self, url, internal):
        while not self.__stopped:
            self.downloadHttpFile(self.__server, url)
            time.sleep(internal)

    def downloadTsFileProc(self, url, internal):
        while not self.__stopped:
            localfilename = self.downloadfilepath+url
            m3u8parser = M3u8FileReader.M3u8FileParser()
            m3u8parser.parsefile(localfilename)
            counter = m3u8parser.getItemCount()
            if counter>1:
                suburl = m3u8parser.getM3u8Item(counter-1).url;
                if (suburl[0] == '/'):
                    pass
                else:
                    if (suburl.startswith("http")):
                        pass
                    else:
                        suburl = Utils.getfilepath(url)+suburl
                self.downloadHttpFile(self.__server, suburl)
            time.sleep(internal)

    def start(self, server, url, bVodMode):
        """
        init the class private variable
        """
        self.__server = server;
        self.__url = url;
        self.__stopped = False;
        
        #get the u3m8 file
        localurlname = self.downloadfilepath+url;
        self.__lock.acquire()
        self.__connect = http.client.HTTPConnection(server)
        self.__connect.request("GET", self.__url)
        res = self.__connect.getresponse()
        if 200 == res.status:
            if not os.path.isdir(Utils.getfilepath(localurlname)):
                os.makedirs(Utils.getfilepath(localurlname))
            m3u8file = open(localurlname, "wb")
            m3u8file.write(res.read())
            m3u8file.close()
            self.__connect.close()
            self.__lock.release()
        else:
            print("return status is :%d, url is %s"%(res.status, self.__url))
            self.__connect.close()
            self.__lock.release()
            return
        self.__m3u8parser = M3u8FileReader.M3u8FileParser()
        if not self.__m3u8parser.parsefile(localurlname):
            return False

        index = 0
        count = self.__m3u8parser.getItemCount()
        filepath = Utils.getfilepath(self.__url)
        if self.__m3u8parser.isMbr():
            while index < count:
                m3u8item = self.__m3u8parser.getM3u8Item(index)
                downloadurl = m3u8item.url;
                startindex = m3u8item.url.find("://")
                if  startindex < 0:
                    if not m3u8item.url.startswith("/"):
                        downloadurl = Utils.getfilepath(self.__url)+m3u8item.url
                else:
                    downloadurl = downloadurl[startindex+3:]
                    startindex = downloadurl.find("/")
                    downloadurl = downloadurl[startindex:]

                if (downloadurl.endswith(".mp4.m3u8") or bVodMode):
                    self.downloadHttpFile(self.__server, downloadurl)
                    m3u8parser = M3u8FileReader.M3u8FileParser()
                    m3u8parser.parsefile(self.downloadfilepath+downloadurl)
                    tsindex = 0
                    tsfilecounter = m3u8parser.getItemCount()
                    while tsindex < tsfilecounter:
                        self.downloadHttpFile(self.__server, Utils.getfilepath(downloadurl)+m3u8parser.getM3u8Item(tsindex).url)
                        tsindex+=1
                else:
                    self.downloadHttpFile(self.__server, downloadurl)
                    m3u8thread = threading.Thread(group = None, target = self.downloadM3u8Proc, name = None, args = (downloadurl,10))
                    self.__subThread.append(m3u8thread)
                    m3u8thread.start()
                    tsthread = threading.Thread(group = None, target = self.downloadTsFileProc, name = None, args = (downloadurl,10))
                    self.__subThread.append(tsthread)
                    tsthread.start()
                index+=1
        else:
            if self.__m3u8parser.isVod() or bVodMode:
                while index<count:
                    m3u8item = self.__m3u8parser.getM3u8Item(index)
                    suburl = filepath+m3u8item.url
                    self.downloadHttpFile(self.__server, suburl)
                    index+=1
            else:
                m3u8update = threading.Thread(group = None, target = self.downloadM3u8Proc, name = None, args = (url, 10))
                self.__subThread.append(m3u8update)
                m3u8update.start()
                m3u8thread = threading.Thread(group = None, target = self.downloadTsFileProc, name = None, args = (url, 10))
                self.__subThread.append(m3u8thread)
                m3u8thread.start()

    def stop(self):
        self.__stopped = True

    def isStoped(self):
        return self.__stopped

if __name__=="__main__":
    player = HlsplayerDownloader()

    """
    replace the server and url with the streamserver request
    """
    server = "172.16.0.188:8300"
    url = "/s1/live/csl/2011/demo_pc.m3u8"
    bvodmode = False
    argc = len(sys.argv)
    if argc ==3:
        server = sys.argv[1]
        url = sys.argv[2]

    suffix=0
    while (os.path.isdir(player.downloadfilepath+"/"+str(suffix)+"/")):
        suffix+=1
    player.downloadfilepath+="/"+str(suffix)+"/"
    player.start(server, url, bvodmode)
    while player.isStoped():
        time.sleep(2)
