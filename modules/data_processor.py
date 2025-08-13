import pandas as pd
import geopandas as gpd
import itertools
import numpy as np
import time
from shapely import wkt
import sys
from pathlib import Path

# Add config to path
sys.path.append(str(Path(__file__).parent.parent))
import config


class DataProcessor:
    """Enhanced data processing for web application with real-time filtering capabilities."""
    
    def __init__(self):
        self.vendors_df = None
        self.poly_gdf = None
        self.original_vendors_df = None  # Keep original for filtering
        self.overlapping_vendor_codes = set()
        self.overlap_pairs = []
        self.intersection_geometries = []
        self.vendor_statistics = {}
        self.last_update_time = None
        
        # Performance tracking
        self.processing_times = {}
        
    def load_data(self, order_file, geo_file, polygon_file):
        """
        Load and process all data files with enhanced performance tracking.
        
        Args:
            order_file (str): Path to vendor order Excel file
            geo_file (str): Path to vendor geo Excel file  
            polygon_file (str): Path to polygon CSV file
        
        Returns:
            bool: True if data loaded successfully, False otherwise
        """
        start_time = time.time()
        
        try:
            # Load data files with progress tracking
            print("📊 Loading data files...")
            
            load_start = time.time()
            order_df = pd.read_excel(order_file)
            geo_df = pd.read_excel(geo_file)
            poly_df = pd.read_csv(polygon_file)
            self.processing_times['data_loading'] = time.time() - load_start
            
            print(f"   ✅ Order records: {len(order_df):,}")
            print(f"   ✅ Geographic records: {len(geo_df):,}")
            print(f"   ✅ Polygon records: {len(poly_df):,}")
            
        except FileNotFoundError as e:
            print(f"❌ Error loading files: {e}")
            return False
        except Exception as e:
            print(f"❌ Error processing files: {e}")
            return False
        
        # Process vendor data
        process_start = time.time()
        self.vendors_df = self._process_vendor_data(order_df, geo_df)
        self.original_vendors_df = self.vendors_df.copy()  # Keep original
        self.processing_times['vendor_processing'] = time.time() - process_start
        
        if self.vendors_df.empty:
            print("❌ No valid vendor data after processing!")
            return False
        
        # Process polygon data
        poly_start = time.time()
        self.poly_gdf = self._process_polygon_data(poly_df)
        self.processing_times['polygon_processing'] = time.time() - poly_start
        
        # Calculate overlaps
        overlap_start = time.time()
        self._calculate_overlaps()
        self.processing_times['overlap_calculation'] = time.time() - overlap_start
        
        # Calculate enhanced analytics
        stats_start = time.time()
        self._calculate_statistics()
        self.processing_times['statistics_calculation'] = time.time() - stats_start
        
        # Record completion time
        self.last_update_time = time.time()
        total_time = self.last_update_time - start_time
        self.processing_times['total_processing'] = total_time
        
        print(f"✅ Processing complete: {len(self.vendors_df):,} vendors ready")
        print(f"⏱️  Total processing time: {total_time:.2f} seconds")
        
        return True
    
    def _process_vendor_data(self, order_df, geo_df):
        """Process and merge vendor order and geo data with enhanced cleaning."""
        print("🔄 Processing vendor data...")
        
        # Remove duplicates from geo data
        geo_df = geo_df.drop_duplicates(subset=['vendor_code'], keep='first')
        
        # Merge order and geo data
        vendors_df = pd.merge(order_df, geo_df, on='vendor_code', how='inner', suffixes=('_order', '_geo'))
        
        # Handle vendor name columns intelligently
        if 'vendor_name_order' in vendors_df.columns:
            vendors_df['vendor_name'] = vendors_df['vendor_name_order'].fillna(vendors_df['vendor_name_geo'])
            vendors_df.drop(columns=['vendor_name_order', 'vendor_name_geo'], inplace=True)
        
        # Clean and validate data
        initial_count = len(vendors_df)
        
        # Remove rows with missing critical data
        vendors_df = vendors_df.dropna(subset=['latitude', 'longitude', 'vendor_name'])
        
        # Filter to Tehran area using config bounds
        bounds = config.TEHRAN_BOUNDS
        vendors_df = vendors_df[
            vendors_df['latitude'].between(bounds['lat_min'], bounds['lat_max']) & 
            vendors_df['longitude'].between(bounds['lon_min'], bounds['lon_max'])
        ]
        
        # Fill missing numeric values with 0 for calculations
        numeric_columns = ['total_order_count', 'organic_order_count', 'non_organic_order_count', 'avg_daily_orders']
        for col in numeric_columns:
            if col in vendors_df.columns:
                vendors_df[col] = vendors_df[col].fillna(0)
        
        # Calculate missing ratio if needed
        if 'organic_to_non_organic_ratio' not in vendors_df.columns:
            vendors_df['organic_to_non_organic_ratio'] = np.where(
                vendors_df['non_organic_order_count'] > 0,
                vendors_df['organic_order_count'] / vendors_df['non_organic_order_count'],
                0
            )
        
        # Add performance indicators
        vendors_df['performance_score'] = self._calculate_performance_score(vendors_df)
        vendors_df['volume_category'] = self._categorize_volume(vendors_df)
        
        print(f"   📍 {len(vendors_df):,} vendors in Tehran area (from {initial_count:,} total)")
        return vendors_df
    
    def _calculate_performance_score(self, df):
        """Calculate a composite performance score for each vendor."""
        # Normalize metrics to 0-1 scale
        total_orders_norm = df['total_order_count'] / df['total_order_count'].max() if df['total_order_count'].max() > 0 else 0
        daily_orders_norm = df['avg_daily_orders'] / df['avg_daily_orders'].max() if df['avg_daily_orders'].max() > 0 else 0
        
        # Composite score (can be customized)
        score = (total_orders_norm * 0.6 + daily_orders_norm * 0.4) * 100
        return score.fillna(0)
    
    def _categorize_volume(self, df):
        """Categorize vendors by volume (High/Medium/Low)."""
        # Calculate percentiles
        high_threshold = df['total_order_count'].quantile(0.75)
        low_threshold = df['total_order_count'].quantile(0.25)
        
        def categorize(orders):
            if orders >= high_threshold:
                return 'High'
            elif orders >= low_threshold:
                return 'Medium'
            else:
                return 'Low'
        
        return df['total_order_count'].apply(categorize)
    
    def _process_polygon_data(self, poly_df):
        """Process polygon data for marketing areas with enhanced validation."""
        poly_gdf = gpd.GeoDataFrame()
        if 'WKT' in poly_df.columns:
            try:
                print("🗺️  Processing marketing area polygons...")
                poly_df['geometry'] = poly_df['WKT'].apply(wkt.loads)
                poly_gdf = gpd.GeoDataFrame(poly_df, geometry='geometry', crs="EPSG:4326")
                
                # Validate and clean geometries
                valid_mask = poly_gdf.geometry.is_valid
                invalid_count = (~valid_mask).sum()
                
                if invalid_count > 0:
                    print(f"   ⚠️  {invalid_count} invalid geometries found, attempting to fix...")
                    poly_gdf.loc[~valid_mask, 'geometry'] = poly_gdf.loc[~valid_mask, 'geometry'].buffer(0)
                
                valid_geoms = poly_gdf.geometry.is_valid.sum()
                print(f"   📐 {len(poly_gdf):,} marketing areas processed ({valid_geoms} valid geometries)")
                
            except Exception as e:
                print(f"⚠️ Warning: Could not process polygon data: {e}")
        
        return poly_gdf
    
    def _calculate_overlaps(self):
        """Enhanced overlap calculation with optimization for web application."""
        print("🔄 Calculating service area overlaps...")
        
        if self.vendors_df.empty:
            return
        
        vendor_count = len(self.vendors_df)
        
        # Skip overlap calculation for very large datasets to maintain performance
        if vendor_count > config.OVERLAP_CONFIG.get('MAX_VENDORS_FOR_OVERLAP', 500):
            print(f"   ⚠️  Skipping detailed overlap calculation for {vendor_count} vendors (performance optimization)")
            self._calculate_simple_overlaps()
            return
        
        # Create GeoDataFrame and transform to projected CRS for accurate calculation
        gdf = gpd.GeoDataFrame(
            self.vendors_df,
            geometry=gpd.points_from_xy(self.vendors_df.longitude, self.vendors_df.latitude),
            crs="EPSG:4326"
        ).to_crs("EPSG:32639")  # UTM Zone 39N for Tehran
        
        # Create service radius buffers
        gdf['geometry'] = gdf.geometry.buffer(config.SERVICE_RADIUS)
        
        # Find overlaps with progress tracking
        self.overlapping_vendor_codes = set()
        self.overlap_pairs = []
        self.intersection_geometries = []
        overlap_areas = []
        
        vendor_list = list(gdf.itertuples())
        total_combinations = len(vendor_list) * (len(vendor_list) - 1) // 2
        
        print(f"   🔍 Checking {total_combinations:,} vendor pairs...")
        
        processed = 0
        for vendor1, vendor2 in itertools.combinations(vendor_list, 2):
            if vendor1.geometry.intersects(vendor2.geometry):
                self.overlapping_vendor_codes.update([vendor1.vendor_code, vendor2.vendor_code])
                self.overlap_pairs.append((vendor1.vendor_code, vendor2.vendor_code))
                
                intersection = vendor1.geometry.intersection(vendor2.geometry)
                self.intersection_geometries.append(intersection)
                overlap_areas.append(intersection.area)
            
            processed += 1
            if processed % 1000 == 0:
                progress = (processed / total_combinations) * 100
                print(f"   📊 Progress: {progress:.1f}% ({processed:,}/{total_combinations:,})")
        
        # Calculate overlap statistics
        total_overlap_area = sum(overlap_areas) if overlap_areas else 0
        avg_overlap_area = total_overlap_area / len(overlap_areas) if overlap_areas else 0
        
        print(f"   ⚠️  {len(self.overlapping_vendor_codes):,} vendors with overlapping areas")
        print(f"   🔗 {len(self.overlap_pairs):,} overlap pairs identified")
        print(f"   📏 Total overlap area: {total_overlap_area/1000000:.2f} km²")
        print(f"   📊 Average overlap size: {avg_overlap_area/1000000:.3f} km²")
    
    def _calculate_simple_overlaps(self):
        """Simplified overlap calculation for large datasets."""
        print("   🚀 Using simplified overlap detection for performance...")
        
        # Simple distance-based overlap detection
        vendors = self.vendors_df[['vendor_code', 'latitude', 'longitude']].values
        overlap_threshold = config.SERVICE_RADIUS * 2 / 111000  # Convert to degrees (approximate)
        
        overlapping = set()
        pairs = []
        
        for i, vendor1 in enumerate(vendors):
            for vendor2 in vendors[i+1:]:
                # Simple distance calculation
                distance = ((vendor1[1] - vendor2[1])**2 + (vendor1[2] - vendor2[2])**2)**0.5
                
                if distance < overlap_threshold:
                    overlapping.add(vendor1[0])
                    overlapping.add(vendor2[0])
                    pairs.append((vendor1[0], vendor2[0]))
        
        self.overlapping_vendor_codes = overlapping
        self.overlap_pairs = pairs
        self.intersection_geometries = []  # Not calculated in simple mode
        
        print(f"   ⚠️  {len(overlapping):,} vendors with potential overlaps (simplified)")
        print(f"   🔗 {len(pairs):,} overlap pairs identified")
    
    def _calculate_statistics(self):
        """Calculate enhanced vendor statistics for web application."""
        print("📈 Calculating vendor analytics...")
        
        if self.vendors_df.empty:
            return
        
        stats = {}
        
        # Basic statistics
        stats['total_vendors'] = len(self.vendors_df)
        stats['overlapping_vendors'] = len(self.overlapping_vendor_codes)
        stats['overlap_rate'] = (stats['overlapping_vendors'] / stats['total_vendors'] * 100) if stats['total_vendors'] > 0 else 0
        
        # Performance statistics
        numeric_columns = ['total_order_count', 'organic_order_count', 'non_organic_order_count', 'avg_daily_orders']
        for col in numeric_columns:
            if col in self.vendors_df.columns:
                stats[f'{col}_mean'] = float(self.vendors_df[col].mean())
                stats[f'{col}_median'] = float(self.vendors_df[col].median())
                stats[f'{col}_std'] = float(self.vendors_df[col].std())
                stats[f'{col}_max'] = float(self.vendors_df[col].max())
                stats[f'{col}_min'] = float(self.vendors_df[col].min())
                stats[f'{col}_sum'] = float(self.vendors_df[col].sum())
        
        # Geographic distribution
        stats['lat_center'] = float(self.vendors_df['latitude'].mean())
        stats['lon_center'] = float(self.vendors_df['longitude'].mean())
        stats['lat_span'] = float(self.vendors_df['latitude'].max() - self.vendors_df['latitude'].min())
        stats['lon_span'] = float(self.vendors_df['longitude'].max() - self.vendors_df['longitude'].min())
        
        # Density metrics
        area_km2 = stats['lat_span'] * stats['lon_span'] * 111000 * 111000 / 1000000  # Rough area in km²
        stats['vendor_density'] = stats['total_vendors'] / area_km2 if area_km2 > 0 else 0
        
        # Performance categories
        volume_counts = self.vendors_df['volume_category'].value_counts()
        stats['high_volume_count'] = int(volume_counts.get('High', 0))
        stats['medium_volume_count'] = int(volume_counts.get('Medium', 0))
        stats['low_volume_count'] = int(volume_counts.get('Low', 0))
        
        # Processing performance
        stats['processing_times'] = self.processing_times
        stats['last_update'] = self.last_update_time
        
        self.vendor_statistics = stats
        
        print(f"   📊 Analytics complete: {stats['overlap_rate']:.1f}% overlap rate")
        print(f"   🗺️  Vendor density: {stats['vendor_density']:.2f} vendors/km²")
        print(f"   🏆 High volume vendors: {stats['high_volume_count']}")
    
    def get_vendor_data_for_js(self):
        """Prepare vendor data for JavaScript with enhanced metadata for web app."""
        if self.vendors_df.empty:
            return []
        
        vendors_js_data = []
        for _, vendor in self.vendors_df.iterrows():
            vendor_dict = {
                'vendor_code': vendor['vendor_code'],
                'vendor_name': str(vendor['vendor_name']),
                'latitude': float(vendor['latitude']),
                'longitude': float(vendor['longitude']),
                'total_order_count': int(vendor.get('total_order_count', 0)) if pd.notna(vendor.get('total_order_count', 0)) else 0,
                'organic_order_count': int(vendor.get('organic_order_count', 0)) if pd.notna(vendor.get('organic_order_count', 0)) else 0,
                'non_organic_order_count': int(vendor.get('non_organic_order_count', 0)) if pd.notna(vendor.get('non_organic_order_count', 0)) else 0,
                'organic_to_non_organic_ratio': float(vendor.get('organic_to_non_organic_ratio', 0)) if pd.notna(vendor.get('organic_to_non_organic_ratio', 0)) else 0,
                'avg_daily_orders': float(vendor.get('avg_daily_orders', 0)) if pd.notna(vendor.get('avg_daily_orders', 0)) else 0,
                'is_overlapping': vendor['vendor_code'] in self.overlapping_vendor_codes,
                'performance_score': float(vendor.get('performance_score', 0)),
                'volume_category': vendor.get('volume_category', 'Unknown')
            }
            vendors_js_data.append(vendor_dict)
        
        return vendors_js_data
    
    def filter_vendors_real_time(self, hidden_vendor_codes):
        """Filter vendors in real-time for web application."""
        if not hidden_vendor_codes:
            # Return all vendors if no filters
            return self.get_vendor_data_for_js(), self.overlapping_vendor_codes
        
        # Filter out hidden vendors
        visible_vendors = self.vendors_df[~self.vendors_df['vendor_code'].isin(hidden_vendor_codes)]
        
        # Recalculate overlaps for visible vendors only
        visible_overlapping = set()
        if not visible_vendors.empty:
            visible_overlapping = self._calculate_overlaps_for_subset(visible_vendors)
        
        # Prepare data for JavaScript
        vendors_js_data = []
        for _, vendor in visible_vendors.iterrows():
            vendor_dict = {
                'vendor_code': vendor['vendor_code'],
                'vendor_name': str(vendor['vendor_name']),
                'latitude': float(vendor['latitude']),
                'longitude': float(vendor['longitude']),
                'total_order_count': int(vendor.get('total_order_count', 0)) if pd.notna(vendor.get('total_order_count', 0)) else 0,
                'organic_order_count': int(vendor.get('organic_order_count', 0)) if pd.notna(vendor.get('organic_order_count', 0)) else 0,
                'non_organic_order_count': int(vendor.get('non_organic_order_count', 0)) if pd.notna(vendor.get('non_organic_order_count', 0)) else 0,
                'organic_to_non_organic_ratio': float(vendor.get('organic_to_non_organic_ratio', 0)) if pd.notna(vendor.get('organic_to_non_organic_ratio', 0)) else 0,
                'avg_daily_orders': float(vendor.get('avg_daily_orders', 0)) if pd.notna(vendor.get('avg_daily_orders', 0)) else 0,
                'is_overlapping': vendor['vendor_code'] in visible_overlapping,
                'performance_score': float(vendor.get('performance_score', 0)),
                'volume_category': vendor.get('volume_category', 'Unknown')
            }
            vendors_js_data.append(vendor_dict)
        
        return vendors_js_data, visible_overlapping
    
    def _calculate_overlaps_for_subset(self, vendors_subset):
        """Calculate overlaps for a subset of vendors (used in real-time filtering)."""
        if len(vendors_subset) < 2:
            return set()
        
        overlapping = set()
        
        # Simple distance-based calculation for real-time performance
        vendors_array = vendors_subset[['vendor_code', 'latitude', 'longitude']].values
        overlap_threshold = config.SERVICE_RADIUS * 2 / 111000  # Convert to degrees
        
        for i, vendor1 in enumerate(vendors_array):
            for vendor2 in vendors_array[i+1:]:
                distance = ((vendor1[1] - vendor2[1])**2 + (vendor1[2] - vendor2[2])**2)**0.5
                
                if distance < overlap_threshold:
                    overlapping.add(vendor1[0])
                    overlapping.add(vendor2[0])
        
        return overlapping
    
    def get_ranking_data(self, ranking_criterion, hidden_vendors=None):
        """Get vendor data sorted by ranking criterion."""
        if hidden_vendors is None:
            hidden_vendors = set()
        
        # Filter vendors
        visible_vendors = self.vendors_df[~self.vendors_df['vendor_code'].isin(hidden_vendors)]
        
        # Get ranking column
        ranking_column = config.RANKING_CRITERIA.get(ranking_criterion)
        if not ranking_column or ranking_column not in visible_vendors.columns:
            return []
        
        # Sort by ranking criteria
        sorted_vendors = visible_vendors.sort_values(
            by=ranking_column,
            ascending=False,
            na_position='last'
        ).reset_index(drop=True)
        
        # Add rank numbers
        sorted_vendors['rank'] = range(1, len(sorted_vendors) + 1)
        
        # Convert to list format
        ranking_data = []
        for _, vendor in sorted_vendors.iterrows():
            vendor_dict = {
                'rank': vendor['rank'],
                'vendor_code': vendor['vendor_code'],
                'vendor_name': vendor['vendor_name'],
                'value': float(vendor[ranking_column]) if pd.notna(vendor[ranking_column]) else 0,
                'latitude': float(vendor['latitude']),
                'longitude': float(vendor['longitude']),
                'is_overlapping': vendor['vendor_code'] in self.overlapping_vendor_codes
            }
            ranking_data.append(vendor_dict)
        
        return ranking_data
    
    def format_dataframe_for_display(self, df):
        """Enhanced DataFrame formatting for HTML display."""
        display_df = df.copy()
        
        # Format numeric columns
        if 'avg_daily_orders' in display_df.columns:
            display_df['avg_daily_orders'] = display_df['avg_daily_orders'].apply(
                lambda x: f"{x:.2f}" if pd.notna(x) else "0.00"
            )
        
        # Convert ratio to percentage
        if 'organic_to_non_organic_ratio' in display_df.columns:
            display_df['organic_to_non_organic_ratio'] = display_df['organic_to_non_organic_ratio'].apply(
                lambda x: f"{x*100:.2f}%" if pd.notna(x) else "0.00%"
            )
        
        # Format integer columns with commas
        int_columns = ['total_order_count', 'organic_order_count', 'non_organic_order_count']
        for col in int_columns:
            if col in display_df.columns:
                display_df[col] = display_df[col].apply(
                    lambda x: f"{int(x):,}" if pd.notna(x) else "0"
                )
        
        # Add ranking columns for each criteria
        for rank_name, rank_column in config.RANKING_CRITERIA.items():
            if rank_column in df.columns:
                rank_col_name = f'{rank_name}_Rank'
                display_df[rank_col_name] = df[rank_column].rank(method='dense', ascending=False).astype(int)
        
        # Add performance category
        if 'volume_category' in display_df.columns:
            display_df['Volume_Category'] = display_df['volume_category']
        
        return display_df
    
    def get_performance_summary(self):
        """Get a summary of processing performance."""
        if not self.processing_times:
            return {}
        
        return {
            'total_time': self.processing_times.get('total_processing', 0),
            'data_loading': self.processing_times.get('data_loading', 0),
            'vendor_processing': self.processing_times.get('vendor_processing', 0),
            'overlap_calculation': self.processing_times.get('overlap_calculation', 0),
            'statistics_calculation': self.processing_times.get('statistics_calculation', 0),
            'last_update': self.last_update_time,
            'vendors_processed': len(self.vendors_df) if self.vendors_df is not None else 0
        }