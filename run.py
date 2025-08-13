#!/usr/bin/env python3
"""
Tehran Vendor Mapping - Simple Run Script
One-click startup for the live web application.
"""

import os
import sys
import subprocess
import platform
import webbrowser
import time
from pathlib import Path


def print_banner():
    """Print application banner."""
    print("\n" + "="*60)
    print("🗺️  TEHRAN VENDOR MAP - LIVE WEB APPLICATION")
    print("="*60)
    print("🚀 Starting your interactive vendor analytics platform...")
    print()


def check_system():
    """Check system compatibility."""
    print("🔍 System Check:")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print(f"   ❌ Python 3.8+ required (current: {sys.version})")
        return False
    else:
        print(f"   ✅ Python {sys.version.split()[0]}")
    
    # Check operating system
    os_name = platform.system()
    print(f"   ✅ Operating System: {os_name}")
    
    # Check available memory (basic check)
    try:
        import psutil
        memory = psutil.virtual_memory()
        print(f"   ✅ Available Memory: {memory.available // (1024**3):.1f} GB")
    except ImportError:
        print("   ℹ️  Memory info not available")
    
    return True


def install_requirements():
    """Install required packages."""
    print("\n📦 Installing Requirements:")
    
    # Check if requirements.txt exists
    req_file = Path("requirements.txt")
    if not req_file.exists():
        print("   ❌ requirements.txt not found")
        return False
    
    try:
        # Try importing key packages first
        import flask, pandas, geopandas, folium
        print("   ✅ All packages already installed")
        return True
    except ImportError:
        print("   🔄 Installing missing packages...")
        
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", "-r", "requirements.txt", 
                "--quiet", "--disable-pip-version-check"
            ])
            print("   ✅ Packages installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"   ❌ Installation failed: {e}")
            return False


def check_data_files():
    """Check if data files exist."""
    print("\n📊 Data Files Check:")
    
    data_dir = Path("data")
    required_files = [
        "vendor_order_info.xlsx",
        "vendor_geo_info.xlsx", 
        "tehran_polygons.csv"
    ]
    
    missing_files = []
    for filename in required_files:
        filepath = data_dir / filename
        if filepath.exists():
            print(f"   ✅ {filename}")
        else:
            print(f"   ❌ {filename} (missing)")
            missing_files.append(filename)
    
    if missing_files:
        print(f"\n   ⚠️  Missing {len(missing_files)} data files")
        create_examples = input("   🔧 Create example data files? (y/n): ").lower().strip()
        
        if create_examples == 'y':
            try:
                create_example_data(data_dir)
                print("   ✅ Example data files created")
                return True
            except Exception as e:
                print(f"   ❌ Failed to create examples: {e}")
                return False
        else:
            print("   ❌ Cannot start without data files")
            return False
    
    return True


def create_example_data(data_dir):
    """Create example data files."""
    import pandas as pd
    
    # Ensure data directory exists
    data_dir.mkdir(exist_ok=True)
    
    # Create example vendor order data
    order_data = {
        'vendor_code': [f'V{i:03d}' for i in range(1, 26)],
        'vendor_name': [f'Tehran Vendor {i}' for i in range(1, 26)],
        'total_order_count': [800 + i * 75 for i in range(25)],
        'organic_order_count': [400 + i * 35 for i in range(25)],
        'non_organic_order_count': [400 + i * 40 for i in range(25)],
        'organic_to_non_organic_ratio': [0.8 + i * 0.05 for i in range(25)],
        'avg_daily_orders': [25 + i * 3 for i in range(25)]
    }
    pd.DataFrame(order_data).to_excel(data_dir / 'vendor_order_info.xlsx', index=False)
    
    # Create example geo data
    geo_data = {
        'vendor_code': [f'V{i:03d}' for i in range(1, 26)],
        'vendor_name': [f'Tehran Vendor {i}' for i in range(1, 26)],
        'latitude': [35.6892 + (i % 6) * 0.015 - 0.04 for i in range(25)],
        'longitude': [51.3890 + (i % 5) * 0.020 - 0.04 for i in range(25)]
    }
    pd.DataFrame(geo_data).to_excel(data_dir / 'vendor_geo_info.xlsx', index=False)
    
    # Create example polygon data
    polygon_data = {
        'name': ['North Tehran', 'Central Tehran', 'South Tehran'],
        'WKT': [
            'POLYGON((51.35 35.72, 51.45 35.72, 51.45 35.80, 51.35 35.80, 51.35 35.72))',
            'POLYGON((51.35 35.68, 51.45 35.68, 51.45 35.72, 51.35 35.72, 51.35 35.68))',
            'POLYGON((51.35 35.64, 51.45 35.64, 51.45 35.68, 51.35 35.68, 51.35 35.64))'
        ]
    }
    pd.DataFrame(polygon_data).to_csv(data_dir / 'tehran_polygons.csv', index=False)


def start_application():
    """Start the Flask application."""
    print("\n🚀 Starting Application:")
    
    # Check if app.py exists
    if not Path("app.py").exists():
        print("   ❌ app.py not found")
        return False
    
    print("   🌐 Initializing web server...")
    print("   ⏳ This may take a moment...")
    
    try:
        # Import and start the app
        os.environ['FLASK_ENV'] = 'development'
        
        # Try to import the app to check for errors
        sys.path.insert(0, str(Path.cwd()))
        from app import main
        
        print("   ✅ Application loaded successfully")
        print("\n" + "="*60)
        print("🎉 READY TO LAUNCH!")
        print("="*60)
        print("📍 The application will open in your browser")
        print("🌍 Share the network URL with your team")
        print("🛑 Press Ctrl+C in this window to stop the server")
        print("="*60)
        
        # Small delay for user to read
        time.sleep(2)
        
        # Start the application
        main()
        
    except ImportError as e:
        print(f"   ❌ Failed to import app: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Failed to start: {e}")
        return False
    
    return True


def main():
    """Main function."""
    print_banner()
    
    # System compatibility check
    if not check_system():
        print("\n❌ System compatibility check failed")
        input("Press Enter to exit...")
        sys.exit(1)
    
    # Install requirements
    if not install_requirements():
        print("\n❌ Failed to install requirements")
        input("Press Enter to exit...")
        sys.exit(1)
    
    # Check data files
    if not check_data_files():
        print("\n❌ Data files check failed")
        input("Press Enter to exit...")
        sys.exit(1)
    
    # Start application
    try:
        start_application()
    except KeyboardInterrupt:
        print("\n\n🛑 Application stopped by user")
        print("👋 Thank you for using Tehran Vendor Map!")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        input("Press Enter to exit...")


if __name__ == "__main__":
    main()
