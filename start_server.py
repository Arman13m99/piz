#!/usr/bin/env python3
"""
Tehran Vendor Mapping - Server Startup Script
Easy startup script with automatic setup and configuration.
"""

import os
import sys
import subprocess
import socket
from pathlib import Path


def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8 or higher is required")
        print(f"   Current version: {sys.version}")
        return False
    return True


def check_and_install_requirements():
    """Check and install required packages."""
    print("📦 Checking requirements...")
    
    try:
        import flask
        import pandas
        import geopandas
        import folium
        print("✅ All required packages are installed")
        return True
    except ImportError as e:
        print(f"⚠️  Missing package: {e.name}")
        print("🔄 Installing requirements...")
        
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
            print("✅ Requirements installed successfully")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install requirements")
            print("   Please run manually: pip install -r requirements.txt")
            return False


def setup_directories():
    """Setup required directories."""
    print("📁 Setting up directories...")
    
    directories = [
        'data',
        'templates',
        'modules',
        'static',
        'logs'
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    
    print("✅ Directories created")


def check_data_files():
    """Check if required data files exist."""
    print("🔍 Checking data files...")
    
    required_files = [
        'data/vendor_order_info.xlsx',
        'data/vendor_geo_info.xlsx',
        'data/tehran_polygons.csv'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
        else:
            print(f"   ✅ Found: {file_path}")
    
    if missing_files:
        print("⚠️  Missing data files:")
        for file in missing_files:
            print(f"   ❌ {file}")
        print("\n📋 Please add your data files to the 'data' directory:")
        print("   1. vendor_order_info.xlsx - Your vendor order data")
        print("   2. vendor_geo_info.xlsx - Your vendor location data")
        print("   3. tehran_polygons.csv - Your marketing area polygons")
        return False
    
    print("✅ All data files found")
    return True


def get_available_port(start_port=5000):
    """Find an available port starting from start_port."""
    for port in range(start_port, start_port + 100):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                return port
        except OSError:
            continue
    return None


def get_local_ip():
    """Get the local IP address."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except:
        return "127.0.0.1"


def create_example_data():
    """Create example data files if they don't exist."""
    import pandas as pd
    
    data_dir = Path('data')
    
    # Create example vendor_order_info.xlsx
    order_file = data_dir / 'vendor_order_info.xlsx'
    if not order_file.exists():
        print("📝 Creating example order data...")
        order_data = {
            'vendor_code': [f'V{i:03d}' for i in range(1, 21)],
            'vendor_name': [f'Vendor {i}' for i in range(1, 21)],
            'total_order_count': [1000 + i * 50 for i in range(20)],
            'organic_order_count': [500 + i * 25 for i in range(20)],
            'non_organic_order_count': [500 + i * 25 for i in range(20)],
            'organic_to_non_organic_ratio': [1.0 + i * 0.1 for i in range(20)],
            'avg_daily_orders': [30 + i * 2 for i in range(20)]
        }
        pd.DataFrame(order_data).to_excel(order_file, index=False)
    
    # Create example vendor_geo_info.xlsx
    geo_file = data_dir / 'vendor_geo_info.xlsx'
    if not geo_file.exists():
        print("📝 Creating example geo data...")
        geo_data = {
            'vendor_code': [f'V{i:03d}' for i in range(1, 21)],
            'vendor_name': [f'Vendor {i}' for i in range(1, 21)],
            'latitude': [35.6892 + (i % 5) * 0.01 for i in range(20)],
            'longitude': [51.3890 + (i % 4) * 0.01 for i in range(20)]
        }
        pd.DataFrame(geo_data).to_excel(geo_file, index=False)
    
    # Create example tehran_polygons.csv
    polygon_file = data_dir / 'tehran_polygons.csv'
    if not polygon_file.exists():
        print("📝 Creating example polygon data...")
        polygon_data = {
            'name': ['District 1', 'District 2'],
            'WKT': [
                'POLYGON((51.3 35.6, 51.4 35.6, 51.4 35.7, 51.3 35.7, 51.3 35.6))',
                'POLYGON((51.4 35.6, 51.5 35.6, 51.5 35.7, 51.4 35.7, 51.4 35.6))'
            ]
        }
        pd.DataFrame(polygon_data).to_csv(polygon_file, index=False)


def main():
    """Main startup function."""
    print("\n" + "="*70)
    print("🚀 TEHRAN VENDOR MAPPING - LIVE WEB APPLICATION STARTUP")
    print("="*70)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Setup directories
    setup_directories()
    
    # Check and install requirements
    if not check_and_install_requirements():
        sys.exit(1)
    
    # Check data files or create examples
    if not check_data_files():
        create_example = input("\n❓ Would you like to create example data files? (y/n): ").strip().lower()
        if create_example == 'y':
            try:
                create_example_data()
                print("✅ Example data files created successfully!")
                print("📋 You can replace these with your actual data files.")
            except Exception as e:
                print(f"❌ Error creating example data: {e}")
                sys.exit(1)
        else:
            print("❌ Cannot start without data files. Please add your data files and restart.")
            sys.exit(1)
    
    # Find available port
    port = get_available_port()
    if port is None:
        print("❌ No available ports found")
        sys.exit(1)
    
    # Get local IP
    local_ip = get_local_ip()
    
    print(f"\n🌐 Starting Tehran Vendor Map Server...")
    print(f"📍 Local Access: http://localhost:{port}")
    print(f"🌍 Network Access: http://{local_ip}:{port}")
    print(f"\n✨ Features Available:")
    print(f"   🎯 Real-time vendor filtering")
    print(f"   📊 Live statistics dashboard")
    print(f"   🏆 Dynamic rankings by multiple criteria")
    print(f"   🌙 Light/Dark theme toggle")
    print(f"   📱 Mobile responsive design")
    print(f"   💾 Data export capabilities")
    print(f"\n⚡ The map updates live as you make changes!")
    print(f"🛑 Press Ctrl+C to stop the server")
    print("="*70)
    
    # Set environment variables
    os.environ['FLASK_ENV'] = 'development'
    os.environ['FLASK_DEBUG'] = 'True'
    
    try:
        # Import and run the app
        from app import app
        app.run(
            host='0.0.0.0',
            port=port,
            debug=True,
            threaded=True
        )
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped by user.")
        print("👋 Thanks for using Tehran Vendor Mapping!")
    except ImportError as e:
        print(f"\n❌ Error importing app: {e}")
        print("   Make sure app.py is in the current directory")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
