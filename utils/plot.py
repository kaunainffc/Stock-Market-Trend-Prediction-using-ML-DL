import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

def plot_price(df, symbol, prediction):
    df['Date'] = pd.to_datetime(df['Date'])
    last_year = df[df['Date'] >= (df['Date'].max() - pd.Timedelta(days=365))]
    plt.figure(figsize=(14, 6))
    plt.plot(last_year['Date'], last_year['Close'], label='Close Price')
    signal = last_year['Close'].iloc[-1]
    next_day = last_year['Date'].iloc[-1] + pd.Timedelta(days=1)
    color = 'green' if prediction == 1 else 'red'
    marker = '^' if prediction == 1 else 'v'
    label = 'Predicted Up 📈' if prediction == 1 else 'Predicted Down 📉'
    plt.scatter(next_day, signal, color=color, s=100, label=label, marker=marker)
    plt.title(f"Prediction for {symbol}")
    plt.xlabel("Date")
    plt.ylabel("Close Price")
    plt.grid(True)
    plt.legend()
    st.pyplot(plt)
