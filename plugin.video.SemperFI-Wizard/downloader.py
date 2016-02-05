import xbmcgui
import urllib


class aresdownload(urllib.FancyURLopener):
    version = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11'



def download(url, dest, dp = None):

	if url.find('ares1') == -1:

		if not dp:
			dp = xbmcgui.DialogProgress()
			dp.create("Please Wait..","Downloading & Copying File",' ', ' ')
		dp.update(0)
		urllib.urlretrieve(url,dest,lambda nb, bs, fs, url=url: _pbhook(nb,bs,fs,url,dp))
		
	else:
	
		if not dp:
			dp = xbmcgui.DialogProgress()
			dp.create("Please Wait..","Downloading & Copying File",' ', ' ')
		dp.update(0)
		aresdownload().retrieve(url,dest,lambda nb, bs, fs, url=url: _pbhook(nb,bs,fs,url,dp))
		
 
def _pbhook(numblocks, blocksize, filesize, url, dp):
    try:
        percent = min((numblocks*blocksize*100)/filesize, 100)
        dp.update(percent)
    except:
        percent = 100
        dp.update(percent)
    if dp.iscanceled(): 
        raise Exception("Canceled")
        dp.close()