import asyncio
from py_lead_generation import GoogleMapsEngine, YelpEngine

# Customize these for Dean's Handyman Service
DEFAULT_QUERIES = [
    "property management",
    "mobile home park",
    "rv park",
    "campground",
    "apartment complex",
]
DEFAULT_LOCATION = "Pittsburg, Texas"

async def build_leads(queries=None, location=None, zoom=11):
    queries = queries or DEFAULT_QUERIES
    location = location or DEFAULT_LOCATION

    all_engines = []

    for q in queries:
        print(f"Searching Google Maps for '{q}' in '{location}'...")
        g_engine = GoogleMapsEngine(q, location, zoom)
        all_engines.append(("google", q, g_engine))

        print(f"Searching Yelp for '{q}' in '{location}'...")
        y_engine = YelpEngine(q, location)
        all_engines.append(("yelp", q, y_engine))

    # Run searches
    for source, q, engine in all_engines:
        await engine.run()
        filename = f"leads_{source}_{q.replace(' ', '_')}.csv"
        print(f"Saving {source} leads for '{q}' to {filename}")
        engine.save_to_csv(filename)

if __name__ == "__main__":
    asyncio.run(build_leads())
