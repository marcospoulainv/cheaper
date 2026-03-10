"""Obtiene y muestra el buildId de unimarc.cl."""

from __future__ import annotations

import argparse
import re
from typing import Optional
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

UNIMARC_URL = "https://www.unimarc.cl/"
BUILD_ID_PATTERNS = (
    re.compile(r'"buildId":"([^"]+)"'),
    re.compile(r'/_next/static/([^/]+)/_buildManifest\.js'),
)


def get_build_id(url: str = UNIMARC_URL, timeout: int = 10) -> Optional[str]:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
    }
    request = Request(url, headers=headers, method="GET")
    with urlopen(request, timeout=timeout) as res:
        charset = res.headers.get_content_charset() or "utf-8"
        body = res.read().decode(charset, errors="replace")

    for pattern in BUILD_ID_PATTERNS:
        match = pattern.search(body)
        if match:
            return match.group(1)

    return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default=UNIMARC_URL, help="URL de unimarc a consultar")
    parser.add_argument("--timeout", type=int, default=10, help="Timeout en segundos")
    args = parser.parse_args()

    try:
        print(f"Fetching {args.url}...")
        build_id = get_build_id(url=args.url, timeout=args.timeout)
    except HTTPError as exc:
        print(f"Error HTTP: {exc.code} {exc.reason}")
        return 1
    except URLError as exc:
        print(f"Error de red: {exc.reason}")
        return 1

    if build_id:
        print(f"FOUND BUILD ID: {build_id}")
        return 0

    print("Build ID no encontrado en el HTML.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
