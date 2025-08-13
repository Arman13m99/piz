"""
Tehran Vendor Mapping Modules - Web Application Version
Core functionality modules for the live web-based vendor mapping application.
"""

__version__ = "2.0.0-web"
__author__ = "Tehran Vendor Mapping Team"

# Import core modules
try:
    from .data_processor import DataProcessor
    from .web_map_generator import WebMapGenerator
    
    __all__ = ['DataProcessor', 'WebMapGenerator']
    
except ImportError as e:
    # Handle import errors gracefully
    import sys
    print(f"Warning: Could not import all modules: {e}", file=sys.stderr)
    __all__ = []

# Module metadata
MODULES_INFO = {
    'data_processor': {
        'description': 'Handles data loading, processing, and validation',
        'dependencies': ['pandas', 'geopandas', 'shapely'],
        'features': ['overlap_detection', 'statistics_calculation', 'data_validation']
    },
    'web_map_generator': {
        'description': 'Generates interactive maps for web application',
        'dependencies': ['folium', 'geopandas'],
        'features': ['multi_layer_maps', 'popup_generation', 'tile_layers']
    }
}

def get_module_info():
    """Get information about available modules."""
    return MODULES_INFO

def check_dependencies():
    """Check if all required dependencies are installed."""
    required_packages = [
        'pandas', 'geopandas', 'folium', 'shapely', 
        'flask', 'flask_cors'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('_', '-'))
        except ImportError:
            missing_packages.append(package)
    
    return missing_packages

def initialize_modules():
    """Initialize all modules and check for compatibility."""
    print("🔧 Initializing Tehran Vendor Mapping modules...")
    
    # Check dependencies
    missing = check_dependencies()
    if missing:
        print(f"⚠️  Missing packages: {', '.join(missing)}")
        print("   Run: pip install -r requirements.txt")
        return False
    
    # Test module imports
    try:
        from . import data_processor, web_map_generator
        print("✅ All modules loaded successfully")
        return True
    except Exception as e:
        print(f"❌ Error loading modules: {e}")
        return False

# Auto-initialize when imported (optional)
if __name__ != '__main__':
    # Only auto-initialize in non-testing environments
    import os
    if not os.environ.get('TESTING'):
        initialize_modules()