import streamlit as st
import yfinance as yf
import pandas as pd

# Page Configuration
st.set_page_config(page_title="Pro Trading Scanner", layout="wide")

# --- SIDEBAR NAVIGATION ---
st.sidebar.title("🚀 Scanner Menu")
app_mode = st.sidebar.selectbox("Choose a Scanner", 
    ["Market Overview", "Stock Breakout Scanner", "EMA Signal Scanner"])

st.sidebar.markdown("---")
st.sidebar.write("Developed by Mohammad Aslam Sha M.")

# --- 1. MARKET OVERVIEW PAGE ---
if app_mode == "Market Overview":
    st.title("📊 Market Indices")
    target_indices = {"NIFTY 50": "^NSEI", "BANK NIFTY": "^NSEBANK", "FINNIFTY": "NIFTY_FIN_SERVICE.NS"}

    cols = st.columns(3)
    for i, (name, ticker) in enumerate(target_indices.items()):
        try:
            data = yf.download(ticker, period="1d", interval="15m", progress=False)
            if not data.empty:
                price = round(data['Close'].iloc[-1], 2)
                with cols[i]:
                    st.metric(name, price)
        except: continue

# --- 2. STOCK BREAKOUT SCANNER ---
elif app_mode == "Stock Breakout Scanner":
    st.title("🔍 Stock Breakout Scanner (Nifty 50)")
    
    if st.button('🚀 Start Scanning Stocks'):
        stocks = ["RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS", "SBI.NS", "BHARTIARTL.NS"]
        results = []
        
        with st.spinner('Analyzing...'):
            for s in stocks:
                try:
                    df = yf.download(s, period="5d", interval="1d", progress=False)
                    if not df.empty:
                        ltp = float(df['Close'].iloc[-1])
                        prev_close = float(df['Close'].iloc[-2])
                        change = round(((ltp - prev_close) / prev_close) * 100, 2)
                        
                        results.append({
                            "Stock": s.replace(".NS", ""),
                            "LTP": round(ltp, 2),
                            "Change %": change
                        })
                except: continue

        if results:
            df_res = pd.DataFrame(results)
            df_res = df_res.sort_values(by="Change %", ascending=False)
            st.table(df_res)
            st.success("Scanning Completed!")

# --- 3. EMA SIGNAL SCANNER ---
elif app_mode == "EMA Signal Scanner":
    st.title("📈 EMA Signal Scanner")
    
    if st.button('🚀 Start EMA Scan'):
        stocks = ["RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS", "SBI.NS"]
        results = []
        
        with st.spinner('Calculating EMA...'):
            for s in stocks:
                try:
                    df = yf.download(s, period="1mo", interval="1d", progress=False)
                    if not df.empty:
                        ltp = float(df['Close'].iloc[-1])
                        ema_20 = float(df['Close'].ewm(span=20, adjust=False).mean().iloc[-1])
                        status = "✅ Above 20 EMA" if ltp > ema_20 else "❌ Below 20 EMA"
                        
                        results.append({
                            "Stock": s.replace(".NS", ""),
                            "LTP": round(ltp, 2),
                            "20 EMA": round(ema_20, 2),
                            "Signal": status
                        })
                except: continue

        if results:
            st.table(pd.DataFrame(results))
            st.success("EMA Scanning Completed!")
