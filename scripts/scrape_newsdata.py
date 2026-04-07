import requests
import json
import re
import os

API_KEY = "pub_fefe2d8361da4c03b55ee0e09bff68bd"
URL = "https://newsdata.io/api/1/latest"

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
    # Simple search
    for state in US_STATES:
        pattern = r'\b' + re.escape(state) + r'\b'
        if re.search(pattern, text, re.IGNORECASE):
            found_states.add(state)
    return list(found_states)

def fetch_wildfire_news():
    params = {
        "apikey": API_KEY,
        "q": "wildfire",
        "country": "us",
        "language": "en"
    }

    print(f"Fetching news from {URL} with params: {params}")
    response = requests.get(URL, params=params)
    data = response.json()
    
    if data.get("status") != "success":
        print("Error fetching data:", data)
        return

    articles = data.get("results", [])
    extracted_data = []

    for article in articles:
        title = article.get("title", "")
        description = article.get("description", "")
        content = article.get("content", "")
        
        combined_text = f"{title} {description} {content}"
        states = extract_states(combined_text)
        
        item = {
            "title": title,
            "link": article.get("link", ""),
            "pubDate": article.get("pubDate", ""),
            "source": article.get("source_name", ""),
            "states_mentioned": states
        }
        extracted_data.append(item)

    # Save to JSON
    os.makedirs("data", exist_ok=True)
    output_file = "data/wildfire_news.json"
    with open(output_file, "w") as f:
        json.dump(extracted_data, f, indent=4)
        
    print(f"Successfully fetched {len(articles)} articles and saved to {output_file}")
    for item in extracted_data:
        print(f"- {item['title']}")
        print(f"  States mentioned: {', '.join(item['states_mentioned']) if item['states_mentioned'] else 'None'}")
        print()

if __name__ == "__main__":
    fetch_wildfire_news()
