import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Simple Scanner", layout="wide")

st.title("🚀 My Trading Scanner")

# ലളിതമായ ഇൻഡക്സ് ചെക്കർ
target_indices = {"NIFTY 50": "^NSEI", "BANK NIFTY": "^NSEBANK"}

cols = st.columns(len(target_indices))

for i, (name, ticker) in enumerate(target_indices.items()):
    data = yf.download(ticker, period="1d", interval="15m", progress=False)
    if not data.empty:
        # ലേറ്റസ്റ്റ് വില എടുക്കുന്നു
        price = round(data['Close'].iloc[-1], 2)
        with cols[i]:
            st.metric(name, price)

st.success("Scanner is running successfully!") 
import streamlit as st
import yfinance as yf
import pandas as pd

# Page Configuration
st.set_page_config(page_title="Pro Trading Scanner", layout="wide")

st.title("🚀 My Trading Scanner Hub")

# --- 1. INDEX WATCHLIST (Top Row) ---
st.subheader("📊 Market Indices")
target_indices = {"NIFTY 50": "^NSEI", "BANK NIFTY": "^NSEBANK", "FINNIFTY": "NIFTY_FIN_SERVICE.NS"}

cols = st.columns(3)
for i, (name, ticker) in enumerate(target_indices.items()):
    data = yf.download(ticker, period="1d", interval="15m", progress=False)
    if not data.empty:
        price = round(data['Close'].iloc[-1], 2)
        with cols[i]:
            st.metric(name, price)

st.markdown("---")

# --- 2. STOCK SCANNER SECTION ---
st.subheader("🔍 Stock Breakout Scanner (Nifty 50)")

# സ്കാനിംഗ് തുടങ്ങാനുള്ള ബട്ടൺ
if st.button('🚀 Start Scanning Stocks'):
    # കുറച്ച് പ്രധാനപ്പെട്ട സ്റ്റോക്കുകൾ (കൂടുതൽ വേണമെങ്കിൽ ഇവിടെ ചേർക്കാം)
    stocks = ["RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS", "SBI.NS", "BHARTIARTL.NS"]
    
    results = []
    
    with st.spinner('Analyzing Market Data...'):
        for s in stocks:
            try:
                # കഴിഞ്ഞ 5 ദിവസത്തെ ഡാറ്റ എടുക്കുന്നു
                df = yf.download(s, period="5d", interval="1d", progress=False)
                if not df.empty:
                    ltp = round(df['Close'].iloc[-1], 2)
                    prev_close = df['Close'].iloc[-2]
                    change = round(((ltp - prev_close) / prev_close) * 100, 2)
                    
                    results.append({
                        "Stock": s.replace(".NS", ""),
                        "LTP": ltp,
                        "Change %": change
                    })
            except:
                continue

    # റിസൾട്ട് ടേബിൾ ആയി കാണിക്കുന്നു
    if results:
        df_results = pd.DataFrame(results)
        # Change % അനുസരിച്ച് ക്രമീകരിക്കുന്നു
        df_results = df_results.sort_values(by="Change %", ascending=False)
        st.table(df_results)
        st.success("Scanning Completed!")
    else:
        st.error("Could not fetch stock data. Please try again.")

# Auto-refresh info
st.sidebar.info("Refresh the page to update Index prices.")
