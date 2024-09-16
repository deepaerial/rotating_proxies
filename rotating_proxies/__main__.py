from pathlib import Path
from pprint import pprint
from operator import itemgetter
import json
from dataclasses import dataclass

PROJECT_ROOT = (Path(__file__).parent / "..").resolve()
PROXIES_JSON_FILE = (PROJECT_ROOT / "proxies.json").absolute()

proxy_itemgetter = itemgetter("protocol", "ip", "port", "proxy", "ip_data.country", "ip_data.continent")

@dataclass
class Proxy:
    protocol: str
    ip: str
    port: int
    proxy: str
    country: str
    continent: str


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
                continent=proxy["ip_data"]["continent"]
            )
            for proxy in data["proxies"] 
            if proxy.get("ip_data") and proxy.get("ip_data").get("country") != "Russia" and proxy.get("protocol") == "http"
        ]

if __name__ == "__main__":
    proxies = read_proxies_json()
