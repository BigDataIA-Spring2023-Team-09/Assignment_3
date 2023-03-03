import io
from urllib import response
import folium
import requests
import streamlit as st
import pandas as pd

# To facilitate folium support with streamlit package
import streamlit_folium as stf

#To suppress future warnings in python pandas package
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

BASE_URL = "http://localhost:8090"

if 'access_token' not in st.session_state:
    st.session_state.access_token = ''

def mapping(my_token):

    # Make a request to the endpoint to check if call limit has exceeded
    username_response = (requests.post(BASE_URL + f'/check-users-api-record?username={st.session_state.username}')).json()
    status = username_response["user"]

    if (status):

        headers = {"Authorization": f"Bearer {my_token}"}
        st.header(':blue[Operational locations of NEXRAD sites]')
        with st.spinner('Refreshing map...'):
            # Make request to FastAPI endpoint and get CSV string
            response = requests.get("http://localhost:8090/mapping-stations", headers=headers)
            csv_string = response.content.decode("utf-8")

            # Convert CSV string to DataFrame
            sat_data = pd.read_csv(io.StringIO(csv_string))

            satellite = folium.map.FeatureGroup()
            latitudes=[]
            longitudes=[]
            labels=[]
            for index, row in sat_data.iterrows():
                satellite.add_child(
                        folium.features.CircleMarker(
                            [row['column1'], row['column2']],
                            radius=5, # define how big you want the circle markers to be
                            color='yellow',
                            fill=True,
                            fill_color='blue',
                            fill_opacity=0.6
                        )
                    )
                latitudes.append(row['column1'])
                longitudes.append(row['column2'])
                labels.append(row['column3'])
            
            # create map with a default starting location
            satellite_map = folium.Map(location=[37.6, -95.665], zoom_start=3)

            # add pop-up text to each marker on the map
            for lat, lng, label in zip(latitudes, longitudes, labels):
                folium.Marker([lat, lng], popup=label).add_to(satellite_map)    

            # add satellite to map and display it using streamlit-folium package
            satellite_map.add_child(satellite)
            stf.st_folium(satellite_map, width=700, height=460)
            st.text("Click on marker to view city name!")

        requests.post(BASE_URL + f'/check-users-api-record?url="/mapping-stations"&response="http"&username={st.session_state.username}')

    else:
        st.text("User limit reached! Please try later.")

if "access_token" not in st.session_state or st.session_state['access_token']=='':
    st.title("Please sign-in to access this feature!")
else:
    mapping(st.session_state["access_token"])