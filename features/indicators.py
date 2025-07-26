import numpy as np

def add_indicators(df):
    df['SMA'] = df['Close'].rolling(window=14).mean()
    df['EMA'] = df['Close'].ewm(span=14).mean()
    delta = df['Close'].diff()
    gain = delta.where(delta > 0, 0).rolling(14).mean()
    loss = -delta.where(delta < 0, 0).rolling(14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    df['MACD'] = df['Close'].ewm(span=12).mean() - df['Close'].ewm(span=26).mean()
    df['OBV'] = (np.sign(df['Close'].diff()) * df['Volume']).fillna(0).cumsum()
    df['Momentum'] = df['Close'] - df['Close'].shift(10)
    df['StdDev'] = df['Close'].rolling(window=10).std()
    df['ROC'] = df['Close'].pct_change(periods=10)
    df['Williams %R'] = ((df['High'].rolling(14).max() - df['Close']) /
                         (df['High'].rolling(14).max() - df['Low'].rolling(14).min())) * -100
    df.dropna(inplace=True)
    return df
