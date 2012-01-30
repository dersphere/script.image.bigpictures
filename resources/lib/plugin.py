from urlparse import parse_qs
import sys
import os

import xbmc
import xbmcgui
import xbmcplugin

handle = int(sys.argv[1])
Addon = sys.modules['__main__'].Addon


def get_sources():
    addon_path = xbmc.translatePath(Addon.getAddonInfo('path'))
    res_path = os.path.join(addon_path, 'resources', 'lib')
    scrapers_path = os.path.join(res_path, 'scrapers')
    scrapers = [f[:-3] for f in os.listdir(scrapers_path) \
                if f.endswith('.py')]
    sys.path.insert(0, res_path)
    sys.path.insert(0, scrapers_path)
    imported_modules = [__import__(scraper) for scraper in scrapers]
    return [m.register() for m in imported_modules]


def get_albums(source_id):
    sources = get_sources()
    source = sources[source_id]
    print source
    albums = source.getAlbums()
    return [{'title': album['title'],
             'pic': album['pic'],
             'id': str(i + 1)} for i, album in enumerate(albums)]


def get_photos(source_id, album_id):
    sources = get_sources()
    source = sources[source_id]
    albums = source.getAlbums()
    album_url = albums[album_id]['link']
    photos = source.getPhotos(album_url)
    return [{'title': str(i + 1),
             'pic': photo['pic']} for i, photo in enumerate(photos)]


def show_albums(source_id):
    albums = get_albums(source_id)
    for album in albums:
        liz = xbmcgui.ListItem(album['title'], iconImage='DefaultImage.png',
                               thumbnailImage=album['pic'])
        liz.setInfo(type='image', infoLabels={'Title': album['title']})
        xbmcplugin.addDirectoryItem(handle=handle, url=album['pic'],
                                    listitem=liz, isFolder=False)


def show_photos(source_id, album_id):
    photos = get_photos(source_id, album_id)
    for photo in photos:
        liz = xbmcgui.ListItem(photo['title'], iconImage='DefaultImage.png',
                               thumbnailImage=photo['pic'])
        liz.setInfo(type='image', infoLabels={'Title': photo['title']})
        xbmcplugin.addDirectoryItem(handle=handle, url=photo['pic'],
                                    listitem=liz, isFolder=False)


def __get_params():
    params = {}
    p = parse_qs(sys.argv[2][1:])
    for key, value in p.iteritems():
        params[key] = value[0]
    return params


def run():
    p = __get_params()
    source_id = int(p['source'])
    if p['mode'] == 'photos':
        album_id = int(p['album'])
        show_photos(source_id, album_id)
    elif p['mode'] == 'albums':
        show_albums(source_id)
    xbmcplugin.endOfDirectory(handle)
