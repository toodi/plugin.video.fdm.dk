#
#      Copyright (C) 2014 Tommy Winther
#      http://tommy.winther.nu
#
#  This Program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2, or (at your option)
#  any later version.
#
#  This Program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this Program; see the file LICENSE.txt.  If not, write to
#  the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.
#  http://www.gnu.org/copyleft/gpl.html
#
import os
import sys
import urllib2
import urlparse

import xml.etree.ElementTree

import buggalo

import xbmcgui
import xbmcaddon
import xbmcplugin

DATA_URL = 'http://vms.api.qbrick.com/rest/v3/getplayer/D5D17F48C5C03FBE?statusCode=xml'

# TODO improve xpath expressions once script.module.elementtree is 1.3+


def showCategories():
    doc = loadXml()
    for category in doc.findall('categories/category'):
        if category.attrib.get('type') != 'standard':
            continue

        id = category.attrib.get('id')
        name = category.attrib.get('name')

        item = xbmcgui.ListItem(name, iconImage=ICON)
        item.setProperty('Fanart_Image', FANART)
        xbmcplugin.addDirectoryItem(HANDLE, PATH + '?category=' + id, item, isFolder=True)

    xbmcplugin.endOfDirectory(HANDLE)


def showMedia(categoryId):
    doc = loadXml()
    for media in doc.findall('media/item'):
        correctCategory = False
        categories = media.findall('categories/category')
        for category in categories:
            if category.text == categoryId:
                correctCategory = True
                break

        if not correctCategory:
            continue

        title = media.findtext('title')
        image = media.findtext('images/image')
        smilUrl = media.findtext('playlist/stream/format/substream')

        infoLabels = dict()
        infoLabels['studio'] = ADDON.getAddonInfo('name')
        infoLabels['plot'] = media.findtext('description')
        infoLabels['title'] = title
        #infoLabels['date'] = date.strftime('%d.%m.%Y')
        infoLabels['aired'] = media.findtext('publishdate')[0:10]
        infoLabels['year'] = int(media.findtext('publishdate')[0:4])

        item = xbmcgui.ListItem(title, iconImage=image, thumbnailImage=image)
        item.setInfo('video', infoLabels)
        item.setProperty('Fanart_Image', image)
        item.setProperty('IsPlayable', 'true')
        xbmcplugin.addDirectoryItem(HANDLE, PATH + '?smil=' + smilUrl.replace('&', '%26'), item)

    xbmcplugin.endOfDirectory(HANDLE)


def playMedia(smilUrl):
    doc = loadXml(smilUrl)
    if doc is not None:
        base = doc.find('head/meta').attrib.get('base')
        videos = doc.findall('body/switch/video')
        video = videos[len(videos) - 1].attrib.get('src')
        # todo quality

        item = xbmcgui.ListItem(path=base)
        item.setProperty('PlayPath', video)
        xbmcplugin.setResolvedUrl(HANDLE, True, item)
    else:
        xbmcplugin.setResolvedUrl(HANDLE, False, xbmcgui.ListItem())


def loadXml(url=DATA_URL):
    try:
        u = urllib2.urlopen(url)
        response = u.read()
        u.close()
        return xml.etree.ElementTree.fromstring(response)
    except Exception:
        return None

if __name__ == '__main__':
    ADDON = xbmcaddon.Addon()
    PATH = sys.argv[0]
    HANDLE = int(sys.argv[1])
    PARAMS = urlparse.parse_qs(sys.argv[2][1:])

    ICON = os.path.join(ADDON.getAddonInfo('path'), 'icon.png')
    FANART = os.path.join(ADDON.getAddonInfo('path'), 'fanart.jpg')

    buggalo.SUBMIT_URL = 'http://tommy.winther.nu/exception/submit.php'
    try:
        if 'category' in PARAMS:
            showMedia(PARAMS['category'][0])
        elif 'smil' in PARAMS:
            playMedia(PARAMS['smil'][0])
        else:
            showCategories()
    except Exception:
        buggalo.onExceptionRaised()
