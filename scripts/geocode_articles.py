import pandas as pd

# Full 50-state centroids
STATE_CENTROIDS = {
    "Alabama": {"lat": 32.8067, "lon": -86.7911},
    "Alaska": {"lat": 64.2008, "lon": -149.4937},
    "Arizona": {"lat": 34.0489, "lon": -111.0937},
    "Arkansas": {"lat": 34.7999, "lon": -92.1999},
    "California": {"lat": 36.7782, "lon": -119.4179},
    "Colorado": {"lat": 39.5501, "lon": -105.7821},
    "Connecticut": {"lat": 41.6032, "lon": -73.0877},
    "Delaware": {"lat": 38.9108, "lon": -75.5277},
    "Florida": {"lat": 27.9944, "lon": -81.7603},
    "Georgia": {"lat": 32.1656, "lon": -82.9001},
    "Hawaii": {"lat": 19.8968, "lon": -155.5828},
    "Idaho": {"lat": 44.0682, "lon": -114.7420},
    "Illinois": {"lat": 40.6331, "lon": -89.3985},
    "Indiana": {"lat": 40.2672, "lon": -86.1349},
    "Iowa": {"lat": 41.8780, "lon": -93.0977},
    "Kansas": {"lat": 39.0119, "lon": -98.4842},
    "Kentucky": {"lat": 37.8393, "lon": -84.2700},
    "Louisiana": {"lat": 31.2448, "lon": -92.1450},
    "Maine": {"lat": 45.2538, "lon": -69.4455},
    "Maryland": {"lat": 39.0458, "lon": -76.6413},
    "Massachusetts": {"lat": 42.4072, "lon": -71.3824},
    "Michigan": {"lat": 44.3148, "lon": -85.6024},
    "Minnesota": {"lat": 46.7296, "lon": -94.6859},
    "Mississippi": {"lat": 32.3547, "lon": -89.3985},
    "Missouri": {"lat": 37.9643, "lon": -91.8318},
    "Montana": {"lat": 46.9219, "lon": -110.4544},
    "Nebraska": {"lat": 41.4925, "lon": -99.9018},
    "Nevada": {"lat": 38.8026, "lon": -116.4194},
    "New Hampshire": {"lat": 43.1939, "lon": -71.5724},
    "New Jersey": {"lat": 40.0583, "lon": -74.4057},
    "New Mexico": {"lat": 34.5199, "lon": -105.8701},
    "New York": {"lat": 42.1657, "lon": -74.9481},
    "North Carolina": {"lat": 35.6301, "lon": -79.8064},
    "North Dakota": {"lat": 47.5515, "lon": -101.0020},
    "Ohio": {"lat": 40.4173, "lon": -82.9071},
    "Oklahoma": {"lat": 35.5653, "lon": -96.9289},
    "Oregon": {"lat": 43.8041, "lon": -120.5542},
    "Pennsylvania": {"lat": 41.2033, "lon": -77.1945},
    "Rhode Island": {"lat": 41.6809, "lon": -71.5118},
    "South Carolina": {"lat": 33.8361, "lon": -81.1637},
    "South Dakota": {"lat": 43.9695, "lon": -99.9018},
    "Tennessee": {"lat": 35.7478, "lon": -86.6923},
    "Texas": {"lat": 31.9686, "lon": -99.9018},
    "Utah": {"lat": 39.3200, "lon": -111.0937},
    "Vermont": {"lat": 44.5588, "lon": -72.5778},
    "Virginia": {"lat": 37.4316, "lon": -78.6569},
    "Washington": {"lat": 47.7511, "lon": -120.7401},
    "West Virginia": {"lat": 38.5976, "lon": -80.4549},
    "Wisconsin": {"lat": 43.7844, "lon": -88.7879},
    "Wyoming": {"lat": 43.0760, "lon": -107.2903},
}

def geocode_articles():
    input_csv = "data/processed/serpapi_wildfire_news.csv"
    output_csv = "data/processed/serpapi_wildfire_news_geocoded.csv"

    print(f"Loading {input_csv}...")
    df = pd.read_csv(input_csv)
    print(f"Total articles: {len(df)}")

    lats, lons = [], []

    for _, row in df.iterrows():
        locations = str(row.get("locations", ""))
        lat, lon = None, None

        # Use the first recognized state in the locations column
        for state, coords in STATE_CENTROIDS.items():
            if state in locations:
                lat = coords["lat"]
                lon = coords["lon"]
                break

        lats.append(lat)
        lons.append(lon)

    df["lat"] = lats
    df["lon"] = lons

    geocoded_count = df[["lat", "lon"]].notna().all(axis=1).sum()
    df.to_csv(output_csv, index=False)

    print(f"Geocoded {geocoded_count} / {len(df)} articles ({geocoded_count/len(df)*100:.1f}%)")
    print(f"Saved to {output_csv}")

if __name__ == "__main__":
    geocode_articles()
