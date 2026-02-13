import csv
import requests

# =========================
# CONFIG - FILL THESE IN
# =========================

API_KEY = "YOUR_GOOGLE_API_KEY_HERE"
SEARCH_ENGINE_ID = "YOUR_SEARCH_ENGINE_ID_HERE"

# How many results to try to pull per query (Google may return fewer)
RESULTS_PER_QUERY = 25

# Your target queries for leads
QUERIES = [
    '"property management" Pittsburg TX',
    '"mobile home park" near Pittsburg TX',
    '"RV park" East Texas',
    '"campground" East Texas',
]


# =========================
# CORE FUNCTIONS
# =========================

def google_search(query, num_results=20):
    """
    Uses Google Custom Search JSON API to get results for a query.
    Searches only the sites you configured in your Programmable Search Engine.
    """
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": API_KEY,
        "cx": SEARCH_ENGINE_ID,
        "q": query,
        "num": 10,  # max per page
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

        # pagination
        next_page = data.get("queries", {}).get("nextPage", [])
        if not next_page:
            break
        params["start"] = next_page[0]["startIndex"]

    return results


def build_leads_csv(queries, filename="google_leads.csv", num_results=25):
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

    # Save to CSV
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
    build_leads_csv(QUERIES, filename="google_leads.csv", num_results=RESULTS_PER_QUERY)
