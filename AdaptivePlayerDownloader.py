'''
Created on 2011-6-27

@author: Feng.Zhang
'''
import threading
import os
import http.client
import AdaptiveMeta
import time
import Utils
import sys
class AdaptiveDownload:
    __stopped = True
    __lock = threading.Lock()
    __downloadthreads = []
    __metaurl = []
    downloadfilepath = "./playertemp/adaptive/"

    def __fromUtcToStr(self, currenttime):
        curtime = time.gmtime(currenttime)
        return "/%04d%02d%02d/%02d/%02d%02d.mp4"%(curtime.tm_year, curtime.tm_mon, curtime.tm_mday,\
                                                  curtime.tm_hour, curtime.tm_min, curtime.tm_sec)

    def __updateMeta(self, metaurl):
        self.__lock.acquire()
        self.__connect.request("GET", metaurl)
        ren = self.__connect.getresponse()
        if ren.status == 200:
            print("download metaurl "+metaurl+" OK")
            filewriter = open(self.downloadfilepath+Utils.getfilename(metaurl)+".meta", 'wb')
            filewriter.write(ren.read())
            filewriter.close()
        self.__connect.close()
        self.__lock.release()

    def __downloadblock(self, url):
        self.__lock.acquire()
        self.__metaparser.parsefile(self.downloadfilepath+Utils.getfilename(url)+'.meta');
        print(str(self.__metaparser.getcurrenttime()))
        localurl = self.__fromUtcToStr(self.__metaparser.getcurrenttime()/1000)
        blockurl = url+localurl
        blockpath = self.downloadfilepath+Utils.getfilename(url)+localurl
        localpath = self.downloadfilepath+Utils.getfilename(url)+Utils.getfilepath(localurl)
        if (False == os.path.isdir(localpath)):
            os.makedirs(localpath)
        #self.__connect.request("GET", blockurl)
        self.__connect.request("GET", blockurl, headers={"Range": "bytes=10-",})
        ren = self.__connect.getresponse()
        if ren.status == 200:
            if False == os.path.isfile(blockpath):
                filewriter = open(blockpath, 'wb')
                filewriter.write(ren.read())
                filewriter.close()
        self.__connect.close()
        self.__lock.release()

    def ontimerproc(self):
        while(False == self.__stopped):
            print("meta download thread")
            for url in self.__metaurl:
                self.__updateMeta(url)
            time.sleep(2)
        pass

    def onthreaddownload(self, url, blockdursec):
        while(False == self.__stopped):
            self.__downloadblock(url)
            time.sleep(blockdursec)
        pass

    def start(self, server, url):
        """
        init the params
        """
        metaurl = "/play?url="+url
        self.__server = server
        self.__metaurl.append(metaurl)
        self.__stopped = False
        self.__metaparser = AdaptiveMeta.AdaptiveMeta_Parser()
        if False == os.path.isdir(self.downloadfilepath):
            os.makedirs(self.downloadfilepath)
        self.__connect = http.client.HTTPConnection(server)
        self.__connect.request("GET", metaurl)
        respon = self.__connect.getresponse()
        if respon.status == 200:
            metafile = open(self.downloadfilepath+Utils.getfilename(url)+".meta", "wb")
            metafile.write(respon.read())
            metafile.close()
            self.__connect.close()
        else:
            self.__connect.close()
            return
        self.__metaparser.parsefile(self.downloadfilepath+Utils.getfilename(url)+".meta");
        streamdatas = self.__metaparser.getstreamdata()
        if len(streamdatas) > 1:
            del self.__metaurl[:]
        for stream in streamdatas:
            metaurl = "/play?url="+stream.url;
            self.__updateMeta(metaurl)
            self.__metaurl.append(metaurl)
            thread = threading.Thread(group=None, target = self.onthreaddownload, args=(stream.url,stream.blockduration/1000))
            self.__downloadthreads.append(thread)
            thread.start()

        self.__timer = threading.Thread(group=None, target = self.ontimerproc)
        self.__timer.start()

    def stop(self):
        self.__stopped = True
        pass

    def isstopped(self):
        return self.__stopped

#argv[1] = "172.16.1.39:8080"
#argv[2] = "/live/as_400/nhl_400"
if __name__ == "__main__":
    player = AdaptiveDownload()
    argv1 = "172.16.1.154:8300"
    argv2 = "/nlds/u/live/as/a_simul_stream_1600"
    suffix = 1
    while (os.path.isdir(player.downloadfilepath+"/"+str(suffix)+"/")):
        suffix+=1
    player.downloadfilepath+="/"+str(suffix)+"/"
    if (sys.argv.count == 3):
        argv1 = sys.argv[1]
        argv2 = sys.argv[2]

    player.start(argv1, argv2)
    while False == player.isstopped():
        time.sleep(2)
