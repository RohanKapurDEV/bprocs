import aiohttp
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, AsyncGenerator, Optional, List


class BinanceClient:
    BASE_URL = "https://api.binance.com/api/v3"

    def __init__(self, symbol: str = "BTCUSDT"):
        self.symbol = symbol

    async def api_get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """Generic API GET request with timeout"""
        url = f"{self.BASE_URL}/{path}"
        timeout = aiohttp.ClientTimeout(total=120)

        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url, params=params) as response:
                response.raise_for_status()
                return await response.json()

    async def fetch_agg_trades(
        self, days_back: int = 1, limit: int = 1000, start_now: bool = True
    ) -> AsyncGenerator[List[Dict[str, Any]], None]:
        """
        Async generator that yields batches of aggTrade data from Binance API
        """
        # Calculate initial time window
        now = datetime.now(timezone.utc)

        if start_now:
            end_time = now
            start_time = now - timedelta(days=days_back)
        else:
            start_time = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end_time = start_time + timedelta(days=days_back)

        # Convert to timestamps in milliseconds
        start_time_ms = int(start_time.timestamp() * 1000)
        end_time_ms = int(end_time.timestamp() * 1000)

        while True:
            params = {
                "symbol": self.symbol,
                "limit": min(limit, 1000),  # Binance max limit is 1000
                "startTime": start_time_ms,
                "endTime": end_time_ms,
            }

            data = await self.api_get("aggTrades", params)

            if not data:  # No more data
                break

            yield data  # Yield batch immediately for progress tracking

            # Check if we need to paginate
            if len(data) < limit:
                break

            # Move window forward using last trade's timestamp
            last_trade_time = data[-1]["T"]
            start_time_ms = last_trade_time + 1  # +1 to avoid duplicates

            # Prevent infinite loop if end_time is in future
            if start_time_ms > end_time_ms:
                break
