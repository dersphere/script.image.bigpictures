import tbp_scraper
import sbb_scraper
import wsj_scraper
import xbmcgui
import os
import imageDownloader
import xbmcaddon
from xbmc import sleep

_id = os.path.basename(os.getcwd())
Addon = xbmcaddon.Addon(_id)
#enable localization
getLS = Addon.getLocalizedString


class GUI(xbmcgui.WindowXML):
    #Label Controls
    CONTROL_MAIN_IMAGE = 100
    CONTROL_USAGE_TEXT = 3
    #Label Actions
    ACTION_CONTEXT_MENU = [117]
    ACTION_MENU = [122]
    ACTION_PREVIOUS_MENU = [9]
    ACTION_SHOW_INFO = [11]
    ACTION_EXIT_SCRIPT = [10, 13]
    ACTION_DOWN = [4]
    ACTION_UP = [3]

    ACTIVESOURCE = 0
    
    SOURCES = list()
    SOURCES.append({'name': 'Boston.com: The Big Picture', 'object': 'tbp', 'url': 'http://www.boston.com/bigpicture/'})
    SOURCES.append({'name': 'Boston.com: The Big Shot', 'object': 'tbp', 'url': 'http://www.boston.com/sports/blogs/bigshots/'})
    SOURCES.append({'name': 'Sacramento Bee: The Frame', 'object': 'sbb', 'url': 'http://blogs.sacbee.com/photos/'})
    SOURCES.append({'name': 'Wallstreetjournal: The Photo Journal', 'object': 'wsj', 'url': 'http://blogs.wsj.com/photojournal/'})

    def __init__(self, *args, **kwargs):
        xbmcgui.WindowXML.__init__(self, *args, **kwargs)
        self.tbp = tbp_scraper.TBP()
        self.sbb = sbb_scraper.SBB()
        self.wsj = wsj_scraper.WSJ()

    def onInit(self):
        self.getControl(2).setLabel(getLS(32001)) #fixme
        self.showAlbums()

    def onFocus(self, controlId):
        pass

    def onAction(self, action):
        if action in self.ACTION_SHOW_INFO:
            self.toggleInfo()
        elif action in self.ACTION_CONTEXT_MENU:
            self.download()
        elif action in self.ACTION_PREVIOUS_MENU:
            # exit the script
            if self.getProperty('type') == 'album':
                self.close()
            # return to previous album
            elif self.getProperty('type') == 'photo':
                self.showAlbums()
        elif action in self.ACTION_EXIT_SCRIPT:
            self.close()
        elif action in self.ACTION_DOWN and self.getProperty('type') == 'album':
            if len(self.SOURCES) > self.ACTIVESOURCE + 1:
                self.ACTIVESOURCE += 1
            else:
                self.ACTIVESOURCE = 0
            self.showAlbums()
        elif action in self.ACTION_UP and self.getProperty('type') == 'album':
            if self.ACTIVESOURCE == 0:
                self.ACTIVESOURCE = len(self.SOURCES) -1
            else:
                self.ACTIVESOURCE -= 1
            self.showAlbums()

    def onClick(self, controlId):
        if controlId == self.CONTROL_MAIN_IMAGE:
            if self.getProperty('type') == 'album':
                self.showPhotos()
            elif self.getProperty('type') == 'photo':
                self.toggleInfo()

    def getProperty(self, property, controlId=CONTROL_MAIN_IMAGE):
        """Returns a property of the selected item"""
        return self.getControl(controlId).getSelectedItem().getProperty(property)

    def toggleInfo(self):
        selectedControl = self.getControl(self.CONTROL_MAIN_IMAGE)
        if self.getProperty('showInfo') == 'false':
            for i in range(selectedControl.size()):
                selectedControl.getListItem(i).setProperty('showInfo', 'true')
                self.getControl(self.CONTROL_USAGE_TEXT).setVisible(True)
        else:
            for i in range(selectedControl.size()):
                selectedControl.getListItem(i).setProperty('showInfo', 'false')
                self.getControl(self.CONTROL_USAGE_TEXT).setVisible(False)

    def download(self):
        #get writable directory
        if self.getProperty('type') == 'photo':
            downloadPath = xbmcgui.Dialog().browse(3, ' '.join([getLS(32020), getLS(32021)]), 'pictures')
            if downloadPath:
                photos = [{'pic':self.getProperty('pic')}] #url needs to be passed as a dict in a list.
                imageDownloader.Download(photos, downloadPath) 
        elif self.getProperty('type') == 'album':
            downloadPath = xbmcgui.Dialog().browse(3, ' '.join([getLS(32020), getLS(32022)]), 'pictures')
            if downloadPath:
                pDialog = xbmcgui.DialogProgress() #show useless dialog so user knows something is happening.
                pDialog.create(self.SOURCES[self.ACTIVESOURCE]['name'])
                pDialog.update(50)
                if self.SOURCES[self.ACTIVESOURCE]['object'] == 'tbp':
                    self.tbp.getPhotos(self.SOURCES[self.ACTIVESOURCE]['url']) # Get a list of photos from the link.
                    photos = self.tbp.photos
                elif self.SOURCES[self.ACTIVESOURCE]['object'] == 'sbb':
                    self.sbb.getPhotos(self.SOURCES[self.ACTIVESOURCE]['url'])
                    photos = self.sbb.photos
                elif self.SOURCES[self.ACTIVESOURCE]['object'] == 'wsj':
                    self.wsj.getPhotos(self.SOURCES[self.ACTIVESOURCE]['url'])
                    photos = self.wsj.photos
                else:
                    pass
                pDialog.update(100)
                pDialog.close()
                imageDownloader.Download(photos, downloadPath)

    def showPhotos(self): #the order is significant!
        self.getControl(self.CONTROL_USAGE_TEXT).setText('\n'.join([getLS(32030), getLS(32031), getLS(32032)]))
        link = self.getProperty('link')
        self.getControl(self.CONTROL_MAIN_IMAGE).reset() #Clear the old list of albums.
        if self.SOURCES[self.ACTIVESOURCE]['object'] == 'tbp':
            self.tbp.getPhotos(link) # Get a list of photos from the link.
            photos = self.tbp.photos
        elif self.SOURCES[self.ACTIVESOURCE]['object'] == 'sbb':
            self.sbb.getPhotos(link)
            photos = self.sbb.photos
        elif self.SOURCES[self.ACTIVESOURCE]['object'] == 'wsj':
            self.wsj.getPhotos(link)
            photos = self.wsj.photos
        else:
            pass
        self.showItems(photos, 'photo')

    def showAlbums(self):
        self.getControl(self.CONTROL_USAGE_TEXT).setText('\n'.join([getLS(32040), getLS(32041), getLS(32042)]))
        self.getControl(self.CONTROL_MAIN_IMAGE).reset() #This is necessary when returning from photos.
        if self.SOURCES[self.ACTIVESOURCE]['object'] == 'tbp':
            self.tbp.getAlbums(self.SOURCES[self.ACTIVESOURCE]['url'])
            albums = self.tbp.albums
        elif self.SOURCES[self.ACTIVESOURCE]['object'] == 'sbb':
            self.sbb.getAlbums(self.SOURCES[self.ACTIVESOURCE]['url'])
            albums = self.sbb.albums
        elif self.SOURCES[self.ACTIVESOURCE]['object'] == 'wsj':
            self.wsj.getAlbums(self.SOURCES[self.ACTIVESOURCE]['url'])
            albums = self.wsj.albums
        else:
            pass
        self.showItems(albums, 'album')

    def showItems(self, itemSet, type):
        total = len(itemSet)
        for i, item in enumerate(itemSet):
            item['showInfo'] = 'true'
            item['type'] = type
            item['title'] = self.SOURCES[self.ACTIVESOURCE]['name'] + '\n' + item['title'] + ' (%s/%s)' % (i+1, total)
            self.addListItem(self.CONTROL_MAIN_IMAGE, item)

    def addListItem(self, controlId, properties):
        li = xbmcgui.ListItem(label=properties['title'], label2=properties['description'], iconImage=properties['pic'])
        for p in properties.keys():
            li.setProperty(p, properties[p])
        self.getControl(controlId).addItem(li)
