import asyncio
import time


class RateLimiter:
    def __init__(self, max_requests: int, time_window: int):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests: dict[str, list[float]] = {}
        self._lock = asyncio.Lock()

    async def is_allowed(self, client_id: str) -> bool:
        async with self._lock:
            current_time = time.time()

            if client_id not in self.requests:
                self.requests[client_id] = []

            if len(self.requests[client_id]) >= self.max_requests:
                oldest_request = min(self.requests[client_id])
                if current_time - oldest_request < self.time_window:
                    return False
                self.requests[client_id].remove(oldest_request)

            self.requests[client_id] = [
                ts
                for ts in self.requests[client_id]
                if current_time - ts < self.time_window
            ]

            self.requests[client_id].append(current_time)
            return True
