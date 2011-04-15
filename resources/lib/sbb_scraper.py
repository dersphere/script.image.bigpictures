import webget
import re
import sys
from BeautifulSoup import BeautifulSoup

scriptName = sys.modules['__main__'].__scriptname__


class SBB:

    def cleanHTML(self, s):
        """The 2nd half of this removes HTML tags.
        The 1st half deals with the fact that beautifulsoup sometimes spits
        out a list of NavigableString objects instead of a regular string.
        This only happens when there are HTML elements, so it made sense to
        fix both problems in the same function."""
        tmp = list()
        for ns in s:
            tmp.append(str(ns))
        s = ''.join(tmp)
        s = re.sub('\s+', ' ', s)  # remove extra spaces
        s = re.sub('<.+?>|Image:.+?\r|\r', '', s)  # remove htmltags, image captions, & newlines
        s = s.replace('&#39;', '\'')  # replace html-encoded double-quotes
        s = s.strip()
        return s

    def getAlbums(self, url):
        """creates an ordered list albums = [{title, pic, description, link}, ...]"""
        tree = BeautifulSoup(webget.getCachedURL(url))
        self.albums = list()
        storyNodes = tree.findAll('div', 'entry-asset asset hentry story')
        for node in storyNodes:
            title = node.find('a').string
            link = node.find('a')['href']
            description = self.cleanHTML(node.find('div', attrs={'style': 'width: 980px; padding: 5px; text-align: left;'}).contents)
            pic = node.find('img')['src']
            self.albums.append({'title': title, 'pic': pic, 'description': description, 'link': link})

    def getPhotos(self, url):
        """creates an ordered list photos = [{title, pic, description}, ...] """
        tree = BeautifulSoup(webget.getCachedUrl(url))
        title = tree.find('div', 'asset-name entry-title title').a.string
        self.photos = list()
        subtree_img = tree.findAll('div', attrs={'style': 'background: rgb(224, 224, 224); width: 982px; padding: 4px;'})
        subtree_txt = tree.findAll('div', attrs={'style': 'background: rgb(224, 224, 224); width: 970px; padding: 10px;'})
        # this is very dirty because this website is very dirty :(
        for i, node_img in enumerate(subtree_img):
            pic = node_img.find('img')['src']
            try:
                description = self.cleanHTML(subtree_txt[i])
            except:
                description = ''
            self.photos.append({'title': title, 'pic': pic, 'description': description})
