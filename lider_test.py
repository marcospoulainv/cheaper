from curl_cffi import requests
import json

def buscar_lider(query):
    url = "https://super.lider.cl/orchestra/graphql/search?query=" + query + "&page=1&prg=mWeb&sort=best_match&ps=40&limit=40&tenant=CHILE_GLASS&pageType=SearchPage"
    
    headers = {
        'content-type': 'application/json',
        'accept': 'application/json',
        'x-apollo-operation-name': 'Search',
        'x-o-bu': 'LIDER-CL',
        'x-o-mart': 'B2C',
        'x-o-platform': 'rweb',
        'x-o-vertical': 'OD'
    }
    
    cookies = {
        'assortmentStoreId': '0000057'
    }
    
    payload = {
        "query": "query Search($query:String,$limit:Int,$page:Int,$prg:Prg!,$sort:Sort){search(query:$query,limit:$limit,page:$page,prg:$prg,sort:$sort){searchResult{itemStacks{itemsV2{... on Product { id usItemId name brand imageInfo { thumbnailUrl } priceInfo { currentPrice { price priceString } } } } } } } }",
        "variables": {
            "query": query,
            "limit": 40,
            "page": 1,
            "prg": "mWeb",
            "sort": "best_match"
        }
    }
    
    res = requests.post(url, headers=headers, cookies=cookies, json=payload, impersonate="chrome110", timeout=15)
    print("Status:", res.status_code)
    try:
        data = res.json()
        search_result = data.get("data", {}).get("search", {}).get("searchResult", {})
        item_stacks = search_result.get("itemStacks", [])
        if not item_stacks:
            print("No itemStacks found")
            print(res.text[:800])
            return
            
        items = item_stacks[0].get("itemsV2", [])
        print(f"Found {len(items)} items")
        if len(items) > 0:
            print(json.dumps(items[0], indent=2))
    except Exception as e:
        print("Error parsing:", e)
        print("Response:", res.text[:500])

if __name__ == "__main__":
    buscar_lider("leche")
