'''
Created on 2011-6-24

@author: Feng.Zhang
'''
import StreamServer

def TestStreamServer_Main(islive, ismbr):
    server = "172.16.0.188:8300"
    vodmbrset = ("/vod/NHL_360.mp4",)
    
    vodurlset = ("/vod/android_400x224_amf.mp4", 
                 "/vod/BigBuckBunny_320x180_500.mp4", 
                "/vod/MLS_800.mp4",
                "/vod/MLS_3000_a.mp4",
                "/vod/nhl_demo_cable_450.mp4",
                "/vod/pc_800.mp4_amf.mp4",
                "/vod/weather_2500_1000.MP4"
                "/vod/zz_test_1000.MP4"
                "/vod/MLS_3000.mp4"
		 )
    liveurlset = (#"/live/nlds/u/live/as_400/nhl_400",
                  #"/live/nlds/u/live/as_800/nhl_800", 
                  "/nlds/u/live/weather/weather_1200", 
                  #"/nlds/u/live/audio/audioonly_128", 
                  #"live/nlds/u/weather_800/weather_800"
				)
    livembrset = ("/live/nlds/u/live/as/a_simul_stream",)
    testcase = StreamServer.Test_StreamServer()
    testcase.setadaptivefolder("./Test_Handler/testAdaptive/")
    testcase.sethlsfolder("./Test_Handler/testHls/")
    testcase.setsnapfolder("./Test_Handler/testSnap/")
    testcase.reset()
    if islive:
        if ismbr:
            urlset = livembrset
        else:
            urlset = liveurlset
        testcase.setstarttime((1,0,0, 2011, 9, 7))
        testcase.setendtime((24,60,60, 2011, 9, 7))
    else:
        if ismbr:
            urlset = vodmbrset
        else:
            urlset = vodurlset
        testcase.setstarttime((0,0,0))
        testcase.setendtime((24,60,60))
        
    for url in urlset:
        testcase.test_hls_m3u8(server, url)
        #if (ismbr):
        #    suburls = testcase.test_sub_hls_m3u8(server, url)
        #    for suburl in suburls:
        #        testcase.test_hls_m3u8(server, suburl)
        #        testcase.test_hls_ts(server, suburl)
        #else:
        testcase.test_hls_ts(server, url)       
        #testcase.test_adaptive_meta(server, url)
        #testcase.test_adaptive_block(server, url)
        #testcase.test_snap(server, url)

if __name__ == "__main__":
    #TestStreamServer_Main(False, False)
    TestStreamServer_Main(False, False)
    pass
