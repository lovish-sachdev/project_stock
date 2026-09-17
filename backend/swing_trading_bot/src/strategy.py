import pandas as pd


def generate_signals(df: pd.DataFrame) -> pd.DataFrame:
    """Generate entry and exit signals from OHLC price data."""
    df = df.copy()
    df['bullish_engulfing'] = (
        (df['close'] > df['open'])
        & (df['close'].shift(1) < df['open'].shift(1))
        & (df['close'] > df['open'].shift(1))
        & (df['open'] < df['close'].shift(1))
    )
    df['bearish_engulfing'] = (
        (df['close'] < df['open'])
        & (df['close'].shift(1) > df['open'].shift(1))
        & (df['close'] < df['open'].shift(1))
        & (df['open'] > df['close'].shift(1))
    )
    df['signal'] = 0
    df.loc[df['bullish_engulfing'], 'signal'] = 1
    df.loc[df['bearish_engulfing'], 'signal'] = -1
    return df


def grid_trading_strategy(investment,no_of_shares, last_actioned_price, current_price, grid_size, grid_price):
    """Determine whether to buy, sell, or hold based on grid trading strategy."""
    if grid_size <= 0:
        raise ValueError("Grid size must be greater than 0.")
    if grid_size >= 1:
        grid_size/= 100.0 # Convert percentage to decimal if grid_size is given as a percentage


    if current_price <= last_actioned_price * (1 - grid_size):
        new_no_of_shares = grid_price // current_price
        investment += new_no_of_shares * current_price
        no_of_shares += new_no_of_shares
        last_actioned_price = current_price
    elif current_price >= last_actioned_price * (1 + grid_size):
        new_no_of_shares = grid_price // current_price
        investment -= new_no_of_shares * current_price
        no_of_shares -= new_no_of_shares
        last_actioned_price = current_price

    return investment, no_of_shares, last_actioned_price

    
    

