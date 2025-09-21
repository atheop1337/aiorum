import aiohttp
import logging
import asyncio
from typing import Optional

from ..utils.formatter import RequestFormatter

class ApiClient:
    def __init__(self, token: str, max_retries: int = 5, session: aiohttp.ClientSession | None = None):
        self._token = token
        self._session: aiohttp.ClientSession | None = session
        self.max_retries = max_retries

    async def __aenter__(self):
        self._session = aiohttp.ClientSession(
            headers={"Authorization": f"Token {self._token}"}
        )
        return self

    async def __aexit__(self, exc_type, exc, tb):
        if self._session and not self._session.closed:
            await self._session.close()

    @property
    def session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                headers={
                    "Authorization": f"Token {self._token}",
                    "Content-Type": "application/json",
                }
            )
        return self._session

    async def request(self, method: str, url: str, data: Optional[dict] = None, timeout: int = 10) -> Optional[dict]:
        for attempt in range(1, self.max_retries + 1):
            try:
                async with self.session.request(method, url, json=data, timeout=aiohttp.ClientTimeout(total=timeout)) as response:
                    if response.status == 429:
                        delay = 10
                        logging.warning(f"Too many requests. Retry in {delay} seconds.")
                        await asyncio.sleep(delay)
                        continue

                    result = {
                        "status": response.status,
                        "status_text": RequestFormatter.format_status(response.status),
                        "json": await response.json(),
                    }
                    logging.debug(f"{method} {url} -> {response.status}")
                    return result

            except aiohttp.ClientError as e:
                logging.error(f"Request error: {e}")
                await asyncio.sleep(2**attempt)
                return {"error": str(e)}

    async def close(self) -> None:
        if self._session and not self._session.closed:
            await self._session.close()