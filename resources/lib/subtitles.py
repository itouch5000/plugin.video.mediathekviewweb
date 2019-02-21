# -*- coding: utf-8 -*-
import os
import sys
import requests

import xbmc
import xbmcvfs
import xbmcaddon

# add pycaption module to path
addon_dir = xbmc.translatePath(xbmcaddon.Addon().getAddonInfo('path')).decode('utf-8')
module_dir = os.path.join(addon_dir, "resources", "lib", "pycaption")
sys.path.insert(0, module_dir)

# we need this fork: https://github.com/lucasheld/pycaption/tree/py27
from pycaption import SRTWriter, detect_format


def download_subtitle(url, destination):
    if not url:
        return False
    r = requests.get(url)
    if not r.ok:
        return False
    reader = detect_format(r.text)
    if not reader:
        return False
    srt = SRTWriter().write(reader().read(r.text))
    if xbmcvfs.exists(destination):
        xbmcvfs.delete(destination)
    f = xbmcvfs.File(destination, 'w')
    f.write(srt.encode("utf-8"))
    f.close()
    return True
