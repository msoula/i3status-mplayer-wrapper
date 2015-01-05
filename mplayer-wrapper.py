#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This script is a simple wrapper which prefixes each i3status line with custom
# information. It is a python reimplementation of:
# http://code.stapelberg.de/git/i3status/tree/contrib/wrapper.pl
#
# To use it, ensure your ~/.i3status.conf contains this line:
#     output_format = "i3bar"
# in the 'general' section.
# Then, in your ~/.i3/config, use:
#     status_command i3status | ~/.i3/contrib/mplayer-wrapper.py
# In the 'bar' section.
#
# In its previous version it would display the cpu frequency governor, but you
# are free to change it to display whatever you like, see the comment in the
# source code below.
#
# © 2012 Valentin Haenel <valentin.haenel@gmx.de>
#
# In its current version, it will display what mplayer is playing by extracting
# song title from ICY Info lines written to a specific file stored whose path
# is stored in METADATA_FILE variable.
# To use it, ensure to output mplayer's ICY Info line to METADATA_FILE (see below).
# I used the following script to launch mplayer:
#     METADATA_FILE=/tmp/mplayer.data
#     [ -f $METADATA_FILE ] && rm -f $METADATA_FILE
#     mplayer -playlist foo.m3u | stdbuf -o L grep ICY > $METADATA_FILE
#     [ -f $METADATA_FILE ] && rm -f $METADATA_FILE
#
# © 2015 Mathieu Soula aka rid  <msoula@gmx.com>
#
# This program is free software. It comes without any warranty, to the extent
# permitted by applicable law. You can redistribute it and/or modify it under
# the terms of the Do What The Fuck You Want To Public License (WTFPL), Version
# 2, as published by Sam Hocevar. See http://sam.zoy.org/wtfpl/COPYING for more
# details.

import re
import os.path
import sys
import json

METADATA_FILE='/tmp/mplayer.data'
SONG_COLOR='#6780fb'
NOSONG_COLOR='#ffffff'
NOSONG_MSG='No Song Played'

def get_song(f):
    """ Read last line of given file which contains Mplayer's ICY Info data
        This line contains dictionary entry StreamTitle that is returned if found """
    try:
        with open(METADATA_FILE) as fp:
            line = fp.readlines()[-1].strip()
            info = line.split(':', 1)[1].strip()
            attrs = dict(re.findall("(\w+)='([^']*)'", info))
            return attrs.get('StreamTitle', None)
    except IndexError:
        return None
    except IOError:
        return None


def print_line(message):
    """ Non-buffered printing to stdout. """
    sys.stdout.write(message + '\n')
    sys.stdout.flush()

def read_line():
    """ Interrupted respecting reader for stdin. """
    # try reading a line, removing any extra whitespace
    try:
        line = sys.stdin.readline().strip()
        # i3status sends EOF, or an empty line
        if not line:
            sys.exit(3)
        return line
    # exit on ctrl-c
    except KeyboardInterrupt:
        sys.exit()

if __name__ == '__main__':
    # Skip the first line which contains the version header.
    print_line(read_line())

    # The second line contains the start of the infinite array.
    print_line(read_line())

    while True:
        line, prefix = read_line(), ''
        # ignore comma at start of lines
        if line.startswith(','):
            line, prefix = line[1:], ','

        j = json.loads(line)

        # insert information into the start of the json, but could be anywhere
        if os.path.exists(METADATA_FILE):
            song = get_song(METADATA_FILE)
            if song is not None:
                j.insert(0, {'full_text' : '%s' % song, 'name' : 'song', 'color' : SONG_COLOR})
            else:
                j.insert(0, {'full_text' : NOSONG_MSG, 'name' : 'song', 'color' : NOSONG_COLOR})
        else:
            j.insert(0, {'full_text' : NOSONG_MSG, 'name' : 'song', 'color' : NOSONG_COLOR})

        # and echo back new encoded json
        print_line(prefix+json.dumps(j))

