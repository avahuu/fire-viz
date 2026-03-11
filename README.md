# 🔥 Fire-Viz: Wildfire Reality vs Media Coverage (2020–2024)

An interactive overlay map comparing **where wildfires actually burned** (satellite-verified) with **where the media reported on them**, revealing geographic gaps in news coverage across the United States.

---

## Motivation

Not all wildfires receive equal media attention. Large fires in remote areas or the interior West may burn tens of thousands of acres with little national coverage, while smaller fires near major metro areas dominate headlines. This project quantifies and visualizes that disparity.

## Data Sources

### 🔥 Fire Perimeters — MTBS (Monitoring Trends in Burn Severity)

| Detail | Value |
|---|---|
| **Source** | [MTBS Direct Download](https://www.mtbs.gov/direct-download) |
| **Basis** | Landsat satellite imagery |
| **Coverage** | 1984–present (US-wide) |
| **Threshold** | ≥1,000 acres (West) · ≥500 acres (East) |
| **Layer used** | `Boundaries` shapefile, filtered to `Event_Type = 'Wildfire'` |
| **Already in repo** | `mtbs_perimeter_data/` and `mtbs_fod_pts_data/` |

> **Known bias:** Very small fires (<500–1000 ac) are excluded, but these are not the focus of this study and the threshold is well-documented.

### 📰 Media Coverage — New York Times Article Search API *(primary)*

| Detail | Value |
|---|---|
| **Source** | [NYT Developer Portal](https://developer.nytimes.com/) |
| **Endpoint** | Article Search API v2 |
| **Rate limits** | 10 requests/min · 4,000 requests/day (free tier) |
| **Archive depth** | Back to 1851 |
| **Query strategy** | Keywords `"wildfire" OR "forest fire" OR "bushfire"`, filtered by `begin_date` / `end_date` per year |

Additional / stretch data sources under evaluation:

| Source | Type | Status |
|---|---|---|
| **GDELT GEO 2.0 API** | Free, keyword → geographic heatmap | ✅ Strong candidate — 100% free, built-in geocoding |
| **SerpAPI (Google News)** | Paid API, 250 free searches/mo | ⚠️ Limited free tier |
| **NewsData.io** | Paid API, no free historical access | ❌ $200+/mo for historical |
| **DuckDuckGo (`duckduckgo_search`)** | Python library, free | ⚠️ Fragile, no official API |

## Architecture (Planned)

```
mtbs_perimeter_data/          ← raw MTBS shapefiles (already downloaded)
mtbs_fod_pts_data/            ← raw MTBS fire-of-discovery points
scripts/
  prepare_fire_data.py        ← filter & convert MTBS → GeoJSON
  scrape_nyt.py               ← query NYT API, store articles
  geocode_articles.py         ← extract locations from article metadata
  (optional) scrape_gdelt.py  ← pull GDELT GEO data
data/
  fires_2020_2024.geojson     ← processed fire perimeters
  nyt_articles.csv            ← scraped article metadata
  media_coverage.geojson      ← geocoded media points
web/
  index.html                  ← interactive Mapbox/Leaflet map
  style.css
  app.js
```

## Getting Started

> **Prerequisites:** Python 3.10+, a free NYT Developer API key

```bash
# Clone & enter
git clone <repo-url> && cd fire-viz

# Install Python dependencies
pip install geopandas shapely requests folium

# Prepare fire data
python scripts/prepare_fire_data.py

# Scrape NYT articles (requires API key in .env)
python scripts/scrape_nyt.py

# Geocode articles
python scripts/geocode_articles.py

# Open the map
open web/index.html   # or serve with: python -m http.server -d web
```

## Roadmap

- [x] Download MTBS fire boundary data
- [ ] Filter & convert fire data to GeoJSON (2020–2024, wildfires only)
- [ ] Build NYT Article Search scraper
- [ ] Geocode article locations
- [ ] Build interactive overlay map
- [ ] Add time slider and summary stats
- [ ] (Stretch) Integrate GDELT as secondary coverage source
- [ ] (Stretch) Compute quantitative "coverage gap" scores

## License

Academic / research use. MTBS data is public domain (USGS). NYT article metadata is subject to [NYT API Terms of Service](https://developer.nytimes.com/terms).
