import os
import sys
import time
import streamlit as st
import pandas as pd
import requests
import yfinance as yf

# Extend system path for local imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from features.pipeline import run_prediction_pipeline
from utils.db_handler import load_user_db, save_user_db
from utils.plot import plot_price
from auth.auth_handler import login_ui, register_ui

# ⚙️ Setup Streamlit page
st.set_page_config("📈 Stock Trend Predictor", layout="wide")
if os.path.exists("style/custom.css"):
    with open("style/custom.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# 🌐 Setup session to prevent Yahoo Finance blocking
session = requests.Session()
session.headers.update({'User-Agent': 'Mozilla/5.0'})

# 📥 Clean download from yfinance (no CSV fallback)
def safe_download(ticker, start="2013-01-01", retries=2):
    import pandas as pd
    import numpy as np
    from datetime import datetime, timedelta

    original = ticker
    tried_fallback = False

    for attempt in range(retries):
        try:
            t_obj = yf.Ticker(ticker)
            hist = t_obj.history(start=start)

            if hist.empty:
                raise ValueError("No historical data returned.")

            hist.reset_index(inplace=True)
            return hist

        except Exception as e:
            st.warning(f"⚠ Attempt {attempt + 1} failed for {ticker}: {e}")

            if not tried_fallback and ".NS" in original:
                ticker = original.replace(".NS", ".BO")
                tried_fallback = True
                st.info(f"🔁 Retrying with fallback: {ticker}")
                continue
            else:
                break

    # If all attempts fail, use static dummy data
    st.error(f"❌ Could not fetch data for {original} or fallback {ticker}")
    st.info("🔄 Using static dummy data for testing.")
    
    dates = pd.date_range(end=datetime.today(), periods=100)
    data = pd.DataFrame({
        "Date": dates,
        "Open": np.random.uniform(1000, 1100, size=100),
        "High": np.random.uniform(1100, 1200, size=100),
        "Low": np.random.uniform(900, 1000, size=100),
        "Close": np.random.uniform(950, 1150, size=100),
        "Volume": np.random.randint(1000000, 3000000, size=100)
    })
    return data


# 🗂️ Load user database
db = load_user_db()
USER_DB = db.get("user_db.json", {})
USER_INFO = db.get("user_info.json", {})
WATCHLIST_DB = db.get("watchlist_db.json", {})

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# 🚪 Authentication Section
st.title("💹 Stock Market Trend Prediction using ML + DL")

if not st.session_state.logged_in:
    tab1, tab2, tab3, tab4 = st.tabs(["SP Login", "User Login", "Register User", "Register SP"])
    with tab1: login_ui("service_providers", USER_DB)
    with tab2: login_ui("remote_users", USER_DB)
    with tab3: register_ui("remote_users", USER_DB, USER_INFO, WATCHLIST_DB)
    with tab4: register_ui("service_providers", USER_DB, USER_INFO, WATCHLIST_DB)

else:
    user = st.session_state.username
    role = st.session_state.user_role

    st.sidebar.success(f"👤 Welcome, {user}")
    if st.sidebar.button("Logout"):
        st.session_state.clear()

    # 👥 Admin View
    if role == "service_providers":
        st.subheader("👥 Registered Remote Users")
        df_users = pd.DataFrame(USER_INFO.get("remote_users", {})).T.reset_index()
        df_users.columns = ["Username", "Email", "Mobile"]
        st.dataframe(df_users)

    # ⭐ Watchlist Management
    st.subheader("⭐ Your Watchlist")
    user_watchlist = WATCHLIST_DB.get(user, [])
    new_stock = st.text_input("Add Stock Symbol (e.g., TCS.NS)")

    if st.button("Add to Watchlist"):
        new_stock = new_stock.upper()
        if new_stock and new_stock not in user_watchlist:
            user_watchlist.append(new_stock)
            WATCHLIST_DB[user] = user_watchlist
            save_user_db({
                "user_db.json": USER_DB,
                "user_info.json": USER_INFO,
                "watchlist_db.json": WATCHLIST_DB,
            })

    if user_watchlist:
        st.write("📌 Symbols in Watchlist:", user_watchlist)
        uptrend, downtrend = [], []

        for symbol in user_watchlist:
            df = safe_download(symbol)
            time.sleep(1)
            if df is not None:
                try:
                    result = run_prediction_pipeline(df)
                    (uptrend if result else downtrend).append(symbol)
                except Exception as e:
                    st.warning(f"⚠ Prediction failed for {symbol}: {e}")
            else:
                st.warning(f"⚠ Data fetch failed for {symbol}")

        st.success(f"📈 Uptrend: {uptrend}" if uptrend else "📈 No Uptrend")
        st.error(f"📉 Downtrend: {downtrend}" if downtrend else "📉 No Downtrend")

    # 🔍 Manual Prediction
    st.subheader("🔍 Predict a Stock Manually")
valid_symbols = ["TCS.NS", "RELIANCE.NS", "HDFCBANK.NS", "INFY.NS", "WIPRO.NS"]
predict_symbol = st.selectbox("Select Symbol", valid_symbols)

if st.button("Predict"):
    df = safe_download(predict_symbol)
    if df is not None:
        try:
            result = run_prediction_pipeline(df)
            st.success("📈 Uptrend" if result else "📉 Downtrend")
            plot_price(df, predict_symbol.upper(), result)
        except Exception as e:
            st.error(f"⚠ Prediction failed: {e}")

