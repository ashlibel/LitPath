# LitPath — Best-Lit Pedestrian Route Finder
LitPath repurposes Dijkstra's shortest-path algorithm to route pedestrians around darkness instead of distance. It downloads a real San Francisco street network from OpenStreetMap (OSMnX), attaches volunteer-tagged lighting data, and computes two routes between any two points: the standard shortest path (what Google Maps would give you) and a "best-lit" path that avoids unlit or undocumented streets where possible.

## What's in this folder

**main.py** — The core project. Downloads the street network and lighting data for a chosen area, runs both the shortest-path and best-lit-path algorithms, and outputs a static map image and an interactive HTML map.

**scan_neighborhoods.py** — A diagnostic script that scans multiple SF neighborhoods at once and reports what percentage of streets in each one have OSM lighting data. Used to decide which areas are reliable enough to route through. Only for 17 neighborhoods in SF.

**chart_coverage.py** — Generates a bar chart visualizing the neighborhood coverage scan results. 

**route_comparison.png** — Output of main.py, a static image showing both routes (red = shortest, green = best-lit) for whichever coordinates are currently set.


**route_map.html** — Output of main.py, an interactive, zoomable browser map of both routes. Double-click to open in any browser. Or you can open with LiveServer.

## Requirements

This project runs in Python 3 and needs the following packages:

pip install osmnx networkx matplotlib geopandas folium scikit-learn

**osmnx** — Downloads real street network and lighting-tag data from OpenStreetMap.

**networkx** — Runs Dijkstra's shortest-path algorithm on the graph.

**matplotlib** — Generates the static route_comparison.png image.

**geopandas** — Required by OSMnx to handle geographic data internally.

**folium** — Builds the interactive route_map.html map.

**scikit-learn** — Required by OSMnx for nearest-node spatial lookups.

## How to run it

1. Create and activate a virtual environment (recommended):

python3 -m venv venv
source venv/bin/activate
(Windows: venv\Scripts\activate)

2. Install dependencies:

pip install osmnx networkx matplotlib geopandas folium scikit-learn

3. Run the main script:

python3 main.py

4. Open the outputs:

route_comparison.png opens like any image file.
OR type this in the terminal to see the image:
open route_comparison.png

route_map.html should be opened by double-clicking it, or right-click and choose Open With and select your browser.

5. (Optional) Run the neighborhood scan and coverage chart:

python3 scan_neighborhoods.py
python3 chart_coverage.py

## Changing the test location

main.py is already set up to test two real San Francisco routes. The coordinates for both are saved as comments above the active settings so you can switch between them.

CENTER_POINT = (37.7873, -122.4208) #midpoint between the two location below
#test one: (37.7714, -122.4417) 
#test two: (37.7873, -122.4208)

ORIGIN = (37.783771, -122.414114) #starting point 
#test one: 37.7664445, -122.4503678 - The Ice Cream Bar 
#test two: (37.783771, -122.414114) - Tenderloin

DESTINATION = (37.790731, -122.427614) #ending point
#test one: 37.776262, -122.433037 - painted ladies
#test two: 37.790731, -122.427614 - lafayette park

To switch back to test one (Cole Valley to Painted Ladies),replace the active CENTER_POINT, ORIGIN, and DESTINATION lines with the values listed in the comments below them.

### Testing a brand new location

You can route between any two points in San Francisco, or any city OSMnx can reach. To do this:

1. Find the latitude and longitude of your two points. In Google Maps, right-click any spot and the coordinates appear at the top of the menu.

2. Set ORIGIN and DESTINATION to those two coordinate pairs.

3. Set CENTER_POINT to the midpoint between them, so the downloaded street network covers both locations. A quick way to estimate the midpoint is to average the two latitudes together, and average the two longitudes together.

4. Make sure RADIUS_METERS is large enough to cover the distance between ORIGIN and DESTINATION from CENTER_POINT. If the route fails to find a path, increase this value.

5. Run python3 main.py again.

Example, testing a new route from the Ferry Building to Union Square:

ORIGIN = (37.7955, -122.3937)        # Ferry Building
DESTINATION = (37.7880, -122.4075)   # Union Square
CENTER_POINT = (37.7918, -122.4006)  # midpoint
RADIUS_METERS = 1000

## Project background

This project was built on Dijkstra's algorithm, the same one behind most navigation apps, is repurposed here to optimize for lighting safety instead of distance, by replacing each street segment's edge weight with a darkness-adjusted cost.

While testing this across 17 San Francisco neighborhoods using scan_neighborhoods.py, lighting data coverage was found to range from 0.1% to 64.2%.

## Resources / Citations

This project relies on the following open-source tools, cited per their requested citation format:

Boeing, G. (2025). Modeling and Analyzing Urban Networks and Amenities with OSMnx. Geographical Analysis 57(4), 567-577. doi:10.1111/gean.70009

Folium version 0.20.0, Copyright 2013-2025, Rob Story.

Aric A. Hagberg, Daniel A. Schult and Pieter J. Swart, "Exploring network structure, dynamics, and function using NetworkX," in Proceedings of the 7th Python in Science Conference (SciPy2008), Gael Varoquaux, Travis Vaught, and Jarrod Millman (Eds), (Pasadena, CA USA), pp. 11-15, Aug 2008.

Street and lighting data, OpenStreetMap contributors, available under the Open Database License (ODbL).

 J. D. Hunter, "Matplotlib: A 2D Graphics Environment", Computing in Science & Engineering, vol. 9, no. 3, pp. 90-95, 2007.