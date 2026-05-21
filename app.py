import os
import streamlit as st
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

# Import utilities
from utils.nlp_processor import extract_trip_details
from utils.itinerary_generator import generate_itinerary
from utils.budget_calculator import estimate_expenses, format_inr, format_currency, get_budget_tier, CURRENCY_OPTIONS
from utils.hotel_recommender import recommend_hotels
from utils.db_manager import init_db, save_trip, get_all_trips, get_trip, delete_trip
from utils.pdf_generator import generate_trip_pdf

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="AI Smart Travel Planner",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize SQLite database
init_db()

# --- CUSTOM CSS FOR STUNNING MODERN AESTHETICS ---
st.markdown("""
<style>
    /* Global Styles & Google Font Import */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', 'Outfit', sans-serif;
    }

    /* Hide Streamlit Deploy button & hamburger menu */
    [data-testid="stToolbar"] { display: none !important; }
    [data-testid="stDecoration"] { display: none !important; }
    #MainMenu { visibility: hidden !important; }
    footer { visibility: hidden !important; }

    
    /* Header Styles with Gradients */
    .hero-title {
        background: linear-gradient(135deg, #6366f1 0%, #a855f7 50%, #ec4899 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-family: 'Outfit', sans-serif;
        font-weight: 800;
        font-size: 3rem;
        line-height: 1.3;
        padding: 10px 0;
        margin-bottom: 5px;
        text-align: center;
    }
    
    .hero-subtitle {
        color: #6b7280;
        font-size: 1.25rem;
        text-align: center;
        margin-bottom: 30px;
        font-weight: 400;
    }
    
    /* Glassmorphic Travel Cards (Saved Trips only) */
    .travel-card {
        background: rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 4px 24px rgba(0,0,0,0.12);
        transition: all 0.3s ease;
        margin-bottom: 12px;
    }
    
    .travel-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 30px rgba(99, 102, 241, 0.18);
        border-color: rgba(99, 102, 241, 0.4);
    }
    
    /* Dark mode subtitle */
    @media (prefers-color-scheme: dark) {
        .hero-subtitle { color: #94a3b8; }
    }
    
    /* Timeline styling for Activities */
    .timeline-container {
        position: relative;
        padding-left: 30px;
        border-left: 2px dashed #6366f1;
        margin-left: 15px;
        margin-bottom: 10px;
    }
    
    .timeline-item {
        position: relative;
        margin-bottom: 25px;
    }
    
    .timeline-badge {
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
        color: white !important;
        border-radius: 9999px;
        padding: 4px 12px;
        font-size: 0.75rem;
        font-weight: 700;
        display: inline-block;
        margin-bottom: 8px;
        box-shadow: 0 2px 4px rgba(79, 70, 233, 0.2);
    }
    
    .timeline-title {
        font-weight: 700;
        font-size: 1.05rem;
        margin-bottom: 4px;
        color: #f1f5f9 !important;
    }
    
    .timeline-loc {
        font-size: 0.85rem;
        font-style: italic;
        color: #818cf8 !important;
        margin-bottom: 8px;
    }
    
    .timeline-cost {
        font-size: 0.85rem;
        font-weight: 600;
        color: #34d399 !important;
    }
    
    .timeline-desc {
        font-size: 0.9rem;
        color: #cbd5e1 !important;
        margin-bottom: 5px;
    }
    
    .timeline-meta {
        font-size: 0.82rem;
        color: #94a3b8 !important;
    }
    
    .act-card {
        background: rgba(99, 102, 241, 0.07);
        border: 1px solid rgba(99, 102, 241, 0.2);
        border-radius: 10px;
        padding: 14px 16px;
        margin-bottom: 14px;
    }
    
    /* Hotel Recommendation Cards */
    .hotel-card {
        border-radius: 12px;
        border-left: 5px solid #6366f1;
        padding: 16px;
        background: rgba(255, 255, 255, 0.8);
        box-shadow: 0 4px 6px rgba(0,0,0,0.02);
        margin-bottom: 15px;
        transition: transform 0.2s;
    }
    
    .hotel-card:hover {
        transform: scale(1.01);
    }
    
    @media (prefers-color-scheme: dark) {
        .hotel-card {
            background: rgba(15, 23, 42, 0.4);
        }
    }
    
    .badge-recommend {
        background: #10b981;
        color: white;
        font-size: 0.7rem;
        font-weight: bold;
        padding: 2px 8px;
        border-radius: 4px;
        margin-left: 10px;
        vertical-align: middle;
    }
    
    /* Custom divider line */
    .custom-hr {
        height: 2px;
        background: linear-gradient(to right, transparent, #6366f1, transparent);
        border: none;
        margin: 20px 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Session States
if 'nlp_parsed' not in st.session_state:
    st.session_state.nlp_parsed = False
if 'extracted_details' not in st.session_state:
    st.session_state.extracted_details = None
if 'generated_itinerary' not in st.session_state:
    st.session_state.generated_itinerary = None
if 'generated_hotels' not in st.session_state:
    st.session_state.generated_hotels = None
if 'input_query' not in st.session_state:
    st.session_state.input_query = ""
if 'selected_currency' not in st.session_state:
    st.session_state.selected_currency = "INR — Indian Rupee (₹)"

# Sidebar Menu (Stunning custom metadata & database controls)
with st.sidebar:
    st.image("https://img.icons8.com/clouds/200/000000/airplane-take-off.png", width=100)
    st.markdown("<h2 style='font-family: Outfit; font-weight:700; margin-bottom: 2px;'>AI Trip Planner</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #6b7280; font-size:0.85rem; margin-top:0px;'>NLP & Gemini Powered Travel Companion</p>", unsafe_allow_html=True)
    st.markdown("<hr style='margin: 10px 0;'/>", unsafe_allow_html=True)
    
    # Storage and Active Session Stats
    st.markdown("### 💾 Local Storage Monitor")
    saved_trips = get_all_trips()
    st.metric("Total Saved Trips", f"{len(saved_trips)} Logs")
    
    st.markdown("<hr style='margin: 10px 0;'/>", unsafe_allow_html=True)
    
    # Safe reset database utility
    if st.button("🗑️ Clear Trip Storage", use_container_width=True, type="secondary"):
        try:
            import sqlite3
            from utils.db_manager import DB_PATH
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM trips")
            conn.commit()
            conn.close()
            st.toast("🗑️ All saved trip logs cleared successfully!", icon="✅")
            st.rerun()
        except Exception as e:
            st.error(f"Error resetting database: {e}")

# --- SINGLE-PAGE APPLICATION (SPA) MAIN FLOW ---

st.markdown("<div class='hero-title'>AI-Powered Smart Travel Planner</div>", unsafe_allow_html=True)
st.markdown("<div class='hero-subtitle'>Plan corporate travel with precision — generate optimized day-wise itineraries, curated hotel recommendations, and detailed budget reports tailored for business trips, all saved securely to your local records.</div>", unsafe_allow_html=True)
# 1. INTERACTIVE FORM CUSTOMIZER
# Only restore details if the user previously generated a plan (not on fresh load)
details = st.session_state.extracted_details or {}

st.markdown("### 🗺️ Plan Your Next Adventure")
with st.container(border=True):
    # Currency selector row
    curr_col, _ = st.columns([2, 3])
    with curr_col:
        currency_label = st.selectbox(
            "💱 Select Currency:",
            options=list(CURRENCY_OPTIONS.keys()),
            index=list(CURRENCY_OPTIONS.keys()).index(st.session_state.selected_currency)
        )
        st.session_state.selected_currency = currency_label

    curr_info   = CURRENCY_OPTIONS[currency_label]
    curr_symbol = curr_info["symbol"]
    curr_code   = curr_info["code"]
    curr_rate   = curr_info["rate"]          # 1 INR = X foreign units

    col_d1, col_d2, col_d3 = st.columns(3)
    with col_d1:
        destination = st.text_input("Destination City:", value=details.get("destination", ""), placeholder="e.g. Goa, Jaipur, Bangkok...")
    with col_d2:
        days = st.number_input("Number of Days (Duration):", min_value=1, max_value=30, value=int(details.get("days", 1)))
    with col_d3:
        # Show budget in selected currency; convert stored INR value for display
        stored_inr = details.get("budget", 1000)
        default_display = round(stored_inr * curr_rate, 2) if curr_code != "INR" else stored_inr
        budget_display = st.number_input(
            f"Total Trip Budget ({curr_symbol}):",
            min_value=0.01, max_value=10_000_000.0,
            value=float(default_display),
            format="%.2f" if curr_code != "INR" else "%.0f"
        )
        # Always store budget internally as INR
        budget_inr = budget_display / curr_rate if curr_code != "INR" else budget_display

    col_d4, col_d5 = st.columns(2)
    with col_d4:
        all_prefs = ["Beach", "Nature", "Nightlife", "History", "Cultural", "Spiritual", "Adventure", "Relaxation", "Luxury", "Foodie", "Shopping", "Wildlife"]
        current_prefs = [p.capitalize() for p in details.get("preferences", []) if p.capitalize() in all_prefs]
        for custom_p in details.get("preferences", []):
            cap_cp = custom_p.capitalize()
            if cap_cp not in all_prefs and len(cap_cp) < 20:
                all_prefs.append(cap_cp)
                current_prefs.append(cap_cp)
        preferences = st.multiselect("Travel Interests & Preferences:", options=all_prefs, default=current_prefs)
    with col_d5:
        vibe_options = ["Solo", "Friends", "Family", "Romantic"]
        default_vibe = details.get("trip_type", "").capitalize()
        vibe_idx = vibe_options.index(default_vibe) if default_vibe in vibe_options else 0
        trip_type = st.selectbox("Trip Companion / Vibe:", vibe_options, index=vibe_idx)

    # Submit generation trigger
    generate_col1, generate_col2 = st.columns([4, 1])
    with generate_col2:
        generate_btn = st.button("✨ Generate AI Plan", type="primary", use_container_width=True)
    
if generate_btn:
    final_details = {
        "destination": destination.strip(),
        "days": int(days),
        "budget": float(budget_inr),   # always stored in INR internally
        "preferences": preferences,
        "trip_type": trip_type
    }
    st.session_state.extracted_details = final_details
    
    # Silently load credentials from background server environment
    api_to_use = os.getenv("GEMINI_API_KEY", None)
    if not api_to_use or api_to_use.strip() == "":
        api_to_use = None
    
    # Execute AI Itinerary Call
    with st.spinner("🧠 Designing your custom day-wise travel itinerary..."):
        itinerary = generate_itinerary(
            destination=final_details["destination"],
            days=final_details["days"],
            budget=final_details["budget"],
            preferences=final_details["preferences"],
            api_key=api_to_use
        )
        st.session_state.generated_itinerary = itinerary
        
    with st.spinner("🏨 Recommending curated hotels matching your budget..."):
        hotels = recommend_hotels(
            destination=final_details["destination"],
            budget=final_details["budget"],
            trip_type=final_details["trip_type"],
            api_key=api_to_use
        )
        st.session_state.generated_hotels = hotels
    st.success("🎉 Your personalized itinerary is ready!")

# 3. RENDER GENERATED PLAN RESULT SECTION
if st.session_state.generated_itinerary:
    itinerary = st.session_state.generated_itinerary
    hotels = st.session_state.generated_hotels
    details = st.session_state.extracted_details
    
    overview = itinerary.get("trip_overview", {})
    dest_title = overview.get("destination", details["destination"]).upper()
    theme_title = overview.get("theme", ", ".join(details["preferences"]))
    
    st.markdown("<div class='custom-hr'></div>", unsafe_allow_html=True)
    st.markdown(f"<h2 style='text-align:center; font-family: Outfit; font-weight:800; background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>📋 YOUR AI-GENERATED ITINERARY TO {dest_title}</h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align:center; color:#6b7280; margin-top:-5px; font-weight:500;'>Theme: {theme_title} | Companion Style: {details['trip_type']}</p>", unsafe_allow_html=True)
    
    # Display highly premium commercial visual badge
    st.markdown("""
        <div style='text-align: center; margin-bottom: 20px;'>
            <span style='background: linear-gradient(135deg, #e0e7ff 0%, #f3e8ff 100%); color: #4f46e5; border: 1px solid #c7d2fe; font-size: 0.85rem; padding: 6px 18px; border-radius: 9999px; font-weight: 700; display: inline-block; box-shadow: 0 4px 6px rgba(99, 102, 241, 0.08);'>
                ✨ Smart AI-Optimized Plan
            </span>
        </div>
    """, unsafe_allow_html=True)
    
    # Action Bar (Save & Download PDF)
    action_col1, action_col2, action_col3, action_col4 = st.columns([1, 1, 2, 1])
    
    with action_col1:
        if st.button("💾 Save Trip Log", use_container_width=True):
            trip_id = save_trip(
                destination=details["destination"],
                days=details["days"],
                budget=details["budget"],
                preferences=details["preferences"],
                itinerary_data=itinerary
            )
            st.toast(f"💾 Trip saved to local logs (ID: {trip_id})!", icon="✅")
            st.rerun()
            
    with action_col2:
        pdf_bytes = generate_trip_pdf(itinerary, hotels)
        st.download_button(
            label="📥 Download PDF",
            data=pdf_bytes,
            file_name=f"AI_Itinerary_{details['destination'].replace(' ', '_')}.pdf",
            mime="application/pdf",
            use_container_width=True
        )
        
    st.markdown("<br/>", unsafe_allow_html=True)
    
    # Resolve currency for display (use session state after form submit)
    _ci    = CURRENCY_OPTIONS.get(st.session_state.selected_currency, CURRENCY_OPTIONS["INR — Indian Rupee (₹)"])
    _sym   = _ci["symbol"]
    _code  = _ci["code"]
    _rate  = _ci["rate"]
    def fmt(inr_val): return format_currency(inr_val * _rate, _sym, _code)

    # Metrics
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    with m_col1:
        st.metric("Total Duration", f"{overview.get('days', details['days'])} Days")
    with m_col2:
        st.metric("Allocated Budget", fmt(overview.get("budget", details["budget"])))
    with m_col3:
        total_est = itinerary.get("budget_breakdown", {}).get("total_estimated_cost", details["budget"])
        st.metric("Estimated Cost", fmt(total_est))
    with m_col4:
        st.metric("Budget Class", get_budget_tier(details["budget"], details["days"]))
        
    st.markdown("<br/>", unsafe_allow_html=True)
    
    # Double Column Layout for detailed content
    layout_col1, layout_col2 = st.columns([3, 2])
    
    with layout_col1:
        # Robustly extract day-wise itinerary matching any common LLM key variation
        day_wise = (
            itinerary.get("day_wise_itinerary") or 
            itinerary.get("itinerary") or 
            itinerary.get("days") or 
            itinerary.get("day_wise") or 
            []
        )
        
        # Local fallback if Gemini returned empty itineraries to guarantee the page is never blank
        if not day_wise:
            from utils.itinerary_generator import get_demo_itinerary
            fallback = get_demo_itinerary(details["destination"], int(details["days"]), float(details["budget"]), details["preferences"])
            day_wise = fallback.get("day_wise_itinerary", [])
            
        # Tabs for days
        day_labels = [f"📅 Day {d.get('day', i+1)}" for i, d in enumerate(day_wise)]
        
        if day_wise:
            day_tabs = st.tabs(day_labels)
            
            for idx, tab in enumerate(day_tabs):
                d_info = day_wise[idx]
                with tab:
                    day_num = d_info.get("day") or (idx + 1)
                    day_theme = d_info.get("theme") or d_info.get("title") or "Sightseeing Schedule"
                    st.markdown(f"#### 🌅 Day {day_num} — {day_theme}")
                    
                    activities = d_info.get("activities", [])
                    
                    if not activities:
                        st.info("🗓️ **Free Day** — No fixed activities scheduled. Enjoy leisure time, spontaneous exploration, or rest at your own pace!")
                    else:
                        for act_info in activities:
                            # Robustly extract fields
                            rating_val = act_info.get("rating") or act_info.get("tripadvisor_rating") or 4.5
                            reviews_val = act_info.get("reviews_count") or act_info.get("tripadvisor_reviews") or "1,200"
                            act_title = act_info.get("activity") or act_info.get("name") or "Explore Local Spot"
                            act_loc = act_info.get("location") or act_info.get("landmark") or details["destination"]
                            act_desc = act_info.get("description") or act_info.get("desc") or "Enjoy scenic viewpoints and local heritage routes."
                            act_time = act_info.get("time") or act_info.get("time_slot") or "Morning"
                            act_cost = act_info.get("cost") or act_info.get("cost_estimation") or 0
                            cost_lbl = format_inr(act_cost) if act_cost > 0 else "Free / Included"

                            try:
                                rating_num = int(float(rating_val))
                            except Exception:
                                rating_num = 4
                            stars = "⭐" * rating_num

                            with st.container(border=True):
                                time_col, title_col = st.columns([1, 4])
                                with time_col:
                                    st.markdown(f"""
                                    <span style='
                                        background: linear-gradient(135deg,#4f46e5,#7c3aed);
                                        color:white; border-radius:20px; padding:4px 12px;
                                        font-size:0.75rem; font-weight:700; white-space:nowrap;
                                    '>{act_time}</span>""", unsafe_allow_html=True)
                                with title_col:
                                    st.markdown(f"**{act_title}**")
                                
                                st.caption(f"📍 {act_loc}")
                                st.write(act_desc)
                                
                                meta_c1, meta_c2 = st.columns(2)
                                with meta_c1:
                                    st.markdown(f"{stars} **{rating_val}** &nbsp; *({reviews_val} reviews)*", unsafe_allow_html=True)
                                with meta_c2:
                                    st.markdown(f"💰 **{cost_lbl}**")
                    
                    # Food recommendations
                    food_recs = d_info.get("food_recommendations", [])
                    if food_recs:
                        st.markdown("**🍽️ Where to Eat Today**")
                        food_cols = st.columns(len(food_recs)) if len(food_recs) <= 3 else st.columns(3)
                        for fi, f in enumerate(food_recs[:3]):
                            with food_cols[fi]:
                                st.markdown(f"""
                                <div style='background:rgba(16,185,129,0.1); border:1px solid rgba(16,185,129,0.25);
                                    border-radius:10px; padding:10px 12px; text-align:center;'>
                                    <div style='font-size:1.2rem;'>🍴</div>
                                    <div style='font-weight:700; font-size:0.82rem; margin:4px 0;'>{f.get('name','Eatery')}</div>
                                    <div style='font-size:0.75rem; opacity:0.8;'>{f.get('type','')}</div>
                                    <div style='font-size:0.72rem; color:#34d399; font-weight:600;'>{f.get('cost_rating','')}</div>
                                </div>""", unsafe_allow_html=True)
                    
    with layout_col2:
        # Hotel Recommendations (At the top of the right column, replacing the map!)
        st.markdown("### 🏨 Recommended Accommodations")
        
        if hotels:
            for h in hotels:
                rec_banner = "<span class='badge-recommend'>Matches Companion Vibe</span>" if h.get("recommended_for_you") else ""
                features_list = "".join([f"<span style='background-color:#eff6ff; color:#1e40af; font-size:0.75rem; padding: 2px 8px; border-radius:12px; margin-right:5px; font-weight:600; display:inline-block; margin-top:5px;'>💡 {feat}</span>" for feat in h.get("features", [])])
                
                st.markdown(f"""
                <div class='hotel-card'>
                    <div style='display: flex; justify-content: space-between; align-items: baseline;'>
                        <h4 style='margin-bottom:2px; font-weight:700;'>{h.get('name')} {rec_banner}</h4>
                        <span style='color: #f59e0b; font-weight:700;'>{'⭐' * int(round(h.get('rating', 4.5)))} ({h.get('rating')})</span>
                    </div>
                    <p style='font-size: 0.8rem; font-weight:600; color: #6366f1; margin: 4px 0;'>Est. Rate: {h.get('price_range')} | Category: <b>{h.get('category')}</b></p>
                    <p style='font-size: 0.85rem; color:#475569;'>{h.get('description')}</p>
                    <div style='margin-top:8px;'>
                        {features_list}
                    </div>
                </div>
                """, unsafe_allow_html=True)

        # Smart Budgeting Breakdowns (Below the hotels section)
        st.markdown("### 📊 Budget Breakdown Estimations")
        breakdown = itinerary.get("budget_breakdown", {})
        
        categories_map = {
            "hotel": ("🏨 Accommodation", "#4f46e5"),
            "food": ("🍔 Food & Dining", "#10b981"),
            "transportation": ("🛵 Transit & Transport", "#f59e0b"),
            "attractions_activities": ("🎫 Attractions & Activities", "#ec4899"),
            "shopping_misc": ("🛍️ Shopping & Extras", "#8b5cf6")
        }
        
        # Display category progress bars & breakdown cards
        with st.container(border=True):
            for cat_key, (cat_label, cat_color) in categories_map.items():
                cost = breakdown.get(cat_key, 0)
                pct = (cost / details["budget"]) if details["budget"] > 0 else 0
                pct = min(1.0, max(0.0, pct))
                
                # Visual breakdown item
                st.markdown(f"""
                    <div style='display: flex; justify-content: space-between; margin-bottom: 4px; font-size: 0.9rem;'>
                        <span style='font-weight:600;'>{cat_label}</span>
                        <span style='font-weight:700; color:{cat_color};'>{fmt(cost)} ({pct*100:.0f}%)</span>
                    </div>
                """, unsafe_allow_html=True)
                st.progress(pct)
            
        # Transit suggestions
        st.markdown("### 🛵 Transportation Advice")
        trans = itinerary.get("transport_suggestions", {})
        st.info(f"🛵 **Local Commute**: {trans.get('local_commute', 'Renting a scooter/scooty is the best budget-friendly option.')}")
        st.info(f"✈️ **Reaching Destination**: {trans.get('interstate_commute', 'Fly in or check overnight express train tickets.')}")
        
        # Essential Tips
        st.markdown("### 🎒 Essential Packing & Travel Tips")
        tips = itinerary.get("essential_tips", [])
        for tip in tips:
            st.warning(f"💡 {tip}")

# 4. SAVED TRAVEL LOGS GALLERY (Always visible at the bottom of the page)
st.markdown("<div class='custom-hr'></div>", unsafe_allow_html=True)
st.markdown("<h2 style='font-family: Outfit; font-weight:700;'>📁 Saved Travel Logs</h2>", unsafe_allow_html=True)
st.markdown("Access, manage, and view all itineraries you previously saved to the SQLite database.")

if not saved_trips:
    st.markdown("""
    <div style='text-align: center; padding: 40px;'>
        <img src='https://img.icons8.com/clouds/100/000000/empty-folder.png' width='100'/>
        <h3>No Saved Trips Found</h3>
        <p style='color:#6b7280;'>You haven't saved any itineraries yet. Generate a new trip and save it to review it here!</p>
    </div>
    """, unsafe_allow_html=True)
else:
    # Display saved trips in 3 columns per row
    rows = [saved_trips[i:i + 3] for i in range(0, len(saved_trips), 3)]
    
    for row in rows:
        cols = st.columns(3)
        for idx, trip in enumerate(row):
            with cols[idx]:
                pref_badges = " ".join([f"<span style='background-color:#eff6ff; color:#1e40af; font-size:0.7rem; padding: 2px 8px; border-radius:10px; font-weight:600; margin-right:4px;'>#{p.capitalize()}</span>" for p in trip["preferences"][:3]])
                
                st.markdown(f"""
                <div class='travel-card' style='height: 250px; display: flex; flex-direction: column; justify-content: space-between; margin-bottom: 10px;'>
                    <div>
                        <div style='display:flex; justify-content:space-between; align-items:flex-start;'>
                            <h3 style='margin:0; font-family: Outfit; font-weight:700;'>✈️ {trip['destination'].upper()}</h3>
                            <span style='background:#f3f4f6; padding: 2px 8px; border-radius:4px; font-size:0.75rem; font-weight:bold;'>{trip['days']} Days</span>
                        </div>
                        <p style='font-size:0.9rem; color:#6366f1; font-weight:700; margin: 8px 0 4px 0;'>Budget: {format_inr(trip['budget'])}</p>
                        <p style='font-size:0.75rem; color:#94a3b8; margin: 0 0 10px 0;'>Saved: {trip['created_at'][:10]}</p>
                        <div style='display:flex; flex-wrap:wrap; gap:4px;'>
                            {pref_badges}
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                btn_col1, btn_col2 = st.columns(2)
                with btn_col1:
                    if st.button("👀 View Plan", key=f"view_{trip['id']}", use_container_width=True):
                        st.session_state.extracted_details = {
                            "destination": trip["destination"],
                            "days": trip["days"],
                            "budget": trip["budget"],
                            "preferences": trip["preferences"],
                            "trip_type": trip["itinerary_data"].get("trip_overview", {}).get("companion_style", "Friends")
                        }
                        st.session_state.generated_itinerary = trip["itinerary_data"]
                        st.session_state.nlp_parsed = True
                        
                        # Load associated hotels for loaded active view
                        st.session_state.generated_hotels = recommend_hotels(
                            destination=trip["destination"],
                            budget=trip["budget"],
                            trip_type=trip["itinerary_data"].get("trip_overview", {}).get("companion_style", "Friends"),
                            api_key=os.getenv("GEMINI_API_KEY", None)
                        )
                        st.toast("📂 Itinerary loaded from SQLite records!", icon="📂")
                        st.rerun()
                with btn_col2:
                    if st.button("🗑️ Delete", key=f"delete_{trip['id']}", type="secondary", use_container_width=True):
                        delete_trip(trip["id"])
                        st.toast(f"🗑️ Trip log #{trip['id']} deleted.", icon="🗑️")
                        st.rerun()
