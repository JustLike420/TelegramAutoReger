import os
import socks
from dotenv import load_dotenv
from typing import Tuple


def get_proxies() -> Tuple[dict, tuple]:
    load_dotenv()
    proxy_method = os.environ.get('PROXY_METHOD')
    proxy_ip = os.environ.get('PROXY_IP')
    proxy_port = os.environ.get('PROXY_PORT')
    proxies = {
        'http': f'{proxy_method}://{proxy_ip}:{proxy_port}',
        'https': f'{proxy_method}://{proxy_ip}:{proxy_port}',
    }
    telethon_proxies = (socks.SOCKS5, f"'{proxy_ip}'", proxy_port, True)
    return proxies, telethon_proxies
