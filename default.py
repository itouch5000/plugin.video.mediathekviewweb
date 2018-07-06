# -*- coding: utf-8 -*-
from datetime import datetime

import xbmcgui

from resources.lib.mediathekviewweb import MediathekViewWeb
from resources.lib.simpleplugin import Plugin, Addon, ListContext

ListContext.cache_to_disk = True
plugin = Plugin()
addon = Addon()
_ = plugin.initialize_gettext()

PER_PAGE = plugin.get_setting("per_page")
FUTURE = plugin.get_setting("enable_future")
QUALITY = plugin.get_setting("quality")


def list_videos(callback, page, query=None, channel=None):
    m = MediathekViewWeb(PER_PAGE, FUTURE)
    data = m.search(query, channel, page)
    if data["err"]:
        dialog = xbmcgui.Dialog()
        dialog.notification(_("Error"), data["err"])
        return
    results = data["result"]["results"]

    listing = []
    for i in results:
        dt = datetime.fromtimestamp(i["timestamp"])

        if QUALITY == 0:  # Hoch
            url = i["url_video_hd"]
            if not url:
                url = i["url_video"]
            if not url:
                url = i["url_video_low"]
        elif QUALITY == 1:  # Mittel
            url = i["url_video"]
            if not url:
                url = i["url_video_low"]
        else:  # Niedrig
            url = i["url_video_low"]

        listing.append({
            'label': u"[{0}] {1} - {2}".format(i["channel"], i["topic"], i["title"]),
            'info': {'video': {
                'title': i["title"],
                'plot': '[B]' + dt.strftime("%d.%m.%Y - %H:%M") + '[/B]\n' + i["description"],
                'dateadded': dt.strftime("%Y-%m-%d %H:%M:%S"),
                'date': dt.strftime("%d.%m.%Y"),
                'aired': dt.strftime("%d.%m.%Y"),
                'year': dt.year,
                "duration": i["duration"],
                "studio": i["channel"],
            }},
            'is_playable': True,
            'url': url,
        })
    if len(results) == PER_PAGE:
        next_page = page + 1
        listing.append({
            'label': '[COLOR blue]{0}[/COLOR]'.format(_("Next page")),
            'url': plugin.get_url(action=callback, page=next_page, query=query, channel=channel),
        })
    return listing


def get_channel():
    dialog = xbmcgui.Dialog()
    m = MediathekViewWeb()
    data = m.channels()
    if data["error"]:
        dialog = xbmcgui.Dialog()
        dialog.notification(_("Error"), data["error"])
        return
    channels = data["channels"]
    index = dialog.select(_("Select channel"), channels)
    if index == -1:
        return
    return channels[index]


@plugin.action()
def root(params):
    return [
        {'label': _("Search"), 'url': plugin.get_url(action='search_all')},
        {'label': _("Search by channel"), 'url': plugin.get_url(action='search_channel')},
        {'label': _("Browse"), 'url': plugin.get_url(action='browse_all')},
        {'label': _("Browse by channel"), 'url': plugin.get_url(action='browse_channel')},
    ]


@plugin.action()
def browse_all(params):
    page = int(params.get("page", 1))
    return list_videos("browse_all", page)


@plugin.action()
def search_all(params):
    page = int(params.get("page", 1))
    query = params.get("query")
    if not query:
        dialog = xbmcgui.Dialog()
        query = dialog.input(_("Search term"))
    if not query:
        return
    return list_videos("search_all", page, query=query)


@plugin.action()
def browse_channel(params):
    page = int(params.get("page", 1))
    channel = params.get("channel")
    if not channel:
        channel = get_channel()
    if not channel:
        return
    return list_videos("browse_channel", page, channel=channel)


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
    if not query:
        return
    return list_videos("search_channel", page, query=query, channel=channel)


@plugin.action()
def play(params):
    return params.url


if __name__ == '__main__':
    plugin.run()
