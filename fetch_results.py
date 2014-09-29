#!/usr/bin/Python

import redis
import core
import tappedout
import logging
import json
import time
import datetime
import itertools
import random
import urllib2
import HTMLParser
import cgi

print "Content-type:text/html\n\r\n\r"


def linkify(cn):
    return '<a href="http://gatherer.wizards.com/Handlers/Image.ashx?name=%s&type=card&.jpg" target="_blank">%s</a>' % (cn, core.cap_cardname(cn))


form = cgi.FieldStorage()
url = form['inputurl'].value
if "http://" not in url:
    url = "http://%s" % url

url = tappedout.URL_PATTERN.match(url)
 

if url is None:
    
    print '<h2>That Uril wasn\'t recognized, sorry...</h2>' #badum tss
else:
    url = str(url.group(1))  

    deck = tappedout.get_deck(url)
    
    newrecs, outrecs = core.recommend(deck)
    lands = []
    creatures =[]
    enchantments = []
    artifacts = []
    spells = []

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

     
        if 'Creature' in types:
            creatures.append((card, score))
        elif 'Land' in types:
            lands.append((card, score))
        elif 'Enchantment' in types:
            enchantments.append((card,score))
        elif 'Artifact' in types:
            artifacts.append((card,score))
        else:
            spells.append((card, score))
    out_str = []

    out_str.append('<table class="table table-striped table-condensed table-bordered"><tr><th>Creatures</th><th>Spells</th><th>Enchantments</th><th>Artifacts</th><th>Lands</th></tr>')
    for i in range(20):

        try:
            c = '<span class="badge">%d</span> %s ' % (creatures[i][1], linkify(creatures[i][0]))
        except IndexError:
            c = ' '

        try:
            s = '<span class="badge">%d</span> %s ' % (spells[i][1], linkify(spells[i][0]))
        except IndexError:
            s = ' '

        try:
            e = '<span class="badge">%d</span> %s ' % (enchantments[i][1], linkify(enchantments[i][0]))
        except IndexError:
            e = ' '

        try:
            a = '<span class="badge">%d</span> %s ' % (artifacts[i][1], linkify(artifacts[i][0]))
        except IndexError:
            a = ' '

        try:
            l = '<span class="badge">%d</span> %s ' % (lands[i][1], linkify(lands[i][0]))
        except IndexError:
            l = ' '

        #try:
        #    u = '%s ' % linkify(outrecs[i][0])
        #except IndexError:
        #    u = ' '

        if len(c + s + e + a + l) == 5:
           break

        out_str.append('<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>' % (c, s , e, a, l))
    out_str.append('</table>')
    core.add_deck(deck)
    for line in out_str:
        print '<p>%s</p>' % line

