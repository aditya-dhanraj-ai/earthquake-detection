import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import country_converter as coco
from datetime import datetime

st.set_page_config(page_title="Earthquake Detection", page_icon="🌍", layout="wide")

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
        city = place_name.split(' of ')[-1].split(',')[0].strip()
        country = place_name.split(',')[-1].strip()
        country_map = {
            "Alaska": "Alaska", "California": "California", "CA": "California",
            "Japan": "Japan", "Peru": "Peru", "Indonesia": "Indonesia",
            "Russia": "Russia", "Chile": "Chile", "Mexico": "Mexico",
            "Papua New Guinea": "Papua_New_Guinea", "Philippines": "Philippines",
            "New Zealand": "New_Zealand", "Argentina": "Argentina",
            "Greece": "Greece", "Italy": "Italy", "Turkey": "Turkey",
            "Iran": "Iran", "India": "India", "Nepal": "Nepal",
            "Fiji": "Fiji", "Tonga": "Tonga", "Panama": "Panama",
            "Costa Rica": "Costa_Rica", "Guatemala": "Guatemala",
            "Vanuatu": "Vanuatu", "Solomon Islands": "Solomon_Islands",
        }
        country_wiki = country_map.get(country, country)
        
        for search_term in [city, country_wiki, place_name]:
            try:
                search_url = f"https://en.wikipedia.org/w/api.php?action=query&titles={search_term.replace(' ', '_')}&prop=pageimages&format=json&pithumbsize=800"
                response = requests.get(search_url).json()
                pages = response['query']['pages']
                for page_id in pages:
                    if 'thumbnail' in pages[page_id]:
                        return pages[page_id]['thumbnail']['source']
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

if selected == "All Countries":
    filtered = df[df['magnitude'] >= min_mag]
else:
    filtered = df[(df['country'] == selected) & (df['magnitude'] >= min_mag)]

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
                photo = get_wiki_photo(selected_location)
                if photo:
                    st.image(photo, caption=selected_location, use_column_width=True)
                else:
                    st.warning("No photo found for this location")
                    st.markdown(f"**Search on Google Images:** [Click here](https://www.google.com/search?tbm=isch&q={selected_location.replace(' ', '+')})")
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
