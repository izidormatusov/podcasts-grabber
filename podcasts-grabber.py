#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#    Created by Izidor Matušov <izidor.matusov@gmail.com>
#            on 10.01.2013

import os
import sys
from urllib.parse import urlparse

# Locate config home or use ~/.config
try:
    from xdg.BaseDirectory import xdg_config_home
    CONFIG_DIR = xdg_config_home
except ImportError:
    CONFIG_DIR = os.path.expanduser("~/.config")

CONFIG_DIR = os.path.join(CONFIG_DIR, "podcasts-grabber")

def load_configuration():
    """ Read list of feeds and already downloaded episodes
    
    If feeds.conf does not exist, terminate (There is nothing to download)  """

    feeds_filename = os.path.join(CONFIG_DIR, "feeds.conf")
    try:
        feeds = [line.strip() for line in open(feeds_filename, "r").readlines()
                    if line.startswith('http')]
    except IOError:
        print('Missing feeds configuration file {}.'.format(feeds_filename),
            file=sys.stderr)
        sys.exit(1)

    return feeds, []


if __name__ == "__main__":
    feeds, episodes = load_configuration()
    for feed in feeds:
        print(feed)
        break

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
