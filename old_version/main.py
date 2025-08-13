import pandas as pd
import geopandas as gpd
import folium
from shapely import wkt
from folium.map import LayerControl
import itertools
import json

def calculate_overlaps_and_intersections(vendors_df):
    """Calculates which vendor radii overlap and computes the intersection geometry."""
    print("Calculating radius overlaps and intersection areas...")
    if vendors_df.empty: return set(), [], []
    gdf = gpd.GeoDataFrame(
        vendors_df, geometry=gpd.points_from_xy(vendors_df.longitude, vendors_df.latitude), crs="EPSG:4326"
    ).to_crs("EPSG:32639")
    gdf['geometry'] = gdf.geometry.buffer(3000)
    
    overlapping_vendors, overlap_pairs, intersection_geometries = set(), [], []
    vendor_list = list(gdf.itertuples())
    for vendor1, vendor2 in itertools.combinations(vendor_list, 2):
        if vendor1.geometry.intersects(vendor2.geometry):
            overlapping_vendors.update([vendor1.vendor_code, vendor2.vendor_code])
            overlap_pairs.append((vendor1.vendor_code, vendor2.vendor_code))
            intersection_geometries.append(vendor1.geometry.intersection(vendor2.geometry))
    print(f"Found {len(overlapping_vendors)} vendors with overlapping service areas.")
    return overlapping_vendors, overlap_pairs, intersection_geometries

def create_statistics_panel(vendors_count, overlapping_count, areas_count):
    """Creates a custom statistics panel HTML for the map."""
    overlap_rate = (overlapping_count / vendors_count * 100) if vendors_count > 0 else 0
    return f"""
    <div id="stats-container" style='position: fixed; top: 10px; left: 10px; z-index: 9999; font-family: Arial, sans-serif;'>
        <div style='width: 280px; background-color: rgba(255,255,255,0.95);
                    border: 2px solid #2c3e50; font-size: 13px; padding: 15px; border-radius: 10px;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.1);'>
            <h4 style='margin: 0 0 10px 0; text-align: center; color: #2c3e50;'>📊 Tehran Vendor Statistics</h4><hr style='margin:10px 0;'>
            <p style='margin: 8px 0;'><strong>🏪 Total Vendors:</strong> <span id="total-vendors" style='float:right; color: #3498db; font-weight:bold;'>{vendors_count}</span></p>
            <p style='margin: 8px 0;'><strong>⚠️ Overlapping:</strong> <span id="overlapping-vendors" style='float:right; color: #e74c3c; font-weight:bold;'>{overlapping_count}</span></p>
            <p style='margin: 8px 0;'><strong>🏢 Marketing Areas:</strong> <span style='float:right; color: #27ae60; font-weight:bold;'>{areas_count}</span></p>
            <p style='margin: 8px 0;'><strong>📈 Overlap Rate:</strong> <span id="overlap-rate" style='float:right; color: #f39c12; font-weight:bold;'>{overlap_rate:.1f}%</span></p>
            <p style='margin: 8px 0;'><strong>📏 Service Radius:</strong> <span style='float:right; color: #9b59b6; font-weight:bold;'>3km</span></p>
        </div>
    </div>
    """

def format_dataframe_for_display(df):
    """Formats the DataFrame for better display in the table."""
    display_df = df.copy()
    
    # Format numeric columns to 2 decimal places
    if 'avg_daily_orders' in display_df.columns:
        display_df['avg_daily_orders'] = display_df['avg_daily_orders'].apply(
            lambda x: f"{x:.2f}" if pd.notna(x) else ""
        )
    
    # Convert ratio to percentage with 2 decimal places
    if 'organic_to_non_organic_ratio' in display_df.columns:
        display_df['organic_to_non_organic_ratio'] = display_df['organic_to_non_organic_ratio'].apply(
            lambda x: f"{x*100:.2f}%" if pd.notna(x) else ""
        )
    
    # Format integer columns with commas
    int_columns = ['total_order_count', 'organic_order_count', 'non_organic_order_count']
    for col in int_columns:
        if col in display_df.columns:
            display_df[col] = display_df[col].apply(
                lambda x: f"{int(x):,}" if pd.notna(x) else ""
            )
    
    return display_df

def create_vendor_filter_html(vendors_df):
    """Creates HTML for vendor filtering interface."""
    vendor_options = []
    for _, vendor in vendors_df.iterrows():
        vendor_options.append(f'<option value="{vendor["vendor_code"]}">{vendor["vendor_name"]} ({vendor["vendor_code"]})</option>')
    
    return f"""
    <!-- Vendor Filter Panel -->
    <div id="filter-panel" style='position: fixed; top: 290px; left: 10px; z-index: 9999; font-family: Arial, sans-serif;'>
        <div style='width: 280px; background-color: rgba(255,255,255,0.95);
                    border: 2px solid #2c3e50; font-size: 12px; padding: 15px; border-radius: 10px;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.1);'>
            <h4 style='margin: 0 0 10px 0; text-align: center; color: #2c3e50;'>🔍 Vendor Filter</h4>
            <hr style='margin:10px 0;'>
            
            <label style='display: block; margin-bottom: 5px; font-weight: bold;'>Select vendors to hide:</label>
            <select id="vendor-filter" multiple style='width: 100%; height: 120px; margin-bottom: 10px;'>
                {''.join(vendor_options)}
            </select>
            
            <div style='text-align: center;'>
                <button id="apply-filter-btn" style='
                    padding: 8px 16px; margin-right: 5px;
                    background-color: #e74c3c; color: white; border: none;
                    border-radius: 5px; cursor: pointer; font-size: 11px;
                '>Hide Selected</button>
                
                <button id="clear-filter-btn" style='
                    padding: 8px 16px;
                    background-color: #27ae60; color: white; border: none;
                    border-radius: 5px; cursor: pointer; font-size: 11px;
                '>Show All</button>
            </div>
            
            <div id="filter-status" style='margin-top: 10px; text-align: center; font-size: 11px; color: #7f8c8d;'>
                All vendors visible
            </div>
        </div>
    </div>
    """

def create_table_modal_html(df):
    """
    Generates the HTML, CSS, and JS for a sortable, closable data table modal.
    Args:
        df (pd.DataFrame): The DataFrame to display in the table.
    Returns:
        str: The complete HTML/CSS/JS block to be injected into the map.
    """
    # Format the DataFrame for display
    display_df = format_dataframe_for_display(df)
    
    # Convert DataFrame to an HTML table with a specific ID and class for styling/scripting
    table_html = display_df.to_html(
        table_id="vendor-table",
        classes="data-table-style",
        index=False,
        justify="center"
    )

    modal_full_html = f"""
    <!-- Button to trigger the modal -->
    <div style='position: fixed; top: 245px; left: 10px; z-index: 9999;'>
         <button id="show-table-btn" style='
            width: 280px;
            padding: 10px;
            font-size: 14px;
            font-weight: bold;
            color: white;
            background-color: #3498db;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            box-shadow: 0 2px 5px rgba(0,0,0,0.2);
            transition: background-color 0.3s;
         '>📋 Show Data Table</button>
    </div>

    <!-- The Modal -->
    <div id="table-modal-overlay" class="modal-overlay">
        <div class="modal-content">
            <span class="modal-close">×</span>
            <h4 style="text-align: center; margin-top: 0;">Vendor Order Information</h4>
            <div class="table-container">
                {table_html}
            </div>
        </div>
    </div>

    <style>
        .modal-overlay {{
            display: none;
            position: fixed;
            z-index: 100000;
            left: 0; top: 0;
            width: 100%; height: 100%;
            overflow: auto;
            background-color: rgba(0,0,0,0.5);
            justify-content: center;
            align-items: center;
        }}
        .modal-content {{
            background-color: #fefefe;
            margin: auto;
            padding: 25px;
            border: 1px solid #888;
            border-radius: 10px;
            width: 90%;
            max-width: 1200px;
            max-height: 80vh;
            display: flex;
            flex-direction: column;
            position: relative;
        }}
        .table-container {{
            overflow-y: auto;
            flex-grow: 1;
        }}
        .modal-close {{
            color: #aaa;
            position: absolute;
            top: 10px;
            right: 20px;
            font-size: 28px;
            font-weight: bold;
            cursor: pointer;
        }}
        .modal-close:hover, .modal-close:focus {{
            color: black;
        }}
        #show-table-btn:hover {{
            background-color: #2980b9;
        }}
        .data-table-style {{
            width: 100%;
            border-collapse: collapse;
            font-size: 12px;
        }}
        .data-table-style th, .data-table-style td {{
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }}
        .data-table-style th {{
            background-color: #f2f2f2;
            cursor: pointer;
            -webkit-user-select: none;
            -moz-user-select: none;
            -ms-user-select: none;
            user-select: none;
        }}
        .data-table-style th:hover {{
            background-color: #e0e0e0;
        }}
        .data-table-style tr:nth-child(even) {{
            background-color: #f9f9f9;
        }}
    </style>

    <script>
        document.addEventListener('DOMContentLoaded', function() {{
            // Modal functionality
            var modal = document.getElementById("table-modal-overlay");
            var btn = document.getElementById("show-table-btn");
            var span = document.getElementsByClassName("modal-close")[0];

            btn.onclick = function() {{
                modal.style.display = "flex";
            }}
            span.onclick = function() {{
                modal.style.display = "none";
            }}
            window.onclick = function(event) {{
                if (event.target == modal) {{
                    modal.style.display = "none";
                }}
            }}

            // Table sorting functionality
            const getCellValue = (tr, idx) => tr.children[idx].innerText || tr.children[idx].textContent;
            const comparer = (idx, asc) => (a, b) => ((v1, v2) =>
                v1 !== '' && v2 !== '' && !isNaN(v1) && !isNaN(v2) ? v1 - v2 : v1.toString().localeCompare(v2)
                )(getCellValue(asc ? a : b, idx), getCellValue(asc ? b : a, idx));

            document.querySelectorAll('#vendor-table th').forEach(th => th.addEventListener('click', (() => {{
                const table = th.closest('table');
                Array.from(table.querySelectorAll('tr:nth-child(n+2)'))
                    .sort(comparer(Array.from(th.parentNode.children).indexOf(th), this.asc = !this.asc))
                    .forEach(tr => table.appendChild(tr));
            }})));
        }});
    </script>
    """
    return modal_full_html

def create_filtering_javascript(vendors_data, poly_gdf_data):
    """Creates JavaScript code for dynamic vendor filtering and map updates."""
    
    # Prepare vendor data for JavaScript
    vendors_js_data = []
    for _, vendor in vendors_data.iterrows():
        vendor_dict = {
            'vendor_code': vendor['vendor_code'],
            'vendor_name': str(vendor['vendor_name']),
            'latitude': float(vendor['latitude']),
            'longitude': float(vendor['longitude']),
            'total_order_count': int(vendor.get('total_order_count', 0)) if pd.notna(vendor.get('total_order_count', 0)) else 0,
            'organic_order_count': int(vendor.get('organic_order_count', 0)) if pd.notna(vendor.get('organic_order_count', 0)) else 0,
            'non_organic_order_count': int(vendor.get('non_organic_order_count', 0)) if pd.notna(vendor.get('non_organic_order_count', 0)) else 0,
            'organic_to_non_organic_ratio': float(vendor.get('organic_to_non_organic_ratio', 0)) if pd.notna(vendor.get('organic_to_non_organic_ratio', 0)) else 0,
            'avg_daily_orders': float(vendor.get('avg_daily_orders', 0)) if pd.notna(vendor.get('avg_daily_orders', 0)) else 0
        }
        vendors_js_data.append(vendor_dict)
    
    return f"""
    <script>
        // Store original vendor data and layer references
        window.originalVendorData = {json.dumps(vendors_js_data)};
        window.hiddenVendors = new Set();
        window.vendorLayers = {{}};
        window.overlapLayers = {{}};
        
        // Ranking criteria configuration
        const rankingCriteria = {{
            "Total Orders": "total_order_count",
            "Organic Orders": "organic_order_count", 
            "Non-Organic Orders": "non_organic_order_count",
            "Organic/Non-Organic Ratio": "organic_to_non_organic_ratio",
            "Avg Daily Orders": "avg_daily_orders"
        }};
        
        const rankColors = {{
            "Total Orders": "#6A0DAD",
            "Organic Orders": "#228B22",
            "Non-Organic Orders": "#FF8C00", 
            "Organic/Non-Organic Ratio": "#808080",
            "Avg Daily Orders": "#4682B4"
        }};

        // Calculate overlaps for given vendor data
        function calculateOverlaps(vendorData) {{
            const overlappingVendors = new Set();
            const overlapPairs = [];
            
            for (let i = 0; i < vendorData.length; i++) {{
                for (let j = i + 1; j < vendorData.length; j++) {{
                    const vendor1 = vendorData[i];
                    const vendor2 = vendorData[j];
                    
                    // Calculate distance in meters (approximate)
                    const R = 6371000; // Earth's radius in meters
                    const lat1Rad = vendor1.latitude * Math.PI / 180;
                    const lat2Rad = vendor2.latitude * Math.PI / 180;
                    const deltaLatRad = (vendor2.latitude - vendor1.latitude) * Math.PI / 180;
                    const deltaLngRad = (vendor2.longitude - vendor1.longitude) * Math.PI / 180;
                    
                    const a = Math.sin(deltaLatRad/2) * Math.sin(deltaLatRad/2) +
                            Math.cos(lat1Rad) * Math.cos(lat2Rad) *
                            Math.sin(deltaLngRad/2) * Math.sin(deltaLngRad/2);
                    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
                    const distance = R * c;
                    
                    // If distance is less than 6000m (2 * 3000m radius), they overlap
                    if (distance < 6000) {{
                        overlappingVendors.add(vendor1.vendor_code);
                        overlappingVendors.add(vendor2.vendor_code);
                        overlapPairs.push([vendor1.vendor_code, vendor2.vendor_code]);
                    }}
                }}
            }}
            
            return {{ overlappingVendors, overlapPairs }};
        }}

        // Update statistics panel
        function updateStatistics(vendorData, overlappingVendors) {{
            const totalVendors = vendorData.length;
            const overlappingCount = overlappingVendors.size;
            const overlapRate = totalVendors > 0 ? (overlappingCount / totalVendors * 100) : 0;
            
            document.getElementById('total-vendors').textContent = totalVendors;
            document.getElementById('overlapping-vendors').textContent = overlappingCount;
            document.getElementById('overlap-rate').textContent = overlapRate.toFixed(1) + '%';
        }}

        // Update filter status
        function updateFilterStatus() {{
            const statusElement = document.getElementById('filter-status');
            if (window.hiddenVendors.size === 0) {{
                statusElement.textContent = 'All vendors visible';
                statusElement.style.color = '#27ae60';
            }} else {{
                statusElement.textContent = `${{window.hiddenVendors.size}} vendors hidden`;
                statusElement.style.color = '#e74c3c';
            }}
        }}

        // Find and store layer control reference
        function findLayerControl() {{
            if (!window.layerControlRef) {{
                // Look for layer control in the map
                window.map.eachLayer(function(layer) {{
                    if (layer._container && layer._container.className && 
                        layer._container.className.includes('leaflet-control-layers')) {{
                        window.layerControlRef = layer;
                    }}
                }});
                
                // Alternative: look in controls
                if (!window.layerControlRef && window.map._controlContainer) {{
                    const controls = window.map._controlContainer.querySelectorAll('.leaflet-control-layers');
                    if (controls.length > 0) {{
                        // Find the actual layer control object
                        for (let control in window.map._controls) {{
                            if (window.map._controls[control]._container === controls[0]) {{
                                window.layerControlRef = window.map._controls[control];
                                break;
                            }}
                        }}
                    }}
                }}
            }}
            return window.layerControlRef;
        }}

        // Recreate map layers with filtered data
        function updateMapLayers() {{
            console.log('Updating map layers...');
            
            // Get filtered vendor data
            const visibleVendors = window.originalVendorData.filter(v => !window.hiddenVendors.has(v.vendor_code));
            
            // Calculate overlaps for visible vendors
            const {{ overlappingVendors, overlapPairs }} = calculateOverlaps(visibleVendors);
            
            // Update statistics
            updateStatistics(visibleVendors, overlappingVendors);
            
            // Remove existing vendor and overlap layers
            Object.values(window.vendorLayers).forEach(layerGroup => {{
                if (layerGroup && window.map.hasLayer(layerGroup)) {{
                    window.map.removeLayer(layerGroup);
                }}
            }});
            Object.values(window.overlapLayers).forEach(layerGroup => {{
                if (layerGroup && window.map.hasLayer(layerGroup)) {{
                    window.map.removeLayer(layerGroup);
                }}
            }});
            
            // Clear layer references
            window.vendorLayers = {{}};
            window.overlapLayers = {{}};
            
            // Find layer control
            const layerControl = findLayerControl();
            
            // Remove old layers from layer control if it exists
            if (layerControl && layerControl._layers) {{
                const layersToRemove = [];
                for (let layerId in layerControl._layers) {{
                    const layerObj = layerControl._layers[layerId];
                    if (layerObj.name && (layerObj.name.startsWith('📊') || 
                        layerObj.name.includes('Overlap'))) {{
                        layersToRemove.push(layerObj.layer);
                    }}
                }}
                layersToRemove.forEach(layer => {{
                    try {{
                        layerControl.removeLayer(layer);
                    }} catch(e) {{
                        console.warn('Could not remove layer from control:', e);
                    }}
                }});
            }}
            
            // Recreate ranking layers
            let isFirst = true;
            Object.entries(rankingCriteria).forEach(([rankName, rankColumn]) => {{
                // Sort vendors by ranking criteria
                const rankedVendors = [...visibleVendors].sort((a, b) => (b[rankColumn] || 0) - (a[rankColumn] || 0));
                
                // Create feature group
                const featureGroup = L.featureGroup();
                const baseColor = rankColors[rankName];
                
                rankedVendors.forEach((vendor, index) => {{
                    const rank = index + 1;
                    const location = [vendor.latitude, vendor.longitude];
                    
                    // Create popup content
                    let popupContent = `
                        <div style='font-family: Arial; min-width: 250px;'>
                            <h4 style='margin: 0; color: ${{baseColor}};'>#${{rank}} - ${{vendor.vendor_name}}</h4>
                            <hr style='margin: 5px 0;'>
                            <table style='width: 100%; font-size: 12px;'>
                                <tr><td><b>Vendor Code:</b></td><td>${{vendor.vendor_code}}</td></tr>
                    `;
                    
                    // Add metrics
                    Object.entries(rankingCriteria).forEach(([metricName, metricCol]) => {{
                        const value = vendor[metricCol];
                        if (value !== undefined && value !== null) {{
                            let displayVal;
                            if (metricCol === 'organic_to_non_organic_ratio') {{
                                displayVal = (value * 100).toFixed(2) + '%';
                            }} else if (metricCol === 'avg_daily_orders') {{
                                displayVal = value.toFixed(2);
                            }} else {{
                                displayVal = Math.round(value).toLocaleString();
                            }}
                            popupContent += `<tr><td><b>${{metricName}}:</b></td><td>${{displayVal}}</td></tr>`;
                        }}
                    }});
                    
                    popupContent += `
                                <tr><td><b>Status:</b></td><td>${{overlappingVendors.has(vendor.vendor_code) ? '⚠️ OVERLAPPING' : '✅ No Overlap'}}</td></tr>
                            </table>
                        </div>
                    `;
                    
                    // Add circle
                    L.circle(location, {{
                        radius: 3000,
                        color: baseColor,
                        weight: 2,
                        fill: true,
                        fillColor: baseColor,
                        fillOpacity: 0.1
                    }}).bindPopup(popupContent)
                      .bindTooltip(`#${{rank}} ${{vendor.vendor_name}} (3km radius)`)
                      .addTo(featureGroup);
                    
                    // Add marker
                    const markerHtml = `<div style="font-size:10pt;font-weight:bold;color:white;background-color:${{baseColor}};width:30px;height:30px;text-align:center;line-height:30px;border-radius:50%;border:2px solid white;box-shadow: 0 2px 5px rgba(0,0,0,0.3);">${{rank}}</div>`;
                    
                    L.marker(location, {{
                        icon: L.divIcon({{
                            iconSize: [30, 30],
                            iconAnchor: [15, 15],
                            html: markerHtml
                        }})
                    }}).bindPopup(popupContent)
                      .bindTooltip(`#${{rank}} ${{vendor.vendor_name}}`)
                      .addTo(featureGroup);
                }});
                
                // Store layer reference
                window.vendorLayers[rankName] = featureGroup;
                
                // Add to layer control if available
                if (layerControl) {{
                    try {{
                        layerControl.addOverlay(featureGroup, `📊 ${{rankName}}`);
                    }} catch(e) {{
                        console.warn('Could not add layer to control:', e);
                    }}
                }}
                
                // Show first layer by default
                if (isFirst) {{
                    featureGroup.addTo(window.map);
                    isFirst = false;
                }}
            }});
            
            // Add overlap connections layer
            if (overlapPairs.length > 0) {{
                const connectionsGroup = L.featureGroup();
                
                overlapPairs.forEach(([v1Code, v2Code]) => {{
                    const v1 = visibleVendors.find(v => v.vendor_code === v1Code);
                    const v2 = visibleVendors.find(v => v.vendor_code === v2Code);
                    
                    if (v1 && v2) {{
                        const popupHtml = `
                            <div style='font-family: Arial;'>
                                <b>Overlap between:</b><br>• ${{v1.vendor_name}}<br>• ${{v2.vendor_name}}
                            </div>
                        `;
                        
                        L.polyline([[v1.latitude, v1.longitude], [v2.latitude, v2.longitude]], {{
                            color: 'orange',
                            weight: 2,
                            opacity: 0.7
                        }}).bindPopup(popupHtml).addTo(connectionsGroup);
                    }}
                }});
                
                window.overlapLayers['connections'] = connectionsGroup;
                
                if (layerControl) {{
                    try {{
                        layerControl.addOverlay(connectionsGroup, '🔗 Overlap Connections');
                    }} catch(e) {{
                        console.warn('Could not add connections layer to control:', e);
                    }}
                }}
            }}
            
            updateFilterStatus();
            console.log('Map layers updated successfully');
        }}

        // Initialize filtering functionality
        document.addEventListener('DOMContentLoaded', function() {{
            // Store map reference with retry mechanism
            function initializeMap() {{
                const mapKeys = Object.keys(window).filter(key => key.startsWith('map_'));
                if (mapKeys.length > 0) {{
                    window.map = window[mapKeys[0]];
                    console.log('Map found and initialized');
                    
                    // Wait a bit more for layer control to be ready
                    setTimeout(() => {{
                        findLayerControl();
                        console.log('Layer control initialized');
                    }}, 500);
                }} else {{
                    setTimeout(initializeMap, 500);
                }}
            }}
            
            setTimeout(initializeMap, 1000);
            
            // Apply filter button
            document.getElementById('apply-filter-btn').addEventListener('click', function() {{
                const select = document.getElementById('vendor-filter');
                const selectedOptions = Array.from(select.selectedOptions);
                
                selectedOptions.forEach(option => {{
                    window.hiddenVendors.add(option.value);
                }});
                
                updateMapLayers();
                
                // Clear selection
                select.selectedIndex = -1;
            }});
            
            // Clear filter button  
            document.getElementById('clear-filter-btn').addEventListener('click', function() {{
                window.hiddenVendors.clear();
                updateMapLayers();
                
                // Clear selection
                document.getElementById('vendor-filter').selectedIndex = -1;
            }});
        }});
    </script>
    """

def create_vendor_map(order_file, geo_file, polygon_file, output_html='tehran_vendor_map.html'):
    """Creates an interactive map of Tehran vendors."""
    try:
        order_df = pd.read_excel(order_file)
        geo_df = pd.read_excel(geo_file)
        poly_df = pd.read_csv(polygon_file)
    except FileNotFoundError as e:
        print(f"❌ Error: {e}"); return

    geo_df = geo_df.drop_duplicates(subset=['vendor_code'], keep='first')
    vendors_df = pd.merge(order_df, geo_df, on='vendor_code', how='inner', suffixes=('_order', '_geo'))
    if 'vendor_name_order' in vendors_df.columns:
        vendors_df['vendor_name'] = vendors_df['vendor_name_order'].fillna(vendors_df['vendor_name_geo'])
        vendors_df.drop(columns=['vendor_name_order', 'vendor_name_geo'], inplace=True)

    vendors_df = vendors_df.dropna(subset=['latitude', 'longitude', 'vendor_name'])
    vendors_df = vendors_df[vendors_df['latitude'].between(35.0, 36.0) & (vendors_df['longitude'].between(50.5, 52.0))]
    
    if vendors_df.empty: print("❌ No valid vendor data after cleaning!"); return

    overlapping_vendor_codes, overlap_pairs, intersection_geometries = calculate_overlaps_and_intersections(vendors_df)

    poly_gdf = gpd.GeoDataFrame()
    if 'WKT' in poly_df.columns:
        poly_df['geometry'] = poly_df['WKT'].apply(wkt.loads)
        poly_gdf = gpd.GeoDataFrame(poly_df, geometry='geometry', crs="EPSG:4326")

    m = folium.Map(location=[35.6892, 51.3890], zoom_start=11, tiles="OpenStreetMap", prefer_canvas=True)
    
    if not poly_gdf.empty:
        marketing_areas = folium.FeatureGroup(name='🏢 Marketing Areas')
        folium.GeoJson(poly_gdf,
                       style_function=lambda x: {'fillColor': '#3186cc', 'color': '#2c3e50', 'weight': 1.5, 'fillOpacity': 0.2},
                       tooltip=folium.GeoJsonTooltip(fields=['name'] if 'name' in poly_gdf.columns else [])
        ).add_to(marketing_areas)
        marketing_areas.add_to(m)

    print("Creating vendor ranking layers...")
    ranking_criteria = {
        "Total Orders": "total_order_count", "Organic Orders": "organic_order_count",
        "Non-Organic Orders": "non_organic_order_count", "Organic/Non-Organic Ratio": "organic_to_non_organic_ratio",
        "Avg Daily Orders": "avg_daily_orders"
    }
    rank_colors = {
        "Total Orders": "#6A0DAD", "Organic Orders": "#228B22",
        "Non-Organic Orders": "#FF8C00", "Organic/Non-Organic Ratio": "#808080",
        "Avg Daily Orders": "#4682B4"
    }
    
    default_rank_key = list(ranking_criteria.keys())[0]
    
    for rank_name, rank_column in ranking_criteria.items():
        if rank_column not in vendors_df.columns: continue
        
        ranked_vendors = vendors_df.sort_values(by=rank_column, ascending=False, na_position='last').reset_index(drop=True)
        ranked_vendors['rank'] = ranked_vendors.index + 1
        
        feature_group = folium.FeatureGroup(name=f'📊 {rank_name}', show=(rank_name == default_rank_key))
        base_color = rank_colors.get(rank_name)
        
        for _, vendor in ranked_vendors.iterrows():
            location = [vendor['latitude'], vendor['longitude']]
            
            popup_content_html = f"""<div style='font-family: Arial; min-width: 250px;'>
                <h4 style='margin: 0; color: {base_color};'>#{vendor['rank']} - {vendor['vendor_name']}</h4><hr style='margin: 5px 0;'>
                <table style='width: 100%; font-size: 12px;'><tr><td><b>Vendor Code:</b></td><td>{vendor['vendor_code']}</td></tr>"""
            
            for metric_name, metric_col in ranking_criteria.items():
                if metric_col in vendor and pd.notna(vendor[metric_col]):
                    value = vendor[metric_col]
                    # Format display values consistently with table
                    if metric_col == 'organic_to_non_organic_ratio':
                        display_val = f'{value*100:.2f}%'
                    elif metric_col == 'avg_daily_orders':
                        display_val = f'{value:.2f}'
                    else:
                        display_val = f'{int(value):,}'
                    popup_content_html += f"<tr><td><b>{metric_name}:</b></td><td>{display_val}</td></tr>"

            popup_content_html += f"""<tr><td><b>Status:</b></td><td>{'⚠️ OVERLAPPING' if vendor['vendor_code'] in overlapping_vendor_codes else '✅ No Overlap'}</td></tr></table></div>"""

            popup_circle = folium.Popup(folium.IFrame(popup_content_html, width=280, height=180), max_width=300)
            popup_marker = folium.Popup(folium.IFrame(popup_content_html, width=280, height=180), max_width=300)
            
            folium.Circle(location=location, radius=3000, color=base_color, weight=2, fill=True, fill_color=base_color, fill_opacity=0.1,
                popup=popup_circle, tooltip=folium.Tooltip(f"#{vendor['rank']} {vendor['vendor_name']} (3km radius)")
            ).add_to(feature_group)
            
            folium.Marker(location=location, popup=popup_marker, tooltip=folium.Tooltip(f"#{vendor['rank']} {vendor['vendor_name']}"),
                icon=folium.DivIcon(icon_size=(30,30), icon_anchor=(15,15),
                    html=f'<div style="font-size:10pt;font-weight:bold;color:white;background-color:{base_color};width:30px;height:30px;text-align:center;line-height:30px;border-radius:50%;border:2px solid white;box-shadow: 0 2px 5px rgba(0,0,0,0.3);">{vendor["rank"]}</div>'
                )
            ).add_to(feature_group)
        
        feature_group.add_to(m)

    if intersection_geometries:
        print("Creating precise overlap highlight layer...")
        overlap_group = folium.FeatureGroup(name="🔴 Highlight Overlapping Areas", show=False)
        intersections_gdf = gpd.GeoDataFrame(geometry=intersection_geometries, crs="EPSG:32639").to_crs("EPSG:4326")
        folium.GeoJson(intersections_gdf, style_function=lambda x: {'fillColor': 'red', 'color': 'none', 'weight': 0, 'fillOpacity': 0.5},
            tooltip="Overlapping Area"
        ).add_to(overlap_group)
        overlap_group.add_to(m)
    
    if overlap_pairs:
        connections_group = folium.FeatureGroup(name="🔗 Overlap Connections", show=False)
        for v1_code, v2_code in overlap_pairs:
            try:
                v1 = vendors_df[vendors_df['vendor_code'] == v1_code].iloc[0]
                v2 = vendors_df[vendors_df['vendor_code'] == v2_code].iloc[0]
                popup_html = f"<div style='font-family: Arial;'><b>Overlap between:</b><br>• {v1['vendor_name']}<br>• {v2['vendor_name']}</div>"
                folium.PolyLine(locations=[[v1['latitude'], v1['longitude']], [v2['latitude'], v2['longitude']]], color='orange', weight=2, opacity=0.7,
                    popup=folium.Popup(folium.IFrame(popup_html, width=270, height=80))
                ).add_to(connections_group)
            except IndexError: continue
        connections_group.add_to(m)

    # Add Panels, Controls, and Features
    m.get_root().html.add_child(folium.Element(create_statistics_panel(len(vendors_df), len(overlapping_vendor_codes), len(poly_gdf))))
    
    # Add the modal table
    modal_html = create_table_modal_html(order_df)
    m.get_root().html.add_child(folium.Element(modal_html))
    
    # Add vendor filter panel
    filter_html = create_vendor_filter_html(vendors_df)
    m.get_root().html.add_child(folium.Element(filter_html))
    
    # Add filtering JavaScript
    filtering_js = create_filtering_javascript(vendors_df, poly_gdf)
    m.get_root().html.add_child(folium.Element(filtering_js))
    
    folium.LayerControl(collapsed=False, position='topright').add_to(m)
    
    print(f"\n💾 Saving map to: {output_html}")
    m.save(output_html)
    print("="*60)
    print("🎉 MAP GENERATION COMPLETE! (v4 - Enhanced with Filtering)")
    print(f"🌐 Open '{output_html}' in your web browser.")
    print("📋 Features:")
    print("   • Data table with formatted decimals and percentages")
    print("   • Vendor filtering system with dynamic recalculation")
    print("   • Real-time statistics updates")
    print("   • Dynamic overlap detection after filtering")
    print("="*60)

if __name__ == '__main__':
    create_vendor_map('vendor_order_info.xlsx', 'vendor_geo_info.xlsx', 'tehran_polygons.csv')