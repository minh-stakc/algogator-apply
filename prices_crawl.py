import yfinance as yf
import pandas as pd

def get_prices(start="2020-01-01", end="2025-12-31",):
    corn = yf.download("ZC=F", start=start, end=end)
    wheat = yf.download("ZW=F", start=start, end=end)
    df = pd.concat([corn, wheat], axis=1).dropna()
    df.to_csv("prices.csv")
    return df

prices = get_prices()
print(prices)