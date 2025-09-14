from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from gdeltdoc import GdeltDoc, Filters
import pandas as pd

def fetch_articles_in_chunks(s_date, e_date, keywords, output):
    results = []
    current_start = datetime.strptime(s_date, "%Y-%m-%d")
    end = datetime.strptime(e_date, "%Y-%m-%d")
    while current_start <= end:
        current_end = (current_start + relativedelta(days=7))
        if current_end > end:
            current_end = end
        gd = GdeltDoc()
        f = Filters(
            start_date=current_start.strftime("%Y-%m-%d"),
            end_date=current_end.strftime("%Y-%m-%d"),
            num_records=3,
            keyword=keywords,
            country="US",
            language="ENG"
        )
        articles = gd.article_search(f)
        print(current_start, current_end)
        if not articles.empty:
            results.append(articles)

        current_start = current_end+relativedelta(days=1)
    
    if results:
        all_articles = pd.concat(results, ignore_index=True)
        all_articles.to_csv(output, index=False)
        return all_articles
    else:
        print("No articles found in given date range.")
        return pd.DataFrame()

articles = fetch_articles_in_chunks(
    s_date="2023-01-01",
    e_date="2025-09-13",
    keywords=[
        "corn", "wheat",
        "drought", "dry spell", "heatwave", "heat wave", "frost", "freeze", "cold snap",
        "flood", "heavy rain", "storm", "hurricane", "cyclone", "wildfire", "fire risk",
        "harvest", "yield"
    ],
    output="articles3.csv"
)

print(articles)
