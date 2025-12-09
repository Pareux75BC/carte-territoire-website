import streamlit as st
import requests
import base64
from io import BytesIO
from PIL import Image
import json

# -------------------- CONFIG --------------------
GOOGLE_MAPS_KEY = st.secrets["GOOGLE_MAPS_KEY"]

st.set_page_config(
    page_title="La carte et le territoire",
    page_icon="🗺️",
    layout="wide"
)

API_ENDPOINT = "http://localhost:8000/upload-and-process/" #"https://carte-territoire-24889736924.europe-west1.run.app/upload-and-process"
API_ENDPOINT_GET = "http://localhost:8000/" #"https://carte-territoire-24889736924.europe-west1.run.app/"

# -------------------- STYLES --------------------

st.markdown(
    """
    <style>
        .main {
            background-color: #fafafa;
        }
        .hero {
            padding: 3rem 1rem 2rem 1rem;
            text-align: center;
        }
        .hero h1 {
            font-size: 3rem;
        }
        .hero p {
            font-size: 1.2rem;
            color: #555;
        }
        .section {
            margin-top: 3rem;
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
            A visual exploration of landscapes through satellite imagery.
        </p>
        <p>
            <strong>Le Wagon — Batch 2130</strong>
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# -------------------- CONTROLS --------------------

st.markdown("## 🌍 Select a satellite view")

col1, col2 = st.columns([3, 1])

with col2:
    square_crop = st.checkbox("📐 Force square image", value=True)
    st.caption("Limits the capture to a square format")

# -------------------- GOOGLE MAPS EMBED --------------------

GOOGLE_MAPS_HTML = f"""
<!DOCTYPE html>
<html>
<head>
  <style>
    #map {{
      height: 600px;
      width: 100%;
      border-radius: 12px;
    }}
    #capture {{
      margin-top: 10px;
      padding: 10px 16px;
      font-size: 16px;
    }}
  </style>
</head>
<body>
  <div id="map"></div>
  <button id="capture">📸 Capture image</button>

  <script src="https://maps.googleapis.com/maps/api/js?key={{GOOGLE_MAPS_KEY}}"></script>
  <script>
    let map;

    function initMap() {{
      map = new google.maps.Map(document.getElementById("map"), {{
        center: {{ lat: 48.8566, lng: 2.3522 }},
        zoom: 14,
        mapTypeId: "satellite",
        disableDefaultUI: true
      }});
    }}

    initMap();

    document.getElementById("capture").onclick = async () => {{
      const canvas = document.createElement("canvas");
      const mapDiv = document.getElementById("map");

      const size = Math.min(mapDiv.offsetWidth, mapDiv.offsetHeight);
      canvas.width = { 'size' if square_crop else 'mapDiv.offsetWidth' };
      canvas.height = { 'size' if square_crop else 'mapDiv.offsetHeight' };

      const ctx = canvas.getContext("2d");

      const xml = new XMLSerializer().serializeToString(mapDiv);
      const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${{mapDiv.offsetWidth}}" height="${{mapDiv.offsetHeight}}">
        <foreignObject width="100%" height="100%">${{xml}}</foreignObject>
      </svg>`;

      const img = new Image();
      img.onload = () => {{
        ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
        const dataUrl = canvas.toDataURL("image/png");
        window.parent.postMessage(dataUrl, "*");
      }};
      img.src = "data:image/svg+xml;charset=utf-8," + encodeURIComponent(svg);
    }};
  </script>
</body>
</html>
"""

with col1:
    st.components.v1.html(GOOGLE_MAPS_HTML, height=700)

# -------------------- IMAGE HANDLING --------------------

st.markdown("## 🧠 Process image")

if "captured_image" not in st.session_state:
    st.session_state.captured_image = None

# Listen for browser message
image_data = st.query_params.get("image")

st.info(
    "Use the **Capture image** button above to take a clean satellite snapshot "
    "(no labels, no UI)."
)

uploaded = st.file_uploader(
    "Or upload a satellite image manually",
    type=["png", "jpg", "jpeg"],
)

if uploaded:
    image = Image.open(uploaded).convert("RGB")
    st.session_state.captured_image = image

# -------------------- API CALL --------------------

if st.session_state.captured_image:
    st.markdown("### ✅ Input image")
    st.image(st.session_state.captured_image, use_container_width=True)

    if st.button("🚀 Send to API"):
        buffer = BytesIO()
        st.session_state.captured_image.save(buffer, format="PNG")
        buffer.seek(0)

        files = {"file": ("input.png", buffer.read(), "image/png")}

        with st.spinner("Processing image..."):
            response = requests.post(API_ENDPOINT, files=files)

        if response.status_code == 200:
            output_image = Image.open(BytesIO(response.content))

            st.markdown("### 🎨 Output image")
            st.image(output_image, use_container_width=True)
            st.success("Image successfully processed ✨")

        else:
            st.error("API request failed. Please try again.")

if st.button("🤗 Test API"):
    try:
        response = requests.get(API_ENDPOINT_GET).json()['greeting']
        st.markdown(response)
    except:
        st.markdown('Something went wrong 😥')
