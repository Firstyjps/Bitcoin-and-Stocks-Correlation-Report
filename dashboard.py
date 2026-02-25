import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Bitcoin Rolling Correlation", layout="wide")
st.title("📈 Bitcoin Rolling Correlation Dashboard")

TICKERS = {
    "Bitcoin": "BTC-USD",
    "Gold": "GC=F",
    "S&P 500": "^GSPC",
    "NASDAQ": "^IXIC"
}

PERIODS = {
    "30 Days": "1mo",
    "6 Months": "6mo",
    "1 Year": "1y",
    "All Time": "max"
}

st.sidebar.header("⚙️ การตั้งค่ากราฟ")
selected_assets = st.sidebar.multiselect(
    "เลือกสินทรัพย์เทียบกับ Bitcoin:",
    options=[k for k in TICKERS.keys() if k != "Bitcoin"],
    default=["Gold", "NASDAQ"]
)

selected_period = st.sidebar.selectbox(
    "เลือกช่วงเวลา:",
    options=list(PERIODS.keys()),
    index=2
)

rolling_window = st.sidebar.slider(
    "Rolling Window (จำนวนวันสำหรับการคำนวณ Correlation ในแต่ละจุด):", 
    min_value=7, max_value=90, value=30, step=1
)

@st.cache_data(ttl=3600)
def load_data(assets, period_key):
    assets_to_load = ["Bitcoin"] + assets 
    period_val = PERIODS[period_key]
    tickers_list = [TICKERS[a] for a in assets_to_load]
    
    df = yf.download(tickers_list, period=period_val)
    
    if len(tickers_list) == 1:
        close_df = df[['Close']].copy()
        close_df.columns = [tickers_list[0]]
    else:
        close_df = df['Close'].copy()
        
    reverse_map = {v: k for k, v in TICKERS.items()}
    close_df = close_df.rename(columns=reverse_map)
    
    close_df = close_df.ffill().dropna()
    
    pct_return_df = ((close_df / close_df.iloc[0]) - 1) * 100
    
    return pct_return_df, close_df

if selected_assets:
    pct_df, raw_df = load_data(selected_assets, selected_period)
    
    fig_price = px.line(
        pct_df,
        title=f"Percentage Return Comparison ({selected_period})",
        labels={"value": "Return (%)", "Date": "Date", "variable": "Asset"},
        template="plotly_dark"
    )
    fig_price.update_layout(hovermode="x unified")
    st.plotly_chart(fig_price, use_container_width=True)
    
    st.subheader(f"🔗 {rolling_window}-Day Rolling Pearson Correlation with Bitcoin")
    st.markdown("แสดงการเปลี่ยนแปลงของความสัมพันธ์เมื่อเวลาผ่านไป (Y-Axis ล็อคที่ -1 ถึง 1)")
    
    daily_returns = raw_df.pct_change().dropna()
    
    rolling_corr_df = pd.DataFrame(index=daily_returns.index)
    
    for asset in selected_assets:
        rolling_corr_df[asset] = daily_returns[asset].rolling(window=rolling_window).corr(daily_returns['Bitcoin'])
    
    rolling_corr_df = rolling_corr_df.dropna()
    
    if not rolling_corr_df.empty:
        fig_corr = go.Figure()
        
        for asset in selected_assets:
            fig_corr.add_trace(go.Scatter(
                x=rolling_corr_df.index, 
                y=rolling_corr_df[asset],
                mode='lines',
                name=asset
            ))
            
        fig_corr.update_layout(
            template="plotly_dark",
            title=f"Rolling Correlation vs Bitcoin (Window={rolling_window} days)",
            xaxis_title="Date",
            yaxis_title="Correlation (-1 to 1)",
            yaxis=dict(range=[-1.1, 1.1]),
            hovermode="x unified"
        )
        
        fig_corr.add_hline(y=0, line_dash="dash", line_color="white", opacity=0.5)
        
        st.plotly_chart(fig_corr, use_container_width=True)
    else:
        st.info(f"ข้อมูลไม่เพียงพอสำหรับการคำนวณ Rolling Correlation (ต้องการข้อมูลมากกว่า {rolling_window} วัน) โปรดเลือกช่วงเวลาที่ยาวขึ้น")

else:
    st.warning("👈 กรุณาเลือกสินทรัพย์อย่างน้อย 1 รายการจากเมนูด้านซ้ายเพื่อเปรียบเทียบกับ Bitcoin")