import tbp_scraper
import xbmcgui
import os
import imageDownloader
import xbmcaddon
from xbmc import sleep

_id = os.path.basename(os.getcwd())
Addon = xbmcaddon.Addon(_id)
#enable localization
getLS = Addon.getLocalizedString

sites = list()
sites.append({'title': 'Boston.com The Big Pictures',
              'pic': 'http://cache.boston.com/universal/site_graphics/blogs/bigpicture/bp_header_e.jpg',
              'description': 'News Stories in photograps',
              'link': 'http://www.boston.com/bigpicture/',
              'source': 'boston_com'})
sites.append({'title': 'Boston.com Big Shots',
              'pic': 'http://graphics.boston.com/universal/site_graphics/blogs/bigpicture/bigShots.gif',
              'description': 'The best sports photograpy of the week',
              'link': 'http://www.boston.com/sports/blogs/bigshots/',
              'source': 'boston_com'})

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

    def __init__(self, *args, **kwargs):
        xbmcgui.WindowXML.__init__(self, *args, **kwargs)
        self.boston_com = tbp_scraper.BOSTON_COM()

    def onInit(self):
        self.getControl(1).setLabel(getLS(32000))
        self.getControl(2).setLabel(getLS(32001))
        self.getControl(self.CONTROL_USAGE_TEXT).setText('\n'.join([getLS(32030), getLS(32031)]))
        self.showSites()
        
    def onFocus(self, controlId):
        pass

    def onAction(self, action):
        if action in self.ACTION_SHOW_INFO:
            self.toggleInfo()
        elif action in self.ACTION_CONTEXT_MENU:
            self.download()
        elif action in self.ACTION_PREVIOUS_MENU:
            # exit the script
            if self.getProperty('type') == 'site':
                self.close()
            # return to sites view
            elif self.getProperty('type') == 'album':
                self.showSites()
            # return to album view
            elif self.getProperty('type') == 'photo':
                self.showSites() #fixme, return from where you come from
        elif action in self.ACTION_EXIT_SCRIPT:
            self.close()

    def onClick(self, controlId):
        if controlId == self.CONTROL_MAIN_IMAGE:
            if self.getProperty('type') == 'site':
                self.showAlbums()
            elif self.getProperty('type') == 'album':
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
                pDialog.create(getLS(32000))
                pDialog.update(50)
                self.boston_com.getPhotos(self.getProperty('link'))
                pDialog.update(100)
                pDialog.close()
                imageDownloader.Download(self.boston_com.photos, downloadPath)

    def showPhotos(self): #the order is significant!
        link = self.getProperty('link')
        source = self.getProperty('source')
        self.getControl(self.CONTROL_MAIN_IMAGE).reset() #Clear the old list of albums.
        self.getControl(self.CONTROL_USAGE_TEXT).setVisible(False)
        if source == 'boston_com':
            self.boston_com.getPhotos(link) # Get a list of photos from the link.
            photos = self.boston_com.photos
        elif source == 'another source which provides a list of photos':
            pass
        self.showItems(photos, 'photo')

    def showAlbums(self):
        albumUrl = self.getProperty('link')
        source = self.getProperty('source')
        self.getControl(self.CONTROL_MAIN_IMAGE).reset() #This is necessary when returning from photos.
        self.getControl(self.CONTROL_USAGE_TEXT).setVisible(True)    
        if source == 'boston_com':
            self.boston_com.getAlbums(albumUrl)
            albums = self.boston_com.albums
        elif source == 'another source which provides a list of albums':
            pass
        self.showItems(albums, 'album')

    def showSites(self):
        self.getControl(self.CONTROL_MAIN_IMAGE).reset()
        self.getControl(self.CONTROL_USAGE_TEXT).setVisible(True)
        self.showItems(sites, 'site')

    def showItems(self, itemSet, type):
        total = len(itemSet)
        for i, item in enumerate(itemSet):
            item['showInfo'] = 'true'
            item['type'] = type #TODO move this to scraper?
            item['title'] = item['title'] + ' (%s/%s)' % (i+1, total)
            self.addListItem(self.CONTROL_MAIN_IMAGE, item)

    def addListItem(self, controlId, properties):
        li = xbmcgui.ListItem(label=properties['title'].upper(), label2=properties['description'], iconImage=properties['pic'])
        for p in properties.keys():
            li.setProperty(p, properties[p])
        self.getControl(controlId).addItem(li)
