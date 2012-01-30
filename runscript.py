import sys
import xbmcaddon
import xbmc

Addon = xbmcaddon.Addon('script.image.bigpictures')

# Script constants
__scriptname__ = Addon.getAddonInfo('name')
__id__ = Addon.getAddonInfo('id')
__author__ = Addon.getAddonInfo('author')
__version__ = Addon.getAddonInfo('version')
__path__ = Addon.getAddonInfo('path')
__cachedir__ = xbmc.translatePath('special://profile/addon_data/%s/cache/'
                                  % __id__)


if (__name__ == '__main__'):
    if 'plugin' in sys.argv[0]:
        # We are called as plugin
        print '[PLUGIN][%s] version %s initialized!' % (__scriptname__,
                                                        __version__)
        import resources.lib.plugin as plugin
        plugin.run()
        print '[PLUGIN][%s] version %s exited!' % (__scriptname__,
                                                   __version__)
    else:
        # We are called as script
        print '[SCRIPT][%s] version %s initialized!' % (__scriptname__,
                                                        __version__)
        import resources.lib.gui as gui
        ui = gui.GUI('script-%s-main.xml' % __scriptname__,
                     __path__,
                     'default',
                     '720p')
        ui.doModal()
        print '[SCRIPT][%s] version %s exited!' % (__scriptname__,
                                                   __version__)
        del ui
        sys.modules.clear()
