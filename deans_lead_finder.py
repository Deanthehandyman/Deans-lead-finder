import csv
import requests
import os

# =========================
# YOUR KEYS
# =========================

API_KEY = "b3480a1c72a209050d4c9c45338f5eb6efa36f28"
SEARCH_ENGINE_ID = "e307169415f8e4471"

RESULTS_PER_QUERY = 25

# =========================
# QUERIES: REAL PEOPLE POSTS
# =========================

QUERIES = [
    # General "need a handyman" posts
    '"need a handyman" "TX"',
    '"looking for a handyman" "Texas"',
    '"handyman recommendation" "Pittsburg TX"',
    '"good handyman" "East Texas"',
    '"handyman near me" "Pittsburg Texas"',

    # Facebook / Nextdoor style
    '"who can fix" "leak" "Texas"',
    '"anyone know a handyman" "TX"',
    '"can anyone recommend" "handyman" "Texas"',
    '"need someone to fix" "house" "Texas"',

    # Reddit / forum style
    '"cant find a handyman" "Texas"',
    '"having trouble finding help" "home repairs"',
    '"how do I find a contractor" "Texas"',
    '"need help with home repairs"',

    # Internet / Starlink
    '"slow internet" "rural" "Texas"',
    '"Starlink install" "who can" "TX"',
    '"need help installing Starlink"',

    # Rentals / landlord issues
    '"landlord wont fix" "Texas"',
    '"rental repair" "need someone" "TX"',

    # Ranch / farm / rural
    '"fence repair" "East Texas"',
    '"barn repair" "Texas"',
    '"ranch maintenance" "need help" "TX"',
]

# =========================
# FUNCTIONS
# =========================

def google_search(query, num_results=20):
    """
    Use Google Custom Search JSON API against your 50 domains.
    """
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


def build_leads_csv(
    queries,
    filename="/sdcard/Download/forum_leads.csv",
    num_results=RESULTS_PER_QUERY,
):
    all_results = []

    for q in queries:
        print(f"Searching: {q}")
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

    # Ensure Downloads path exists and save file
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

    print(f"✅ SAVED {len(unique_results)} FORUM LEADS to {filename}")


if __name__ == "__main__":
    build_leads_csv(QUERIES)
