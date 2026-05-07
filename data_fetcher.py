import yfinance as yf
import pandas as pd



def fetch_stock(ticker, start, end):
    df = yf.download(ticker, start=start, end=end)
    df.reset_index(inplace=True)
    return df

    
