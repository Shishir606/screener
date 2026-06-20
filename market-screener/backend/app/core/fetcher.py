"""
Async stock data fetcher for the market screener.

Uses yfinance for all market data retrieval and asyncio.Semaphore
to limit concurrent requests.
"""

import asyncio
import os

import yfinance as yf


SEMAPHORE_LIMIT = int(os.getenv("SEMAPHORE_LIMIT", "5"))


async def _fetch_ticker(
    ticker: str,
    semaphore: asyncio.Semaphore,
) -> dict | None:
    """
    Fetch price history and company metadata for a single ticker.

    Returns:
        dict on success
        None on failure
    """
    try:
        async with semaphore:
            print(f"[ACQUIRE] {ticker}")

            history = await asyncio.to_thread(
                yf.download,
                ticker,
                period="1y",
                progress=False,
            )

            info = await asyncio.to_thread(
                lambda: yf.Ticker(ticker).info
            )

            result = {
                "ticker": ticker,
                "company_name": info.get("longName")
                or info.get("shortName")
                or ticker,
                "price_history": history,
                "market_cap": info.get("marketCap"),
            }

            print(f"[RELEASE] {ticker}")
            return result

    except Exception as exc:
        print(f"[ERROR] {ticker}: {exc}")
        return None


async def fetch_universe(tickers: list[str]) -> list[dict]:
    """
    Fetch stock data for an entire universe.

    Args:
        tickers: List of Yahoo Finance ticker symbols

    Returns:
        List of successful fetch results
    """
    semaphore = asyncio.Semaphore(SEMAPHORE_LIMIT)

    tasks = [
        _fetch_ticker(ticker, semaphore)
        for ticker in tickers
    ]

    results = await asyncio.gather(
        *tasks,
        return_exceptions=False,
    )

    return [
        result
        for result in results
        if result is not None
    ]


if __name__ == "__main__":
    sample_tickers = [
        "RELIANCE.NS",
        "TCS.NS",
        "INFY.NS",
    ]

    data = asyncio.run(fetch_universe(sample_tickers))

    for item in data:
        print(item.keys())
