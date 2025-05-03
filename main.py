from common.trade import Trade
from common.binance_client import BinanceClient
from common.csv_writer import write_trades_to_csv


async def run_fetch_trades(symbol: str, days: int, output: str, start_now: bool):
    print(f"Fetching trades for {symbol} for the last {days} days...")

    client = BinanceClient(symbol)
    data = await client.fetch_agg_trades(days_back=days, start_now=start_now)
    trades = [Trade(item.get("p"), item.get("q"), item.get("T")) for item in data]
    write_trades_to_csv(trades, output)

    print(f"Wrote {len(trades)} trades to {output}")
