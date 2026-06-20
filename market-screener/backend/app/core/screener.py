# screener.py
import pandas as pd

def compute_moving_averages(price_history: pd.DataFrame) -> dict | None:
    """
    Takes the price_history DataFrame from yfinance.
    Returns a dict with keys: price, ma_50, ma_100, ma_150, ma_200
    Returns None if there isn't enough data (< 200 rows).
    """
    # 1. Extract the "Close" column
    close = price_history["Close"]
    if isinstance(close, pd.DataFrame):
        close = close.squeeze()
    # 2. Check you have at least 200 data points — return None if not
    if len(close) < 200:
        return None
    # 3. Compute rolling means: close.rolling(50).mean()
    ma_50 = close.rolling(50).mean()
    ma_100 = close.rolling(100).mean()
    ma_150 = close.rolling(150).mean()
    ma_200 = close.rolling(200).mean()
    # 4. Take the most recent value and return as a dict
    return {
        "price": close.iloc[-1],
        "ma_50": ma_50.iloc[-1],
        "ma_100": ma_100.iloc[-1],
        "ma_150": ma_150.iloc[-1],
        "ma_200": ma_200.iloc[-1]
    }


def apply_stage2_filter(metrics: dict) -> bool:
    """
    Returns True if the stock satisfies ALL four conditions:
    price > ma_50 > ma_100 > ma_150 > ma_200
    """
    # Write the condition chain here — one boolean expression
    return (
        metrics["price"] > metrics["ma_50"] >
        metrics["ma_100"] > metrics["ma_150"] > metrics["ma_200"]
    )


def screen_candidates(fetched_data: list[dict]) -> list[dict]:
    """
    Takes output from fetch_universe.
    Returns list of dicts for stocks passing the Stage 2 filter.
    Each dict should have: ticker, company_name, price, ma_50, ma_100, ma_150, ma_200, market_cap, cap_category
    """
    candidates = []
    for stock in fetched_data:
        # 1. Call compute_moving_averages — skip if None
        metrics = compute_moving_averages(stock["price_history"])
        if not metrics:
            continue
        # 2. Call apply_stage2_filter — skip if False
        if not apply_stage2_filter(metrics):
            continue
        # 3. Derive cap_category:
        #    market_cap > 20_000 Cr → "Large"  (multiply Yahoo's value by... figure out the unit)
        #    market_cap > 5_000 Cr → "Mid"
        #    else → "Small"
        market_cap = stock.get("market_cap") or 0      # safe None guard
        market_cap_cr = market_cap / 10_000_000        # use the safe variable
        
        if market_cap==0:
            cap_category = "Unknown"
        elif market_cap_cr > 20_000:                     # compare the converted value
            cap_category = "Large"
        elif market_cap_cr > 5_000:                    # compare the converted value
            cap_category = "Mid"
        else:
            cap_category = "Small"
        # 4. Append to candidates
        candidates.append({
            **stock,
            **metrics,
            "cap_category": cap_category
        })
    return candidates