
import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
from datetime import date, timedelta

# --- SETUP ---
st.set_page_config(page_title="📈 Stock Advisor", layout="wide")
st.title("📈 Smart Stock Advisor")
st.markdown("Analyze stocks with fundamentals, technicals, and get smart BUY/HOLD/SELL suggestions")

# --- SIDEBAR INPUT ---
tickers = st.sidebar.text_input("Enter stock tickers (comma-separated)", "TATAMOTORS.NS, RELIANCE.NS").upper().split(",")
tickers = [t.strip() for t in tickers if t.strip()]
period = st.sidebar.selectbox("Select time period", ["6mo", "1y", "2y"], index=1)

# --- CORE FUNCTION ---
def analyze_stock(ticker):
    data = {}
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period=period)
        info = stock.info
        df = hist.copy()
        df['RSI'] = ta.rsi(df['Close'], length=14)
        df['MA50'] = ta.sma(df['Close'], length=50)
        df['MA200'] = ta.sma(df['Close'], length=200)

        last_rsi = round(df['RSI'].dropna().iloc[-1], 2)
        price = df['Close'].iloc[-1]
        ma50 = df['MA50'].dropna().iloc[-1] if not df['MA50'].dropna().empty else None
        ma200 = df['MA200'].dropna().iloc[-1] if not df['MA200'].dropna().empty else None

        # Fundamental metrics
        pe = info.get("trailingPE", None)
        roe = info.get("returnOnEquity", None)
        debt = info.get("debtToEquity", None)
        market_cap = info.get("marketCap", None)

        # Simple Rule-based Suggestion
        suggestion = "HOLD"
        if pe and pe < 20 and roe and roe > 0.15 and debt and debt < 100:
            if last_rsi and last_rsi < 40:
                suggestion = "BUY"
        if last_rsi and last_rsi > 70:
            suggestion = "SELL"

        data = {
            "Price": f"₹{price:.2f}",
            "PE Ratio": round(pe, 2) if pe else "N/A",
            "ROE": f"{roe*100:.1f}%" if roe else "N/A",
            "Debt/Equity": round(debt, 2) if debt else "N/A",
            "RSI": last_rsi,
            "50 MA": round(ma50, 2) if ma50 else "N/A",
            "200 MA": round(ma200, 2) if ma200 else "N/A",
            "Suggestion": suggestion
        }

    except Exception as e:
        data = {"Error": str(e)}
    return data

# --- ANALYSIS DISPLAY ---
results = []
for ticker in tickers:
    with st.spinner(f"Analyzing {ticker}..."):
        stock_data = analyze_stock(ticker)
        stock_data["Ticker"] = ticker
        results.append(stock_data)

df_results = pd.DataFrame(results).set_index("Ticker")
st.dataframe(df_results, use_container_width=True)

# --- News Placeholder ---
st.markdown("### 📰 News & Alerts (Coming Soon)")
for ticker in tickers:
    st.markdown(f"- 🔔 **{ticker}**: No news alerts at the moment.")
