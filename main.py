import pandas as pd
from common.trade import Trade
from common.binance_client import BinanceClient
from common.csv_writer import write_trades_to_csv
from rich.progress import Progress
from rich import print
from datetime import datetime


async def run_fetch_trades(symbol: str, days: int, output: str, start_now: bool):
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
    interval: str = "5min",
):
    """Generate OHLCV CSV from trades CSV."""
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
