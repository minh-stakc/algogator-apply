import pandas as pd
from transformers import pipeline


articles = pd.read_csv("articles_merged.csv")
articles['Date'] = pd.to_datetime(articles['seendate'], format='%Y%m%dT%H%M%SZ').dt.date

#Load Hugging Face 
sentiment_pipeline = pipeline("sentiment-analysis", model="ProsusAI/finbert")
def sentiment_score(text):
    if pd.isna(text):
        return 0
    result = sentiment_pipeline(text[:512])[0] #512 tokens
    label = result['label']
    score = result['score'] #=>confidence level
    return score if label == "POSITIVE" else -score

articles['sentiment'] = articles['title'].apply(sentiment_score)
dates = pd.date_range(articles['Date'].min(), articles['Date'].max(), freq='D')
daily_sent = (
    articles.groupby('Date')['sentiment']
    .sum()
    .reindex(dates, fill_value=0)
    .rename("sentiment")
    .reset_index()
    .rename(columns={"index": "Date"})
)

daily_sent['sentiment_z'] = (daily_sent['sentiment'] - daily_sent['sentiment'].mean()) / daily_sent['sentiment'].std()
daily_sent.to_csv("daily_sentiment.csv", index=False)

print(daily_sent)
