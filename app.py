# =========================================================
# EASYCHARTS ULTRA PRO MAX - FIXED PRODUCTION VERSION
# =========================================================

import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import pandas_ta as ta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
from streamlit_autorefresh import st_autorefresh
from concurrent.futures import ThreadPoolExecutor

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="EasyCharts Ultra Pro",
    layout="wide",
    page_icon="📈"
)

# Custom CSS
st.markdown("""
<style>
.main-header {
    background: linear-gradient(135deg,#0f2027,#203a43,#2c5364);
    padding: 25px; border-radius: 18px; color: white; text-align: center;
    margin-bottom: 20px; box-shadow: 0 0 20px rgba(0,0,0,0.4);
}
.card { padding: 18px; border-radius: 16px; color: white; text-align: center; font-weight: bold; margin-bottom: 15px; }
.buy { background: linear-gradient(135deg,#11998e,#38ef7d); }
.sell { background: linear-gradient(135deg,#ff416c,#ff4b2b); }
.watch { background: linear-gradient(135deg,#396afc,#2948ff); }
.momentum { background: linear-gradient(135deg,#8e2de2,#4a00e0); }
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='main-header'><h1>🚀 EasyCharts Ultra Pro</h1><h4>Advanced Intraday Trading Scanner</h4></div>", unsafe_allow_html=True)

# =========================================================
# SIDEBAR
# =========================================================
st.sidebar.title("⚙️ Scanner Settings")
interval = st.sidebar.selectbox("Select Timeframe", ["5m", "15m", "30m", "1h"], index=1)
period = st.sidebar.selectbox("Select Period", ["5d", "1mo", "3mo"], index=0)
refresh = st.sidebar.checkbox("Auto Refresh (1 Min)")

if refresh:
    st_autorefresh(interval=60000, key="datarefresh")

watch_list = ["RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS", "ITC.NS", "WIPRO.NS", "BHARTIARTL.NS", "TATAMOTORS.NS", "ADANIENT.NS", "LT.NS", "AXISBANK.NS", "MARUTI.NS", "TITAN.NS"]

# =========================================================
# MARKET SENTIMENT
# =========================================================
def market_sentiment():
    try:
        nifty = yf.download("^NSEI", period="5d", interval="15m", progress=False, group_by="column")
        if isinstance(nifty.columns, pd.MultiIndex): nifty.columns = nifty.columns.droplevel(1)
        close = float(nifty['Close'].dropna().iloc[-1])
        prev = float(nifty['Close'].dropna().iloc[-2])
        change = round(((close - prev) / prev) * 100, 2)
        return close, change
    except:
        return None, None

nifty_price, nifty_change = market_sentiment()
if nifty_price:
    col1, col2 = st.columns(2)
    col1.metric("NIFTY", f"₹{nifty_price:,}", f"{nifty_change}%")
    col2.metric("Market Sentiment", "BULLISH 🚀" if nifty_change > 0 else "BEARISH 🔻")
else:
    st.warning("Market Sentiment unavailable")

# =========================================================
# INDICATOR ENGINE
# =========================================================
def calculate_indicators(df):
    close_series = df['Close'].astype(float)
    df['EMA20'] = ta.ema(close_series, length=20)
    df['EMA50'] = ta.ema(close_series, length=50)
    df['RSI'] = ta.rsi(close_series, length=14)
    
    macd = ta.macd(close_series)
    if macd is not None:
        df['MACD'] = macd.iloc[:, 0]
        df['MACD_SIGNAL'] = macd.iloc[:, 2]
    else:
        df['MACD'] = df['MACD_SIGNAL'] = np.nan

    df['VWAP'] = ta.vwap(high=df['High'], low=df['Low'], close=close_series, volume=df['Volume'])
    df['ATR'] = ta.atr(high=df['High'], low=df['Low'], close=close_series, length=14)
    
    supertrend = ta.supertrend(high=df['High'], low=df['Low'], close=close_series, length=10, multiplier=3.0)
    if supertrend is not None:
        df['SUPERT'] = supertrend.iloc[:, 0]
        df['SUPERTD'] = supertrend.iloc[:, 1]
    else:
        df['SUPERT'] = df['SUPERTD'] = np.nan
    return df

# =========================================================
# SINGLE STOCK SCAN FUNCTION (For Parallel Execution)
# =========================================================
def scan_single_stock(stock):
    try:
        df = yf.download(stock, period=period, interval=interval, progress=False, group_by="column")
        if df.empty or len(df) < 55: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.droplevel(1)
        
        df = calculate_indicators(df)
        latest, previous = df.iloc[-1], df.iloc[-2]
        if pd.isna(latest['RSI']): return None

        ltp = round(float(latest['Close']), 2)
        change = round(((latest['Close'] - previous['Close']) / previous['Close']) * 100, 2)
        rsi = round(float(latest['RSI']), 2)
        volume = int(latest['Volume'])
        avg_vol = df['Volume'].tail(20).mean()

        res = {'Stock': stock.replace('.NS', ''), 'Price': ltp, 'Change %': change, 'RSI': rsi, 'Volume': volume}
        
        # Logics
        vol_spike = volume > (avg_vol * 2) if avg_vol > 0 else False
        bull_m = latest['MACD'] > latest['MACD_SIGNAL'] if not pd.isna(latest['MACD']) else False
        bear_m = latest['MACD'] < latest['MACD_SIGNAL'] if not pd.isna(latest['MACD']) else False
        bull_s = latest['SUPERTD'] == 1 if not pd.isna(latest['SUPERTD']) else False
        bear_s = latest['SUPERTD'] == -1 if not pd.isna(latest['SUPERTD']) else False

        if rsi > 60 and latest['Close'] > latest['VWAP'] and latest['Close'] > latest['EMA20'] and bull_m and bull_s and vol_spike:
            return ('BUY', res)
        elif rsi < 40 and latest['Close'] < latest['VWAP'] and bear_m and bear_s:
            return ('SELL', res)
        elif rsi > 55:
            return ('MOMENTUM', res)
        else:
            return ('WATCH', res)
    except:
        return None

# =========================================================
# SCANNER EXECUTION
# =========================================================
if st.button("🔍 START ULTRA SCAN", use_container_width=True):
    buy, sell, momentum, watch = [], [], [], []
    
    with st.spinner("Analyzing Watchlist Stocks via Multi-threading..."):
        with ThreadPoolExecutor(max_workers=10) as executor:
            scanned_results = list(executor.map(scan_single_stock, watch_list))
            
        for item in scanned_results:
            if item:
                cat, data = item
                if cat == 'BUY': buy.append(data)
                elif cat == 'SELL': sell.append(data)
                elif cat == 'MOMENTUM': momentum.append(data)
                elif cat == 'WATCH': watch.append(data)

    # Cards UI
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(f"<div class='card buy'><h2>{len(buy)}</h2>Strong Buy</div>", unsafe_allow_html=True)
    c2.markdown(f"<div class='card sell'><h2>{len(sell)}</h2>Strong Sell</div>", unsafe_allow_html=True)
    c3.markdown(f"<div class='card momentum'><h2>{len(momentum)}</h2>Momentum</div>", unsafe_allow_html=True)
    c4.markdown(f"<div class='card watch'><h2>{len(watch)}</h2>Watchlist</div>", unsafe_allow_html=True)

    # Tables Display
    st.subheader("🚀 Strong Buy Stocks")
    st.dataframe(pd.DataFrame(buy) if buy else pd.DataFrame(columns=['Stock','Price','Change %','RSI']), use_container_width=True, hide_index=True)
    
    st.subheader("🔻 Strong Sell Stocks")
    st.dataframe(pd.DataFrame(sell) if sell else pd.DataFrame(columns=['Stock','Price','Change %','RSI']), use_container_width=True, hide_index=True)

    st.subheader("⚡ Momentum Stocks")
    st.dataframe(pd.DataFrame(momentum) if momentum else pd.DataFrame(columns=['Stock','Price','Change %','RSI']), use_container_width=True, hide_index=True)

    # CSV Export (Safe checking)
    valid_dfs = [pd.DataFrame(x) for x in [buy, sell, momentum, watch] if x]
    if valid_dfs:
        final_df = pd.concat(valid_dfs)
        csv = final_df.to_csv(index=False).encode('utf-8')
        st.download_button(label="⬇️ Download Results CSV", data=csv, file_name="scanner_results.csv", mime="text/csv")

# =========================================================
# CHART SECTION (Moved outside the Scan Button Loop to prevent bugs)
# =========================================================
st.markdown("---")
st.subheader("📈 Interactive Stock Chart")
selected_stock = st.selectbox("Select Stock for Visual Analysis", watch_list)

try:
    df_chart = yf.download(selected_stock, period="5d", interval="15m", progress=False, group_by="column")
    if isinstance(df_chart.columns, pd.MultiIndex): df_chart.columns = df_chart.columns.droplevel(1)
    
    if not df_chart.empty:
        df_chart['EMA20'] = ta.ema(df_chart['Close'], length=20)
        df_chart['EMA50'] = ta.ema(df_chart['Close'], length=50)

        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.7, 0.3])
        fig.add_trace(go.Candlestick(x=df_chart.index, open=df_chart['Open'], high=df_chart['High'], low=df_chart['Low'], close=df_chart['Close'], name='Candles'), row=1, col=1)
        fig.add_trace(go.Scatter(x=df_chart.index, y=df_chart['EMA20'], name='EMA20', line=dict(color='orange')), row=1, col=1)
        fig.add_trace(go.Scatter(x=df_chart.index, y=df_chart['EMA50'], name='EMA50', line=dict(color='cyan')), row=1, col=1)
        fig.add_trace(go.Bar(x=df_chart.index, y=df_chart['Volume'], name='Volume', marker=dict(color='gray')), row=2, col=1)
        fig.update_layout(template='plotly_dark', height=500, xaxis_rangeslider_visible=False, margin=dict(t=10,b=10,l=10,r=10))
        st.plotly_chart(fig, use_container_width=True)
except Exception as e:
    st.error(f"Chart error: {e}")

# =========================================================
# TRADINGVIEW WIDGET & MOVERS
# =========================================================
st.subheader("📊 TradingView Live Widget")
tradingview_html = f"""
<div class="tradingview-widget-container" style="height:550px;">
  <div id="tradingview_chart"></div>
  <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
  <script type="text/javascript">
  new TradingView.widget({{ "width": "100%", "height": 520, "symbol": "NSE:{selected_stock.replace('.NS','')}", "interval": "15", "timezone": "Asia/Kolkata", "theme": "dark", "style": "1", "locale": "en", "enable_publishing": false, "allow_symbol_change": true, "container_id": "tradingview_chart" }});
  </script>
</div>"""
st.components.v1.html(tradingview_html, height=550)

# AI Commentary & Fear/Greed
st.subheader("🤖 AI Market Commentary")
if nifty_change is not None:
    if nifty_change > 0.5: st.success("Market showing strong bullish momentum. Intraday breakout opportunities active.")
    elif nifty_change < -0.5: st.error("Market under selling pressure. Focus on defensive or short setups.")
    else: st.info("Market is consolidating. Wait for clear breakout confirmation.")

st.subheader("Fear & Greed Index")
st.progress(55) # Fixed placeholder or integrate with dynamic source

# Alert Placeholder Info
st.subheader("📢 Alert System Example")
st.code('# Telegram Alert Integration snippet inside app\n# requests.post(url, data=payload)')
