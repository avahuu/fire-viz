import requests
import json
import re
import os
import time
import calendar

API_KEY = "b291182494b0c9c75dc51c9f6fbd410dc2f723abf12dbee960475aa1ddf02040"
URL = "https://serpapi.com/search.json"

US_STATES = [
    "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado",
    "Connecticut", "Delaware", "Florida", "Georgia", "Hawaii", "Idaho",
    "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana",
    "Maine", "Maryland", "Massachusetts", "Michigan", "Minnesota",
    "Mississippi", "Missouri", "Montana", "Nebraska", "Nevada", "New Hampshire",
    "New Jersey", "New Mexico", "New York", "North Carolina", "North Dakota",
    "Ohio", "Oklahoma", "Oregon", "Pennsylvania", "Rhode Island", "South Carolina",
    "South Dakota", "Tennessee", "Texas", "Utah", "Vermont", "Virginia",
    "Washington", "West Virginia", "Wisconsin", "Wyoming"
]

def extract_states(text):
    if not text:
        return []
    found_states = set()
    for state in US_STATES:
        pattern = r'\b' + re.escape(state) + r'\b'
        if re.search(pattern, text, re.IGNORECASE):
            found_states.add(state)
    return list(found_states)

def fetch_wildfire_news(start_year, start_month, end_year, end_month):
    new_articles = []

    for year in range(start_year, end_year + 1):
        month_start = start_month if year == start_year else 1
        month_end = end_month if year == end_year else 12

        for month in range(month_start, month_end + 1):
            _, last_day = calendar.monthrange(year, month)
            cd_min = f"{month:02d}/01/{year}"
            cd_max = f"{month:02d}/{last_day:02d}/{year}"
            tbs_param = f"cdr:1,cd_min:{cd_min},cd_max:{cd_max}"

            print(f"\n--- Scraping {month:02d}/{year} ---")

            for page in range(30):
                params = {
                    "engine": "google",
                    "q": "wildfire",
                    "gl": "us",
                    "hl": "en",
                    "tbm": "nws",
                    "tbs": tbs_param,
                    "start": page * 10,
                    "api_key": API_KEY
                }

                print(f"  Page {page+1}...")
                response = requests.get(URL, params=params)
                data = response.json()

                if "error" in data:
                    print("API Error:", data["error"])
                    if "You have no more searches left" in data["error"] or "Invalid API key" in data["error"]:
                        return new_articles, True  # out of credits
                    break

                articles = data.get("news_results", [])
                if not articles:
                    break

                for article in articles:
                    title = article.get("title", "")
                    snippet = article.get("snippet", "")
                    combined_text = f"{title} {snippet}"
                    states = extract_states(combined_text)

                    new_articles.append({
                        "title": title,
                        "link": article.get("link", ""),
                        "date": article.get("date", ""),
                        "source": article.get("source", ""),
                        "states_mentioned": states
                    })

                if "serpapi_pagination" not in data or "next" not in data["serpapi_pagination"]:
                    break

                time.sleep(20)  # Stay under 200 searches/hour plan limit

    return new_articles, False  # completed normally


if __name__ == "__main__":
    output_file = "data/serpapi_wildfire_news.json"

    # Load existing data
    with open(output_file) as f:
        existing = json.load(f)
    print(f"Loaded {len(existing)} existing articles. Resuming from Dec 2020...\n")

    new_articles, ran_out = fetch_wildfire_news(
        start_year=2024, start_month=9,   # Resume from Sep 2024 (throttled last time)
        end_year=2024,   end_month=12
    )

    # Append and save
    combined = existing + new_articles
    with open(output_file, "w") as f:
        json.dump(combined, f, indent=4)