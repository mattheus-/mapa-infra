import dash
from dash import html, dcc, Input, Output
import dash_leaflet as dl
import geopandas as gpd
import json
import zipfile
import os
from dash_extensions.javascript import assign  # Import assign to wrap JS functions

# ---------------------------
# Extract and load the shapefile
# ---------------------------
zip_path = "rodovia-federal.zip"
extract_path = "data/shapefile"

with zipfile.ZipFile(zip_path, "r") as zip_ref:
    zip_ref.extractall(extract_path)

# Locate the .shp file (the DBF, PRJ, and SHX files are loaded automatically)
shapefile_path = None
for root, dirs, files in os.walk(extract_path):
    for file in files:
        if file.endswith(".shp"):
            shapefile_path = os.path.join(root, file)
            break

if shapefile_path:
    gdf = gpd.read_file(shapefile_path)
    # Ensure data is in EPSG:4326 (WGS84)
    if gdf.crs != "EPSG:4326":
        gdf = gdf.to_crs(epsg=4326)
    geojson_data = json.loads(gdf.to_json())
    print("Number of features loaded:", len(geojson_data.get("features", [])))
else:
    geojson_data = {"type": "FeatureCollection", "features": []}

# ---------------------------
# Map defaults (centered on Brazil)
# ---------------------------
brazil_center = [-18, -55]
brazil_zoom = 5

# ---------------------------
# Define the onEachFeature JavaScript function using assign
# ---------------------------
on_each_feature = assign(
    """
    function(feature, layer) {
        let tooltipContent = "";
        for (var key in feature.properties) {
            tooltipContent += key + ": " + feature.properties[key] + "<br/>";
        }
        layer.bindTooltip(tooltipContent);
    }
    """
)

# ---------------------------
# Initialize the Dash app and layout
# ---------------------------
app = dash.Dash(__name__)

app.layout = html.Div(
    [
        html.H1("Interactive Map with Shapefile Tooltips"),
        # Checklist to toggle the shapefile layer
        dcc.Checklist(
            id="toggle-shapefile",
            options=[{"label": "Show Shapefile Info", "value": "show"}],
            value=["show"],
        ),
        # Dash-Leaflet Map filling the full vertical viewport
        dl.Map(
            id="map",
            center=brazil_center,
            zoom=brazil_zoom,
            children=[
                dl.TileLayer(),  # Base layer
                dl.GeoJSON(
                    id="geojson-layer",
                    data=geojson_data,
                    options=dict(onEachFeature=on_each_feature),
                    hoverStyle=dict(weight=3, color="red", dashArray=""),
                ),
            ],
            style={"width": "100%", "height": "100vh"},
        ),
    ]
)


# ---------------------------
# Callback to toggle the GeoJSON layer without reloading the whole map
# ---------------------------
@app.callback(Output("geojson-layer", "data"), Input("toggle-shapefile", "value"))
def toggle_geojson(selected):
    if "show" in selected:
        return geojson_data
    else:
        # Return a valid empty GeoJSON FeatureCollection to clear the layer
        return {"type": "FeatureCollection", "features": []}


if __name__ == "__main__":
    app.run_server(debug=True)

