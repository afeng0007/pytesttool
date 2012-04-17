'''
Created on 2011-7-1

@author: Feng.Zhang
'''
class M3u8FileInfo:
    EXTM3U = False
    TARGETDURATION = 0
    STARTSEQUENCE = 0

class M3u8Item:
    sequence = 0
    duration = 0
    url = ""
    
class M3u8FileParser:
    
    def isMbr(self):
        return self.__isMbr
    
    def isVod(self):
        return self.__isVod
    
    def getItemCount(self):
        return len(self.__m3u8itemsset)
    
    def getM3u8Item(self, index):
        if (len(self.__m3u8itemsset)<=index):
            return M3u8Item()
        return self.__m3u8itemsset[index]
    
    def parsefile(self, filename):
        file = open(filename,"r")
        templine = str(file.readline())
        self.__m3u8fileinfo = M3u8FileInfo()
        self.__isMbr = False
        self.__isVod = False
        while (not templine.startswith("#EXTINF")) & (not templine.startswith("#EXT-X-STREAM-INF:")):
            templine = templine.rstrip('\r\n')
            if templine.startswith("#EXTM3U"):
                self.__m3u8fileinfo.EXTM3U = True
            if templine.startswith("#EXT-X-TARGETDURATION:"):
                self.__m3u8fileinfo.TARGETDURATION = int(templine[templine.find(':')+1: ])
            if templine.startswith("#EXT-X-MEDIA-SEQUENCE:"):
                self.__m3u8fileinfo.STARTSEQUENCE = int (templine[templine.find(':')+1: ])
            templine = file.readline()
        firstitemduration = self.__m3u8fileinfo.STARTSEQUENCE
        self.__m3u8itemsset=[]
        if templine.startswith("#EXTINF"):
            while templine != "":
                templine = templine.rstrip('\r\n')
                item = M3u8Item()
                item.duration = firstitemduration
                if (templine.startswith("#EXTINF:")):
                    item.duration = int(templine[templine.find(":")+1: templine.find(",")])
                    item.url = file.readline().rstrip("\r\n")
                    if item.url[0] == "#":
                        return False
                if templine.startswith("#EXT-X-DISCONTINUITY"):
                    item.url = "EXT-X-DISCONTINUITY"
                if templine.startswith("#EXT-X-ENDLIST"):
                    item.url = "EXT-X-ENDLIST"
                    self.__isVod = True
                self.__m3u8itemsset.append(item)
                templine = file.readline()
        else:
            if templine.startswith("#EXT-X-STREAM-INF:"):
                self.__isMbr = True
                while templine != "":
                    templine = templine.rstrip("\r\n")
                    item = M3u8Item()
                    item.url = str(file.readline()).rstrip("\r\n")
                    self.__m3u8itemsset.append(item)
                    templine = file.readline()
                pass
        return True