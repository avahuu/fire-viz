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

def fetch_wildfire_news():
    extracted_data = []
    
    # Iterate year by year, month by month
    for year in range(2020, 2025):
        for month in range(1, 13):
            _, last_day = calendar.monthrange(year, month)
            cd_min = f"{month:02d}/01/{year}"
            cd_max = f"{month:02d}/{last_day:02d}/{year}"
            tbs_param = f"cdr:1,cd_min:{cd_min},cd_max:{cd_max}"
            
            print(f"\n--- Scraping {month:02d}/{year} ---")
            
            # Fetch up to 300 results (30 pages) per month
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

                print(f"Fetching page {page+1} for {month:02d}/{year}...")
                response = requests.get(URL, params=params)
                data = response.json()
                
                if "error" in data:
                    print("API Error:", data["error"])
                    # If we ran out of credits, save what we have and completely exit
                    if "You have no more searches left" in data["error"] or "Invalid API key" in data["error"]:
                        return extracted_data
                    break # Break inner page loop on random errors

                articles = data.get("news_results", [])
                if not articles:
                    print(f"No more articles found for {month:02d}/{year}.")
                    break

                for article in articles:
                    title = article.get("title", "")
                    snippet = article.get("snippet", "")
                    
                    combined_text = f"{title} {snippet}"
                    states = extract_states(combined_text)
                    
                    item = {
                        "title": title,
                        "link": article.get("link", ""),
                        "date": article.get("date", ""),
                        "source": article.get("source", ""),
                        "states_mentioned": states
                    }
                    extracted_data.append(item)
                    
                if "serpapi_pagination" not in data or "next" not in data["serpapi_pagination"]:
                    break
                    
                time.sleep(1) # Be nice to the API

    return extracted_data

if __name__ == "__main__":
    articles = fetch_wildfire_news()

    # Save to JSON
    os.makedirs("data", exist_ok=True)
    output_file = "data/serpapi_wildfire_news.json"
    
    # Append if desired or just rewrite. Given month approach, overwriting is fine
    with open(output_file, "w") as f:
        json.dump(articles, f, indent=4)
        
    print(f"\nSuccessfully fetched {len(articles)} articles and saved to {output_file}")
