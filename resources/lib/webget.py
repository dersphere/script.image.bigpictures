import urllib2
import os
import sys
import time
from zlib import crc32

scriptname = sys.modules['__main__'].__scriptname__
cachedir = sys.modules['__main__'].__cachedir__

def getCachedURL(url, referer=None):
    print '[SCRIPT][%s] attempting to open %s' % (scriptname, url)
    headers = [('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:2.0) Gecko/20100101 Firefox/4.0')]
    if referer:
        headers.append(('Referer', referer))
    filename = str(crc32(url))
    cachefilefullpath = cachedir + filename
    timetolive = 3600
    if (not os.path.isdir(cachedir)):
        os.makedirs(cachedir)
    try: cachefiledate = os.path.getmtime(cachefilefullpath)
    except: cachefiledate = 0
    cachefiledate = 0
    if (time.time() - (timetolive)) > cachefiledate:
        try:
            print '[SCRIPT][%s] %s retrieved from web' % (scriptname, url)
            opener = urllib2.build_opener()
            opener.addheaders = headers
            sock = opener.open(url)
            link = sock.read()
            outfile = open(cachefilefullpath, 'w')
            outfile.write(link)
            outfile.close()
        except urllib2.HTTPError, error:
            print '[SCRIPT][%s] error opening %s' % (scriptname, url)
            print error.msg, error.code, error.geturl() 
    else:
        print '[SCRIPT][%s] %s retrieved from cache' % (scriptname, url)
        sock = open(cachefilefullpath, 'r')
        link = sock.read()
    sock.close()
    return link
