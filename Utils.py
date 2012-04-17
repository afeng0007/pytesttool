'''
Created on 2011-6-24

@author: Feng.Zhang
'''
import os

def appendtsfile(foldername, m3u8file):
    file = open(foldername+"\\"+m3u8file, "r")
    wholefile = open (foldername+"\\"+m3u8file+".ts", "wb")
    tmpline = file.readline()
    while tmpline != "":
        print(tmpline)
        if tmpline[0] != "#":
            tsfile = open(foldername+"\\"+tmpline.rstrip("\n"), "rb")
            wholefile.write(tsfile.read())
            tsfile.close()
        if (tmpline.find("#EXT-X-DISCONTINUITY") != -1):
            break
        tmpline = file.readline()
    wholefile.close()
    file.close()
    
    
def indentxml(dom, node, indent = 0):
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
                    indentxml(dom, n, indent + 1)

def getfilepath(filePath):
    index = filePath.rfind('/')
    if (index != -1):
        return filePath[0:index+1]
    return filePath

def getfilename(filepath):
    index = filepath.rfind('/')
    if (index != -1):
        return filepath[index:]
    return filepath

if __name__ == "__main__":
    foldername = "./playertemp/hls/0/testmedia"
    #appendtsfile(foldername, "playlist_350k.m3u8")
    appendtsfile(foldername, "NHL_720_3000MS.mp4.m3u8")