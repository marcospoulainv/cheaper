import requests
import json

url = "https://pwcdauseo-zone.cnstrc.com/autocomplete/coca?c=ciojs-client-2.64.3&key=key_8pjkPsSkEsJHKgxR&i=c78830c8-462d-47a2-822e-9359ebc0ad55&s=1&num_results_Search%20Suggestions=7&num_results_Products=10&num_results_Categories=2"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json"
}

try:
    print("Fetching URL...")
    r = requests.get(url, headers=headers)
    print("Status:", r.status_code)
    data = r.json()
    with open("response_test.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print("Saved to response_test.json")
except Exception as e:
    print("Error:", e)
