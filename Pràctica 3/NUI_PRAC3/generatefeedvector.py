# -*- coding: iso-8859-15 -*-
import feedparser
import re
import csv
#------------------------------------------------------------------------------------------------------
# Returns title and dictionary of word counts for an RSS feed
def getwordcounts(url):
  # Parse the feed
  d=feedparser.parse(url)
  wc={}

  # Loop over all the entries
  for e in d.entries:
    if 'summary' in e: summary=e.summary
    else: summary=e.description

    # Extract a list of words
    words=getwords(e.title+' '+summary)
    for word in words:
      wc.setdefault(word,0)
      wc[word]+=1
  return d.feed.title,wc

#-----------------------------------------------------------------------------------------------------

DecodeDict={u'&aacute;':u'a',
        u'&eacute;':u'e',
        u'&iacute;':u'i',
        u'&oacute;':u'o',
        u'&uacute;':u'u',
        u'&agrave;':u'a',
        u'&egrave;':u'e',
        u'&igrave;':u'i',
        u'&ograve;':u'o',
        u'&ugrave;':u'u',
        u'&uuml;':u'u',
        u'&iuml;':u'i',
        u'&rsquo;':u' ',
        u'&ccedil;':u'c',
        u'\xed':u'i',
        u'\xe8':u'e',
        u'\u2019':u' ',
        u'\xe9':u'e',
        u'\xf3':u'o',
        u'\xfc':u'u',
        u'\xf2':u'o',
        u'':u'a',
        u'':u'a',
        u'?':u'e',
        u'':u'e',
        u'':u'i',
        u'':u'o',
        u'':u'o',
        u'':u'u',
        u'&middot;':u'',
        u'&nbsp;':u' ',
        u'&Agrave;':u'a',
        u'&Eacute;':u'e',
        u'&Egrave;':u'e',
        u'&Iacute;':u'i',
        u'&Ograve;':u'o',
        u'&Oacute;':u'o',
        u'&Ugrave;':u'u',
        u'&ldquo;':u' ',
        u'&rdquo;':u' '
        }

def stripHTMLaccents(text,rwords):
  for item in rwords:
    text=text.replace(item,rwords[item])
  return text

def getwords(html):
  # Remove all the HTML tags
  txt=re.compile(r'<[^>]+>').sub('',html)
  txt=stripHTMLaccents(txt,DecodeDict)
  # Split words by all non-alpha characters
  words=re.compile(r'[^A-Z^a-z]+').split(txt)

  # Convert to lowercase
  return [word.lower() for word in words if word!='' and len(word)>2 and len(word)<20]

