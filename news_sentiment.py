from newsapi import NewsApiClient
from textblob import TextBlob

API_KEY = "8591aa1d335a424a87daff2af83456d5"

newsapi = NewsApiClient(api_key=API_KEY)

def get_sentiment(stock):
    articles = newsapi.get_everything(q=stock, language="en", page_size=5)

    sentiments = []
    for a in articles['articles']:
        text = a['title']
        blob = TextBlob(text)
        sentiments.append(blob.sentiment.polarity)

    if len(sentiments)==0:
        return "Neutral"

    avg = sum(sentiments)/len(sentiments)

    if avg>0:
        return "Positive"
    elif avg<0:
        return "Negative"
    else:
        return "Neutral"
