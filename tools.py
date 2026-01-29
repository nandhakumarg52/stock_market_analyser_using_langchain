import os
import matplotlib.pyplot as plt
import pandas as pd
import requests
from utils import safe_execute
from langchain.tools import tool
from dotenv import load_dotenv
load_dotenv()

BASE_URL = "https://stock.indianapi.in"
API_KEY = os.getenv("INDIAN_API_KEY")


@safe_execute
def _get(endpoint: str, params: dict | None = None):
    if not API_KEY:
        raise ValueError("INDIAN_API_KEY not found in environment variables")

    headers = {
        "X-Api-Key": API_KEY,
        "Accept": "application/json"
    }

    resp = requests.get(f"{BASE_URL}{endpoint}", headers=headers, params=params, timeout=10)

    if resp.status_code != 200:
        raise ValueError(f"API returned {resp.status_code}: {resp.text}")

    data = resp.json()
    if not data:
        raise ValueError("Empty response received from API")

    return {
        "status": "success",
        "data": data
    }


@tool
@safe_execute
def get_market_news():
    """
    Fetch latest stock market and company-related news.
    """
    return _get("/news")


@tool
@safe_execute
def get_ipo_data():
    """
    Fetch latest IPO data from Indian Stock Exchange API.
    Includes upcoming, ongoing, and recently listed IPO information.
    """
    return _get("/ipo")


@tool
@safe_execute
def get_stock_by_name(name: str):
    """
    Get detailed stock data for a company by name.
    Example: name="Reliance"
    """
    return _get("/stock", {"name": name})


@tool
@safe_execute
def industry_search(query: str):
    """
    Search companies by industry.
    """
    return _get("/industry_search", {"query": query})


@tool
@safe_execute
def mutual_fund_search(query: str):
    """
    Search mutual funds by keyword.
    """
    return _get("/mutual_fund_search", {"query": query})


@tool
@safe_execute
def get_trending_stocks():
    """
    Get top gainers and losers in real-time.
    """
    return _get("/trending")


@tool
@safe_execute
def fetch_52_week_high_low():
    """
    Fetch stocks with 52 week high and low data.
    """
    return _get("/fetch_52_week_high_low_data")


@tool
@safe_execute
def nse_most_active():
    """
    Get NSE most active stocks by volume.
    """
    return _get("/NSE_most_active")


@tool
@safe_execute
def bse_most_active():
    """
    Get BSE most active stocks by volume.
    """
    return _get("/BSE_most_active")


@tool
@safe_execute
def get_mutual_funds():
    """
    Fetch latest mutual fund data.
    """
    return _get("/mutual_funds")


@tool
@safe_execute
def price_shockers():
    """
    Get stocks with significant price movements.
    """
    return _get("/price_shockers")


@tool
@safe_execute
def get_commodities():
    """
    Get active commodity futures market data.
    """
    return _get("/commodities")


@tool
@safe_execute
def stock_target_price(stock_id: str):
    """
    Get analyst target price and recommendation data.
    """
    return _get("/stock_target_price", {"stock_id": stock_id})


@tool
@safe_execute
def stock_forecasts(
    stock_id: str,
    measure_code: str,   # EPS, ROE, SAL, etc
    period_type: str,    # Annual / Interim
    data_type: str,      # Actuals / Estimates
    age: str             # OneWeekAgo, ThirtyDaysAgo, etc
):
    """
    Fetch forecast data for a stock.
    """
    params = {
        "stock_id": stock_id,
        "measure_code": measure_code,
        "period_type": period_type,
        "data_type": data_type,
        "age": age,
    }
    return _get("/stock_forecasts", params)


@tool
@safe_execute
def historical_data(
    stock_name: str,
    period: str = "5yr",
    filter: str = "default"
):
    """
    Fetch historical stock price/financial data.
    """
    params = {
        "stock_name": stock_name,
        "period": period,
        "filter": filter,
    }
    return _get("/historical_data", params)


@tool
@safe_execute
def historical_stats(
    stock_name: str,
    stats: str
):
    """
    Fetch historical statistics like quarter_results, balancesheet, etc.
    """
    params = {
        "stock_name": stock_name,
        "stats": stats,
    }
    return _get("/historical_stats", params)


data_collector_agent_tools = [
        get_stock_by_name,
        get_trending_stocks,
        fetch_52_week_high_low,
        nse_most_active,
        bse_most_active,
        industry_search,
        get_mutual_funds,
        mutual_fund_search,
        price_shockers,
        get_commodities,
        historical_data,
        historical_stats,
        stock_target_price,
        stock_forecasts,
        get_ipo_data,
        get_market_news
    ]


@tool
@safe_execute
def plot_stock_price_trend(data: list):
    """
    Visualize stock price trend over time.
    Input: data -> list of dicts with keys: date, close
    Example: [{"date": "2026-01-01", "close": 3500}, ...]
    """
    df = pd.DataFrame(data)
    df["date"] = pd.to_datetime(df["date"])

    plt.figure(figsize=(10, 5))
    plt.plot(df["date"], df["close"])
    plt.title("Stock Price Trend")
    plt.xlabel("Date")
    plt.ylabel("Closing Price")
    plt.show()


@tool
@safe_execute
def plot_volume_chart(data: list):
    """
    Visualize trading volume over time.
    Input: data -> list of dicts with keys: date, volume
    """
    df = pd.DataFrame(data)
    df["date"] = pd.to_datetime(df["date"])

    plt.figure(figsize=(10, 5))
    plt.bar(df["date"], df["volume"])
    plt.title("Trading Volume")
    plt.xlabel("Date")
    plt.ylabel("Volume")
    plt.show()


@tool
@safe_execute
def plot_moving_averages(data: list, short_window: int = 20, long_window: int = 50):
    """
    Visualize stock price with moving averages.
    Input: data -> list of dicts with keys: date, close
    """
    df = pd.DataFrame(data)
    df["date"] = pd.to_datetime(df["date"])
    df["SMA_short"] = df["close"].rolling(window=short_window).mean()
    df["SMA_long"] = df["close"].rolling(window=long_window).mean()

    plt.figure(figsize=(10, 5))
    plt.plot(df["date"], df["close"], label="Close Price")
    plt.plot(df["date"], df["SMA_short"], label=f"SMA {short_window}")
    plt.plot(df["date"], df["SMA_long"], label=f"SMA {long_window}")
    plt.title("Moving Averages")
    plt.xlabel("Date")
    plt.ylabel("Price")
    plt.legend()
    plt.show()


@tool
@safe_execute
def plot_candlestick_like(data: list):
    """
    Visualize OHLC data in a simple candlestick-style chart.
    Input: data -> list of dicts with keys: date, open, high, low, close
    (Lightweight version without mplfinance)
    """
    df = pd.DataFrame(data)
    df["date"] = pd.to_datetime(df["date"])

    plt.figure(figsize=(10, 5))
    for _, row in df.iterrows():
        plt.plot([row["date"], row["date"]], [row["low"], row["high"]])
        plt.plot([row["date"], row["date"]], [row["open"], row["close"]], linewidth=4)

    plt.title("OHLC (Candlestick Style)")
    plt.xlabel("Date")
    plt.ylabel("Price")
    plt.show()


@tool
@safe_execute
def plot_sector_allocation(data: dict):
    """
    Visualize portfolio or market sector allocation as a pie chart.
    Input: data -> dict like {"IT": 35, "Banking": 25, "Pharma": 15, "FMCG": 25}
    """
    sectors = list(data.keys())
    values = list(data.values())

    plt.figure(figsize=(6, 6))
    plt.pie(values, labels=sectors, autopct="%1.1f%%")
    plt.title("Sector Allocation")
    plt.show()


data_analyst_tools = [
    plot_stock_price_trend,
    plot_volume_chart,
    plot_moving_averages,
    plot_candlestick_like,
    plot_sector_allocation
]