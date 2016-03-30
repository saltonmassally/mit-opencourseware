# 6.00 Problem Set 5
# RSS Feed Filter

import feedparser
import string
import time
from project_util import translate_html
from news_gui import Popup

#-----------------------------------------------------------------------
#
# Problem Set 5

#======================
# Code for retrieving and parsing
# Google and Yahoo News feeds
# Do not change this code
#======================

def process(url):
    """
    Fetches news items from the rss url and parses them.
    Returns a list of NewsStory-s.
    """
    feed = feedparser.parse(url)
    entries = feed.entries
    ret = []
    for entry in entries:
        guid = entry.guid
        title = translate_html(entry.title)
        link = entry.link
        summary = translate_html(entry.summary)
        try:
            subject = translate_html(entry.tags[0]['term'])
        except AttributeError:
            subject = ""
        newsStory = NewsStory(guid, title, subject, summary, link)
        ret.append(newsStory)
    return ret

#======================
# Part 1
# Data structure design
#======================

# Problem 1

# TODO: NewsStory 

class NewsStory(object):
    """docstring for NewsStory"""
    def __init__(self, guid, title, subject, summary, link):
        self.guid = guid
        self.title = title
        self.subject = subject
        self.summary = summary
        self.link = link

    def get_guid(self):
        return self.guid

    def get_title(self):
        return self.title

    def get_subject(self):
        return self.subject

    def get_summary(self):
        return self.summary

    def get_link(self):
        return self.link


#======================
# Part 2
# Triggers
#======================

class Trigger(object):
    def evaluate(self, story):
        """
        Returns True if an alert should be generated
        for the given news item, or False otherwise.
        """
        raise NotImplementedError

# Whole Word Triggers
# Problems 2-5

# TODO: WordTrigger
class WordTrigger(Trigger):
    """docstring for WordTrigger"""
    def __init__(self, word):
        super(WordTrigger, self).__init__()
        self.word = self._sanitize_text(word)

    def _sanitize_text(self, text):
        text = text.lower()
        for punctuation in string.punctuation:
            if punctuation == "'":
                text = text.replace("'s", '')
            text = text.replace(punctuation, '')
        return text

    def is_word_in(self, text):
        text = self._sanitize_text(text)
        text_tokens = text.split(' ')
        return self.word in text_tokens
        

# TODO: TitleTrigger
class TitleTrigger(WordTrigger):
    """docstring for TitleTrigger"""

    def evaluate(self, story):
        """
        Returns True if an alert should be generated
        for the given news item, or False otherwise.
        """
        return self.is_word_in(story.get_title())
        

# TODO: SubjectTrigger
class SubjectTrigger(WordTrigger):
    """docstring for TitleTrigger"""

    def evaluate(self, story):
        """
        Returns True if an alert should be generated
        for the given news item, or False otherwise.
        """
        return self.is_word_in(story.get_subject())

# TODO: SummaryTrigger
class SummaryTrigger(WordTrigger):
    """docstring for TitleTrigger"""

    def evaluate(self, story):
        """
        Returns True if an alert should be generated
        for the given news item, or False otherwise.
        """
        return self.is_word_in(story.get_summary())

# Composite Triggers
# Problems 6-8

# TODO: NotTrigger
class NotTrigger(Trigger):
    """docstring for NotTrigger"""
    def __init__(self, Trig):
        super(NotTrigger, self).__init__()
        self.Trig = Trig

    def evaluate(self, story):
        return not self.Trig.evaluate(story)
        

# TODO: AndTrigger
class AndTrigger(Trigger):
    """docstring for AndTrigger"""
    def __init__(self, Trig1, Trig2):
        super(AndTrigger, self).__init__()
        self.Trig1 = Trig1
        self.Trig2 = Trig2

    def evaluate(self, story):
        return self.Trig1.evaluate(story) and self.Trig2.evaluate(story)
        

# TODO: OrTrigger
class OrTrigger(Trigger):
    """docstring for OrTrigger"""
    def __init__(self, Trig1, Trig2):
        super(OrTrigger, self).__init__()
        self.Trig1 = Trig1
        self.Trig2 = Trig2

    def evaluate(self, story):
        return self.Trig1.evaluate(story) or self.Trig2.evaluate(story)

# Phrase Trigger
# Question 9

# TODO: PhraseTrigger
class PhraseTrigger(Trigger):
    """docstring for WordTrigger"""
    def __init__(self, phrase):
        super(PhraseTrigger, self).__init__()
        self.phrase = phrase

    def evaluate(self, story):
        return (
            self.phrase in story.get_title()
            or self.phrase in story.get_subject()
            or self.phrase in story.get_summary()
        )


#======================
# Part 3
# Filtering
#======================

def filter_stories(stories, triggerlist):
    """
    Takes in a list of NewsStory-s.
    Returns only those stories for whom
    a trigger in triggerlist fires.
    """
    # TODO: Problem 10
    # This is a placeholder (we're just returning all the stories, with no filtering) 
    # Feel free to change this line!
    res = []
    for story in stories:
        res.extend([story for trigger in triggerlist if trigger.evaluate(story)])
    return res

#======================
# Part 4
# User-Specified Triggers
#======================

def readTriggerConfig(filename):
    """
    Returns a list of trigger objects
    that correspond to the rules set
    in the file filename
    """
    # Here's some code that we give you
    # to read in the file and eliminate
    # blank lines and comments
    triggerfile = open(filename, "r")
    all = [ line.rstrip() for line in triggerfile.readlines() ]
    lines = []
    for line in all:
        if len(line) == 0 or line[0] == '#':
            continue
        lines.append(line)
    internalTriggerMap = {}
    triggerOperators = {
        'NOT': NotTrigger,
        'AND': AndTrigger,
        'OR': OrTrigger,
    }
    triggerOperand = {
        'TITLE': TitleTrigger,
        'SUBJECT': SubjectTrigger,
        'SUMMARY': SummaryTrigger,
        'PHRASE': PhraseTrigger
    }
    triggerSet = []
    for line in lines:
        token = line.split(' ')
        print token
        if token[1] in triggerOperand:
            internalTriggerMap[token[0]] = triggerOperand[token[1]](' '.join(token[2:]))
        elif token[1] in triggerOperators:
            operatorList = [internalTriggerMap[trigger] for trigger in token[2:]]
            internalTriggerMap[token[0]] = triggerOperators[token[1]](*operatorList)
        elif token[0] == 'ADD':
            triggerSet = [internalTriggerMap[trigger] for trigger in token[1:]]
        else:
            pass

    return triggerSet
    
import thread

def main_thread(p):
    # A sample trigger list - you'll replace
    # this with something more configurable in Problem 11
    t1 = SubjectTrigger("Obama")
    t2 = SummaryTrigger("MIT")
    t3 = PhraseTrigger("Supreme Court")
    t4 = OrTrigger(t2, t3)
    triggerlist = [t1, t4]
    
    # TODO: Problem 11
    # After implementing readTriggerConfig, uncomment this line 
    triggerlist = readTriggerConfig("triggers.txt")
    print triggerlist

    guidShown = []
    
    while True:
        print "Polling..."

        # Get stories from Google's Top Stories RSS news feed
        stories = process("http://news.google.com/?output=rss")
        # Get stories from Yahoo's Top Stories RSS news feed
        stories.extend(process("http://rss.news.yahoo.com/rss/topstories"))

        # Only select stories we're interested in
        stories = filter_stories(stories, triggerlist)
    
        # Don't print a story if we have already printed it before
        newstories = []
        for story in stories:
            if story.get_guid() not in guidShown:
                newstories.append(story)
        
        for story in newstories:
            guidShown.append(story.get_guid())
            p.newWindow(story)

        print "Sleeping..."
        time.sleep(SLEEPTIME)

SLEEPTIME = 60 #seconds -- how often we poll
if __name__ == '__main__':
    p = Popup()
    thread.start_new_thread(main_thread, (p,))
    p.start()

