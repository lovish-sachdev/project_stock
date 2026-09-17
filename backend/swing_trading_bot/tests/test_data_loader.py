from pathlib import Path

import pandas as pd

from src import data_loader


class FakeTicker:
    def __init__(self, symbol):
        self.symbol = symbol

    def history(self, period="3y"):
        return pd.DataFrame(
            {
                "Open": [10.0, 11.0],
                "High": [10.5, 11.5],
                "Low": [9.5, 10.5],
                "Close": [10.2, 11.2],
                "Volume": [100, 200],
            },
            index=pd.to_datetime(["2024-01-01", "2024-01-02"]),
        )


def test_load_ticker_uses_database_cache(tmp_path, monkeypatch):
    db_path = tmp_path / "ticker_cache.db"
    monkeypatch.setattr(data_loader, "DB_PATH", db_path)
    monkeypatch.setattr(data_loader.yf, "Ticker", FakeTicker)

    first = data_loader.load_ticker("TEST")
    second = data_loader.load_ticker("TEST")

    assert isinstance(first, pd.DataFrame)
    assert first.equals(second)
    assert db_path.exists()
