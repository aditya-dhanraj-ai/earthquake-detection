import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import country_converter as coco
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np

st.set_page_config(page_title="Earthquake Detection", page_icon="🌍", layout="wide")

st.markdown('<meta http-equiv="refresh" content="30">', unsafe_allow_html=True)

st.markdown("""
<style>
    .stApp {background: linear-gradient(180deg, #0e1117 0%, #1a1f2e 100%);}
    h1 {color: #ff4b4b; text-align: center;}
    .quake-card {
        padding: 15px; border-radius: 10px; margin: 8px 0;
        background: linear-gradient(90deg, #1e2530 0%, #2a3441 100%);
        border-left: 4px solid #ff4b4b;
    }
    .admin-box {
        background: #1e2530; padding: 20px; border-radius: 15px;
        border: 2px solid #ff4b4b; margin: 20px 0;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1>🌍 Earthquake Detection System</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#888;'>Real-time Seismic Monitoring</p>", unsafe_allow_html=True)
st.markdown("---")

url = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/2.5_day.geojson"
data = requests.get(url).json()

quakes = []
for q in data['features']:
    place = q['properties']['place']
    country = place.split(',')[-1].strip() if ',' in place else "Unknown"
    time_ms = q['properties']['time']
    time_readable = datetime.fromtimestamp(time_ms / 1000).strftime('%d-%m-%Y %H:%M:%S')

    quakes.append({
        'magnitude': q['properties']['mag'],
        'place': place,
        'country': country,
        'depth': q['geometry']['coordinates'][2],
        'lat': q['geometry']['coordinates'][1],
        'lon': q['geometry']['coordinates'][0],
        'time': time_readable
    })

df = pd.DataFrame(quakes)

def get_flag_url(country_name):
    try:
        iso = coco.convert(names=country_name, to='ISO2')
        if iso == 'not found' or len(iso) != 2:
            return None
        return f"https://flagcdn.com/48x36/{iso.lower()}.png"
    except:
        return None

def get_wiki_photo(place_name):
    try:
        country = place_name.split(',')[-1].strip()
        country_clean = country.replace("'", "").replace("-", " ").replace(" ", "")

        for term in [country_clean, country.replace(" ", ""), "landscape"]:
            try:
                url = f"https://loremflickr.com/800/500/{term}"
                response = requests.get(url, timeout=15, allow_redirects=True)
                if response.status_code == 200 and len(response.content) > 10000:
                    return response.content
            except:
                continue
        return None
    except:
        return None

def get_satellite_url(lat, lon):
    return f"https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/export?bbox={lon-0.5},{lat-0.5},{lon+0.5},{lat+0.5}&bboxSR=4326&imageSR=4326&size=800,500&f=image&format=png"

st.sidebar.header("🎯 Filters")

countries = ["All Countries"] + sorted(df['country'].unique().tolist())
countries_display = ["All Countries"] + countries[1:]

selected = st.sidebar.selectbox("Select Country", countries_display)

if selected != "All Countries":
    flag_url_sidebar = get_flag_url(selected)
    if flag_url_sidebar:
        st.sidebar.markdown(
            f'<div style="text-align:center; margin-top:-10px; margin-bottom:10px;">'
            f'<img src="{flag_url_sidebar}" style="width:60px; border-radius:5px; box-shadow:0 0 10px rgba(255,75,75,0.5);">'
            f'</div>',
            unsafe_allow_html=True
        )

min_mag = st.sidebar.slider("Minimum Magnitude", 2.5, 7.0, 2.5, 0.1)

min_depth, max_depth = st.sidebar.slider(
    "Depth Range (km)",
    min_value=0, max_value=700,
    value=(0, 700)
)

time_range = st.sidebar.selectbox(
    "Time Range",
    ["Last 1 Hour", "Last 6 Hours", "Last 12 Hours", "Last 24 Hours"]
)

hours_map = {"Last 1 Hour": 1, "Last 6 Hours": 6, "Last 12 Hours": 12, "Last 24 Hours": 24}
hours = hours_map[time_range]
cutoff_time = datetime.now() - pd.Timedelta(hours=hours)
df['datetime'] = pd.to_datetime(df['time'], format='%d-%m-%Y %H:%M:%S')
time_filtered = df[df['datetime'] >= cutoff_time]

if selected == "All Countries":
    filtered = time_filtered[(time_filtered['magnitude'] >= min_mag) & (time_filtered['depth'] >= min_depth) & (time_filtered['depth'] <= max_depth)]
else:
    filtered = time_filtered[(time_filtered['country'] == selected) & (time_filtered['magnitude'] >= min_mag) & (time_filtered['depth'] >= min_depth) & (time_filtered['depth'] <= max_depth)]

st.sidebar.markdown("---")
st.sidebar.header("🔒 Admin Login")

ADMIN_PASSWORD = "aditya2026"

password = st.sidebar.text_input("Enter Admin Password", type="password")

if password == ADMIN_PASSWORD:
    st.sidebar.success("✅ Admin Logged In")
    is_admin = True
elif password == "":
    is_admin = False
else:
    st.sidebar.error("❌ Wrong Password")
    is_admin = False

major_quakes = df[df['magnitude'] >= 5.0]
if len(major_quakes) > 0:
    st.markdown(f"""
    <div style="background: linear-gradient(90deg, #ff0000 0%, #8b0000 100%);
                padding: 20px; border-radius: 15px; margin: 20px 0;
                animation: pulse 2s infinite; border: 2px solid #ff4b4b;">
        <h2 style="color: white; margin: 0;">🚨 ALERT: {len(major_quakes)} Major Earthquake(s) Detected!</h2>
        <p style="color: #ffcccc; margin: 5px 0 0 0;">Magnitude 5.0+ events in last 24 hours</p>
    </div>
    <style>
    @keyframes pulse {{
        0% {{ opacity: 1; }}
        50% {{ opacity: 0.7; }}
        100% {{ opacity: 1; }}
    }}
    </style>
    """, unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["📊 Live Data", "📸 Photos", "🛰️ Satellite"])

with tab1:
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Earthquakes", len(filtered))
    with col2:
        st.metric("Max Magnitude", f"{filtered['magnitude'].max():.1f}" if len(filtered) > 0 else "0")
    with col3:
        st.metric("Avg Magnitude", f"{filtered['magnitude'].mean():.2f}" if len(filtered) > 0 else "0")
    with col4:
        st.metric("Avg Depth (km)", f"{filtered['depth'].mean():.1f}" if len(filtered) > 0 else "0")

    st.markdown("---")

    st.subheader("📈 Live Seismic Signal (Simulated)")
    t = np.linspace(0, 10, 1000)
    signal = (2.0 * np.sin(2 * np.pi * 1 * t) +
              1.5 * np.sin(2 * np.pi * 3 * t) +
              0.5 * np.random.randn(len(t)))

    fig_sig, ax = plt.subplots(figsize=(12, 3))
    fig_sig.patch.set_facecolor('#0e1117')
    ax.set_facecolor('#1e2530')
    ax.plot(t, signal, color='#ff4b4b', linewidth=1)
    ax.set_xlabel("Time (seconds)", color='white')
    ax.set_ylabel("Amplitude", color='white')
    ax.set_title("Earthquake Signal - Seismic Waveform", color='white')
    ax.tick_params(colors='white')
    ax.grid(True, alpha=0.3)
    for spine in ax.spines.values():
        spine.set_color('white')
    st.pyplot(fig_sig)

    st.markdown("---")

    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("📊 Magnitude Distribution")
        if len(filtered) > 0:
            fig = px.histogram(filtered, x='magnitude', nbins=15, color_discrete_sequence=['#ff4b4b'])
            fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                              font_color='white', height=400)
            st.plotly_chart(fig, use_container_width=True)

    with col_right:
        st.subheader("🗺️ Earthquake Map")
        if len(filtered) > 0:
            fig2 = px.scatter_geo(filtered, lat='lat', lon='lon', size='magnitude',
                                  color='magnitude', hover_name='place',
                                  color_continuous_scale='Reds', projection='natural earth')
            fig2.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                               font_color='white', height=400)
            st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")

    st.subheader("🏆 Top 10 Strongest Earthquakes")
    if len(filtered) > 0:
        top10 = filtered.nlargest(10, 'magnitude')
        fig3 = px.bar(top10, x='magnitude', y='place', orientation='h',
                      color='magnitude', color_continuous_scale='Reds')
        fig3.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                           font_color='white', height=400)
        st.plotly_chart(fig3, use_container_width=True)

    st.markdown("---")

    if selected != "All Countries":
        flag_url_header = get_flag_url(selected)
        if flag_url_header:
            st.markdown(
                f'<div style="display:flex; align-items:center; margin-bottom:10px;">'
                f'<img src="{flag_url_header}" style="width:45px; margin-right:15px; border-radius:5px;">'
                f'<h2 style="color:#ff4b4b; margin:0;">Live Earthquakes — {selected}</h2>'
                f'</div>',
                unsafe_allow_html=True
            )
        else:
            st.subheader(f"🔴 Live Earthquakes — {selected}")
    else:
        st.subheader(f"🔴 Live Earthquakes — {selected}")

    if len(filtered) == 0:
        st.info("No earthquakes match your filters")
    else:
        for _, row in filtered.head(15).iterrows():
            mag = row['magnitude']
            if mag >= 5:
                color, icon = "#ff0000", "🔴"
            elif mag >= 4:
                color, icon = "#ff8c00", "🟠"
            else:
                color, icon = "#00c853", "🟢"

            st.markdown(f"""
            <div class="quake-card" style="border-left-color: {color};">
                <span style="color:{color}; font-weight:bold; font-size:1.2rem;">
                    {icon} Magnitude {mag:.1f}
                </span>
                <span style="color:#ccc; margin-left:20px;">
                    📍 {row['place']} | Depth: {row['depth']:.1f} km
                </span>
                <br>
                <span style="color:#888; margin-left:0px; font-size:0.9rem;">
                    🕐 {row['time']}
                </span>
            </div>
            """, unsafe_allow_html=True)

with tab2:
    st.subheader("📸 Earthquake Location Photos")
    st.write("Select an earthquake location to see photos")

    if len(filtered) > 0:
        locations = filtered['place'].unique().tolist()
        selected_location = st.selectbox("Choose location:", locations)

        if st.button("🔍 Load Photos"):
            with st.spinner("Loading photos..."):
                row = filtered[filtered['place'] == selected_location].iloc[0]

                col1, col2 = st.columns([2, 1])

                with col1:
                    photo = get_wiki_photo(selected_location)
                    if photo:
                        country = selected_location.split(',')[-1].strip()
                        st.image(photo, caption=f"📸 Photo of {country}", use_column_width=True)
                    else:
                        st.info("Photo not available. Click below to search:")

                with col2:
                    st.markdown("### 🌍 Country Info")
                    country = selected_location.split(',')[-1].strip()
                    st.markdown(f"**Country:** {country}")

                    flag = get_flag_url(country)
                    if flag:
                        st.markdown(f'<img src="{flag}" style="width:100px; margin:10px 0;">', unsafe_allow_html=True)

                    st.markdown(f"**Magnitude:** {row['magnitude']}")
                    st.markdown(f"**Time:** {row['time']}")
                    st.markdown(f"**Depth:** {row['depth']} km")

                    google_link = f"https://www.google.com/search?tbm=isch&q={selected_location.replace(' ', '+')}"
                    st.markdown(f"[🔍 Search on Google Images]({google_link})")
    else:
        st.info("No earthquakes match your filters")

with tab3:
    st.subheader("🛰️ Satellite View")
    st.write("Select an earthquake to see satellite view with marker")

    if len(filtered) > 0:
        locations = filtered['place'].unique().tolist()
        selected_location = st.selectbox("Choose earthquake:", locations, key="sat")

        if st.button("🛰️ Load Satellite View"):
            with st.spinner("Loading satellite image..."):
                row = filtered[filtered['place'] == selected_location].iloc[0]
                sat_url = get_satellite_url(row['lat'], row['lon'])
                st.image(sat_url, caption=f"{row['place']} | Lat: {row['lat']:.2f}, Lon: {row['lon']:.2f}", use_column_width=True)
                st.markdown(f"**Location Details:**")
                st.write(f"- 🌐 Latitude: {row['lat']}")
                st.write(f"- 🌐 Longitude: {row['lon']}")
                st.write(f"- 📊 Magnitude: {row['magnitude']}")
                st.write(f"- 🕐 Time: {row['time']}")
                st.write(f"- 🌊 Depth: {row['depth']} km")
                st.markdown(f"[🔗 Open in Google Maps](https://www.google.com/maps?q={row['lat']},{row['lon']})")
    else:
        st.info("No earthquakes match your filters")

if is_admin:
    st.markdown("---")
    st.markdown("""
    <div class="admin-box">
        <h2 style="color:#ff4b4b;">🔒 Admin Panel</h2>
    </div>
    """, unsafe_allow_html=True)

    st.subheader("🎛️ Admin Controls")

    col_a, col_b, col_c = st.columns(3)

    with col_a:
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Full Data", csv, "all_earthquakes.csv", "text/csv")

    with col_b:
        if st.button("🔄 Refresh Data"):
            st.rerun()

    with col_c:
        st.write(f"Total records: {len(df)}")

    st.subheader("📊 Full Data Preview")
    st.dataframe(df)

st.markdown("---")
st.markdown("<p style='text-align:center; color:#555;'>Built with Streamlit • Powered by USGS</p>", unsafe_allow_html=True)
