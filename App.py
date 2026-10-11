import streamlit as st
import requests
st.title("Earthquake Detection System")
st.write("Live Earthquake Data from USGS")
url = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/2.5_day.geojson"
response = requests.get(url)
data = response.json()
st.header("Latest Earthquakes (Last 24 Hours)")
st.write(f"Total: {len(data['features'])}")
for quake in data['features'][:10]:
    mag = quake['properties']['mag']
    place = quake['properties']['place']
    if mag >= 5:
        st.error(f"Magnitude {mag} | {place}")
    elif mag >= 4:
        st.warning(f"Magnitude {mag} | {place}")
    else:
        st.success(f"Magnitude {mag} | {place}")
