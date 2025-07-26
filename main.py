import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))  # ✅ fix typo: "__file__"
import time
import streamlit as st
import yfinance as yf
import pandas as pd

from features.pipeline import run_prediction_pipeline
from utils.db_handler import load_user_db, save_user_db
from utils.plot import plot_price
from auth.auth_handler import login_ui, register_ui

# ✅ Safe download function to handle YFTzMissingError
def safe_download(ticker, start="2013-01-01", retries=3):
    fallback_ticker = ticker.replace(".NS", ".BO") if ".NS" in ticker else ticker

    for attempt in range(retries):
        try:
            ticker_obj = yf.Ticker(ticker)
            hist = ticker_obj.history(start=start)
            if hist.empty:
                # Try fallback ticker
                if ticker != fallback_ticker:
                    st.warning(f"⚠ No data for {ticker}, trying fallback {fallback_ticker}")
                    ticker_obj = yf.Ticker(fallback_ticker)
                    hist = ticker_obj.history(start=start)
                if hist.empty:
                    raise ValueError("No historical data found.")

            hist.reset_index(inplace=True)
            return hist

        except Exception as e:
            if attempt < retries - 1:
                time.sleep(2)
            else:
                st.error(f"❌ Failed to fetch data for {ticker}: {e}")
                return None

# ========== Streamlit Config ==========
st.set_page_config("📈 Stock Trend Predictor", layout="wide")
with open("style/custom.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Load database
db = load_user_db()
USER_DB = db["user_db.json"]
USER_INFO = db["user_info.json"]
WATCHLIST_DB = db["watchlist_db.json"]

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

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

    st.sidebar.success(f"Welcome, {user}")
    if st.sidebar.button("Logout"):
        st.session_state.clear()

    if role == "service_providers":
        st.subheader("👥 Registered Remote Users")
        df_users = pd.DataFrame(USER_INFO["remote_users"]).T.reset_index()
        df_users.columns = ["Username", "Email", "Mobile"]
        st.dataframe(df_users)

    # ⭐ WATCHLIST
    st.subheader("⭐ Watchlist")
    user_watchlist = WATCHLIST_DB.get(user, [])
    new_stock = st.text_input("Add Stock Symbol (e.g., TCS.NS)")

    if st.button("Add to Watchlist"):
        if new_stock and new_stock.upper() not in user_watchlist:
            user_watchlist.append(new_stock.upper())
            WATCHLIST_DB[user] = user_watchlist
            save_user_db({
                "user_db.json": USER_DB,
                "user_info.json": USER_INFO,
                "watchlist_db.json": WATCHLIST_DB,
            })

    if user_watchlist:
        st.write("Watchlist:", user_watchlist)
        uptrend, downtrend = [], []
        for symbol in user_watchlist:
            df = safe_download(symbol)
            time.sleep(1) 
            if df is not None:
                try:
                    pred = run_prediction_pipeline(df)
                    (uptrend if pred else downtrend).append(symbol)
                except Exception as e:
                    st.warning(f"⚠ Prediction failed for {symbol}: {e}")
            else:
                st.warning(f"⚠ Could not fetch data for {symbol}")
        st.success(f"📈 Uptrend: {uptrend}" if uptrend else "📈 No Uptrend")
        st.error(f"📉 Downtrend: {downtrend}" if downtrend else "📉 No Downtrend")

    # 🔍 PREDICT
    st.subheader("🔍 Predict a Stock")
    predict_symbol = st.text_input("Enter Stock Symbol (e.g., INFY.NS)")

    if st.button("Predict"):
        df = safe_download(predict_symbol)
        if df is not None:
            try:
                prediction = run_prediction_pipeline(df)
                st.success("📈 Uptrend" if prediction else "📉 Downtrend")
                plot_price(df, predict_symbol.upper(), prediction)
            except Exception as e:
                st.error(f"⚠ Prediction failed: {e}")
