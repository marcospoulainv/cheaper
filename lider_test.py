"""Prueba del endpoint GraphQL de Líder para una búsqueda puntual."""

from __future__ import annotations

import argparse
import json
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen


def buscar_lider(query: str, timeout: int = 15) -> list[dict]:
    encoded_query = quote(query)
    url = (
        "https://super.lider.cl/orchestra/graphql/search"
        f"?query={encoded_query}&page=1&prg=mWeb&sort=best_match&ps=40&limit=40"
        "&tenant=CHILE_GLASS&pageType=SearchPage"
    )

    headers = {
        "content-type": "application/json",
        "accept": "application/json",
        "x-apollo-operation-name": "Search",
        "x-o-bu": "LIDER-CL",
        "x-o-mart": "B2C",
        "x-o-platform": "rweb",
        "x-o-vertical": "OD",
        "cookie": "assortmentStoreId=0000057",
    }

    payload = {
        "query": (
            "query Search($query:String,$limit:Int,$page:Int,$prg:Prg!,$sort:Sort){"
            "search(query:$query,limit:$limit,page:$page,prg:$prg,sort:$sort){"
            "searchResult{itemStacks{itemsV2{... on Product {"
            "id usItemId name brand imageInfo { thumbnailUrl } "
            "priceInfo { currentPrice { price priceString } }"
            "} } } } } }"
        ),
        "variables": {
            "query": query,
            "limit": 40,
            "page": 1,
            "prg": "mWeb",
            "sort": "best_match",
        },
    }

    body = json.dumps(payload).encode("utf-8")
    request = Request(url, data=body, headers=headers, method="POST")
    with urlopen(request, timeout=timeout) as response:
        charset = response.headers.get_content_charset() or "utf-8"
        data = json.loads(response.read().decode(charset))

    return (
        data.get("data", {})
        .get("search", {})
        .get("searchResult", {})
        .get("itemStacks", [{}])[0]
        .get("itemsV2", [])
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("query", nargs="?", default="leche")
    args = parser.parse_args()

    try:
        items = buscar_lider(args.query)
    except HTTPError as exc:
        print(f"Error HTTP: {exc.code} {exc.reason}")
        return 1
    except URLError as exc:
        print(f"Error de red: {exc.reason}")
        return 1
    except json.JSONDecodeError as exc:
        print(f"Error parseando respuesta: {exc}")
        return 1

    print(f"Found {len(items)} items para query='{args.query}'")
    if items:
        print(json.dumps(items[0], indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
