from scraper import ScraperPlugin


class Scraper(ScraperPlugin):

    NAME = 'RSS Sources'

    def getAlbums(self):
        rss_list = ('http://www.guardian.co.uk/world/series/eyewitness/rss', )
        
        self.albums = list()
        for rss_source in rss_list:
            tree = self.getCachedTree(rss_source)
            print repr(tree)
            title = self.cleanHTML(tree.find('title'))
            link = rss_source
            description = self.cleanHTML(tree.find('description'))
            pic = tree.find('item').findAll('media:content', {'type': 'image/jpeg'})[-1]['url']
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
            pic = node.findAll('media:content', {'type': 'image/jpeg'})[-1]['url']
            description = node.find('media:description').string
            self.photos.append({'title': self.cleanHTML(title),
                                'pic': pic,
                                'description': description})
        return self.photos


def register():
    return Scraper()
