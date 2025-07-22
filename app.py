
import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta

st.set_page_config(page_title="📈 Smart Stock Advisor", layout="wide")
st.title("📊 Smart Multi-Stock Analyzer with News")

tickers = st.text_input("Enter Stock Tickers (comma separated, e.g., TATAMOTORS.NS, RELIANCE.NS)", value="TATAMOTORS.NS, RELIANCE.NS")

if tickers:
    ticker_list = [t.strip().upper() for t in tickers.split(",") if t.strip()]
    for ticker_symbol in ticker_list:
        st.divider()
        try:
            stock = yf.Ticker(ticker_symbol)
            info = stock.info
            st.header(f"{info.get('longName', 'Stock Info')} ({ticker_symbol})")

            # Fundamentals
            pe = info.get("trailingPE", None)
            roe = info.get("returnOnEquity", 0) * 100
            debt_to_equity = info.get("debtToEquity", 0)

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("PE Ratio", pe)
            with col2:
                st.metric("ROE (%)", f"{roe:.2f}")
            with col3:
                st.metric("Debt to Equity", f"{debt_to_equity:.2f}")

            with st.expander("📈 Fundamental Verdict"):
                if pe and pe < 20:
                    st.success("✅ PE is low — possible undervaluation.")
                elif pe:
                    st.warning("⚠️ PE is high — check if growth justifies it.")

                if roe > 15:
                    st.success("✅ High ROE — good profitability.")
                else:
                    st.warning("⚠️ Low ROE — might not be efficient.")

                if debt_to_equity < 50:
                    st.success("✅ Low debt — financially healthy.")
                else:
                    st.warning("⚠️ High debt — risk of leverage.")

            # Technicals
            df = stock.history(period="6mo")
            df["RSI"] = ta.rsi(df["Close"], length=14)
            df["MA50"] = ta.sma(df["Close"], length=50)
            df["MA200"] = ta.sma(df["Close"], length=200)

            if len(df) > 0:
                latest = df.iloc[-1]
                st.subheader("📊 Technical Indicators")
                st.write(f"**RSI:** {latest['RSI']:.2f}")
                st.write(f"**50-day MA:** ₹{latest['MA50']:.2f}")
                st.write(f"**200-day MA:** ₹{latest['MA200']:.2f}")

                with st.expander("📉 Technical Verdict"):
                    if latest["RSI"] < 30:
                        st.success("✅ RSI < 30 — oversold zone, potential buy.")
                    elif latest["RSI"] > 70:
                        st.warning("⚠️ RSI > 70 — overbought zone.")

                    if latest["MA50"] > latest["MA200"]:
                        st.success("✅ Golden Cross — bullish signal.")
                    else:
                        st.warning("⚠️ Death Cross — bearish trend.")

                # Final Suggestion
                st.subheader("📌 Final Recommendation")
                if pe and pe < 20 and roe > 15 and latest["RSI"] < 40:
                    st.success("🔔 Suggestion: BUY or ADD MORE")
                elif pe and pe > 40 or roe < 10 or latest["RSI"] > 70:
                    st.error("⚠️ Suggestion: SELL or TRIM HOLDINGS")
                else:
                    st.info("💡 Suggestion: HOLD and Monitor")
            else:
                st.warning("⚠️ Not enough historical data for technicals.")

            # News Placeholder
            st.subheader("📰 Latest News (Coming Soon)")
            st.info("Real-time news integration is under development...")

        except Exception as e:
            st.error(f"Error with {ticker_symbol}: {e}")
