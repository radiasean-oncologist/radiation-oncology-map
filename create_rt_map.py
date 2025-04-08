import pandas as pd
import folium
from folium import Element

# ============================================================================
# Editable Section: Change these if needed.
# ============================================================================
excel_file = "2025 PROS RT Facility Directory Coordinates.xlsx"
sheet_name = "Coordinates"  # Update if your sheet name is different

# ============================================================================
# Load the data from the Excel file.
# ============================================================================
df = pd.read_excel(excel_file, sheet_name=sheet_name)

# ============================================================================
# Create a base map centered on the Philippines.
# ============================================================================
philippines_center = [12.8797, 121.7740]
m = folium.Map(location=philippines_center, zoom_start=5, tiles="CartoDB positron")

# ============================================================================
# Create three separate feature groups corresponding to each service category.
# We include HTML formatting in the names for color and font-size.
# ============================================================================
basic_layer = folium.FeatureGroup(
    name='<span style="color:blue; font-size:16px;">Basic RT (2D/3D CRT, IMRT, IGRT, VMAT, Electron Therapy)</span>'
)
advanced_layer = folium.FeatureGroup(
    name='<span style="color:red; font-size:16px;">Advanced Techniques (SRS, SBRT, TBI, IORT)</span>'
)
brachy_layer = folium.FeatureGroup(
    name='<span style="color:green; font-size:16px;">Brachytherapy (HDR & IGBT)</span>'
)

# ============================================================================
# Loop through each facility to extract coordinates and modality information.
# ============================================================================
for idx, row in df.iterrows():
    # Extract facility details
    facility = row['Facility']
    address = row['Address']
    
    # Parse the "Coordinates" column which is of the format "lat, lon"
    coord_str = str(row['Coordinates'])
    try:
        lat_str, lon_str = coord_str.split(',')
        lat = float(lat_str.strip())
        lon = float(lon_str.strip())
    except Exception as e:
        print(f"Error parsing coordinates for {facility}: {e}")
        continue

    # Determine modality offerings.
    offers_basic = (
        bool(row.get("2D3D", False)) or 
        bool(row.get("IMRT", False)) or 
        bool(row.get("IGRT", False)) or 
        bool(row.get("VMAT", False)) or 
        bool(row.get("Electron", False))
    )
    offers_advanced = (
        bool(row.get("SRS", False)) or 
        bool(row.get("SBRT", False)) or 
        bool(row.get("TBI", False)) or 
        bool(row.get("IORT", False))
    )
    offers_brachy = (
        bool(row.get("HDR", False)) or 
        bool(row.get("IGBT", False))
    )
    
    # Construct a popup message with facility details and offered services.
    popup_html = f"<b>{facility}</b><br>{address}<br>Services: "
    services = []
    if offers_basic:
        services.append("Basic RT")
    if offers_advanced:
        services.append("Advanced Techniques")
    if offers_brachy:
        services.append("Brachytherapy")
    popup_html += ", ".join(services)

    # Add markers to each applicable layer.
    if offers_basic:
        folium.Marker(
            location=[lat, lon],
            popup=popup_html,
            icon=folium.Icon(color="blue", icon="info-sign")
        ).add_to(basic_layer)

    if offers_advanced:
        folium.Marker(
            location=[lat, lon],
            popup=popup_html,
            icon=folium.Icon(color="red", icon="star")
        ).add_to(advanced_layer)

    if offers_brachy:
        folium.Marker(
            location=[lat, lon],
            popup=popup_html,
            icon=folium.Icon(color="green", icon="medkit")
        ).add_to(brachy_layer)

# ============================================================================
# Add all feature groups (layers) and include a layer control.
# ============================================================================
m.add_child(basic_layer)
m.add_child(advanced_layer)
m.add_child(brachy_layer)
m.add_child(folium.LayerControl(collapsed=False))

# ============================================================================
# Add custom CSS to increase the font size of the layer control labels.
# ============================================================================
css = """
<style>
.leaflet-control-layers-base label, 
.leaflet-control-layers-overlays label {
    font-size: 16px !important;
    font-weight: bold;
}
</style>
"""
css_element = Element(css)
m.get_root().html.add_child(css_element)

# ============================================================================
# Add a header to the map: "Radiation Oncology Facility in the Philippines as of 2025"
# ============================================================================
header_html = """
<div style="position: fixed; top: 10px; left: 50%; transform: translateX(-50%);
     z-index: 9999; background-color: white; padding: 10px; border: 2px solid #ccc;
     box-shadow: 2px 2px 6px rgba(0,0,0,0.3);">
    <h2 style="margin: 0; font-size: 24px;">Radiation Oncology Facility in the Philippines as of 2025</h2>
</div>
"""
header_element = Element(header_html)
m.get_root().html.add_child(header_element)

# ============================================================================
# Save the resulting map to an HTML file.
# ============================================================================
output_file = "philippines_rt_facilities_map.html"
m.save(output_file)
print(f"Map has been saved to {output_file}")
