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
