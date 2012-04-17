'''
Created on 2011-6-24

@author: Feng.Zhang
'''
import xml.parsers.expat
class MPEG_TS_Checker_Expat:
    __lastdts = 0
    __lastpts_video = '0'
    __lastpts_audio = '0'
    __lastpcr = '0'
    __lastdtsdelta = 0

    def __check_common(self, name, attrs):
        if (name == "PES_info"):
            if ("PES_packet_length" in attrs.keys()):
                print(attrs["PES_packet_length"])

    def __check_dts_video(self, name, attrs):
        if (name == 'PTS_DTS'):
            if ('DTS' in attrs.keys()):
                if (self.__lastdtsdelta != int(attrs["DTS"]) - int(self.__lastdts)):
                    print("dts delta:"+str(int(attrs["DTS"]) - int (self.__lastdts))+" dts:" + attrs["DTS"])
                self.__lastdtsdelta = int(attrs["DTS"]) - int(self.__lastdts)
                if (self.__lastdts >= int(attrs['DTS'])):
                    print("dts revoled last dts:"+str(self.__lastdts) +"current dts:" + attrs['DTS'])
                self.__lastdts = int(attrs['DTS'])

    def __check_pts_video(self, name, attrs):
        if (name == 'PTS_DTS'):
            if ('PTS' in attrs.keys()):
                print(str(int(attrs['PTS']) - int(self.__lastpts_video)))
                if (int(self.__lastpts_video) >= int(attrs['PTS'])):
                    #pass
                    print(self.__lastpts_video, attrs['PTS'])
                self.__lastpts_video = attrs['PTS']

    def __check_pts_audio(self, name, attrs):
        if (name == 'PTS'):
            if ('DTS' not in attrs.keys()):
                print(str(int(attrs['PTS']) - int(self.__lastpts_audio)))
                if (int(self.__lastpts_audio) >= int(attrs['PTS'])):
                    print(self.__lastpts_audio, attrs['PTS'])
                self.__lastpts_audio = attrs['PTS']

    def __check_pcr(self, name, attrs):
        if (name == "PCR"):
            if (self.__lastpcr>=attrs["PCRBase"]):
                print(self.__lastpcr, attrs["PCRbase"])
            self.__lastpcr = attrs["PCRBase"]

    def check(self, xmlfilepath):
        xmlf = open(xmlfilepath, 'rb')
        print("open file:%s"%(xmlfilepath,))
        parserHandle = xml.parsers.expat.ParserCreate()
        parserHandle.StartElementHandler = self.__check_dts_video
        print("start check dts video")
        parserHandle.ParseFile(xmlf)
        xmlf.close()
        
from xml.etree.ElementTree import ElementTree
class MPEG_TS_Checker_Tree:
    last_counter = 0;
    def __printpacketpos(self, pocket):
        print("pos:", pocket.get("index"))

    def checkcommon(self, strfile):
        xmlfile = open(strfile, "rb")
        if xmlfile == None:
            print(strfile+"File open failed!!!")
            return -1
        parsertree = ElementTree()
        parsertree.parse(xmlfile)
        streamlist =parsertree.findall("stream")
        if (streamlist == None):
            print("No stream Error!!!")
            return -1
        for stream in streamlist:
            streampid = 0
            attstr = stream.keys()
            if ("pid" not in attstr):
                print("stream has not pid attrib")
                return -1
            streampid = int(stream.get("pid"),16)
            if ("total_packet" not in attstr):
                print("there is no total_packet attrib")
                return -1
            streampacknomber = int(stream.get("total_packet"))
            if (streampacknomber == 0):
                print("stream packet number is 0")
                return -1
            packetlist = stream.findall("tspacket")
            if (len(packetlist)!= streampacknomber):
                print("the stream count and the packet number is not the same")
                return -1
            for packet in packetlist:
                attpack = packet.keys()
                currentnum = int(packet.get("continuity_counter"))
                if (currentnum != (self.last_counter+1)%0x10):
                    print("currentnum %d is not eq to last_counter(%d)+1, index:%s, pid:%s"%
                          (currentnum, self.last_counter, packet.get("index"), packet.get("pid")))
                self.last_counter = currentnum
                pass
        return 0

    #check the TS file bitrate base on pts
    '''
    check the ts.xml under such:
    (index*188+offset)*8/(pts-starttime)
    '''
    def checkfile_biterate_pts(self, strfile, reqbitrate, starttime = 0, offset = 0):
        xmlfile = open(strfile, 'rb')
        print("open "+strfile)
        print("check biterate base on pts")
        parsertree = ElementTree()
        parsertree.parse(xmlfile)
        ptsstart = starttime
        streamlist = parsertree.findall("stream")
        for stream in streamlist:
            # print("pid="+stream.get("pid"))
            packets = stream.findall("tspacket")
            for packet in packets:
                tsindex = int(packet.get("index"))
                #if (packet.get("payload_unit_start_indicator") == "true"):
                #    print(packet.get("payload_unit_start_indicator"))
                adapt = packet.find("PES_info")
                if (adapt != None):
                    sepcinfo = adapt.find("stream_special_info")
                    if (sepcinfo != None):
                        pts_dts = sepcinfo.find("PTS_DTS")
                        if (pts_dts != None):
                            ptsvalue = int(pts_dts.get("PTS"))
                            ptsvalue = ptsvalue*1000000/90000
                            print(str(ptsvalue))
                            #if (ptsvalue-ptsstart != 0):
                            #    biterate = (offset+tsindex*188)*8/(ptsvalue-ptsstart)
                            #print(str(biterate)+"\t"+str((biterate-reqbitrate)/reqbitrate))
                            #else:
                            #pts = sepcinfo.find("PTS")
                            #if (pts != None):
                                #ptsvalue = int(pts.get("PTS"))
                                #ptsvalue = ptsvalue/90000
                               # if (ptsvalue-ptsstart != 0):
                                #    biterate = (offset+tsindex*188)*8/(ptsvalue-ptsstart)
                                    #print(str(biterate)+"\t"+str((biterate-reqbitrate)/reqbitrate))


    #check the TS file bitrate
    """
    check the ts.xml file base on:
    (index*188+offset)*8/pcr-pcrstart
    """
    def checkfile_bitrate_pcr(self, strfile, reqbitrate, starttime = 0, offset = 0):
        xmlfile = open(strfile, 'rb')
        print("open "+strfile)
        print("check biterate base on pcr")
        parsertree = ElementTree()
        parsertree.parse(xmlfile)
        filepcrstart = -1
        pcrstart = starttime
        pcrend = 0
        streamlist = parsertree.findall("stream");
        for stream in streamlist:
            packets = stream.findall("tspacket")
            for packet in packets:
                tsindex = int(packet.get("index"))
                adapt = packet.find("tspacketadaptation")
                if (adapt != None):
                    pcr = adapt.find("PCR")
                    if (pcr != None):
                        pcrbase = float(pcr.get("PCRBase"))
                        pcrext = float(pcr.get("PCRExt"))
                        pcri = pcrbase*300+pcrext
                        pcrsec = pcri/27000000
                        pcrend = pcrsec
                        if (filepcrstart == -1):
                            filepcrstart = pcrsec
                        bitrate = (offset+tsindex*188)*8/(pcrsec-pcrstart)
                        print(str(bitrate)+"\t"+str((bitrate-reqbitrate)/reqbitrate))

        print(str(filepcrstart)+"\t"+str(pcrend))
        return pcrend

from xml.dom import minidom
class MPEG_TS_rebuilder:
    '''
    Indent the xml file
    '''
    def __Indent(self, dom, node, indent = 0):
        children = node.childNodes[:]
        if indent:
            text = dom.createTextNode('\n' + '\t' * indent)
            node.parentNode.insertBefore(text, node)
        if children:
            if children[-1].nodeType == node.ELEMENT_NODE:
                text = dom.createTextNode('\n' + '\t' * indent)
                node.appendChild(text)
                for n in children:
                    if n.nodeType == node.ELEMENT_NODE:
                        self.__Indent(dom, n, indent + 1)


    '''
    This function is for rebuild the ts dump file of the tsfiledump.exe
    made xml file, rebuildts
    '''
    def rebuildts(self, inputfile, outputfile):
        parser = minidom.parse(inputfile)
        print("minidom parser has created")
        ##Get the packet raw according to the index
        packetsraw = {}
        for fileinfo in parser.childNodes:
            if fileinfo.nodeType == fileinfo.ELEMENT_NODE:
                print(fileinfo.localName)
                for stream in fileinfo.childNodes:
                    if (stream.nodeType == stream.ELEMENT_NODE):
                        print(stream.localName)
                        for packet in stream.childNodes:
                            if (packet.nodeType == packet.ELEMENT_NODE):
                                packetsraw[int(packet.attributes["index"].value)]=packet
        ##init the output file
        fileout = open(outputfile, "w")
        implout = minidom.DOMImplementation()
        domroot = implout.createDocument(None, "TsStreamRaw", None)
        rootout = domroot.documentElement
        for i in packetsraw:
            ##nextline = domroot.createTextNode("\n")
            ##rootout.appendChild(nextline)
            rootout.appendChild(packetsraw[i])
            ##print(str(i)+str(packetsraw[i]));
        ##print(rootout.toxml())
        self.__Indent(domroot, rootout)
        domroot.writexml(fileout)

if __name__ == "__main__":
    folderpath = "c:\\"
    filenameset = ("test.ts.xml",)
    checktree = MPEG_TS_Checker_Tree()
    checker = MPEG_TS_Checker_Expat()
    #rebuilder = MPEG_TS_rebuilder()
    for filename in filenameset:
        print("check tree:"+filename)
        checktree.checkcommon(folderpath+filename)
        #rebuilder.rebuildts(folderpath+filename, folderpath+filename+"out.xml")
    #checker = MPEG_TS_Checker_Expat()
    for filename in filenameset:
        print("check expat:"+filename)
        checker.check(folderpath+filename);
