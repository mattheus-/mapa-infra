window.dashExtensions = Object.assign({}, window.dashExtensions, {
    default: {
        function0: function(feature, layer) {
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
                layer.bindTooltip(tooltipContent, {
                    pane: 'tooltipPane'
                });
            }

            ,
        function1: function(feature, latlng) {
                var iconUrl = "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-black.png";
                var markerIcon = L.icon({
                    iconUrl: iconUrl,
                    shadowUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png",
                    iconSize: [25, 41],
                    iconAnchor: [12, 41],
                    popupAnchor: [1, -34],
                    shadowSize: [41, 41]
                });
                return L.marker(latlng, {
                    icon: markerIcon
                });
            }

            ,
        function2: function(feature, latlng) {
                var iconUrl = "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-grey.png";
                var markerIcon = L.icon({
                    iconUrl: iconUrl,
                    shadowUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png",
                    iconSize: [25, 41],
                    iconAnchor: [12, 41],
                    popupAnchor: [1, -34],
                    shadowSize: [41, 41]
                });
                return L.marker(latlng, {
                    icon: markerIcon
                });
            }

            ,
        function3: function(feature, latlng) {
                var iconUrl = "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-orange.png";
                var markerIcon = L.icon({
                    iconUrl: iconUrl,
                    shadowUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png",
                    iconSize: [25, 41],
                    iconAnchor: [12, 41],
                    popupAnchor: [1, -34],
                    shadowSize: [41, 41]
                });
                return L.marker(latlng, {
                    icon: markerIcon
                });
            }

            ,
        function4: function(feature, latlng) {
                var iconUrl = "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-blue.png";
                var markerIcon = L.icon({
                    iconUrl: iconUrl,
                    shadowUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png",
                    iconSize: [25, 41],
                    iconAnchor: [12, 41],
                    popupAnchor: [1, -34],
                    shadowSize: [41, 41]
                });
                return L.marker(latlng, {
                    icon: markerIcon
                });
            }

            ,
        function5: function(feature, latlng) {
                var iconUrl = "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-green.png";
                var markerIcon = L.icon({
                    iconUrl: iconUrl,
                    shadowUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png",
                    iconSize: [25, 41],
                    iconAnchor: [12, 41],
                    popupAnchor: [1, -34],
                    shadowSize: [41, 41]
                });
                return L.marker(latlng, {
                    icon: markerIcon
                });
            }

            ,
        function6: function(feature, latlng) {
            var iconUrl = "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-red.png";
            var markerIcon = L.icon({
                iconUrl: iconUrl,
                shadowUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png",
                iconSize: [25, 41],
                iconAnchor: [12, 41],
                popupAnchor: [1, -34],
                shadowSize: [41, 41]
            });
            return L.marker(latlng, {
                icon: markerIcon
            });
        }

    }
});