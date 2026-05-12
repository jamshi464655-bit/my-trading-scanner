import streamlit as st
import pandas as pd
import yfinance as yf
import numpy as np
import pandas_ta as ta
from datetime import datetime

# --- PAGE SETUP ---
st.set_page_config(page_title="EasyCharts Pro - Intraday Scanner", layout="wide")

# --- CUSTOM CSS (മനോഹരമായ ഡിസൈനിനായി) ---
st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px; border-radius: 15px; text-align: center; color: white; margin-bottom: 30px;
    }
    .stat-box {
        padding: 20px; border-radius: 10px; text-align: center; color: white; margin: 10px 0; font-weight: bold;
    }
    .pre-breakout { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }
    .live-breakout { background: linear-gradient(135deg, #2af598 0%, #009efd 100%); }
    .momentum { background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); }
    </style>
""", unsafe_allow_html=True)

# --- SCANNER LOGIC ---
def analyze_intraday_stocks(stock_list):
    pre_breakout, live_breakout, momentum = [], [], []
    progress_bar = st.progress(0)
    
    for i, s in enumerate(stock_list):
        try:
            # ഇൻട്രാഡേയ്ക്ക് 15 മിനിറ്റ് ഡാറ്റയാണ് നല്ലത്
            df = yf.download(s, period="5d", interval="15m", progress=False)
            if len(df) < 50: continue
            
            # Indicators
            df['EMA200'] = ta.ema(df['Close'], length=200)
            df['RSI'] = ta.rsi(df['Close'], length=14)
            
            ltp = round(df['Close'].iloc[-1], 2)
            prev_close = round(df['Close'].iloc[-2], 2)
            change_pct = round(((ltp - prev_close) / prev_close) * 100, 2)
            rsi = round(df['RSI'].iloc[-1], 2)
            ema200 = df['EMA200'].iloc[-1]
            
            stock_info = {"Stock": s.replace(".NS", ""), "LTP": ltp, "Change %": f"{change_pct}%", "RSI": rsi}
            
            # Intraday Strategies
            if change_pct > 1.5 and ltp > ema200 and rsi > 60:
                live_breakout.append(stock_info)
            elif ltp > ema200 and 40 < rsi < 50:
                pre_breakout.append(stock_info)
            elif rsi > 55:
                momentum.append(stock_info)
                
            progress_bar.progress((i + 1) / len(stock_list))
        except: continue
    
    progress_bar.empty()
    return pre_breakout, live_breakout, momentum

# --- MAIN INTERFACE ---
st.markdown('<div class="main-header"><h1>🚀 EasyCharts Pro - Intraday Scanner</h1><p>Nifty Quality Stocks</p></div>', unsafe_allow_html=True)

# കൂടുതൽ സ്റ്റോക്കുകൾ ഇവിടെ ചേർക്കാം
intraday_stocks = [
    "RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS", "SBI.NS", 
    "BHARTIARTL.NS", "ITC.NS", "ADANIENT.NS", "TATASTEEL.NS", "WIPRO.NS", "HUL.NS"
]

if st.button("🚀 START MARKET SCAN"):
    pre, live, mom = analyze_intraday_stocks(intraday_stocks)
    
    # ഡിസൈൻ കാർഡുകൾ
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f'<div class="stat-box pre-breakout"><h2>{len(pre)}</h2><p>Pre-Breakout Setups</p></div>', unsafe_allow_html=True)
        if pre: st.dataframe(pd.DataFrame(pre), use_container_width=True)
    with col2:
        st.markdown(f'<div class="stat-box live-breakout"><h2>{len(live)}</h2><p>Live Breakouts</p></div>', unsafe_allow_html=True)
        if live: st.dataframe(pd.DataFrame(live), use_container_width=True)
    with col3:
        st.markdown(f'<div class="stat-box momentum"><h2>{len(mom)}</h2><p>Momentum Stocks</p></div>', unsafe_allow_html=True)
        if mom: st.dataframe(pd.DataFrame(mom), use_container_width=True)
    
    st.success(f"Scan completed at {datetime.now().strftime('%I:%M:%S %p')}")
