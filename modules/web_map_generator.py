import folium
import geopandas as gpd
import pandas as pd
import json
import sys
from pathlib import Path

# Add config to path
sys.path.append(str(Path(__file__).parent.parent))
import config


class WebMapGenerator:
    """Web-based map generator for Flask application with real-time updates."""
    
    def __init__(self):
        self.ranking_criteria = config.RANKING_CRITERIA
        self.rank_colors = config.RANK_COLORS
    
    def get_map_data(self, data_processor):
        """Get map data for web application rendering."""
        try:
            print("🗺️  Generating map data for web application...")
            
            # Create base map
            m = self._create_base_map()
            
            # Add marketing areas if available
            if config.ENABLE_MARKETING_AREAS and not data_processor.poly_gdf.empty:
                self._add_marketing_areas(m, data_processor.poly_gdf)
            
            # Add vendor layers
            self._add_vendor_layers(m, data_processor)
            
            # Add overlap layers
            if config.ENABLE_OVERLAP_DETECTION:
                self._add_overlap_layers(m, data_processor)
            
            # Add layer control
            folium.LayerControl(collapsed=False, position='topright').add_to(m)
            
            # Get the map HTML
            map_html = m._repr_html_()
            
            return {
                'map_html': map_html,
                'center': config.MAP_CENTER,
                'zoom': config.MAP_ZOOM,
                'bounds': config.TEHRAN_BOUNDS,
                'service_radius': config.SERVICE_RADIUS
            }
            
        except Exception as e:
            print(f"❌ Error generating map data: {e}")
            return None
    
    def _create_base_map(self):
        """Create base map with multiple tile layers."""
        m = folium.Map(
            location=config.MAP_CENTER,
            zoom_start=config.MAP_ZOOM,
            tiles=None,
            prefer_canvas=True
        )
        
        # Add tile layers
        folium.TileLayer(
            tiles='OpenStreetMap',
            name='🗺️ Standard Map',
            control=True
        ).add_to(m)
        
        folium.TileLayer(
            tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
            attr='Esri',
            name='🛰️ Satellite',
            control=True
        ).add_to(m)
        
        folium.TileLayer(
            tiles='CartoDB dark_matter',
            name='🌙 Dark Theme',
            control=True
        ).add_to(m)
        
        return m
    
    def _add_marketing_areas(self, m, poly_gdf):
        """Add marketing area polygons to the map."""
        print("📐 Adding marketing areas...")
        
        marketing_areas = folium.FeatureGroup(name='🏢 Marketing Areas', show=True)
        
        folium.GeoJson(
            poly_gdf,
            style_function=lambda x: {
                'fillColor': '#3186cc',
                'color': '#1565c0',
                'weight': 2,
                'fillOpacity': 0.15,
                'dashArray': '5, 5'
            },
            highlight_function=lambda x: {
                'weight': 3,
                'fillOpacity': 0.3
            },
            tooltip=folium.GeoJsonTooltip(
                fields=['name'] if 'name' in poly_gdf.columns else [],
                aliases=['Area Name:'] if 'name' in poly_gdf.columns else []
            )
        ).add_to(marketing_areas)
        
        marketing_areas.add_to(m)
    
    def _add_vendor_layers(self, m, data_processor):
        """Add vendor ranking layers to the map."""
        print("📊 Creating vendor ranking layers...")
        
        vendors_df = data_processor.vendors_df
        overlapping_vendor_codes = data_processor.overlapping_vendor_codes
        
        default_rank_key = list(self.ranking_criteria.keys())[0]
        
        for rank_name, rank_column in self.ranking_criteria.items():
            if rank_column not in vendors_df.columns:
                continue
            
            # Sort vendors by ranking criteria
            ranked_vendors = vendors_df.sort_values(
                by=rank_column,
                ascending=False,
                na_position='last'
            ).reset_index(drop=True)
            ranked_vendors['rank'] = ranked_vendors.index + 1
            
            # Create feature group
            feature_group = folium.FeatureGroup(
                name=f'📊 {rank_name}',
                show=(rank_name == default_rank_key)
            )
            
            base_color = self.rank_colors.get(rank_name, '#666666')
            
            # Add vendors to layer
            for _, vendor in ranked_vendors.iterrows():
                self._add_vendor_to_layer(
                    feature_group, vendor, base_color, overlapping_vendor_codes
                )
            
            feature_group.add_to(m)
    
    def _add_vendor_to_layer(self, feature_group, vendor, base_color, overlapping_vendor_codes):
        """Add a single vendor to a feature group."""
        location = [vendor['latitude'], vendor['longitude']]
        is_overlapping = vendor['vendor_code'] in overlapping_vendor_codes
        
        # Create popup content
        popup_content = self._create_vendor_popup_content(vendor, base_color, is_overlapping)
        
        # Add circle (service radius)
        circle_style = {
            'radius': config.SERVICE_RADIUS,
            'color': base_color,
            'weight': 3 if is_overlapping else 2,
            'fill': True,
            'fillColor': base_color,
            'fillOpacity': 0.15 if is_overlapping else 0.1,
            'dashArray': '10, 5' if is_overlapping else None,
            'className': f'vendor-circle vendor-{vendor["vendor_code"]}'
        }
        
        circle = folium.Circle(
            location=location,
            popup=folium.Popup(popup_content, max_width=300),
            tooltip=folium.Tooltip(f"#{vendor['rank']} {vendor['vendor_name']} (3km radius)"),
            **circle_style
        )
        circle.add_to(feature_group)
        
        # Add marker
        marker_html = f"""
        <div class="vendor-marker" data-vendor-code="{vendor['vendor_code']}" 
             style="font-size: 11px; font-weight: bold; color: white; 
                    background: {base_color}; width: 32px; height: 32px; 
                    text-align: center; line-height: 32px; border-radius: 50%; 
                    border: 3px solid white; box-shadow: 0 3px 10px rgba(0,0,0,0.3);
                    transition: all 0.3s ease;">
            {vendor['rank']}
        </div>
        """
        
        marker = folium.Marker(
            location=location,
            popup=folium.Popup(popup_content, max_width=300),
            tooltip=folium.Tooltip(f"#{vendor['rank']} {vendor['vendor_name']}"),
            icon=folium.DivIcon(
                icon_size=(32, 32),
                icon_anchor=(16, 16),
                html=marker_html,
                class_name=f"vendor-marker-container vendor-{vendor['vendor_code']}"
            )
        )
        marker.add_to(feature_group)
    
    def _create_vendor_popup_content(self, vendor, base_color, is_overlapping):
        """Create popup content for vendor markers."""
        total_orders = vendor.get('total_order_count', 0)
        organic_orders = vendor.get('organic_order_count', 0)
        non_organic_orders = vendor.get('non_organic_order_count', 0)
        
        organic_pct = (organic_orders / total_orders * 100) if total_orders > 0 else 0
        non_organic_pct = (non_organic_orders / total_orders * 100) if total_orders > 0 else 0
        
        return f"""
        <div style='font-family: "Segoe UI", Arial, sans-serif; width: 280px; padding: 0;'>
            <div style='background: linear-gradient(135deg, {base_color} 0%, {base_color}CC 100%); 
                        color: white; padding: 12px; margin: -10px -10px 12px -10px; border-radius: 6px 6px 0 0;'>
                <h4 style='margin: 0; font-size: 14px; font-weight: 600;'>
                    #{vendor['rank']} - {vendor['vendor_name']}
                </h4>
                <div style='font-size: 11px; opacity: 0.9; margin-top: 2px;'>
                    {vendor['vendor_code']}
                </div>
            </div>
            
            <div style='margin-bottom: 12px;'>
                <span style='background: {"#ffebee" if is_overlapping else "#e8f5e8"}; 
                            color: {"#c62828" if is_overlapping else "#2e7d32"}; 
                            padding: 4px 8px; border-radius: 12px; font-size: 10px; font-weight: 600;'>
                    {"⚠️ OVERLAPPING" if is_overlapping else "✅ NO OVERLAP"}
                </span>
            </div>
            
            <div style='display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-bottom: 12px;'>
                <div style='text-align: center; padding: 6px; background: #f8f9fa; border-radius: 4px;'>
                    <div style='font-size: 16px; font-weight: bold; color: #333;'>{total_orders:,}</div>
                    <div style='font-size: 9px; color: #666;'>Total Orders</div>
                </div>
                <div style='text-align: center; padding: 6px; background: #f8f9fa; border-radius: 4px;'>
                    <div style='font-size: 16px; font-weight: bold; color: #333;'>{vendor.get("avg_daily_orders", 0):.1f}</div>
                    <div style='font-size: 9px; color: #666;'>Daily Avg</div>
                </div>
            </div>
            
            <div style='margin-bottom: 12px;'>
                <div style='font-size: 11px; font-weight: 600; color: #333; margin-bottom: 6px;'>
                    📊 Order Distribution
                </div>
                <div style='display: flex; height: 16px; border-radius: 8px; overflow: hidden; border: 1px solid #e0e0e0;'>
                    <div style='background: #4CAF50; width: {organic_pct}%;'></div>
                    <div style='background: #FF9800; width: {non_organic_pct}%;'></div>
                </div>
                <div style='display: flex; justify-content: space-between; margin-top: 4px; font-size: 9px;'>
                    <span style='color: #4CAF50;'>🟢 Organic: {organic_orders:,}</span>
                    <span style='color: #FF9800;'>🟠 Non-organic: {non_organic_orders:,}</span>
                </div>
            </div>
            
            <div style='font-size: 10px; color: #555; line-height: 1.3;'>
                <div>Ratio: {(vendor.get("organic_to_non_organic_ratio", 0) * 100):.1f}%</div>
                <div>Location: {vendor["latitude"]:.4f}, {vendor["longitude"]:.4f}</div>
            </div>
        </div>
        """
    
    def _add_overlap_layers(self, m, data_processor):
        """Add overlap visualization layers."""
        vendors_df = data_processor.vendors_df
        intersection_geometries = data_processor.intersection_geometries
        overlap_pairs = data_processor.overlap_pairs
        
        # Add overlap areas
        if intersection_geometries:
            print("🔴 Creating overlap highlight layer...")
            overlap_group = folium.FeatureGroup(name="🔴 Overlap Areas", show=False)
            
            intersections_gdf = gpd.GeoDataFrame(
                geometry=intersection_geometries,
                crs="EPSG:32639"
            ).to_crs("EPSG:4326")
            
            folium.GeoJson(
                intersections_gdf,
                style_function=lambda x: {
                    'fillColor': '#ff5722',
                    'color': '#d32f2f',
                    'weight': 2,
                    'fillOpacity': 0.6,
                    'dashArray': '5, 5'
                },
                tooltip="Overlapping Service Area"
            ).add_to(overlap_group)
            
            overlap_group.add_to(m)
        
        # Add connection lines
        if overlap_pairs:
            print("🔗 Creating overlap connections...")
            connections_group = folium.FeatureGroup(name="🔗 Overlap Connections", show=False)
            
            for v1_code, v2_code in overlap_pairs:
                try:
                    v1 = vendors_df[vendors_df['vendor_code'] == v1_code].iloc[0]
                    v2 = vendors_df[vendors_df['vendor_code'] == v2_code].iloc[0]
                    
                    popup_html = f"""
                    <div style='font-family: Arial; padding: 8px;'>
                        <h4 style='margin: 0 0 8px 0; color: #ff5722;'>⚠️ Service Area Overlap</h4>
                        <div><strong>Vendor 1:</strong> {v1['vendor_name']} ({v1_code})</div>
                        <div><strong>Vendor 2:</strong> {v2['vendor_name']} ({v2_code})</div>
                    </div>
                    """
                    
                    folium.PolyLine(
                        locations=[[v1['latitude'], v1['longitude']], [v2['latitude'], v2['longitude']]],
                        color='#ff5722',
                        weight=3,
                        opacity=0.7,
                        popup=folium.Popup(popup_html, max_width=250),
                        tooltip=f"Overlap: {v1['vendor_name']} ↔ {v2['vendor_name']}"
                    ).add_to(connections_group)
                    
                except IndexError:
                    continue
            
            connections_group.add_to(m)