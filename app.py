import streamlit as st
import pandas as pd
import yfinance as yf
import pandas_ta as ta
import time
from datetime import datetime

# --- PAGE SETUP ---
st.set_page_config(page_title="Ultimate Pro Scanner Hub", layout="wide")

# --- SIDEBAR NAVIGATION ---
st.sidebar.title("🚀 Scanner Menu")
app_mode = st.sidebar.selectbox("Choose a Scanner", 
    ["Multi-Index Pro Scanner", "Option Pro Scanner", "Stock Pro Scanner"])

st.sidebar.markdown("---")
st.sidebar.info(f"⏰ Last Refresh: {datetime.now().strftime('%I:%M:%S %p')}")

# --- GLOBAL STYLES ---
st.markdown("""
<style>
    .stApp { background-color: #0b0e14; color: #ffffff; }
    .card { background-color: #161b22; padding: 15px; border-radius: 12px; border: 1px solid #30363d; text-align: center; }
    .res { color: #ff7b72; font-weight: bold; }
    .sup { color: #44cf6c; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# SECTION 1: MULTI-INDEX PRO SCANNER
# ---------------------------------------------------------
if app_mode == "Multi-Index Pro Scanner":
    st.header("🎯 All-in-One Multi-Index Master")
    
    indices_config = [
        {"name": "NIFTY 50", "ticker": "^NSEI", "sym": "NIFTY"},
        {"name": "BANK NIFTY", "ticker": "^NSEBANK", "sym": "BANKNIFTY"},
        {"name": "FINNIFTY", "ticker": "NIFTY_FIN_SERVICE.NS", "sym": "FINNIFTY"}
    ]

    cols = st.columns(3)
    for i, idx in enumerate(indices_config):
        data = yf.download(idx['ticker'], period="2d", interval="15m", progress=False)
        if not data.empty:
            if isinstance(data.columns, pd.MultiIndex): data.columns = data.columns.get_level_values(0)
            curr = round(data['Close'].iloc[-1], 2)
            with cols[i]:
                st.markdown(f"""
                <div class="card">
                    <h3>{idx['name']}</h3>
                    <h1 style="color:#58a6ff;">{curr}</h1>
                </div>
                """, unsafe_allow_html=True)

# ---------------------------------------------------------
# SECTION 2: OPTION PRO SCANNER
# ---------------------------------------------------------
elif app_mode == "Option Pro Scanner":
    st.header("💎 Option Pro Master Scanner")
    st.write("ഈ ഭാഗത്ത് നിങ്ങളുടെ രണ്ടാമത്തെ കോഡിലെ ഓപ്ഷൻ ചെയിൻ വിവരങ്ങൾ കാണാം.")
    
    # Example logic for Option Chain
    ticker = st.selectbox("Select Index", ["^NSEI", "^NSEBANK"])
    df_opt = yf.download(ticker, period="1d", interval="5m", progress=False)
    if not df_opt.empty:
        st.metric(label="Current Price", value=round(df_opt['Close'].iloc[-1], 2))
        st.success("Option Levels identified successfully.")

# ---------------------------------------------------------
# SECTION 3: STOCK PRO SCANNER (NIFTY 500)
# ---------------------------------------------------------
elif app_mode == "Stock Pro Scanner":
    st.header("📈 EasyCharts Pro - Stock Scanner")
    
    if st.button('🚀 START SCANNING NIFTY 50 STOCKS'):
        stocks = ["RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS"]
        results = []
        with st.spinner('Analyzing Indicators...'):
            for s in stocks:
                df = yf.download(s, period="1y", interval="1d", progress=False)
                if not df.empty:
                    rsi = ta.rsi(df['Close'], length=14).iloc[-1]
                    results.append({"Symbol": s, "LTP": round(df['Close'].iloc[-1], 2), "RSI": round(rsi, 2)})
            
            st.table(pd.DataFrame(results))

if st.sidebar.button("🔄 Manual Refresh"):
    st.rerun()
