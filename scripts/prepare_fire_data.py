import geopandas as gpd
import pandas as pd
import os

def prepare_data():
    gdf = gpd.read_file('mtbs_perimeter_data/mtbs_perims_DD.shp')

    # Filter for wildfire
    if 'Incid_Type' in gdf.columns:
        gdf = gdf[gdf['Incid_Type'] == 'Wildfire']
    elif 'Event_Type' in gdf.columns:
        gdf = gdf[gdf['Event_Type'] == 'Wildfire']
    
    
    # Filter for dates 2020 to 2024
    gdf['Ig_Date'] = pd.to_datetime(gdf['Ig_Date'], errors='coerce')
    gdf = gdf[(gdf['Ig_Date'].dt.year >= 2020) & (gdf['Ig_Date'].dt.year <= 2024)]

    # Select columns 
    cols_to_keep = ['Event_ID', 'Incid_Name', 'Incid_Type', 'BurnBndAc', 'BurnBndLat', 'BurnBndLon', 'Ig_Date', 'geometry']
    gdf = gdf[[c for c in cols_to_keep if c in gdf.columns]]
    
    # Make date a string for export
    gdf['Ig_Date'] = gdf['Ig_Date'].dt.strftime('%Y-%m-%d')
    gdf['Year'] = gdf['Ig_Date'].str[:4]
    
    os.makedirs('data', exist_ok=True)
    
    # Export to GeoJSON
    geojson_path = 'data/fires_2020_2024.geojson'
    gdf.to_file(geojson_path, driver='GeoJSON')
    
    # Export centroids to CSV for easier point maps in Datawrapper
    csv_path = 'data/fires_2020_2024_points.csv'
    df = pd.DataFrame(gdf.drop(columns='geometry'))
    df.to_csv(csv_path, index=False)

if __name__ == '__main__':
    prepare_data()
