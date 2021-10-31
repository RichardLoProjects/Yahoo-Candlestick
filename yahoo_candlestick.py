from datetime import datetime as dt
import pandas as pd
import yfinance as yf
import numpy as np
import mplfinance as mpf

def get_ticker():
    return input('Enter valid ticker symbol (e.g. ^GSPC or ^VIX): ')

def get_df(ticker):
    df = yf.download(
        ticker, start='2000-04-01', end=dt.today().strftime('%Y-%m-%d'))
    return df

def aggregate_df(df):
    df['LogReturns'] = pd.DataFrame.diff(np.log(df['Close']), periods=1, axis=0)
    period = 'Q'  # Q, M
    temp_open = df.groupby(pd.Grouper(freq=period))['Adj Close'].nth([0])
    temp_close = df.groupby(pd.Grouper(freq=period))['Adj Close'].nth([-1])
    #temp_volume = df.groupby(pd.Grouper(freq=period))['Volume'].sum()
    temp_volatility = df.groupby(pd.Grouper(freq=period))['LogReturns'].std()*np.sqrt(250)
    df = df.groupby(pd.Grouper(freq=period))['Adj Close'].agg(
        Low=np.min,High=np.max).reset_index()
    df['Open'] = temp_open.values
    df['Close'] = temp_close.values
    #df['Volume'] = temp_volume.values
    df['Volume'] = temp_volatility.values  # Intentionally mislabelled as "volume"
    df = df[['Date','Open','High','Low','Close','Volume']]
    df.set_index('Date', inplace=True)
    return df

def plot(ticker, df):
    market_colours = mpf.make_marketcolors(
        up='green',down='red',
        edge='inherit',
        wick={'up':'green','down':'red'},
        volume={'up':'green','down':'red'},
    )
    custom_style = mpf.make_mpf_style(
        base_mpl_style='dark_background',
        marketcolors=market_colours,
        gridstyle='',gridcolor='white'
    )
    mpf.plot(
        df, type='candle', style=custom_style,
        title=ticker.upper(),
        ylabel='Price (USD)', ylabel_lower='Volatility',
        volume=not (df['Volume']==0).all(),
        show_nontrading=True
    )

def main():
    ticker = get_ticker()
    df = get_df(ticker)
    df = aggregate_df(df).dropna()
    plot(ticker, df)

if __name__ == '__main__':
    main()