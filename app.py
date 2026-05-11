import streamlit as st
import pandas as pd
import yfinance as yf
import pandas_ta as ta
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Page config
st.set_page_config(
    page_title="Trading Scanner",
    page_icon="📈",
    layout="wide"
)

st.title("📈 Trading Scanner")
st.write(f"Last Update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Ticker list
tickers = ["RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS"]

@st.cache_data(ttl=300)
def scan_stock(ticker):
    try:
        df = yf.download(ticker, period="1y", interval="1d", progress=False)
        
        if df.empty:
            return None
        
        # Calculate indicators
        df['RSI'] = ta.rsi(df['Close'], length=14)
        df['EMA_20'] = ta.ema(df['Close'], length=20)
        df['EMA_50'] = ta.ema(df['Close'], length=50)
        
        last_row = df.iloc[-1]
        
        if pd.isna(last_row['RSI']):
            return None
        
        rsi_val = round(float(last_row['RSI']), 2)
        price = round(float(last_row['Close']), 2)
        ema20 = round(float(last_row['EMA_20']), 2)
        ema50 = round(float(last_row['EMA_50']), 2)
        
        # Signal generation
        if rsi_val > 70:
            signal = "🔴 Sell Signal"
        elif rsi_val < 30:
            signal = "🟢 Buy Signal"
        else:
            signal = "⚪ Neutral"
            
        return {
            "Ticker": ticker,
            "Price": price,
            "RSI": rsi_val,
            "EMA 20": ema20,
            "EMA 50": ema50,
            "Signal": signal
        }
    except Exception as e:
        return None

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    st.markdown("---")
    st.subheader("About")
    st.info("This scanner uses RSI (14) and EMA (20,50) to generate trading signals")
    
    if st.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.rerun()

# Main content
col1, col2 = st.columns([3, 1])

with col1:
    st.subheader("📊 Stock Scanner")

with col2:
    start_scan = st.button("🔍 Start Scanning", type="primary", use_container_width=True)

if start_scan:
    results = []
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, ticker in enumerate(tickers):
        status_text.text(f"Scanning {ticker}...")
        data = scan_stock(ticker)
        if data:
            results.append(data)
        progress_bar.progress((i + 1) / len(tickers))
    
    status_text.text("✅ Scanning complete!")
    progress_bar.empty()
    
    if results:
        df_results = pd.DataFrame(results)
        
        # Color coding for RSI
        def color_rsi(val):
            if isinstance(val, (int, float)):
                if val > 70:
                    return 'color: red'
                elif val < 30:
                    return 'color: green'
            return ''
        
        st.dataframe(
            df_results.style.applymap(color_rsi, subset=['RSI']),
            use_container_width=True,
            hide_index=True
        )
        
        # Download option
        csv = df_results.to_csv(index=False)
        st.download_button(
            label="📥 Download as CSV",
            data=csv,
            file_name=f"scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    else:
        st.error("⚠️ No data found. Please check your internet connection.")
else:
    st.info("👈 Click 'Start Scanning' to begin analysis")

# Footer
st.markdown("---")
st.caption("⚠️ Disclaimer: This is for educational purposes only. Not financial advice.")
