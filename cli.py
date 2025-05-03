import argparse
import asyncio
from main import run_fetch_trades


def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command")

    # Subparser for fetching trades and producing a trades csv file
    fetch_parser = subparsers.add_parser("fetch-trades")
    fetch_parser.add_argument("symbol", nargs="?", default="BTCUSDT")
    fetch_parser.add_argument("days", nargs="?", type=int, default=2)
    fetch_parser.add_argument("output", nargs="?", default="trades.csv")
    fetch_parser.add_argument("start_now", nargs="?", type=bool, default=True)

    # Subparser for turning a trades csv file into time-discretized OHLCV data
    ohlcv_parser = subparsers.add_parser("timebars")
    ohlcv_parser.add_argument("input_file", nargs="?", default="trades.csv")
    ohlcv_parser.add_argument("output_file", nargs="?", default="ohlcv.csv")

    # Subparser for turning a trades csv file into quote-asset-discretized OHLCV data (basically dollar bars in my case)
    ohlcv_parser = subparsers.add_parser("quotebars")
    ohlcv_parser.add_argument("input_file", nargs="?", default="trades.csv")
    ohlcv_parser.add_argument("output_file", nargs="?", default="ohlcv.csv")

    args = parser.parse_args()

    if args.command == "fetch-trades":
        asyncio.run(
            run_fetch_trades(args.symbol, args.days, args.output, args.start_now)
        )
    elif args.command == "convert-to-timebars":
        print(f"Converting {args.input_file} to {args.output_file}...")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
