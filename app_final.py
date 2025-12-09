import streamlit as st
import folium
from streamlit_folium import st_folium
import requests
from io import BytesIO
from PIL import Image
import numpy as np

# -------------------- CONFIG --------------------------------------------------
st.set_page_config(
    page_title="La carte et le territoire",
    page_icon="🗺️",
    layout="wide"
)

MAPBOX_TOKEN = st.secrets["MAPBOX_TOKEN"]
MAPBOX_STYLE = "mapbox/satellite-v9" # Use a satellite style

# Define the initial map center and zoom
INITIAL_CENTER = [48.8566, 2.3522] # Example: Paris, France
INITIAL_ZOOM = 4

API_ENDPOINT = "http://localhost:8000/upload-and-process/" #"https://carte-territoire-24889736924.europe-west1.run.app/upload-and-process"
API_ENDPOINT_GET = "http://localhost:8000/" #"https://carte-territoire-24889736924.europe-west1.run.app/"

FLAIR_CLASS_DATA = {
0  : ['other','#000000'],
1   : ['building','#db0e9a'] ,
2   : ['pervious surface','#938e7b'],
3   : ['impervious surface','#f80c00'],
4   : ['swimming_pool','#3de6eb'],
5   : ['bare_soil','#a97101'],
6   : ['water','#1553ae'],
7   : ['snow','#ffffff'],
8   : ['coniferous','#194a26'],
9  : ['deciduous','#46e483'],
10  : ['brushwood','#f3a60d'],
11  : ['vineyard','#660082'],
12  : ['herbaceous vegetation','#55ff00'],
13  : ['agricultural land','#fff30d'],
14  : ['plowed land','#e4df7c'],
15  : ['greenhouse','#9999ff'],
}

# -------------------- STYLES --------------------------------------------------

st.markdown(
    """
    <style>
        .hero {
            text-align: center;
            padding: 3rem 1rem 2rem 1rem;
        }
        .hero h1 {
            font-size: 3rem;
        }
        .hero p {
            font-size: 1.2rem;
            color: #555;
        }
        .block {
            margin-top: 2rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# -------------------- HERO ----------------------------------------------------

st.markdown(
    """
    <div class="hero">
        <h1>🗺️ La carte et le territoire</h1>
        <p>
            Satellite landscapes explored through image processing !
        </p>
        <p>
            <strong>Le Wagon — Batch 2130</strong>
        </p>
        <p>
            <strong>Happily sponsored by the French public administration 😄</strong>
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# -------------------- IMAGE HANDLING (Mapbox/Folium Version) ------------------
# --- Initialize session state variables for management ------------------------
if "image_source" not in st.session_state:
    st.session_state.image_source = None  # 'upload' or 'map'
if "uploaded_file_object" not in st.session_state:
    st.session_state.uploaded_file_object = None
if "captured_image" not in st.session_state:
    st.session_state.captured_image = None
if "last_bbox" not in st.session_state:
    st.session_state.last_bbox = None

tab_upload, tab_map = st.tabs(["📂 Upload an image", "🌍 Explore the world"])
with tab_upload:
    st.info("Upload a satellite image")

    uploaded = st.file_uploader(
        "Use the button below",
        type=["png", "jpg", "jpeg"],
        key="file_uploader_key"
    )

    if uploaded and uploaded != st.session_state.uploaded_file_object:
        # Check if the image currently stored is from the map tab
        if st.session_state.image_source == 'map':
            st.session_state.captured_image = None # Clear map image

        # Process the new uploaded image
        image = Image.open(uploaded).convert("RGB")
        st.session_state.captured_image = image
        st.session_state.image_source = 'upload' # Set source flag
        st.session_state.uploaded_file_object = uploaded # Store the file object reference

        # Display image shape
        img_array = np.array(image)
        st.write(f'Image shape: {img_array.shape}')

with tab_map:
    st.info(
        "Browse and zoom in and out the map as you wish below to select an area, then click 'Capture View'."
    )

    # Initialize Folium Map
    m = folium.Map(
        location=INITIAL_CENTER,
        zoom_start=INITIAL_ZOOM,
        tiles=f"https://api.mapbox.com/styles/v1/{MAPBOX_STYLE}/tiles/{{z}}/{{x}}/{{y}}@2x?access_token={MAPBOX_TOKEN}",
        attr="Mapbox",
        control_scale=True,
        scrollWheelZoom=True
    )

    # Display the map and capture its state (bounding box and zoom)
    map_data = st_folium(m, width=700, height=500, key="folium_map", return_on_hover=False)

    if st.button("📸 Capture View"):
        if map_data and 'bounds' in map_data:
            # Check if the image currently stored is from the upload tab
            if st.session_state.image_source == 'upload':
                st.session_state.captured_image = None # Clear uploaded image

            # The 'bounds' dictionary contains the NorthEast (NE) and SouthWest (SW) corners
            # of the current map view (bounding box - bbox).
            sw_lat = map_data['bounds']['_southWest']['lat']
            sw_lon = map_data['bounds']['_southWest']['lng']
            ne_lat = map_data['bounds']['_northEast']['lat']
            ne_lon = map_data['bounds']['_northEast']['lng']
            bbox_string = f"{sw_lon},{sw_lat},{ne_lon},{ne_lat}"
            st.session_state.last_bbox = bbox_string

            # --- Static Images API Call ---
            image_width = 512
            image_height = 512
            static_api_url = f"https://api.mapbox.com/styles/v1/{MAPBOX_STYLE}/static/[{bbox_string}]/{image_width}x{image_height}?access_token={MAPBOX_TOKEN}&padding=0.1"

            with st.spinner("Fetching static map image..."):
                try:
                    response = requests.get(static_api_url)
                    response.raise_for_status()

                    image = Image.open(BytesIO(response.content)).convert("RGB")
                    st.session_state.captured_image = image
                    st.session_state.image_source = 'map' # Set source flag

                    st.success("✅ Map view captured!")

                    # Display image shape
                    img_array = np.array(image)
                    st.write(f'Image shape: {img_array.shape}')
                except requests.exceptions.RequestException as e:
                    st.error(f"Error fetching image from Mapbox API: {e}")
                    st.session_state.captured_image = None
        else:
            st.warning("Please interact with the map first to set the view.")

# -------------------- API CALL ------------------------------------------------

if st.session_state.captured_image:
    st.markdown("### ✅ Input image")
    # Display the captured image, this replaces the previous uploaded file display
    st.image(st.session_state.captured_image, use_container_width=False)

    if st.button("🚀 Send to API"):
        # Existing API logic
        buffer = BytesIO()
        st.session_state.captured_image.save(buffer, format="PNG")
        buffer.seek(0)

        files = {"file": ("input.png", buffer.read(), "image/png")}

        with st.spinner("Processing image..."):
            response = requests.post(API_ENDPOINT, files=files)

        if response.status_code == 200:
            output_image = Image.open(BytesIO(response.content))

            st.markdown("### 🖼️ Result")
            st.success("✅ Image successfully processed")

            col1, col2, col3 = st.columns([2, 2, 1])

            with col1:
                st.caption("Input image")
                st.image(st.session_state.captured_image, use_container_width=False)

            with col2:
                st.caption("Predicted label")
                st.image(output_image, use_container_width=False)

            with col3:
                st.caption("🗂️ Legend")

                try:
                    for _, (label, color) in FLAIR_CLASS_DATA.items():
                        st.markdown(
                            f"""
                            <div style="
                                display: flex;
                                align-items: center;
                                margin-bottom: 6px;
                            ">
                                <div style="
                                    width: 18px;
                                    height: 18px;
                                    background-color: {color};
                                    border: 1px solid #333;
                                    margin-right: 10px;
                                "></div>
                                <span>{label}</span>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                except NameError:
                    st.warning("FLAIR_CLASS_DATA is not defined to display the legend.")

        else:
            st.error(f"API error ({response.status_code}): {response.text}")
