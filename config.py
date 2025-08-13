"""
Enhanced Configuration Settings for Tehran Vendor Mapping Web Application.
Modify these settings to customize the application behavior and features.
"""

import os
from pathlib import Path

# ==================== FILE PATHS ====================
DEFAULT_ORDER_FILE = 'vendor_order_info.xlsx'
DEFAULT_GEO_FILE = 'vendor_geo_info.xlsx'
DEFAULT_POLYGON_FILE = 'tehran_polygons.csv'

# Directory structure for Flask application
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / 'data'
TEMPLATES_DIR = BASE_DIR / 'templates'
STATIC_DIR = BASE_DIR / 'static'
MODULES_DIR = BASE_DIR / 'modules'
LOGS_DIR = BASE_DIR / 'logs'

# ==================== TEHRAN GEOGRAPHIC SETTINGS ====================
# Tehran geographic bounds (lat_min, lat_max, lon_min, lon_max)
TEHRAN_BOUNDS = {
    'lat_min': 35.0,
    'lat_max': 36.0,
    'lon_min': 50.5,
    'lon_max': 52.0
}

# Map settings
MAP_CENTER = [35.6892, 51.3890]  # Tehran center coordinates
MAP_ZOOM = 11
SERVICE_RADIUS = 3000  # Service radius in meters (3km)

# ==================== RANKING CRITERIA & METRICS ====================
# Original ranking criteria with display names
RANKING_CRITERIA = {
    "Total Orders": "total_order_count",
    "Organic Orders": "organic_order_count",
    "Non-Organic Orders": "non_organic_order_count",
    "Organic/Non-Organic Ratio": "organic_to_non_organic_ratio",
    "Avg Daily Orders": "avg_daily_orders"
}

# Enhanced color scheme for ranking layers (restored from original)
RANK_COLORS = {
    "Total Orders": "#6A0DAD",        # Purple - represents overall volume
    "Organic Orders": "#228B22",      # Forest Green - natural/organic
    "Non-Organic Orders": "#FF8C00",  # Dark Orange - processed/non-organic
    "Organic/Non-Organic Ratio": "#808080",  # Gray - neutral metric
    "Avg Daily Orders": "#4682B4"     # Steel Blue - daily performance
}

# ==================== WEB APPLICATION SETTINGS ====================
# Flask application configuration
FLASK_CONFIG = {
    'SECRET_KEY': os.environ.get('SECRET_KEY', 'tehran-vendor-map-secret-key-2024'),
    'DEBUG': os.environ.get('FLASK_DEBUG', 'True').lower() == 'true',
    'HOST': '0.0.0.0',  # Listen on all interfaces
    'PORT': int(os.environ.get('FLASK_PORT', 5000)),
    'THREADED': True
}

# API configuration
API_CONFIG = {
    'ENABLE_CORS': True,
    'RATE_LIMITING': True,
    'MAX_REQUESTS_PER_MINUTE': 100,
    'CACHE_TIMEOUT': 300  # 5 minutes
}

# ==================== REAL-TIME FEATURES ====================
# Enable/disable real-time features
ENABLE_REAL_TIME_FILTERING = True
ENABLE_LIVE_STATISTICS = True
ENABLE_AUTO_REFRESH = True
AUTO_REFRESH_INTERVAL = 30000  # milliseconds (30 seconds)

# WebSocket settings (for future real-time features)
WEBSOCKET_CONFIG = {
    'ENABLE_WEBSOCKETS': False,  # Future feature
    'PING_INTERVAL': 25,
    'PING_TIMEOUT': 60
}

# ==================== UI & THEME SETTINGS ====================
# Theme configuration
THEMES = {
    'light': {
        'name': 'Light Theme',
        'primary_color': '#667eea',
        'secondary_color': '#764ba2',
        'background_color': '#f8f9fa',
        'text_color': '#333333',
        'card_background': '#ffffff',
        'border_color': '#e0e0e0'
    },
    'dark': {
        'name': 'Dark Theme',
        'primary_color': '#667eea',
        'secondary_color': '#764ba2',
        'background_color': '#1a1a1a',
        'text_color': '#e0e0e0',
        'card_background': '#2d2d2d',
        'border_color': '#404040'
    }
}

DEFAULT_THEME = 'light'
ENABLE_THEME_SWITCHER = True

# Panel configuration
PANEL_CONFIG = {
    'ENABLE_STATISTICS_PANEL': True,
    'ENABLE_VENDOR_SELECTION': True,
    'ENABLE_RANKING_PANEL': True,
    'ALLOW_PANEL_MINIMIZE': True,
    'PANELS_MINIMIZED_BY_DEFAULT': False
}

# Display limits
DISPLAY_LIMITS = {
    'MAX_VENDORS_DISPLAY': 50,
    'MAX_SEARCH_RESULTS': 20,
    'MAX_RANKING_DISPLAY': 100
}

# ==================== PERFORMANCE & FILTERING SETTINGS ====================
# Overlap detection settings
OVERLAP_CONFIG = {
    'ENABLE_OVERLAP_DETECTION': True,
    'MAX_VENDORS_FOR_OVERLAP': 500,  # Optimize for large datasets
    'OVERLAP_THRESHOLD_METERS': 6000,  # 2 * SERVICE_RADIUS
    'ENABLE_OVERLAP_VISUALIZATION': True
}

# Filtering capabilities
FILTER_CONFIG = {
    'ENABLE_TEXT_SEARCH': True,
    'ENABLE_PERFORMANCE_FILTER': True,
    'ENABLE_OVERLAP_FILTER': True,
    'ENABLE_BULK_SELECTION': True,
    'SEARCH_DEBOUNCE_MS': 300
}

# Performance thresholds
PERFORMANCE_THRESHOLDS = {
    'HIGH_VOLUME_PERCENTILE': 75,  # Top 25% are "high volume"
    'LOW_VOLUME_PERCENTILE': 25,   # Bottom 25% are "low volume"
    'MIN_ORDERS_THRESHOLD': 10     # Minimum orders to be considered active
}

# ==================== MAP & VISUALIZATION SETTINGS ====================
# Map layer configuration
MAP_LAYERS = {
    'openstreetmap': {
        'name': '🗺️ Standard Map',
        'url': 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
        'attribution': '© OpenStreetMap contributors',
        'default': True
    },
    'satellite': {
        'name': '🛰️ Satellite',
        'url': 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        'attribution': '© Esri',
        'default': False
    },
    'dark': {
        'name': '🌙 Dark Theme',
        'url': 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',
        'attribution': '© CARTO',
        'default': False
    }
}

# Visual enhancements
VISUAL_CONFIG = {
    'ENABLE_ANIMATIONS': True,
    'ANIMATION_DURATION': 300,
    'ENABLE_HOVER_EFFECTS': True,
    'ENABLE_MARKER_CLUSTERING': False,  # For very large datasets
    'MARKER_SIZE': 32,
    'CIRCLE_OPACITY': 0.1,
    'CIRCLE_STROKE_WIDTH': 2
}

# Marketing areas
MARKETING_AREAS_CONFIG = {
    'ENABLE_MARKETING_AREAS': True,
    'AREA_OPACITY': 0.15,
    'AREA_STROKE_WIDTH': 2,
    'AREA_COLOR': '#3186cc'
}

# ==================== DATA PROCESSING SETTINGS ====================
# Column mapping for flexible data structures
COLUMN_MAPPING = {
    'vendor_code': ['vendor_code', 'vendor_id', 'code', 'id'],
    'vendor_name': ['vendor_name', 'name', 'business_name'],
    'latitude': ['latitude', 'lat', 'y'],
    'longitude': ['longitude', 'lng', 'lon', 'x'],
    'total_order_count': ['total_order_count', 'total_orders', 'order_count'],
    'organic_order_count': ['organic_order_count', 'organic_orders'],
    'non_organic_order_count': ['non_organic_order_count', 'non_organic_orders'],
    'organic_to_non_organic_ratio': ['organic_to_non_organic_ratio', 'organic_ratio'],
    'avg_daily_orders': ['avg_daily_orders', 'daily_avg', 'avg_daily']
}

# Data validation settings
DATA_VALIDATION = {
    'REQUIRE_ALL_METRICS': False,
    'MIN_VENDORS_REQUIRED': 1,
    'VALIDATE_COORDINATES': True,
    'ALLOW_MISSING_NAMES': False,
    'MIN_ORDER_COUNT': 0,
    'MAX_ORDER_COUNT': 999999
}

# ==================== EXPORT & ANALYTICS SETTINGS ====================
# Data export configuration
EXPORT_CONFIG = {
    'ENABLE_CSV_EXPORT': True,
    'ENABLE_EXCEL_EXPORT': True,
    'INCLUDE_METADATA': True,
    'CSV_DELIMITER': ',',
    'CSV_ENCODING': 'utf-8'
}

# Analytics configuration
ANALYTICS_CONFIG = {
    'ENABLE_PERFORMANCE_MONITORING': True,
    'TRACK_USER_INTERACTIONS': False,  # Privacy-focused
    'LOG_API_CALLS': True,
    'CACHE_STATISTICS': True,
    'STATISTICS_CACHE_DURATION': 60  # seconds
}

# ==================== NOTIFICATION SETTINGS ====================
# User feedback system
NOTIFICATION_CONFIG = {
    'ENABLE_NOTIFICATIONS': True,
    'DEFAULT_DURATION': 3000,  # milliseconds
    'MAX_NOTIFICATIONS': 5,
    'POSITION': 'top-right',
    'TYPES': {
        'success': {'icon': 'fas fa-check-circle', 'color': '#4CAF50'},
        'warning': {'icon': 'fas fa-exclamation-triangle', 'color': '#FF9800'},
        'error': {'icon': 'fas fa-exclamation-circle', 'color': '#F44336'},
        'info': {'icon': 'fas fa-info-circle', 'color': '#2196F3'}
    }
}

# ==================== ACCESSIBILITY SETTINGS ====================
# WCAG compliance and accessibility features
ACCESSIBILITY_CONFIG = {
    'ENABLE_KEYBOARD_NAVIGATION': True,
    'ENABLE_SCREEN_READER_SUPPORT': True,
    'ENABLE_HIGH_CONTRAST': True,
    'ENABLE_REDUCED_MOTION': True,
    'MIN_FONT_SIZE': 12,
    'MIN_TOUCH_TARGET': 44,  # pixels
    'FOCUS_OUTLINE_WIDTH': 2
}

# ==================== RESPONSIVE DESIGN SETTINGS ====================
# Mobile and responsive design configuration
RESPONSIVE_CONFIG = {
    'ENABLE_MOBILE_RESPONSIVE': True,
    'MOBILE_BREAKPOINT': 768,  # pixels
    'TABLET_BREAKPOINT': 1024,  # pixels
    'ENABLE_TOUCH_GESTURES': True,
    'MOBILE_MAP_HEIGHT': '60vh',
    'DESKTOP_MAP_HEIGHT': '100vh'
}

# ==================== SECURITY SETTINGS ====================
# Security configuration for web application
SECURITY_CONFIG = {
    'ENABLE_CSRF_PROTECTION': True,
    'ENABLE_SECURE_HEADERS': True,
    'SESSION_TIMEOUT': 3600,  # 1 hour
    'MAX_CONTENT_LENGTH': 16 * 1024 * 1024,  # 16MB
    'ALLOWED_EXTENSIONS': {'xlsx', 'csv', 'json'}
}

# ==================== LOGGING SETTINGS ====================
# Logging configuration
LOGGING_CONFIG = {
    'ENABLE_LOGGING': True,
    'LOG_LEVEL': 'INFO',
    'LOG_FORMAT': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'LOG_FILE': LOGS_DIR / 'vendor_map.log',
    'MAX_LOG_SIZE': 10 * 1024 * 1024,  # 10MB
    'BACKUP_COUNT': 5
}

# ==================== DEVELOPMENT SETTINGS ====================
# Development and debugging
DEVELOPMENT_CONFIG = {
    'ENABLE_DEBUG_MODE': FLASK_CONFIG['DEBUG'],
    'ENABLE_AUTO_RELOAD': True,
    'ENABLE_DETAILED_ERRORS': FLASK_CONFIG['DEBUG'],
    'ENABLE_PROFILING': False,
    'MOCK_DATA_ENABLED': False
}

# ==================== FEATURE FLAGS ====================
# Feature toggles for easy enable/disable
FEATURE_FLAGS = {
    # Core features
    'VENDOR_SELECTION': True,
    'REAL_TIME_FILTERING': True,
    'LIVE_STATISTICS': True,
    'RANKING_SYSTEM': True,
    
    # UI features
    'THEME_SWITCHER': True,
    'PANEL_MINIMIZE': True,
    'SEARCH_FUNCTIONALITY': True,
    'BULK_OPERATIONS': True,
    
    # Advanced features
    'OVERLAP_DETECTION': True,
    'MARKETING_AREAS': True,
    'DATA_EXPORT': True,
    'PERFORMANCE_ANALYTICS': True,
    
    # Future features
    'WEBSOCKET_SUPPORT': False,
    'USER_AUTHENTICATION': False,
    'MULTI_TENANT': False,
    'API_VERSIONING': False
}

# ==================== UTILITY FUNCTIONS ====================
def get_config_summary():
    """Get a summary of current configuration."""
    enabled_features = [k for k, v in FEATURE_FLAGS.items() if v]
    
    return {
        'flask_debug': FLASK_CONFIG['DEBUG'],
        'service_radius_km': SERVICE_RADIUS / 1000,
        'ranking_criteria_count': len(RANKING_CRITERIA),
        'enabled_features': len(enabled_features),
        'theme_count': len(THEMES),
        'map_layers_count': len(MAP_LAYERS),
        'data_directory': str(DATA_DIR),
        'templates_directory': str(TEMPLATES_DIR)
    }

def validate_config():
    """Validate configuration settings."""
    warnings = []
    
    # Check directories
    for directory in [DATA_DIR, TEMPLATES_DIR, MODULES_DIR]:
        if not directory.exists():
            warnings.append(f"Directory missing: {directory}")
    
    # Check bounds
    bounds = TEHRAN_BOUNDS
    if bounds['lat_min'] >= bounds['lat_max']:
        warnings.append("Invalid latitude bounds")
    
    if bounds['lon_min'] >= bounds['lon_max']:
        warnings.append("Invalid longitude bounds")
    
    # Check colors
    for name, color in RANK_COLORS.items():
        if not color.startswith('#') or len(color) != 7:
            warnings.append(f"Invalid color format for {name}: {color}")
    
    return warnings

def create_directories():
    """Create necessary directories if they don't exist."""
    directories = [DATA_DIR, TEMPLATES_DIR, STATIC_DIR, MODULES_DIR, LOGS_DIR]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)

# Auto-create directories when config is imported
if not os.environ.get('TESTING'):
    create_directories()

# ==================== EXPORTS ====================
__all__ = [
    'RANKING_CRITERIA', 'RANK_COLORS', 'MAP_CENTER', 'MAP_ZOOM', 'SERVICE_RADIUS',
    'TEHRAN_BOUNDS', 'FLASK_CONFIG', 'FEATURE_FLAGS', 'THEMES', 'DEFAULT_THEME',
    'DATA_DIR', 'TEMPLATES_DIR', 'STATIC_DIR', 'MODULES_DIR',
    'get_config_summary', 'validate_config'
]