# Stock Trading Signals

A simple stock market analysis application using 10-day moving average with ±1 standard deviation strategy.

## Features

- **Buy/Sell/Hold Signals**: Shows which stocks to buy, sell, or hold based on ±1 standard deviation
- **Date Selection**: Dropdown to select any date and see signals for that specific date
- **Interactive Charts**: Visual trends for each stock with Bollinger Bands and signal markers
- **Time Period Filters**: View trends for different time periods (All Data, Last 7 Days, Last 14 Days)

## Files

- `streamlit_app.py` - Streamlit web application
- `requirements.txt` - Required Python packages
- Stock CSV files: `Eternal.csv`, `ADANIGREEN.csv`, `PAYTM.csv`, `NTPC.csv`, `DLF.csv`

## How to Run

### 1. Install Requirements
```
pip install -r requirements.txt
```

### 2. Run Streamlit App
```bash
streamlit run streamlit_app.py
```

