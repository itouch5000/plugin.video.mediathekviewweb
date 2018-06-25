# -*- coding: utf-8 -*-
import json
import requests


class MediathekViewWeb(object):
    def __init__(self, size=10, future=False):
        self.future = future
        self.size = size
        self.session = requests.session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:58.0) Gecko/20100101 Firefox/58.0",
            "content-type": "text/plain",
        })

    def search(self, query=None, channel=None, page=1):
        offset = self.size * (page - 1)
        data = {
            "sortBy": "timestamp",
            "sortOrder": "desc",
            "future": self.future,
            "offset": offset,
            "size": self.size,
        }
        if query or channel:
            data["queries"] = list()
        if query:
            data["queries"].append({
                "fields": [
                    "title",
                    "topic",
                ],
                "query": query,
            })
        if channel:
            data["queries"].append({
                "fields": [
                    "channel",
                ],
                "query": channel,
            })
        r = self.session.post(
            "https://mediathekviewweb.de/api/query",
            data=json.dumps(data)
        )
        return r.json()

    def channels(self):
        r = self.session.get(
            "https://mediathekviewweb.de/api/channels",
        )
        return r.json()
