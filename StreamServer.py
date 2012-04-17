'''
Created on 2011-6-24

@author: Feng.Zhang
'''
import http.client
import os.path
import shutil

class Test_StreamServer:
    def getfilepath(self,filePath):
        index = filePath.rfind('/')
        if (index != -1):
            return filePath[0:index+1]
        return filePath
    
    def getfilename(self,filepath):
        index = filepath.rfind('/')
        if (index != -1):
            return filepath[index:]
        return filepath
    
    def setsnapfolder(self, folderpath):
        self.__snapfolder = folderpath
        
    def setadaptivefolder(self, folderpath):
        self.__adaptivefolder = folderpath
        
    def sethlsfolder(self, folderpath):
        self.__hlsfolder = folderpath
        
    def setstarttime(self, yeardatetime):
        paramsc = len(yeardatetime)
        self.__starthour = yeardatetime[0]
        self.__startmin = yeardatetime[1]
        self.__startsec = yeardatetime[2]
        
        if (paramsc == 6):
            year = yeardatetime[3]
            month = yeardatetime[4]
            day = yeardatetime[5]
            self.__liveDatePath = ("%04d%02d%02d"%(year,month, day))
            self.__livestream = True
        else:
            self.__livestream = False
        
    def setendtime(self, yeardatetime):
        paramsc = len(yeardatetime)
        self.__endhour = yeardatetime[0]
        self.__endmin = yeardatetime[1]
        self.__endsec = yeardatetime[2]
        if (paramsc == 6):
            year = yeardatetime[3]
            month = yeardatetime[4]
            day = yeardatetime[5]
            self.__liveDatePath = ("%04d%02d%02d"%(year,month, day))
            self.__livestream = True
        else:
            self.__livestream = False
            
        
    def test_snap(self, server, urlPath):
        con = http.client.HTTPConnection(server)
        sufindex = urlPath.rfind('.mp4')
        prefix = urlPath
        isLiveStream = True
        if (sufindex != -1):
            prefix = urlPath[0:sufindex]
            isLiveStream = False
        if  False == os.path.isdir(self.__snapfolder+urlPath):
            os.makedirs(self.__snapfolder+urlPath)
        for hour in range(self.__starthour, self.__endhour):
            for min in range(self.__startmin, self.__endmin):
                for sec in range(self.__startsec, self.__endsec, 1):
                    reqstring = "%02u%02u%02u.jpg"%(hour, min, sec)
                    if isLiveStream:
                        reqstring = self.__liveDatePath+reqstring
                    print(prefix+"_"+reqstring)
                    con.request("GET", prefix+"_"+reqstring)
                    ren = con.getresponse()
                    if ren.status == 200:
                        file = open(self.__snapfolder+urlPath+"/"+reqstring, 'wb')
                        file.write(ren.read())
                        file.close()
                    else:
                        print ("url:"+prefix+"_"+reqstring+" status:"+str(ren.status))
                        return
                    
    def test_hls_m3u8(self, server, urlPath):
        con = http.client.HTTPConnection(server)
        con.request("GET", urlPath+".m3u8")
        ren = con.getresponse()
        if ren.status == 200:
            file = open(self.__hlsfolder+self.getfilename(urlPath)+".m3u8", 'wb')
            file.write(ren.read())
            file.close()
        else:
            print ("url:"+urlPath+".m3u8"+" status:"+str(ren.status))
            
    def test_sub_hls_m3u8(self, server, mbrurl):
        mbrfile = open(self.__hlsfolder+self.getfilename(mbrurl)+".m3u8", 'r')
        templine = mbrfile.readline()
        ret = []
        while templine != "":
            while templine.find(".m3u8") == -1:
                templine = mbrfile.readline()
                if templine == "":
                    break
            if templine == "":
                break
            templine = templine[0:templine.find(".m3u8")]
            ret.append(templine)
            templine = mbrfile.readline()
        return ret
    
    def test_hls_ts(self, server, urlPath):
        con = http.client.HTTPConnection(server)
        if True != os.path.isdir(self.__hlsfolder):
            os.makedirs(self.__hlsfolder)
        m3u8file = open(self.__hlsfolder+self.getfilename(urlPath)+".m3u8", "r")
        tmpline = m3u8file.readline()
        while tmpline != "":
            while tmpline.find(".ts") == -1:
                tmpline = m3u8file.readline()
                if tmpline == "":
                    break
            if tmpline == "":
                break
            tmpline = tmpline[0:tmpline.find("\n")]
            con.request("GET", self.getfilepath(urlPath)+tmpline)
            ren = con.getresponse();
            if ren.status == 200:
                file = open(self.__hlsfolder+tmpline, 'wb')
                file.write(ren.read())
                file.close()
            else:
                print ("Url:"+self.getfilepath(urlPath)+tmpline+" status:"+str(ren.status))
                break
            tmpline = m3u8file.readline()
            
    def test_adaptive_meta(self, server, urlPath):
        con = http.client.HTTPConnection(server)
        con.request("GET", "/play?url="+urlPath)
        ren = con.getresponse();
        if ren.status == 200:
            metafile = open(self.__adaptivefolder+self.getfilename(urlPath)+".meta", "wb")
            metafile.write(ren.read())
            metafile.close()
        else:
            print(ren.status)

    def test_adaptive_block(self, server, urlPath):
        con = http.client.HTTPConnection(server)
        for hour in range(self.__starthour, self.__endhour):
            for min in range(self.__startmin, self.__endmin):
                for sec in range(self.__startsec, self.__endsec, 2):
                    datetime = "/%02u/"%(hour)
                    if (urlPath.find(".mp4") == -1):
                        datetime = "/"+self.__liveDatePath+datetime
                    foldpath = urlPath+datetime
                    filename = "%02u%02u.mp4"%(min, sec)
                    if True != os.path.isdir(self.__adaptivefolder+foldpath):
                        os.makedirs(self.__adaptivefolder+foldpath)
                    con.request("GET", foldpath+filename)
                    ren = con.getresponse()
                    if ren.status == 200:
                        blockfile = open(self.__adaptivefolder+foldpath+"%02u%02u.mp4"%(min, sec), "wb")
                        blockfile.write(ren.read())
                        blockfile.close()
                    else:
                        print("Url:"+foldpath+filename+" status:"+str(ren.status))
                        return

    def reset(self):
        if os.path.isdir(self.__adaptivefolder):
            shutil.rmtree(self.__adaptivefolder)
        os.makedirs(self.__adaptivefolder)
        if os.path.isdir(self.__hlsfolder):
            shutil.rmtree(self.__hlsfolder)
        os.makedirs(self.__hlsfolder)
        if os.path.isdir(self.__snapfolder):
            shutil.rmtree(self.__snapfolder)
        os.makedirs(self.__snapfolder)
        
        
