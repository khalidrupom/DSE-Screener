import streamlit as st
import pandas as pd
import numpy as np

# -------------------------------------------------------------
# 1. PAGE CONFIGURATION & MOBILE OPTIMIZATION
# -------------------------------------------------------------
st.set_page_config(
    page_title="DSE Hot Stock Screener", 
    page_icon="📈", 
    layout="wide"
)

st.title("🔥 DSE Hot Stock & Technical Screener")
st.markdown("Advanced multi-tier screening funnel with built-in technical analysis (RSI, EMA, Momentum).")

# -------------------------------------------------------------
# 2. TECHNICAL ANALYSIS FUNCTIONS (Pure Pandas/Numpy Engine)
# -------------------------------------------------------------
def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def calculate_ema(series, span):
    return series.ewm(span=span, adjust=False).mean()

# -------------------------------------------------------------
# 3. DATA ENGINE (Google Sheets Connector or Mock Engine)
# -------------------------------------------------------------
@st.cache_data(ttl=300)
def load_stock_data():
    # You can replace this URL later with your published Google Sheet CSV link
    np.random.seed(42)
    tickers = ["KPPL", "SQURPHARMA", "BATBC", "RENATA", "BEACONPHAR", "LANKABANGL", "BXPHARMA", "OLYMPIC", "Grameenphone", "BEXIMCO"] + [f"STOCK_{i}" for i in range(11, 60)]
    
    n = len(tickers)
    base_prices = np.random.uniform(20, 400, n)
    
    df = pd.DataFrame({
        'Ticker': tickers,
        'Category': np.random.choice(['A', 'B', 'N'], n, p=[0.7, 0.2, 0.1]),
        'Close_Price': base_prices,
        'PaidUp_Mn': np.random.uniform(200, 3000, n),
        'Volume_Today': np.random.uniform(50000, 2500000, n),
        'Volume_20D_Avg': np.random.uniform(40000, 2000000, n),
        'PE_Ratio': np.random.uniform(6, 35, n),
        'Div_Yield': np.random.uniform(0, 8, n)
    })
    
    # Simulate historical price series for technical indicators
    simulated_history = []
    for price in df['Close_Price']:
        hist = price * (1 + np.random.normal(0, 0.015, 50).cumsum())
        simulated_history.append(pd.Series(hist))
    
    df['RSI_14'] = [calculate_rsi(h).iloc[-1] for h in simulated_history]
    df['EMA_50'] = [calculate_ema(h, 50).iloc[-1] for h in simulated_history]
    df['EMA_200'] = [calculate_ema(h, 200).iloc[-1] for h in simulated_history]
    df['Vol_Spike_Ratio'] = df['Volume_Today'] / df['Volume_20D_Avg']
    
    return df

raw_df = load_stock_data()

# -------------------------------------------------------------
# 4. MOBILE SIDEBAR: THE ADVANCED SCREENING FUNNEL
# -------------------------------------------------------------
st.sidebar.header("⚙️ Funnel Filters")

# Tier 1: Risk & Liquidity
st.sidebar.subheader("1. Risk & Liquidity")
selected_cats = st.sidebar.multiselect("Allowed Categories", ['A', 'B', 'N'], default=['A', 'B'])
min_vol = st.sidebar.number_input("Min Today's Volume", value=100000, step=50000)

# Tier 2: Fundamentals
st.sidebar.subheader("2. Fundamentals")
pe_slider = st.sidebar.slider("P/E Ratio Range", 0, 50, (5, 25))
min_div_yield = st.sidebar.slider("Min Dividend Yield (%)", 0.0, 10.0, 1.0)

# Tier 3: Technical Indicators
st.sidebar.subheader("3. Technical Setup")
rsi_slider = st.sidebar.slider("RSI (14) Range", 10, 90, (40, 70))
require_uptrend = st.sidebar.checkbox("Price Above 50 EMA (Uptrend)", value=True)
require_vol_surge = st.sidebar.checkbox("Smart Money Volume Surge (>1.2x)", value=True)

# -------------------------------------------------------------
# 5. EXECUTE FILTERING LOGIC
# -------------------------------------------------------------
df = raw_df.copy()

df = df[df['Category'].isin(selected_cats)]
df = df[df['Volume_Today'] >= min_vol]
df = df[(df['PE_Ratio'] >= pe_slider[0]) & (df['PE_Ratio'] <= pe_slider[1])]
df = df[df['Div_Yield'] >= min_div_yield]
df = df[(df['RSI_14'] >= rsi_slider[0]) & (df['RSI_14'] <= rsi_slider[1])]

if require_uptrend:
    df = df[df['Close_Price'] > df['EMA_50']]
if require_vol_surge:
    df = df[df['Vol_Spike_Ratio'] >= 1.2]

# Calculate a "Hot Momentum Score" for ranking
if len(df) > 0:
    df['Hot_Score'] = (
        (df['Vol_Spike_Ratio'] * 30) + 
        ((df['RSI_14'] - 40) * 2) + 
        (df['Div_Yield'] * 5)
    ).round(1)
    df = df.sort_values(by='Hot_Score', ascending=False)

# -------------------------------------------------------------
# 6. DASHBOARD DISPLAY
# -------------------------------------------------------------
c1, c2, c3 = st.columns(3)
c1.metric("Total Universe", len(raw_df))
c2.metric("Hot Setups Found", len(df))
survival = (len(df) / len(raw_df)) * 100 if len(raw_df) > 0 else 0
c3.metric("Funnel Pass Rate", f"{survival:.1f}%")

st.markdown("---")
st.subheader("🏆 Filtered Hot Stocks Ranking")

if len(df) > 0:
    # Format view columns
    view_df = df[[
        'Ticker', 'Category', 'Close_Price', 'PE_Ratio', 
        'RSI_14', 'Vol_Spike_Ratio', 'Hot_Score'
    ]].copy()
    
    view_df['Close_Price'] = view_df['Close_Price'].round(2)
    view_df['PE_Ratio'] = view_df['PE_Ratio'].round(2)
    view_df['RSI_14'] = view_df['RSI_14'].round(1)
    view_df['Vol_Spike_Ratio'] = view_df['Vol_Spike_Ratio'].round(2)
    
    st.dataframe(view_df, use_container_width=True)
    
    # Detailed Stock Inspector
    st.markdown("---")
    st.subheader("🔍 Deep Stock Inspector")
    chosen_stock = st.selectbox("Select a ticker to analyze technical health:", view_df['Ticker'].tolist())
    
    if chosen_stock:
        st_data = df[df['Ticker'] == chosen_stock].iloc[0]
        col_a, col_b, col_c = st.columns(3)
        col_a.metric("Current Price", f"{st_data['Close_Price']:.2f} BDT")
        col_b.metric("RSI Status", f"{st_data['RSI_14']:.1f} ({'Overbought' if st_data['RSI_14']>70 else 'Oversold' if st_data['RSI_14']<30 else 'Neutral'})")
        col_c.metric("Volume Momentum", f"{st_data['Vol_Spike_Ratio']:.2f}x Average")
        
        if st_data['Close_Price'] > st_data['EMA_50']:
            st.success(f"✅ **{chosen_stock}** is trading above its 50-day Exponential Moving Average, confirming a healthy mid-term technical uptrend.")
        else:
            st.warning(f"⚠️ **{chosen_stock}** is trading below its 50-day EMA. Exercise caution regarding trend continuation.")
else:
    st.warning("No stocks match your strict technical criteria. Try adjusting your RSI or volume filters in the sidebar.")
