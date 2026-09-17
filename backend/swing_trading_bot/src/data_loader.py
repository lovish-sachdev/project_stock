import json
import sqlite3
from pathlib import Path

import pandas as pd
import yfinance as yf

pd.set_option('display.max_columns', None)

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "ticker_cache.db"


def _ensure_db() -> None:
    """Create the SQLite cache database and table if it does not exist."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS ticker_history (
                ticker TEXT NOT NULL,
                period TEXT NOT NULL,
                data TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                PRIMARY KEY (ticker, period)
            )
            """
        )


def _read_ticker_from_db(ticker: str, period: str = "3y") -> pd.DataFrame | None:
    """Return cached ticker data for a symbol if it exists in the database."""
    _ensure_db()
    with sqlite3.connect(DB_PATH) as conn:
        row = conn.execute(
            "SELECT data FROM ticker_history WHERE ticker = ? AND period = ?",
            (ticker.upper(), period),
        ).fetchone()

    if row is None:
        return None

    payload = json.loads(row[0])
    df = pd.DataFrame(payload["data"])
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.set_index("Date")
    return df[["Open", "High", "Low", "Close", "Volume"]]


def _save_ticker_to_db(ticker: str, history: pd.DataFrame, period: str = "3y") -> None:
    """Persist ticker history to the SQLite cache."""
    _ensure_db()
    frame = history.copy()
    frame = frame[["Open", "High", "Low", "Close", "Volume"]].copy()
    frame.index = pd.to_datetime(frame.index)
    frame = frame.reset_index().rename(columns={"index": "Date"})
    frame["Date"] = frame["Date"].dt.strftime("%Y-%m-%d")
    payload = {
        "ticker": ticker.upper(),
        "period": period,
        "data": frame.to_dict(orient="records"),
    }

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            INSERT INTO ticker_history (ticker, period, data, updated_at)
            VALUES (?, ?, ?, datetime('now'))
            ON CONFLICT(ticker, period)
            DO UPDATE SET data = excluded.data, updated_at = datetime('now')
            """,
            (ticker.upper(), period, json.dumps(payload)),
        )
        conn.commit()


def load_ticker(ticker: str, period: str = "3y") -> pd.DataFrame:
    """Load ticker history from local SQLite cache or fetch from yfinance if missing."""
    symbol = ticker.strip().upper()
    cached = _read_ticker_from_db(symbol, period=period)
    if cached is not None:
        return cached

    ticker_data = yf.Ticker(symbol)
    history = ticker_data.history(period=period)
    if history.empty:
        return history[["Open", "High", "Low", "Close", "Volume"]]

    cleaned = history[["Open", "High", "Low", "Close", "Volume"]].copy()
    _save_ticker_to_db(symbol, cleaned, period=period)
    return cleaned


def get_ticker_history(ticker_data, period: str = "3y") -> pd.DataFrame:
    """Get historical OHLC price data for a ticker or cached dataframe."""
    if isinstance(ticker_data, pd.DataFrame):
        history = ticker_data.copy()
        return history[["Open", "High", "Low", "Close", "Volume"]]

    history = ticker_data.history(period=period)
    return history[["Open", "High", "Low", "Close", "Volume"]]


