#!/usr/bin/python3
# geektechstuff
# Twitter Tweet Analysis V2

# modules to handle connecting to Twitter and saving to file
from twython import Twython
import requests
import csv

# modules to handle data analysis
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# time to make a delay
import time

# Azure API endpoint
sentiment_uri = "https://uksouth.api.cognitive.microsoft.com/text/analytics/v2.0/sentiment"
# Azure key
headers ={"Ocp-Apim-Subscription-Key":"AZURE_KEY_HERE"}

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
    # list to hold ids whilst checking them
    ids_seen = []
    # opens the txt file containing previously seen tweets
    with open('ids_seen.txt', 'r') as filehandle:
        filecontents = filehandle.readlines()
        for line in filecontents:
            # remove linebreak which is the last character of the string
            current_place = line[:-1]
            # add item to the list
            ids_seen.append(current_place)
    # this searches Twitter
    results = twitter.cursor(twitter.search, q=search_term)
    # this then pulls each individual tweet
    for result in results:
        tweet_id = result['id_str']
        if tweet_id in ids_seen:
            print(tweet_id, "Skipping as already seen")
        else:
            time.sleep(1)
            # Tweet details that I may be interested in
            tweet_text = result['text']
            tweeted_time = result['created_at']
            name = result['user']
            tweet_screen_name = name['screen_name']
            tweet_language = result['lang']
            ids_seen.append(tweet_id)
            azure_response = ""

            # Preparing the data to give to Azure
            documents = {'documents' : [
            {'id': tweet_id, 'language': 'en', 'text': tweet_text},
            ]}
            # Sending the data to Azure
            response  = requests.post(sentiment_uri, headers=headers, json=documents)
            # Getting response back from Azure
            azure_response = response.json()
            # Stripping the score out
            try:
                azure_documents = azure_response['documents']
                azure_score = azure_documents[0]['score']
                # azure scores may need reviewing
                if azure_score >= 0.6:
                    azure_feedback = "positive"
                elif azure_score == 0.5:
                    azure_feedback = "neutral"
                else:
                    azure_feedback = "negative"
            except:
                azure_feedback = "ERROR"

            # saves id so it does not get checked more than once
            with open('ids_seen.txt', 'w') as filehandle:
                filehandle.writelines("%s\n" % place for place in ids_seen)
            # saves the data of the tweet
            with open('twitter_data.csv', 'a') as datawrite:
                csv_write = csv.writer(datawrite, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                write_to_row = csv_write.writerow([tweet_screen_name, tweet_language, tweeted_time, tweet_text, azure_feedback])
    return()

def twitter_analysis_language():
    # reads csv created in get_tweets function
    filehandle = pd.read_csv("twitter_data.csv")
    filehandle.head()
    tweet_lang = filehandle['tweet_language'].value_counts()
    tweet_lang_index = filehandle['tweet_language'].value_counts().index
    plt.bar(tweet_lang_index,tweet_lang)
    plt.xlabel("Language")
    plt.ylabel("Number of Tweets")
    plt.title("Tweet Language Breakdown")
    # saves bar chart as a PDF
    plt.savefig('lang.pdf')
    return()

def twitter_analysis_sentiment():
    # reads csv created in get_tweets function
    filehandle = pd.read_csv("twitter_data.csv")
    filehandle.head()
    tweet_feedback = filehandle['azure_feedback'].value_counts()
    tweet_feedback_index = filehandle['azure_feedback'].value_counts().index
    plt.bar(tweet_feedback_index,tweet_feedback)
    plt.xlabel("Feedback")
    plt.ylabel("Number of Tweets")
    plt.title("Tweet Feedback Breakdown")
    # saves bar chart as a PDF
    plt.savefig('feedback.pdf')
    return()