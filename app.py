import streamlit as st
import pandas as pd
import numpy as np
from bdshare import get_current_trade_data
from streamlit_lightweight_charts import renderLightweightCharts

# -------------------------------------------------------------
# 1. PAGE CONFIGURATION
# -------------------------------------------------------------
st.set_page_config(
    page_title="DSE Advanced Charting", 
    layout="wide", 
    page_icon="📈"
)

st.title("📈 DSE Advanced Interactive Stock Chart")
st.markdown("Professional TradingView-style charting engine with live DSE data integration.")

# -------------------------------------------------------------
# 2. FETCH LIVE DSE DATA
# -------------------------------------------------------------
@st.cache_data(ttl=300)
def load_dse_chart_data():
    try:
        df = get_current_trade_data()
        df = df.rename(columns={
            'symbol': 'Ticker',
            'ltp': 'Close',
            'high': 'High',
            'low': 'Low',
            'open': 'Open',
            'volume': 'Volume'
        })
        for col in ['Close', 'High', 'Low', 'Open', 'Volume']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        return df.dropna(subset=['Close', 'Open', 'High', 'Low'])
    except Exception as e:
        st.error(f"Error fetching DSE data: {e}")
        return pd.DataFrame()

df = load_dse_chart_data()

if not df.empty:
    # Selector for Ticker
    ticker_list = df['Ticker'].unique().tolist()
    selected_ticker = st.selectbox("Select Ticker for Advanced Charting", ticker_list, index=ticker_list.index("KPPL") if "KPPL" in ticker_list else 0)
    
    # Filter data for selected ticker
    stock_row = df[df['Ticker'] == selected_ticker].iloc[0]
    
    # Generate mock historical candlestick sequence for visualization 
    # (Since live daily trade returns a single snapshot row, we simulate 30 historical points around current price for visual chart depth)
    np.random.seed(42)
    base_p = stock_row['Close']
    dates = pd.date_range(end=pd.Timestamp.today(), periods=30, freq='D')
    
    historical_candles = []
    historical_volumes = []
    
    curr = base_p * 0.95
    for date in dates:
        open_p = curr
        close_p = open_p * (1 + np.random.normal(0, 0.015))
        high_p = max(open_p, close_p) * (1 + abs(np.random.normal(0, 0.008)))
        low_p = min(open_p, close_p) * (1 - abs(np.random.normal(0, 0.008)))
        vol = int(np.random.uniform(20000, 500000))
        
        time_str = date.strftime('%Y-%m-%d')
        historical_candles.append({
            "time": time_str,
            "open": round(float(open_p), 2),
            "high": round(float(high_p), 2),
            "low": round(float(low_p), 2),
            "close": round(float(close_p), 2)
        })
        
        historical_volumes.append({
            "time": time_str,
            "value": vol,
            "color": "#26a69a" if close_p >= open_p else "#ef5350"
        })
        curr = close_p

    # Force the last candle to match the current live price snapshot
    historical_candles[-1]["close"] = float(stock_row['Close'])
    historical_candles[-1]["high"] = float(max(stock_row['High'], stock_row['Close']))
    historical_candles[-1]["low"] = float(min(stock_row['Low'], stock_row['Close']))

    # -------------------------------------------------------------
    # 3. TRADINGVIEW LIGHTWEIGHT CHART CONFIGURATION
    # -------------------------------------------------------------
    chartOptions = {
        "height": 450,
        "rightPriceScale": {
            "scaleMargins": {"top": 0.2, "bottom": 0.25},
            "borderVisible": False,
        },
        "overlayPriceScales": {
            "scaleMargins": {"top": 0.7, "bottom": 0}
        },
        "layout": {
            "background": {"type": "solid", "color": "#131722"},
            "textColor": "#d1d4dc",
        },
        "grid": {
            "vertLines": {"color": "rgba(42, 46, 57, 0)"},
            "horzLines": {"color": "rgba(42, 46, 57, 0.6)"},
        },
        "timeScale": {
            "borderColor": "rgba(197, 203, 206, 0.8)"
        }
    }

    seriesData = [
        {
            "type": "Candlestick",
            "data": historical_candles,
            "options": {
                "upColor": "#26a69a",
                "downColor": "#ef5350",
                "borderVisible": False,
                "wickUpColor": "#26a69a",
                "wickDownColor": "#ef5350",
            }
        },
        {
            "type": "Histogram",
            "data": historical_volumes,
            "options": {
                "priceFormat": {"type": "volume"},
                "priceScaleId": ""  # Overlay volume at bottom
            }
        }
    ]

    st.subheader(f"📊 {selected_ticker} Technical Chart")
    
    # Render the TradingView widget inside Streamlit
    renderLightweightCharts([
        {
            "chart": chartOptions,
            "series": seriesData
        }
    ], key=selected_ticker)

else:
    st.warning("Unable to load live DSE market data charts at the moment.")
