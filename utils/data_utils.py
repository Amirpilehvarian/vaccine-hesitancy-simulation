# utils/data_utils.py

import os
import re
import json
import requests
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import pandas as pd
from newspaper import Article
from bs4 import BeautifulSoup
from tqdm import tqdm
import snscrape.modules.twitter as sntwitter


def scrape_news(url_list):
    """Scrape news articles given a list of URLs."""
    articles = []
    for url in tqdm(url_list, desc="Scraping articles"):
        try:
            article = Article(url)
            article.download()
            article.parse()
            articles.append({
                "url": url,
                "title": article.title,
                "text": article.text,
                "source": re.findall(r'https?://(www\.)?([^/]+)', url)[0][1],
                "type": "real"  # Default label, can be changed later
            })
        except Exception as e:
            print(f"Failed to process {url}: {e}")
    return pd.DataFrame(articles)


def scrape_tweets(query, max_tweets=100):
    """Scrape tweets using snscrape."""
    tweets = []
    for i, tweet in enumerate(sntwitter.TwitterSearchScraper(query).get_items()):
        if i >= max_tweets:
            break
        tweets.append({
            "date": tweet.date,
            "username": tweet.user.username,
            "content": tweet.content,
            "url": tweet.url,
            "type": "social_media"
        })
    return pd.DataFrame(tweets)


def save_dataframe(df, filename):
    """Save dataframe to CSV in processed folder."""
    os.makedirs("data", exist_ok=True)
    df.to_csv(f"data/{filename}", index=False)


def load_dataframe(filename):
    """Load CSV from processed folder."""
    return pd.read_csv(f"data/{filename}")
