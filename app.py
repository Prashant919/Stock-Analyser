import streamlit as st
import pandas as pd
from nsepython import *

st.set_page_config(page_title="Stock Analyser", layout="wide")
st.title("📈 Indian Stock Analyser - NSE")

# Input for ticker symbols (comma-separated)
ticker_input = st.text_input("Enter NSE stock tickers (e.g. RELIANCE, INFY, TCS):", "RELIANCE")
tickers = [ticker.strip().upper() for ticker in ticker_input.split(",") if ticker.strip()]

# Function to fetch stock data from NSE
@st.cache_data(show_spinner=False)
def fetch_nse_data(ticker):
    try:
        data = nse_eq(ticker)
        price_info = data['priceInfo']
        return {
            'lastPrice': price_info.get('lastPrice', 0),
            'dayHigh': price_info.get('intraDayHighLow', {}).get('max', 0),
            'dayLow': price_info.get('intraDayHighLow', {}).get('min', 0),
            'weekHigh52': price_info.get('weekHighLow', {}).get('max', 0),
            'weekLow52': price_info.get('weekHighLow', {}).get('min', 0),
            'change': price_info.get('change', 0),
            'pChange': price_info.get('pChange', 0)
        }
    except Exception as e:
        st.warning(f"Failed to fetch data for {ticker}: {e}")
        return None

st.markdown("---")

for ticker in tickers:
    st.subheader(f"📊 {ticker} Analysis")
    stock_data = fetch_nse_data(ticker)

    if stock_data:
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Current Price (₹)", stock_data['lastPrice'], f"{stock_data['pChange']}%")
        col2.metric("Day High", stock_data['dayHigh'])
        col3.metric("Day Low", stock_data['dayLow'])
        col4.metric("52W High / Low", f"{stock_data['weekHigh52']} / {stock_data['weekLow52']}")

        # Basic Decision Rule Example
        suggestion = "Hold"
        if stock_data['lastPrice'] <= 1.05 * stock_data['weekLow52']:
            suggestion = "Consider Buying (near 52W Low)"
        elif stock_data['lastPrice'] >= 0.95 * stock_data['weekHigh52']:
            suggestion = "Consider Selling (near 52W High)"

        st.success(f"📌 Suggestion: **{suggestion}**")
    else:
        st.error(f"No data available for {ticker}")
