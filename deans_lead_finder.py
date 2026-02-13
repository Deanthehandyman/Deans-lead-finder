import csv
import requests
import os

API_KEY = "b3480a1c72a209050d4c9c45338f5eb6efa36f28"
SEARCH_ENGINE_ID = "e307169415f8e4471"

QUERIES = [
    # Craigslist / classifieds
    '"handyman" "TX" "labor" OR "gigs"',
    '"need handyman" "Texas" "craigslist"',
    '"handyman needed" "East Texas"',
    
    # Reddit / forums (public threads)
    '"need handyman" site:reddit.com "Texas"',
    '"handyman recommendation" site:reddit.com "TX"',
    '"roof leak" site:reddit.com "Texas"',
    
    # Public Q&A
    '"looking for handyman" "Texas"',
    '"recommend handyman" "East Texas"',
    '"slow internet" "rural" "Texas"',
]

def google_search(query, num_results=20):
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": API_KEY,
        "cx": SEARCH_ENGINE_ID,
        "q": query,
        "num": 10,
    }
    results = []
    fetched = 0
    while fetched < num_results:
        resp = requests.get(url, params=params)
        data = resp.json()
        items = data.get("items", [])
        if not items:
            break
        for item in items:
            results.append({
                "title": item.get("title"),
                "link": item.get("link"),
                "snippet": item.get("snippet"),
                "query": query,
            })
            fetched += 1
            if fetched >= num_results:
                break
        next_page = data.get("queries", {}).get("nextPage", [])
        if not next_page:
            break
        params["start"] = next_page[0]["startIndex"]
    return results

def build_leads_csv(queries, filename="/sdcard/Download/public_leads.csv"):
    all_results = []
    for q in queries:
        print(f"Searching: {q}")
        rs = google_search(q, 20)
        all_results.extend(rs)
    
    # Dedupe
    seen_links = set()
    unique_results = []
    for r in all_results:
        link = r.get("link")
        if link and link not in seen_links:
            seen_links.add(link)
            unique_results.append(r)
    
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Title", "URL", "Snippet", "Query"])
        for r in unique_results:
            writer.writerow([
                r.get("title", ""),
                r.get("link", ""),
                r.get("snippet", ""),
                r.get("query", ""),
            ])
    
    print(f"✅ SAVED {len(unique_results)} PUBLIC LEADS to {filename}")

if __name__ == "__main__":
    build_leads_csv(QUERIES)
