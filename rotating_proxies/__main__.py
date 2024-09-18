import asyncio
import json
from dataclasses import dataclass
from pathlib import Path

import httpx


PROJECT_ROOT = (Path(__file__).parent / "..").resolve()
PROXIES_JSON_FILE = (PROJECT_ROOT / "proxies.json").absolute()

URL_TO_CHECK = "https://httpbin.org/ip"


@dataclass
class Proxy:
    protocol: str
    ip: str
    port: int
    proxy: str
    country: str
    continent: str

    def __str__(self) -> str:
        return f"{self.protocol}://{self.ip}:{self.port}"

    def __repr__(self) -> str:
        return f"{self.protocol}://{self.ip}:{self.port} ({self.country}, {self.continent})"


def read_proxies_json(proxies_json_file: Path = PROXIES_JSON_FILE) -> str:
    with proxies_json_file.open("r") as f:
        data = json.loads(f.read())
        return [
            Proxy(
                protocol=proxy["protocol"],
                ip=proxy["ip"],
                port=proxy["port"],
                proxy=proxy["proxy"],
                country=proxy["ip_data"]["country"],
                continent=proxy["ip_data"]["continent"],
            )
            for proxy in data["proxies"]
            if proxy.get("ip_data") and proxy.get("protocol") in ("http", "https")
        ]


async def probe_proxy(proxy: Proxy, url_to_check: str, log_number: str) -> Proxy | None:
    async with httpx.AsyncClient(proxy=proxy.proxy) as client:
        try:
            response = await client.get(url_to_check)
            response.raise_for_status()
            print(f"Response for {proxy} ({log_number}): {response.json()}")
            return proxy
        except Exception as e:
            print(f"Failed to connect to {proxy} ({log_number}). Reason: {e}")
            return None


async def probing_proxies(proxies: list[Proxy]):
    checked_proxies = await asyncio.gather(
        *[probe_proxy(proxy, URL_TO_CHECK, f"{idx}/{len(proxies)}") for idx, proxy in enumerate(proxies)]
    )
    print("\n".join(repr(p) for p in filter(lambda e: e is not None, checked_proxies)))


if __name__ == "__main__":
    proxies: list[Proxy] = read_proxies_json()
    asyncio.run(probing_proxies(proxies))
