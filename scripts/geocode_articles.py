import pandas as pd
import json

# Common state centroid approximate coordinates for quick geocoding
# In NYT data, geo_facet often gives State names or major cities.
STATE_CENTROIDS = {
    "California": {"lat": 36.7782, "lon": -119.4179},
    "Oregon": {"lat": 43.8041, "lon": -120.5542},
    "Washington State": {"lat": 47.7511, "lon": -120.7401},
    "Colorado": {"lat": 39.5501, "lon": -105.7821},
    "Texas": {"lat": 31.9686, "lon": -99.9018},
    "Arizona": {"lat": 34.0489, "lon": -111.0937},
    "New Mexico": {"lat": 34.5199, "lon": -105.8701},
    "Nevada": {"lat": 38.8026, "lon": -116.4194},
    "Utah": {"lat": 39.3200, "lon": -111.0937},
    "Idaho": {"lat": 44.0682, "lon": -114.7420},
    "Montana": {"lat": 46.9219, "lon": -110.4544},
    "Wyoming": {"lat": 43.0760, "lon": -107.2903},
    "Alaska": {"lat": 64.2008, "lon": -149.4937},
    "Hawaii": {"lat": 19.8968, "lon": -155.5828},
}

def geocode_articles():
    print("Loading scraped NYT articles...")
    try:
        df = pd.read_csv("data/nyt_articles.csv")
    except FileNotFoundError:
        print("data/nyt_articles.csv not found yet. Run scrape_nyt.py first.")
        return
    
    print(f"Total articles loaded: {len(df)}")
    
    geocoded_rows = []
    
    for _, row in df.iterrows():
        locations = str(row['locations']) if pd.notnull(row['locations']) else ""
        lat, lon = None, None
        
        # 1) Specific state matches
        for state, coords in STATE_CENTROIDS.items():
            if state in locations or state in str(row['headline']) or state in str(row['snippet']):
                lat = coords['lat']
                lon = coords['lon']
                break
        
        if pd.notnull(row['headline']) and lat is None:
            # Fallback simple guesses based on "Maui", "Dixie", "Camp Fire"
            headline_lower = row['headline'].lower()
            if "hawaii" in headline_lower or "maui" in headline_lower or "lahaina" in headline_lower:
                lat, lon = 20.8783, -156.6825 # Maui
            elif "california" in headline_lower or "dixie" in headline_lower:
                lat, lon = STATE_CENTROIDS['California']['lat'], STATE_CENTROIDS['California']['lon']
            elif "oregon" in headline_lower:
                lat, lon = STATE_CENTROIDS['Oregon']['lat'], STATE_CENTROIDS['Oregon']['lon']
            elif "colorado" in headline_lower or "marshall" in headline_lower:
                lat, lon = STATE_CENTROIDS['Colorado']['lat'], STATE_CENTROIDS['Colorado']['lon']
        
        geocoded_rows.append({
            "date": row['date'],
            "headline": row['headline'],
            "snippet": row['snippet'],
            "web_url": row['web_url'],
            "locations": row['locations'],
            "lat": lat,
            "lon": lon
        })
    
    geo_df = pd.DataFrame(geocoded_rows)
    # Give it a final pass where only non-null lat/lons are kept, or mark them as Unknown
    geocoded_count = len(geo_df.dropna(subset=['lat', 'lon']))
    
    output_csv = "data/nyt_articles_geocoded.csv"
    geo_df.to_csv(output_csv, index=False)
    print(f"Finished geocoding! {geocoded_count} out of {len(geo_df)} articles have lat/lon.")
    print(f"Saved to {output_csv}")

if __name__ == "__main__":
    geocode_articles()
