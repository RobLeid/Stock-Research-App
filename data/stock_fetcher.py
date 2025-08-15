"""
Stock Data Fetching Module
Handles all stock data API calls and caching
"""

import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime


@st.cache_data(ttl=300)  # Cache for 5 minutes
def fetch_stock_data(symbol: str, start_date: datetime, end_date: datetime) -> pd.DataFrame:
    """
    Fetch stock data from Yahoo Finance for a specific date range
    
    Args:
        symbol: Stock ticker symbol
        start_date: Start date for data fetch
        end_date: End date for data fetch
        
    Returns:
        DataFrame with stock price data
    """
    try:
        stock = yf.Ticker(symbol)
        data = stock.history(start=start_date, end=end_date)
        if data.empty:
            raise ValueError(f"No data found for symbol {symbol}")
        return data
    except Exception as e:
        st.error(f"Error fetching data for {symbol}: {str(e)}")
        return pd.DataFrame()


@st.cache_data(ttl=300)  # Cache for 5 minutes
def fetch_max_stock_data(symbol: str) -> pd.DataFrame:
    """
    Fetch maximum available stock data from Yahoo Finance
    
    Args:
        symbol: Stock ticker symbol
        
    Returns:
        DataFrame with all available stock price data
    """
    try:
        stock = yf.Ticker(symbol)
        data = stock.history(period="max")
        if data.empty:
            raise ValueError(f"No data found for symbol {symbol}")
        return data
    except Exception as e:
        st.error(f"Error fetching maximum data for {symbol}: {str(e)}")
        return pd.DataFrame()


def get_latest_price(symbol: str) -> float:
    """
    Get the most recent trading day close price
    
    Args:
        symbol: Stock ticker symbol
        
    Returns:
        Latest closing price, or None if error
    """
    try:
        stock = yf.Ticker(symbol)
        # Get last 5 trading days to ensure we have recent data
        recent_data = stock.history(period="5d")
        if not recent_data.empty:
            return recent_data['Close'].iloc[-1]
        return None
    except Exception as e:
        st.error(f"Error fetching latest price for {symbol}: {str(e)}")
        return None


@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_stock_info(symbol: str) -> dict:
    """
    Get comprehensive stock information
    
    Args:
        symbol: Stock ticker symbol
        
    Returns:
        Dictionary with stock information
    """
    try:
        stock = yf.Ticker(symbol)
        info = stock.info
        
        # Extract key information, handling missing data gracefully
        stock_info = {
            'name': info.get('longName', info.get('shortName', symbol)),
            'sector': info.get('sector', 'N/A'),
            'industry': info.get('industry', 'N/A'),
            'market_cap': info.get('marketCap'),
            'enterprise_value': info.get('enterpriseValue'),
            'pe_ratio': info.get('trailingPE'),
            'forward_pe': info.get('forwardPE'),
            'price_to_book': info.get('priceToBook'),
            'dividend_yield': info.get('dividendYield'),
            'beta': info.get('beta'),
            'fifty_two_week_high': info.get('fiftyTwoWeekHigh'),
            'fifty_two_week_low': info.get('fiftyTwoWeekLow'),
            'average_volume': info.get('averageVolume'),
            'description': info.get('longBusinessSummary', ''),
            'country': info.get('country', 'N/A'),
            'currency': info.get('currency', 'USD')
        }
        
        return stock_info
    except Exception as e:
        st.warning(f"Could not fetch detailed information for {symbol}: {str(e)}")
        return {'name': symbol}