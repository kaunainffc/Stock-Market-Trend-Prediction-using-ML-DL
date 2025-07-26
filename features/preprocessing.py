from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

def preprocess(df):
    features = ['SMA', 'EMA', 'RSI', 'MACD', 'OBV', 'Momentum', 'StdDev', 'ROC', 'Williams %R']
    X = df[features]
    y = df['Target']
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    return train_test_split(X_scaled, y, test_size=0.2, shuffle=False), X_scaled
