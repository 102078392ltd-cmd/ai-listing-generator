"""
Real Estate Listing Generator — Streamlit Demo App
Powered by Azure OpenAI GPT-4o
"""

import streamlit as st
from core import ListingEngine

# ── Page config ──────────────────────────────────────────────
st.set_page_config(
    page_title="AI Listing Generator",
    page_icon="🏠",
    layout="centered",
)

# ── Custom styling ───────────────────────────────────────────
st.markdown("""
<style>
    .block-container { max-width: 740px; padding-top: 1.5rem; }

    /* Header banner */
    .brand-header {
        background: linear-gradient(135deg, #1B4D7A 0%, #2E86C1 100%);
        color: white;
        padding: 1.8rem 2rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        text-align: center;
    }
    .brand-header h1 {
        margin: 0;
        font-size: 1.9rem;
        font-weight: 700;
        letter-spacing: -0.5px;
    }
    .brand-header p {
        margin: 0.4rem 0 0 0;
        font-size: 0.95rem;
        opacity: 0.9;
    }

    /* Generate button */
    .stButton > button {
        width: 100%;
        padding: 0.7rem 1rem;
        font-weight: 600;
        font-size: 1.05rem;
        border-radius: 8px;
    }

    /* Listing output card */
    .listing-card {
        background: #FAFBFC;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 0.8rem 0;
        font-size: 15px;
        line-height: 1.7;
        color: #1A1A2E;
        white-space: pre-wrap;
    }

    /* Word count badge */
    .word-badge {
        display: inline-block;
        background: #E8F4FD;
        color: #1B4D7A;
        padding: 0.2rem 0.7rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }

    /* Sidebar polish */
    [data-testid="stSidebar"] { background: #F7F9FB; }
    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] .stNumberInput label,
    [data-testid="stSidebar"] .stTextInput label,
    [data-testid="stSidebar"] .stTextArea label {
        font-weight: 600;
        color: #1A1A2E;
    }
</style>
""", unsafe_allow_html=True)

# ── Cached engine (one connection per session) ───────────────
@st.cache_resource
def get_engine():
    return ListingEngine()

# ── Header ───────────────────────────────────────────────────
st.markdown("""
<div class="brand-header">
    <h1>🏠 AI Listing Generator</h1>
    <p>MLS-ready property descriptions in seconds — powered by Azure OpenAI</p>
</div>
""", unsafe_allow_html=True)

# ── Sidebar: property inputs ────────────────────────────────
with st.sidebar:
    st.header("📋 Property Details")

    property_type = st.selectbox(
        "Property Type",
        ["Bungalow", "Two-Storey", "Bi-Level", "Condo / Apartment",
         "Townhouse", "Acreage", "Mobile Home", "Other"],
    )

    col1, col2 = st.columns(2)
    with col1:
        bedrooms = st.number_input("Bedrooms", min_value=0, max_value=10, value=3)
    with col2:
        bathrooms = st.number_input("Bathrooms", min_value=0.0, max_value=10.0,
                                     value=2.0, step=0.5)

    sqft = st.number_input("Square Footage", min_value=0, max_value=20000,
                            value=1200, step=50)

    col3, col4 = st.columns(2)
    with col3:
        year_built = st.number_input("Year Built", min_value=1900, max_value=2026,
                                      value=1985)
    with col4:
        lot_size = st.text_input("Lot Size", placeholder="e.g. 50x120 ft")

    st.divider()

    neighbourhood = st.text_input("Neighbourhood", placeholder="e.g. Cathedral")
    city = st.text_input("City", value="Regina")

    st.divider()

    features_text = st.text_area(
        "Key Features (one per line)",
        placeholder="Hardwood floors\nUpdated kitchen\nFenced backyard\nNew furnace",
        height=140,
    )

    extras = st.text_area(
        "Additional Notes (optional)",
        placeholder="Near schools, walkable area, etc.",
        height=80,
    )

    tone = st.selectbox(
        "Tone",
        ["Professional", "Family-Friendly", "Luxury", "Investor-Focused",
         "First-Time Buyer"],
    )

    num_variations = st.radio(
        "Versions to Generate",
        [1, 2, 3],
        horizontal=True,
        index=0,
    )

# ── Build property dict ─────────────────────────────────────
def build_property_dict():
    features = [f.strip() for f in features_text.strip().splitlines() if f.strip()]
    details = {
        "property_type": property_type,
        "bedrooms": bedrooms,
        "bathrooms": bathrooms,
        "sqft": sqft,
        "year_built": year_built,
        "neighbourhood": neighbourhood or None,
        "city": city or "Regina",
        "features": features or None,
        "tone": tone.lower(),
    }
    if lot_size.strip():
        details["lot_size"] = lot_size.strip()
    if extras.strip():
        details["extras"] = extras.strip()
    return details

# ── Generate ─────────────────────────────────────────────────
if st.button("✨ Generate Listing", type="primary"):
    engine = get_engine()
    prop = build_property_dict()

    with st.spinner("Writing listing..."):
        if num_variations == 1:
            descriptions = [engine.generate(prop)]
        else:
            descriptions = engine.generate_variations(prop, count=num_variations)

    st.session_state["listings"] = descriptions

# ── Display results ──────────────────────────────────────────
if "listings" in st.session_state:
    descriptions = st.session_state["listings"]

    for i, desc in enumerate(descriptions, 1):
        word_count = len(desc.split())

        if len(descriptions) > 1:
            st.subheader(f"Version {i}")

        st.markdown(f'<span class="word-badge">{word_count} words</span>',
                     unsafe_allow_html=True)
        st.markdown(f'<div class="listing-card">{desc}</div>',
                     unsafe_allow_html=True)

        col_a, col_b = st.columns(2)
        with col_a:
            st.download_button(
                label="📄 Download as Text",
                data=desc,
                file_name=f"listing_v{i}.txt",
                mime="text/plain",
                key=f"dl_{i}",
            )
        with col_b:
            with st.expander("📋 Copy to Clipboard"):
                st.code(desc, language=None)

    st.success(
        f"{'Listing' if len(descriptions) == 1 else f'{len(descriptions)} versions'} "
        f"generated  •  {property_type}  •  {neighbourhood or city}"
    )

else:
    st.info("👈 Fill in the property details, then click **Generate Listing** to get started.")

# ── Footer ───────────────────────────────────────────────────
st.divider()
st.caption("Built with Azure OpenAI  •  © 2026 Lang Automation Solutions")
