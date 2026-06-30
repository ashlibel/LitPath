import osmnx as ox

CANDIDATES = {
    "Painted Ladies / Alamo Square": (37.7762, -122.4329),
    "Western Addition / Fillmore": (37.7800, -122.4330),
    "Hayes Valley": (37.7766, -122.4244),
    "Lower Haight": (37.7715, -122.4310),
    "Bayview (for contrast)": (37.7300, -122.3930),
    "Visitacion Valley (for contrast)": (37.7150, -122.4040),
    "Excelsior": (37.7250, -122.4280),
    "Outer Mission": (37.7220, -122.4400),
    "Portola": (37.7280, -122.4150),
    "Ingleside": (37.7200, -122.4530),
    "Glen Park": (37.7340, -122.4330),
    "Bernal Heights": (37.7390, -122.4150),
    "Mission District": (37.7600, -122.4180),
    "Sunnydale / Visitacion Valley North": (37.7180, -122.4090),
    "Pacific Heights": (37.7925, -122.4382),
    "Noe Valley": (37.7502, -122.4337),
    "Cole Valley": (37.7665, -122.4505),
}

RADIUS_METERS = 1000


#scans each neighborhood listed above to count how many streets have lightin info vs. unknown
def scan_area(name, center_point, radius=RADIUS_METERS):

    print(f"\nScanning: {name} ...") #tracking the progress making sure it did not crash

    #wraps in try/except to have scirpt still run even if OSMX has no data
    try:
        G = ox.graph_from_point(center_point, dist=radius, network_type="walk") #grpahs where intersections are nodes + st segmentns are edges
    except Exception as e:
        print(f"  Failed to fetch street network: {e}") #download fails then skip
        return None

    try:
        lit_gdf = ox.features_from_point(center_point, {"lit": True}, dist=radius)

        #build the lookup dict from the results
        lit_lookup = {}
        for idx, row in lit_gdf.iterrows():
            osmid = idx[1] if isinstance(idx, tuple) else idx #osmx ID (tuple or number)
            lit_value = row.get("lit", None) #actual lit value 

            if lit_value is not None: #store if val exists 
                lit_lookup[osmid] = lit_value

    except Exception as e:
        print(f"  No lighting features found: {e}") 
        lit_lookup = {}
    
    total = 0 #total number of street segments
    lit_yes = 0 #streets confirmed as lit
    lit_no = 0 #streets confirmed as unlit
    unknown = 0 # treets with no lighting data at all

    # u =start node / v = end node/ k = edge key/ data = edge attributes
    for u, v, k, data in G.edges(keys=True, data=True):

        total += 1
        osmid = data.get("osmid", None)
        lit_value = None

        if isinstance(osmid, list):
            
            for oid in osmid:
                if oid in lit_lookup:
                    lit_value = lit_lookup[oid]
                    break  # stop as soon as we find a match
        else:
            lit_value = lit_lookup.get(osmid, None) 

        #add this edge to the right counter based on its lighting status
        if lit_value == "yes":
            lit_yes += 1
        elif lit_value == "no":
            lit_no += 1
        else:
            # No lighting data found for this edge
            unknown += 1

    #calculate what percentage of streets have any lighting data
    pct_known = 100 * (lit_yes + lit_no) / total if total else 0

    print(f"  Total segments:   {total}")
    print(f"  lit=yes:          {lit_yes} ({100*lit_yes/total:.1f}%)")
    print(f"  lit=no:           {lit_no} ({100*lit_no/total:.1f}%)")
    print(f"  unknown:          {unknown} ({100*unknown/total:.1f}%)")
    print(f"  TOTAL KNOWN:      {pct_known:.1f}%")

    return {
        "name": name,
        "total": total,
        "lit_yes": lit_yes,
        "lit_no": lit_no,
        "unknown": unknown,
        "pct_known": pct_known,
    }

if __name__ == "__main__":

    results = []
    for name, point in CANDIDATES.items():
        result = scan_area(name, point)

        if result: #only add if scan was successful 
            results.append(result)

    print("\nSummary ")
    #sorting  results from highest to lowest lighting data coverage
    results_sorted = sorted(results, key=lambda r: r["pct_known"], reverse=True)

    for r in results_sorted:
        print(f"{r['name']:35s} | known: {r['pct_known']:5.1f}% | "
              f"yes: {r['lit_yes']:4d} | no: {r['lit_no']:4d} | total: {r['total']:5d}")
        

        