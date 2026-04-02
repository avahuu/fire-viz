import os
import time
import requests
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.environ.get("NYT_API_KEY")

def scrape_nyt_articles():
    base_url = "https://api.nytimes.com/svc/search/v2/articlesearch.json"
    keywords = "wildfire"
    years = [2020, 2021, 2022, 2023, 2024]
    
    all_articles = []
    output_file = "data/nyt_articles.csv"
    
    if os.path.exists(output_file):
        print(f"{output_file} exists. Overwriting.")
    
    
    for year in years:
        b_date = f"{year}0101"
        e_date = f"{year}1231"
        page = 0
        
        while True:
            params = {
                "q": keywords,
                "begin_date": b_date,
                "end_date": e_date,
                "page": page,
                "api-key": API_KEY
            }
            
            
            response = requests.get(base_url, params=params)
            if response.status_code == 429:
                print("Rate limited! Waiting 15 seconds...")
                time.sleep(15)
                continue
            elif response.status_code != 200:
                print(f"Error {response.status_code}: {response.text}")
                break
            
            data = response.json()
            docs = data.get("response", {}).get("docs", [])
            meta = data.get("response", {}).get("meta", data.get("response", {}).get("metadata", {}))
            hits = meta.get("hits", 0)
            
            print(f"Retrieved {len(docs)} articles. (Total hints for {year}: {hits})")
                
            if not docs:
                break
            
            for doc in docs:
                geo_facet = doc.get("geo_facet", [])
                locations = "; ".join([str(g) for g in geo_facet]) if geo_facet else None
                
                keywords_list = [k["value"] for k in doc.get("keywords", []) if k.get("name") == "glocations"]
                glocations = "; ".join(keywords_list) if keywords_list else None
                
                # Find location data
                combined_locations = []
                if locations: combined_locations.append(locations)
                if glocations: combined_locations.append(glocations)
                final_locations = "; ".join(set(combined_locations)) if combined_locations else "Unknown"

                article_data = {
                    "date": doc.get("pub_date"),
                    "headline": doc.get("headline", {}).get("main"),
                    "snippet": doc.get("snippet"),
                    "web_url": doc.get("web_url"),
                    "section": doc.get("section_name"),
                    "locations": final_locations
                }
                all_articles.append(article_data)
            
            if (page + 1) * 10 >= hits or page >= 2:
                break
            
            page += 1
            # Rate limit is 10/min. Wait 12s to be 100% safe.
            time.sleep(12) 
            
        # Save intermediate progress for each year
        df = pd.DataFrame(all_articles)
        df.to_csv(output_file, index=False)
        print(f"--- Finished Year {year}. Total articles so far: {len(all_articles)} ---")
        time.sleep(12)

    df = pd.DataFrame(all_articles)
    df.to_csv(output_file, index=False)

if __name__ == "__main__":
    scrape_nyt_articles()
