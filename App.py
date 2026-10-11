import streamlit as st
import requests

st.title("🌍 Earthquake Detection System")
st.write("Live Earthquake Data from USGS")


url = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/2.5_day.geojson"
response = requests.get(url)
data = response.json()


countries = set()
for quake in data['features']:
    place = quake['properties']['place']
   
    if ',' in place:
        country = place.split(',')[-1].strip()
        countries.add(country)

countries = sorted(list(countries))
countries.insert(0, "All Countries")

st.header("Select Country")
selected_country = st.selectbox("Choose a country:", countries)

st.header(f"Earthquakes: {selected_country}")
st.write(f"Total: {len(data['features'])}")

filtered_count = 0
for quake in data['features']:
    mag = quake['properties']['mag']
    place = quake['properties']['place']
    
    if selected_country == "All Countries":
        show = True
    else:
        if ',' in place:
            country = place.split(',')[-1].strip()
            show = (country == selected_country)
        else:
            show = False
    
    if show:
        filtered_count += 1
        if mag >= 5:
            st.error(f"🔴 Magnitude {mag} | {place}")
        elif mag >= 4:
            st.warning(f"🟠 Magnitude {mag} | {place}")
        else:
            st.success(f"🟢 Magnitude {mag} | {place}")

if filtered_count == 0:
    st.info(f"No earthquakes in {selected_country} in last 24 hours")
