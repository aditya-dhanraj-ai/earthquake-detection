# 🌍 Earthquake Detection System

A real-time, AI-powered earthquake monitoring and analysis web application using USGS live data.

## 🚀 Features

- 📊 **Live Earthquake Data** - Real-time from USGS API
- 🤖 **AI Risk Prediction** - Random Forest classifier for HIGH/MEDIUM/LOW risk
- 📈 **Live Seismic Signal** - Real-time waveform visualization
- 🗺️ **Interactive World Map** - All earthquakes with magnitude
- 📊 **Magnitude Distribution** - Bar chart analysis
- 🏆 **Top 10 Strongest** - Ranking of largest earthquakes
- 🌐 **Country Filter** - Select any country with flag
- 🎚️ **Magnitude Filter** - Range slider
- 🕳️ **Depth Filter** - Shallow vs deep earthquakes
- ⏰ **Time Range Filter** - Last 1/6/12/24 hours
- 🛰️ **Satellite View** - Location-specific satellite imagery
- 📸 **Location Photos** - Country photos with flags
- 🚨 **Alert System** - Auto alert for magnitude 5+ events
- 🔒 **Admin Panel** - Password-protected controls
- 📥 **CSV Export** - Download earthquake data
- ⚡ **Auto-Refresh** - Updates every 30 seconds

## 🛠️ Tech Stack

- **Python** - Core language
- **Streamlit** - Web framework
- **Scikit-Learn** - Machine Learning (Random Forest)
- **Plotly** - Interactive charts
- **Pandas** - Data handling
- **NumPy** - Numerical computing
- **Matplotlib** - Seismic signal visualization
- **USGS API** - Real-time earthquake data
- **Esri Satellite** - Satellite imagery
- **country_converter** - Country flag emojis

## 🤖 AI Model

- **Algorithm:** Random Forest Classifier
- **Trees:** 100
- **Features:** Magnitude, Depth, Latitude, Longitude
- **Output:** Risk Classification (HIGH / MEDIUM / LOW) with confidence score
- **Risk Score:** 0-100 scale based on magnitude and depth

## 🔗 Live Demo

🌍 **[Click here to view the Live App]( https://earthquake-detection-db80.onrender.com)**

## 📄 Research Paper

Published on Zenodo (Open Access): 
**[Real-Time Earthquake Detection and Risk Classification](https://doi.org/10.5281/zenodo.23410853)**

DOI: `10.5281/zenodo.23410853`

## 📊 Data Source

Data is fetched in real-time from [USGS Earthquake Hazards Program](https://earthquake.usgs.gov/)

## 👨‍💻 Developer

**Aditya Dhanraj**  
BCA Student | Aspiring ML Engineer

---

*Built with ❤️ for Hokkaido University MEXT Application*

## 📦 Installation

```bash
pip install -r requirements.txt
streamlit run App.py
