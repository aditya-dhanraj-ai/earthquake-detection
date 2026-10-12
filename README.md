# 🌍 Earthquake Detection System

A real-time earthquake monitoring and analysis web application powered by USGS live data.

## 🚀 Features

- 📊 **Live Earthquake Data** - Real-time from USGS API
- 🗺️ **Interactive World Map** - All earthquakes with magnitude
- 📈 **Magnitude Distribution** - Bar chart analysis
- 🌐 **Country Filter** - Select any country with flag
- 🎚️ **Magnitude Filter** - Range slider
- 🛰️ **Satellite View** - Location-specific satellite imagery
- 🕐 **Timestamp Display** - When each earthquake occurred
- 🔒 **Admin Panel** - Password-protected controls
- 📥 **CSV Export** - Download earthquake data
- ⚡ **Auto-Refresh** - Updates every 30 seconds

## 🛠️ Tech Stack

- **Python** - Core language
- **Streamlit** - Web framework
- **Plotly** - Interactive charts
- **Pandas** - Data handling
- **USGS API** - Real-time earthquake data
- **Esri Satellite** - Satellite imagery
- **country_converter** - Country flag emojis

## 📦 Installation

```bash
pip install -r requirements.txt
streamlit run App.py
