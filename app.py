#!/usr/bin/env python3
"""
Tehran Vendor Mapping - Live Web Application
Flask-based web server for real-time vendor filtering and analytics.
"""

import os
import sys
import json
import socket
from pathlib import Path
from flask import Flask, render_template, jsonify, request, send_from_directory
from flask_cors import CORS

# Add modules directory to path
sys.path.append(str(Path(__file__).parent / 'modules'))

from data_processor import DataProcessor
from web_map_generator import WebMapGenerator
import config

app = Flask(__name__)
CORS(app)  # Enable CORS for AJAX requests

# Global variables to store data
data_processor = None
map_generator = None
original_vendor_data = []
current_hidden_vendors = set()

def initialize_application():
    """Initialize the application with data loading."""
    global data_processor, map_generator, original_vendor_data
    
    print("🚀 Initializing Tehran Vendor Mapping Web Application...")
    
    # Setup directories
    project_root = Path(__file__).parent
    data_dir = project_root / 'data'
    
    # File paths
    order_file = data_dir / config.DEFAULT_ORDER_FILE
    geo_file = data_dir / config.DEFAULT_GEO_FILE
    polygon_file = data_dir / config.DEFAULT_POLYGON_FILE
    
    # Check if files exist
    if not all([order_file.exists(), geo_file.exists(), polygon_file.exists()]):
        print("❌ Error: Required data files not found in 'data' directory")
        print(f"   Looking for: {order_file.name}, {geo_file.name}, {polygon_file.name}")
        return False
    
    # Initialize data processor and load data
    data_processor = DataProcessor()
    if not data_processor.load_data(str(order_file), str(geo_file), str(polygon_file)):
        print("❌ Error: Failed to load data")
        return False
    
    # Initialize map generator
    map_generator = WebMapGenerator()
    
    # Store original vendor data for filtering
    original_vendor_data = data_processor.get_vendor_data_for_js()
    
    print(f"✅ Application initialized with {len(original_vendor_data)} vendors")
    return True

@app.route('/')
def index():
    """Main page route."""
    if data_processor is None:
        return "Application not initialized. Please check data files.", 500
    
    return render_template('index.html', 
                         vendor_data=original_vendor_data,
                         config=get_config_for_template())

@app.route('/api/vendors')
def get_vendors():
    """API endpoint to get vendor data."""
    return jsonify({
        'vendors': original_vendor_data,
        'hidden': list(current_hidden_vendors),
        'total': len(original_vendor_data)
    })

@app.route('/api/filter_vendors', methods=['POST'])
def filter_vendors():
    """API endpoint to filter vendors in real-time."""
    global current_hidden_vendors
    
    try:
        data = request.get_json()
        hidden_vendor_codes = data.get('hidden_vendors', [])
        current_hidden_vendors = set(hidden_vendor_codes)
        
        # Calculate filtered statistics
        visible_vendors = [v for v in original_vendor_data if v['vendor_code'] not in current_hidden_vendors]
        
        # Calculate overlaps for visible vendors only
        overlapping_visible = calculate_overlaps_for_vendors(visible_vendors)
        
        statistics = {
            'total_vendors': len(original_vendor_data),
            'active_vendors': len(visible_vendors),
            'hidden_vendors': len(current_hidden_vendors),
            'overlapping_vendors': len(overlapping_visible),
            'overlap_rate': (len(overlapping_visible) / len(visible_vendors) * 100) if visible_vendors else 0,
            'avg_orders': sum(v['total_order_count'] for v in visible_vendors) / len(visible_vendors) if visible_vendors else 0,
            'max_orders': max((v['total_order_count'] for v in visible_vendors), default=0)
        }
        
        return jsonify({
            'success': True,
            'visible_vendors': visible_vendors,
            'statistics': statistics,
            'overlapping_vendors': list(overlapping_visible)
        })
        
    except Exception as e:
        print(f"Error in filter_vendors: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/rankings/<ranking_type>')
def get_rankings(ranking_type):
    """API endpoint to get vendor rankings by different criteria."""
    try:
        # Get visible vendors
        visible_vendors = [v for v in original_vendor_data if v['vendor_code'] not in current_hidden_vendors]
        
        # Map ranking type to column name
        ranking_mapping = {
            'Total Orders': 'total_order_count',
            'Organic Orders': 'organic_order_count', 
            'Non-Organic Orders': 'non_organic_order_count',
            'Organic/Non-Organic Ratio': 'organic_to_non_organic_ratio',
            'Avg Daily Orders': 'avg_daily_orders'
        }
        
        ranking_column = ranking_mapping.get(ranking_type)
        if not ranking_column:
            return jsonify({'error': f'Invalid ranking type: {ranking_type}'}), 400
        
        # Sort vendors by the specified criteria
        sorted_vendors = sorted(visible_vendors, 
                              key=lambda x: x.get(ranking_column, 0), 
                              reverse=True)
        
        # Add rank numbers
        for i, vendor in enumerate(sorted_vendors):
            vendor['rank'] = i + 1
        
        return jsonify({
            'ranking_type': ranking_type,
            'vendors': sorted_vendors,
            'total': len(sorted_vendors)
        })
        
    except Exception as e:
        print(f"Error in get_rankings: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/statistics')
def get_statistics():
    """API endpoint to get current statistics."""
    try:
        visible_vendors = [v for v in original_vendor_data if v['vendor_code'] not in current_hidden_vendors]
        overlapping_visible = calculate_overlaps_for_vendors(visible_vendors)
        
        statistics = {
            'total_vendors': len(original_vendor_data),
            'active_vendors': len(visible_vendors),
            'hidden_vendors': len(current_hidden_vendors),
            'overlapping_vendors': len(overlapping_visible),
            'overlap_rate': (len(overlapping_visible) / len(visible_vendors) * 100) if visible_vendors else 0,
            'vendor_density': data_processor.vendor_statistics.get('vendor_density', 0),
            'avg_orders': sum(v['total_order_count'] for v in visible_vendors) / len(visible_vendors) if visible_vendors else 0,
            'max_orders': max((v['total_order_count'] for v in visible_vendors), default=0),
            'total_orders': sum(v['total_order_count'] for v in visible_vendors)
        }
        
        return jsonify(statistics)
        
    except Exception as e:
        print(f"Error in get_statistics: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/export/<format>')
def export_data(format):
    """API endpoint to export data in different formats."""
    try:
        visible_vendors = [v for v in original_vendor_data if v['vendor_code'] not in current_hidden_vendors]
        
        if format == 'csv':
            # Convert to CSV format
            import csv
            import io
            
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write headers
            headers = ['vendor_code', 'vendor_name', 'total_order_count', 'organic_order_count', 
                      'non_organic_order_count', 'organic_to_non_organic_ratio', 'avg_daily_orders']
            writer.writerow(headers)
            
            # Write data
            for vendor in visible_vendors:
                row = [vendor.get(header, '') for header in headers]
                writer.writerow(row)
            
            return jsonify({
                'success': True,
                'data': output.getvalue(),
                'filename': f'tehran_vendors_{len(visible_vendors)}.csv'
            })
            
        else:
            return jsonify({'error': 'Unsupported format'}), 400
            
    except Exception as e:
        print(f"Error in export_data: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/static/<path:filename>')
def static_files(filename):
    """Serve static files."""
    return send_from_directory('static', filename)

def calculate_overlaps_for_vendors(vendors):
    """Calculate which vendors have overlapping service areas."""
    overlapping = set()
    
    for i, vendor1 in enumerate(vendors):
        for vendor2 in vendors[i+1:]:
            # Calculate distance between vendors
            lat1, lon1 = vendor1['latitude'], vendor1['longitude']
            lat2, lon2 = vendor2['latitude'], vendor2['longitude']
            
            # Simple distance calculation (approximate)
            distance = ((lat1 - lat2) ** 2 + (lon1 - lon2) ** 2) ** 0.5 * 111000  # rough conversion to meters
            
            # If distance is less than 6km (2 * 3km radius), they overlap
            if distance < 6000:
                overlapping.add(vendor1['vendor_code'])
                overlapping.add(vendor2['vendor_code'])
    
    return overlapping

def get_config_for_template():
    """Get configuration data for template rendering."""
    return {
        'RANKING_CRITERIA': config.RANKING_CRITERIA,
        'RANK_COLORS': config.RANK_COLORS,
        'MAP_CENTER': config.MAP_CENTER,
        'MAP_ZOOM': config.MAP_ZOOM,
        'SERVICE_RADIUS': config.SERVICE_RADIUS,
        'TEHRAN_BOUNDS': config.TEHRAN_BOUNDS
    }

def get_local_ip():
    """Get the local IP address."""
    try:
        # Connect to a dummy address to get local IP
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except:
        return "127.0.0.1"

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({'error': 'Internal server error'}), 500

def main():
    """Main application entry point."""
    print("\n" + "="*70)
    print("🗺️  TEHRAN VENDOR MAPPING - LIVE WEB APPLICATION")
    print("="*70)
    
    # Initialize application
    if not initialize_application():
        print("❌ Failed to initialize application")
        sys.exit(1)
    
    # Get local IP
    local_ip = get_local_ip()
    port = 5000
    
    print(f"\n🌐 Starting web server...")
    print(f"📍 Local Access: http://localhost:{port}")
    print(f"🌍 Network Access: http://{local_ip}:{port}")
    print(f"\n✨ Features Available:")
    print(f"   🎯 Real-time vendor filtering")
    print(f"   📊 Live statistics dashboard")
    print(f"   🏆 Dynamic rankings by multiple criteria")
    print(f"   🌙 Light/Dark theme toggle")
    print(f"   📱 Mobile responsive design")
    print(f"   💾 Data export capabilities")
    print(f"\n🔄 The application will automatically refresh when you make changes!")
    print("="*70)
    
    try:
        # Run the Flask application
        app.run(
            host='0.0.0.0',  # Listen on all interfaces
            port=port,
            debug=True,      # Enable debug mode for development
            threaded=True    # Handle multiple requests
        )
    except KeyboardInterrupt:
        print("\n\n🛑 Application stopped by user.")
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()