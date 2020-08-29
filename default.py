# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
import os
import sys
import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin

from resources.lib.mediathekviewweb import MediathekViewWeb
from resources.lib.simpleplugin import Plugin, Addon
from resources.lib.utils import py2_encode, py2_decode

# add pytz module to path
addon_dir = py2_decode(xbmc.translatePath(xbmcaddon.Addon().getAddonInfo('path')))
module_dir = os.path.join(addon_dir, "resources", "lib", "pytz")
sys.path.insert(0, module_dir)

import pytz


plugin = Plugin()
addon = Addon()
_ = plugin.initialize_gettext()

PER_PAGE = plugin.get_setting("per_page")
FUTURE = plugin.get_setting("enable_future")
QUALITY = plugin.get_setting("quality")
SUBTITLE = plugin.get_setting("enable_subtitle")


if SUBTITLE:
    from resources.lib.subtitles import download_subtitle

# -- ka --
# for icons and co.
def artPath(channel):
    art = channel.lower() + '.png'
    return os.path.join(addon_dir, 'resources', 'media', art)

#removes duplicates
def chk_duplicates(url, title, duplicates):
    try:
        for j in duplicates:
            if url.split("//")[1] == j['url'].split("//")[1]:
                return True
            elif title in j['title']:
                return True
            else:
                continue
    except:
        pass

def list_videos(callback, page, query=None, channel=None):
    m = MediathekViewWeb(PER_PAGE, FUTURE)
    data = m.search(query, channel, page)
    if data["err"]:
        dialog = xbmcgui.Dialog()
        dialog.notification(_("Error"), data["err"])
        return
    results = data["result"]["results"]

    no_duplicates = []

    for i in results:
        dt = datetime.datetime.fromtimestamp(i["timestamp"], pytz.timezone("Europe/Berlin"))
        url = ''
        if QUALITY == 0:  # Hoch
            for j in ("url_video_hd", "url_video", "url_video_low"):
                if i.get(j) == '': 
                    continue
                else:
                    url = i.get(j)

        elif QUALITY == 1:  # Mittel
            for j in ("url_video", "url_video_low"):
                if i.get(j) == '': 
                    continue
                else:
                    url = i.get(j)

        else:  # Niedrig
            url = i.get("url_video_low")

        if url == '': continue

        if not chk_duplicates(url, i["title"], no_duplicates) == True:
            no_duplicates.append({'url': url, 'title': i["title"]})
        else:
            continue
#--------------------------------------------------------

        today = datetime.date.today()
        if dt.date() == today:
            date = _("Today")
        elif dt.date() == today + datetime.timedelta(days=-1):
            date = _("Yesterday")
        else:
            date = dt.strftime("%d.%m.%Y")

        li = xbmcgui.ListItem("[{0}] {1} - {2}".format(i["channel"], i["topic"], i["title"]))

        li.setArt({'poster': artPath(i["channel"]), 'icon': artPath(i["channel"])})
        li.setProperty('Fanart_Image', artPath('fanart'))

        li.setInfo("video", {
            "title": i["title"],
            "plot": "[B]" + date + " - " + dt.strftime("%H:%M") + "[/B]\n" + i["description"],
            "dateadded": dt.strftime("%Y-%m-%d %H:%M:%S"),
            "date": dt.strftime("%d.%m.%Y"),
            "aired": dt.strftime("%d.%m.%Y"),
            "year": dt.year,
            "duration": i["duration"],
            "studio": i["channel"],
        })
        li.setProperty("isPlayable", "true")

        xbmcplugin.addDirectoryItem(
            plugin.handle,
            plugin.get_url(action="play", url=url, subtitle=i["url_subtitle"]),
            li,
            isFolder=False
        )

    if len(results) == PER_PAGE:
        next_page = page + 1
        li = xbmcgui.ListItem("[COLOR blue]{0}[/COLOR]".format(_("Next page")))

        li.setArt({'poster': artPath('next'), 'icon': artPath('next')})
        li.setProperty('Fanart_Image', artPath('fanart'))
        li.setInfo('video', {'overlay': 4, 'plot': '[COLOR blue]{0}[/COLOR]'.format(_("Next page"))}) #remove cm menu

        xbmcplugin.addDirectoryItem(
            plugin.handle,
            plugin.get_url(action=callback, page=next_page, query=query, channel=channel),
            li,
            isFolder=True
        )

    xbmcplugin.endOfDirectory(plugin.handle, cacheToDisc=True)


def get_channel():
    m = MediathekViewWeb()
    data = m.channels()
    if data["error"]:
        dialog = xbmcgui.Dialog()
        dialog.notification(_("Error"), data["error"])
        return
    channels = data["channels"]
    dialog = xbmcgui.Dialog()
    index = dialog.select(_("Select channel"), channels)
    if index == -1:
        return
    return channels[index]


def save_query(query, channel=None):
    with plugin.get_storage() as storage:
        if 'queries' not in storage:
            storage['queries'] = []
        entry = {
            'query': query,
            'channel': channel
        }
        if entry in storage['queries']:
            storage['queries'].remove(entry)
        storage['queries'].insert(0, entry)


def load_queries():
    with plugin.get_storage() as storage:
        if 'queries' not in storage:
            storage['queries'] = []
        return storage['queries']


@plugin.action()
def root():
    li = xbmcgui.ListItem(_("Last queries"))
    li.setArt({'poster': artPath('search')})
    li.setProperty('Fanart_Image', artPath('fanart'))
    # remove unused cm menu
    li.setInfo('video', {'overlay': 4, 'plot': '[COLOR blue]{0}[/COLOR]'.format(_("Last queries"))})
    xbmcplugin.addDirectoryItem(
        plugin.handle,
        plugin.get_url(action='last_queries'),
        li,
        isFolder=True
    )
    li = xbmcgui.ListItem(_("Search"))
    li.setArt({'poster': artPath('search')})
    li.setProperty('Fanart_Image', artPath('fanart'))
    # remove unused cm menu
    li.setInfo('video', {'overlay': 4, 'plot': '[COLOR blue]{0}[/COLOR]'.format(_("Search"))})
    xbmcplugin.addDirectoryItem(
        plugin.handle,
        plugin.get_url(action='search_all'),
        li,
        isFolder=True
    )
    li = xbmcgui.ListItem(_("Search by channel"))
    li.setArt({'poster': artPath('search')})
    li.setProperty('Fanart_Image', artPath('fanart'))
    # remove unused cm menu
    li.setInfo('video', {'overlay': 4, 'plot': '[COLOR blue]{0}[/COLOR]'.format(_("Search by channel"))})
    xbmcplugin.addDirectoryItem(
        plugin.handle,
        plugin.get_url(action='search_channel'),
        li,
        isFolder=True
    )
    li = xbmcgui.ListItem(_("Browse"))
    li.setArt({'poster': artPath('search')})
    li.setProperty('Fanart_Image', artPath('fanart'))
    # remove unused cm menu
    li.setInfo('video', {'overlay': 4, 'plot': '[COLOR blue]{0}[/COLOR]'.format(_("Browse"))})
    xbmcplugin.addDirectoryItem(
        plugin.handle,
        plugin.get_url(action='browse_all'),
        li,
        isFolder=True
    )
    li = xbmcgui.ListItem(_("Browse by channel"))
    li.setArt({'poster': artPath('search')})
    li.setProperty('Fanart_Image', artPath('fanart'))
    # remove unused cm menu
    li.setInfo('video', {'overlay': 4, 'plot': '[COLOR blue]{0}[/COLOR]'.format(_("Browse by channel"))})
    xbmcplugin.addDirectoryItem(
        plugin.handle,
        plugin.get_url(action='browse_channel'),
        li,
        isFolder=True
    )
    xbmcplugin.endOfDirectory(plugin.handle)


@plugin.action()
def last_queries():
    queries = load_queries()
    for index, item in enumerate(queries):
        query = item.get('query')
        # fix type for already saved encoded queries
        if type(query) == str:
            query = py2_decode(query)
        channel = item.get('channel')
        if channel:
            label = "{0}: {1}".format(channel, query)
            url = plugin.get_url(action='search_channel', query=query, channel=channel)
        else:
            label = query
            url = plugin.get_url(action='search_all', query=query)
        li = xbmcgui.ListItem(label)
        li.setArt({'poster': artPath('icon'), 'icon': artPath('icon')})
        li.setProperty('Fanart_Image', artPath('fanart'))
        li.setInfo('video', {'overlay': 4, 'plot': '[COLOR blue]{0}[/COLOR]'.format(_("Search term"))})  # remove unused cm menu

        li.addContextMenuItems([
            (
                _("Remove query"),
                'XBMC.RunPlugin({0})'.format(plugin.get_url(action='remove_query', index=index))
            )
        ])
        xbmcplugin.addDirectoryItem(
            plugin.handle,
            url,
            li,
            isFolder=True
        )
    xbmcplugin.endOfDirectory(plugin.handle)


@plugin.action()
def remove_query(params):
    with plugin.get_storage() as storage:
        storage['queries'].pop(int(params.index))
    xbmc.executebuiltin('Container.Refresh')


@plugin.action()
def browse_all(params):
    page = int(params.get("page", 1))
    list_videos("browse_all", page)


@plugin.action()
def search_all(params):
    page = int(params.get("page", 1))
    query = params.get("query")
    if not query:
        dialog = xbmcgui.Dialog()
        query = dialog.input(_("Search term"))
        query = py2_decode(query)
    if not query:
        return
    save_query(query)
    list_videos("search_all", page, query=query)


@plugin.action()
def browse_channel(params):
    page = int(params.get("page", 1))
    channel = params.get("channel")
    if not channel:
        channel = get_channel()
    if not channel:
        return
    list_videos("browse_channel", page, channel=channel)


@plugin.action()
def search_channel(params):
    page = int(params.get("page", 1))
    channel = params.get("channel")
    if not channel:
        channel = get_channel()
    if not channel:
        return
    query = params.get("query")
    if not query:
        dialog = xbmcgui.Dialog()
        query = dialog.input(_("Search term"))
        query = py2_decode(query)
    if not query:
        return
    save_query(query, channel)
    list_videos("search_channel", page, query=query, channel=channel)


@plugin.action()
def play(params):
    li = xbmcgui.ListItem(path=params.url)
    if SUBTITLE:
        subtitle_file = os.path.join(addon.profile_dir, "subtitle.srt")
        subtitle_downloaded = download_subtitle(params.subtitle, subtitle_file)
        if subtitle_downloaded:
            li.setSubtitles([subtitle_file])
    xbmcplugin.setResolvedUrl(plugin.handle, True, li)


if __name__ == '__main__':
    plugin.run()
