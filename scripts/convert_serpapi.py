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

# News outlet name
CITY_TO_STATE = {
    # Regions
    "bay area": "California",
    "socal": "California",
    "norcal": "California",
    "southern california": "California",
    "northern california": "California",
    "inland empire": "California",
    "central valley": "California",
    "san francisco": "California",
    "los angeles": "California",
    "san diego": "California",
    "sacramento": "California",
    "fresno": "California",
    "bakersfield": "California",
    "san jose": "California",
    "oakland": "California",
    "long beach": "California",
    "anaheim": "California",
    "riverside": "California",
    "stockton": "California",
    "santa barbara": "California",
    "ventura": "California",
    "palm springs": "California",
    "new york city": "New York",
    "new york": "New York",
    "nyc": "New York",
    "buffalo": "New York",
    "albany": "New York",
    "rochester": "New York",
    "chicago": "Illinois",
    "springfield": "Illinois",
    "houston": "Texas",
    "dallas": "Texas",
    "san antonio": "Texas",
    "austin": "Texas",
    "fort worth": "Texas",
    "el paso": "Texas",
    "lubbock": "Texas",
    "amarillo": "Texas",
    "phoenix": "Arizona",
    "tucson": "Arizona",
    "mesa": "Arizona",
    "scottsdale": "Arizona",
    "flagstaff": "Arizona",
    "denver": "Colorado",
    "colorado springs": "Colorado",
    "boulder": "Colorado",
    "fort collins": "Colorado",
    "seattle": "Washington",
    "spokane": "Washington",
    "tacoma": "Washington",
    "portland": "Oregon",
    "eugene": "Oregon",
    "bend": "Oregon",
    "las vegas": "Nevada",
    "reno": "Nevada",
    "henderson": "Nevada",
    "albuquerque": "New Mexico",
    "santa fe": "New Mexico",
    "salt lake city": "Utah",
    "salt lake": "Utah",
    "provo": "Utah",
    "miami": "Florida",
    "orlando": "Florida",
    "tampa": "Florida",
    "jacksonville": "Florida",
    "tallahassee": "Florida",
    "pensacola": "Florida",
    "atlanta": "Georgia",
    "savannah": "Georgia",
    "charlotte": "North Carolina",
    "raleigh": "North Carolina",
    "greensboro": "North Carolina",
    "nashville": "Tennessee",
    "memphis": "Tennessee",
    "knoxville": "Tennessee",
    "chattanooga": "Tennessee",
    "louisville": "Kentucky",
    "lexington": "Kentucky",
    "birmingham": "Alabama",
    "montgomery": "Alabama",
    "mobile": "Alabama",
    "jackson": "Mississippi",
    "new orleans": "Louisiana",
    "baton rouge": "Louisiana",
    "shreveport": "Louisiana",
    "little rock": "Arkansas",
    "oklahoma city": "Oklahoma",
    "tulsa": "Oklahoma",
    "wichita": "Kansas",
    "kansas city": "Kansas",
    "omaha": "Nebraska",
    "lincoln": "Nebraska",
    "minneapolis": "Minnesota",
    "st paul": "Minnesota",
    "duluth": "Minnesota",
    "milwaukee": "Wisconsin",
    "madison": "Wisconsin",
    "detroit": "Michigan",
    "grand rapids": "Michigan",
    "lansing": "Michigan",
    "cleveland": "Ohio",
    "columbus": "Ohio",
    "cincinnati": "Ohio",
    "toledo": "Ohio",
    "indianapolis": "Indiana",
    "fort wayne": "Indiana",
    "pittsburgh": "Pennsylvania",
    "philadelphia": "Pennsylvania",
    "allentown": "Pennsylvania",
    "hartford": "Connecticut",
    "bridgeport": "Connecticut",
    "providence": "Rhode Island",
    "boston": "Massachusetts",
    "worcester": "Massachusetts",
    "springfield": "Massachusetts",
    "manchester": "New Hampshire",
    "concord": "New Hampshire",
    "portland": "Maine",
    "burlington": "Vermont",
    "newark": "New Jersey",
    "jersey city": "New Jersey",
    "trenton": "New Jersey",
    "wilmington": "Delaware",
    "dover": "Delaware",
    "baltimore": "Maryland",
    "annapolis": "Maryland",
    "richmond": "Virginia",
    "virginia beach": "Virginia",
    "norfolk": "Virginia",
    "roanoke": "Virginia",
    "charleston": "West Virginia",
    "huntington": "West Virginia",
    "columbia": "South Carolina",
    "charleston": "South Carolina",
    "greenville": "South Carolina",
    "fargo": "North Dakota",
    "bismarck": "North Dakota",
    "sioux falls": "South Dakota",
    "pierre": "South Dakota",
    "billings": "Montana",
    "missoula": "Montana",
    "boise": "Idaho",
    "nampa": "Idaho",
    "cheyenne": "Wyoming",
    "casper": "Wyoming",
    "anchorage": "Alaska",
    "fairbanks": "Alaska",
    "juneau": "Alaska",
    "honolulu": "Hawaii",
    "hilo": "Hawaii",
    "washington dc": "Virginia",
    "washington d.c.": "Virginia",
}


def extract_states_from_text(text):
    found = set()
    if not text:
        return found
    for state in US_STATES:
        if re.search(r'\b' + re.escape(state) + r'\b', text, re.IGNORECASE):
            found.add(state)
    return found


def extract_states_from_url(url):
    found = set()
    if not url:
        return found
    url_text = re.sub(r'[/\-_\.\?=&]', ' ', url.lower())
    for state in US_STATES:
        if state.lower() in url_text:
            found.add(state)
    tokens = re.findall(r'\b([a-z]{2})\b', url_text)
    for token in tokens:
        if token in STATE_ABBREVS:
            found.add(STATE_ABBREVS[token])
    return found


def extract_state_from_source(source):
    """Try to infer a US state from the news source name (e.g. 'NBC Bay Area' -> California)."""
    found = set()
    if not source:
        return found
    src_lower = source.lower()

    # check source name
    found |= extract_states_from_text(source)

    
    for city, state in sorted(CITY_TO_STATE.items(), key=lambda x: -len(x[0])):
        if city in src_lower:
            found.add(state)
            break  

    return found


def mentions_australia(item):
    text = ' '.join([
        item.get('title', ''),
        item.get('link', ''),
        item.get('source', '')
    ])
    return bool(re.search(r'\baustrali[a-z]*\b', text, re.IGNORECASE))


def convert_to_csv():
    input_file = "data/serpapi_wildfire_news.json"
    output_file = "data/serpapi_wildfire_news.csv"

    with open(input_file, "r") as f:
        data = json.load(f)

    # Remove Australia articles
    before = len(data)
    data = [item for item in data if not mentions_australia(item)]
    removed = before - len(data)
    if removed:
        print(f"Removed {removed} Australia-related articles.")

    headers = ["date", "headline", "snippet", "web_url", "section", "locations"]
    source_improved = 0
    still_unknown = 0

    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()

        for item in data:
            # Parse date
            date_str = item.get("date", "")
            iso_date = ""
            try:
                if date_str:
                    iso_date = parser.parse(date_str).strftime("%Y-%m-%dT%H:%M:%SZ")
            except Exception:
                iso_date = date_str

            # Layer 1: states from scraped JSON
            states = set(item.get("states_mentioned", []))
            # Layer 2: re-scan title
            states |= extract_states_from_text(item.get("title", ""))
            # Layer 3: scan URL slug
            states |= extract_states_from_url(item.get("link", ""))

            # Layer 4 (fallback): only if still nothing, try inferring from source name
            if not states:
                source_states = extract_state_from_source(item.get("source", ""))
                if source_states:
                    states |= source_states
                    source_improved += 1
                else:
                    still_unknown += 1

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

    

if __name__ == "__main__":
    convert_to_csv()
