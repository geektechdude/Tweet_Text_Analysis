#!/usr/bin/python3
# geektechstuff
# Twitter Azure Sentiment Application

from twython import Twython
import requests
from pprint import pprint

# Azure API endpoint
sentiment_uri = "https://uksouth.api.cognitive.microsoft.com/text/analytics/v2.0/sentiment"
# Azure key
headers ={"Ocp-Apim-Subscription-Key":"ENTER AZURE KEY HERE"}

# imports the Twitter API keys from a .py file called auth
from auth import (
    consumer_key,
    consumer_secret,
    access_token,
    access_token_secret
)

# sets up a variable called Twitter that calls the relevent Twython modules
twitter = Twython(
    consumer_key,
    consumer_secret,
    access_token,
    access_token_secret
)

def get_tweets(search_term):
    # this searches Twitter
    results = twitter.cursor(twitter.search, q=search_term)
    # this then pulls each individual tweet
    for result in results:
        # Tweet details that I may be interested in
        tweet_id = result['id_str']
        tweet_text = result['text']
        tweeted_time = result['created_at']
        name = result['user']
        tweet_screen_name = name['screen_name']
        # Preparing the data to give to Azure
        documents = {'documents' : [
        {'id': tweet_id, 'language': 'en', 'text': tweet_text},
        ]}
        # Sending the data to Azure
        response  = requests.post(sentiment_uri, headers=headers, json=documents)
        # Getting response back from Azure
        languages = response.json()
        # Printing the response
        pprint(languages)

get_tweets('geektechstuff')