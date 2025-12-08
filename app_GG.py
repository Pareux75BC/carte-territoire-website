import streamlit as st
import requests
from PIL import Image
import io
from streamlit_folium import folium_static
import folium

# --- Configuration & Helpers ---

# Placeholder API Endpoint - REPLACE WITH YOUR ACTUAL API URL
API_URL = "https://carte-territoire-24889736924.europe-west1.run.app/upload-and-process"

def process_and_post_image(image_bytes: bytes, squared: bool) -> bytes | None:
    """
    Sends the captured image to the external API for processing and
    returns the processed image bytes.
    """
    st.info("📦 Sending image to the API for processing...")

    # In a real app, you might send the image and parameters (like 'squared')
    # in the POST request.
    files = {'image': ('input_image.png', image_bytes, 'image/png')}
    data = {'squared': str(squared)}

    try:
        # Send POST request
        response = requests.post(API_URL, files=files, data=data, timeout=30)

        # Check if the request was successful
        if response.status_code == 200:
            st.success("✅ API call successful! Receiving processed image.")
            return response.content
        else:
            st.error(f"❌ API Error: Received status code {response.status_code}.")
            st.error("Please check the API service and its endpoint.")
            return None

    except requests.exceptions.RequestException as e:
        st.error(f"❌ Connection Error: Could not connect to the API. Details: {e}")
        return None


# --- Streamlit App Front-End ---

def main():
    st.set_page_config(
        page_title="La carte et le territoire",
        page_icon="🗺️",
        layout="wide"
    )

    ## 🖼️ Header and Welcome Message
    st.title("🛰️ La carte et le territoire")
    st.subheader("Welcome to the **Satellite Image Processor** App!")

    st.markdown(
        """
        This is the project page for the **'La carte et le territoire'** group
        from **Le Wagon** batch **2130**.

        Use the interface below to select an area, capture a clean satellite image,
        and have it processed by our powerful external API!
        """
    )

    st.markdown("---")


    ## 📍 Step 1: Map Interaction and Image Capture (Conceptual)

    # IMPORTANT: The following Folium map is a conceptual placeholder.
    # It allows interaction (pan/zoom) but *cannot* natively capture a
    # label-free, cropped satellite screenshot that is immediately sent to an API
    # without significant custom JavaScript/component integration.

    st.header("1. Select Your Area of Interest")

    col1, col2 = st.columns([3, 1])

    with col1:
        # Create a Folium map centered around Paris (example)
        m = folium.Map(
            location=[48.8566, 2.3522],
            zoom_start=12,
            tiles='Stamen Terrain',
            attr='Map tiles by Stamen Design, under CC BY 3.0. Data by OpenStreetMap, under ODbL.' # A tile set with less labels, but not true 'naked' satellite.
            # To get true satellite tiles: folium.TileLayer('Stamen Terrain', attr='...').add_to(m)
            # Or use a custom tile layer for Google Satellite (requires an API key/proxy for commercial use)
        )
        # Display the map
        folium_static(m, width=700, height=450)

        st.caption("Conceptual Map Interface: In a fully implemented version, you would use this interactive map to define a **bounding box** and trigger the 'Capture Image' action to grab a **label-free** satellite image.")

    with col2:
        # Option to limit the capture to a squared image
        squared_capture = st.checkbox("Limit screenshot to a **squared** image", value=True)

        # Simple file uploader as a fallback/test for the processing pipeline
        uploaded_file = st.file_uploader(
            "Upload a sample image (e.g., a satellite shot) to test the API pipeline:",
            type=["png", "jpg", "jpeg"]
        )

        if uploaded_file is not None:
            # Read the uploaded image bytes
            input_image_bytes = uploaded_file.read()
            st.image(input_image_bytes, caption="Input Image Preview", use_column_width=True)

            # The button to trigger the whole process
            process_button = st.button("🚀 Process Image via API")

            if process_button:
                # Proceed to step 2 only if an image is available (uploaded or captured)
                st.markdown("---")
                st.header("2. Processing and Output")

                # --- Step 2: Image Processing and API Request ---

                with st.spinner('Processing image and contacting API...'):
                    # The function that handles the API request
                    output_image_bytes = process_and_post_image(input_image_bytes, squared_capture)

                    if output_image_bytes:
                        # Convert bytes back to a PIL Image for display
                        output_image = Image.open(io.BytesIO(output_image_bytes))

                        # Display the output image
                        st.subheader("🖼️ Processed Output Image")
                        st.image(output_image, caption="Processed Image from API", use_column_width=True)

                        # Final success message
                        st.balloons()
                        st.success("🎉 **Success!** Your image has been processed and is displayed above.")

                        # Download button for the output
                        st.download_button(
                            label="Download Processed Image",
                            data=output_image_bytes,
                            file_name="processed_image.png",
                            mime="image/png"
                        )

                    else:
                        st.warning("Please upload an image to test the processing pipeline.")


if __name__ == "__main__":
    main()
