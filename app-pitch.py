# # app.py
# import os
# import requests
# from io import BytesIO

# import numpy as np
# import pydeck as pdk
# import streamlit as st
# from PIL import Image

# st.set_page_config(page_title="Satellite Segmentation Demo", layout="wide")
# st.title("🌍 Satellite Image Segmentation Demo")


# # --------------------
# # Helper: get Mapbox token
# # --------------------
# def get_mapbox_token():
#     # Prefer Streamlit secrets, fall back to environment variable
#     if "MAPBOX_TOKEN" in st.secrets:
#         return st.secrets["MAPBOX_TOKEN"]
#     return os.getenv("MAPBOX_TOKEN")


# MAPBOX_TOKEN = get_mapbox_token()


# # --------------------
# # TABS: upload vs map snapshot
# # --------------------
# tab_upload, tab_map = st.tabs(["📂 Upload image", "🗺️ Pick area on map"])

# with tab_upload:
#     st.subheader("Upload a satellite image")

#     uploaded_file = st.file_uploader(
#         "Upload a satellite image",
#         type=["png", "jpg", "jpeg", "tif", "tiff"]
#     )

#     if uploaded_file is not None:
#         image = Image.open(uploaded_file)
#         st.image(image, caption="Uploaded satellite image", use_column_width=True)

#         img_array = np.array(image)
#         st.write("Image shape:", img_array.shape)

#         if st.button("Run model on uploaded image"):
#             # TODO: call your API here
#             st.write("👉 Here you would call your model API with `img_array`.")


# with tab_map:
#     st.subheader("Choose a location and take a satellite snapshot")

#     if MAPBOX_TOKEN is None:
#         st.warning(
#             "You need a Mapbox access token to use this feature. "
#             "Set `MAPBOX_TOKEN` in `.streamlit/secrets.toml` or as an environment variable."
#         )
#     else:
#         # Controls for map view
#         col1, col2, col3 = st.columns(3)
#         with col1:
#             lat = st.number_input("Latitude", value=48.8566)  # Paris by default
#         with col2:
#             lon = st.number_input("Longitude", value=2.3522)
#         with col3:
#             zoom = st.slider("Zoom", min_value=0, max_value=20, value=14)

#         # Show interactive Mapbox map (satellite style)
#         view_state = pdk.ViewState(latitude=lat, longitude=lon, zoom=zoom, pitch=0)

#         MAPBOX_TOKEN = st.secrets["MAPBOX_TOKEN"]

#         deck = pdk.Deck(
#             map_style="mapbox://styles/mapbox/satellite-v9",
#             initial_view_state=view_state,
#             layers=[],
#             mapbox_key=MAPBOX_TOKEN,
#         )

#         st.pydeck_chart(deck)

#         st.markdown(
#             "Adjust latitude/longitude and zoom to frame the area you want, "
#             "then click **Take snapshot**."
#         )

#         snapshot_size = st.selectbox(
#             "Snapshot size (pixels)",
#             options=[256, 512, 1024],
#             index=1,
#         )

#         if st.button("📸 Take snapshot"):
#             # Call Mapbox Static Images API to grab a satellite snapshot
#             width = height = snapshot_size
#             url = (
#                 f"https://api.mapbox.com/styles/v1/mapbox/satellite-v9/static/"
#                 f"{lon},{lat},{zoom},0,0/{width}x{height}"
#                 f"?access_token={MAPBOX_TOKEN}"
#             )

#             resp = requests.get(url)
#             if resp.status_code != 200:
#                 st.error(f"Error getting snapshot from Mapbox (status {resp.status_code}).")
#             else:
#                 img_bytes = BytesIO(resp.content)
#                 snap_image = Image.open(img_bytes)

#                 st.image(
#                     snap_image,
#                     caption=f"Satellite snapshot @ lat={lat}, lon={lon}, zoom={zoom}",
#                     use_column_width=False,
#                 )

#                 snap_array = np.array(snap_image)
#                 st.write("Snapshot shape:", snap_array.shape)

#                 if st.button("Run model on snapshot"):
#                     # TODO: call your model API here with snap_array
#                     st.write("👉 Here you would call your model API with `snap_array`.")


# app.py
import os
from io import BytesIO

import requests
import numpy as np
import pydeck as pdk
import streamlit as st
from PIL import Image

# -------------------- CONFIG --------------------

st.set_page_config(
    page_title="Satellite Segmentation Demo",
    layout="wide",
)

st.title("🌍 Satellite Segmentation Demo")

# Your API endpoints (override via environment variables if you want)
API_ENDPOINT = os.getenv("API_ENDPOINT", "http://localhost:8000/predict")
API_ENDPOINT_GET = os.getenv("API_ENDPOINT_GET", "http://localhost:8000/")


# -------------------- MAPBOX TOKEN --------------------

def get_mapbox_token():
    # Prefer Streamlit secrets, fall back to environment variable
    if "MAPBOX_TOKEN" in st.secrets:
        return st.secrets["MAPBOX_TOKEN"]
    # Common env var name for Mapbox / pydeck
    token = os.getenv("MAPBOX_API_KEY") or os.getenv("MAPBOX_TOKEN")
    return token


MAPBOX_TOKEN = get_mapbox_token()
if MAPBOX_TOKEN:
    pdk.settings.mapbox_key = MAPBOX_TOKEN


# -------------------- SESSION STATE --------------------

if "captured_image" not in st.session_state:
    st.session_state.captured_image = None


# -------------------- TABS --------------------
st.markdown("""
    <style>
        .stTabs [data-baseweb="tab"] {
            font-size: 1.4rem;
            padding: 14px;
            height: 3.8rem;
        }
        .stTabs [data-baseweb="tab"] > div {
            font-weight: 600;
        }
    </style>
""", unsafe_allow_html=True)
tab_upload, tab_map = st.tabs(["📂 Upload image", "🗺️ Map snapshot"])

# ====== TAB 1: FILE UPLOAD ======
with tab_upload:
    st.subheader("Upload a satellite image")

    uploaded_file = st.file_uploader(
        "Upload a satellite image",
        type=["png", "jpg", "jpeg", "tif", "tiff"],
        key="file_uploader",
    )

    if uploaded_file is not None:
        image = Image.open(uploaded_file).convert("RGB")
        st.image(image, caption="Uploaded image", use_container_width=True)

        img_array = np.array(image)
        st.write("Image shape:", img_array.shape)
        x_chunks = round(img_array.shape[1]/256)
        y_chunks = round(img_array.shape[0]/256)
        total_chunks = x_chunks * y_chunks
        st.write(y_chunks," divisions sur la hauteur de l'image et",x_chunks, "sur la largeur")
        st.write("Nombre de chunks:", total_chunks)

        if st.button("➡️ Use this image for the API", key="use_uploaded"):
            st.session_state.captured_image = image
            st.success("Uploaded image selected for API ✅")


# ====== TAB 2: MAP SNAPSHOT ======
with tab_map:
    st.subheader("Choose a location and take a satellite snapshot")

    if not MAPBOX_TOKEN:
        st.warning(
            "You need a Mapbox access token to use this feature. \n\n"
            "Set `MAPBOX_TOKEN` in `.streamlit/secrets.toml` or as an environment variable "
            "(`MAPBOX_API_KEY` or `MAPBOX_TOKEN`)."
        )
    else:
        col1, col2, col3 = st.columns(3)
        with col1:
            lat = st.number_input("Latitude", value=48.8566)  # Paris by default
        with col2:
            lon = st.number_input("Longitude", value=2.3522)
        with col3:
            zoom = st.slider("Zoom", min_value=0, max_value=20, value=14)

        # Show interactive map
        view_state = pdk.ViewState(latitude=lat, longitude=lon, zoom=zoom, pitch=0)
        deck = pdk.Deck(
            map_style="mapbox://styles/mapbox/satellite-v9",
            initial_view_state=view_state,
            layers=[],
        )
        st.pydeck_chart(deck)

        st.markdown(
            "Adjust latitude, longitude and zoom to frame your area, "
            "then take a **satellite snapshot**."
        )

        snapshot_size = st.selectbox(
            "Snapshot size (pixels)",
            options=[256, 512, 1024],
            index=1,
            key="snapshot_size",
        )

        if st.button("📸 Take snapshot", key="take_snapshot"):
            width = height = snapshot_size

            # Mapbox Static Images API URL
            url = (
                f"https://api.mapbox.com/styles/v1/mapbox/satellite-v9/static/"
                f"{lon},{lat},{zoom},0,0/{width}x{height}"
                f"?access_token={MAPBOX_TOKEN}"
            )

            with st.spinner("Fetching snapshot from Mapbox..."):
                resp = requests.get(url)

            if resp.status_code != 200:
                st.error(f"Error getting snapshot from Mapbox (status {resp.status_code}).")
            else:
                img_bytes = BytesIO(resp.content)
                snap_image = Image.open(img_bytes).convert("RGB")

                st.image(
                    snap_image,
                    caption=f"Snapshot @ lat={lat}, lon={lon}, zoom={zoom}",
                    use_container_width=False,
                )

                snap_array = np.array(snap_image)
                st.write("Snapshot shape:", snap_array.shape)

                if st.button("➡️ Use this snapshot for the API", key="use_snapshot"):
                    st.session_state.captured_image = snap_image
                    st.success("Snapshot selected for API ✅")


# -------------------- API CALL SECTION --------------------

st.markdown("---")
st.header("⚙️ Model API")

# Show currently selected image (from upload or map)
if st.session_state.captured_image is not None:
    st.markdown("### ✅ Current input image")
    st.image(st.session_state.captured_image, use_container_width=True)

    if st.button("🚀 Send to API", type="primary", key="send_to_api"):
        buffer = BytesIO()
        st.session_state.captured_image.save(buffer, format="PNG")
        buffer.seek(0)

        files = {"file": ("input.png", buffer.read(), "image/png")}

        try:
            with st.spinner("Processing image..."):
                response = requests.post(API_ENDPOINT, files=files)

            if response.status_code == 200:
                output_image = Image.open(BytesIO(response.content))

                st.markdown("### 🎨 Output image")
                st.image(output_image, use_container_width=True)
                st.success("Image successfully processed ✨")
            else:
                st.error(f"API request failed (status {response.status_code}). Please try again.")
                st.text(f"Response text: {response.text[:500]}")

        except Exception as e:
            st.error("API request failed due to an exception.")
            st.text(str(e))
else:
    st.info("No image selected yet. Upload an image or take a snapshot on the map.")

# -------------------- TEST API (GET) --------------------

st.markdown("---")
if st.button("🤗 Test API", key="test_api"):
    try:
        response = requests.get(API_ENDPOINT_GET, timeout=5)
        response.raise_for_status()
        greeting = response.json().get("greeting", str(response.json()))
        st.markdown(greeting)
    except Exception as e:
        st.markdown("Something went wrong 😥")
        st.text(str(e))
