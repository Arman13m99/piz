# 🚀 Tehran Vendor Map - Live Web Application Setup Guide

This guide will help you set up and run the enhanced Tehran Vendor Mapping application as a live web server that runs on your local IP address.

## 📁 Required Directory Structure

Create this folder structure in your project directory:

```
tehran-vendor-mapping/
├── app.py                           # 🌐 Main Flask web application
├── start_server.py                  # 🚀 Easy startup script
├── requirements.txt                 # 📦 Python dependencies
├── config.py                        # ⚙️ Configuration settings
├── setup_guide.md                   # 📖 This setup guide
│
├── data/                            # 📊 Your data files go here
│   ├── vendor_order_info.xlsx      # Your vendor order data
│   ├── vendor_geo_info.xlsx        # Your vendor location data
│   └── tehran_polygons.csv         # Your marketing area polygons
│
├── templates/                       # 🎨 HTML templates
│   └── index.html                   # Main web interface
│
├── modules/                         # 🏗️ Core application modules
│   ├── __init__.py
│   ├── data_processor.py           # Data processing module
│   └── web_map_generator.py        # Web map generation
│
├── static/                          # 📱 Static files (CSS, JS, images)
│   ├── css/
│   ├── js/
│   └── images/
│
└── logs/                           # 📝 Application logs
```

## 🛠️ Quick Setup (2 Minutes)

### Option 1: Automatic Setup
```bash
# 1. Download all files to a folder
# 2. Run the startup script - it will do everything automatically!
python start_server.py
```

The startup script will:
- ✅ Check Python version
- ✅ Install requirements automatically
- ✅ Create missing directories
- ✅ Check for data files
- ✅ Create example data if needed
- ✅ Start the web server

### Option 2: Manual Setup
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Create directories
mkdir data templates modules static logs

# 3. Add your data files to the data/ directory

# 4. Start the application
python app.py
```

## 📊 Data Files

### Required Files in `data/` Directory:

#### 1. `vendor_order_info.xlsx`
```
vendor_code | vendor_name | total_order_count | organic_order_count | non_organic_order_count | organic_to_non_organic_ratio | avg_daily_orders
V001        | Vendor A    | 1250             | 800                 | 450                     | 1.78                        | 41.7
V002        | Vendor B    | 890              | 320                 | 570                     | 0.56                        | 29.7
```

#### 2. `vendor_geo_info.xlsx`
```
vendor_code | vendor_name | latitude  | longitude
V001        | Vendor A    | 35.6892   | 51.3890
V002        | Vendor B    | 35.7219   | 51.3347
```

#### 3. `tehran_polygons.csv`
```
name          | WKT
District 1    | POLYGON((51.2 35.6, 51.4 35.6, 51.4 35.8, 51.2 35.8, 51.2 35.6))
District 2    | POLYGON((51.4 35.6, 51.6 35.6, 51.6 35.8, 51.4 35.8, 51.4 35.6))
```

## 🌐 Starting the Application

### Easy Start (Recommended)
```bash
python start_server.py
```

### Manual Start
```bash
python app.py
```

### What You'll See:
```
🌐 Starting web server...
📍 Local Access: http://localhost:5000
🌍 Network Access: http://192.168.1.100:5000

✨ Features Available:
   🎯 Real-time vendor filtering
   📊 Live statistics dashboard
   🏆 Dynamic rankings by multiple criteria
   🌙 Light/Dark theme toggle
   📱 Mobile responsive design
   💾 Data export capabilities
```

## 🎯 Using the Application

### For You (Application Owner):
1. Start the server using `python start_server.py`
2. Share the **Network Access URL** with your team
3. Everyone can access it from their browsers
4. Changes update in real-time across all connected users

### For End Users:
1. Open the provided URL in any web browser
2. **No software installation needed**
3. Use the intuitive interface:
   - **Search vendors** by name or code
   - **Filter by performance** (high volume, overlapping)
   - **Hide/show vendors** with checkboxes
   - **Switch ranking criteria** with tabs
   - **Toggle themes** with the theme button
   - **Export data** for further analysis

## 🎨 Key Features

### 🎯 **Real-time Vendor Selection**
- **Smart search**: Find vendors instantly
- **Performance filters**: Show only high-volume or overlapping vendors
- **Bulk selection**: Select multiple vendors with checkboxes
- **Live updates**: Changes apply immediately across all users

### 📊 **Live Analytics Dashboard**
- **Real-time metrics**: Vendor count, overlap rate, performance scores
- **Visual indicators**: Progress bars and color-coded metrics
- **Auto-refresh**: Statistics update every 30 seconds

### 🏆 **Dynamic Rankings**
- **Multiple criteria**: Total Orders, Organic Orders, Daily Average, etc.
- **Color-coded markers**: Each ranking has its own color scheme
- **Instant switching**: Change rankings with a single click
- **Real-time updates**: Rankings recalculate based on visible vendors

### 🌙 **Theme Toggle**
- **Light/Dark themes**: Toggle between themes instantly
- **Saved preferences**: Theme choice is remembered
- **System-wide**: Affects all panels and components

### 📱 **Mobile Responsive**
- **Works on all devices**: Phones, tablets, laptops
- **Touch-friendly**: Large buttons and intuitive gestures
- **Adaptive layout**: Interface adjusts to screen size

## ⚙️ Configuration

Edit `config.py` to customize:

```python
# Service radius (in meters)
SERVICE_RADIUS = 3000  # 3km

# Map center (Tehran coordinates)
MAP_CENTER = [35.6892, 51.3890]

# Ranking criteria colors
RANK_COLORS = {
    "Total Orders": "#6A0DAD",     # Purple
    "Organic Orders": "#228B22",   # Green
    # ... customize as needed
}

# Feature toggles
ENABLE_THEME_SWITCHER = True
ENABLE_REAL_TIME_UPDATES = True
ENABLE_MOBILE_RESPONSIVE = True
```

## 🔧 Advanced Usage

### Running on Different Port
```bash
# Set custom port
export FLASK_PORT=8080
python app.py
```

### Production Deployment
```bash
# Install production server
pip install gunicorn

# Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Enabling HTTPS
```bash
# Generate self-signed certificate
openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365

# Run with HTTPS
python app.py --ssl-context adhoc
```

## 🚨 Troubleshooting

### Common Issues:

**1. "Port already in use"**
```bash
# Check what's using the port
netstat -tulpn | grep :5000

# Kill the process or use different port
python start_server.py  # Auto-finds available port
```

**2. "Module not found"**
```bash
# Install missing modules
pip install -r requirements.txt

# Or install individually
pip install flask pandas geopandas folium flask-cors
```

**3. "Data files not found"**
- Check that files are in the `data/` directory
- Verify file names match exactly
- Use the startup script to create example files

**4. "Map doesn't load"**
- Check browser console for errors (F12)
- Verify data has valid coordinates
- Ensure vendor codes match between files

**5. "Real-time updates not working"**
- Check network connectivity
- Verify JavaScript is enabled
- Look for CORS errors in browser console

### Network Issues:

**Can't access from other devices:**
```bash
# Check firewall settings
# Windows: Allow Python through Windows Firewall
# Mac: System Preferences > Security & Privacy > Firewall
# Linux: sudo ufw allow 5000
```

**Slow performance:**
```bash
# Reduce data size in config.py
MAX_VENDORS_FOR_OVERLAP = 100

# Disable expensive features
ENABLE_REAL_TIME_UPDATES = False
```

## 📈 Performance Tips

### For Large Datasets:
1. **Filter data** before loading (edit `data_processor.py`)
2. **Reduce overlap calculations** (set `MAX_VENDORS_FOR_OVERLAP`)
3. **Use caching** (install Redis and enable Flask-Caching)
4. **Optimize database queries** (if using database)

### For Many Users:
1. **Use production server** (Gunicorn with multiple workers)
2. **Enable caching** (Flask-Caching with Redis)
3. **Use reverse proxy** (nginx for static files)
4. **Monitor resources** (check CPU/memory usage)

## 🔒 Security Considerations

### For Internal Use:
- Use behind company firewall
- No external access needed
- Default security settings are adequate

### For External Access:
```bash
# Install security extensions
pip install Flask-Talisman Flask-Limiter

# Enable in app.py
from flask_talisman import Talisman
from flask_limiter import Limiter
```

## 🎓 Training End Users

### Share This Quick Guide:

**For End Users:**
1. **Access**: Open the provided URL in any browser
2. **Search**: Type in the search box to find specific vendors
3. **Filter**: Use filter buttons for quick vendor groups
4. **Select**: Check boxes next to vendors you want to hide
5. **Apply**: Click "Apply" to update the map
6. **Rankings**: Click ranking tabs to change vendor ordering
7. **Theme**: Click the moon/sun button to change themes
8. **Export**: Use the data table to export information

**No Technical Knowledge Required!**

## 📞 Support

### Self-Help:
1. Check this setup guide
2. Look at browser console (F12) for errors
3. Verify data file formats
4. Restart the application

### Getting Help:
1. Check the application logs in the `logs/` directory
2. Share error messages and steps to reproduce
3. Include your operating system and Python version
4. Describe what you expected vs. what happened

---

**Ready to start? Run `python start_server.py` and you'll be up and running in minutes!** 🚀