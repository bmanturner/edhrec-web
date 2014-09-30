#!/usr/bin/Python

import redis
import core
import tappedout
import logging
import json
import itertools
import random
import urllib2
import HTMLParser
import cgi

# Required header for cgi output
# Everything printed after this will be output to webpage
print "Content-type:text/html\n\r\n\r"

# Formats individual cards for html links
def linkify(cn):
    return '<a href="http://gatherer.wizards.com/Handlers/Image.ashx?name=%s&type=card&.jpg" target="_blank">%s</a>' % (cn, core.cap_cardname(cn))

# Returns card recommendations of the specified type
# t = 'Artifact' || 'Creature' || 'Enchantment' || 'Instant' || 'Sorcery' || 'Land'
def rec_by_type(deck, t):
    newrecs, outrecs = core.recommend(deck)
    rec = []

    for card, score in newrecs:
        # filter out basic lands from being recommendations
        if card in ['swamp', 'island', 'plains', 'mountain', 'forest']:
            continue # there is an annoying thing that happens when people use snow-covered basics
                     # where edhrec will post basic lands as a recommendation. this prevents that
        if score < .3:
            continue

        score = int(score * 100) # make score easier to read

        try:
            types = core.lookup_card(card)['types']
        except:
            logging.warn('something went wong with the card %s, ignoring it' % card)
            continue

        if t in types:
            rec.append((card, score))

    return rec

# Formats results in a table. t = the type
# This should be expanded with more information about each card
def print_rec(rec,t):
    
    print '<table class="table table-striped table-condensed table-hover"><tr><th style="width: 20px;">Score</th><th style="width: 200px;">%s</th><th>Mana Cost</th></tr>' % (t)

    for i in range(20):

        manacost = core.lookup_card(rec[i][0])['manaCost']

        try:
            l = '<tr><td style="text-align: center;"><span class="badge">%d</td><td>%s</td><td>%s</td></tr>' % (rec[i][1], linkify(rec[i][0]), manacost)
        except IndexError:
            l = ' '

        if len(l) == 1:
            break

        print l

    print '</table>'

# Retrieve input from index.html
form = cgi.FieldStorage()

url = form['inputurl'].value
if "http://" not in url:
    url = "http://%s" % url
url = tappedout.URL_PATTERN.match(url)

if url is None:
    print '<h2>That Uril wasn\'t recognized, sorry...</h2>' #badum tss
else:
    url = str(url.group(1))
    card_type = form['cardtype'].value

    deck = tappedout.get_deck(url)
    rec = rec_by_type(deck, card_type)
    print_rec(rec, card_type)