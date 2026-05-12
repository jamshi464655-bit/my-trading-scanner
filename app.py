import streamlit as st
import pandas as pd
import yfinance as yf
import pandas_ta as ta
from datetime import datetime

# പേജ് സജ്ജീകരണം
st.set_page_config(page_title="EasyCharts Pro - Intraday Master", layout="wide")

# മനോഹരമായ ഡിസൈനിനായുള്ള CSS
st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 25px; border-radius: 15px; text-align: center; color: white; margin-bottom: 20px;
    }
    .stat-card {
        padding: 20px; border-radius: 12px; text-align: center; color: white; font-weight: bold; margin-bottom: 15px;
    }
    .pre { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }
    .live { background: linear-gradient(135deg, #2af598 0%, #009efd 100%); }
    .momentum { background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); }
    </style>
""", unsafe_allow_html=True)

# സ്കാനർ ലോജിക്
def run_scanner(stock_list):
    pre_list, live_list, mom_list = [], [], []
    progress = st.progress(0)
    
    for idx, stock in enumerate(stock_list):
        try:
            # 15 മിനിറ്റ് ഇന്റർവെലിൽ ഡാറ്റ എടുക്കുന്നു
            df = yf.download(stock, period="5d", interval="15m", progress=False)
            if len(df) < 50: continue
            
            df['EMA200'] = ta.ema(df['Close'], length=200)
            df['RSI'] = ta.rsi(df['Close'], length=14)
            
            ltp = round(float(df['Close'].iloc[-1]), 2)
            chg = round(((ltp - float(df['Close'].iloc[-2])) / float(df['Close'].iloc[-2])) * 100, 2)
            rsi_val = round(float(df['RSI'].iloc[-1]), 2)
            ema_val = float(df['EMA200'].iloc[-1])
            
            res = {"Stock": stock.replace(".NS", ""), "Price": ltp, "Change%": chg, "RSI": rsi_val}
            
            # ഇൻട്രാഡേ കണ്ടീഷനുകൾ
            if chg > 1.5 and ltp > ema_val and rsi_val > 60:
                live_list.append(res)
            elif ltp > ema_val and 40 < rsi_val < 50:
                pre_list.append(res)
            elif rsi_val > 55:
                mom_list.append(res)
                
            progress.progress((idx + 1) / len(stock_list))
        except: continue
    
    progress.empty()
    return pre_list, live_list, mom_list

# ഡിസ്‌പ്ലേ
st.markdown('<div class="main-header"><h1>🚀 EasyCharts Pro - Intraday Master</h1></div>', unsafe_allow_html=True)

# ഇൻട്രാഡേ വാച്ച് ലിസ്റ്റ്
watch_list = ["RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS", "BHARTIARTL.NS", "ITC.NS", "TATAMOTORS.NS", "WIPRO.NS", "ADANIENT.NS", "TITAN.NS"]

if st.button("🔍 START MARKET SCAN"):
    pre, live, mom = run_scanner(watch_list)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f'<div class="stat-card pre"><h2>{len(pre)}</h2>Pre-Breakout</div>', unsafe_allow_html=True)
        if pre: st.dataframe(pd.DataFrame(pre), use_container_width=True)
    with col2:
        st.markdown(f'<div class="stat-card live"><h2>{len(live)}</h2>Live Breakouts</div>', unsafe_allow_html=True)
        if live: st.dataframe(pd.DataFrame(live), use_container_width=True)
    with col3:
        st.markdown(f'<div class="stat-card momentum"><h2>{len(mom)}</h2>Momentum Stocks</div>', unsafe_allow_html=True)
        if mom: st.dataframe(pd.DataFrame(mom), use_container_width=True)
    
    st.success(f"Scan Finished at {datetime.now().strftime('%H:%M:%S')}")
