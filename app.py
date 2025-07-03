import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# Set page config
st.set_page_config(
    page_title="Stock Trading Signals",
    page_icon="📈",
    layout="wide"
)

# Title
st.title("Stock Trading Signals Dashboard")
st.markdown("**10-Day Moving Average with ±1 Standard Deviation Strategy**")

@st.cache_data
def load_and_analyze_data():
    """Load and analyze stock data"""
    files = [
        ('Eternal', 'Eternal.csv'),
        ('ADANIGREEN', 'ADANIGREEN.csv'),
        ('PAYTM', 'PAYTM.csv'),
        ('NTPC', 'NTPC.csv'),
        ('DLF', 'DLF.csv')
    ]
    
    dfs = []
    for stock_name, file in files:
        try:
            df = pd.read_csv(file)
            df.columns = df.columns.str.strip()
            df = df.sort_values(['Date', 'Expiry']).groupby('Date').first().reset_index()
            df['Stock'] = stock_name
            dfs.append(df)
        except FileNotFoundError:
            st.error(f"File {file} not found!")
            continue
    
    if not dfs:
        return pd.DataFrame()
    
    combined_df = pd.concat(dfs, ignore_index=True)
    combined_df['Date'] = pd.to_datetime(combined_df['Date'], format='%d-%b-%Y')
    combined_df = combined_df.sort_values(['Stock', 'Date'])
    
    # Analysis with 10-day moving average and ±1 std dev
    window_size = 10
    result_df = pd.DataFrame()
    
    for stock in combined_df['Stock'].unique():
        stock_data = combined_df[combined_df['Stock'] == stock].copy()
        stock_data = stock_data.sort_values('Date')
        
        stock_data['MA_10'] = stock_data['Close'].rolling(window=window_size, min_periods=1).mean()
        stock_data['STD_10'] = stock_data['Close'].rolling(window=window_size, min_periods=1).std()
        stock_data['Upper_Band'] = stock_data['MA_10'] + (1 * stock_data['STD_10'])
        stock_data['Lower_Band'] = stock_data['MA_10'] - (1 * stock_data['STD_10'])
        
        # Generate signals
        stock_data['Signal'] = 'Hold'
        stock_data.loc[stock_data['Close'] < stock_data['Lower_Band'], 'Signal'] = 'Buy'
        stock_data.loc[stock_data['Close'] > stock_data['Upper_Band'], 'Signal'] = 'Sell'
        
        # Calculate standard deviations
        stock_data['Std_Deviations'] = (stock_data['Close'] - stock_data['MA_10']) / stock_data['STD_10']
        
        result_df = pd.concat([result_df, stock_data])
    
    result_df = result_df.reset_index(drop=True)
    return result_df

# Load data
with st.spinner("Loading data..."):
    data = load_and_analyze_data()

if data.empty:
    st.error("No data available. Please check your CSV files.")
    st.stop()

st.sidebar.header("Controls")

available_dates = sorted(data['Date'].dt.date.unique())
selected_date = st.sidebar.selectbox(
    "Select Date:",
    available_dates,
    index=len(available_dates)-1  
)

selected_datetime = pd.to_datetime(selected_date)

date_data = data[data['Date'] == selected_datetime]

# Main content
st.header(f"Trading Signals for {selected_date}")

if not date_data.empty:
    col1, col2, col3 = st.columns(3)
    
    buy_signals = date_data[date_data['Signal'] == 'Buy']
    sell_signals = date_data[date_data['Signal'] == 'Sell']
    hold_signals = date_data[date_data['Signal'] == 'Hold']
    
    with col1:
        st.subheader("BUY Signals")
        if not buy_signals.empty:
            for _, row in buy_signals.iterrows():
                st.success(f"**{row['Stock']}**: Rs.{row['Close']:.2f}")
                st.caption(f"MA: Rs.{row['MA_10']:.2f} | {row['Std_Deviations']:.2f}σ")
        else:
            st.info("No buy signals")
    
    with col2:
        st.subheader("SELL Signals")
        if not sell_signals.empty:
            for _, row in sell_signals.iterrows():
                st.error(f"**{row['Stock']}**: Rs.{row['Close']:.2f}")
                st.caption(f"MA: Rs.{row['MA_10']:.2f} | {row['Std_Deviations']:.2f}σ")
        else:
            st.info("No sell signals")
    
    with col3:
        st.subheader("HOLD Signals")
        if not hold_signals.empty:
            for _, row in hold_signals.iterrows():
                st.warning(f"**{row['Stock']}**: Rs.{row['Close']:.2f}")
                st.caption(f"MA: Rs.{row['MA_10']:.2f} | {row['Std_Deviations']:.2f}σ")
        else:
            st.info("No hold signals")
else:
    st.warning(f"No data available for {selected_date}")

# Stock trends section
st.header("Stock Price Trends")

# Stock selection for charts
selected_stocks = st.multiselect(
    "Select stocks to display:",
    options=sorted(data['Stock'].unique()),
    default=sorted(data['Stock'].unique())
)

if selected_stocks:
    # Time period selection
    time_period = st.selectbox(
        "Select time period:",
        ["All Data", "Last 7 Days", "Last 14 Days"],
        index=0
    )
    
    # Filter data based on time period
    if time_period == "Last 7 Days":
        cutoff_date = data['Date'].max() - pd.Timedelta(days=7)
        chart_data = data[data['Date'] >= cutoff_date]
    elif time_period == "Last 14 Days":
        cutoff_date = data['Date'].max() - pd.Timedelta(days=14)
        chart_data = data[data['Date'] >= cutoff_date]
    else:
        chart_data = data
    
    # Create charts for each selected stock
    for stock in selected_stocks:
        stock_data = chart_data[chart_data['Stock'] == stock].copy()
        
        if stock_data.empty:
            continue
        
        # Create plotly chart
        fig = go.Figure()
        
        # Add price line
        fig.add_trace(go.Scatter(
            x=stock_data['Date'],
            y=stock_data['Close'],
            mode='lines+markers',
            name='Close Price',
            line=dict(color='blue', width=2)
        ))
        
        # Add moving average
        fig.add_trace(go.Scatter(
            x=stock_data['Date'],
            y=stock_data['MA_10'],
            mode='lines',
            name='10-Day MA',
            line=dict(color='orange', dash='dash')
        ))
        
        # Add Bollinger Bands
        fig.add_trace(go.Scatter(
            x=stock_data['Date'],
            y=stock_data['Upper_Band'],
            mode='lines',
            name='Upper Band (+1σ)',
            line=dict(color='red', dash='dot'),
            showlegend=False
        ))
        
        fig.add_trace(go.Scatter(
            x=stock_data['Date'],
            y=stock_data['Lower_Band'],
            mode='lines',
            name='Lower Band (-1σ)',
            line=dict(color='green', dash='dot'),
            fill='tonexty',
            fillcolor='rgba(128,128,128,0.1)',
            showlegend=True
        ))
        
        # Add buy/sell signals
        buy_points = stock_data[stock_data['Signal'] == 'Buy']
        sell_points = stock_data[stock_data['Signal'] == 'Sell']
        
        if not buy_points.empty:
            fig.add_trace(go.Scatter(
                x=buy_points['Date'],
                y=buy_points['Close'],
                mode='markers',
                name='Buy Signal',
                marker=dict(color='green', size=10, symbol='triangle-up')
            ))
        
        if not sell_points.empty:
            fig.add_trace(go.Scatter(
                x=sell_points['Date'],
                y=sell_points['Close'],
                mode='markers',
                name='Sell Signal',
                marker=dict(color='red', size=10, symbol='triangle-down')
            ))
        
        # Update layout
        fig.update_layout(
            title=f'{stock} - Price Analysis with Trading Signals',
            xaxis_title='Date',
            yaxis_title='Price (Rs.)',
            hovermode='x unified',
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)

# Summary section
st.header("Summary")

# Signal counts for selected date
if not date_data.empty:
    signal_summary = date_data['Signal'].value_counts()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Buy Signals", signal_summary.get('Buy', 0))
    with col2:
        st.metric("Sell Signals", signal_summary.get('Sell', 0))
    with col3:
        st.metric("Hold Signals", signal_summary.get('Hold', 0))

# Strategy explanation
st.subheader("Trading Strategy")
st.write("""
**Strategy Rules:**
- **BUY**: When stock price falls below (10-day Moving Average - 1 Standard Deviation)
- **SELL**: When stock price rises above (10-day Moving Average + 1 Standard Deviation)  
- **HOLD**: When stock price is within ±1 standard deviation of the moving average
""")

# Footer
st.markdown("---")
st.caption("Data source: Stock CSV files | Strategy: 10-day MA with ±1σ Bollinger Bands")
