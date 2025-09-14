import numpy as np
import pandas as pd

prices = pd.read_csv('prices.csv', skiprows=2, header=None)
prices = prices.iloc[1:].copy()
prices.columns = ["Date","CornClose","CornHigh","CornLow","CornOpen","CornVolume",
                  "WheatClose","WheatHigh","WheatLow","WheatOpen","WheatVolume"]
prices['Date'] = pd.to_datetime(prices['Date'])
start, end = pd.Timestamp('2020-01-01'), pd.Timestamp('2025-09-12')
prices = prices[(prices.Date>=start) & (prices.Date<=end)].reset_index(drop=True)
prices['logCorn'] = np.log(prices['CornClose'])
prices['logWheat'] = np.log(prices['WheatClose'])

print(prices)

from statsmodels.regression.linear_model import OLS
from statsmodels.tools import add_constant
betas = [np.nan]*len(prices)
for i in range(60, len(prices)):
    y = prices['logCorn'].iloc[i-60:i]
    X = add_constant(prices['logWheat'].iloc[i-60:i])
    beta = OLS(y, X).fit().params.iloc[1]
    betas[i] = beta
prices['beta'] = betas
prices['spread'] = prices['logCorn'] - prices['beta']*prices['logWheat']
prices['spread_mean'] = prices['spread'].rolling(window=252).mean()
prices['spread_std']  = prices['spread'].rolling(window=252).std()
prices['spread_z']    = (prices['spread'] - prices['spread_mean']) / prices['spread_std']

weather = pd.read_csv("weather_sentiment.csv", parse_dates=["Date"])
daily_sent = pd.read_csv("daily_sentiment.csv", parse_dates=["Date"])
signals = pd.merge(weather, daily_sent, on="Date", how="left").fillna(0)

signals["WRI"] = (
    signals["corn_temp_z"] 
    - signals["corn_precip_z"] 
    + signals["wheat_temp_z"] 
    - signals["wheat_precip_z"] 
    - signals["sentiment_z"]
) / 5 

data = pd.merge(prices[['Date','spread','spread_z']], signals[['Date','WRI']], on='Date', how='left')
data['WRI_lag'] = data['WRI'].shift(1)


def run_backtest(data, z_entry=2.0, exit_rule="zero", hold_days=10, WRI_thr=None):
    """
    Run backtest with customizable parameters.
    """
    positions = []
    current_pos = 0
    entry_info = {}

    for i, row in data.iterrows():
        z = row['spread_z']; WRI0 = row['WRI_lag']
        if np.isnan(z):
            continue
        date = row['Date']

        if current_pos != 0:
            days = (date - entry_info['entry_date']).days
            exit_flag = False
            if days >= hold_days:
                exit_flag = True
            elif exit_rule == "zero" and ((current_pos==1 and z>=0) or (current_pos==-1 and z<=0)):
                exit_flag = True
            elif exit_rule == "half" and abs(z) < 0.5:
                exit_flag = True
            elif exit_rule == "one" and abs(z) < 1.0:
                exit_flag = True

            if exit_flag:
                exit_price = row['spread']
                pnl = (exit_price - entry_info['entry_price']) * current_pos
                entry_info.update({'exit_date': date, 'exit_price': exit_price, 'pnl': pnl, 'days': days})
                positions.append(entry_info)
                current_pos = 0
                entry_info = {}

        if current_pos == 0 and not np.isnan(WRI0) and (WRI_thr is None or WRI0 < WRI_thr):
            if z > z_entry:
                current_pos = -1  
            elif z < -z_entry:
                current_pos = 1  
            if current_pos != 0:
                entry_info = {'entry_date': date, 'position': current_pos, 'entry_price': row['spread']}
    daily_pnl = pd.Series(0.0, index=data.index)
    for tr in positions:
        pos = tr['position']
        i0 = data.index[data.Date == tr['entry_date']][0]
        i1 = data.index[data.Date == tr['exit_date']][0]
        for k in range(i0+1, i1+1):
            daily_pnl.iloc[k] += (data.loc[k,'spread'] - data.loc[k-1,'spread']) * pos

    equity = daily_pnl.cumsum()
    total_pnl = daily_pnl.sum()
    sharpe = np.mean(daily_pnl)/np.std(daily_pnl)*np.sqrt(252) if np.std(daily_pnl) else 0
    
    return total_pnl, sharpe


#test diffrent parameters
results = []
for z_entry in [2.0, 2.5, 3.0]:
    for exit_rule in ["zero", "half", "one"]:
        for hold_days in [5, 10, 15]:
            for wri_pct in [70, 75, 80, 90]:
                WRI_thr = np.percentile(signals["WRI"], wri_pct)
                total_pnl, sharpe = run_backtest(data, z_entry, exit_rule, hold_days, WRI_thr)
                results.append({
                    "z_entry": z_entry,
                    "exit_rule": exit_rule,
                    "hold_days": hold_days,
                    "wri_pct": wri_pct,
                    "Sharpe": sharpe,
                    "PnL": total_pnl
                })
results_df = pd.DataFrame(results).sort_values("Sharpe", ascending=False)
print(results_df)
