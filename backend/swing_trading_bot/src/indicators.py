import pandas as pd


def is_bullish_engulfing(df: pd.DataFrame) -> pd.Series:
    """Detect bullish engulfing candlestick patterns."""
    return (
        (df['close'] > df['open'])
        & (df['close'].shift(1) < df['open'].shift(1))
        & (df['close'] > df['open'].shift(1))
        & (df['open'] < df['close'].shift(1))
    )


def is_bearish_engulfing(df: pd.DataFrame) -> pd.Series:
    """Detect bearish engulfing candlestick patterns."""
    return (
        (df['close'] < df['open'])
        & (df['close'].shift(1) > df['open'].shift(1))
        & (df['close'] < df['open'].shift(1))
        & (df['open'] > df['close'].shift(1))
    )
