import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
import json
import os

st.set_page_config(page_title="📈 Smart Stock Advisor", layout="wide")
st.title("📉 Smart Stock Advisor")
st.markdown("Analyze stocks with fundamentals, technicals, and get smart BUY/HOLD/SELL suggestions")

# --- Sidebar Inputs ---
st.sidebar.header("Stock Input")
tickers_input = st.sidebar.text_input("Enter stock tickers (comma-separated)", value="TATAMOTORS, RELIANCE")
time_period = st.sidebar.selectbox("Select time period", ["1mo", "3mo", "6mo", "1y", "2y", "5y"], index=3)

# --- Helper Functions ---
def normalize_ticker(ticker):
    ticker = ticker.strip().upper()
    if not ticker.endswith(".NS") and not ticker.endswith(".BO"):
        return ticker + ".NS"  # Default to NSE
    return ticker

def fetch_stock_data(ticker, period):
    try:
        data = yf.download(ticker, period=period)
        if data.empty:
            raise ValueError("No data returned. Check ticker symbol or market availability.")
        return data
    except Exception as e:
        return str(e)

def analyze_technical(data):
    try:
        data.ta.sma(length=20, append=True)
        data.ta.rsi(length=14, append=True)
        data.ta.macd(append=True)
        return data.tail(1)  # Return latest row with indicators
    except Exception as e:
        return str(e)

def generate_signal(row):
    try:
        rsi = row.get("RSI_14")
        macd = row.get("MACD_12_26_9")
        macds = row.get("MACDs_12_26_9")

        if pd.isna(rsi) or pd.isna(macd) or pd.isna(macds):
            return "Not enough data"

        if rsi < 30 and macd > macds:
            return "BUY"
        elif rsi > 70 and macd < macds:
            return "SELL"
        else:
            return "HOLD"
    except:
        return "ERROR"

# --- Processing ---
stocks = [normalize_ticker(ticker) for ticker in tickers_input.split(",") if ticker.strip()]

results = []
errors = []

for ticker in stocks:
    data = fetch_stock_data(ticker, time_period)
    if isinstance(data, str):  # Error
        errors.append((ticker, data))
        continue

    last_row = analyze_technical(data)
    if isinstance(last_row, str):
        errors.append((ticker, last_row))
        continue

    signal = generate_signal(last_row.iloc[0])
    results.append((ticker, signal, last_row.iloc[0].to_dict()))

# --- Display Results ---
st.subheader("🔍 Smart Recommendations")
if results:
    for ticker, signal, indicators in results:
        st.markdown(f"### {ticker}")
        st.markdown(f"**Signal:** `{signal}`")
        st.write(indicators)
else:
    st.info("No valid stock data available for analysis.")

if errors:
    st.subheader("⚠️ Errors")
    error_df = pd.DataFrame(errors, columns=["Ticker", "Error"])
    st.dataframe(error_df, use_container_width=True)

# --- Placeholder for News/Alerts ---
st.subheader("📰 News & Alerts (Coming Soon)")
for ticker in stocks:
    st.markdown(f"- 🔔 **{ticker}**: No news alerts at the moment.")
