"""
Weekly Return Calculation Module
Handles all week-over-week percentage calculations and timeframe analysis
"""

import pandas as pd
from typing import Optional
from datetime import datetime, timedelta


def calculate_weekly_returns(data: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate week-over-week percentage returns
    
    Args:
        data: DataFrame with stock price data
        
    Returns:
        DataFrame with weekly returns
    """
    if data.empty:
        return pd.DataFrame()
    
    # Resample to weekly data (Friday close, or last trading day of week)
    weekly_data = data['Close'].resample('W-FRI', label='right', closed='right').last()
    
    # Calculate week-over-week percentage change
    weekly_returns = weekly_data.pct_change().dropna() * 100
    
    return weekly_returns.to_frame(name='Weekly_Return_Pct')


def get_timeframe_data(full_data: pd.DataFrame, years: Optional[int] = None) -> pd.DataFrame:
    """
    Extract data for a specific timeframe from full dataset
    
    Args:
        full_data: Complete stock data DataFrame
        years: Number of years back from latest date (None for all data)
        
    Returns:
        DataFrame with data for specified timeframe
    """
    if full_data.empty:
        return pd.DataFrame()
    
    if years is None:
        return full_data
    
    # Ensure years is an integer
    years = int(years) if years is not None else None
    
    latest_date = full_data.index.max()
    start_date = latest_date - pd.DateOffset(years=years)
    
    return full_data[full_data.index >= start_date]


def calculate_multi_timeframe_stats(full_data: pd.DataFrame) -> dict:
    """
    Calculate weekly return statistics for multiple timeframes
    
    Args:
        full_data: Complete stock data DataFrame
        
    Returns:
        Dictionary with statistics for different timeframes
    """
    timeframes = {
        'max': None,  # All available data
        '10yr': 10,
        '5yr': 5,
        '3yr': 3,
        '1yr': 1
    }
    
    results = {}
    
    for period_name, years in timeframes.items():
        period_data = get_timeframe_data(full_data, years)
        
        if period_data.empty:
            continue
            
        # Calculate weekly returns for this period
        weekly_returns = calculate_weekly_returns(period_data)
        
        if weekly_returns.empty:
            continue
            
        # Calculate statistics
        from utils.stats import calculate_statistics
        stats = calculate_statistics(weekly_returns['Weekly_Return_Pct'])
        
        # Add period-specific info
        if stats:
            stats['data_start'] = period_data.index.min()
            stats['data_end'] = period_data.index.max()
            stats['years_of_data'] = len(period_data) / 252  # Approximate trading days per year
            
        results[period_name] = stats
    
    return results


def predict_future_week_price(current_price: float, stats: dict, weeks_ahead: int = 1) -> dict:
    """
    Predict potential stock prices for future weeks based on historical weekly returns with proper compounding
    
    Args:
        current_price: Most recent closing price
        stats: Dictionary with statistical metrics (average, minimum, maximum)
        weeks_ahead: Number of weeks ahead to predict (default: 1)
        
    Returns:
        Dictionary with predicted prices for different scenarios
    """
    if not stats or 'average' not in stats or weeks_ahead < 1:
        return {}
    
    # Calculate target date (weeks_ahead from today, landing on a Friday)
    today = datetime.now()
    days_to_add = weeks_ahead * 7
    target_date = today + timedelta(days=days_to_add)
    
    # Adjust to next Friday if not already a Friday (weekday() returns 0=Monday, 6=Sunday)
    days_until_friday = (4 - target_date.weekday()) % 7
    if days_until_friday > 0:
        target_date = target_date + timedelta(days=days_until_friday)
    
    # Calculate predicted prices using proper compounding: price * (1 + return/100)^weeks
    expected_price = current_price * ((1 + stats['average'] / 100) ** weeks_ahead)
    optimistic_price = current_price * ((1 + stats['maximum'] / 100) ** weeks_ahead)
    pessimistic_price = current_price * ((1 + stats['minimum'] / 100) ** weeks_ahead)
    
    # Calculate total percentage changes
    expected_total_change = ((expected_price / current_price) - 1) * 100
    optimistic_total_change = ((optimistic_price / current_price) - 1) * 100
    pessimistic_total_change = ((pessimistic_price / current_price) - 1) * 100
    
    return {
        'current_price': current_price,
        'expected_price': expected_price,
        'optimistic_price': optimistic_price,
        'pessimistic_price': pessimistic_price,
        'expected_change': expected_total_change,
        'optimistic_change': optimistic_total_change,
        'pessimistic_change': pessimistic_total_change,
        'weeks_ahead': weeks_ahead,
        'target_date': target_date,
        'target_date_str': target_date.strftime('%B %d, %Y'),
        'weekly_avg_return': stats['average'],
        'weekly_max_return': stats['maximum'],
        'weekly_min_return': stats['minimum']
    }

# Keep the old function for backward compatibility
def predict_current_week_price(current_price: float, stats: dict) -> dict:
    """
    Predict potential stock prices for current week based on historical weekly returns
    (Wrapper for predict_future_week_price with weeks_ahead=1)
    
    Args:
        current_price: Most recent closing price
        stats: Dictionary with statistical metrics (average, minimum, maximum)
        
    Returns:
        Dictionary with predicted prices for different scenarios
    """
    return predict_future_week_price(current_price, stats, weeks_ahead=1)