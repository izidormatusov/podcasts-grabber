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
import re
from urllib.parse import urlparse
from urllib.request import urlretrieve
from shutil import rmtree
from multiprocessing import Pool
from random import shuffle

import feedparser

# Locate config home or use ~/.config
try:
    from xdg.BaseDirectory import xdg_config_home
    CONFIG_DIR = xdg_config_home
except ImportError:
    CONFIG_DIR = os.path.expanduser("~/.config")

CONFIG_DIR = os.path.join(CONFIG_DIR, "podcasts-grabber")

MAX_CONCURRENT_DOWNLOADS = 10

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

    episodes_filename = os.path.join(CONFIG_DIR, "episodes.txt")
    if os.path.exists(episodes_filename):
        episodes = set([episode.strip() for episode in 
                            open(episodes_filename, "r").readlines()
                            if episode.strip() != ""])
    else:
        episodes = set()

    return feeds, episodes

def process_feed(url, already_downloaded):
    """ Process a single feed

    Download feed, find new episodes and print nice stats """

    feed = feedparser.parse(url)

    # check for errors
    if feed.bozo != 0 and 'title' not in feed.feed:
        print("Problem with podcast {}".format(url), file=sys.stderr)
        return None

    title = feed.feed.get('title', '(no title)')
    normalized_title = re.sub('\W+', '-', title).lower()[:30]

    urls = []
    for entry in feed.entries:
        for link in entry.links:
            if link['rel'] == 'enclosure' and link['href'] not in already_downloaded:
                urls.append(link['href'])
                break

    if len(urls) > 0:
        print("{} new from {}".format(len(urls), title))
        return {'title': normalized_title,
            'url': url,
            'links': urls}
    else:
        print("{}: NO NEW EPISODES\n{}\n".format(title, url))
        return None

def download_file(params):
    """ Download a file into specific folder """
    url, folder = params
    name = os.path.join(folder, url[url.rfind('/') + 1:])
    urlretrieve(url, filename=name)

def download_episodes(feeds):
    """ Download episodes """
    podcasts_dir = os.path.expanduser("~/podcasts")
    if os.path.exists(podcasts_dir):
        answer = input("{} already exists! Delete? [y/N] ".format(podcasts_dir))
        if answer.lower() in ["y", "yes"]:
            rmtree(podcasts_dir)

    try:
        os.mkdir(podcasts_dir)
    except OSError:
        # ignore existing folder
        pass

    os.chdir(podcasts_dir)

    jobs = []
    old_episodes = []

    # create folders and prepare list of urls
    for feed in feeds:
        try:
            os.mkdir(feed['title'])
            info_name = os.path.join(feed['title'], 'info.txt')
            open(info_name, 'w').write("Feed URL:\n{}".format(feed['url']))
        except OSError:
            # ignore existing folder
            pass
        
        for link in feed['links']:
            old_episodes.append(link)
            jobs.append((link, feed['title']))

    # Shuffle jobs to prevent downloading many files from same server in the same time
    shuffle(jobs)

    # Download files with progressbar
    pool = Pool(processes=4)
    result = pool.imap(download_file, jobs, 1)
    len_jobs = len(jobs)
    print("0 / {}".format(len_jobs))
    pos = 0
    for _ in result :
        pos += 1
        print("\r{} / {}".format(pos, len_jobs))

    # save old episodes
    episodes_filename = os.path.join(CONFIG_DIR, "episodes.txt")
    open(episodes_filename, 'a').write("\n{}\n".format('\n'.join(old_episodes)))


if __name__ == "__main__":
    feeds, episodes = load_configuration()
    download_list = [process_feed(feed, episodes) for feed in feeds]
    # filter non-empty
    download_list = [feed for feed in download_list if feed is not None]

    # nothing to do => finish
    if len(download_list) == 0:
        sys.exit(0)

    total = sum(len(feed['links']) for feed in download_list)
    print("Total new episodes: {}".format(total))
    answer = input("\nStart downloading? [Y/n] ")
    if answer.lower() in ["n", "no"]:
        sys.exit(0)

    download_episodes(download_list)

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
