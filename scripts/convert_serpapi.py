import json
import csv
from dateutil import parser
import os
import re

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

# Map abbreviations to full state names
STATE_ABBREVS = {
    "al": "Alabama", "ak": "Alaska", "az": "Arizona", "ar": "Arkansas",
    "ca": "California", "co": "Colorado", "ct": "Connecticut", "de": "Delaware",
    "fl": "Florida", "ga": "Georgia", "hi": "Hawaii", "id": "Idaho",
    "il": "Illinois", "in": "Indiana", "ia": "Iowa", "ks": "Kansas",
    "ky": "Kentucky", "la": "Louisiana", "me": "Maine", "md": "Maryland",
    "ma": "Massachusetts", "mi": "Michigan", "mn": "Minnesota", "ms": "Mississippi",
    "mo": "Missouri", "mt": "Montana", "ne": "Nebraska", "nv": "Nevada",
    "nh": "New Hampshire", "nj": "New Jersey", "nm": "New Mexico", "ny": "New York",
    "nc": "North Carolina", "nd": "North Dakota", "oh": "Ohio", "ok": "Oklahoma",
    "or": "Oregon", "pa": "Pennsylvania", "ri": "Rhode Island", "sc": "South Carolina",
    "sd": "South Dakota", "tn": "Tennessee", "tx": "Texas", "ut": "Utah",
    "vt": "Vermont", "va": "Virginia", "wa": "Washington", "wv": "West Virginia",
    "wi": "Wisconsin", "wy": "Wyoming"
}

def extract_states_from_text(text):
    """Match full state names in any text."""
    found = set()
    if not text:
        return found
    for state in US_STATES:
        if re.search(r'\b' + re.escape(state) + r'\b', text, re.IGNORECASE):
            found.add(state)
    return found

def extract_states_from_url(url):
    """Extract states from URL slugs using both full names and 2-letter abbreviations."""
    found = set()
    if not url:
        return found

    # Replace URL separators with spaces for easier matching
    url_text = re.sub(r'[/\-_\.\?=&]', ' ', url.lower())

    # Check full state names (lowercased) in the URL text
    for state in US_STATES:
        if state.lower() in url_text:
            found.add(state)

    # Check 2-letter state abbreviations as standalone tokens
    # e.g. /ca/, -tx-, /wa/ etc.
    tokens = re.findall(r'\b([a-z]{2})\b', url_text)
    for token in tokens:
        if token in STATE_ABBREVS:
            found.add(STATE_ABBREVS[token])

    return found

def convert_to_csv():
    input_file = "data/serpapi_wildfire_news.json"
    output_file = "data/serpapi_wildfire_news.csv"

    with open(input_file, "r") as f:
        data = json.load(f)

    headers = ["date", "headline", "snippet", "web_url", "section", "locations"]
    improved = 0

    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()

        for item in data:
            # Parse date to ISO format
            date_str = item.get("date", "")
            iso_date = ""
            try:
                if date_str:
                    iso_date = parser.parse(date_str).strftime("%Y-%m-%dT%H:%M:%SZ")
            except Exception:
                iso_date = date_str  # Fallback to original string

            # --- Enhanced location extraction ---
            # 1. States already in JSON (scraped from title/snippet)
            states = set(item.get("states_mentioned", []))

            # 2. Re-scan title in case anything was missed
            states |= extract_states_from_text(item.get("title", ""))

            # 3. Extract from the URL slug (new: catches /california/, -tx-, etc.)
            url_states = extract_states_from_url(item.get("link", ""))
            if url_states - states:
                improved += 1
            states |= url_states

            locations = ", ".join(sorted(states)) if states else "Unknown"

            row = {
                "date": iso_date,
                "headline": item.get("title", ""),
                "snippet": "",
                "web_url": item.get("link", ""),
                "section": item.get("source", ""),
                "locations": locations
            }
            writer.writerow(row)

    print(f"Successfully converted {len(data)} items to {output_file}")
    print(f"URL extraction improved location for {improved} additional articles")

if __name__ == "__main__":
    convert_to_csv()
