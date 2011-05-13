import sys

import xbmcgui
import imageDownloader
import xbmcaddon

import tbp_scraper
import sbb_scraper
import wsj_scraper

Addon = sys.modules['__main__'].Addon
getLS = Addon.getLocalizedString


class GUI(xbmcgui.WindowXML):
    # Label Controls
    CONTROL_MAIN_IMAGE = 100
    CONTROL_USAGE_TEXT = 103
    CONTROL_USAGE_BG = 104
    # Label Actions
    ACTION_CONTEXT_MENU = [117]
    ACTION_MENU = [122]
    ACTION_PREVIOUS_MENU = [9]
    ACTION_SHOW_INFO = [11]
    ACTION_EXIT_SCRIPT = [10, 13]
    ACTION_DOWN = [4]
    ACTION_UP = [3]
    ACTION_ANYKEY = [117, 122, 9, 11, 10, 13, 4, 3, 1, 2, 107]

    def __init__(self, *args, **kwargs):
        xbmcgui.WindowXML.__init__(self, *args, **kwargs)
        tbp = tbp_scraper.TBP()
        sbb = sbb_scraper.SBB()
        wsj = wsj_scraper.WSJ()

        self.SOURCES = list()
        self.SOURCES.append(tbp)
        self.SOURCES.append(sbb)
        self.SOURCES.append(wsj)

    def onInit(self):
        self.show_info = 'true'
        self.active_source_id = 0
        self.setSource()
        self.showAlbums()

    def onFocus(self, controlId):
        pass

    def onAction(self, action):
        if action in self.ACTION_ANYKEY:
            self.toggleHelp('false')
        else:
            #print action.getId()
            pass
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
        elif action in self.ACTION_DOWN and \
             self.getProperty('type') == 'album':
            self.nextSource()
            self.showAlbums()
        elif action in self.ACTION_UP and \
             self.getProperty('type') == 'album':
            self.prevSource()
            self.showAlbums()

    def onClick(self, controlId):
        if controlId == self.CONTROL_MAIN_IMAGE:
            self.toggleHelp('true')
            if self.getProperty('type') == 'album':
                self.showPhotos()
            elif self.getProperty('type') == 'photo':
                self.toggleInfo()

    def getProperty(self, property, controlId=CONTROL_MAIN_IMAGE):
        """Returns a property of the selected item"""
        control = self.getControl(controlId)
        return control.getSelectedItem().getProperty(property)

    def toggleInfo(self):
        selectedControl = self.getControl(self.CONTROL_MAIN_IMAGE)
        if self.getProperty('show_info') == 'false':
            for i in range(selectedControl.size()):
                selectedControl.getListItem(i).setProperty('show_info',
                                                           'true')
            self.show_info = 'true'
        else:
            for i in range(selectedControl.size()):
                selectedControl.getListItem(i).setProperty('show_info',
                                                           'false')
            self.show_info = 'false'

    def toggleHelp(self, show):
        selectedControl = self.getControl(self.CONTROL_USAGE_TEXT)
        if show == 'false':
            self.getControl(self.CONTROL_USAGE_TEXT).setVisible(False)
        elif show == 'true':
            self.getControl(self.CONTROL_USAGE_TEXT).setVisible(True)

    def download(self):
        # get writable directory
        downloadPath = xbmcgui.Dialog().browse(3, ' '.join([getLS(32020),
                                                            getLS(32022)]),
                                               'pictures')
        if downloadPath:
            if self.getProperty('type') == 'photo':
                photos = [{'pic':self.getProperty('pic'), 'title': ''}]
                imageDownloader.Download(photos, downloadPath)
            elif self.getProperty('type') == 'album':
                pDialog = xbmcgui.DialogProgress()
                pDialog.create(self.Source.NAME)
                link = self.getProperty('link')
                pDialog.update(50)
                photos = self.Source.getPhotos(link)
                pDialog.update(100)
                pDialog.close()
                imageDownloader.Download(photos, downloadPath)

    def showPhotos(self):  # the order is significant!
        control = self.getControl(self.CONTROL_USAGE_TEXT)
        control.setText('\n'.join([getLS(32030),
                                   getLS(32031),
                                   getLS(32032)]))
        link = self.getProperty('link')
        photos = self.Source.getPhotos(link)
        self.getControl(self.CONTROL_MAIN_IMAGE).reset()
        self.showItems(photos, 'photo')

    def showAlbums(self):
        control = self.getControl(self.CONTROL_USAGE_TEXT)
        control.setText('\n'.join([getLS(32040),
                                   getLS(32041),
                                   getLS(32042)]))
        self.getControl(self.CONTROL_MAIN_IMAGE).reset()
        albums = self.Source.getAlbums()
        self.showItems(albums, 'album')

    def showItems(self, itemSet, type):
        total = len(itemSet)
        for i, item in enumerate(itemSet):
            item['show_info'] = self.show_info
            item['type'] = type
            item['album'] = self.Source.NAME
            item['title'] = item['title']
            item['duration'] = '%s/%s' % (i + 1, total)
            self.addListItem(self.CONTROL_MAIN_IMAGE, item)

    def addListItem(self, controlId, properties):
        li = xbmcgui.ListItem(label=properties['title'],
                              label2=properties['description'],
                              iconImage=properties['pic'])
        for p in properties.keys():
            li.setProperty(p, properties[p])
        self.getControl(controlId).addItem(li)

    def nextSource(self):
        if len(self.SOURCES) > self.active_source_id + 1:
            self.active_source_id += 1
        else:
            self.active_source_id = 0
        self.setSource()

    def prevSource(self):
        if self.active_source_id == 0:
            self.active_source_id = len(self.SOURCES) - 1
        else:
            self.active_source_id -= 1
        self.setSource()

    def setSource(self):
        self.Source = self.SOURCES[self.active_source_id]
