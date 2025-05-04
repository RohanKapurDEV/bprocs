import pandas as pd
from common.trade import Trade
from common.binance_client import BinanceClient
from common.csv_writer import write_trades_to_csv
from rich.progress import Progress
from rich import print
from datetime import datetime
import csv
from typing import List, Dict, Any


async def run_fetch_trades(symbol: str, days: int, output: str, start_now: bool):
    """
    Fetch trades from Binance and write to CSV.

    Args:
        symbol (str): Trading pair symbol (e.g., 'BTCUSDT').
        days (int): Number of days to fetch trades for.
        output (str): Output CSV file path.
        start_now (bool): Whether to start fetching from now or from the past.
    """

    print(f"Fetching trades for {symbol} for the last {days} days...")

    client = BinanceClient(symbol)
    data = []

    with Progress() as progress:
        task = progress.add_task(
            "[cyan]Fetching...", total=None
        )  # Indeterminate progress
        async for batch in client.fetch_agg_trades(days_back=days, start_now=start_now):
            data.extend(batch)
            latest_ts = datetime.utcfromtimestamp(batch[-1]["T"] / 1000).strftime(
                "%Y-%m-%d %H:%M:%S"
            )
            progress.update(task, description=f"Latest trade: {latest_ts}")

    trades = [Trade(item.get("p"), item.get("q"), item.get("T")) for item in data]
    write_trades_to_csv(trades, output)
    print(f"\nWrote {len(trades)} trades to {output}")


async def run_generate_timebars(
    input_file: str,
    output_file: str,
    interval: str = "1min",
):
    """
    Generate time-discrete OHLCV data from trades CSV file.

    Args:
        input_file (str): Path to the input trades CSV file.
        output_file (str): Path to the output OHLCV CSV file.
        interval (str): Time interval for OHLCV bars (e.g., '1min', '5min', '1H').
    """

    print(f"Generating {interval} OHLCV bars from {input_file}...")

    # Read trades CSV
    df = pd.read_csv(input_file)

    # Parse timestamps (assuming timestamp is in milliseconds)
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True)
    df.set_index("timestamp", inplace=True)

    # Resample into OHLCV
    ohlcv = df["price"].resample(interval).ohlc()
    ohlcv["volume"] = df["quantity"].resample(interval).sum()
    ohlcv = ohlcv.dropna()  # Remove intervals with no trades

    # Reset index to include timestamp as a column
    ohlcv.reset_index(inplace=True)

    # Save to CSV
    ohlcv.to_csv(output_file, index=False)
    print(f"Wrote {len(ohlcv)} bars to {output_file}")


async def run_generate_quotebars(input_file: str, output_file: str, dollar_size: float):
    """Generate dollar-denominated OHLCV bars"""
    print(f"Generating ${dollar_size:,.0f} dollar bars from {input_file}...")

    trades = _read_trades_from_csv(input_file)
    bars = []

    current_bar: Dict[str, Any] = None
    accumulated = 0.0

    for trade in trades:
        # Calculate dollar value of this trade
        value = trade.price * trade.quantity

        if not current_bar:
            # Initialize new bar
            current_bar = {
                "start_time": trade.timestamp,
                "open": trade.price,
                "high": trade.price,
                "low": trade.price,
                "close": trade.price,
                "volume": value,
                "trade_count": 1,
            }
        else:
            # Update existing bar
            current_bar["high"] = max(current_bar["high"], trade.price)
            current_bar["low"] = min(current_bar["low"], trade.price)
            current_bar["close"] = trade.price
            current_bar["volume"] += value
            current_bar["trade_count"] += 1

        accumulated += value

        # Check if bar is complete
        if accumulated >= dollar_size:
            current_bar["end_time"] = trade.timestamp
            bars.append(current_bar)

            # Reset for next bar
            current_bar = None
            accumulated = 0.0

    # Add final partial bar if exists
    if current_bar:
        current_bar["end_time"] = trade.timestamp  # Last trade's timestamp
        bars.append(current_bar)

    # Write to CSV
    _write_dollar_bars(bars, output_file)
    print(f"Generated {len(bars)} dollar bars in {output_file}")


def _write_dollar_bars(bars: List[Dict], filename: str):
    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "start_time",
                "end_time",
                "open",
                "high",
                "low",
                "close",
                "dollar_volume",
                "trade_count",
            ]
        )
        for bar in bars:
            writer.writerow(
                [
                    bar["start_time"],
                    bar["end_time"],
                    bar["open"],
                    bar["high"],
                    bar["low"],
                    bar["close"],
                    bar["volume"],
                    bar["trade_count"],
                ]
            )


def _read_trades_from_csv(filename: str) -> List[Trade]:
    trades = []
    with open(filename, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            trades.append(
                Trade(
                    price=row["price"],
                    quantity=row["quantity"],
                    timestamp=row["timestamp"],
                )
            )
    return trades
