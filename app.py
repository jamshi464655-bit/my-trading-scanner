import streamlit as st
import pandas as pd
import yfinance as yf
import pandas_ta as ta
from datetime import datetime

# Page config
st.set_page_config(page_title="Trading Scanner", layout="wide")

st.title("📈 My Trading Scanner")
st.write(f"Last Update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# ചിഹ്നങ്ങൾ (Stocks) - നിങ്ങൾക്ക് ഇഷ്ടമുള്ളവ ഇവിടെ ചേർക്കാം
tickers = ["RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS"]

def scan_stock(ticker):
    try:
        # ഡാറ്റ ഡൗൺലോഡ് ചെയ്യുന്നു
        df = yf.download(ticker, period="1y", interval="1d", progress=False)
        if df.empty:
            return None
        
        # RSI കണക്കാക്കുന്നു
        df['RSI'] = ta.rsi(df['Close'], length=14)
        
        # EMA കണക്കാക്കുന്നു
        df['EMA_20'] = ta.ema(df['Close'], length=20)
        df['EMA_50'] = ta.ema(df['Close'], length=50)
        
        last_row = df.iloc[-1]
        
        # കണ്ടീഷനുകൾ
        rsi_val = round(float(last_row['RSI']), 2)
        price = round(float(last_row['Close']), 2)
        
        status = "Neutral"
        if rsi_val > 70:
            status = "Overbought (Sell?)"
        elif rsi_val < 30:
            status = "Oversold (Buy?)"
            
        return {
            "Ticker": ticker,
            "Price": price,
            "RSI": rsi_val,
            "Status": status
        }
    except:
        return None

# സ്കാനിംഗ് ബട്ടൺ
if st.button('Start Scanning'):
    results = []
    with st.spinner('Scanning Markets...'):
        for t in tickers:
            data = scan_stock(t)
            if data:
                results.append(data)
    
    if results:
        res_df = pd.DataFrame(results)
        st.table(res_df)
    else:
        st.error("No data found. Please check your internet or tickers.")
