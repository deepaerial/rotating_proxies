import asyncio
import json
from dataclasses import dataclass
from pathlib import Path
from typing import List

import httpx
from rich.console import Console
from rich.table import Table
from tqdm.asyncio import tqdm_asyncio

PROJECT_ROOT = (Path(__file__).parent / "..").resolve()
PROXIES_JSON_FILE = (PROJECT_ROOT / "proxies.json").absolute()
OUTPUT_FILE = (PROJECT_ROOT / "working_proxies.txt").absolute()
URL_TO_CHECK = "https://httpbin.org/ip"

console = Console()


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


def export_to_file(proxies: List[Proxy], output_file: Path):
    with output_file.open("w") as f:
        for proxy in proxies:
            f.write(str(proxy))
            f.write("\n")


def export_to_console_table(proxies: List[Proxy]):
    table = Table(title="Working Proxies")

    table.add_column("Protocol", style="cyan")
    table.add_column("IP", style="magenta")
    table.add_column("Port", style="magenta")
    table.add_column("Country", style="green")

    for proxy in proxies:
        table.add_row(proxy.protocol, proxy.ip, str(proxy.port), proxy.country)
    console.print(table)


def read_proxies_json(proxies_json_file: Path = PROXIES_JSON_FILE) -> List[Proxy]:
    try:
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
    except FileNotFoundError:
        print(f"Error: {proxies_json_file} not found.")
        return []
    except json.JSONDecodeError as e:
        print(f"Error reading JSON from {proxies_json_file}: {e}")
        return []


async def probe_proxy(proxy: Proxy, url_to_check: str) -> Proxy | None:
    async with httpx.AsyncClient(proxy=proxy.proxy) as client:
        try:
            response = await client.get(url_to_check)
            response.raise_for_status()
            return proxy
        except Exception:
            return None


async def probing_proxies(proxies: List[Proxy]):
    # Wrapping tasks in tqdm to show progress
    tasks = [probe_proxy(proxy, URL_TO_CHECK, f"{idx + 1}/{len(proxies)}") for idx, proxy in enumerate(proxies)]
    checked_proxies = await tqdm_asyncio.gather(*tasks, desc="Checking Proxies", unit="proxy")

    # Filter out None values (failed proxies)
    only_working_proxies = [p for p in checked_proxies if p is not None]
    export_to_console_table(only_working_proxies)
    export_to_file(only_working_proxies, OUTPUT_FILE)
    console.print(f"[bold cyan]Results saved to:[/bold cyan] [bold white]{OUTPUT_FILE.resolve()}[/bold white]")


if __name__ == "__main__":
    proxies: list[Proxy] = read_proxies_json()
    if proxies:
        asyncio.run(probing_proxies(proxies))
    else:
        print("No proxies to check.")
