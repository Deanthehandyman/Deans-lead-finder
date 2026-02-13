import csv
import requests
import os

# =========================
# YOUR KEYS
# =========================

API_KEY = "b3480a1c72a209050d4c9c45338f5eb6efa36f28"
SEARCH_ENGINE_ID = "e307169415f8e4471"

RESULTS_PER_QUERY = 25

# TARGET: Homeowners posting HELP requests in forums/groups
QUERIES = [
    # Facebook groups / local posts
    '"need handyman" OR "looking for handyman" Pittsburg TX',
    '"recommend handyman" OR "good handyman" East Texas',
    '"handyman needed" OR "need repairs" Tyler TX',
    '"looking for handyman" OR "need house repair" Longview TX',
    '"handyman recommendation" Mount Pleasant TX',
    
    # Forums asking for help
    '"need plumber" OR "need electrician" Shreveport LA',
    '"roof leak" OR "fix my house" Texarkana',
    '"slow internet" OR "internet problems" rural Texas',
    
    # Rental/homeowner issues
    '"landlord won't fix" OR "rental repair" East Texas',
    '"HOA repair" OR "neighbor handyman" Pittsburg',
    
    # Ranch/farm/rural specific
    '"barn repair" OR "fence fix" East Texas',
    '"ranch maintenance" OR "farm help" Tyler TX',
]

# =========================
# FUNCTIONS
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


def build_leads_csv(queries, filename="/sdcard/Download/forum_leads.csv", num_results=25):
    all_results = []

    for q in queries:
        print(f"Searching: {q}")
        rs = google_search(q, num_results=num_results)
        all_results.extend(rs)

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

    print(f"✅ SAVED {len(unique_results)} FORUM LEADS to {filename}")


if __name__ == "__main__":
    build_leads_csv(QUERIES)
