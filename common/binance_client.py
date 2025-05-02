import aiohttp
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional


class BinanceClient:
    BASE_URL = "https://api.binance.com/api/v3"

    def __init__(self, symbol: str = "BTCUSDT"):
        self.symbol = symbol

    async def api_get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Any:
        url = f"{self.BASE_URL}/{path}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                response.raise_for_status()
                return await response.json()

    async def fetch_agg_trades(
        self,
        days_back: int = 1,
        limit: int = 1000,
    ) -> List[Dict[str, Any]]:
        """
        Fetch all aggTrades for the symbol in the past `days_back` days.
        Handles pagination over time windows.
        """
        now = datetime.utcnow()
        end_time = int(now.timestamp() * 1000)
        start_time = int((now - timedelta(days=days_back)).timestamp() * 1000)
        all_trades = []

        while True:
            params = {
                "symbol": self.symbol,
                "limit": limit,
                "startTime": start_time,
                "endTime": end_time,
            }
            data = await self.api_get("aggTrades", params)

            if not data:
                break

            all_trades.extend(data)

            # If we received less than limit, we're done
            if len(data) < limit:
                break

            # Move start_time forward to just after the last trade's timestamp
            last_trade_time = data[-1]["T"]
            start_time = last_trade_time + 1

        return all_trades
