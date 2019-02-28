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
    # file to hold replied/retweeted Tweet ids to stop duplication
    ids_replied_to = []
    with open('ids_replied_to.txt', 'r') as filehandle:
        filecontents = filehandle.readlines()
        for line in filecontents:
            # remove linebreak which is the last character of the string
            current_place = line[:-1]
            # add item to the list
            ids_replied_to.append(current_place)
    # this searches Twitter
    results = twitter.cursor(twitter.search, q=search_term)
    # this then pulls each individual tweet
    for result in results:
        tweet_id = result['id_str']
        if tweet_id in ids_replied_to:
            print("Skipping as already seen")
        else:
            # Tweet details that I may be interested in
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
            azure_response = response.json()
            # Stripping the score out
            azure_documents = azure_response['documents']
            azure_score = azure_documents[0]['score']
            if azure_score >= 0.6:
                print(tweet_id,"\n", tweet_text, "from \n", tweet_screen_name)
                print(azure_documents,"\n is postive")
                print("Retweeting....")
                twitter.retweet(id = tweet_id)
                ids_replied_to.append(tweet_id)
                with open('ids_replied_to.txt', 'w') as filehandle:
                    filehandle.writelines("%s\n" % place for place in ids_replied_to)
            elif azure_score == 0.5:
                print(tweet_id,"\n", tweet_text, "from \n", tweet_screen_name)
                print(azure_documents,"\n is neutral")
            else:
                print(tweet_id,"\n", tweet_text, "from \n", tweet_screen_name)
                print(azure_documents,"\n is negative")

get_tweets('geektechstuff')
