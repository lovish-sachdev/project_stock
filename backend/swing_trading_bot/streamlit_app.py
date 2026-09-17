import json
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from src.data_loader import get_ticker_history, load_ticker

STORAGE_PATH = Path(__file__).parent / "tickers.json"


def ensure_storage() -> Path:
    STORAGE_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not STORAGE_PATH.exists():
        STORAGE_PATH.write_text("[]", encoding="utf-8")
    return STORAGE_PATH


def load_saved_tickers() -> list[str]:
    path = ensure_storage()
    try:
        tickers = json.loads(path.read_text(encoding="utf-8"))
        return [t.upper() for t in tickers if isinstance(t, str)]
    except Exception:
        return []


def save_tickers(tickers: list[str]) -> None:
    path = ensure_storage()
    cleaned = sorted({ticker.strip().upper() for ticker in tickers if isinstance(ticker, str) and ticker.strip()})
    path.write_text(json.dumps(cleaned, indent=2), encoding="utf-8")


def add_ticker(new_ticker: str) -> list[str]:
    new_ticker = new_ticker.strip().upper()
    if not new_ticker:
        st.warning("Enter a ticker symbol before saving.")
        return load_saved_tickers()

    tickers = load_saved_tickers()
    if new_ticker in tickers:
        st.info(f"Ticker {new_ticker} is already saved.")
        return tickers

    tickers.append(new_ticker)
    save_tickers(tickers)
    st.success(f"Saved ticker: {new_ticker}")
    return tickers


def filter_tickers(tickers: list[str], query: str) -> list[str]:
    query = query.strip().upper()
    if not query:
        return tickers
    return [ticker for ticker in tickers if query in ticker]


def show_ticker_summary(history: "pd.DataFrame") -> None:
    stats = history["Close"].describe()
    st.metric("Latest Close", f"{history['Close'].iloc[-1]:.2f}")
    st.metric("52-week High", f"{history['Close'].max():.2f}")
    st.metric("52-week Low", f"{history['Close'].min():.2f}")
    st.write(stats)


def main() -> None:
    st.set_page_config(page_title="Swing Trading Lab", layout="wide")
    st.title("Swing Trading Watchlist")
    st.markdown(
        "Add tickers to a saved watchlist, search saved tickers, and select one for charting and analysis."
    )

    saved_tickers = load_saved_tickers()
    with st.sidebar:
        st.header("Watchlist")
        new_ticker = st.text_input("Add ticker", placeholder="AAPL")
        if st.button("Save ticker"):
            saved_tickers = add_ticker(new_ticker)

        search = st.text_input("Search saved tickers")
        filtered = filter_tickers(saved_tickers, search)

        selected_ticker = st.selectbox(
            "Select ticker",
            options=[""] + filtered,
            index=0,
            help="Choose a saved ticker to use across the dashboard.",
        )

        st.write("---")
        st.header("Chart tuning")
        smoothing_window = st.slider("Smoothing window (days)", 1, 50, 5)
        smoothing_method = st.selectbox("Smoothing method", ["SMA", "EMA"])

        st.write("---")
        st.write("**Saved tickers**")
        if filtered:
            st.write(filtered)
        else:
            st.write("No tickers match your search yet.")

    if selected_ticker:
        with st.spinner(f"Loading {selected_ticker}..."):
            ticker_data = load_ticker(selected_ticker)
            history = get_ticker_history(ticker_data, period="3y")

        history = history.copy()
        history["Close"] = history["Close"].astype(float)
        if smoothing_method == "SMA":
            history["Smoothed"] = history["Close"].rolling(window=smoothing_window, min_periods=1).mean()
        else:
            history["Smoothed"] = history["Close"].ewm(span=smoothing_window, adjust=False).mean()

        st.subheader(f"Selected ticker: {selected_ticker}")
        col1, col2 = st.columns([3, 1])
        with col1:
            fig = px.line(
                history,
                x=history.index,
                y=["Close", "Smoothed"],
                title=f"{selected_ticker} Close Price",
                labels={"index": "Date", "value": "Price", "variable": "Series"},
            )
            fig.data[0].name = "Close"
            fig.data[1].name = f"{smoothing_method}({smoothing_window})"
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("### Snapshot")
            show_ticker_summary(history)
            st.markdown("### Last 5 rows")
            st.dataframe(history.tail(5))
    else:
        st.info("Add a ticker and choose it from the sidebar to start analysis.")


if __name__ == "__main__":
    main()
