from bs4 import BeautifulSoup
from time import time
import requests
import datetime
import tweepy
import codecs
import json
import sys
import re

from requests.packages.urllib3.exceptions import InsecurePlatformWarning
requests.packages.urllib3.disable_warnings(InsecurePlatformWarning)

class TwitterManager(object):
    def __init__(self, keys_json='twitter_keys.json'):
        with open(keys_json) as f:
            keys = eval(f.read())

        auth = tweepy.OAuthHandler(keys['consumer_key'], keys['consumer_secret'])
        auth.set_access_token(keys['access_token'], keys['access_token_secret'])
        self.api = tweepy.API(auth)

    def extract_links(self, screen_name, from_date='2017-06-01', verbose=True):
        from_date = datetime.datetime.strptime(from_date, '%Y-%m-%d').date()
        all_tweets = []

        old_tweets_n = 0
        all_tweets = self.api.user_timeline(screen_name=screen_name, count=200)
        new_tweets_n = len(all_tweets)
        while all([tweet.created_at.date() >= from_date for tweet in all_tweets]) and old_tweets_n != new_tweets_n:
            old_tweets_n = len(all_tweets)
            oldest = all_tweets[-1].id - 1
            new_tweets = self.api.user_timeline(screen_name=screen_name, count=200, max_id=oldest)
            all_tweets.extend(new_tweets)
            new_tweets_n = len(all_tweets)

        all_tweets = [tweet for tweet in all_tweets if tweet.created_at.date() >= from_date]
        links = [tweet.entities['urls'][0]['expanded_url'] for tweet in all_tweets if tweet.entities['urls']]
        dates = [tweet.created_at.date() for tweet in all_tweets if tweet.entities['urls']]


        if verbose:
            print 'LINKS EXTRACTING DONE, @{}'.format(screen_name)
            print '{}/{} have links'.format(len(links), len(links))
            print 'Tweets from @{} until now, total: {} links'.format(screen_name, len(links))

        return links, dates

def url2text(url):
    html = requests.get(url).text
    soup = BeautifulSoup(html, 'lxml')
    lines = [x.text.strip() for x in soup.findAll('p')]
    lines = [re.sub('\n', ' ', line) for line in lines]
    lines = [re.sub('\s+', ' ', line) for line in lines]
    text = ' '.join(lines)
    return text

def dump_by_screen_name(screen_name):

    links_file = 'links/{}.links.csv'.format(screen_name)
    texts_file = 'texts/{}.texts.json'.format(screen_name)

    twitter_manager = TwitterManager()
    links, dates = twitter_manager.extract_links(screen_name=screen_name)
    with open(links_file, 'w') as f:
        for link, date in zip(links, dates):
            if 'twitter.com' not in link:
                try:
                    f.write('{},{}\n'.format(date, link))
                except UnicodeEncodeError:
                    print 'Error at link: {}'.format(link)


    with open(links_file, 'r') as f, \
         codecs.open(texts_file, 'w', encoding='utf-8') as out:
        reader = [line.strip().split(',') for line in f.readlines()]
        out.write('[\n')
        start_time = time()
        for n, record in enumerate(reader):
            date, link = record
            text = url2text(link)
            json.dump({'date': date, 'text': text}, out, ensure_ascii=False)
            if n != len(reader) - 1:
                out.write(',')
            out.write('\n')
            time_until_now = time() - start_time
            msg = '\r{}/{}, time: {} min. {} sec.'.format(n+1, len(reader), int(time_until_now) / 60, int(time_until_now) % 60)
            sys.stdout.write(msg)
            sys.stdout.flush()
        print '\n@{} parsing done'.format(screen_name)
        out.write(']\n')


if __name__ == '__main__':
    screen_names = [
        'rgrus',
        'kommersant',
        'ru_rbc',
        'izvestia_ru',
        'kpru',
        'mkomsomolets',
        'GazetaRu',
        'lifenews_ru',
        'ForbesRussia',
        'fontanka_news',
        'snob_project',
        'meduzaproject',
        'lentaruofficial'
    ]
    for screen_name in screen_names:
        dump_by_screen_name(screen_name)
