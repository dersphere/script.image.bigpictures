import webget
import re
import sys
from BeautifulSoup import BeautifulSoup

scriptName = sys.modules['__main__'].__scriptname__


class TBP:

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
        s = re.sub('#$', '', s)  # remove hash at the end
        s = s.strip()
        return s

    def getFilters(self, url):
        """TBP lets you filter results by categories or months.
        creatues a list of those filters: [[month|category,url], ...]"""
        tree = BeautifulSoup(webget.getCachedURL(url))
        self.months = list()
        self.categories = list()
        optionNodes = tree.findAll('option', value=re.compile('.+?'))
        for node in optionNodes:
            if node.parent.option.contents[0] == 'Select a month':
                self.months.append([node.string, node['value']])
            elif node.parent.option.contents[0] == 'Select a category':
                self.categories.append([node.string, node['value']])

    def getAlbums(self, url):
        """creates an ordered list albums = [{title, pic, description, link}, ...]"""
        tree = BeautifulSoup(webget.getCachedURL(url))
        self.albums = list()
        storyNodes = tree.findAll('div', 'headDiv2')
        for node in storyNodes:
            title = node.find('a').string
            link = node.find('a')['href']
            description = self.cleanHTML(node.find('div', attrs={'class': 'bpBody'}).contents)
            pic = node.find('img')['src']
            self.albums.append({'title': title, 'pic': pic, 'description': description, 'link': link})

    def getPhotos(self, url):
        """creates an ordered list photos = [{title, pic, description}, ...] """
        referer = 'http://www.boston.com/bigpicture/'
        tree = BeautifulSoup(webget.getCachedURL(url, referer))
        title = tree.find('div', 'headDiv2').h2.a.string
        self.photos = list()
        photoNodes = tree.findAll('div', {'class': re.compile('bpImageTop|bpBoth')})
        for node in photoNodes:
            pic = node.img['src']
            if node.find('div', 'photoNum'):
                node.find('div', 'photoNum').replaceWith('')
            description = self.cleanHTML(node.find('div', 'bpCaption').contents)
            self.photos.append({'title': title, 'pic': pic, 'description': description})
