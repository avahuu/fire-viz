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
     "berkeleyside": "California",
    "kqed": "California",
    "calmatters": "California",
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

    # Organized output folders
    os.makedirs("data/processed", exist_ok=True)
    output_file = "data/processed/serpapi_wildfire_news.csv"

    with open(input_file, "r") as f:
        data = json.load(f)

    # Remove Australia articles
    before = len(data)
    data = [item for item in data if not mentions_australia(item)]
    removed = before - len(data)
    if removed:
        print(f"Removed {removed} Australia-related articles.")

    # Remove .gov source articles
    before = len(data)
    data = [item for item in data if ".gov" not in item.get("source", "").lower()]
    removed_gov = before - len(data)
    if removed_gov:
        print(f"Removed {removed_gov} .gov source articles.")

    # Deduplicate by URL
    before = len(data)
    seen = set()
    deduped = []
    for item in data:
        url = item.get("link", "")
        if url not in seen:
            seen.add(url)
            deduped.append(item)
    data = deduped
    print(f"Removed {before - len(data)} duplicate articles. {len(data)} unique articles remaining.")



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

    print(f"Successfully converted {len(data)} items to {output_file}")
    print(f"Source name inference resolved location for {source_improved} additional articles")
    print(f"Still 'Unknown' after all layers: {still_unknown} articles")


def make_choropleth():
    """Read the manually curated geocoded Numbers file and count articles per state."""
    from numbers_parser import Document
    from collections import Counter

    STATES_META = [
        ('01','AL','Alabama'), ('02','AK','Alaska'), ('04','AZ','Arizona'),
        ('05','AR','Arkansas'), ('06','CA','California'), ('08','CO','Colorado'),
        ('09','CT','Connecticut'), ('10','DE','Delaware'),
        ('12','FL','Florida'), ('13','GA','Georgia'), ('15','HI','Hawaii'),
        ('16','ID','Idaho'), ('17','IL','Illinois'), ('18','IN','Indiana'),
        ('19','IA','Iowa'), ('20','KS','Kansas'), ('21','KY','Kentucky'),
        ('22','LA','Louisiana'), ('23','ME','Maine'), ('24','MD','Maryland'),
        ('25','MA','Massachusetts'), ('26','MI','Michigan'), ('27','MN','Minnesota'),
        ('28','MS','Mississippi'), ('29','MO','Missouri'), ('30','MT','Montana'),
        ('31','NE','Nebraska'), ('32','NV','Nevada'), ('33','NH','New Hampshire'),
        ('34','NJ','New Jersey'), ('35','NM','New Mexico'), ('36','NY','New York'),
        ('37','NC','North Carolina'), ('38','ND','North Dakota'), ('39','OH','Ohio'),
        ('40','OK','Oklahoma'), ('41','OR','Oregon'), ('42','PA','Pennsylvania'),
        ('44','RI','Rhode Island'), ('45','SC','South Carolina'), ('46','SD','South Dakota'),
        ('47','TN','Tennessee'), ('48','TX','Texas'), ('49','UT','Utah'),
        ('50','VT','Vermont'), ('51','VA','Virginia'), ('53','WA','Washington'),
        ('54','WV','West Virginia'), ('55','WI','Wisconsin'), ('56','WY','Wyoming'),
    ]

    input_file = "data/manuly/M_serpapi_wildfire_news_geocoded.numbers"
    output_file = "data/processed/news_choropleth.csv"

    print(f"\nReading {input_file}...")
    doc = Document(input_file)
    sheet = doc.sheets[0]
    table = sheet.tables[0]
    rows = list(table.rows())
    headers = [cell.value for cell in rows[0]]
    data = [[cell.value for cell in row] for row in rows[1:]]

    import csv as csv_module
    counts = Counter()
    for row in data:
        row_dict = dict(zip(headers, row))
        locs = str(row_dict.get("locations", "")).strip()
        if locs and locs != "Unknown":
            for state in locs.split(", "):
                state = state.strip()
                if state:
                    counts[state] += 1

    os.makedirs("data/processed", exist_ok=True)
    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv_module.DictWriter(f, fieldnames=["FIPS", "STUSPS", "NAME", "Article_Count"])
        writer.writeheader()
        for fips, abbr, name in STATES_META:
            writer.writerow({"FIPS": fips, "STUSPS": abbr, "NAME": name, "Article_Count": counts.get(name, 0)})

    print(f"Saved choropleth to {output_file}")
    top5 = counts.most_common(5)
    print("Top 5 states: " + ", ".join(f"{s}={c}" for s, c in top5))


if __name__ == "__main__":
    convert_to_csv()
    make_choropleth()
