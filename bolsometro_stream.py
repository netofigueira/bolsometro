#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 10 00:00:27 2021

@author: neto
"""
import tweepy
import sqlite3
import config
from leia import SentimentIntensityAnalyzer
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener
from tweepy import Stream
import time
from unidecode import unidecode
import json


ckey = config.CONSUMER_KEY
csecret = config.CONSUMER_SECRET
atoken = config.ACCESS_TOKEN
asecret = config.ACCESS_TOKEN_SECRET



#object from LEiA library to make sentiment analysis
# LEiA é uma adaptação de VADER p analise em portugues
analyzer = SentimentIntensityAnalyzer()

conn = sqlite3.connect('twitter.db')
c = conn.cursor()



def create_table():
    try:
        c.execute("CREATE TABLE IF NOT EXISTS sentiment(unix REAL, tweet TEXT, sentiment REAL)")
        c.execute("CREATE INDEX fast_unix ON sentiment(unix)")
        c.execute("CREATE INDEX fast_tweet ON sentiment(tweet)")
        c.execute("CREATE INDEX fast_sentiment ON sentiment(sentiment)")
        conn.commit()
    except Exception as e:
        print(str(e))
create_table()



class listener(StreamListener):

    def on_data(self, data):
        try:
            data = json.loads(data)
            tweet = unidecode(data['text'])
            time_ms = data['timestamp_ms']
            vs = analyzer.polarity_scores(tweet)
            sentiment = vs['compound']
            #print(time_ms, tweet, sentiment)
            c.execute("INSERT INTO sentiment (unix, tweet, sentiment) VALUES (?, ?, ?)",
                  (time_ms, tweet, sentiment))
            conn.commit()

        except KeyError as e:
            print(str(e))
        return(True)

    def on_error(self, status):
        print(status)



while True:

    try:
        auth = OAuthHandler(ckey, csecret)
        auth.set_access_token(atoken, asecret)
        twitterStream = Stream(auth, listener())
        twitterStream.filter(track=["Bolsonaro", "Lula"], languages=['pt'])
    except Exception as e:
        print(str(e))
        time.sleep(5)