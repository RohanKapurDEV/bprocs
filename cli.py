import argparse
import asyncio
from main import (
    run_fetch_trades,
    run_generate_timebars,
    run_generate_quotebars,
    run_analyze_bars,
)


def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command")

    # Subparser for fetching trades and producing a trades csv file
    fetch_parser = subparsers.add_parser("fetch-trades")
    fetch_parser.add_argument("symbol", nargs="?", default="BTCUSDT")
    fetch_parser.add_argument("days", nargs="?", type=int, default=2)
    fetch_parser.add_argument("output", nargs="?", default="trades.csv")
    fetch_parser.add_argument("start_now", nargs="?", type=bool, default=True)

    # Subparser for converting trades to time-discrete OHLCV data
    ohlcv_parser = subparsers.add_parser("timebars")
    ohlcv_parser.add_argument("input_file", nargs="?", default="trades.csv")
    ohlcv_parser.add_argument("output_file", nargs="?", default="ohlcv.csv")
    ohlcv_parser.add_argument(
        "--interval",
        type=str,
        default="5min",
        help="Time interval for OHLCV bars (e.g., '1min', '5min', '1H')",
    )

    # Subparser for converting trades to dollar bars
    quotebar_parser = subparsers.add_parser("quotebars")
    quotebar_parser.add_argument("input_file", nargs="?", default="trades.csv")
    quotebar_parser.add_argument("output_file", nargs="?", default="dollar_bars.csv")
    quotebar_parser.add_argument(
        "--dollar-size",
        type=float,
        required=True,
        help="Dollar size per bar (e.g., 100000 for $100k bars)",
    )

    # Subparser for analyzing dollar bars
    analyze_parser = subparsers.add_parser("analyze-bars")
    analyze_parser.add_argument("input_file", help="Dollar bars CSV")
    analyze_parser.add_argument("--output", default="bar_analysis.txt")
    analyze_parser.add_argument("--target-size", type=float, required=True)

    args = parser.parse_args()

    if args.command == "fetch-trades":
        asyncio.run(
            run_fetch_trades(args.symbol, args.days, args.output, args.start_now)
        )
    elif args.command == "timebars":
        asyncio.run(
            run_generate_timebars(
                args.input_file, args.output_file, interval=args.interval
            )
        )
    elif args.command == "quotebars":
        asyncio.run(
            run_generate_quotebars(args.input_file, args.output_file, args.dollar_size)
        )
    elif args.command == "analyze-bars":
        asyncio.run(
            run_analyze_bars(
                args.input_file,
                args.output,
                target_size=args.target_size,
            )
        )

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
