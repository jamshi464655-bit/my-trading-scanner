import streamlit as st
import pandas as pd
import yfinance as yf
import numpy as np
from datetime import datetime, timedelta
import talib

# --- PAGE SETUP ---
st.set_page_config(page_title="EasyCharts Pro - Nifty 500 Scanner", layout="wide", initial_sidebar_state="expanded")

# --- CSS STYLING (For the entire dashboard) ---
st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        color: white;
        margin-bottom: 30px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .main-header h1 { color: white; margin: 0; font-size: 2.5rem; }
    .main-header p { color: rgba(255,255,255,0.8); margin: 5px 0 0; }
    .stat-box {
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        color: white;
        margin: 10px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .stat-box h2 { color: white; margin: 0 0 10px; font-size: 2.5rem; }
    .stat-box p { color: rgba(255,255,255,0.9); margin: 0; }
    .pre-breakout { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }
    .live-breakout { background: linear-gradient(135deg, #2af598 0%, #009efd 100%); }
    .momentum { background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); }
    
    .status-alert { padding: 10px; border-radius: 8px; font-weight: bold; margin: 10px 0; text-align: center; }
    .alert-orange { background-color: #ff9800; color: white; }
    .alert-green { background-color: #4caf50; color: white; }
    .alert-blue { background-color: #2196f3; color: white; }
    
    .scan-status { padding: 15px; border-radius: 8px; font-weight: bold; margin-top: 20px; }
    .status-scanning { background-color: #e3f2fd; color: #1565c0; border: 1px solid #1565c0; }
    .status-completed { background-color: #e8f5e9; color: #2e7d32; border: 1px solid #2e7d32; }
    
    .stApp { background-color: #f8f9fa; }
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white; border: none; font-weight: bold; border-radius: 8px;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- GLOBAL VARIABLES & FUNCTIONS ---
audio_alert_url = "https://www.soundjay.com/buttons/beep-07a.mp3"

def play_alert():
    audio_html = f"""
    <audio autoplay>
        <source src="{audio_alert_url}" type="audio/mpeg">
    </audio>
    """
    st.markdown(audio_html, unsafe_allow_html=True)

# Function to safely load data (using a larger, quality set of symbols)
def load_stock_symbols(segment="NIFTY 50"):
    # Pre-defined list of high-quality Indian stocks for better performance
    all_quality_stocks = [
        # Nifty 50
        "ADANIENT.NS", "ADANIPORTS.NS", "APOLLOHOSP.NS", "ASIANPAINT.NS", "AXISBANK.NS", "BAJAJ-AUTO.NS", "BAJFINANCE.NS", "BAJAJFINSV.NS", "BPCL.NS", "BHARTIARTL.NS", "BRITANNIA.NS", "CIPLA.NS", "COALINDIA.NS", "DIVISLAB.NS", "DRREDDY.NS", "EICHERMOT.NS", "GRASIM.NS", "HCLTECH.NS", "HDFCBANK.NS", "HDFCLIFE.NS", "HEROMOTOCO.NS", "HINDALCO.NS", "HINDUNILVR.NS", "ICICIBANK.NS", "ITC.NS", "INDUSINDBK.NS", "INFY.NS", "JSWSTEEL.NS", "KOTAKBANK.NS", "LTIM.NS", "LT.NS", "M&M.NS", "MARUTI.NS", "NESTLEIND.NS", "NTPC.NS", "ONGC.NS", "POWERGRID.NS", "RELIANCE.NS", "SBILIFE.NS", "SBIN.NS", "SUNPHARMA.NS", "TCS.NS", "TATACONSUM.NS", "TATAMOTORS.NS", "TATASTEEL.NS", "TECHM.NS", "TITAN.NS", "ULTRACEMCO.NS", "UPL.NS", "WIPRO.NS",
        # Next 50 (Subset)
        "ADANIGREEN.NS", "DLF.NS", "DMART.NS", "GAIL.NS", "INDIGO.NS", "PNB.NS", "RVNL.NS", "ZOMATO.NS"
    ]
    
    return all_quality_stocks

# Function to run the main scanner logic
def analyze_nifty500_stocks(stocks_to_scan):
    pre_breakout, live_breakout, momentum = [], [], []
    
    tickers_string = " ".join(stocks_to_scan)
    
    st.markdown(f'<div class="scan-status status-scanning">📋 Scanning {len(stocks_to_scan)} stocks from Nifty 500...</div>', unsafe_allow_html=True)
    
    progress_bar = st.progress(0)
    
    try:
        # Download data for all stocks in one batch for speed
        with st.spinner("Downloading and analyzing market data..."):
            data = yf.download(tickers_string, period="1y", interval="1d", group_by='ticker', progress=False)
        
        for i, s in enumerate(stocks_to_scan):
            try:
                progress = (i + 1) / len(stocks_to_scan)
                progress_bar.progress(progress)
                
                # Check if data exists for this symbol
                if s not in data.columns.levels[0]:
                    continue
                    
                df = data[s].dropna()
                
                if len(df) < 150: # Need enough data for 200 EMA
                    continue
                
                ltp = round(df['Close'].iloc[-1], 2)
                prev_close = round(df['Close'].iloc[-2], 2)
                change_pct = round(((ltp - prev_close) / prev_close) * 100, 2)
                
                # Calculate required indicators using numpy for speed where possible
                close_prices = df['Close'].to_numpy()
                ema200 = talib.EMA(close_prices, timeperiod=200)[-1]
                rsi = talib.RSI(close_prices, timeperiod=14)[-1]
                
                # Volume logic
                curr_vol = df['Volume'].iloc[-1]
                avg_vol = df['Volume'].rolling(20).mean().iloc[-1]
                vol_ratio = curr_vol / avg_vol if avg_vol > 0 else 0
                
                # Setup details for results
                setup_details = {
                    "Stock": s.replace(".NS", ""),
                    "LTP": f"₹{ltp}",
                    "Change": f"{change_pct}%",
                    "RSI": round(rsi, 1),
                    "Volume": f"{round(vol_ratio, 1)}x"
                }
                
                # Setup conditions based on standard strategies
                if change_pct > 1 and ltp > ema200 and rsi > 55 and vol_ratio > 2.0:
                    setup_details["Change"] = f'<span style="color:#2e7d32">{setup_details["Change"]}</span>'
                    live_breakout.append(setup_details)
                elif 0.95 * ema200 <= ltp <= 1.05 * ema200 and rsi < 40:
                    pre_breakout.append(setup_details)
                elif change_pct > 0.5 and ltp > ema200 and rsi > 60:
                    setup_details["Change"] = f'<span style="color:#2e7d32">{setup_details["Change"]}</span>'
                    momentum.append(setup_details)
                    
            except Exception:
                continue
                
        progress_bar.empty()
        
    except Exception as e:
        st.error(f"Scanner error: {e}")
        
    return pre_breakout, live_breakout, momentum

def render_setup_details(col, details_list):
    with col:
        if not details_list:
            st.markdown('<div class="status-alert alert-blue">No setups found</div>', unsafe_allow_html=True)
            return
            
        st.markdown(f'<div class="status-alert alert-green">Total {len(details_list)} Setups Found</div>', unsafe_allow_html=True)
        
        for stock in details_list:
            # Render each stock details clearly
            st.markdown(f"**Symbol:** {stock['Stock']}")
            col1, col2 = st.columns([1, 1])
            col1.markdown(f"**LTP:** {stock['LTP']}")
            col2.markdown(f"**Change:** {stock['Change']}", unsafe_allow_html=True)
            col1, col2 = st.columns([1, 1])
            col1.markdown(f"**RSI:** {stock['RSI']}")
            col2.markdown(f"**Volume:** {stock['Volume']}")
            st.markdown("---")

# --- SIDEBAR NAVIGATION ---
st.sidebar.markdown("""
    <div style="text-align: center;">
        <h2>⚙️ Pro Scanner HUB</h2>
        <p>Market Tools developed by J.</p>
    </div>
""", unsafe_allow_html=True)

page = st.sidebar.selectbox("Choose Scanner Tool", [
    "📉 Stock Pro Scanner", 
    "📈 All-in-One Multi-Index",
    "💎 Option Pro Scanner"
])

# Load symbols once to be used by all pages
if 'all_symbols' not in st.session_state:
    st.session_state.all_symbols = load_stock_symbols("NIFTY 50")
    st.session_state.quality_symbols = st.session_state.all_symbols # For easy access

# Handle different page choices
if page == "📈 All-in-One Multi-Index":
    # Insert code from All_inO_ne_Multi_Index_Pro_Scanner
    st.title("🎯 All-in-One Multi-Index Master Scanner")
    # ... other content from Multi_Index scanner

elif page == "💎 Option Pro Scanner":
    # Insert code from Option Pro Scanner
    st.title("Ultimate Option Pro Master Scanner")
    # ... other content from Option Pro scanner

elif page == "📉 Stock Pro Scanner":
    # Handle the main Stock Scanner logic
    
    # --- PAGE HEADER ---
    st.markdown("""
    <div class="main-header">
        <h1>EasyCharts Pro - Nifty 500 Scanner</h1>
        <p>AI-Powered Multi-Indicator Stock Scanner (Subset of Nifty 500 Stocks)</p>
    </div>
    """, unsafe_allow_html=True)
    
    # --- SCANNING CONTROL SECTION ---
    stocks_segment = st.selectbox("Select Market Segment to Scan", ["NIFTY 50", "NEXT 50 (Quality Subset)"])
    
    # Set the list to scan based on selection
    if stocks_segment == "NIFTY 50":
        st.session_state.current_scan_list = load_stock_symbols("NIFTY 50")
    else:
        st.session_state.current_scan_list = st.session_state.quality_symbols # Using pre-loaded quality subset
        
    start_scan = st.button("🚀 START MARKET SCAN")
    
    # --- MAIN CONTENT AREA ---
    if start_scan:
        st.markdown(f'<div class="scan-status status-scanning">📋 Scanning {len(st.session_state.current_scan_list)} stocks...</div>', unsafe_allow_html=True)
        
        pre, live, mom = analyze_nifty500_stocks(st.session_state.current_scan_list)
        
        # Play alert sound if a live breakout is found
        if live:
            play_alert()
            st.success("🎯 Live breakout identified!")
            st.balloons()

        # --- SUMMARY STATISTICS CARDS ---
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f'<div class="stat-box pre-breakout"><h2>{len(pre)}</h2><p>Pre-Breakout Setups</p></div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="stat-box live-breakout"><h2>{len(live)}</h2><p>Live Breakouts</p></div>', unsafe_allow_html=True)
        with col3:
            st.markdown(f'<div class="stat-box momentum"><h2>{len(mom)}</h2><p>Momentum Stocks</p></div>', unsafe_allow_html=True)
            
        # --- BUTTON ROW (FOR FILTERING) ---
        col1, col2, col3 = st.columns(3)
        col1.markdown(f'<div class="status-alert alert-orange">🔵 Pre-Breakout Setups</div>', unsafe_allow_html=True)
        col2.markdown(f'<div class="status-alert alert-green">🟢 Live Breakouts</div>', unsafe_allow_html=True)
        col3.markdown(f'<div class="status-alert alert-blue">🔥 Strong Momentum</div>', unsafe_allow_html=True)
            
        # --- DETAIL RESULTS SECTION ---
        st.markdown("---")
        res_col1, res_col2, res_col3 = st.columns([1,1,1])
        
        render_setup_details(res_col1, pre)
        render_setup_details(res_col2, live)
        render_setup_details(res_col3, mom)
        
        # Footer Scan Completed status
        completion_time = datetime.now().strftime('%I:%M:%S %p')
        st.markdown(f'---')
        st.markdown(f'<div class="scan-status status-completed">✅ Scan completed at {completion_time}</div>', unsafe_allow_html=True)

    else:
        st.markdown('<div class="status-alert alert-blue">Select a segment and click the button above to start the scan.</div>', unsafe_allow_html=True)

# Footer info (constant on all pages)
st.sidebar.markdown("---")
st.sidebar.info(f"⏰ Current Time: {datetime.now().strftime('%I:%M:%S %p')}")
