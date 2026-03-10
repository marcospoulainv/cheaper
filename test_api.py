"""Pequeña utilidad para probar endpoint de autocomplete y guardar la respuesta."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

DEFAULT_URL = (
    "https://pwcdauseo-zone.cnstrc.com/autocomplete/coca?c=ciojs-client-2.64.3"
    "&key=key_8pjkPsSkEsJHKgxR&i=c78830c8-462d-47a2-822e-9359ebc0ad55&s=1"
    "&num_results_Search%20Suggestions=7&num_results_Products=10&num_results_Categories=2"
)
DEFAULT_OUTPUT = Path("response_test.json")
DEFAULT_TIMEOUT_SECONDS = 20


def fetch_json(url: str, timeout: int = DEFAULT_TIMEOUT_SECONDS) -> dict:
    """Obtiene JSON de la URL de prueba con headers de navegador."""
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": "application/json",
    }
    request = Request(url, headers=headers, method="GET")
    with urlopen(request, timeout=timeout) as response:
        charset = response.headers.get_content_charset() or "utf-8"
        return json.loads(response.read().decode(charset))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default=DEFAULT_URL, help="URL a consultar")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT), help="Ruta de salida para guardar el JSON")
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT_SECONDS)
    args = parser.parse_args()

    try:
        print(f"Fetching URL: {args.url}")
        payload = fetch_json(args.url, timeout=args.timeout)
        output = Path(args.output)
        output.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"OK: respuesta guardada en {output}")
        return 0
    except HTTPError as exc:
        print(f"Error HTTP: {exc.code} {exc.reason}")
    except URLError as exc:
        print(f"Error de red: {exc.reason}")
    except json.JSONDecodeError as exc:
        print(f"Error parseando JSON: {exc}")

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
