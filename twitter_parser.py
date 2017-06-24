import tweepy
import json

class TwitterManager(object):
    def __init__(self, keys_json='twitter_keys.json'):
        with open(keys_json) as f:
            keys = eval(f.read())

        auth = tweepy.OAuthHandler(keys['consumer_key'], keys['consumer_secret'])
        auth.set_access_token(keys['access_token'], keys['access_token_secret'])
        self.api = tweepy.API(auth)

    def extract_links(self, screen_name, total_count, chunk_size = 200):
        alltweets = []
        new_tweets = self.api.user_timeline(screen_name=screen_name, count=chunk_size)
        alltweets.extend(new_tweets)
        oldest = alltweets[-1].id - 1
        for _ in range(total_count / chunk_size - 1):
            new_tweets = self.api.user_timeline(screen_name=screen_name, count=chunk_size, max_id=oldest)
            alltweets.extend(new_tweets)
            oldest = alltweets[-1].id - 1
        links = [tweet.entities['urls'][0]['expanded_url'] for tweet in alltweets
                    if len(tweet.entities['urls']) == 1]
        return links

if __name__ == '__main__':
    screen_name = 'lentaruofficial'
    twitter_manager = TwitterManager()
    links = twitter_manager.extract_links(screen_name, 1000)
    with open('twitter_links.txt', 'w') as f:
        f.write('\n'.join(links))
