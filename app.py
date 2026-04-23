"""
Real Estate Listing Generator — Streamlit Demo App
Full Marketing Package: MLS + Social Media + Email + Photo Captions
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
    .block-container { max-width: 760px; padding-top: 1.5rem; }

    .brand-header {
        background: linear-gradient(135deg, #1B4D7A 0%, #2E86C1 100%);
        color: white;
        padding: 1.8rem 2rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        text-align: center;
    }
    .brand-header h1 { margin: 0; font-size: 1.9rem; font-weight: 700; }
    .brand-header p { margin: 0.4rem 0 0 0; font-size: 0.95rem; opacity: 0.9; }

    .stButton > button {
        width: 100%;
        padding: 0.7rem 1rem;
        font-weight: 600;
        font-size: 1.05rem;
        border-radius: 8px;
    }

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

    .platform-badge {
        display: inline-block;
        padding: 0.2rem 0.7rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
        margin-right: 0.4rem;
    }
    .badge-instagram { background: #FCEDF2; color: #C13584; }
    .badge-facebook { background: #E8F0FE; color: #1877F2; }
    .badge-email { background: #FFF8E1; color: #F57C00; }
    .badge-mls { background: #E8F5E9; color: #2E7D32; }
    .badge-photo { background: #F3E5F5; color: #7B1FA2; }

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

# ── Cached engine ────────────────────────────────────────────
@st.cache_resource
def get_engine():
    return ListingEngine()

# ── Header ───────────────────────────────────────────────────
st.markdown("""
<div class="brand-header">
    <h1>🏠 AI Listing Generator</h1>
    <p>MLS descriptions, social posts, email campaigns, and photo captions — powered by Azure OpenAI</p>
</div>
""", unsafe_allow_html=True)

# ── Sidebar ──────────────────────────────────────────────────
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


# ── Helper: render a content card ────────────────────────────
def render_card(content, badge_class, badge_label, key_prefix):
    word_count = len(content.split())
    st.markdown(
        f'<span class="platform-badge {badge_class}">{badge_label}</span>'
        f'<span class="word-badge">{word_count} words</span>',
        unsafe_allow_html=True,
    )
    st.markdown(f'<div class="listing-card">{content}</div>', unsafe_allow_html=True)

    col_a, col_b = st.columns(2)
    with col_a:
        st.download_button(
            label="📄 Download",
            data=content,
            file_name=f"{key_prefix}.txt",
            mime="text/plain",
            key=f"dl_{key_prefix}",
        )
    with col_b:
        with st.expander("📋 Copy"):
            st.code(content, language=None)


# ── Tabs ─────────────────────────────────────────────────────
tab_pkg, tab_mls, tab_social, tab_email, tab_photo = st.tabs([
    "📦 Full Package", "📝 MLS Listing", "📱 Social Media",
    "📧 Email Blast", "📸 Photo Captions"
])

# ── TAB: Full Package ────────────────────────────────────────
with tab_pkg:
    st.markdown("**Generate your complete marketing kit in one click** — "
                "MLS description, Instagram post, Facebook post, and email blast.")

    if st.button("🚀 Generate Full Package", type="primary", key="btn_pkg"):
        engine = get_engine()
        prop = build_property_dict()

        with st.spinner("Creating your full marketing package..."):
            package = engine.generate_full_package(prop)

        st.session_state["package"] = package

    if "package" in st.session_state:
        pkg = st.session_state["package"]

        if pkg.get("mls"):
            st.subheader("MLS Listing")
            render_card(pkg["mls"], "badge-mls", "MLS", "pkg_mls")

        if pkg.get("instagram"):
            st.subheader("Instagram")
            render_card(pkg["instagram"], "badge-instagram", "Instagram", "pkg_insta")

        if pkg.get("facebook"):
            st.subheader("Facebook")
            render_card(pkg["facebook"], "badge-facebook", "Facebook", "pkg_fb")

        if pkg.get("email"):
            st.subheader("Email Blast")
            render_card(pkg["email"], "badge-email", "Email", "pkg_email")

        combined = ""
        for label, key in [("MLS LISTING", "mls"), ("INSTAGRAM", "instagram"),
                           ("FACEBOOK", "facebook"), ("EMAIL", "email")]:
            if pkg.get(key):
                combined += f"{'='*50}\n{label}\n{'='*50}\n\n{pkg[key]}\n\n\n"

        st.divider()
        st.download_button(
            label="📥 Download Entire Package",
            data=combined,
            file_name=f"marketing_package_{neighbourhood or city}.txt",
            mime="text/plain",
            key="dl_full_pkg",
        )

        st.success(f"Full package generated  •  {property_type}  •  "
                   f"{neighbourhood or city}")

# ── TAB: MLS Listing ────────────────────────────────────────
with tab_mls:
    st.markdown("**Generate a polished MLS listing description** — "
                "third person, no clichés, ready to paste.")

    num_variations = st.radio(
        "Versions to Generate", [1, 2, 3],
        horizontal=True, index=0, key="mls_variations",
    )

    if st.button("✨ Generate MLS Listing", type="primary", key="btn_mls"):
        engine = get_engine()
        prop = build_property_dict()

        with st.spinner("Writing listing..."):
            if num_variations == 1:
                descriptions = [engine.generate(prop)]
            else:
                descriptions = engine.generate_variations(prop, count=num_variations)

        st.session_state["mls_listings"] = descriptions

    if "mls_listings" in st.session_state:
        for i, desc in enumerate(st.session_state["mls_listings"], 1):
            if len(st.session_state["mls_listings"]) > 1:
                st.subheader(f"Version {i}")
            render_card(desc, "badge-mls", "MLS", f"mls_v{i}")

        st.success(
            f"{'Listing' if num_variations == 1 else f'{num_variations} versions'} "
            f"generated  •  {property_type}  •  {neighbourhood or city}"
        )

# ── TAB: Social Media ───────────────────────────────────────
with tab_social:
    st.markdown("**Generate social media posts** — "
                "ready to paste into Instagram or Facebook.")

    platform = st.radio(
        "Platform", ["Instagram", "Facebook", "Both"],
        horizontal=True, key="social_platform",
    )

    if st.button("📱 Generate Social Post", type="primary", key="btn_social"):
        engine = get_engine()
        prop = build_property_dict()

        with st.spinner("Writing social posts..."):
            results = {}
            if platform in ("Instagram", "Both"):
                results["instagram"] = engine.generate_social(prop, "instagram")
            if platform in ("Facebook", "Both"):
                results["facebook"] = engine.generate_social(prop, "facebook")

        st.session_state["social_posts"] = results

    if "social_posts" in st.session_state:
        posts = st.session_state["social_posts"]

        if posts.get("instagram"):
            st.subheader("Instagram")
            render_card(posts["instagram"], "badge-instagram", "Instagram", "social_insta")

        if posts.get("facebook"):
            st.subheader("Facebook")
            render_card(posts["facebook"], "badge-facebook", "Facebook", "social_fb")

        st.success(f"Social posts generated  •  {property_type}  •  "
                   f"{neighbourhood or city}")

# ── TAB: Email Blast ─────────────────────────────────────────
with tab_email:
    st.markdown("**Generate a new-listing email announcement** — "
                "subject line and body, ready to send.")

    if st.button("📧 Generate Email", type="primary", key="btn_email"):
        engine = get_engine()
        prop = build_property_dict()

        with st.spinner("Writing email..."):
            email_text = engine.generate_email(prop)

        st.session_state["email_blast"] = email_text

    if "email_blast" in st.session_state:
        render_card(st.session_state["email_blast"], "badge-email", "Email", "email_blast")

        st.success(f"Email generated  •  {property_type}  •  {neighbourhood or city}")

# ── TAB: Photo Captions ─────────────────────────────────────
with tab_photo:
    st.markdown(
        "**Upload a listing photo** and AI will analyze what's in the image "
        "to write a tailored social media caption. The property details from "
        "the sidebar are included for context."
    )

    uploaded_photo = st.file_uploader(
        "Upload a listing photo",
        type=["jpg", "jpeg", "png", "webp"],
        key="photo_upload",
        help="Upload a photo of the property — kitchen, living room, exterior, yard, etc.",
    )

    if uploaded_photo:
        st.image(uploaded_photo, use_container_width=True)

    photo_output = st.radio(
        "What to generate",
        ["Instagram Caption", "Facebook Post", "Photo Description", "All Three"],
        horizontal=True,
        key="photo_output_type",
    )

    if st.button("📸 Generate from Photo", type="primary", key="btn_photo"):
        if not uploaded_photo:
            st.warning("Please upload a listing photo first.")
        else:
            engine = get_engine()
            prop = build_property_dict()
            image_bytes = uploaded_photo.getvalue()

            results = {}

            with st.spinner("Analyzing photo and writing captions..."):
                if photo_output in ("Instagram Caption", "All Three"):
                    results["instagram"] = engine.generate_photo_caption(
                        image_bytes, prop, platform="instagram"
                    )
                if photo_output in ("Facebook Post", "All Three"):
                    results["facebook"] = engine.generate_photo_caption(
                        image_bytes, prop, platform="facebook"
                    )
                if photo_output in ("Photo Description", "All Three"):
                    results["description"] = engine.describe_photo(image_bytes)

            st.session_state["photo_results"] = results

    if "photo_results" in st.session_state:
        results = st.session_state["photo_results"]

        if results.get("instagram"):
            st.subheader("Instagram Caption")
            render_card(
                results["instagram"], "badge-instagram",
                "Instagram • Photo", "photo_insta"
            )

        if results.get("facebook"):
            st.subheader("Facebook Post")
            render_card(
                results["facebook"], "badge-facebook",
                "Facebook • Photo", "photo_fb"
            )

        if results.get("description"):
            st.subheader("Photo Description")
            render_card(
                results["description"], "badge-photo",
                "Description", "photo_desc"
            )

        st.success("Photo captions generated!")

# ── Footer ───────────────────────────────────────────────────
st.divider()
st.caption("Built with Azure OpenAI  •  © 2026 Lang Automation Solutions")
