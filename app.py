# =========================================================
# EASYCHARTS ULTRA PRO MAX
# FULL PROFESSIONAL INTRADAY TRADING DASHBOARD
# =========================================================

import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import pandas_ta as ta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import time

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="EasyCharts Ultra Pro",
    layout="wide",
    page_icon="📈"
)

# =========================================================
# CUSTOM CSS
# =========================================================
st.markdown("""
<style>
body {
    background-color: #0e1117;
}

.main-header {
    background: linear-gradient(135deg,#0f2027,#203a43,#2c5364);
    padding: 25px;
    border-radius: 18px;
    color: white;
    text-align: center;
    margin-bottom: 20px;
    box-shadow: 0 0 20px rgba(0,0,0,0.4);
}

.card {
    padding: 18px;
    border-radius: 16px;
    color: white;
    text-align: center;
    font-weight: bold;
    margin-bottom: 15px;
}

.buy {
    background: linear-gradient(135deg,#11998e,#38ef7d);
}

.sell {
    background: linear-gradient(135deg,#ff416c,#ff4b2b);
}

.watch {
    background: linear-gradient(135deg,#396afc,#2948ff);
}

.momentum {
    background: linear-gradient(135deg,#8e2de2,#4a00e0);
}

div[data-testid="stDataFrame"] {
    border-radius: 15px;
    overflow: hidden;
}
</style>
""", unsafe_allow_html=True)

# =========================================================
# HEADER
# =========================================================
st.markdown(
    """
    <div class='main-header'>
        <h1>🚀 EasyCharts Ultra Pro</h1>
        <h4>Advanced Intraday Trading Scanner</h4>
    </div>
    """,
    unsafe_allow_html=True
)

# =========================================================
# SIDEBAR
# =========================================================
st.sidebar.title("⚙️ Scanner Settings")

interval = st.sidebar.selectbox(
    "Select Timeframe",
    ["5m", "15m", "30m", "1h"]
)

period = st.sidebar.selectbox(
    "Select Period",
    ["5d", "1mo", "3mo"]
)

refresh = st.sidebar.checkbox("Auto Refresh")

# =========================================================
# WATCHLIST
# =========================================================
watch_list = [
    "RELIANCE.NS",
    "TCS.NS",
    "INFY.NS",
    "HDFCBANK.NS",
    "ICICIBANK.NS",
    "SBIN.NS",
    "ITC.NS",
    "WIPRO.NS",
    "BHARTIARTL.NS",
    "TATAMOTORS.NS",
    "ADANIENT.NS",
    "LT.NS",
    "AXISBANK.NS",
    "MARUTI.NS",
    "TITAN.NS"
]

# =========================================================
# MARKET SENTIMENT
# =========================================================
def market_sentiment():
    nifty = yf.download(
        "^NSEI",
        period="5d",
        interval="15m",
        progress=False,
        threads=True
    )

    nifty.columns = nifty.columns.get_level_values(0)

    close = float(nifty['Close'].iloc[-1])
    prev = float(nifty['Close'].iloc[-2])

    change = round(((close - prev) / prev) * 100, 2)

    return close, change

# =========================================================
# INDICATOR ENGINE
# =========================================================
def calculate_indicators(df):
    df['EMA20'] = ta.ema(df['Close'], length=20)
    df['EMA50'] = ta.ema(df['Close'], length=50)
    df['RSI'] = ta.rsi(df['Close'], length=14)

    macd = ta.macd(df['Close'])
    df['MACD'] = macd['MACD_12_26_9']
    df['MACD_SIGNAL'] = macd['MACDs_12_26_9']

    df['VWAP'] = ta.vwap(
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        volume=df['Volume']
    )

    atr = ta.atr(
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        length=14
    )

    df['ATR'] = atr

    supertrend = ta.supertrend(
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        length=10,
        multiplier=3.0
    )

    df['SUPERT'] = supertrend['SUPERT_10_3.0']
    df['SUPERTD'] = supertrend['SUPERTd_10_3.0']

    return df

# =========================================================
# SCANNER
# =========================================================
def run_scanner(stock_list):

    buy_list = []
    sell_list = []
    momentum_list = []
    watch_list_out = []

    progress = st.progress(0)

    for idx, stock in enumerate(stock_list):

        try:
            df = yf.download(
                stock,
                period=period,
                interval=interval,
                progress=False,
                threads=True
            )

            if df.empty:
                continue

            df.columns = df.columns.get_level_values(0)

            if len(df) < 60:
                continue

            df = calculate_indicators(df)

            latest = df.iloc[-1]
            previous = df.iloc[-2]

            if pd.isna(latest['RSI']):
                continue

            ltp = round(float(latest['Close']), 2)
            change = round(((latest['Close'] - previous['Close']) / previous['Close']) * 100, 2)
            rsi = round(float(latest['RSI']), 2)
            volume = int(latest['Volume'])

            avg_vol = df['Volume'].tail(20).mean()
            volume_spike = volume > avg_vol * 2

            bullish_macd = latest['MACD'] > latest['MACD_SIGNAL']
            bearish_macd = latest['MACD'] < latest['MACD_SIGNAL']

            bullish_super = latest['SUPERTD'] == 1
            bearish_super = latest['SUPERTD'] == -1

            above_vwap = latest['Close'] > latest['VWAP']
            below_vwap = latest['Close'] < latest['VWAP']

            res = {
                'Stock': stock.replace('.NS', ''),
                'Price': ltp,
                'Change %': change,
                'RSI': rsi,
                'Volume': volume
            }

            # STRONG BUY
            if (
                rsi > 60 and
                above_vwap and
                latest['Close'] > latest['EMA20'] and
                bullish_macd and
                bullish_super and
                volume_spike
            ):
                buy_list.append(res)

            # STRONG SELL
            elif (
                rsi < 40 and
                below_vwap and
                bearish_macd and
                bearish_super
            ):
                sell_list.append(res)

            # MOMENTUM
            elif rsi > 55:
                momentum_list.append(res)

            # WATCHLIST
            else:
                watch_list_out.append(res)

            progress.progress((idx + 1) / len(stock_list))

        except Exception as e:
            st.warning(f"{stock} Error: {e}")

    progress.empty()

    return buy_list, sell_list, momentum_list, watch_list_out

# =========================================================
# PLOTLY CHART
# =========================================================
def create_chart(stock):

    df = yf.download(
        stock,
        period="5d",
        interval="15m",
        progress=False
    )

    if df.empty:
        return

    df.columns = df.columns.get_level_values(0)

    df['EMA20'] = ta.ema(df['Close'], length=20)
    df['EMA50'] = ta.ema(df['Close'], length=50)

    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=[0.7, 0.3]
    )

    fig.add_trace(
        go.Candlestick(
            x=df.index,
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name='Candles'
        ),
        row=1,
        col=1
    )

    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df['EMA20'],
            name='EMA20'
        ),
        row=1,
        col=1
    )

    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df['EMA50'],
            name='EMA50'
        ),
        row=1,
        col=1
    )

    fig.add_trace(
        go.Bar(
            x=df.index,
            y=df['Volume'],
            name='Volume'
        ),
        row=2,
        col=1
    )

    fig.update_layout(
        template='plotly_dark',
        height=700,
        xaxis_rangeslider_visible=False
    )

    st.plotly_chart(fig, use_container_width=True)

# =========================================================
# MAIN DASHBOARD
# =========================================================
try:
    nifty_price, nifty_change = market_sentiment()

    col1, col2 = st.columns(2)

    with col1:
        st.metric("NIFTY", nifty_price, f"{nifty_change}%")

    with col2:
        sentiment = "BULLISH 🚀" if nifty_change > 0 else "BEARISH 🔻"
        st.metric("Market Sentiment", sentiment)

except:
    st.warning("Market Sentiment unavailable")

# =========================================================
# RUN SCANNER BUTTON
# =========================================================
if st.button("🔍 START ULTRA SCAN"):

    buy, sell, momentum, watch = run_scanner(watch_list)

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown(
            f"""
            <div class='card buy'>
            <h2>{len(buy)}</h2>
            Strong Buy
            </div>
            """,
            unsafe_allow_html=True
        )

    with c2:
        st.markdown(
            f"""
            <div class='card sell'>
            <h2>{len(sell)}</h2>
            Strong Sell
            </div>
            """,
            unsafe_allow_html=True
        )

    with c3:
        st.markdown(
            f"""
            <div class='card momentum'>
            <h2>{len(momentum)}</h2>
            Momentum
            </div>
            """,
            unsafe_allow_html=True
        )

    with c4:
        st.markdown(
            f"""
            <div class='card watch'>
            <h2>{len(watch)}</h2>
            Watchlist
            </div>
            """,
            unsafe_allow_html=True
        )

    # =====================================================
    # TABLES
    # =====================================================
    st.subheader("🚀 Strong Buy Stocks")
    if buy:
        st.dataframe(pd.DataFrame(buy), use_container_width=True)
    else:
        st.info("No Buy Signals")

    st.subheader("🔻 Strong Sell Stocks")
    if sell:
        st.dataframe(pd.DataFrame(sell), use_container_width=True)
    else:
        st.info("No Sell Signals")

    st.subheader("⚡ Momentum Stocks")
    if momentum:
        st.dataframe(pd.DataFrame(momentum), use_container_width=True)
    else:
        st.info("No Momentum Stocks")

    st.subheader("👀 Watchlist Stocks")
    if watch:
        st.dataframe(pd.DataFrame(watch), use_container_width=True)
    else:
        st.info("No Watchlist Stocks")

    # =====================================================
    # EXPORT CSV
    # =====================================================
    final_df = pd.concat([
        pd.DataFrame(buy),
        pd.DataFrame(sell),
        pd.DataFrame(momentum),
        pd.DataFrame(watch)
    ])

    csv = final_df.to_csv(index=False).encode('utf-8')

    st.download_button(
        label="⬇️ Download Results CSV",
        data=csv,
        file_name="scanner_results.csv",
        mime="text/csv"
    )

    # =====================================================
    # CHART SECTION
    # =====================================================
    st.subheader("📈 Live Chart")

    selected_stock = st.selectbox(
        "Select Stock",
        watch_list
    )

    create_chart(selected_stock)

    st.success(f"Scan completed at {datetime.now().strftime('%H:%M:%S')}")

# =========================================================
# TRADINGVIEW WIDGET
# =========================================================
st.subheader("📊 TradingView Chart")

tradingview_html = """
<div class="tradingview-widget-container">
  <div id="tradingview_123"></div>
  <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
  <script type="text/javascript">
  new TradingView.widget(
  {
  "width": "100%",
  "height": 650,
  "symbol": "NSE:RELIANCE",
  "interval": "15",
  "timezone": "Asia/Kolkata",
  "theme": "dark",
  "style": "1",
  "locale": "en",
  "toolbar_bg": "#0e1117",
  "enable_publishing": false,
  "allow_symbol_change": true,
  "container_id": "tradingview_123"
}
  );
  </script>
</div>
"""

st.components.v1.html(tradingview_html, height=700)

# =========================================================
# AI MARKET COMMENTARY
# =========================================================
st.subheader("🤖 AI Market Commentary")

try:
    if nifty_change > 1:
        st.success("Market showing strong bullish momentum. Intraday breakout opportunities active.")
    elif nifty_change < -1:
        st.error("Market under selling pressure. Focus on defensive or short setups.")
    else:
        st.info("Market is consolidating. Wait for clear breakout confirmation.")
except:
    st.warning("AI Commentary unavailable")

# =========================================================
# FEAR & GREED METER
# =========================================================
st.subheader("😨 Fear & Greed Meter")

fear_value = np.random.randint(20, 90)

st.progress(fear_value)

if fear_value > 70:
    st.success(f"Greed Zone : {fear_value}")
elif fear_value < 35:
    st.error(f"Fear Zone : {fear_value}")
else:
    st.info(f"Neutral Zone : {fear_value}")

# =========================================================
# TOP GAINERS / LOSERS
# =========================================================
st.subheader("🔥 Market Movers")

market_data = []

for stock in watch_list:
    try:
        df = yf.download(stock, period='2d', interval='15m', progress=False)

        if df.empty:
            continue

        df.columns = df.columns.get_level_values(0)

        last = float(df['Close'].iloc[-1])
        prev = float(df['Close'].iloc[-2])

        change = round(((last - prev) / prev) * 100, 2)

        market_data.append({
            'Stock': stock.replace('.NS', ''),
            'Change %': change
        })

    except:
        pass

if market_data:
    movers_df = pd.DataFrame(market_data)

    gainers = movers_df.sort_values('Change %', ascending=False).head(5)
    losers = movers_df.sort_values('Change %', ascending=True).head(5)

    g1, g2 = st.columns(2)

    with g1:
        st.success("🚀 Top Gainers")
        st.dataframe(gainers, use_container_width=True)

    with g2:
        st.error("🔻 Top Losers")
        st.dataframe(losers, use_container_width=True)

# =========================================================
# TELEGRAM ALERT PLACEHOLDER
# =========================================================
st.subheader("📢 Alert System")

st.code('''
# Telegram Alert Integration Example

import requests

BOT_TOKEN = "YOUR_BOT_TOKEN"
CHAT_ID = "YOUR_CHAT_ID"

message = "BUY SIGNAL DETECTED"

url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

payload = {
    "chat_id": CHAT_ID,
    "text": message
}

requests.post(url, data=payload)
''')

# =========================================================
# AUTO REFRESH
# =========================================================
if refresh:
    time.sleep(30)
    st.rerun()
