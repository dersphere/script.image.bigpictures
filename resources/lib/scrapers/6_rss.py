from scraper import ScraperPlugin
import re

class Scraper(ScraperPlugin):

    NAME = 'RSS Sources'
    
    PIC_REGEX = re.compile('media:content|enclosure')
    DESC_REGEX = re.compile('media:description|description')

    def getAlbums(self):
        rss_list = ('http://www.guardian.co.uk/world/series/eyewitness/rss', 
                    'http://www.stern.de/feed/daily/')
        
        self.albums = list()
        for rss_source in rss_list:
            tree = self.getCachedTree(rss_source)
            title = self.cleanHTML(tree.find('title'))
            link = rss_source
            description = self.cleanHTML(tree.find('description'))
            element_regex = re.compile('media:content|enclosure')
            pic = tree.find('item').findAll(self.PIC_REGEX, {'type': 'image/jpeg'})[-1]['url']
            self.albums.append({'title': title,
                                'pic': pic,
                                'description': description,
                                'link': link})
        return self.albums

    def getPhotos(self, url):
        self.photos = list()
        tree = self.getCachedTree(url)
        rss_title = tree.find('title')
        photoNodes = tree.findAll('item')
        for node in photoNodes:
            item_title = node.find('title')
            title = item_title
            pic = node.findAll(self.PIC_REGEX, {'type': 'image/jpeg'})[-1]['url']
            description = node.find(self.DESC_REGEX).string
            self.photos.append({'title': self.cleanHTML(title),
                                'pic': pic,
                                'description': description})
        return self.photos


def register():
    return Scraper()
