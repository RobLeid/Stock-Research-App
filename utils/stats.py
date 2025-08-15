"""
Statistical Analysis Module
Handles statistical calculations for weekly returns
"""

import pandas as pd
from typing import Dict, Union


def calculate_statistics(returns: pd.Series) -> Dict[str, Union[float, int]]:
    """
    Calculate statistical metrics for weekly returns
    
    Args:
        returns: Series of weekly percentage returns
        
    Returns:
        Dictionary with statistical metrics
    """
    if returns.empty:
        return {}
    
    return {
        'average': returns.mean(),
        'minimum': returns.min(),
        'maximum': returns.max(),
        'std_dev': returns.std(),
        'count': len(returns)
    }


def format_large_number(num: Union[float, int, None]) -> str:
    """
    Format large numbers with appropriate suffixes
    
    Args:
        num: Number to format
        
    Returns:
        Formatted string with suffix (T, B, M, K)
    """
    if num is None:
        return "N/A"
    
    if num >= 1e12:
        return f"${num/1e12:.2f}T"
    elif num >= 1e9:
        return f"${num/1e9:.2f}B"
    elif num >= 1e6:
        return f"${num/1e6:.2f}M"
    elif num >= 1e3:
        return f"${num/1e3:.2f}K"
    else:
        return f"${num:.2f}"