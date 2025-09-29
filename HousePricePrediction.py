import streamlit as st
import pickle
import numpy as np
import pandas as pd
import base64
import time 

# ================================
# 🎯 CONFIGURATION
# ================================
MODEL_PATH = "lr_model.pkl"
FEATURE_NAMES = ['sqft_living', 'bedrooms', 'bathrooms', 'floors', 'grade', 'waterfront', 'yr_built']

# BASE64 FALLBACK IMAGE (Dark, subtle, embedded SVG image)
BASE64_FALLBACK_IMAGE = """
data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIwMCIgaGVpZ2h0PSI4MDAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+
  <rect width="1200" height="800" fill="#1b1c19"/>
  <rect x="50" y="50" width="1100" height="700" stroke="#227c45" stroke-width="5" fill="none" stroke-opacity="0.3"/>
  <rect x="100" y="100" width="500" height="200" fill="rgba(255, 255, 255, 0.05)" rx="10" ry="10"/>
  <rect x="600" y="400" width="500" height="300" fill="rgba(255, 255, 255, 0.08)" rx="10" ry="10"/>
  <line x1="50" y1="750" x2="1150" y2="50" stroke="#227c45" stroke-width="2" stroke-opacity="0.1"/>
  <circle cx="600" cy="400" r="100" fill="rgba(255, 255, 255, 0.05)"/>
</svg>
"""

# ================================
# ⚙️ UTILITIES
# ================================

def get_base64_image_url(uploaded_file):
    """Reads an uploaded file and converts it to a Base64 data URL."""
    try:
        bytes_data = uploaded_file.getvalue()
        base64_encoded_data = base64.b64encode(bytes_data).decode('utf-8')
        mime_type = uploaded_file.type if uploaded_file.type else "image/png"
        return f"data:{mime_type};base64,{base64_encoded_data}"
    except Exception as e:
        st.error(f"Error processing image: {e}")
        return None

# ================================
# 🌄 CINEMATIC BACKGROUND SLIDESHOW
# ================================

def set_cinematic_bg(base64_urls, interval_per_image=6):
    """Applies a smooth crossfading background slideshow using Base64 URLs."""
    num_images = len(base64_urls)
    total_duration = num_images * interval_per_image

    # Overlay opacity set to 0.55 for higher image visibility
    OVERLAY_OPACITY = "rgba(0,0,0,0.55)" 

    # --- CSS Selectors for Frosted Glass Effect ---
    # Target only the sidebar and the main content tabs (stTabs),
    # explicitly excluding the main header title/subtitle block.
    FROSTED_GLASS_SELECTORS = """
        /* Sidebar container */
        [data-testid="stSidebar"] > div:first-child,
        /* Tab containers */
        [data-testid="stTabs"] > div:nth-child(2)
    """

    if num_images == 0:
        st.warning("No images uploaded. Using static dark background image.")
        
        # --- FALLBACK CSS: Base64 Embedded Image (Static) ---
        st.markdown(f"""
            <style>
            .stApp {{
                background-image: url('{BASE64_FALLBACK_IMAGE.replace('\n', '')}');
                background-attachment: fixed;
                background-size: cover;
                background-position: center;
                animation: none !important;
            }}
            .stApp::before {{
                content: "";
                position: fixed;
                top: 0; left: 0;
                width: 100%; height: 100%;
                background: {OVERLAY_OPACITY};
                z-index: 0;
            }}
            {FROSTED_GLASS_SELECTORS} {{
                background: rgba(255, 255, 255, 0.15); 
                backdrop-filter: blur(8px);
                border-radius: 16px;
                padding: 20px;
                z-index: 10;
            }}
            </style>
        """, unsafe_allow_html=True)
        return

    # --- SUCCESS CSS: Image Slideshow (Dynamic) ---
    
    css_keyframes = []
    for i in range(num_images):
        start_percent = (i * 100) / num_images
        hold_percent = (start_percent + ((100 / num_images) * (1 - 1 / interval_per_image))) 
        
        css_keyframes.append(f"{start_percent:.2f}% {{ background-image: url('{base64_urls[i]}'); }}")
        if i < num_images - 1:
             css_keyframes.append(f"{hold_percent:.2f}% {{ background-image: url('{base64_urls[i]}'); }}")
        
    css_keyframes.append(f"100% {{ background-image: url('{base64_urls[0]}'); }}")


    st.markdown(f"""
        <style>
        .stApp {{
            background-size: cover;
            background-attachment: fixed;
            background-repeat: no-repeat;
            background-image: url('{base64_urls[0]}');
            animation: cinematicBg {total_duration}s infinite;
        }}
        @keyframes cinematicBg {{
            {"".join(css_keyframes)}
        }}

        /* Apply a dark overlay for better readability and subtlety */
        .stApp::before {{
            content: "";
            position: fixed;
            top: 0; left: 0;
            width: 100%; height: 100%;
            background: {OVERLAY_OPACITY};
            z-index: 0;
        }}
        
        /* Frosted glass content containers (Only Sidebar and Tabs) */
        {FROSTED_GLASS_SELECTORS} {{
            background: rgba(255, 255, 255, 0.15); 
            backdrop-filter: blur(8px);
            border-radius: 16px;
            padding: 20px;
            z-index: 10;
        }}

        /* General styling adjustments */
        * {{ color: white; font-family: 'Inter', sans-serif; }}
        /* Ensure prediction box stands out */
        .prediction-box {{
            color: white !important; 
        }}
        .prediction-box h2, .prediction-box h1, .prediction-box p {{
            color: inherit !important;
        }}

        [data-testid="stHeader"], [data-testid="stToolbar"] {{ background: transparent !important; }}
        </style>
    """, unsafe_allow_html=True)

# ================================
# 📌 LOAD MODEL
# ================================
model = None
try:
    with open(MODEL_PATH, "rb") as f:
        model = pickle.load(f)
except FileNotFoundError:
    st.error(f"❌ Model file '{MODEL_PATH}' not found. Please check the path.")
except Exception as e:
    st.error(f"⚠️ Error loading model: {e}")

# ================================
# 📌 SIDEBAR CONTENT (Includes Image Uploader)
# ================================

base64_image_urls = []
with st.sidebar:
    st.title("ℹ️ App Configuration")
    
    # --- IMAGE UPLOADER ---
    st.subheader("🖼️ Background Images")
    uploaded_files = st.file_uploader(
        "Upload images (JPG/PNG) for the slideshow:",
        type=["jpg", "jpeg", "png"],
        accept_multiple_files=True,
        help="The slideshow starts once images are uploaded. This runs without a network."
    )
    
    if uploaded_files:
        if len(uploaded_files) < 3:
            st.info("Upload at least 3 images for a better slideshow effect.")
        
        with st.spinner(f"Processing {len(uploaded_files)} image(s)..."):
            for file in uploaded_files:
                url = get_base64_image_url(file)
                if url:
                    base64_image_urls.append(url)
            time.sleep(0.5)

    st.markdown("---")
    st.subheader("Model Info")
    st.info("This app predicts house prices using a trained Linear Regression Model.")
    st.markdown(
        "✨ Made with ❤️<br>👨‍💻 Developed by **Umar Imam**",
        unsafe_allow_html=True
    )

# Apply background logic (using images uploaded in the sidebar)
set_cinematic_bg(base64_image_urls)

# ================================
# 🏡 HEADER (Main Screen)
# ================================
st.markdown("<h1 style='text-align:center; color:#FFD700; text-shadow: 2px 2px 6px #000000;'>🏠 LUXURY HOUSE PRICE PREDICTION</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; font-size:18px; color:#F0F0F0;'>Predict housing prices based on key architectural and locational features.</p>", unsafe_allow_html=True)
# Removed st.markdown("---") here, as it was creating an extra line/bar

# ================================
# 📊 TABS (Main Screen)
# ================================
tab1, tab2 = st.tabs(["🔑 Prediction", "📈 Model Info"])

# ================================
# ✨ TAB 1 — PREDICTION
# ================================
with tab1:
    st.header("Enter Property Features")

    if model:
        col1, col2 = st.columns(2)

        # Collect user inputs
        with col1:
            sqft_living = st.number_input("📏 Living Area (Sq. Ft.)", 300, 15000, 2000, step=10)
            bedrooms = st.number_input("🛏️ Bedrooms", 0, 15, 3)
            bathrooms = st.number_input("🛁 Bathrooms", 0.0, 10.0, 2.0, step=0.25)
            floors = st.selectbox("🏢 Floors", [1.0, 1.5, 2.0, 2.5, 3.0, 3.5], index=2)

        with col2:
            grade = st.slider("🌟 Quality Grade (1 = poor, 13 = excellent)", 1, 13, 7)
            waterfront = st.selectbox("🌊 Waterfront Property", [0, 1], format_func=lambda x: "Yes" if x == 1 else "No")
            yr_built = st.number_input("🏗️ Year Built", 1900, 2024, 2000)

        if st.button("💰 Predict Price", use_container_width=True, type="primary"):
            # Prepare data as a Pandas DataFrame with correct column names
            input_data = [sqft_living, bedrooms, bathrooms, floors, grade, waterfront, yr_built]
            features_df = pd.DataFrame([input_data], columns=FEATURE_NAMES)
            
            try:
                prediction = model.predict(features_df)
                st.markdown(f"""
                    <div class="prediction-box" style="background-color:rgba(34, 139, 34, 0.9); padding:20px; border-radius:15px; text-align:center; margin-top: 20px;">
                        <h2 style="color:white;">🏡 Estimated Price</h2>
                        <h1 style="color:#FFD700;">${prediction[0]:,.2f}</h1>
                        <p style="color:white;">Based on the details you provided.</p>
                    </div>
                """, unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Prediction failed: {e}")
    else:
        st.warning("⚠️ Prediction feature unavailable due to model loading error.")

# ================================
# 📊 TAB 2 — MODEL INFO
# ================================
with tab2:
    st.header("Model Overview & Performance")

    st.subheader("📌 Model Used")
    st.info("**Linear Regression** was used for this prediction task.")

    st.subheader("🧰 Training Features")
    st.markdown("""
    - `sqft_living`, `bedrooms`, `bathrooms`, `floors`, `grade`, `waterfront`, `yr_built`
    - Additional features were used during training but are omitted here for simplicity.
    """)

    st.subheader("📊 Performance Metrics")
    col1, col2, col3 = st.columns(3)
    col1.metric("R²", "0.7736", delta="Good Fit")
    col2.metric("RMSE", "0.2540", delta="Scaled")
    col3.metric("MSE", "0.0645", delta="Scaled")