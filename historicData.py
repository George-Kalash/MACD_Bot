import yfinance as yf
import yahooquery as yq
import pandas as pd
import asyncio

tickers = yq.Ticker('mu')

df = tickers.history(period='60d', interval='15m')
# place historic_data.csv in the tests/ directory
df.reset_index(inplace=True)
with open('tests/historic_data.csv', 'w') as f:
    df.to_csv(f)

df.head()

print(df)