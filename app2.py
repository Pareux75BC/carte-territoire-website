import streamlit as st
import requests
import base64
from io import BytesIO
from PIL import Image

# -------------------- CONFIG --------------------
st.set_page_config(
    page_title="La carte et le territoire",
    page_icon="🗺️",
    layout="wide"
)

MAPBOX_TOKEN = st.secrets["MAPBOX_TOKEN"]

API_ENDPOINT = "https://carte-territoire-24889736924.europe-west1.run.app/upload-and-process"
API_ENDPOINT_GET = "https://carte-territoire-24889736924.europe-west1.run.app/"

# -------------------- STYLES --------------------

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

# -------------------- HERO --------------------

st.markdown(
    """
    <div class="hero">
        <h1>🗺️ La carte et le territoire</h1>
        <p>
            Satellite landscapes explored through image processing.
        </p>
        <p>
            <strong>Le Wagon — Batch 2130</strong>
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# -------------------- CONTROLS --------------------

st.markdown("## 🌍 Explore the map")

square_crop = st.checkbox("📐 Force square image", value=True)

# -------------------------------------------------
# MAPBOX HTML (SATELLITE VIEW, NO LABELS)
# -------------------------------------------------

mapbox_html = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8" />
<script src="https://api.mapbox.com/mapbox-gl-js/v2.15.0/mapbox-gl.js"></script>
<link href="https://api.mapbox.com/mapbox-gl-js/v2.15.0/mapbox-gl.css" rel="stylesheet" />

<style>
  body {{ margin: 0; }}
  #map {{
    width: 100%;
    height: 600px;
    border-radius: 14px;
  }}
  #btn {{
    margin-top: 10px;
    padding: 10px 16px;
    font-size: 16px;
    cursor: pointer;
  }}
</style>
</head>

<body>

<div id="map"></div>
<button id="btn">📸 Capture image</button>

<script>
  mapboxgl.accessToken = "{MAPBOX_TOKEN}";

  const map = new mapboxgl.Map({{
    container: "map",
    style: "mapbox://styles/mapbox/satellite-v9",
    center: [2.3522, 48.8566],
    zoom: 13
  }});

  map.addControl(new mapboxgl.NavigationControl());

  document.getElementById("btn").onclick = () => {{
    const canvas = map.getCanvas();
    let size = Math.min(canvas.width, canvas.height);

    const outCanvas = document.createElement("canvas");
    outCanvas.width = { "size" if square_crop else "canvas.width" };
    outCanvas.height = { "size" if square_crop else "canvas.height" };

    const ctx = outCanvas.getContext("2d");

    if ({str(square_crop).lower()}) {{
        const x = (canvas.width - size) / 2;
        const y = (canvas.height - size) / 2;
        ctx.drawImage(canvas, x, y, size, size, 0, 0, size, size);
    }} else {{
        ctx.drawImage(canvas, 0, 0);
    }}

    const imageData = outCanvas.toDataURL("image/png");
    window.parent.postMessage(imageData, "*");
  }};
</script>

</body>
</html>
"""

st.components.v1.html(mapbox_html, height=700)

# -------------------------------------------------
# IMAGE STATE
# -------------------------------------------------

if "input_image" not in st.session_state:
    st.session_state.input_image = None

st.info("Use the **Capture image** button to grab a clean satellite snapshot.")

uploaded = st.file_uploader(
    "Or upload an image manually",
    type=["png", "jpg", "jpeg"]
)

if uploaded:
    st.session_state.input_image = Image.open(uploaded).convert("RGB")

# -------------------------------------------------
# API PROCESSING
# -------------------------------------------------

if st.session_state.input_image:
    st.markdown("### ✅ Input image")
    st.image(st.session_state.input_image, use_container_width=True)

    if st.button("🚀 Send to API"):
        buffer = BytesIO()
        st.session_state.input_image.save(buffer, format="PNG")

        payload = {
            "image": base64.b64encode(buffer.getvalue()).decode()
        }

        with st.spinner("Processing image..."):
            response = requests.post(API_ENDPOINT, json=payload)

        if response.status_code == 200:
            output_b64 = response.json()["image"]
            output_image = Image.open(
                BytesIO(base64.b64decode(output_b64))
            )

            st.markdown("### 🎨 Output image")
            st.image(output_image, use_container_width=True)
            st.success("Image successfully processed ✨")

        else:
            st.error("Something went wrong with the API request.")

if st.button("🤗 Test API"):
    try:
        response = requests.get(API_ENDPOINT_GET).json()['greeting']
        st.markdown(response)
    except:
        st.markdown('Something went wrong 😥')
