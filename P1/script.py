import tweepy
from tweepy import OAuthHandler
import json
import datetime as dt
import time
import os
import sys
from pytz import timezone as tz


def load_api():
    ''' Function that loads the twitter API after authorizing the user. '''

    consumer_key = ''
    consumer_secret = ''

    access_token = ''
    access_secret = ''

    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_secret)
    # load the twitter API via tweepy
    return tweepy.API(auth)

    
def tweet_search(api, query, max_tweets, max_id, since_id, geoloc, ling):

    searched_tweets = []
    while len(searched_tweets) < max_tweets:
        remaining_tweets = max_tweets - len(searched_tweets)
        try:
            new_tweets = api.search(q=query, count=remaining_tweets,
                                    since_id=str(since_id),
				                    max_id=str(max_id-1),lang=ling, geocode=geoloc)
#                                    geocode=geocode)
            print('found',len(new_tweets),'tweets')
            if not new_tweets:
                print('no tweets found')
                break
            searched_tweets.extend(new_tweets)
            max_id = new_tweets[-1].id
        except tweepy.TweepError:
            print('exception raised, waiting 15 minutes')
            print('(until:', dt.datetime.now()+dt.timedelta(minutes=15), ')')
            time.sleep(15*60)
            break # stop the loop
    return searched_tweets, max_id


def get_tweet_id(api, date='', days_ago=9, query='a'):
    ''' Function that gets the ID of a tweet. This ID can then be
        used as a 'starting point' from which to search. The query is
        required and has been set to a commonly used word by default.
        The variable 'days_ago' has been initialized to the maximum
        amount we are able to search back in time (9).'''

    if date:
        # return an ID from the start of the given day
        td = date + dt.timedelta(days=1)
        tweet_date = '{0}-{1:0>2}-{2:0>2}'.format(td.year, td.month, td.day)
        tweet = api.search(q=query, count=1, until=tweet_date)
    else:
        # return an ID from __ days ago
        td = dt.datetime.now() - dt.timedelta(days=days_ago)
        tweet_date = '{0}-{1:0>2}-{2:0>2}'.format(td.year, td.month, td.day)
        # get list of up to 10 tweets
        tweet = api.search(q=query, count=10, until=tweet_date)
        print('search limit (start/stop):',tweet[0].created_at)
        # return the id of the first tweet in the list
        return tweet[0].id


def write_tweets(tweets, filename, topic, city, ling):
    ''' Function that appends tweets to a file. '''
    
    tzone = tz('US/Central')

    with open(filename, 'a+', encoding='utf8') as f:
        for tweet in tweets:
            data = tweet._json
            date_changed = tzone.localize(tweet.created_at)
            fmt = '%Y-%m-%dT%H:%M:%SZ'

            #date_changed.strftime(fmt)
            data['tweet_date'] = str(date_changed.strftime(fmt))

            iso_lan = data['metadata']['iso_language_code']
            print('iso_lan_code : {} '.format(iso_lan))
            data['topic'] = topic
            data['city']= city
            data['tweet_lang']=ling
            json.dump(data, f, ensure_ascii=False, indent=4)
            f.write('\n')

    

def main():
    ''' This is a script that continuously searches for tweets
        that were created over a given number of days. The search
        dates and search phrase can be changed below. '''

    ''' search variables: '''
    search_phrases = ['trump']

    time_limit = 1.5                           # runtime limit in hours
    max_tweets = 100                           # number of tweets per search (will be
                                               # iterated over) - maximum is 100
    min_days_old, max_days_old = 6, 7          # search limits e.g., from 7 to 8
                                               # gives current weekday from last week,
                                               # min_days_old=0 will search from right now
    #USA = '39.8,-95.583068847656,2500km'      # this geocode includes nearly all American
                                               # states (and a large portion of Canada)
    
    # Geo Locations, Languages, Places 
    root_fldr = 'environment' # Topic
    pl = 'bangkok'  # Hardcode place here 

    # Empty Variables - Used to set data into it.
    language = ''
    geolocation = ''
    city = ''

    lang_loc = {

        "nyc": {
            "lang": "en",
            "loc": "40.7127753,-74.0059728,25km"
        },

        "delhi": {
            "lang": "hi",
            "loc": "28.68627380000001,77.22178310000004,25km"
        },

        "mexico city": {
            "lang": "es",
            "loc": "19.4326077,-99.13320799999997,25km"
        },

        "bangkok": {
            "lang": "th",
            "loc": "13.7563309,100.50176510000006,25km"
        },

        "paris": {
            "lang": "fr",
            "loc": "48.85661400000001,2.3522219000000177,25km"
            }
    }

    for key, value in lang_loc.items():
        place = key
        if place.__contains__(pl):
            language = value.get('lang')
            location = value.get('loc')
            city = place

    print(root_fldr)
    print("language : {}".format(language))
    print("geo_location : {}".format(location))
    print("city : {}".format(city))

    # loop over search items,
    # creating a new file for each
    for search_phrase in search_phrases:
        print('Search phrase =', search_phrase)

        ''' other variables '''
        """ location = ''
        geo_loc = '' """
        name = search_phrase
        lang_subf = 'thai'
        json_file_root = root_fldr + '/'  + name + '/'  + name
        json_file_root = root_fldr + '/' + lang_subf + '/' + name + '/'  + name
        os.makedirs(os.path.dirname(json_file_root), exist_ok=True)
        read_IDs = False
        
        # open a file in which to store the tweets
        if max_days_old - min_days_old == 1:
            d = dt.datetime.now() - dt.timedelta(days=min_days_old)
            day = '{0}-{1:0>2}-{2:0>2}'.format(d.year, d.month, d.day)
        else:
            d1 = dt.datetime.now() - dt.timedelta(days=max_days_old-1)
            d2 = dt.datetime.now() - dt.timedelta(days=min_days_old)
            day = '{0}-{1:0>2}-{2:0>2}_to_{3}-{4:0>2}-{5:0>2}'.format(
                  d1.year, d1.month, d1.day, d2.year, d2.month, d2.day)
        json_file = json_file_root + '_' + day + '.json'
        if os.path.isfile(json_file):
            print('Appending tweets to file named: ',json_file)
            read_IDs = True
        
        # authorize and load the twitter API
        api = load_api()
        
        # set the 'starting point' ID for tweet collection
        if read_IDs:
            # open the json file and get the latest tweet ID
            with open(json_file, 'r') as f:
                lines = f.readlines()
                max_id = json.loads(lines[-1])['id']
                print('Searching from the bottom ID in file')
        else:
            # get the ID of a tweet that is min_days_old
            if min_days_old == 0:
                max_id = -1
            else:
                max_id = get_tweet_id(api, days_ago=(min_days_old-1))
        # set the smallest ID to search for
        since_id = get_tweet_id(api, days_ago=(max_days_old-1))
        print('max id (starting point) =', max_id)
        print('since id (ending point) =', since_id)
        


        ''' tweet gathering loop  '''
        
        start = dt.datetime.now()
        end = start + dt.timedelta(hours=time_limit)
        count, exitcount = 0, 0
        while dt.datetime.now() < end:
            count += 1
            print('count =',count)
            # collect tweets and update max_id
            tweets, max_id = tweet_search(api, search_phrase, max_tweets,
                                          max_id=max_id, since_id=since_id, geoloc=location, ling=language)
            # write tweets to file in JSON format
            if tweets:
                write_tweets(tweets, json_file, topic=root_fldr, city=city, ling=language)
                exitcount = 0
            else:
                exitcount += 1
                if exitcount == 3:
                    if search_phrase == search_phrases[-1]:
                        sys.exit('Maximum number of empty tweet strings reached - exiting')
                    else:
                        print('Maximum number of empty tweet strings reached - breaking')
                        break


if __name__ == "__main__":
    main()
