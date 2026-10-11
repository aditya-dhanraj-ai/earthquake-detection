import streamlit as st
import requests
import pandas as pd
import plotly.express as px

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
    quakes.append({
        'magnitude': q['properties']['mag'],
        'place': place,
        'country': country,
        'depth': q['geometry']['coordinates'][2],
        'lat': q['geometry']['coordinates'][1],
        'lon': q['geometry']['coordinates'][0]
    })

df = pd.DataFrame(quakes)

st.sidebar.header("🎯 Filters")
# Country flags
flags = {
    "Japan": "🇯🇵", "Alaska": "🇺🇸", "Peru": "🇵🇪",
    "Papua New Guinea": "🇵🇬", "Russia": "🇷🇺", "Indonesia": "🇮🇩",
    "Chile": "🇨🇱", "Mexico": "🇲🇽", "California": "🇺🇸",
    "Philippines": "🇵🇭", "Argentina": "🇦🇷", "New Zealand": "🇳🇿",
}

def add_flag(country):
    flag = flags.get(country, "🌍")
    return f"{flag} {country}"

countries = ["All Countries"] + sorted(df['country'].unique().tolist())
countries_display = ["🌍 All Countries"] + [add_flag(c) for c in countries[1:]]

selected_display = st.sidebar.selectbox("Select Country", countries_display)
selected = selected_display.split(' ', 1)[1] if selected_display != "🌍 All Countries" else "All Countries"
selected = st.sidebar.selectbox("Select Country", countries)
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
        </div>
        """, unsafe_allow_html=True)


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
        if st.button("📥 Download Full Data"):
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("Click to Download", csv, "all_earthquakes.csv", "text/csv")
    
    with col_b:
        if st.button("🔄 Refresh Data"):
            st.rerun()
    
    with col_c:
        st.write(f"Total records: {len(df)}")
    
    st.subheader("📊 Full Data Preview")
    st.dataframe(df)

st.markdown("---")
st.markdown("<p style='text-align:center; color:#555;'>Built with Streamlit • Powered by USGS</p>", unsafe_allow_html=True)
