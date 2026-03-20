# Algogator — Commodity Sentiment Trading Strategy

A pairs trading strategy for corn and wheat futures that combines NLP-based sentiment scoring with statistical mean-reversion signals.

## Strategy Overview

1. **Price data crawling** — fetches historical CBOT corn and wheat futures prices
2. **Sentiment analysis** — scrapes agricultural news and weather reports; scores and z-score normalizes sentiment signals
3. **Mean-reversion signal** — builds a spread via OLS regression on log-prices; generates entry/exit signals when z-score exceeds threshold
4. **Backtest** — simulates long/short positions and computes PnL, Sharpe ratio, and max drawdown

## Files

| File | Purpose |
|---|---|
| `prices_crawl.py` | Fetches commodity price history |
| `nlp_crawl.py` | Scrapes news and agricultural articles |
| `nlp_z_score.py` | Computes NLP sentiment z-scores |
| `weather_z_score.py` | Computes weather-based sentiment signals |
| `backtest.py` | Runs the full pairs trading backtest |

## Setup

```bash
conda env create -f environment.yml
conda activate <env>
python backtest.py
```

> `data_0.nc` (raw weather NetCDF data, ~150 MB) is excluded from the repo due to size. Download separately and place in the root directory.
