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

# -------------------- API endpoints for each mode --------------------
API_ENDPOINT_MODEL_1 = os.getenv("API_ENDPOINT_MODEL_1", "http://localhost:8000/upload-and-process")
API_ENDPOINT_MODEL_2 = os.getenv("API_ENDPOINT_MODEL_2", "http://localhost:8000/upload-and-process")
API_ENDPOINT_COMPARE = os.getenv("API_ENDPOINT_COMPARE", "http://localhost:8000/upload-and-process")
API_ENDPOINT_EVOLUTION = os.getenv("API_ENDPOINT_EVOLUTION", "http://localhost:8000/upload-and-process")

# test endpoint
API_ENDPOINT_GET = os.getenv("API_ENDPOINT_GET", "http://localhost:8000/")

# -------------------- SIDEBAR MODE SELECTION --------------------
st.sidebar.title("⚙️ Mode")
mode = st.sidebar.radio(
    "our models:",
    ("U-net", "U-net +", "Compare models", "Surface evolution")
)
if mode == "U-net":
    API_ENDPOINT = API_ENDPOINT_MODEL_1
elif mode == "U-net +":
    API_ENDPOINT = API_ENDPOINT_MODEL_2
elif mode == "Surface evolution":
    API_ENDPOINT = API_ENDPOINT_EVOLUTION
else:
    API_ENDPOINT = API_ENDPOINT_COMPARE

# Show which mode is active (optional)
# st.info(f"Current mode: **{mode}**")


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

if mode == "Compare models":
    st.subheader("🔍 Compare models on the same image")

    uploaded_file = st.file_uploader(
        "Upload a satellite image",
        type=["png", "jpg", "jpeg"],
        key="compare_uploader"
    )

    if uploaded_file is not None:
        # Read image once
        input_image = Image.open(uploaded_file).convert("RGB")

        # Show input image
        st.markdown("### ✅ Input image")
        st.image(input_image, use_container_width=True)

        if st.button("🚀 Run comparison"):
            # Prepare file buffer
            buf = BytesIO()
            input_image.save(buf, format="PNG")
            buf.seek(0)
            files = {"file": ("input.png", buf.read(), "image/png")}

            with st.spinner("Running both models..."):
                # Call model 1
                resp1 = requests.post(API_ENDPOINT, files=files)

                # Rewind buffer for second call
                buf.seek(0)
                files = {"file": ("input.png", buf.read(), "image/png")}

                # Call model 2
                resp2 = requests.post(API_ENDPOINT_MODEL_2, files=files)

            if resp1.status_code == 200 and resp2.status_code == 200:
                pred1 = Image.open(BytesIO(resp1.content))
                pred2 = Image.open(BytesIO(resp2.content))

                st.markdown("### 📊 Results")

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.caption("🛰️ Original")
                    st.image(input_image, use_container_width=True)

                with col2:
                    st.caption("🧠 Model 1")
                    st.image(pred1, use_container_width=True)

                with col3:
                    st.caption("🧠 Model 2")
                    st.image(pred2, use_container_width=True)
            else:
                st.error("One of the model calls failed. Check the API endpoints and logs.")

elif mode == "Surface evolution":

    # if uploaded_file is not None:
    #     image = Image.open(uploaded_file).convert("RGB")
    #     st.image(image, caption="Uploaded image", use_container_width=True)

    #     img_array = np.array(image)
    #     st.write("Image shape:", img_array.shape)
    #     x_chunks = round(img_array.shape[1]/256)
    #     y_chunks = round(img_array.shape[0]/256)
    #     total_chunks = x_chunks * y_chunks
    #     st.write(y_chunks," divisions sur la hauteur de l'image et",x_chunks, "sur la largeur")
    #     st.write("Nombre de chunks:", total_chunks)

    #     if st.button("➡️ Use this image for the API", key="use_uploaded"):
    #         st.session_state.captured_image = image
    #         st.success("Uploaded image selected for API ✅")

    st.subheader("Upload 2 or 3 satellite images of the same place (different years)")

    # Allow multiple files
    uploaded_files = st.file_uploader(
        "Upload 2 or 3 satellite images (same location, different years)",
        type=["png", "jpg", "jpeg", "tif", "tiff"],
        accept_multiple_files=True,
        key="surface_evolution_uploader",
    )

    if uploaded_files:
        n_files = len(uploaded_files)

        if n_files < 2:
            st.warning("Please upload **at least 2 images**.")
            st.stop()

        if n_files > 3:
            st.warning("Please upload **maximum 3 images**.")
            st.stop()
        else:
            # Open input images
            images = [Image.open(f).convert("RGB") for f in uploaded_files]

            st.markdown("### ✅ Input images")
            cols = st.columns(3)
            for i, (col, img, f) in enumerate(zip(cols, images, uploaded_files), start=1):
                with col:
                    st.image(img, caption=f"Image {i}: {f.name}", use_container_width=True)

            if st.button("🚀 Run model on 3 images", key="run_surface_evolution"):
                predictions = []

                with st.spinner("Running the model on all images..."):
                    for img in images:
                        # Prepare buffer for API
                        buf = BytesIO()
                        img.save(buf, format="PNG")
                        buf.seek(0)

                        files = {"file": ("input.png", buf.read(), "image/png")}

                        # 🔴 IMPORTANT: API_ENDPOINT should be the endpoint of the ONE model you want
                        # e.g. API_ENDPOINT_MODEL_1 or whatever you chose earlier
                        resp = requests.post(API_ENDPOINT, files=files)

                        if resp.status_code == 200:
                            pred_img = Image.open(BytesIO(resp.content))
                            predictions.append(pred_img)
                        else:
                            st.error(f"API call failed with status code {resp.status_code}")
                            predictions = []
                            break

                if predictions:
                    st.markdown("### 🧠 Model outputs (aligned horizontally)")
                    out_cols = st.columns(3)
                    for i, (col, pred) in enumerate(zip(out_cols, predictions), start=1):
                        with col:
                            st.image(pred, caption=f"Prediction {i}", use_container_width=True)


else:
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
        DISPLAY_WIDTH = 600

        uploaded_file = st.file_uploader(
            "Upload a satellite image",
            type=["png", "jpg", "jpeg", "tif", "tiff"],
            key="file_uploader",
        )

        if uploaded_file is not None:
            image = Image.open(uploaded_file).convert("RGB")
            display_image = image.copy()
            display_image.thumbnail((DISPLAY_WIDTH, DISPLAY_WIDTH))
            st.image(display_image, caption="Uploaded image", use_container_width=False)

            img_array = np.array(image)
            st.write("Image shape:", img_array.shape)
            x_chunks = round(img_array.shape[1]/256)
            y_chunks = round(img_array.shape[0]/256)
            total_chunks = x_chunks * y_chunks
            st.write(y_chunks," divisions sur la hauteur de l'image et",x_chunks, "sur la largeur")
            st.write("Nombre de chunks:", total_chunks)

            # if st.button("➡️ Use this image for the API", key="use_uploaded"):
            #     st.session_state.captured_image = image
            #     st.success("Uploaded image selected for API ✅")


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

    if st.session_state.captured_image is not None:
        if st.button("🚀 Send to API", type="primary", key="send_to_api"):
            buffer = BytesIO()
            st.session_state.captured_image.save(buffer, format="PNG")
            buffer.seek(0)

            files = {"file": ("input.png", buffer.read(), "image/png")}

            try:
                with st.spinner("Processing image..."):
                    response = requests.post(API_ENDPOINT_MODEL_1, files=files)

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
