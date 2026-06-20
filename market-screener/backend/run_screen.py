import argparse
import asyncio
import sys

from app.core.universes import UNIVERSES
from app.core.fetcher import fetch_universe
from app.core.screener import screen_candidates


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Stage 2 stock screener")
    parser.add_argument(
        "--universe",
        default="NIFTY 50",
        help="Universe to screen (default: NIFTY 50)",
    )
    args = parser.parse_args()

    if args.universe not in UNIVERSES:
        print(f"Error: Invalid universe '{args.universe}'")
        print(f"Available: {', '.join(UNIVERSES.keys())}")
        sys.exit(1)

    tickers = UNIVERSES[args.universe]

    print(f"Screening {args.universe} ({len(tickers)} tickers)...")

    fetched_data = asyncio.run(fetch_universe(tickers))
    candidates = screen_candidates(fetched_data)

    print("\nTicker               Price      50DMA     200DMA      Market Cap")
    print("-" * 68)

    for stock in candidates:
        print(
            f"{stock['ticker']:<18}"
            f"{stock['price']:>10.2f}"
            f"{stock['ma_50']:>11.2f}"
            f"{stock['ma_200']:>11.2f}"
            f"{str(stock['market_cap']):>16}"
        )

    print("-" * 68)
    print(
        f"Candidates found: {len(candidates)} / "
        f"{len(fetched_data)} tickers screened"
    )


if __name__ == "__main__":
    main()