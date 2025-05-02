import csv
from typing import List
from .trade import Trade


def write_trades_to_csv(trades: List[Trade], filename: str):
    with open(filename, "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["price", "quantity", "timestamp"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for trade in trades:
            writer.writerow(trade.to_dict())
