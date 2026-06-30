import osmnx as ox
import networkx as nx
import matplotlib.pyplot as plt
import folium

CENTER_POINT = (37.7873, -122.4208) #midpoint between the two location below
#test one: (37.7714, -122.4417) 
#test two: (37.7873, -122.4208)

RADIUS_METERS = 1300 #approx. .8 miles to cover both neighborhoods

ORIGIN = (37.783771, -122.414114) #starting point 
# test one: 37.7664445, -122.4503678 - The Ice Cream Bar 
#test two: (37.783771, -122.414114) - Tenderloin

DESTINATION = (37.790731, -122.427614) #ending point
# test one: 37.776262, -122.433037 - painted ladies
#test two: 37.790731, -122.427614 - lafayette park

DARKNESS_PENALTY = 3.0 #4x longer than they are
UNKNOWN_PENALTY = 1.0 #2x longer than they ar


def get_combined_graph():
    print(f"Fetching street network within {RADIUS_METERS}m of center point.") 
    G = ox.graph_from_point(CENTER_POINT, dist=RADIUS_METERS, network_type="walk") #retrieving pedestrain paths

    return G

def get_lit_data():
    tags = {"lit": True} #lit tag from OSM  
    lit_gdf = ox.features_from_point(CENTER_POINT, tags, dist=RADIUS_METERS) #volunteers who tagged w/ lighting info in OSMX

    return lit_gdf #GeoDataFrame

def merge_lit_data_into_graph(G, lit_gdf):
    #combine G and lit_gdf by using each street's OSM ID
    #build a lookup dictionary: osmid -> lit value
    lit_lookup = {}
    for idx, row in lit_gdf.iterrows():
        #get the OSM ID from the index (either tuple or a plain val)
        osmid = idx[1] if isinstance(idx, tuple) else idx

        lit_value = row.get("lit", None)#get the actual lit val  (yes, no, limited)
        if lit_value is not None: #add if it exists 
            lit_lookup[osmid] = lit_value
    matched = 0
    unmatched = 0

    #u = start node, v= end node, k =edge key 
    for u, v, k, data in G.edges(keys=True, data=True): #loop every edge in G
        osmid = data.get("osmid", None) 

        if isinstance(osmid, list):
            #check each osmid in the list until we find one in our lookup
            found = None
            for oid in osmid:
                if oid in lit_lookup:
                    found = lit_lookup[oid]
                    break #stop as soon as we find a match
            if found:
                data["lit"] = found
                matched += 1
            else:
                unmatched += 1
        else:
            if osmid in lit_lookup:
                data["lit"] = lit_lookup[osmid]
                matched += 1
            else:
                unmatched += 1

    print(f"Matched lighting data to {matched} edges ({unmatched} unmatched).") #report how many edges got lighting data attached
    return G

def assign_darkness_cost(G, darkness_penalty=DARKNESS_PENALTY, unknown_penalty=UNKNOWN_PENALTY):
    for u, v, k, data in G.edges(keys=True, data=True): #iteriaite through every edge in the graph

        length = data.get("length", 1) 
        lit_value = data.get("lit", None) #lighting status
        #inflate the weight for unknown/ no lit  so Dijkstra's algo avoids them
        if lit_value == "yes": #penalty multiplier based on lighting status
            penalty = 0 #st confirmed
        elif lit_value == "no":
            penalty = darkness_penalty 
        else:
            penalty = unknown_penalty #be cautious rather than assuming it's safe

        data["cost"] = length * (1 + penalty) 

def report_lighting_coverage(G):
    #count of how many edges fall into each lighting category
    total = 0
    lit_yes = 0
    lit_no = 0
    unknown = 0

    for u, v, k, data in G.edges(keys=True, data=True):
        total += 1  # count every edge regardless of lighting status
        lit_value = data.get("lit", None)
        if lit_value == "yes":
            lit_yes += 1
        elif lit_value == "no":
            lit_no += 1
        else:
            unknown += 1  #no "lit" tag was found for this edge

    print("\nLighting Data Coverage Report")
    print(f"Total street segments: {total}")
    print(f"Tagged lit=yes:        {lit_yes} ({100*lit_yes/total:.1f}%)")
    print(f"Tagged lit=no:         {lit_no} ({100*lit_no/total:.1f}%)")
    print(f"No lighting data:      {unknown} ({100*unknown/total:.1f}%)")
    print("\n")

def find_and_compare_routes(G, origin_point, destination_point):
    orig_node = ox.distance.nearest_nodes(G, origin_point[1], origin_point[0]) #graoh node closet to the origin
    dest_node = ox.distance.nearest_nodes(G, destination_point[1], destination_point[0]) #graph node closet to destination

    shortest_route = nx.shortest_path(G, orig_node, dest_node, weight="length") #Dijkstra's algorithm that uses the standard shortest path
    lit_route = nx.shortest_path(G, orig_node, dest_node, weight="cost") #running the algo again but w/ custom darkness weight 

    return shortest_route, lit_route, orig_node, dest_node

def plot_comparison(G, shortest_route, lit_route, save_path="route_comparison.png"): #static image compares both routes
    fig, ax = ox.plot_graph_routes( #OSMx built in route plotter
        G,
        routes=[shortest_route, lit_route],
        route_colors=["red", "green"],# red= shortest and green =best-lit
        route_linewidth=4,                 
        node_size=0,                          
        show=False,                     
        close=False,                     
    )
    ax.set_title("Red = Shortest Path | Green = Best-Lit Path")
    plt.savefig(save_path, dpi=200, bbox_inches="tight")

def make_interactive_map(G, shortest_route, lit_route, save_path="route_map.html"): #using Folium for intereactive map
    #helper function (converts a list of graph node IDs into coordinate pairs)
    def route_to_coords(route):
        return [(G.nodes[n]["y"], G.nodes[n]["x"]) for n in route]

    shortest_coords = route_to_coords(shortest_route)
    lit_coords = route_to_coords(lit_route)

    m = folium.Map(location=CENTER_POINT, zoom_start=15, tiles="CartoDB positron")

    #shortest path
    folium.PolyLine(
        shortest_coords,
        color="red",
        weight=5,       
        opacity=0.8,  
        tooltip="Shortest path (ignores lighting)",
    ).add_to(m)

    #litpath 
    folium.PolyLine( 
        lit_coords,
        color="green",
        weight=5,
        opacity=0.8,
        tooltip="Best-lit path",
    ).add_to(m)

    folium.Marker(
        shortest_coords[0],
        popup="Start: The Ice Cream Bar (Cole Valley)",
        icon=folium.Icon(color="blue"),
    ).add_to(m)

 
    folium.Marker(
        shortest_coords[-1],
        popup="Destination: Painted Ladies! (Alamo Square)",
        icon=folium.Icon(color="purple"),
    ).add_to(m)

    legend_html = """
    <div style="position: fixed; bottom: 30px; left: 30px; z-index: 9999;
                background-color: white; padding: 10px; border: 2px solid grey;
                border-radius: 6px; font-size: 14px;">
        <b>Route Legend</b><br>
        <span style="color:red;">&#9644;&#9644;&#9644;</span> Shortest path<br>
        <span style="color:green;">&#9644;&#9644;&#9644;</span> Best-lit path
    </div>
    """

    m.get_root().html.add_child(folium.Element(legend_html))
    m.save(save_path)
 
if __name__ == "__main__":

    G = get_combined_graph() #street network
    lit_gdf = get_lit_data() #lighting tag data
    G = merge_lit_data_into_graph(G, lit_gdf) #attaching lightintg data onto graph's edges
    assign_darkness_cost(G) #calc darkness for each street

    report_lighting_coverage(G)

    shortest_route, lit_route, orig_node, dest_node = find_and_compare_routes(
        G, ORIGIN, DESTINATION
    ) 

    shortest_length = nx.shortest_path_length(G, orig_node, dest_node, weight="length") #calcs the actual dist of shortest path 
    lit_route_length = sum(
        G[u][v][0]["length"] for u, v in zip(lit_route[:-1], lit_route[1:]) #pairs up consecutive nodes
    )

    print(f"Shortest path distance: {shortest_length:.0f} meters")
    print(f"Best-lit path distance: {lit_route_length:.0f} meters")
    print(f"Extra distance for better lighting: {lit_route_length - shortest_length:.0f} meters")

    plot_comparison(G, shortest_route, lit_route)
    make_interactive_map(G, shortest_route, lit_route)