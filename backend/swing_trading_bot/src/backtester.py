import pandas as pd


def backtest_signals(df: pd.DataFrame, initial_capital: float = 10000.0) -> pd.DataFrame:
    """Simple backtest engine for entry/exit signals."""
    df = df.copy()
    df['position'] = df['signal'].replace({-1: 0}).ffill().fillna(0)
    df['returns'] = df['close'].pct_change().fillna(0)
    df['strategy_returns'] = df['position'].shift(1) * df['returns']
    df['equity_curve'] = (1 + df['strategy_returns']).cumprod() * initial_capital
    return df
