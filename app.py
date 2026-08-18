import streamlit as st
import pandas as pd
import numpy as np

# -------------------------------------------------------------
# 1. APP CONFIGURATION
# -------------------------------------------------------------
st.set_page_config(
    page_title="Advanced DSE Tech Analyzer", 
    layout="wide", 
    page_icon="📈"
)

st.title("🚀 Advanced DSE Technical Analysis Engine")
st.markdown("Professional quantitative screening framework incorporating MACD, Bollinger Bands, ATR Volatility, and Momentum Oscillators.")

# -------------------------------------------------------------
# 2. ADVANCED MATHEMATICAL INDICATOR FUNCTIONS
# -------------------------------------------------------------
def calculate_macd(series, fast=12, slow=26, signal=9):
    exp1 = series.ewm(span=fast, adjust=False).mean()
    exp2 = series.ewm(span=slow, adjust=False).mean()
    macd_line = exp1 - exp2
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram

def calculate_bollinger_bands(series, window=20, num_std=2):
    middle_band = series.rolling(window=window).mean()
    std_dev = series.rolling(window=window).std()
    upper_band = middle_band + (num_std * std_dev)
    lower_band = middle_band - (num_std * std_dev)
    return upper_band, middle_band, lower_band

def calculate_atr(high, low, close, window=14):
    tr1 = high - low
    tr2 = abs(high - close.shift())
    tr3 = abs(low - close.shift())
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.rolling(window=window).mean()
    return atr

def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

# -------------------------------------------------------------
# 3. MOCK DSE DATA GENERATION & MATRIX MAPPING
# -------------------------------------------------------------
@st.cache_data(ttl=300)
def load_advanced_dse_data():
    np.random.seed(101)
    tickers = ["KPPL", "SQURPHARMA", "BATBC", "RENATA", "BEACONPHAR", "LANKABANGL", "BXPHARMA", "OLYMPIC"] + [f"DSE_STK_{i}" for i in range(9, 50)]
    n = len(tickers)
    
    data = []
    for ticker in tickers:
        base_price = np.random.uniform(20, 450)
        # Generate 60 days of synthetic price movement
        price_series = base_price * (1 + np.random.normal(0.001, 0.02, 60).cumsum())
        high_series = price_series * np.random.uniform(1.002, 1.018, 60)
        low_series = price_series * np.random.uniform(0.982, 0.998, 60)
        vol_series = np.random.uniform(40000, 2000000, 60)
        
        close_p = pd.Series(price_series)
        high_p = pd.Series(high_series)
        low_p = pd.Series(low_series)
        
        # Calculate Indicators
        _, _, hist = calculate_macd(close_p)
        upper, _, lower = calculate_bollinger_bands(close_p)
        atr = calculate_atr(high_p, low_p, close_p)
        rsi = calculate_rsi(close_p)
        
        # Determine MACD Crossover Status
        current_hist = hist.iloc[-1]
        prev_hist = hist.iloc[-2]
        if current_hist > 0 and prev_hist <= 0:
            cross_status = "Bullish Crossover"
        elif current_hist < 0 and prev_hist >= 0:
            cross_status = "Bearish Crossover"
        elif current_hist > 0:
            cross_status = "Bullish Momentum"
        else:
            cross_status = "Bearish Momentum"

        data.append({
            'Ticker': ticker,
            'Close': close_p.iloc[-1],
            'RSI_14': rsi.iloc[-1],
            'MACD_Status': cross_status,
            'BB_Upper': upper.iloc[-1],
            'BB_Lower': lower.iloc[-1],
            'ATR_Volatility': atr.iloc[-1],
            'Volume_Today': vol_series[-1]
        })
        
    return pd.DataFrame(data)

raw_df = load_advanced_dse_data()

# -------------------------------------------------------------
# 4. SIDEBAR FILTER CONTROLS
# -------------------------------------------------------------
st.sidebar.header("⚙️ Quantitative Funnel")

st.sidebar.subheader("Momentum Filters")
rsi_range = st.sidebar.slider("RSI (14) Range", 0, 100, (40, 75))
macd_filter = st.sidebar.selectbox("MACD Filter", ["All", "Bullish Crossover", "Bullish Momentum", "Bearish Momentum", "Bearish Crossover"])

st.sidebar.subheader("Risk & Volatility Management")
max_atr = st.sidebar.slider("Max ATR Volatility Threshold", 1.0, 30.0, 12.0)

# -------------------------------------------------------------
# 5. EXECUTE FILTERING MATRIX
# -------------------------------------------------------------
df = raw_df.copy()

df = df[(df['RSI_14'] >= rsi_range[0]) & (df['RSI_14'] <= rsi_range[1])]
df = df[df['ATR_Volatility'] <= max_atr]

if macd_filter != "All":
    df = df[df['MACD_Status'] == macd_filter]

# -------------------------------------------------------------
# 6. DASHBOARD DISPLAY LAYOUT
# -------------------------------------------------------------
c1, c2, c3 = st.columns(3)
c1.metric("Total Universe Evaluated", len(raw_df))
c2.metric("Qualifying Technical Setups", len(df))
c3.metric("Screening Efficiency", f"{(len(df)/len(raw_df))*100:.1f}%")

st.markdown("---")
st.subheader("📊 Quantitative Indicator Matrix")

if len(df) > 0:
    view_df = df.copy()
    view_df['Close'] = view_df['Close'].round(2)
    view_df['RSI_14'] = view_df['RSI_14'].round(1)
    view_df['BB_Upper'] = view_df['BB_Upper'].round(2)
    view_df['BB_Lower'] = view_df['BB_Lower'].round(2)
    view_df['ATR_Volatility'] = view_df['ATR_Volatility'].round(2)
    view_df['Volume_Today'] = view_df['Volume_Today'].astype(int)
    
    st.dataframe(view_df, use_container_width=True)
    
    # Deep Indicator Breakdown Tool
    st.markdown("---")
    st.subheader("🔍 Single Asset Technical Inspector")
    chosen_ticker = st.selectbox("Select equity identifier:", view_df['Ticker'].tolist())
    
    if chosen_ticker:
        record = df[df['Ticker'] == chosen_ticker].iloc[0]
        col_x, col_y, col_z = st.columns(3)
        
        col_x.metric("Last Price", f"{record['Close']:.2f} BDT")
        col_y.metric("Average True Range (ATR)", f"{record['ATR_Volatility']:.2f}")
        col_z.metric("Momentum Status", record['MACD_Status'])
        
        # Volatility / Band position evaluation
        if record['Close'] >= record['BB_Upper'] * 0.98:
            st.warning(f"⚠️ **{chosen_ticker}** is testing its upper Bollinger Band boundary. Watch for potential overextension or breakout continuation.")
        elif record['Close'] <= record['BB_Lower'] * 1.02:
            st.info(f"💡 **{chosen_ticker}** is approaching its lower Bollinger Band support level, indicating potential mean-reversion opportunity.")
        else:
            st.success(f"✅ **{chosen_ticker}** is trading safely within normal volatility boundaries.")
else:
    st.warning("No securities match the selected multi-tier advanced indicators. Adjust parameters in the sidebar.")
