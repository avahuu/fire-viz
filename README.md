# Fire-Viz Wildfire Reality vs Media Coverage (2020–2024)

An interactive overlay map comparing **where wildfires actually burned** (satellite-verified) with **where the media reported on them**, revealing geographic gaps in news coverage across the United States.

---

## Data Sources

### Fire Perimeters MTBS

| Detail              | Value                                                         |
| ------------------- | ------------------------------------------------------------- |
| **Source**          | [MTBS Direct Download](https://www.mtbs.gov/direct-download)  |
| **Basis**           | Landsat satellite imagery                                     |
| **Coverage**        | 1984–present (US-wide)                                        |
| **Threshold**       | ≥1,000 acres (West) · ≥500 acres (East)                       |
| **Layer used**      | `Boundaries` shapefile, filtered to `Event_Type = 'Wildfire'` |
| **Already in repo** | `mtbs_perimeter_data/` and `mtbs_fod_pts_data/`               |

> **Known bias:** Very small fires (<500–1000 ac) are excluded, but these are not the focus of this study and the threshold is well-documented.

### Media Coverage

| Detail             | Value                                                                                                |
| ------------------ | ---------------------------------------------------------------------------------------------------- |
| **Source**         | [NYT Developer Portal](https://developer.nytimes.com/)                                               |
| **Endpoint**       | Article Search API v2                                                                                |
| **Rate limits**    | 10 requests/min · 4,000 requests/day (free tier)                                                     |
| **Archive depth**  | Back to 1851                                                                                         |
| **Query strategy** | Keywords `"wildfire" OR "forest fire" OR "bushfire"`, filtered by `begin_date` / `end_date` per year |
