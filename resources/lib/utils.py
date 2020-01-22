# -*- coding: utf-8 -*-
import sys

is_python2 = sys.version_info.major == 2


def py2_decode(value):
    if is_python2:
        return value.decode('utf-8')
    return value


def py2_encode(value):
    if is_python2:
        return value.encode('utf-8')
    return value
