import webget
import re
import sys
from BeautifulSoup import BeautifulSoup

scriptName = sys.modules['__main__'].__scriptname__


class WSJ:

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
        s = s.replace('&#8217;', '\'')  # replace html-encoded single-quotes
        s = s.replace('&#8221;', '"')  # replace html-encoded double-quotes
        s = s.strip()
        return s

    def getAlbums(self, url):
        """creates an ordered list albums = [{title, pic, description, link}, ...]"""
        tree = BeautifulSoup(webget.getCachedURL(url))
        self.albums = list()
        storyNodes = tree.findAll('li', 'postitem imageFormat-P')
        for node in storyNodes:
            title = self.cleanHTML(node.find('h2').a.string)
            link = node.find('h2').a['href']
            description = self.cleanHTML(node.findAll('div', attrs={'class': 'postContent'})[1].p)
            pic = node.find('img')['src'].strip()
            self.albums.append({'title': title, 'pic': pic, 'description': description, 'link': link})

    def getPhotos(self, url, append=False):
        """creates an ordered list photos = [{title, pic, description}, ...] """
        tree = BeautifulSoup(webget.getCachedUrl(url))
        title = tree.find('div', 'articleHeadlineBox headlineType-newswire').h1.string
        if not append:
            self.photos = list()
        subtree = tree.find('div', {'class': 'articlePage'})
        subtree.extract()
        photoNodes = subtree.findAll('p')
        for node in photoNodes:
            pic = node.img['src'].strip()
            description = self.cleanHTML(node.contents)
            self.photos.append({'title': title, 'pic': pic, 'description': description})
        if tree.find('a', 'nav_next'):
            self.getPhotos(tree.find('a', 'nav_next')['href'], append=True)
