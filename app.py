import streamlit as st
import pandas as pd
import yfinance as yf
import pandas_ta as ta
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

# Page Config
st.set_page_config(page_title="Ultra Master Terminal", layout="wide")

# CSS Styling
st.markdown("""
<style>
    .stApp { background-color: #0d1117; color: white; }
    .main-header { 
        background: linear-gradient(90deg, #1e3a8a, #1e1b4b); 
        padding: 25px; border-radius: 15px; 
        text-align: center; border-bottom: 4px solid #3b82f6; 
        margin-bottom: 20px;
    }
    .metric-box { background: #161b22; padding: 20px; border-radius: 12px; border: 1px solid #30363d; }
</style>
""", unsafe_allow_html=True)

# Analysis Logic
def master_analyzer(symbol):
    try:
        ticker = f"{symbol}.NS"
        df = yf.download(ticker, period="1y", interval="1d", progress=False)
        if len(df) < 50: return None

        ltp = round(df['Close'].iloc[-1], 2)
        prev_close = df['Close'].iloc[-2]
        change = round(((ltp - prev_close) / prev_close) * 100, 2)
        rsi = round(ta.rsi(df['Close'], length=14).iloc[-1], 2)
        ema_200 = ta.ema(df['Close'], length=200).iloc[-1]
        bb = ta.bbands(df['Close'], length=20, std=2)
        upper_bb = bb['BBU_20_2.0'].iloc[-1]
        vol_ratio = round(df['Volume'].iloc[-1] / df['Volume'].tail(10).mean(), 2)

        category = "Wait"
        if ltp > upper_bb and vol_ratio > 1.5 and rsi > 60:
            category = "🚀 Breakout"
        elif ltp > ema_200 and rsi > 55:
            category = "📈 Swing Buy"
        elif rsi > 70:
            category = "🔥 Momentum"
        elif ltp < ema_200:
            category = "🔴 Avoid"

        return {
            "Stock": symbol,
            "LTP": ltp,
            "Change%": change,
            "RSI": rsi,
            "Vol_Ratio": vol_ratio,
            "Category": category,
            "Chart": f"https://www.tradingview.com/chart/?symbol=NSE:{symbol}"
        }
    except: return None

# UI Header
st.markdown("<div class='main-header'><h1>🎯 ULTRA MASTER SCANNER</h1><p>Live Market Analytics Dashboard</p></div>", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("Settings")
    stock_list = ["RELIANCE", "TCS", "HDFCBANK", "INFY", "ICICIBANK", "SBIN", "ZOMATO", "RVNL", "IRFC", "TATASTEEL", "TITAN", "BHEL", "PNB"]
    selected_stocks = st.multiselect("Select Stocks", stock_list, default=stock_list)
    run_btn = st.button("🚀 RUN LIVE SCAN")

if run_btn:
    with st.spinner("Analyzing Stocks..."):
        with ThreadPoolExecutor(max_workers=20) as executor:
            results = list(executor.map(master_analyzer, selected_stocks))
        
        final_data = [r for r in results if r]
        if final_data:
            df = pd.DataFrame(final_data)
            
            # Metrics
            c1, c2, c3 = st.columns(3)
            c1.metric("Scanned", f"{len(df)} Stocks")
            c2.metric("Breakouts", len(df[df['Category'] == "🚀 Breakout"]))
            c3.metric("Swing", len(df[df['Category'] == "📈 Swing Buy"]))

            # Tabs
            t1, t2, t3 = st.tabs(["🚀 Breakouts", "📈 Swing Picks", "📊 All Data"])
            with t1: st.table(df[df['Category'] == "🚀 Breakout"])
            with t2: st.table(df[df['Category'] == "📈 Swing Buy"])
            with t3: st.dataframe(df, use_container_width=True)
            
            st.success(f"Last Update: {datetime.now().strftime('%H:%M:%S')}")

st.caption("Developed by Ashraf Manjeri")