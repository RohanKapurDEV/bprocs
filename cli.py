import argparse
import asyncio
from main import run


def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command")

    # Subparser for fetching trades
    fetch_parser = subparsers.add_parser("fetch-trades")
    fetch_parser.add_argument("symbol", nargs="?", default="BTCUSDT")
    fetch_parser.add_argument("days", nargs="?", type=int, default=2)
    fetch_parser.add_argument("output", nargs="?", default="trades.csv")

    # Subparser for turning a trades csv file into time-discretized OHLCV data
    ohlcv_parser = subparsers.add_parser("convert-to-ohlcv")
    ohlcv_parser.add_argument("input_file", nargs="?", default="trades.csv")
    ohlcv_parser.add_argument("output_file", nargs="?", default="ohlcv.csv")

    # Subparser for turning a trades csv file into dollar-discretized OHLCV data (assumes dollar is the quote asset)
    ohlcv_parser = subparsers.add_parser("convert-to-ohlcv")
    ohlcv_parser.add_argument("input_file", nargs="?", default="trades.csv")
    ohlcv_parser.add_argument("output_file", nargs="?", default="ohlcv.csv")

    args = parser.parse_args()

    if args.command == "fetch-trades":
        asyncio.run(run(args.symbol, args.days, args.output))
    elif args.command == "convert-to-timebars":
        print(f"Converting {args.input_file} to {args.output_file}...")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
