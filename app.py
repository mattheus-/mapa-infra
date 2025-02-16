import dash
from dash import html, dcc, Input, Output, State, MATCH
import dash_leaflet as dl
import dash_bootstrap_components as dbc
import geopandas as gpd
import json
import zipfile
import os
from dash_extensions.javascript import assign  # to wrap JS functions

# ---------------------------
# Process all zipped shapefiles from the "base" folder
# ---------------------------
base_folder = "base"  # Folder containing zipped shapefiles
data_folder = "data"  # Folder where each zip will be extracted

# Dictionaries to hold GeoJSON data and point-type flag for each shapefile
geojson_layers = {}
layer_is_point = {}  # True if the layer contains Point/MultiPoint features

# Ensure the data folder exists
if not os.path.exists(data_folder):
    os.makedirs(data_folder)

# Iterate over all zip files in the base folder
for file in os.listdir(base_folder):
    if file.endswith(".zip"):
        zip_path = os.path.join(base_folder, file)
        # Define a unique extraction folder for this zip file
        folder_name = os.path.splitext(file)[0]
        extract_path = os.path.join(data_folder, folder_name)
        if not os.path.exists(extract_path):
            os.makedirs(extract_path)
        # Extract the zip file
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(extract_path)
        # Locate the first .shp file in the extracted folder
        shapefile_path = None
        for root, dirs, files_in_dir in os.walk(extract_path):
            for f in files_in_dir:
                if f.endswith(".shp"):
                    shapefile_path = os.path.join(root, f)
                    break
            if shapefile_path:
                break
        if shapefile_path:
            gdf = gpd.read_file(shapefile_path, encoding="latin1")
            # Convert to EPSG:4326 (WGS84) if necessary
            if gdf.crs != "EPSG:4326":
                gdf = gdf.to_crs(epsg=4326)
            geojson_data = json.loads(gdf.to_json(default=str))
            layer_name = folder_name  # Use the folder name as the layer name
            geojson_layers[layer_name] = geojson_data
            # Determine if the layer is a point layer based on its first feature (if any)
            if geojson_data.get("features") and len(geojson_data["features"]) > 0:
                geom_type = geojson_data["features"][0]["geometry"]["type"]
                layer_is_point[layer_name] = geom_type in ["Point", "MultiPoint"]
            else:
                layer_is_point[layer_name] = False
            print(
                f"Loaded {layer_name} with {len(geojson_data.get('features', []))} features. Point layer: {layer_is_point[layer_name]}"
            )
        else:
            print(f"No shapefile found in {file}.")
            geojson_layers[folder_name] = {"type": "FeatureCollection", "features": []}
            layer_is_point[folder_name] = False

# ---------------------------
# Map defaults (centered on Brazil)
# ---------------------------
brazil_center = [-18, -55]
brazil_zoom = 5

# ---------------------------
# Define the onEachFeature JavaScript function using assign
# (This function binds a tooltip that lists all properties.)
# ---------------------------
on_each_feature = assign(
    """
    function(feature, layer) {
        var tooltipContent = "";
        for (var key in feature.properties) {
            tooltipContent += key + ": " + feature.properties[key] + "<br/>";
        }
        // Create a custom pane for tooltips if it doesn't exist
        if (layer._map) {
            if (!layer._map.getPane('tooltipPane')) {
                layer._map.createPane('tooltipPane');
                layer._map.getPane('tooltipPane').style.zIndex = 650;
            }
        }
        layer.bindTooltip(tooltipContent, {pane: 'tooltipPane'});
    }
    """
)

# ---------------------------
# Assign a different color to each layer
# ---------------------------
# Use only valid colors available in the Leaflet Color Markers repository.
color_list = [
    "black",
    "blue",
    "grey",
    "green",
    "orange",
    "red",
]
layer_colors = {}
for idx, layer_name in enumerate(geojson_layers.keys()):
    layer_colors[layer_name] = color_list[idx % len(color_list)]

# ---------------------------
# Build per-layer options for dl.GeoJSON components
# ---------------------------
layer_options = {}  # Options for the GeoJSON's "options" property.
layer_hover = {}  # Hover style for each layer.
for layer_name in geojson_layers.keys():
    if layer_is_point[layer_name]:
        # For point layers, define a custom pointToLayer function that uses a colored marker icon.
        js_func = f"""
        function(feature, latlng) {{
            var iconUrl = "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-{layer_colors[layer_name]}.png";
            var markerIcon = L.icon({{
                iconUrl: iconUrl,
                shadowUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png",
                iconSize: [25, 41],
                iconAnchor: [12, 41],
                popupAnchor: [1, -34],
                shadowSize: [41, 41]
            }});
            return L.marker(latlng, {{icon: markerIcon}});
        }}
        """
        point_to_layer = assign(js_func)
        layer_options[layer_name] = dict(
            onEachFeature=on_each_feature, pointToLayer=point_to_layer
        )
        # Do not set hoverStyle for markers (as markers do not support setStyle)
        layer_hover[layer_name] = None
    else:
        # For polygon/line layers, set the style (stroke and fill colors).
        layer_options[layer_name] = dict(
            onEachFeature=on_each_feature,
            style=dict(
                color=layer_colors[layer_name],
                weight=2,
                fillOpacity=0.5,
                fillColor=layer_colors[layer_name],
            ),
        )
        layer_hover[layer_name] = dict(
            weight=3, color=layer_colors[layer_name], dashArray=""
        )

# ---------------------------
# Initialize the Dash app and layout
# ---------------------------
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    meta_tags=[
        {
            "name": "norton-safeweb-site-verification",
            "content": "TCC1BNVWZ7PH-JMUXHYCFW3TCB1D4Q09JFL3VC2ZKEMNTM5S045K9FE5C9Q7PC8MCRXZXJCOPRGI0OH7K7Q1MCN134X8WQOGW6D5TZKV2UB-Q6NJDQ4XGZ5OVBBQPYRR",
        }
    ],
)

# Sort the layer selector options alphabetically
dropdown_options = [
    {"label": name, "value": name} for name in sorted(geojson_layers.keys())
]
initial_selection = []  # No layer is active by default

layer_selector = html.Div(
    [
        dcc.Dropdown(
            id="toggle-shapefile",
            options=dropdown_options,
            value=initial_selection,
            multi=True,
            placeholder="Selecione uma ou mais camadas",
        ),
    ],
    className="mb-3",
)

app.layout = html.Div(
    [
        html.H1("Mapa da Infraestrutura no Brasil", className="mb-4"),
        dbc.Container(
            [
                dbc.Row(
                    dbc.Col(layer_selector, width=6),
                    className="mb-4",
                ),
                dbc.Row(
                    dbc.Col(
                        html.Div(
                            dl.Map(
                                id="map",
                                center=brazil_center,
                                zoom=brazil_zoom,
                                children=[
                                    dl.TileLayer(),
                                    *[
                                        dl.GeoJSON(
                                            id={
                                                "type": "geojson-layer",
                                                "index": layer_name,
                                            },
                                            data={
                                                "type": "FeatureCollection",
                                                "features": [],
                                            },  # Initially empty; loaded via callback
                                            options=layer_options[layer_name],
                                            # Conditionally pass hoverStyle only for non-point layers.
                                            hoverStyle=(
                                                layer_hover[layer_name]
                                                if not layer_is_point[layer_name]
                                                else None
                                            ),
                                        )
                                        for layer_name in geojson_layers.keys()
                                    ],
                                ],
                                style={"width": "100%", "height": "100%"},
                            ),
                            style={
                                "width": "100%",
                                "height": "70vh",
                                "overflow": "visible",
                            },
                        ),
                        width=12,
                    )
                ),
            ],
            fluid=True,
        ),
    ],
    className="p-4",
)


# ---------------------------
# Callback to toggle each GeoJSON layer using pattern matching
# ---------------------------
@app.callback(
    Output({"type": "geojson-layer", "index": MATCH}, "data"),
    Input("toggle-shapefile", "value"),
    State({"type": "geojson-layer", "index": MATCH}, "id"),
)
def toggle_geojson(selected, id_data):
    layer_name = id_data["index"]
    if layer_name in selected:
        return geojson_layers[layer_name]
    else:
        return {"type": "FeatureCollection", "features": []}


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run_server(host="0.0.0.0", port=port, debug=False)
