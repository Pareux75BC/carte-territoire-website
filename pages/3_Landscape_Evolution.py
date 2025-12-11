import streamlit as st
from PIL import Image
import requests
from io import BytesIO

# constants and dictionaries
from utils.constants import MAPBOX_STYLE, INITIAL_CENTER, INITIAL_ZOOM, API_ENDPOINT_INITIAL, REDUCED_7

st.header("⏱️ Under construction")

st.subheader("Upload 2 or 3 satellite images of the same place (different years)")

# images=[3]
# # images[0]=st.image("default/vegas2002.PNG", caption=None, use_container_width=True,
# #          channels="RGB")
# # images[1]=st.image("default/vegas1989.PNG", caption=None, use_container_width=True,
# #          channels="RGB")
# images[0]=Image.open("default/vegas1972.PNG").convert("RGB")
# images[1]=Image.open("default/vegas1989.PNG").convert("RGB")
# images[2]=Image.open("default/vegas2002.PNG").convert("RGB")

# #images = [Image.open(f).convert("RGB") for f in uploaded_files]

# st.markdown("### ✅ Input images")
# cols = st.columns(2)
# for i, (col, img) in enumerate(zip(cols, images), start=1):
#     with col:
#         st.image(img, caption=f"Image {i}: ", use_container_width=True)

img1 = Image.open("default/vegas1989.png")
img2 = Image.open("default/vegas2020.png")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Before")
    st.image(img1, use_container_width=True)

with col2:
    st.subheader("After")
    st.image(img2, use_container_width=True)

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
                    resp = requests.post(API_ENDPOINT_INITIAL, files=files)

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
