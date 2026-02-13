import csv
import requests
import os

# =========================
# YOUR KEYS - READY TO RUN
# =========================

API_KEY = "b3480a1c72a209050d4c9c45338f5eb6efa36f28"
SEARCH_ENGINE_ID = "e307169415f8e4471"

# How many results to try to pull per query (Google may return fewer)
RESULTS_PER_QUERY = 25

# Target queries for Pittsburg + ~200 miles (East TX, AR, LA, OK)
QUERIES = [
    # Core around Pittsburg
    '"property management" Pittsburg TX',
    '"property management" Mount Pleasant TX',
    '"property management" Longview TX',
    '"property management" Tyler TX',
    '"property management" Texarkana TX',
    '"property management" Sulphur Springs TX',

    # Mobile home & RV within that radius
    '"mobile home park" near Pittsburg TX',
    '"mobile home park" East Texas',
    '"RV park" near Pittsburg TX',
    '"RV park" East Texas',

    # Campgrounds / rural spots
    '"campground" East Texas',
    '"campground" near Pittsburg TX',
    '"lake cabin rentals" East Texas',

    # Cross-border within 200 miles (AR / LA / OK)
    '"property management" Shreveport LA',
    '"property management" Texarkana AR',
    '"property management" Idabel OK',
    '"RV park" Shreveport LA',
    '"RV park" Texarkana AR',
    '"campground" Shreveport LA',
]

# =========================
# CORE FUNCTIONS
# =========================

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


def build_leads_csv(queries, filename="/sdcard/Download/google_leads.csv", num_results=25):
    all_results = []

    for q in queries:
        print(f"Searching for: {q}")
        rs = google_search(q, num_results=num_results)
        all_results.extend(rs)

    # De-duplicate by URL
    seen_links = set()
    unique_results = []
    for r in all_results:
        link = r.get("link")
        if link and link not in seen_links:
            seen_links.add(link)
            unique_results.append(r)

    # Save directly to Downloads
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

    print(f"Saved {len(unique_results)} unique leads to {filename}")


if __name__ == "__main__":
    build_leads_csv(QUERIES)
