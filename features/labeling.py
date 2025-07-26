import numpy as np

def create_labels(df):
    df['Target'] = np.where(df['Close'].shift(-1) > df['Close'], 1, 0)
    return df
