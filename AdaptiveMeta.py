'''
Created on 2011-6-24

@author: Feng.Zhang
'''
from xml.etree.ElementTree import ElementTree

class Range:
    start = 0
    end = 0

class VideoInfo:
    width = 0
    height = 0
    fps = 0.0
    
class AudioInfo:
    channelCounter = 0
    samplerate = 0
    samplebitsize = 0

class AdaptiveMetaInfo:
    url = ""
    blockduration = 0
    livedvrdutation = 0
    videoinfo = VideoInfo()
    audioinfo = AudioInfo()
    ranges = []
    
class AdaptiveMeta_Parser:
    
    
    def parsefile(self, filename):
        self.__streamdata = []
        self.__defaultStreamIndex = ""
        self.__currentdis = ""
        self.__currenttime = 0
        
        print("open file %s"%(filename,))
        filefd = open(filename, "rb")
        elementtree = ElementTree()
        elementtree.parse(filefd)
        channel = elementtree.getroot()
        chkeys = channel.keys()
        if "currentTime" in chkeys:
            self.__currenttime = int(channel.get("currentTime"))
        if "currentTimeDescription" in chkeys:
            self.__currentdis = channel.get("currentTimeDescription")
        if "defaultStreamIndex" in chkeys:
            self.__defaultStreamIndex = channel.get("defaultStreamIndex")
            streamdatases = channel.findall("streamDatas")
            for streamdatas in streamdatases:
                streamDs = streamdatas.findall("streamData")
                for stream in streamDs:
                    metainfo = AdaptiveMetaInfo()
                    streamkeys = stream.keys()
                    if "url" in streamkeys:
                        metainfo.url = stream.get("url")
                    if "blockDuration" in streamkeys:
                        metainfo.blockduration = int(stream.get("blockDuration"))
                    if "liveDVRDuration" in streamkeys:
                        metainfo.livedvrdutation = int(stream.get("liveDVRDuration"))
                    videoinfo = stream.find("video")
                    videokeys = videoinfo.keys()
                    if "width" in videokeys:
                        metainfo.videoinfo.width = int(videoinfo.get("width"))
                    if "height" in videokeys:
                        metainfo.videoinfo.height = int(videoinfo.get("height"))
                    if "fps" in videokeys:
                        metainfo.videoinfo.fps = float(videoinfo.get("fps"))
                    audioinfo = stream.find("audio")
                    audiokeys = audioinfo.keys()
                    if "channelCount" in audiokeys:
                        metainfo.audioinfo.channelCounter = int(audioinfo.get("channelCount"))
                    if "samplesRate" in audiokeys:
                        metainfo.audioinfo.samplerate = int(audioinfo.get("samplesRate"))
                    if "sampleBitSize" in audiokeys:
                        metainfo.audioinfo.samplebitsize = int(audioinfo.get("sampleBitSize"))
                    rangestag = stream.find("ranges")
                    ranges = rangestag.findall("range")
                    for range in ranges:
                        rangemeta = Range()
                        if "begin" in range.keys():
                            rangemeta.start = range.get("begin")
                        if "end" in range.keys():
                            rangemeta.end = range.get("end")
                        metainfo.ranges.append(rangemeta)
                    self.__streamdata.append(metainfo)

    def getcurrenttime(self):
        return int(self.__currenttime)
    
    def getstreamdata(self):
        return self.__streamdata
                    
        
        
        