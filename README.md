podcasts-grabber
================

Command line script to download podcasts

Configuration is placed in `~/.config/podcasts-grabber/feeds.conf`:

    # English
    http://feeds.feedburner.com/freakonomicsradio
    http://www.npr.org/rss/podcast.php?id=510184

    # German
    http://chaosradio.ccc.de/chaosradio-latest.rss
    http://www.br-online.de/podcast/blogbuster-on3-radio/cast.xml
    http://www.br-online.de/podcast/popart-on3-radio/cast.xml

Notes:
  * non-URL line is ignored
  * every feed is downloaded in its own folder
  * only new episodes are downloaded
  * podcasts are downloaded to `~/podcasts` folder
