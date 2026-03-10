import requests
import re
import time

def get_build_id():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
        "Cache-Control": "max-age=0",
        "Connection": "keep-alive"
    }
    try:
        print("Fetching unimarc.cl...")
        res = requests.get("https://www.unimarc.cl/", headers=headers, timeout=10)
        print("Status code:", res.status_code)
        
        # Searching for the build ID
        m = re.search(r'\"buildId\"\:\"([^\"]+)\"', res.text)
        if m:
            print(f"FOUND BUILD ID: {m.group(1)}")
            return m.group(1)
        else:
            print("Build ID not found in HTML.")
            
            # Additional check: Next.js script tags like <script src="/_next/static/BUILD_ID/_buildManifest.js"
            m2 = re.search(r'/_next/static/([^/]+)/_buildManifest\.js', res.text)
            if m2:
                print(f"FOUND BUILD ID (Regex 2): {m2.group(1)}")
                return m2.group(1)
                
    except Exception as e:
        print("Error:", e)
        
if __name__ == "__main__":
    get_build_id()
