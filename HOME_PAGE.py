import streamlit as st

st.set_page_config(
    page_title="La carte et le territoire",
    page_icon="🌍",
    layout="wide"
)

# You can keep your common CSS styles here or in a separate file.
st.markdown("""<style>...</style>""", unsafe_allow_html=True)

st.markdown(
    """
    <style>
        .block-container {
            /* Keep top padding minimal for a clean look */
            padding-top: 1rem !important;
        }
        .hero {
            text-align: center;
            /* Increase vertical padding (top/bottom) significantly */
            padding: 5rem 1rem 5rem 1rem;
            /* This adds 5rem of space above and below the hero content */
        }
        .hero h1 {
            /* Significantly increase the main title font size */
            font-size: 5rem;
            margin-bottom: 1rem;
        }
        .hero p {
            /* Increase paragraph font size */
            font-size: 1.5rem;
            margin-bottom: 0.5rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# -------------------- HERO ----------------------------------------------------

st.markdown(
    """
    <div class="hero">
        <h1>🌍 La carte et le territoire</h1>
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

# You can add more vertical space by adding a couple of empty lines
st.markdown("<br><br>", unsafe_allow_html=True)
st.info("👈 Use the navigation sidebar to select a model page and start exploring!")
