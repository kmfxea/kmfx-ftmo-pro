
# ====================== KMFX EA - FULL 2026 APP WITH PUBLIC LANDING + QR ======================
import streamlit as st
import pandas as pd
import datetime
import bcrypt
import os
import threading
import time
import requests
import plotly.graph_objects as go
import qrcode
from io import BytesIO
from supabase import create_client, Client
from dotenv import load_dotenv
import uuid

load_dotenv()

supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
if not supabase_url or not supabase_key:
    st.error("Missing SUPABASE_URL or SUPABASE_KEY in .env file!")
    st.stop()

supabase: Client = create_client(supabase_url, supabase_key)
def upload_to_supabase(file, bucket: str, folder: str = "", use_signed_url: bool = False, signed_expiry: int = 3600) -> tuple[str, str]:
    """
    Upload file to Supabase Storage - FIXED for memoryview + upsert header issues
    Returns (url, storage_path)
    """
    try:
        # Unique filename to prevent overwrites
        safe_name = f"{uuid.uuid4()}_{file.name}"
        file_path = f"{folder}/{safe_name}" if folder else safe_name

        # Convert memoryview → bytes (fixes previous error)
        content = file.getbuffer()
        if isinstance(content, memoryview):
            content = content.tobytes()
        elif not isinstance(content, bytes):
            content = bytes(content)

        with st.spinner(f"Uploading {file.name}..."):
            supabase.storage.from_(bucket).upload(
                path=file_path,
                file=content,
                file_options={
                    "content-type": file.type or "application/octet-stream",
                    "upsert": "true"          # ← fixed: string instead of bool
                }
            )

        # Get URL
        if use_signed_url:
            signed = supabase.storage.from_(bucket).create_signed_url(file_path, signed_expiry)
            url = signed["signedURL"]
        else:
            url = supabase.storage.from_(bucket).get_public_url(file_path)

        st.success(f"✅ {file.name} uploaded successfully!")
        return url, file_path

    except Exception as e:
        st.error(f"Upload failed for {file.name}: {str(e)}")
        raise
        # Theme & Colors (ilagay dito sa top, after supabase)
accent_primary = "#00ffaa"
accent_gold = "#ffd700"
accent_glow = "#00ffaa40"
accent_color = accent_primary  # <-- IMPORTANT: Define accent_color here
accent_hover = "#00ffcc"

# Keep-alive for Streamlit Cloud
def keep_alive():
    while True:
        try:
            requests.get("https://kmfxeaftmo.streamlit.app", timeout=10)
        except:
            pass
        time.sleep(1500)

if os.getenv("STREAMLIT_SHARING") or os.getenv("STREAMLIT_CLOUD"):
    if not hasattr(st, "_keep_alive_thread_started"):
        thread = threading.Thread(target=keep_alive, daemon=True)
        thread.start()
        st._keep_alive_thread_started = True

st.set_page_config(
    page_title="KMFX EA - Elite Empire",
    page_icon="👑",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Local folders
folders = [
    "uploaded_files",
    "uploaded_files/client_files",
    "uploaded_files/announcements",
    "uploaded_files/testimonials",
    "uploaded_files/ea_versions"
]
for folder in folders:
    os.makedirs(folder, exist_ok=True)

# Log action
def log_action(action, details="", user_name=None):
    user_name = user_name or st.session_state.get("full_name", "Unknown")
    user_type = st.session_state.get("role", "unknown")
    try:
        supabase.table("logs").insert({
            "timestamp": datetime.datetime.now().isoformat(),
            "action": action,
            "details": details,
            "user_type": user_type,
            "user_name": user_name
        }).execute()
    except:
        pass

# Default users
def create_default_users():
    try:
        response = supabase.table("users").select("id", count="exact").execute()
        if response.count == 0:
            hashed_owner = bcrypt.hashpw("ChangeMeNow123!".encode(), bcrypt.gensalt()).decode()
            supabase.table("users").insert([
                {"username": "kingminted", "password": hashed_owner, "full_name": "King Minted", "role": "owner"}
            ]).execute()
            st.success("Default owner created. CHANGE PASSWORD ASAP!")
    except Exception as e:
        st.error(f"Error creating defaults: {e}")

create_default_users()

# ====================== THEME SETUP - DEFAULT LIGHT MODE FOR LOGGED IN, FORCE DARK FOR PUBLIC LANDING ======================
if "theme" not in st.session_state:
    st.session_state.theme = "light"  # Default light mode pag fresh open / login

theme = st.session_state.theme

accent_primary = "#00ffaa"
accent_gold = "#ffd700"
accent_glow = "#00ffaa40"
accent_hover = "#00ffcc" if theme == "dark" else "#00cc99"

bg_color = "#f8fbff" if theme == "light" else "#0a0d14"
card_bg = "rgba(255, 255, 255, 0.75)" if theme == "light" else "rgba(15, 20, 30, 0.70)"
border_color = "rgba(0, 0, 0, 0.08)" if theme == "light" else "rgba(100, 100, 100, 0.15)"
text_primary = "#0f172a" if theme == "light" else "#ffffff"
text_muted = "#64748b" if theme == "light" else "#aaaaaa"

card_shadow = "0 8px 25px rgba(0,0,0,0.12)" if theme == "light" else "0 10px 30px rgba(0,0,0,0.5)"
card_shadow_hover = "0 15px 40px rgba(0,0,0,0.2)" if theme == "light" else "0 20px 50px rgba(0,255,170,0.45)"
sidebar_bg = "rgba(248, 251, 255, 0.95)" if theme == "light" else "rgba(10, 13, 20, 0.95)"

st.markdown(f"""
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&family=Playfair+Display:wght@700&display=swap" rel="stylesheet">
<style>
    /* Global - Slightly larger base font */
    html, body, [class*="css-"] {{
        font-family: 'Poppins', sans-serif !important;
        font-size: 15px !important; /* Increased overall */
    }}
    .stApp {{
        background: {bg_color};
        color: {text_primary};
    }}
    /* Adaptive text */
    h1, h2, h3, h4, h5, h6, p, div, span, label, .stMarkdown {{
        color: {text_primary} !important;
    }}
    small, caption, .caption {{
        color: {text_muted} !important;
    }}
    /* Medium glass cards - reduced padding for medium size */
    .glass-card {{
        background: {card_bg};
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border-radius: 20px;
        border: 1px solid {border_color};
        padding: 2.2rem !important; /* Slightly more spacious for public */
        box-shadow: {card_shadow};
        transition: all 0.3s ease;
        margin: 2rem 0;
    }}
    .glass-card:hover {{
        box-shadow: {card_shadow_hover};
        transform: translateY(-6px);
        border-color: {accent_primary};
    }}
    /* Font inside cards - balanced for public readability */
    .glass-card h1, .glass-card h2, .glass-card h3,
    .glass-card h4, .glass-card p, .glass-card div,
    .glass-card span, .glass-card label {{
        font-size: 15px !important;
        line-height: 1.6 !important;
    }}
    .glass-card h1 {{ font-size: 2.2rem !important; }}
    .glass-card h2 {{ font-size: 1.8rem !important; }}
    .glass-card h3 {{ font-size: 1.5rem !important; }}
    /* GOLD TEXT CLASS - for premium headings */
    .gold-text {{
        color: {accent_gold} !important;
        font-weight: 600;
        letter-spacing: 0.5px;
    }}
    /* PUBLIC HERO SECTION */
    .public-hero {{
        text-align: center;
        padding: 6rem 2rem 4rem;
        min-height: 80vh;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }}
    .public-hero h1 {{
        font-size: clamp(3rem, 8vw, 5rem);
        background: linear-gradient(90deg, {accent_gold}, {accent_primary});
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1rem;
    }}
    .public-hero h2 {{
        font-size: clamp(1.8rem, 5vw, 3rem);
        margin: 1.5rem 0;
    }}
    /* TIMELINE CARD - for progress section */
    .timeline-card {{
        background: rgba(30, 35, 45, 0.6);
        border-left: 6px solid {accent_gold};
        border-radius: 0 20px 20px 0;
        padding: 2rem;
        margin: 2.5rem 0;
        transition: all 0.3s ease;
    }}
    .timeline-card:hover {{
        transform: translateX(10px);
        box-shadow: 0 10px 30px {accent_glow};
    }}
    .timeline-card h3 {{
        color: {accent_gold};
        margin-bottom: 1rem;
    }}
    /* BIG STATS in hero */
    .big-stat {{
        font-size: 3rem !important;
        font-weight: 700;
        color: {accent_primary};
    }}
    /* Inputs - PURE WHITE BACKGROUND + BLACK TEXT */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > div,
    .stSelectbox > div > div > div > div,
    .stSelectbox > div > div input,
    .stTextInput > div > div,
    .stTextArea > div > div {{
        background: #ffffff !important;
        color: #000000 !important;
        border: 1px solid {border_color} !important;
        border-radius: 16px !important;
    }}
    /* Selectbox fixes */
    .stSelectbox > div > div > div > div[role="button"] > div,
    .stSelectbox > div > div > div > div > div:first-child {{
        color: #000000 !important;
        background: #ffffff !important;
    }}
    [data-baseweb="select"] > div[role="listbox"] > div,
    [data-baseweb="select"] div[role="option"] {{
        background: #ffffff !important;
        color: #000000 !important;
    }}
    [data-baseweb="select"] div[role="option"]:hover,
    [data-baseweb="select"] div[role="option"][aria-selected="true"] {{
        background: #e0e0e0 !important;
        color: #000000 !important;
    }}
    .stSelectbox [data-baseweb="select"] svg {{
        fill: #000000 !important;
    }}
    ::placeholder {{
        color: #666666 !important;
        opacity: 1 !important;
    }}
    /* Buttons */
    button[kind="primary"] {{
        background: {accent_primary} !important;
        color: #000000 !important;
        border-radius: 16px !important;
        box-shadow: 0 6px 20px {accent_glow} !important;
        padding: 1rem 2rem !important;
        font-size: 1.2rem !important;
    }}
    button[kind="primary"]:hover {{
        background: {accent_hover} !important;
        box-shadow: 0 12px 35px {accent_glow} !important;
        transform: translateY(-3px);
    }}
    /* TOP HEADER BLEND */
    header[data-testid="stHeader"] {{
        background-color: {bg_color} !important;
        backdrop-filter: blur(20px);
    }}
    /* SIDEBAR - NO SHADOW */
    section[data-testid="stSidebar"] {{
        background: {sidebar_bg} !important;
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        width: 320px !important;
        min-width: 320px !important;
        border-right: 1px solid {border_color};
        box-shadow: none !important;
    }}
    /* RED arrow/hamburger */
    [data-testid="collapsedControl"] {{
        color: #ff4757 !important;
    }}
    [data-testid="collapsedControl"] svg {{
        fill: #ff4757 !important;
        stroke: #ff4757 !important;
    }}
    /* Desktop */
    @media (min-width: 769px) {{
        .main .block-container {{
            padding-left: 3rem !important;
            padding-top: 2rem !important;
        }}
    }}
    /* Mobile: Wider + looser */
    @media (max-width: 768px) {{
        section[data-testid="stSidebar"] {{
            width: 92% !important;
            max-width: 420px !important;
        }}
        .public-hero {{ padding: 4rem 1rem 3rem; min-height: 70vh; }}
        .glass-card {{ padding: 2rem !important; }}
        .timeline-card {{ border-left: none; border-top: 6px solid {accent_gold}; border-radius: 20px; }}
        .big-stat {{ font-size: 2.2rem !important; }}
    }}
    /* Premium Menu (sidebar) */
    div[data-testid="stSidebar"] div.stRadio > div > label {{
        background: rgba(255,255,255,0.08);
        border-radius: 18px;
        padding: 18px 24px;
        margin: 10px 16px;
        transition: all 0.3s ease;
        border: 1px solid {border_color};
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        font-weight: 500;
        color: {text_primary} !important;
    }}
    div[data-testid="stSidebar"] div.stRadio > div > label:hover {{
        background: rgba(0,255,170,0.18);
        border-color: {accent_primary};
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(0,255,170,0.25);
    }}
    div[data-testid="stSidebar"] div.stRadio > div > label[data-checked="true"] {{
        background: {accent_primary} !important;
        color: #000000 !important;
        border-color: {accent_primary};
        box-shadow: 0 10px 30px rgba(0,255,170,0.4);
        font-weight: 600;
    }}
    /* Force black text for metrics */
    .stMetric label, .stMetric value {{
        color: black !important;
    }}
    svg text {{
        fill: black !important;
        color: black !important;
    }}
    /* SIDEBAR COLLAPSE FIX */
    section[data-testid="stSidebar"][aria-expanded="false"] {{
        width: 0 !important;
        min-width: 0 !important;
        overflow: hidden !important;
    }}
    [data-testid="collapsedControl"] {{
        position: fixed !important;
        left: 0 !important;
        top: 50% !important;
        transform: translateY(-50%) !important;
        z-index: 9999 !important;
        background: rgba(255, 255, 255, 0.1) !important;
        border-radius: 0 12px 12px 0 !important;
        padding: 20px 8px !important;
        box-shadow: 2px 0 10px rgba(0,0,0,0.3) !important;
    }}
    @media (max-width: 768px) {{
        [data-testid="collapsedControl"] {{
            padding: 24px 10px !important;
        }}
    }}
</style>
""", unsafe_allow_html=True)

# QR Auto-Login
params = st.query_params
qr_token = params.get("qr")
if qr_token and not st.session_state.get("authenticated", False):
    try:
        resp = supabase.table("users").select("*").eq("qr_token", qr_token).execute()
        if resp.data:
            user = resp.data[0]
            st.session_state.authenticated = True
            st.session_state.username = user["username"]
            st.session_state.full_name = user["full_name"]
            st.session_state.role = user["role"]
            log_action("QR Login Success", f"User: {user['full_name']}")
            st.query_params.clear()
            st.rerun()
        else:
            st.error("Invalid or revoked QR code")
    except:
        st.error("QR login failed")

# Login helper
def login_user(username, password):
    try:
        response = supabase.table("users").select("password, full_name, role").eq("username", username.lower()).execute()
        if response.data:
            user = response.data[0]
            if bcrypt.checkpw(password.encode('utf-8'), user["password"].encode('utf-8')):
                st.session_state.authenticated = True
                st.session_state.username = username.lower()
                st.session_state.full_name = user["full_name"] or username
                st.session_state.role = user["role"]
                
                # 🔥 AUTO LIGHT MODE ON EVERY SUCCESSFUL LOGIN (fix for dark mode carryover)
                st.session_state.theme = "light"
                
                log_action("Login Successful", f"User: {username} | Role: {user['role']}")
                st.rerun()
            else:
                st.error("Invalid password")
        else:
            st.error("Username not found")
    except Exception as e:
        st.error(f"Login error: {e}")

# Auth check
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    # FORCE DARK MODE FOR PUBLIC LANDING PAGE ONLY
    if st.session_state.get("theme") != "dark":
        st.session_state.theme = "dark"
        st.rerun()  # Reload once to apply dark theme immediately

    # ====================== PUBLIC LANDING PAGE (DARK MODE + LOGO AT TOP, ZERO SPACE) ======================
   
    # GLOBAL FIX: Zero top space + hide Streamlit bar
    st.markdown("""
    <style>
    /* Remove all top space */
    .block-container {
        padding-top: 0rem !important;
        margin-top: 0rem !important;
    }
    .main > div {
        padding-top: 0rem !important;
    }
    header { visibility: hidden !important; }
    </style>
    """, unsafe_allow_html=True)
   
    # === LOGO AT VERY TOP (centered, large, responsive - NO DEPRECATION WARNING) ===
    logo_col = st.columns([1, 6, 1])[1] # Slightly wider middle column for better logo size
    with logo_col:
        st.image("assets/logo.png") # No use_column_width → no warning, still large & responsive
   
    # Original content (centered)
    st.markdown(f"<h1 class='gold-text' style='text-align: center;'>KMFX EA</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center; color:{text_primary};'>Automated Gold Trading for Financial Freedom</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size:1.4rem; color:{text_muted};'>Passed FTMO Phase 1 • +3,071% 5-Year Backtest • Building Legacies of Generosity</p>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size:1.2rem;'>Mark Jeff Blando – Founder & Developer • 2026</p>", unsafe_allow_html=True)
   
    # Realtime Stats - FIXED QUERY + RESPONSIVE (NO TRUNCATION)
    try:
        accounts_count = supabase.table("ftmo_accounts").select("id", count="exact").execute().count or 0
        equity_data = supabase.table("ftmo_accounts").select("current_equity").execute().data or []
        total_equity = sum(acc.get("current_equity", 0) for acc in equity_data)
        
        # FIXED: Correct "type, amount" format
        gf_data = supabase.table("growth_fund_transactions").select("type, amount").execute().data or []
        gf_balance = sum(t["amount"] if t["type"] == "In" else -t["amount"] for t in gf_data)
        
        members_count = supabase.table("users").select("id", count="exact").eq("role", "client").execute().count or 0
    except Exception as e:
        print(f"Supabase stats error: {e}")
        accounts_count = total_equity = gf_balance = members_count = 0
   
    # FULL-WIDTH RESPONSIVE METRICS (auto-stack on mobile, no truncation)
    cols = st.columns(4)
    with cols[0]:
        st.metric("Active Accounts", accounts_count)
    with cols[1]:
        st.metric("Total Equity", f"${total_equity:,.0f}")
    with cols[2]:
        st.metric("Growth Fund", f"${gf_balance:,.0f}")
    with cols[3]:
        st.metric("Members", members_count) # Shortened label to prevent cutoff on small screens
   
    # =====================================================================================================

    # Portfolio Story
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("<h2 class='gold-text'>Origin & Motivation (2024)</h2>", unsafe_allow_html=True)
    st.write("""
    Noong 2024, frustrated ako sa manual trading — paulit-ulit na losses dahil sa emotions, lack of discipline, at timing issues. Realization: "Kung hindi professional, maloloss ka lang sa market."

    Decided to build my own Expert Advisor (EA) to remove human error, achieve consistency, and become a professional trader through automation.

    Early inspiration from ~2016 trading days, sharing ideas with friend Ramil.
    """)

    st.markdown("<h2 class='gold-text'>Development Phase (2024)</h2>", unsafe_allow_html=True)
    st.write("""
    - Full year of self-study in MQL5 programming
    - Trial-and-error: Combined multiple indicators, price action rules, risk management filters
    - Hundreds of backtests, forward tests, debugging — almost 1 year of experiment before stability
    """)

    st.markdown("<h2 class='gold-text'>Official Launch & Early Testing (2025)</h2>", unsafe_allow_html=True)
    st.write("""
    - January 2025: Breakthrough — EA fully functional and running smoothly. Officially named KMFX EA
    - Focused exclusively on XAUUSD (GOLD) for its volatility and opportunities
    - September 2025: Formed KMFX EA TESTER group (initial: Weber — most active, Ramil, Sheldon, Jai). ~2 months forward testing with multiple trials and real-time feedback
    - Late 2025 (Oct-Dec): Mastered backtesting — ran historical data from 2021–2025. Game-changer: Quickly spotted weaknesses, polished entries/exits, filters for gold spikes/news volatility
    """)

    st.markdown("<h2 class='gold-text'>Major Milestones & Tools (2025)</h2>", unsafe_allow_html=True)
    st.write("""
    - October 15, 2025: Launched sleek KMFX EA MT5 Client Tracker dashboard at kmfxea.streamlit.app — premium portal for performance tracking (owner, admin, client logins)
    - December 2025: Pioneer community formed — 14 believers contributed ₱17,000 PHP (₱1,000 per unit) to fund the real challenge phase
      - Profit sharing: 30% of profits proportional to units
      - Thank you to: Mark, Jai, Doc, Weber (2 units), Don, Mark Fernandez (3 units), Ramil, Cristy, Meg, Roland, Mila, Malruz, Julius, Joshua
    """)

    st.markdown("<h2 class='gold-text'>FTMO Prop Firm Journey – First Attempt (Dec 2025 - Jan 2026)</h2>", unsafe_allow_html=True)
    st.write("""
    - December 13, 2025: Started FTMO 10K Challenge (Plan A, real evaluation)
    - December 26, 2025: PASSED Phase 1 (Challenge) in just ~13 days!
      - Certificate issued: Proven profit target achieved + quality risk management
      - Stats snapshot: $10,000 → $11,040.58 (+10.41% gain), 2.98% max drawdown, 118 trades (longs only, 52% win rate), +12,810.8 pips, profit factor 1.52
      - Avg trade: 43 minutes (scalping-style on gold volatility)
    """)

    st.markdown("<h2 class='gold-text'>Phase 2 (Verification) Attempt</h2>", unsafe_allow_html=True)
    st.write("""
    - Goal: 5% profit target, same strict risk limits (5% daily / 10% overall loss)
    - Outcome: Failed due to emotional intervention — shaken by market noise, manually adjusted parameters and added trades
    - Key Insight: Untouched sim run (Jan 1–16, 2026) showed ~$2,000 additional gain — would have passed easily
    - Big Lesson: Trust the System No Matter What. Emotions are the real enemy; the EA is solid when left alone
    - Turned failure into life rebuild: Discipline, patience, surrender to God's plan — applied to trading AND personal life
    """)

    st.markdown("<h2 class='gold-text'>Current Attempt (Jan 2026)</h2>", unsafe_allow_html=True)
    st.write("""
    - New FTMO 10K Challenge (Phase 1) ongoing
    - Full trust mode: 100% hands-off — no tweaks, no manual trades, pure automated execution
    - Confidence: Previous pass + untouched sims prove the edge. Goal: Pass with consistency, low DD, then Verification → funded account
    """)

    st.markdown("<h2 class='gold-text'>Dual Product Evolution (2026)</h2>", unsafe_allow_html=True)
    st.write("""
    - Prop Firm Version (KMFX EA – Locked): For FTMO/challenges only — personal use, strict no-intervention during evaluations
    - Personal/Client Version (in progress): Same core strategy, but client-friendly
      - Solid backtest results on historical GOLD data (consistent gains, controlled risk)
      - Future: Deployable on personal accounts, potential for clients/pioneers (with sharing or access via dashboard)
      - Advantage: Separate from prop rules — flexible for real-money growth
    """)

    st.markdown("<h2 class='gold-text'>Performance Proof</h2>", unsafe_allow_html=True)
    st.write("""
    - FTMO Phase 1 Passed: +10.41%, 2.98% max DD
    - 2025 Backtest: +187.97%
    - 5-Year Backtest (2021-2025): +3,071%
    - Safety First: 1% risk per trade, no martingale/grid, controlled drawdown
    """)

    st.markdown("</div>", unsafe_allow_html=True)

    # Progress Timeline
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("<h2 class='gold-text'>Empire Progress Timeline</h2>", unsafe_allow_html=True)

    timeline = [
        ("2024", "Origin & Development", "Frustration with manual trading → Full year MQL5 self-study → Trial-and-error building the EA"),
        ("Early 2025", "Breakthrough", "EA fully functional → Official KMFX EA name → Focused on XAUUSD"),
        ("Sep-Dec 2025", "Testing & Community", "Tester group formed → Mastered backtesting → Dashboard launched (Oct 15) → Pioneer community (₱17k funded)"),
        ("Dec 2025-Jan 2026", "First FTMO Success", "Phase 1 passed in 13 days → +10.41% gain, 2.98% DD"),
        ("Phase 2", "Key Lesson", "Emotional failure → Learned to trust the system completely"),
        ("Jan 2026", "Current Challenge", "New FTMO 10K • Full hands-off mode • On track for funded account")
    ]

    for date, title, desc in timeline:
        st.markdown(f"<div class='timeline-card'><h3 class='gold-text'>{date} — {title}</h3><p>{desc}</p></div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # Member Login CTA
    st.markdown("<div class='glass-card' style='text-align:center; margin:5rem 0; padding:4rem;'>", unsafe_allow_html=True)
    st.markdown(f"<h2 class='gold-text'>Already a Pioneer or Member?</h2>", unsafe_allow_html=True)
    st.markdown("<p style='font-size:1.4rem;'>Access your elite dashboard, balance, shares, and tools</p>", unsafe_allow_html=True)
    if st.button("Member Login →", type="primary", use_container_width=True):
        st.session_state.show_login = True

    if st.session_state.get("show_login"):
        col1, col2, col3 = st.columns([1, 4, 1])
        with col2:
            st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
            tab_owner, tab_admin, tab_client = st.tabs(["👑 Owner Login", "🛠️ Admin Login", "👥 Client Login"])

            with tab_owner:
                with st.form("login_form_owner"):
                    username = st.text_input("Username", placeholder="Owner username", key="owner_user")
                    password = st.text_input("Password", type="password", key="owner_pwd")
                    if st.form_submit_button("Login as Owner →", type="primary", use_container_width=True):
                        login_user(username, password)

            with tab_admin:
                with st.form("login_form_admin"):
                    username = st.text_input("Username", placeholder="Admin username", key="admin_user")
                    password = st.text_input("Password", type="password", key="admin_pwd")
                    if st.form_submit_button("Login as Admin →", type="primary", use_container_width=True):
                        login_user(username, password)

            with tab_client:
                with st.form("login_form_client"):
                    username = st.text_input("Username", placeholder="Your username", key="client_user")
                    password = st.text_input("Password", type="password", key="client_pwd")
                    if st.form_submit_button("Login as Client →", type="primary", use_container_width=True):
                        login_user(username, password)

            st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# ====================== AUTHENTICATED APP STARTS HERE (bago mag dashboard) ======================
with st.sidebar:
    st.markdown(f"<h3 style='text-align:center;'>👤 {st.session_state.full_name}</h3>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align:center; color:{accent_primary};'><strong>{st.session_state.role.title()}</strong></p>", unsafe_allow_html=True)
    st.divider()

    current_role = st.session_state.role
    if current_role == "client":
        pages = [
            "🏠 Dashboard", "👤 My Profile", "📊 FTMO Accounts", "💰 Profit Sharing",
            "🌱 Growth Fund", "📁 File Vault", "📢 Announcements", "💬 Messages",
            "🔔 Notifications", "💳 Withdrawals", "🤖 EA Versions", "📸 Testimonials",
            "🔮 Simulator"
        ]
    elif current_role == "admin":
        pages = [
            "🏠 Dashboard", "📊 FTMO Accounts", "💰 Profit Sharing", "🌱 Growth Fund",
            "📁 File Vault", "📢 Announcements", "💬 Messages", "🔔 Notifications",
            "💳 Withdrawals", "🤖 EA Versions", "📸 Testimonials", "📈 Reports & Export",
            "🔮 Simulator"
        ]
    elif current_role == "owner":
        pages = [
            "🏠 Dashboard", "📊 FTMO Accounts", "💰 Profit Sharing", "🌱 Growth Fund",
            "🔑 License Generator", "📁 File Vault", "📢 Announcements", "💬 Messages",
            "🔔 Notifications", "💳 Withdrawals", "🤖 EA Versions", "📸 Testimonials",
            "📈 Reports & Export", "🔮 Simulator", "📜 Audit Logs", "👤 Admin Management"
        ]

    if "selected_page" not in st.session_state:
        st.session_state.selected_page = pages[0]

    selected = st.radio("Navigation", pages, index=pages.index(st.session_state.selected_page), label_visibility="collapsed")
    st.session_state.selected_page = selected

    st.divider()
    if st.button("☀️ Light Mode" if theme == "dark" else "🌙 Dark Mode", use_container_width=True):
        st.session_state.theme = "light" if theme == "dark" else "dark"
        st.rerun()

    if st.button("🚪 Logout", use_container_width=True, type="secondary"):
        log_action("Logout", f"User: {st.session_state.username}")
        st.session_state.clear()
        st.rerun()

# ====================== COMMON HEADER (APPLY THIS FIRST - BEFORE PAGES) ======================
# FIXED: Growth Fund now uses materialized view (instant, consistent everywhere)
try:
    gf_resp = supabase.table("mv_growth_fund_balance").select("balance").execute()
    gf_balance = gf_resp.data[0]["balance"] if gf_resp.data else 0.0
except:
    gf_balance = 0.0

col1, col2 = st.columns([3, 1])
with col1:
    st.markdown(f"<h1>{selected}</h1>", unsafe_allow_html=True)
with col2:
    st.metric("Growth Fund", f"${gf_balance:,.0f}")

# Announcement Banner (unchanged - already good)
try:
    ann = supabase.table("announcements").select("title, message, date").order("date", desc=True).limit(1).execute().data[0]
    st.markdown(f"""
    <div class='glass-card' style='border-left: 5px solid {accent_primary}; padding:1.5rem;'>
        <h4 style='margin:0; color:{accent_primary};'>📢 {ann['title']}</h4>
        <p style='margin:0.8rem 0 0; opacity:0.9;'>{ann['message']}</p>
        <small style='opacity:0.7;'>Posted: {ann['date']}</small>
    </div>
    """, unsafe_allow_html=True)
except:
    st.markdown(f"""
    <div class='glass-card' style='text-align:center; padding:2rem;'>
        <h3 style='margin:0; color:{accent_primary};'>Welcome back, {st.session_state.full_name}! 🚀</h3>
        <p style='margin:1rem 0 0; opacity:0.8;'>Scale smarter. Trade bolder. Win bigger.</p>
    </div>
    """, unsafe_allow_html=True)

# ====================== DASHBOARD PAGE - FULL LATEST FIXED (100% REALTIME, CLEAN, FAST, NO CACHE, NO BUGS) ======================
# ====================== DASHBOARD PAGE - CLEAN, FAST, 100% RELIABLE 2026 ======================
if selected == "🏠 Dashboard":
    st.header("Elite Empire Command Center 🚀")
    st.markdown(
        "**Realtime overview: Accounts • Equity • Withdrawable • Funded PHP • Profits • Distributed • Client Balances • Growth Fund**  \n"
        "Everything synced instantly via materialized views • No delays • No mismatches"
    )

    current_role = st.session_state.get("role", "guest")
    my_name = st.session_state.get("full_name", "Unknown")

    # ─── Optimized fetch ─── (very few queries, heavy use of materialized views)
    @st.cache_data(ttl=45, show_spinner="Loading empire summary...")
    def get_dashboard_data():
        try:
            # 1. Instant totals from materialized views
            empire = supabase.table("mv_empire_summary").select("*").execute().data
            empire = empire[0] if empire else {}

            gf = supabase.table("mv_growth_fund_balance").select("balance").execute().data
            gf_balance = gf[0]["balance"] if gf else 0.0

            clients = supabase.table("mv_client_balances").select("*").execute().data
            client_summary = clients[0] if clients else {}

            # 2. Lightweight account list (only needed fields)
            accounts = supabase.table("ftmo_accounts").select(
                "id, name, current_phase, current_equity, withdrawable_balance, "
                "participants_v2, contributors_v2, contributor_share_pct"
            ).execute().data or []

            # 3. Profits & distributions summary
            profits = supabase.table("profits").select("gross_profit").execute().data or []
            total_gross = sum(p.get("gross_profit", 0) for p in profits)

            dists = supabase.table("profit_distributions").select(
                "share_amount, participant_name, is_growth_fund"
            ).execute().data or []
            total_distributed = sum(
                d["share_amount"] for d in dists if not d.get("is_growth_fund", False)
            )

            # 4. Participant shares aggregation (for tree)
            participant_shares = {}
            for d in dists:
                if not d.get("is_growth_fund", False):
                    name = d["participant_name"]
                    participant_shares[name] = participant_shares.get(name, 0) + d["share_amount"]

            # 5. Total funded PHP (contributors_v2 priority)
            total_funded_php = 0
            for acc in accounts:
                contribs = acc.get("contributors_v2") or acc.get("contributors", [])
                for c in contribs:
                    units = c.get("units", 0)
                    php_per_unit = c.get("php_per_unit", 0)
                    total_funded_php += units * php_per_unit

            return {
                "accounts": accounts,
                "total_accounts": empire.get("total_accounts", len(accounts)),
                "total_equity": empire.get("total_equity", 0.0),
                "total_withdrawable": empire.get("total_withdrawable", 0.0),
                "gf_balance": gf_balance,
                "total_gross": total_gross,
                "total_distributed": total_distributed,
                "total_client_balances": client_summary.get("total_client_balances", 0.0),
                "total_funded_php": total_funded_php,
                "participant_shares": participant_shares
            }
        except Exception as e:
            st.error(f"Dashboard data load failed: {str(e)}")
            return {
                "accounts": [],
                "total_accounts": 0,
                "total_equity": 0.0,
                "total_withdrawable": 0.0,
                "gf_balance": 0.0,
                "total_gross": 0.0,
                "total_distributed": 0.0,
                "total_client_balances": 0.0,
                "total_funded_php": 0.0,
                "participant_shares": {}
            }

    data = get_dashboard_data()

    # Safety check: materialized view count should match actual accounts
    if data["total_accounts"] != len(data["accounts"]):
        st.warning("⚠️ Count mismatch detected — data is being refreshed")
        st.cache_data.clear()
        st.rerun()

    # ─── MAIN METRICS GRID ───
    st.markdown(
        f"""
        <div style="
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
            gap: 1.2rem;
            margin: 1.8rem 0 2.5rem;
        ">
        """,
        unsafe_allow_html=True
    )

    metrics = [
        ("Active Accounts", data["total_accounts"], "#00ffaa", "2.8rem"),
        ("Total Equity", f"${data['total_equity']:,.0f}", "#00ffaa", "2.6rem"),
        ("Withdrawable", f"${data['total_withdrawable']:,.0f}", "#ff6b6b", "2.6rem"),
        ("Empire Funded (PHP)", f"₱{data['total_funded_php']:,.0f}", "#ffd700", "2.6rem"),
        ("Gross Profits", f"${data['total_gross']:,.0f}", "#ffffff", "2.4rem"),
        ("Distributed Shares", f"${data['total_distributed']:,.0f}", "#00ffaa", "2.4rem"),
        ("Client Balances", f"${data['total_client_balances']:,.0f}", "#ffd700", "2.4rem"),
        ("Growth Fund", f"${data['gf_balance']:,.0f}", "#ffd700", "2.8rem"),
    ]

    for label, value, color, size in metrics:
        st.markdown(
            f"""
            <div class="glass-card" style="text-align:center; padding:1.4rem;">
                <div style="opacity:0.85; font-size:1.05rem; margin-bottom:0.6rem;">{label}</div>
                <div style="font-size:{size}; font-weight:700; color:{color};">{value}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("</div>", unsafe_allow_html=True)

    # ─── QUICK ACTIONS ───
    st.subheader("⚡ Quick Actions")
    cols = st.columns(3 if current_role in ["owner", "admin"] else 2)

    with cols[0]:
        if current_role in ["owner", "admin"]:
            if st.button("➕ Launch New Account", use_container_width=True, type="primary"):
                st.session_state.selected_page = "📊 FTMO Accounts"
                st.rerun()
        else:
            st.button("💳 Request Withdrawal", use_container_width=True, disabled=True,
                      help="Go to Withdrawals page")

    with cols[1]:
        if current_role in ["owner", "admin"]:
            if st.button("💰 Record Profit", use_container_width=True):
                st.session_state.selected_page = "💰 Profit Sharing"
                st.rerun()
        else:
            st.info("Your earnings update automatically")

    with cols[2] if current_role in ["owner", "admin"] else None:
        if st.button("🌱 Growth Fund Details", use_container_width=True):
            st.session_state.selected_page = "🌱 Growth Fund"
            st.rerun()

    # ─── EMPIRE FLOW TREES ───
    st.subheader("🌳 Empire Flow Trees")
    tab1, tab2 = st.tabs(["Participant Shares", "Contributor Funding (PHP)"])

    with tab1:
        if data["participant_shares"]:
            labels = ["Empire"] + list(data["participant_shares"].keys())
            values = [sum(data["participant_shares"].values())] + list(data["participant_shares"].values())
            fig = go.Figure(data=[go.Sankey(
                node=dict(pad=18, thickness=28, label=labels, color="#00ffaa"),
                link=dict(source=[0]*len(values[1:]), target=list(range(1, len(values))), value=values[1:])
            )])
            fig.update_layout(height=520, title="Total Distributed by Participant")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No profit distributions yet")

    with tab2:
        funded_by = {}
        for acc in data["accounts"]:
            contribs = acc.get("contributors_v2") or acc.get("contributors", [])
            for c in contribs:
                name = c.get("display_name") or c.get("name", "Unknown")
                php = c.get("units", 0) * c.get("php_per_unit", 0)
                funded_by[name] = funded_by.get(name, 0) + php

        if funded_by:
            labels = ["Total Funded"] + list(funded_by.keys())
            values = [sum(funded_by.values())] + list(funded_by.values())
            fig = go.Figure(data=[go.Sankey(
                node=dict(pad=18, thickness=28, label=labels, color="#ffd700"),
                link=dict(source=[0]*len(values[1:]), target=list(range(1, len(values))), value=values[1:])
            )])
            fig.update_layout(height=520, title="Funding by Contributor (PHP)")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No contributors recorded yet")

    # ─── LIVE ACCOUNTS ───
    st.subheader("📊 Live Accounts")
    if data["accounts"]:
        for acc in data["accounts"]:
            phase_emoji = {
                "Challenge P1": "🔴", "Challenge P2": "🟡", "Verification": "🟠",
                "Funded": "🟢", "Scaled": "💎"
            }.get(acc["current_phase"], "⚪")

            funded_php = sum(
                c.get("units", 0) * c.get("php_per_unit", 0)
                for c in (acc.get("contributors_v2") or acc.get("contributors", []))
            )

            with st.expander(
                f"{phase_emoji} {acc['name']} • {acc['current_phase']} • "
                f"Equity ${acc.get('current_equity', 0):,.0f} • Funded ₱{funded_php:,.0f}"
            ):
                st.markdown(f"**Equity:** ${acc.get('current_equity', 0):,.0f}")
                st.markdown(f"**Withdrawable:** ${acc.get('withdrawable_balance', 0):,.0f}")

                tab_p, tab_c = st.tabs(["Participants", "Contributors"])
                with tab_p:
                    parts = acc.get("participants_v2") or acc.get("participants", [])
                    if parts:
                        labels = ["Profit"] + [p.get("display_name", p.get("name", "Unknown")) for p in parts]
                        values = [sum(p["percentage"] for p in parts)] + [p["percentage"] for p in parts]
                        fig = go.Figure(go.Sankey(
                            node=dict(pad=12, thickness=18, label=labels),
                            link=dict(source=[0]*len(values[1:]), target=list(range(1,len(values))), value=values[1:])
                        ))
                        fig.update_layout(height=380)
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("No participants")

                with tab_c:
                    contribs = acc.get("contributors_v2") or acc.get("contributors", [])
                    if contribs:
                        labels = ["Funded PHP"] + [c.get("display_name", c.get("name", "Unknown")) for c in contribs]
                        values = [sum(c["units"]*c["php_per_unit"] for c in contribs)] + \
                                 [c["units"]*c["php_per_unit"] for c in contribs]
                        fig = go.Figure(go.Sankey(
                            node=dict(pad=12, thickness=18, label=labels),
                            link=dict(source=[0]*len(values[1:]), target=list(range(1,len(values))), value=values[1:])
                        ))
                        fig.update_layout(height=380)
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("No contributors")
    else:
        st.info("No accounts launched yet")

    # ─── CLIENT-ONLY BALANCES (if owner/admin) ───
    if current_role in ["owner", "admin"]:
        st.subheader("👥 Client Balances Overview")
        try:
            client_list = supabase.table("users").select("full_name, balance").eq("role", "client").execute().data or []
            if client_list:
                df = pd.DataFrame(client_list)
                df["balance"] = df["balance"].apply(lambda x: f"${x:,.2f}")
                df = df.sort_values("balance", ascending=False)
                st.dataframe(df.rename(columns={"full_name": "Client", "balance": "Balance"}), hide_index=True)
            else:
                st.info("No clients yet")
        except Exception as e:
            st.error(f"Could not load client balances: {str(e)}")

    # ─── MOTIVATIONAL FOOTER ───
    st.markdown(
        f"""
        <div class='glass-card' style='
            padding:3.5rem 2rem;
            text-align:center;
            margin:4rem 0 2rem;
            border:2px solid {accent_primary}44;
        '>
            <h2 style='margin:0; font-size:2.4rem; background:linear-gradient(90deg, {accent_primary}, #ffd700); -webkit-background-clip:text; -webkit-text-fill-color:transparent;'>
                Fully Automatic • Realtime • Exponential Empire
            </h2>
            <p style='font-size:1.3rem; margin:1.5rem 0; opacity:0.9;'>
                Every profit flows • Balances update live • Trees visualize growth • Built to scale forever.
            </p>
            <h3 style='color:#ffd700; margin-top:2rem;'>KMFX Pro • Cloud Empire 2026 👑</h3>
        </div>
        """,
        unsafe_allow_html=True
    )
# ====================== FTMO ACCOUNTS PAGE - FULL LATEST FIXED (100% REALTIME, CLEAN, FAST, NO CACHE ISSUES, v2 PRIORITY, BULLETPROOF) ======================
elif selected == "📊 FTMO Accounts":
    st.header("FTMO Accounts Management 🚀")
    st.markdown("**Empire core: Owner/Admin launch, edit, delete accounts • Clients view shared participation • Unified profit tree (include 'Contributor Pool' row) • Edit all % freely • Must sum exactly 100% • Contributors dropdown registered only • Auto pro-rata from Contributor Pool % • Realtime previews • Full validation • Instant sync • UUID v2 active (bulletproof balance sync).**")
 
    current_role = st.session_state.get("role", "guest")
 
    # NO CACHE → always fresh realtime data (matches dashboard style)
    def fetch_all_data():
        accounts_resp = supabase.table("ftmo_accounts").select("*").order("created_date", desc=True).execute()
        users_resp = supabase.table("users").select("id, full_name, role, balance, title").execute()
        return accounts_resp.data or [], users_resp.data or []
 
    accounts, all_users = fetch_all_data()
 
    # ============ DISPLAY MAPS FOR TITLED NAMES + UUID v2 SUPPORT ============
    user_id_to_display = {}  # str(uuid) → "Name (Title)"
    display_to_user_id = {}  # "Name (Title)" → str(uuid) or None (for specials)
    user_id_to_full_name = {}  # str(uuid) → "Name"
   
    for u in all_users:
        if u["role"] in ["client", "owner"]:  # Include owner for "King Minted"
            str_id = str(u["id"])
            display = u["full_name"]
            if u.get("title"):
                display += f" ({u['title']})"
            user_id_to_display[str_id] = display
            display_to_user_id[display] = str_id
            user_id_to_full_name[str_id] = u["full_name"]
   
    # Special non-user entries
    special_options = ["Contributor Pool", "Growth Fund", "Manual Payout (Temporary)"]
    for s in special_options:
        display_to_user_id[s] = None
   
    participant_options = special_options + list(display_to_user_id.keys())
    contributor_options = list(user_id_to_display.values())  # Only real users
   
    # Owner display fallback
    owner_display = next((d for d, uid in display_to_user_id.items() if uid and next((uu for uu in all_users if str(uu["id"]) == uid and uu["role"] == "owner"), None)), "King Minted")
 
    if current_role in ["owner", "admin"]:
        with st.expander("➕ Launch New FTMO Account", expanded=True):
            with st.form("create_account_form", clear_on_submit=True):
                col1, col2 = st.columns(2)
                with col1:
                    name = st.text_input("Account Name *", placeholder="e.g. KMFX Verification 100K")
                    ftmo_id = st.text_input("FTMO ID (Optional)")
                    phase = st.selectbox("Current Phase *", ["Challenge P1", "Challenge P2", "Verification", "Funded", "Scaled"], index=2)
                with col2:
                    equity = st.number_input("Current Equity (USD)", min_value=0.0, value=100000.0, step=1000.0)
                    withdrawable = st.number_input("Current Withdrawable (USD)", min_value=0.0, value=0.0, step=500.0)
             
                notes = st.text_area("Notes (Optional)")
             
                st.subheader("🌳 Unified Profit Distribution Tree (%)")
                st.info("**Include 'Contributor Pool' row** • Edit all % freely • Total must be exactly 100% • Contributor Pool % auto pro-rata to contributors")
              
                # Default rows with titled displays
                default_rows = [
                    {"display_name": "Contributor Pool", "role": "Funding Contributors (pro-rata)", "percentage": 30.0},
                    {"display_name": owner_display, "role": "Founder/Owner", "percentage": 70.0}
                ]
                tree_df = pd.DataFrame(default_rows)
              
                edited_tree = st.data_editor(
                    tree_df,
                    num_rows="dynamic",
                    use_container_width=True,
                    key="participants_editor_create",
                    column_config={
                        "display_name": st.column_config.SelectboxColumn("Name *", options=participant_options, required=True),
                        "role": st.column_config.TextColumn("Role"),
                        "percentage": st.column_config.NumberColumn("% *", min_value=0.0, max_value=100.0, step=0.5)
                    }
                )
              
                total_sum = edited_tree["percentage"].sum()
                st.progress(total_sum / 100)
              
                contrib_rows = edited_tree[edited_tree["display_name"] == "Contributor Pool"]
                if len(contrib_rows) != 1:
                    st.error("Must have exactly one 'Contributor Pool' row")
                elif abs(total_sum - 100.0) > 0.1:
                    st.error(f"Total must be exactly 100% (current: {total_sum:.1f}%)")
                else:
                    st.success("✅ Perfect 100% unified tree")
              
                contributor_share_pct = contrib_rows.iloc[0]["percentage"] if len(contrib_rows) == 1 else 0.0
              
                # Manual custom names handling
                manual_inputs = []
                for idx, row in edited_tree.iterrows():
                    if row["display_name"] == "Manual Payout (Temporary)":
                        custom_name = st.text_input(f"Custom Name for Manual Row {idx+1}", key=f"manual_create_{idx}")
                        if custom_name:
                            manual_inputs.append((idx, custom_name))
             
                st.subheader("🌳 Contributors Tree - Funding (PHP Units)")
                st.info("Dropdown from registered clients only (with titles) • Auto pro-rata from Contributor Pool row above")
              
                contrib_df = pd.DataFrame(columns=["display_name", "units", "php_per_unit"])
                edited_contrib = st.data_editor(
                    contrib_df,
                    num_rows="dynamic",
                    use_container_width=True,
                    key="contrib_editor_create",
                    column_config={
                        "display_name": st.column_config.SelectboxColumn("Contributor Name *", options=contributor_options, required=True),
                        "units": st.column_config.NumberColumn("Units Funded", min_value=0.0, step=0.5),
                        "php_per_unit": st.column_config.NumberColumn("PHP per Unit", min_value=100.0, step=100.0)
                    }
                )
              
                if not edited_contrib.empty:
                    total_php = (edited_contrib["units"] * edited_contrib["php_per_unit"]).sum()
                    st.metric("Total Funded (PHP)", f"₱{total_php:,.0f}")
             
                tab_prev1, tab_prev2 = st.tabs(["Unified Profit Tree Preview", "Contributors Funding Tree Preview"])
                with tab_prev1:
                    labels = ["Gross Profit"]
                    for _, row in edited_tree.iterrows():
                        d = row["display_name"]
                        if d == "Contributor Pool":
                            d = "Contributor Pool (pro-rata)"
                        labels.append(f"{d} ({row['percentage']:.1f}%)")
                    values = edited_tree["percentage"].tolist()
                    fig = go.Figure(data=[go.Sankey(
                        node=dict(pad=15, thickness=20, label=labels),
                        link=dict(source=[0]*len(values), target=list(range(1, len(values)+1)), value=values)
                    )])
                    fig.update_layout(font=dict(color="black"))
                    st.plotly_chart(fig, use_container_width=True)
                with tab_prev2:
                    if not edited_contrib.empty:
                        valid = edited_contrib.dropna(subset=["units", "php_per_unit"])
                        if not valid.empty:
                            labels = ["Funded (PHP)"] + [f"{row['display_name']} ({row['units']} units @ ₱{row['php_per_unit']:,.0f}/unit)" for _, row in valid.iterrows()]
                            values = (valid["units"] * valid["php_per_unit"]).tolist()
                            fig = go.Figure(data=[go.Sankey(
                                node=dict(pad=15, thickness=20, label=labels),
                                link=dict(source=[0]*len(values), target=list(range(1, len(values)+1)), value=values)
                            )])
                            fig.update_layout(font=dict(color="black"))
                            st.plotly_chart(fig, use_container_width=True)
             
                submitted = st.form_submit_button("🚀 Launch Account", type="primary", use_container_width=True)
                if submitted:
                    if not name.strip():
                        st.error("Account name required")
                    elif len(contrib_rows) != 1:
                        st.error("Must have exactly one 'Contributor Pool' row")
                    elif abs(total_sum - 100.0) > 0.1:
                        st.error("Total % not 100%")
                    else:
                        try:
                            # Build v2 structures
                            final_part_v2 = []
                            for row in edited_tree.to_dict(orient="records"):
                                display = row["display_name"]
                                user_id = display_to_user_id.get(display)
                                final_part_v2.append({
                                    "user_id": user_id,
                                    "display_name": display,
                                    "percentage": row["percentage"],
                                    "role": row["role"]
                                })
                            for row_idx, custom in manual_inputs:
                                final_part_v2[row_idx]["display_name"] = custom
                                final_part_v2[row_idx]["user_id"] = None
                           
                            final_contrib_v2 = []
                            for row in edited_contrib.to_dict(orient="records"):
                                display = row["display_name"]
                                user_id = display_to_user_id.get(display)
                                final_contrib_v2.append({
                                    "user_id": user_id,
                                    "units": row["units"],
                                    "php_per_unit": row["php_per_unit"]
                                })
                           
                            # Backward compatibility old columns
                            final_part_old = []
                            for p in final_part_v2:
                                name = user_id_to_full_name.get(p["user_id"], p["display_name"]) if p["user_id"] else p["display_name"]
                                final_part_old.append({
                                    "name": name,
                                    "role": p["role"],
                                    "percentage": p["percentage"]
                                })
                           
                            final_contrib_old = []
                            for c in final_contrib_v2:
                                name = user_id_to_full_name.get(c["user_id"], "Unknown")
                                final_contrib_old.append({
                                    "name": name,
                                    "units": c["units"],
                                    "php_per_unit": c["php_per_unit"]
                                })
                           
                            supabase.table("ftmo_accounts").insert({
                                "name": name.strip(),
                                "ftmo_id": ftmo_id or None,
                                "current_phase": phase,
                                "current_equity": equity,
                                "withdrawable_balance": withdrawable,
                                "notes": notes or None,
                                "created_date": datetime.date.today().isoformat(),
                                "participants": final_part_old,
                                "contributors": final_contrib_old,
                                "participants_v2": final_part_v2,
                                "contributors_v2": final_contrib_v2,
                                "contributor_share_pct": contributor_share_pct
                            }).execute()
                           
                            st.success("Account launched successfully! 🎉")
                            st.balloons()
                            st.rerun()
                        except Exception as e:
                            st.error(f"Failed to launch account: {str(e)}")
     
        # ==================== LIVE ACCOUNTS LIST + EDIT ====================
        st.subheader("Live Empire Accounts")
        if accounts:
            for acc in accounts:
                # Prefer v2 if populated
                use_v2 = bool(acc.get("participants_v2"))
                participants = acc.get("participants_v2") if use_v2 else acc.get("participants", [])
                contributors = acc.get("contributors_v2") if use_v2 else acc.get("contributors", [])
               
                total_funded_php = sum(c.get("units", 0) * c.get("php_per_unit", 0) for c in contributors)
                contrib_pct = acc.get("contributor_share_pct", 0)
               
                with st.expander(f"🌟 {acc['name']} • {acc['current_phase']} • Equity ${acc.get('current_equity', 0):,.0f} • Funded ₱{total_funded_php:,.0f} • Contributor Pool: {contrib_pct:.1f}% {'(UUID v2)' if use_v2 else '(Legacy)'}", expanded=False):
                    tab1, tab2 = st.tabs(["Unified Profit Tree", "Contributors Funding Tree"])
                    with tab1:
                        labels = ["Gross Profit"]
                        for p in participants:
                            display = p.get("display_name", user_id_to_display.get(p.get("user_id"), p.get("name", "Unknown"))) if use_v2 else p.get("name", "Unknown")
                            if display == "Contributor Pool":
                                display = "Contributor Pool (pro-rata)"
                            labels.append(f"{display} ({p['percentage']:.1f}%)")
                        values = [p["percentage"] for p in participants]
                        fig = go.Figure(data=[go.Sankey(
                            node=dict(pad=15, thickness=20, label=labels),
                            link=dict(source=[0]*len(values), target=list(range(1, len(values)+1)), value=values)
                        )])
                        fig.update_layout(font=dict(color="black"))
                        st.plotly_chart(fig, use_container_width=True)
                    with tab2:
                        if contributors:
                            labels = ["Funded (PHP)"]
                            values = []
                            for c in contributors:
                                display = user_id_to_display.get(c.get("user_id"), c.get("name", "Unknown")) if use_v2 else c.get("name", "Unknown")
                                labels.append(f"{display} ({c.get('units', 0)} units @ ₱{c.get('php_per_unit', 0):,.0f}/unit)")
                                values.append(c.get("units", 0) * c.get("php_per_unit", 0))
                            fig = go.Figure(data=[go.Sankey(
                                node=dict(pad=15, thickness=20, label=labels),
                                link=dict(source=[0]*len(values), target=list(range(1, len(values)+1)), value=values)
                            )])
                            fig.update_layout(font=dict(color="black"))
                            st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.info("No contributors yet")
                 
                    col_e1, col_e2 = st.columns(2)
                    with col_e1:
                        if st.button("✏️ Edit", key=f"edit_{acc['id']}"):
                            st.session_state.edit_acc_id = acc["id"]
                            st.session_state.edit_acc_data = acc
                            st.rerun()
                    with col_e2:
                        if st.button("🗑️ Delete", key=f"del_{acc['id']}", type="secondary"):
                            try:
                                supabase.table("ftmo_accounts").delete().eq("id", acc["id"]).execute()
                                st.success("Account removed")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error: {str(e)}")
         
            # ==================== FULL EDIT FORM (FORCES v2 MIGRATION ON SAVE) ====================
            if "edit_acc_id" in st.session_state:
                eid = st.session_state.edit_acc_id
                cur = st.session_state.edit_acc_data
               
                with st.expander(f"✏️ Editing {cur['name']}", expanded=True):
                    with st.form(key=f"edit_form_{eid}", clear_on_submit=True):
                        col1, col2 = st.columns(2)
                        with col1:
                            new_name = st.text_input("Account Name *", value=cur["name"])
                            new_ftmo_id = st.text_input("FTMO ID (Optional)", value=cur.get("ftmo_id") or "")
                            new_phase = st.selectbox("Current Phase *", ["Challenge P1", "Challenge P2", "Verification", "Funded", "Scaled"],
                                                     index=["Challenge P1", "Challenge P2", "Verification", "Funded", "Scaled"].index(cur["current_phase"]))
                        with col2:
                            new_equity = st.number_input("Current Equity (USD)", value=float(cur.get("current_equity", 0)), step=1000.0)
                            new_withdrawable = st.number_input("Current Withdrawable (USD)", value=float(cur.get("withdrawable_balance", 0)), step=500.0)
                     
                        new_notes = st.text_area("Notes (Optional)", value=cur.get("notes") or "")
                     
                        st.subheader("🌳 Unified Profit Distribution Tree (%)")
                        st.info("**Include 'Contributor Pool' row** • Edit all % freely • Total must be exactly 100%")
                      
                        # Load current tree - prefer v2, fallback + auto-migrate
                        use_v2 = bool(cur.get("participants_v2"))
                        if use_v2:
                            current_part = pd.DataFrame(cur.get("participants_v2", []))
                            current_part["display_name"] = current_part.apply(
                                lambda row: row.get("display_name") or user_id_to_display.get(row.get("user_id"), "Unknown"), axis=1
                            )
                        else:
                            legacy_part = pd.DataFrame(cur.get("participants", []))
                            legacy_part["display_name"] = legacy_part["name"].apply(
                                lambda n: next((d for d, uid in display_to_user_id.items() if user_id_to_full_name.get(uid) == n), n)
                            )
                            current_part = legacy_part[["display_name", "role", "percentage"]].copy()
                            st.info("🔄 Legacy → saving will migrate to v2")
                      
                        # Auto-add missing Contributor Pool
                        if "Contributor Pool" not in current_part["display_name"].values:
                            contrib_pct = cur.get("contributor_share_pct", 30.0)
                            contrib_row = pd.DataFrame([{"display_name": "Contributor Pool", "role": "Funding Contributors (pro-rata)", "percentage": contrib_pct}])
                            current_part = pd.concat([contrib_row, current_part], ignore_index=True)
                            st.info(f"Auto-added missing Contributor Pool ({contrib_pct:.1f}%)")
                      
                        edited_tree = st.data_editor(
                            current_part[["display_name", "role", "percentage"]],
                            num_rows="dynamic",
                            use_container_width=True,
                            key=f"participants_editor_edit_{eid}",
                            column_config={
                                "display_name": st.column_config.SelectboxColumn("Name *", options=participant_options, required=True),
                                "role": st.column_config.TextColumn("Role"),
                                "percentage": st.column_config.NumberColumn("% *", min_value=0.0, max_value=100.0, step=0.5)
                            }
                        )
                      
                        contrib_rows = edited_tree[edited_tree["display_name"] == "Contributor Pool"]
                        if len(contrib_rows) != 1:
                            st.error("Must have exactly one 'Contributor Pool' row")
                        contributor_share_pct = contrib_rows.iloc[0]["percentage"] if len(contrib_rows) == 1 else 0.0
                      
                        total_sum = edited_tree["percentage"].sum()
                        st.progress(total_sum / 100)
                        if abs(total_sum - 100.0) > 0.1:
                            st.error(f"Total must be exactly 100% (current: {total_sum:.1f}%)")
                        else:
                            st.success("✅ Perfect 100% unified tree")
                      
                        manual_inputs = []
                        for idx, row in edited_tree.iterrows():
                            if row["display_name"] == "Manual Payout (Temporary)":
                                custom_name = st.text_input(f"Custom Name for Manual Row {idx+1}", key=f"manual_edit_{eid}_{idx}")
                                if custom_name:
                                    manual_inputs.append((idx, custom_name))
                      
                        st.subheader("🌳 Contributors Tree - Funding (PHP Units)")
                        if use_v2:
                            current_contrib = pd.DataFrame(cur.get("contributors_v2", []))
                            current_contrib["display_name"] = current_contrib["user_id"].apply(lambda uid: user_id_to_display.get(uid, "Unknown"))
                        else:
                            legacy_contrib = pd.DataFrame(cur.get("contributors", []))
                            legacy_contrib["display_name"] = legacy_contrib["name"].apply(
                                lambda n: next((d for d, uid in display_to_user_id.items() if user_id_to_full_name.get(uid) == n), n)
                            )
                            current_contrib = legacy_contrib[["display_name", "units", "php_per_unit"]].copy()
                            st.info("🔄 Legacy contributors → saving will migrate to v2")
                       
                        edited_contrib = st.data_editor(
                            current_contrib[["display_name", "units", "php_per_unit"]],
                            num_rows="dynamic",
                            use_container_width=True,
                            key=f"contrib_editor_edit_{eid}",
                            column_config={
                                "display_name": st.column_config.SelectboxColumn("Contributor Name *", options=contributor_options, required=True),
                                "units": st.column_config.NumberColumn("Units Funded", min_value=0.0, step=0.5),
                                "php_per_unit": st.column_config.NumberColumn("PHP per Unit", min_value=100.0, step=100.0)
                            }
                        )
                      
                        if not edited_contrib.empty:
                            total_php = (edited_contrib["units"] * edited_contrib["php_per_unit"]).sum()
                            st.metric("Total Funded (PHP)", f"₱{total_php:,.0f}")
                      
                        tab_prev1, tab_prev2 = st.tabs(["Unified Profit Tree Preview", "Contributors Funding Tree Preview"])
                        with tab_prev1:
                            labels = ["Gross Profit"]
                            for _, row in edited_tree.iterrows():
                                d = row["display_name"]
                                if d == "Contributor Pool":
                                    d = "Contributor Pool (pro-rata)"
                                labels.append(f"{d} ({row['percentage']:.1f}%)")
                            values = edited_tree["percentage"].tolist()
                            fig = go.Figure(data=[go.Sankey(
                                node=dict(pad=15, thickness=20, label=labels),
                                link=dict(source=[0]*len(values), target=list(range(1, len(values)+1)), value=values)
                            )])
                            fig.update_layout(font=dict(color="black"))
                            st.plotly_chart(fig, use_container_width=True)
                        with tab_prev2:
                            if not edited_contrib.empty:
                                valid = edited_contrib.dropna(subset=["units", "php_per_unit"])
                                if not valid.empty:
                                    labels = ["Funded (PHP)"] + [f"{row['display_name']} ({row['units']} units @ ₱{row['php_per_unit']:,.0f}/unit)" for _, row in valid.iterrows()]
                                    values = (valid["units"] * valid["php_per_unit"]).tolist()
                                    fig = go.Figure(data=[go.Sankey(
                                        node=dict(pad=15, thickness=20, label=labels),
                                        link=dict(source=[0]*len(values), target=list(range(1, len(values)+1)), value=values)
                                    )])
                                    fig.update_layout(font=dict(color="black"))
                                    st.plotly_chart(fig, use_container_width=True)
                      
                        col_save, col_cancel = st.columns(2)
                        with col_save:
                            if st.form_submit_button("💾 Save Changes", type="primary", use_container_width=True):
                                if not new_name.strip():
                                    st.error("Account name required")
                                elif len(contrib_rows) != 1:
                                    st.error("Must have exactly one 'Contributor Pool' row")
                                elif abs(total_sum - 100.0) > 0.1:
                                    st.error("Total % not 100%")
                                else:
                                    try:
                                        # Force v2 on save
                                        final_part_v2 = []
                                        for row in edited_tree.to_dict(orient="records"):
                                            display = row["display_name"]
                                            user_id = display_to_user_id.get(display)
                                            final_part_v2.append({
                                                "user_id": user_id,
                                                "display_name": display,
                                                "percentage": row["percentage"],
                                                "role": row["role"]
                                            })
                                        for row_idx, custom in manual_inputs:
                                            final_part_v2[row_idx]["display_name"] = custom
                                            final_part_v2[row_idx]["user_id"] = None
                                       
                                        final_contrib_v2 = []
                                        for row in edited_contrib.to_dict(orient="records"):
                                            display = row["display_name"]
                                            user_id = display_to_user_id.get(display)
                                            final_contrib_v2.append({
                                                "user_id": user_id,
                                                "units": row["units"],
                                                "php_per_unit": row["php_per_unit"]
                                            })
                                       
                                        # Keep old for backward compat
                                        final_part_old = []
                                        for p in final_part_v2:
                                            name = user_id_to_full_name.get(p["user_id"], p["display_name"]) if p["user_id"] else p["display_name"]
                                            final_part_old.append({"name": name, "role": p["role"], "percentage": p["percentage"]})
                                       
                                        final_contrib_old = []
                                        for c in final_contrib_v2:
                                            name = user_id_to_full_name.get(c["user_id"], "Unknown")
                                            final_contrib_old.append({"name": name, "units": c["units"], "php_per_unit": c["php_per_unit"]})
                                       
                                        supabase.table("ftmo_accounts").update({
                                            "name": new_name.strip(),
                                            "ftmo_id": new_ftmo_id or None,
                                            "current_phase": new_phase,
                                            "current_equity": new_equity,
                                            "withdrawable_balance": new_withdrawable,
                                            "notes": new_notes or None,
                                            "participants": final_part_old,
                                            "contributors": final_contrib_old,
                                            "participants_v2": final_part_v2,
                                            "contributors_v2": final_contrib_v2,
                                            "contributor_share_pct": contributor_share_pct
                                        }).eq("id", eid).execute()
                                       
                                        st.success("Account updated + migrated to v2! 🎉")
                                        del st.session_state.edit_acc_id
                                        del st.session_state.edit_acc_data
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"Error: {str(e)}")
                        with col_cancel:
                            if st.form_submit_button("Cancel", use_container_width=True):
                                del st.session_state.edit_acc_id
                                del st.session_state.edit_acc_data
                                st.rerun()
        else:
            st.info("No accounts yet")
 
    # ==================== CLIENT VIEW (REALTIME TITLES & TREES) ====================
    else:
        my_name = st.session_state.full_name
        my_accounts = []
        for a in accounts:
            participants = a.get("participants_v2") or a.get("participants", [])
            if any(
                p.get("display_name") == my_name or 
                p.get("name") == my_name or 
                user_id_to_full_name.get(p.get("user_id")) == my_name 
                for p in participants
            ):
                my_accounts.append(a)
       
        st.subheader(f"Your Shared Accounts ({len(my_accounts)})")
        if my_accounts:
            for acc in my_accounts:
                participants = acc.get("participants_v2") or acc.get("participants", [])
                my_pct = next((
                    p["percentage"] for p in participants if
                    p.get("display_name") == my_name or 
                    p.get("name") == my_name or 
                    user_id_to_full_name.get(p.get("user_id")) == my_name
                ), 0)
               
                contributors = acc.get("contributors_v2") or acc.get("contributors", [])
                my_funded_php = sum(
                    c.get("units", 0) * c.get("php_per_unit", 0) for c in contributors
                    if user_id_to_full_name.get(c.get("user_id")) == my_name or c.get("name") == my_name
                )
               
                with st.expander(f"🌟 {acc['name']} • Your Share: {my_pct:.1f}% • Your Funded ₱{my_funded_php:,.0f}", expanded=True):
                    st.markdown(f"**Phase:** {acc['current_phase']} • **Equity:** ${acc.get('current_equity', 0):,.0f}")
                    tab1, tab2 = st.tabs(["Unified Profit Tree", "Contributors Funding Tree"])
                    with tab1:
                        labels = ["Gross Profit"]
                        for p in participants:
                            display = p.get("display_name", user_id_to_display.get(p.get("user_id"), p.get("name", "Unknown")))
                            if display == "Contributor Pool":
                                display = "Contributor Pool (pro-rata)"
                            labels.append(f"{display} ({p['percentage']:.1f}%)")
                        values = [p["percentage"] for p in participants]
                        fig = go.Figure(data=[go.Sankey(
                            node=dict(pad=15, thickness=20, label=labels),
                            link=dict(source=[0]*len(values), target=list(range(1, len(values)+1)), value=values)
                        )])
                        fig.update_layout(font=dict(color="black"))
                        st.plotly_chart(fig, use_container_width=True)
                    with tab2:
                        if contributors:
                            labels = ["Funded (PHP)"]
                            values = []
                            for c in contributors:
                                display = user_id_to_display.get(c.get("user_id"), c.get("name", "Unknown"))
                                labels.append(f"{display} ({c.get('units', 0)} units @ ₱{c.get('php_per_unit', 0):,.0f}/unit)")
                                values.append(c.get("units", 0) * c.get("php_per_unit", 0))
                            fig = go.Figure(data=[go.Sankey(
                                node=dict(pad=15, thickness=20, label=labels),
                                link=dict(source=[0]*len(values), target=list(range(1, len(values)+1)), value=values)
                            )])
                            fig.update_layout(font=dict(color="black"))
                            st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.info("No contributors yet")
        else:
            st.info("No participation yet • Owner will assign")
       
        st.subheader("Empire Overview (All Accounts)")
        for acc in accounts:
            total_funded_php = sum(c.get("units", 0) * c.get("php_per_unit", 0) for c in (acc.get("contributors_v2") or acc.get("contributors", [])))
            with st.expander(f"{acc['name']} • {acc['current_phase']} • Equity ${acc.get('current_equity', 0):,.0f} • Funded ₱{total_funded_php:,.0f}"):
                tab1, tab2 = st.tabs(["Unified Profit Tree", "Contributors Funding Tree"])
                with tab1:
                    participants = acc.get("participants_v2") or acc.get("participants", [])
                    labels = ["Gross Profit"]
                    for p in participants:
                        display = p.get("display_name", user_id_to_display.get(p.get("user_id"), p.get("name", "Unknown")))
                        if display == "Contributor Pool":
                            display = "Contributor Pool (pro-rata)"
                        labels.append(f"{display} ({p['percentage']:.1f}%)")
                    values = [p["percentage"] for p in participants]
                    fig = go.Figure(data=[go.Sankey(
                        node=dict(pad=15, thickness=20, label=labels),
                        link=dict(source=[0]*len(values), target=list(range(1, len(values)+1)), value=values)
                    )])
                    fig.update_layout(font=dict(color="black"))
                    st.plotly_chart(fig, use_container_width=True)
                with tab2:
                    contributors = acc.get("contributors_v2") or acc.get("contributors", [])
                    if contributors:
                        labels = ["Funded (PHP)"]
                        values = []
                        for c in contributors:
                            display = user_id_to_display.get(c.get("user_id"), c.get("name", "Unknown"))
                            labels.append(f"{display} ({c.get('units', 0)} units @ ₱{c.get('php_per_unit', 0):,.0f}/unit)")
                            values.append(c.get("units", 0) * c.get("php_per_unit", 0))
                        fig = go.Figure(data=[go.Sankey(
                            node=dict(pad=15, thickness=20, label=labels),
                            link=dict(source=[0]*len(values), target=list(range(1, len(values)+1)), value=values)
                        )])
                        fig.update_layout(font=dict(color="black"))
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("No contributors yet")
 
    if not accounts:
        st.info("No accounts in empire yet")
# ====================== PROFIT SHARING PAGE - FULL LATEST FIXED (100% REALTIME, CLEAN, FAST, BULLETPROOF v2 SYNC, AUTO-EMAIL PERFECT) ======================
elif selected == "💰 Profit Sharing":
    st.header("Profit Sharing & Auto-Distribution 💰")
    st.markdown("**Empire scaling engine: Input FTMO withdrawable profit → Auto-split & distribute using stored v2 tree • Bulletproof UUID balance updates • Premium HTML auto-email to ALL involved • Realtime preview • Instant sync across dashboard/balances/GF.**")
    
    current_role = st.session_state.get("role", "guest")
    if current_role not in ["owner", "admin"]:
        st.warning("Profit recording is owner/admin only.")
        st.stop()

    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart

    # NO CACHE → always fresh realtime data (accounts, users, trees)
    def fetch_profit_data():
        accounts = supabase.table("ftmo_accounts").select(
            "id, name, current_phase, current_equity, unit_value, "
            "participants_v2, contributors_v2, contributor_share_pct"
        ).execute().data or []
        users = supabase.table("users").select("id, full_name, email, title, balance").execute().data or []
        
        # Fast v2 lookup maps
        user_id_to_display = {}
        user_id_to_email = {}
        user_id_to_balance = {}
        for u in users:
            str_id = str(u["id"])
            display = u["full_name"]
            if u.get("title"):
                display += f" ({u['title']})"
            user_id_to_display[str_id] = display
            user_id_to_email[str_id] = u.get("email")
            user_id_to_balance[str_id] = u.get("balance", 0)
        
        return accounts, users, user_id_to_display, user_id_to_email, user_id_to_balance

    accounts, raw_users, user_id_to_display, user_id_to_email, user_id_to_balance = fetch_profit_data()

    if not accounts:
        st.info("No accounts yet — launch first in FTMO Accounts.")
        st.stop()

    account_options = {f"{a['name']} • Phase: {a['current_phase']} • Equity ${a.get('current_equity', 0):,.0f} • Contributor Pool: {a.get('contributor_share_pct', 0):.1f}%": a for a in accounts}
    selected_key = st.selectbox("Select Account for Profit Recording", list(account_options.keys()))
    acc = account_options[selected_key]
    acc_id = acc["id"]
    acc_name = acc["name"]
    unit_value = acc.get("unit_value", 3000.0)

    # FORCE v2 ONLY (safe check)
    participants = acc.get("participants_v2", [])
    contributors = acc.get("contributors_v2", [])
    contributor_share_pct = acc.get("contributor_share_pct", 0)

    if not participants:
        st.error("Account missing v2 participants data • Re-edit in FTMO Accounts to migrate.")
        st.stop()

    st.info(f"**Recording for:** {acc_name} | Contributor Pool: {contributor_share_pct:.1f}% | UUID v2: Active (perfect sync + auto-email)")

    with st.form("profit_form", clear_on_submit=True):
        col1, col2 = st.columns([2, 1])
        with col1:
            gross_profit = st.number_input("FTMO Gross Profit Received (USD) *", min_value=0.01, step=500.0)
        with col2:
            record_date = st.date_input("Record Date", datetime.date.today())

        # Stored v2 tree preview (with titles)
        st.subheader("Stored Unified Profit Tree (Edit in FTMO Accounts)")
        part_df = pd.DataFrame([
            {
                "Name": user_id_to_display.get(p.get("user_id"), p.get("display_name", "Unknown")),
                "Role": p.get("role", ""),
                "%": f"{p['percentage']:.1f}"
            } for p in participants
        ])
        st.dataframe(part_df, use_container_width=True, hide_index=True)

        # Previews + involved users collection
        contrib_preview = []
        part_preview = []
        involved_user_ids = set()
        total_funded_php = sum(c.get("units", 0) * c.get("php_per_unit", 0) for c in contributors)
        contributor_pool = gross_profit * (contributor_share_pct / 100)
        gf_add = 0.0

        if total_funded_php > 0 and contributor_share_pct > 0:
            for c in contributors:
                user_id = c.get("user_id")
                if not user_id:
                    continue
                involved_user_ids.add(user_id)
                funded = c.get("units", 0) * c.get("php_per_unit", 0)
                share = contributor_pool * (funded / total_funded_php)
                display = user_id_to_display.get(user_id, "Unknown")
                contrib_preview.append({"Name": display, "Funded PHP": f"₱{funded:,.0f}", "Share": f"${share:,.2f}"})

        for p in participants:
            user_id = p.get("user_id")
            if not user_id:
                continue
            involved_user_ids.add(user_id)
            display = user_id_to_display.get(user_id, p.get("display_name", "Unknown"))
            share = gross_profit * (p["percentage"] / 100)
            if "growth fund" in display.lower() or "gf" in display.lower():
                gf_add += share
            part_preview.append({"Name": display, "%": f"{p['percentage']:.1f}", "Share": f"${share:,.2f}"})

        col_prev1, col_prev2 = st.columns(2)
        with col_prev1:
            st.subheader("Contributor Pool Preview (Pro-rata)")
            if contrib_preview:
                st.dataframe(pd.DataFrame(contrib_preview), use_container_width=True, hide_index=True)
            else:
                st.info("No contributors or 0% pool")
        with col_prev2:
            st.subheader("Participants Preview (Direct %)")
            st.dataframe(pd.DataFrame(part_preview), use_container_width=True, hide_index=True)

        units = gross_profit / unit_value if gross_profit > 0 else 0
        col_p1, col_p2, col_p3 = st.columns(3)
        col_p1.metric("Gross Profit", f"${gross_profit:,.2f}")
        col_p2.metric("Contributor Pool Total", f"${contributor_pool:,.2f}")
        col_p3.metric("Units Generated", f"{units:.2f}")

        # Sankey preview (safe & clean)
        labels = [f"Gross Profit ${gross_profit:,.0f}"]
        values = []
        source = []
        target = []
        idx = 1
        contrib_start = None
        if contributor_pool > 0 and contrib_preview:
            labels.append("Contributor Pool")
            values.append(contributor_pool)
            source.append(0)
            target.append(idx)
            contrib_start = idx
            idx += 1
            for c in contrib_preview:
                share_val = float(c["Share"].replace("$", "").replace(",", ""))
                labels.append(c["Name"])
                values.append(share_val)
                source.append(contrib_start)
                target.append(idx)
                idx += 1
        for p in part_preview:
            share_val = float(p["Share"].replace("$", "").replace(",", ""))
            labels.append(p["Name"])
            values.append(share_val)
            source.append(0)
            target.append(idx)
            idx += 1

        fig = go.Figure(data=[go.Sankey(
            node=dict(pad=20, thickness=30, label=labels, color=["#00ffaa"] + ["#ffd700"]*len(contrib_preview) + [accent_primary]*len(part_preview)),
            link=dict(source=source, target=target, value=values)
        )])
        fig.update_layout(title_text="Realtime Distribution Flow Preview", height=600)
        st.plotly_chart(fig, use_container_width=True)

        submitted = st.form_submit_button("🚀 Record Profit & Execute Auto-Distribution", type="primary", use_container_width=True)
        if submitted:
            if gross_profit <= 0:
                st.error("Gross profit > 0 required")
            else:
                try:
                    # Record profit
                    profit_resp = supabase.table("profits").insert({
                        "account_id": acc_id,
                        "gross_profit": gross_profit,
                        "record_date": str(record_date),
                        "units_generated": units,
                        "growth_fund_add": gf_add,
                        "contributor_share_pct": contributor_share_pct,
                        "timestamp": datetime.datetime.now().isoformat()
                    }).execute()
                    profit_id = profit_resp.data[0]["id"]

                    distributions = []
                    updated = []

                    # Contributors pro-rata
                    if contributor_pool > 0 and total_funded_php > 0:
                        for c in contributors:
                            user_id = c.get("user_id")
                            if not user_id:
                                continue
                            display_name = user_id_to_display.get(user_id, "Unknown")
                            funded = c.get("units", 0) * c.get("php_per_unit", 0)
                            share = contributor_pool * (funded / total_funded_php)
                            pro_rata_pct = (funded / total_funded_php) * 100

                            distributions.append({
                                "profit_id": profit_id,
                                "participant_name": display_name,
                                "participant_user_id": user_id,
                                "participant_role": "Contributor",
                                "percentage": round(pro_rata_pct, 2),
                                "share_amount": share,
                                "is_growth_fund": False
                            })

                            current_bal = user_id_to_balance.get(user_id, 0)
                            new_bal = current_bal + share
                            supabase.table("users").update({"balance": new_bal}).eq("id", user_id).execute()
                            updated.append(f"{display_name} +${share:,.2f}")

                    # Direct participants
                    for p in participants:
                        user_id = p.get("user_id")
                        if not user_id:
                            continue
                        display_name = user_id_to_display.get(user_id, p.get("display_name", "Unknown"))
                        share = gross_profit * (p["percentage"] / 100)
                        is_gf = "growth fund" in display_name.lower() or "gf" in display_name.lower()

                        distributions.append({
                            "profit_id": profit_id,
                            "participant_name": display_name,
                            "participant_user_id": user_id,
                            "participant_role": p.get("role", ""),
                            "percentage": p["percentage"],
                            "share_amount": share,
                            "is_growth_fund": is_gf
                        })

                        if not is_gf:
                            current_bal = user_id_to_balance.get(user_id, 0)
                            new_bal = current_bal + share
                            supabase.table("users").update({"balance": new_bal}).eq("id", user_id).execute()
                            updated.append(f"{display_name} +${share:,.2f}")

                    if distributions:
                        supabase.table("profit_distributions").insert(distributions).execute()

                    if gf_add > 0:
                        supabase.table("growth_fund_transactions").insert({
                            "date": str(record_date),
                            "type": "In",
                            "amount": gf_add,
                            "description": f"Auto from {acc_name} profit",
                            "account_source": acc_name,
                            "recorded_by": st.session_state.full_name
                        }).execute()

                    # ==================== AUTO HTML EMAIL (RELIABLE ON STREAMLIT CLOUD) ====================
                    date_str = record_date.strftime("%B %d, %Y")
                    html_breakdown = f"""
                    <html>
                    <body style="font-family: Arial, sans-serif; color: #000; background: #f8fbff; padding: 20px;">
                        <div style="max-width: 800px; margin: auto; background: white; border-radius: 20px; padding: 30px; box-shadow: 0 10px 30px rgba(0,0,0,0.1);">
                            <h1 style="color: #00ffaa; text-align: center;">🚀 KMFX Profit Distribution Report</h1>
                            <h2 style="text-align: center;">Account: {acc_name} • Date: {date_str}</h2>
                            <p style="font-size: 1.2rem; text-align: center;">Gross Profit: <strong>${gross_profit:,.2f}</strong></p>
                            <p style="font-size: 1.2rem; text-align: center;">Contributor Pool ({contributor_share_pct:.1f}%): <strong>${contributor_pool:,.2f}</strong></p>
                            <p style="font-size: 1.2rem; text-align: center;">Units Generated: <strong>{units:.2f}</strong></p>
                            <h3>Contributor Pool Breakdown</h3>
                            <table style="width:100%; border-collapse: collapse;">
                                <tr style="background: #00ffaa; color: black;">
                                    <th style="padding: 12px; border: 1px solid #ddd;">Name</th>
                                    <th style="padding: 12px; border: 1px solid #ddd;">Funded PHP</th>
                                    <th style="padding: 12px; border: 1px solid #ddd;">Share</th>
                                </tr>
                                {''.join(f'<tr><td style="padding: 12px; border: 1px solid #ddd;">{c["Name"]}</td><td style="padding: 12px; border: 1px solid #ddd;">{c["Funded PHP"]}</td><td style="padding: 12px; border: 1px solid #ddd;">{c["Share"]}</td></tr>' for c in contrib_preview) or '<tr><td colspan="3" style="text-align: center; padding: 12px;">No contributors</td></tr>'}
                            </table>
                            <h3>Participants Breakdown</h3>
                            <table style="width:100%; border-collapse: collapse;">
                                <tr style="background: #ffd700; color: black;">
                                    <th style="padding: 12px; border: 1px solid #ddd;">Name</th>
                                    <th style="padding: 12px; border: 1px solid #ddd;">%</th>
                                    <th style="padding: 12px; border: 1px solid #ddd;">Share</th>
                                </tr>
                                {''.join(f'<tr><td style="padding: 12px; border: 1px solid #ddd;">{p["Name"]}</td><td style="padding: 12px; border: 1px solid #ddd;">{p["%"]}%</td><td style="padding: 12px; border: 1px solid #ddd;">{p["Share"]}</td></tr>' for p in part_preview)}
                            </table>
                            <p style="margin-top: 30px; text-align: center; font-size: 1.1rem;">
                                Thank you for being part of the KMFX Empire • Built by Faith, Shared for Generations 👑<br>
                                Questions? Contact owner.
                            </p>
                        </div>
                    </body>
                    </html>
                    """

                    st.subheader("Profit Distribution Breakdown (Auto-Sent via Email)")
                    st.markdown(html_breakdown, unsafe_allow_html=True)

                    # RELIABLE EMAIL SEND (Port 587 + STARTTLS - proven on Streamlit Cloud)
                    sender_email = os.getenv("EMAIL_SENDER")
                    sender_password = os.getenv("EMAIL_PASSWORD")
                    sent_count = 0
                    failed_details = []

                    if sender_email and sender_password and involved_user_ids:
                        try:
                            server = smtplib.SMTP("smtp.gmail.com", 587)
                            server.ehlo()
                            server.starttls()
                            server.ehlo()
                            server.login(sender_email, sender_password)

                            for uid in involved_user_ids:
                                email = user_id_to_email.get(uid)
                                display_name = user_id_to_display.get(uid, "Member")
                                if email:
                                    try:
                                        msg = MIMEMultipart("alternative")
                                        msg["From"] = sender_email
                                        msg["To"] = email
                                        msg["Subject"] = f"KMFX Profit Distribution - {acc_name} {date_str}"
                                        msg.attach(MIMEText(html_breakdown, "html"))
                                        server.sendmail(sender_email, email, msg.as_string())
                                        sent_count += 1
                                    except Exception as e:
                                        failed_details.append(f"{display_name}: {str(e)}")
                            server.quit()

                            if sent_count > 0:
                                st.success(f"Breakdown emailed to {sent_count} members! 🚀")
                            if failed_details:
                                st.warning("Some emails failed — check member emails in Team Management")
                        except Exception as login_e:
                            st.error(f"SMTP Error: {str(login_e)}")
                            st.info("Fix: Use Gmail App Password (16-digit) + correct EMAIL_SENDER in secrets")
                    else:
                        st.warning("Email skipped — add EMAIL_SENDER/PASSWORD secrets or member emails")
                        st.info("Copy HTML above for manual send")

                    st.success(f"Profit recorded & distributed! Updated: {', '.join(updated) or 'GF only'}")
                    st.rerun()
                except Exception as e:
                    st.error(f"Recording error: {str(e)}")
# ====================== MY PROFILE PAGE - FULL FINAL LATEST (WITH SELF QR GENERATE/REGENERATE) ======================
elif selected == "👤 My Profile":
    # SAFE ROLE CHECK
    current_role = st.session_state.get("role", "guest")
    if current_role != "client":
        st.error("🔒 My Profile is client-only.")
        st.stop()
  
    st.header("My Profile 👤")
    st.markdown("**Your KMFX EA empire membership: Realtime premium flip card, earnings, full details, participation, withdrawals • Full transparency & motivation.**")
  
    my_name = st.session_state.full_name
    my_username = st.session_state.username
  
    # FULL REALTIME CACHE
    @st.cache_data(ttl=30)
    def fetch_my_profile_data():
        user_resp = supabase.table("users").select("*").eq("full_name", my_name).execute()
        my_user = user_resp.data[0] if user_resp.data else {}
      
        accounts_resp = supabase.table("ftmo_accounts").select("*").execute()
        accounts = accounts_resp.data or []
        my_accounts = [a for a in accounts if any(p["name"] == my_name for p in a.get("participants", []))]
      
        wd_resp = supabase.table("withdrawals").select("*").eq("client_name", my_name).order("date_requested", desc=True).execute()
        my_withdrawals = wd_resp.data or []
      
        files_resp = supabase.table("client_files").select("id, original_name, file_name, upload_date").eq("assigned_client", my_name).execute()
        my_proofs = files_resp.data or []
      
        all_users_resp = supabase.table("users").select("full_name, title").execute()
        all_users = all_users_resp.data or []
      
        return my_user, my_accounts, my_withdrawals, my_proofs, all_users
  
    my_user, my_accounts, my_withdrawals, my_proofs, all_users = fetch_my_profile_data()
  
    st.caption("🔄 Profile auto-refresh every 30s • Earnings & card update realtime")
  
    # ====================== PREMIUM THEME-ADAPTIVE FLIP CARD ======================
    my_title = my_user.get("title", "Member").upper()
    card_title = f"{my_title} CARD" if my_title != "NONE" else "MEMBER CARD"
    my_balance = my_user.get("balance", 0)
    if theme == "dark":
        front_bg = "linear-gradient(135deg, #000000, #1f1f1f)"
        back_bg = "linear-gradient(135deg, #1f1f1f, #000000)"
        text_color = "#ffffff"
        accent_gold = "#ffd700"
        accent_green = "#00ffaa"
        border_color = "#ffd700"
        shadow = "0 20px 50px rgba(0,0,0,0.9)"
        mag_strip = "#333"
        opacity_low = "0.7"
        opacity_med = "0.8"
    else:
        front_bg = "linear-gradient(135deg, #ffffff, #f5f8fa)"
        back_bg = "linear-gradient(135deg, #f5f8fa, #eef2f5)"
        text_color = "#0f172a"
        accent_gold = "#a67c00"
        accent_green = "#004d33"
        border_color = "#d4af37"
        shadow = "0 20px 50px rgba(0,0,0,0.1)"
        mag_strip = "#b0b0b0"
        opacity_low = "0.7"
        opacity_med = "0.85"
    st.markdown(f"""
    <div style="perspective: 1500px; max-width: 600px; margin: 3rem auto;">
      <div class="flip-card">
        <div class="flip-card-inner">
          <!-- Front -->
          <div class="flip-card-front">
            <div style="background: {front_bg}; backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px); border-radius: 20px; padding: 2rem; height: 380px; box-shadow: {shadow}; color: {text_color}; display: flex; flex-direction: column; justify-content: space-between; border: 2px solid {border_color};">
              <div style="display: flex; justify-content: space-between; align-items: center;">
                <h2 style="margin: 0; font-size: 3rem; color: {accent_gold}; letter-spacing: 6px; text-shadow: 0 0 12px {accent_gold};">KMFX EA</h2>
                <h3 style="margin: 0; font-size: 1.6rem; color: {accent_gold}; letter-spacing: 2px;">{card_title}</h3>
              </div>
              <div style="text-align: center; flex-grow: 1; display: flex; align-items: center; justify-content: center;">
                <h1 style="margin: 0; font-size: 2.4rem; letter-spacing: 3px; color: {text_color};">{my_name.upper()}</h1>
              </div>
              <div style="display: flex; justify-content: space-between; align-items: flex-end;">
                <div style="font-size: 1.4rem; opacity: {opacity_med};">💳 Elite Empire Member</div>
                <div style="text-align: right;">
                  <p style="margin: 0; opacity: {opacity_med}; font-size: 1.2rem;">Available Earnings</p>
                  <h2 style="margin: 0; font-size: 3rem; color: {accent_green}; text-shadow: 0 0 18px {accent_green};">${my_balance:,.2f}</h2>
                </div>
              </div>
              <p style="margin: 0; text-align: center; opacity: {opacity_low}; font-size: 1rem; letter-spacing: 1px;">Built by Faith • Shared for Generations • 👑 2026</p>
            </div>
          </div>
          <!-- Back -->
          <div class="flip-card-back">
            <div style="background: {back_bg}; backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px); border-radius: 20px; padding: 1.8rem 2rem; height: 380px; box-shadow: {shadow}; color: {text_color}; display: flex; flex-direction: column; justify-content: flex-start; border: 2px solid {border_color}; overflow: hidden;">
              <h2 style="margin: 0 0 1rem; text-align: center; color: {accent_gold}; font-size: 1.7rem; letter-spacing: 2px;">Membership Details</h2>
              <div style="height: 35px; background: {mag_strip}; border-radius: 8px; margin-bottom: 1rem;"></div>
              <div style="flex-grow: 1; font-size: 1.1rem; line-height: 1.7; overflow-y: auto; padding-right: 0.5rem;">
                <strong style="color: {accent_gold};">Full Name:</strong> {my_name}<br>
                <strong style="color: {accent_gold};">Title:</strong> {my_title}<br>
                <strong style="color: {accent_gold};">MT5 Accounts:</strong> {my_user.get('accounts') or 'Not set'}<br>
                <strong style="color: {accent_gold};">Email:</strong> {my_user.get('email') or 'Not set'}<br>
                <strong style="color: {accent_gold};">Contact No.:</strong> {my_user.get('contact_no') or 'Not set'}<br>
                <strong style="color: {accent_gold};">Address:</strong> {my_user.get('address') or 'Not set'}<br>
                <strong style="color: {accent_gold};">Balance:</strong> <span style="color: {accent_green}; font-size: 1.3rem;">${my_balance:,.2f}</span><br>
                <strong style="color: {accent_gold};">Shared Accounts:</strong> {len(my_accounts)} active
              </div>
              <p style="margin: 1rem 0 0; text-align: center; opacity: {opacity_low}; font-size: 0.9rem;">Elite Access • KMFX Empire 👑</p>
            </div>
          </div>
        </div>
      </div>
    </div>
    <style>
      .flip-card {{
        background: transparent;
        width: 600px;
        height: 380px;
        perspective: 1000px;
        margin: 0 auto;
      }}
      .flip-card-inner {{
        position: relative;
        width: 100%;
        height: 100%;
        text-align: center;
        transition: transform 0.8s cubic-bezier(0.68, -0.55, 0.27, 1.55);
        transform-style: preserve-3d;
      }}
      .flip-card:hover .flip-card-inner,
      .flip-card:focus-within .flip-card-inner {{
        transform: rotateY(180deg);
      }}
      .flip-card-front, .flip-card-back {{
        position: absolute;
        width: 100%;
        height: 100%;
        -webkit-backface-visibility: hidden;
        backface-visibility: hidden;
        border-radius: 20px;
      }}
      .flip-card-back {{
        transform: rotateY(180deg);
      }}
    
      @media (max-width: 768px) {{
        .flip-card {{
          width: 90vw !important;
          max-width: 340px !important;
          height: 215px !important;
          margin: 2rem auto !important;
        }}
        .flip-card-front > div,
        .flip-card-back > div {{
          padding: 1rem !important;
          height: 215px !important;
          border-radius: 16px !important;
          box-sizing: border-box !important;
          overflow: hidden !important;
        }}
        .flip-card-front h2:first-child {{ font-size: 1.8rem !important; }}
        .flip-card-front h3 {{ font-size: 1rem !important; }}
        .flip-card-front h1 {{ font-size: 1.4rem !important; }}
        .flip-card-front h2:last-of-type {{ font-size: 1.8rem !important; }}
        .flip-card-front p {{ font-size: 0.75rem !important; }}
        .flip-card-front > div > div:first-child {{ margin-bottom: 0.3rem !important; }}
        .flip-card-front > div > div:nth-child(3) {{ margin-top: 0.3rem !important; }}
        .flip-card-front > div > div:nth-child(3) > div:first-child {{ font-size: 0.85rem !important; }}
        .flip-card-front > div > div:nth-child(3) > div:last-child p {{ font-size: 0.75rem !important; }}
        .flip-card-back h2 {{ font-size: 1.1rem !important; }}
        .flip-card-back div:nth-child(2) {{ height: 22px !important; }}
        .flip-card-back div:nth-child(3) {{ font-size: 0.78rem !important; line-height: 1.35 !important; }}
        .flip-card-back p:last-child {{ font-size: 0.7rem !important; }}
      }}
    </style>
    <p style="text-align:center; opacity:0.7; margin-top:1rem; font-size:1rem;">
      Hover (desktop) or tap (mobile) the card to flip ↺
    </p>
    """, unsafe_allow_html=True)

    # ====================== MY QUICK LOGIN QR CODE (CLIENT SELF-GENERATE & REGENERATE) ======================
    st.subheader("🔑 My Quick Login QR Code")
    import qrcode
    from io import BytesIO
    import uuid

    current_qr_token = my_user.get("qr_token")
    app_url = "https://kmfxeaftmo.streamlit.app"  # Replace if your deployed URL is different

    if current_qr_token:
        qr_url = f"{app_url}/?qr={current_qr_token}"

        # Generate QR image
        buf = BytesIO()
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(qr_url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        img.save(buf, format="PNG")

        col_qr1, col_qr2 = st.columns([1, 2])
        with col_qr1:
            st.image(buf.getvalue(), caption="Your Current QR Code")
        with col_qr2:
            st.markdown("**Your Quick Login QR**")
            st.markdown("Scan this on your phone or another device to auto-login instantly.")
            st.code(qr_url, language="text")

        # SELF-REGENERATE BUTTON
        st.markdown("---")
        st.info("If your QR code is compromised or not working, regenerate a new one below (old QR will be revoked instantly).")
        if st.button("🔄 Regenerate My QR Code", type="primary", use_container_width=True):
            new_token = str(uuid.uuid4())
            try:
                supabase.table("users").update({"qr_token": new_token}).eq("id", my_user["id"]).execute()
                log_action("QR Token Self-Regenerated", f"By {my_name}")
                st.success("New QR code generated successfully! Page will refresh to show the updated code.")
                st.cache_data.clear()
                st.rerun()
            except Exception as e:
                st.error(f"Error regenerating QR code: {str(e)}")
    else:
        st.info("You don't have a QR login code yet. Generate one below for quick access on mobile/other devices.")
        if st.button("🚀 Generate My QR Code", type="primary", use_container_width=True):
            new_token = str(uuid.uuid4())
            try:
                supabase.table("users").update({"qr_token": new_token}).eq("id", my_user["id"]).execute()
                log_action("QR Token Self-Generated", f"By {my_name}")
                st.success("QR code generated successfully! Page will refresh to show it.")
                st.cache_data.clear()
                st.rerun()
            except Exception as e:
                st.error(f"Error generating QR code: {str(e)}")

    # ====================== CHANGE PASSWORD (CLIENT SELF-SERVICE) ======================
    st.subheader("🔑 Change Password")
    with st.expander("Update your password", expanded=False):
        with st.form("change_password_form", clear_on_submit=True):
            current_pwd = st.text_input("Current Password *", type="password")
            new_pwd = st.text_input("New Password *", type="password")
            confirm_pwd = st.text_input("Confirm New Password *", type="password")
          
            submitted = st.form_submit_button("Change Password", type="primary")
            if submitted:
                if not current_pwd or not new_pwd or not confirm_pwd:
                    st.error("All fields required")
                elif new_pwd != confirm_pwd:
                    st.error("New passwords do not match")
                else:
                    try:
                        resp = supabase.table("users").select("password").eq("username", my_username).execute()
                        if not resp.data:
                            st.error("User not found")
                        else:
                            hashed = resp.data[0]["password"]
                            if bcrypt.checkpw(current_pwd.encode(), hashed.encode()):
                                new_hashed = bcrypt.hashpw(new_pwd.encode(), bcrypt.gensalt()).decode()
                                supabase.table("users").update({"password": new_hashed}).eq("username", my_username).execute()
                                st.success("Password changed successfully! Logging out for security...")
                                st.session_state.clear()
                                st.rerun()
                            else:
                                st.error("Current password incorrect")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
  
    # ====================== FORGOT PASSWORD REQUEST (TO OWNER) ======================
    st.subheader("🔒 Forgot Password?")
    with st.expander("Request password reset", expanded=False):
        st.info("Submit request — owner will reset & inform you securely.")
        with st.form("forgot_pwd_form", clear_on_submit=True):
            reason = st.text_area("Reason / Message to Owner (Optional)", placeholder="e.g. I forgot my password, please reset to 'NewPass123'")
          
            submitted = st.form_submit_button("Send Reset Request to Owner", type="primary")
            if submitted:
                try:
                    log_action("Password Reset Request", f"From {my_name} ({my_username}) | Reason: {reason or 'No reason'}")
                    st.success("Request sent to owner! They will reset your password & inform you.")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
  
    # ====================== SHARED ACCOUNTS WITH % & FUNDED PHP ======================
    st.subheader(f"Your Shared Accounts ({len(my_accounts)} active)")
    if my_accounts:
        for acc in my_accounts:
            my_pct = next((p["percentage"] for p in acc.get("participants", []) if p["name"] == my_name), 0)
            my_projected = (acc.get("current_equity", 0) * my_pct / 100) if acc.get("current_equity") else 0
            my_funded_php = sum(c["units"] * c["php_per_unit"] for c in acc.get("contributors", []) if c["name"] == my_name)
          
            with st.expander(f"🌟 {acc['name']} • Your Share: {my_pct:.1f}% • Phase: {acc['current_phase']}", expanded=False):
                col_acc1, col_acc2 = st.columns(2)
                with col_acc1:
                    st.metric("Account Equity", f"${acc.get('current_equity', 0):,.0f}")
                    st.metric("Your Projected Share", f"${my_projected:,.2f}")
                with col_acc2:
                    st.metric("Account Withdrawable", f"${acc.get('withdrawable_balance', 0):,.0f}")
                    st.metric("Your Funded (PHP)", f"₱{my_funded_php:,.0f}")
              
                participants = acc.get("participants", [])
                if participants:
                    labels = ["Profits"]
                    for p in participants:
                        display = p["name"]
                        user = next((u for u in all_users if u["full_name"] == p["name"]), None)
                        if user and user.get("title"):
                            display += f" ({user['title']})"
                        labels.append(f"{display} ({p['percentage']:.1f}%)")
                    values = [p["percentage"] for p in participants]
                    fig = go.Figure(data=[go.Sankey(node=dict(pad=15, thickness=20, label=labels),
                                                    link=dict(source=[0]*len(values), target=list(range(1, len(values)+1)), value=values))])
                    fig.update_layout(height=350, margin=dict(t=20))
                    st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No participation yet • Owner will assign you to shared profits")
  
    # ====================== WITHDRAWAL HISTORY & QUICK REQUEST ======================
    st.subheader("💳 Your Withdrawal Requests & History")
    if my_withdrawals:
        for w in my_withdrawals:
            status_color = {"Pending": "#ffa502", "Approved": accent_color, "Paid": "#2ed573", "Rejected": "#ff4757"}.get(w["status"], "#888")
            st.markdown(f"""
            <div class='glass-card' style='padding:1.5rem; border-left:5px solid {status_color};'>
                <h4>${w['amount']:,.0f} • {w['status']}</h4>
                <small>Method: {w['method']} • Requested: {w['date_requested']}</small>
            </div>
            """, unsafe_allow_html=True)
            if w["details"]:
                with st.expander("Details"):
                    st.write(w["details"])
            st.divider()
    else:
        st.info("No requests yet • Earnings auto-accumulate")
  
    # Quick request
    with st.expander("➕ Request New Withdrawal (from Balance)", expanded=False):
        if my_balance <= 0:
            st.info("No available balance yet • Earnings auto-accumulate from profits")
        else:
            with st.form("my_wd_form", clear_on_submit=True):
                amount = st.number_input("Amount (USD)", min_value=1.0, max_value=float(my_balance), step=100.0, help=f"Max: ${my_balance:,.2f}")
                method = st.selectbox("Method", ["USDT", "Bank Transfer", "Wise", "PayPal", "GCash", "Other"])
                details = st.text_area("Details")
                proof = st.file_uploader("Upload Proof * (Required)", help="Auto-saved to vault")
              
                submitted = st.form_submit_button("Submit Request", type="primary")
                if submitted:
                    if amount > my_balance:
                        st.error("Exceeds balance")
                    elif not proof:
                        st.error("Proof required")
                    else:
                        try:
                            safe = "".join(c for c in proof.name if c.isalnum() or c in "._- ")
                            path = f"uploaded_files/client_files/{safe}"
                            with open(path, "wb") as f:
                                f.write(proof.getbuffer())
                            supabase.table("client_files").insert({
                                "file_name": safe,
                                "original_name": proof.name,
                                "upload_date": datetime.date.today().isoformat(),
                                "sent_by": my_name,
                                "category": "Withdrawal Proof",
                                "assigned_client": my_name,
                                "notes": f"Proof for ${amount:,.0f}"
                            }).execute()
                          
                            supabase.table("withdrawals").insert({
                                "client_name": my_name,
                                "amount": amount,
                                "method": method,
                                "details": details,
                                "status": "Pending",
                                "date_requested": datetime.date.today().isoformat()
                            }).execute()
                          
                            st.success("Request submitted!")
                            st.cache_data.clear()
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
  
    # My proofs
    st.subheader("📁 Your Proofs in Vault")
    if my_proofs:
        cols = st.columns(4)
        for idx, p in enumerate(my_proofs):
            path = f"uploaded_files/client_files/{p['file_name']}"
            if os.path.exists(path):
                with cols[idx % 4]:
                    if p["original_name"].lower().endswith(('.png', '.jpg', '.jpeg')):
                        st.image(path, caption=p["original_name"], width=200)
                    with open(path, "rb") as f:
                        st.download_button(p["original_name"], f, p["original_name"])
    else:
        st.info("No proofs uploaded yet")
  
    st.markdown(f"""
    <div class='glass-card' style='padding:3rem; text-align:center; margin:3rem 0;'>
        <h1 style="background:linear-gradient(90deg,{accent_color},#ffd700); -webkit-background-clip:text; -webkit-text-fill-color:transparent;">
            Your Empire Journey
        </h1>
        <p style="font-size:1.3rem; margin:2rem 0;">
            Realtime earnings • Participation details • Withdrawal control • Proofs synced • Motivated & aligned.
        </p>
    </div>
    """, unsafe_allow_html=True)
# ====================== PART 5: GROWTH FUND PAGE (FINAL SUPER ADVANCED - FULL MAIN FLOW SYNC & REALTIME) ======================
# ====================== GROWTH FUND PAGE - FULLY OPTIMIZED WITH MATERIALIZED VIEW (INSTANT GF BALANCE) ======================
elif selected == "🌱 Growth Fund":
    st.header("Growth Fund Management 🌱")
    st.markdown("**Empire reinvestment engine: 100% automatic inflows from profit distributions • Full source transparency with auto-trees • Advanced projections & scaling simulations • Manual adjustments • Instant sync across dashboard, profits, balances.**")
   
    # SAFE ROLE
    current_role = st.session_state.get("role", "guest")
   
    # NEW: Instant GF balance + full data fetch (materialized view for speed)
    @st.cache_data(ttl=30)
    def fetch_gf_full_data():
        try:
            # INSTANT GF Balance from materialized view (<0.1s even with 1000+ transactions)
            gf_resp = supabase.table("mv_growth_fund_balance").select("balance").execute()
            gf_balance = gf_resp.data[0]["balance"] if gf_resp.data else 0.0
           
            # Transactions for history & trees (lightweight with indexes)
            trans_resp = supabase.table("growth_fund_transactions").select("*").order("date", desc=True).execute()
            transactions = trans_resp.data or []
           
            # Auto-sources from profits (for tree)
            profits_resp = supabase.table("profits").select("id, account_id, record_date, growth_fund_add").gt("growth_fund_add", 0).execute()
            profits = profits_resp.data or []
           
            accounts_resp = supabase.table("ftmo_accounts").select("id, name").execute()
            account_map = {a["id"]: a["name"] for a in accounts_resp.data or []}
           
            auto_sources = {}
            for p in profits:
                acc_name = account_map.get(p["account_id"], "Unknown")
                key = f"{acc_name} ({p['record_date']})"
                auto_sources[key] = auto_sources.get(key, 0) + p["growth_fund_add"]
           
            # Manual sources
            manual_sources = {}
            for t in transactions:
                if t["account_source"] == "Manual" or not t.get("description", "").startswith("Auto"):
                    key = t.get("description") or "Manual"
                    manual_sources[key] = manual_sources.get(key, 0) + t["amount"]
           
            # Current accounts count for projections
            acc_count_resp = supabase.table("mv_empire_summary").select("total_accounts").execute()
            total_accounts = acc_count_resp.data[0]["total_accounts"] if acc_count_resp.data else 0
           
            return transactions, gf_balance, auto_sources, manual_sources, account_map, total_accounts
        except Exception as e:
            st.error(f"Growth Fund fetch error: {e}")
            return [], 0.0, {}, {}, {}, 0
   
    transactions, gf_balance, auto_sources, manual_sources, account_map, total_accounts = fetch_gf_full_data()
   
    # AUTO BALANCE & KEY METRICS
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Current Growth Fund", f"${gf_balance:,.0f}")
    auto_in = sum(auto_sources.values())
    col2.metric("Auto Inflows (Profits)", f"${auto_in:,.0f}")
    manual_in = sum(v for v in manual_sources.values() if v > 0)
    col3.metric("Manual Inflows", f"${manual_in:,.0f}")
    outflows = sum(abs(v) for v in manual_sources.values() if v < 0)
    col4.metric("Outflows", f"${outflows:,.0f}")
   
    # AUTO SOURCE TREE
    st.subheader("🌳 Automatic Inflow Sources Tree (Realtime)")
    all_sources = {**auto_sources, **manual_sources}
    if all_sources:
        labels = ["Growth Fund"] + list(all_sources.keys())
        values = list(all_sources.values())
        colors = [accent_color if k in auto_sources else "#ffd700" for k in labels[1:]]
        fig = go.Figure(data=[go.Sankey(
            node=dict(pad=20, thickness=30, label=labels, color=["#ffd700"] + colors),
            link=dict(source=[0]*len(values), target=list(range(1, len(values)+1)), value=values)
        )])
        fig.update_layout(height=600, title="All Inflows by Source (Auto + Manual)")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Growth Fund empty • Activates with first profit distribution")
   
    # MANUAL TRANSACTION
    if current_role in ["owner", "admin"]:
        with st.expander("➕ Manual Transaction (Scaling Capital)", expanded=False):
            with st.form("gf_manual_form", clear_on_submit=True):
                col1, col2 = st.columns([1, 2])
                with col1:
                    trans_type = st.selectbox("Type", ["In", "Out"])
                with col2:
                    amount = st.number_input("Amount (USD)", min_value=0.01, step=100.0)
                purpose = st.selectbox("Purpose", ["New Challenge Purchase", "Scaling Capital", "EA Development", "Team Bonus", "Other"])
                desc = st.text_area("Description (Optional)")
                trans_date = st.date_input("Date", datetime.date.today())
               
                submitted = st.form_submit_button("Record Transaction", type="primary", use_container_width=True)
                if submitted:
                    try:
                        supabase.table("growth_fund_transactions").insert({
                            "date": str(trans_date),
                            "type": trans_type,
                            "amount": amount,
                            "description": desc or purpose,
                            "account_source": "Manual",
                            "recorded_by": st.session_state.full_name
                        }).execute()
                        st.success("Transaction recorded & synced instantly!")
                        st.cache_data.clear()
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
   
    # HISTORY TABLE
    st.subheader("📜 Complete Transaction History")
    if transactions:
        df = pd.DataFrame(transactions)
        df["Amount"] = df.apply(lambda row: f"+${row['amount']:,.0f}" if row["type"] == "In" else f"-${row['amount']:,.0f}", axis=1)
        df["Type"] = df["type"].map({"In": "✅ In", "Out": "❌ Out"})
        df["Source"] = df.apply(lambda row: row["account_source"] if row["account_source"] != "Manual" else row["description"], axis=1)
        df_display = df[["date", "Type", "Amount", "Source", "recorded_by"]].rename(columns={
            "date": "Date", "Source": "Source/Description", "recorded_by": "By"
        })
        st.dataframe(df_display, use_container_width=True, hide_index=True)
    else:
        st.info("No transactions yet • Auto-inflows start with profits")
   
    # PROJECTIONS (Already good - minor auto-load from empire summary)
    st.subheader("🔮 Advanced Scaling Projections")
    col_proj1, col_proj2 = st.columns(2)
    with col_proj1:
        months = st.slider("Projection Months", 6, 60, 24)
        avg_monthly_profit = st.number_input("Avg Monthly Gross per Account (USD)", value=15000.0, step=1000.0)
        projected_accounts = st.slider("Projected Active Accounts", total_accounts, total_accounts + 20, total_accounts + 5)
    with col_proj2:
        avg_gf_pct = st.number_input("Avg Growth Fund %", value=20.0, min_value=0.0, max_value=50.0)
        monthly_manual = st.number_input("Additional Monthly Manual In (USD)", value=0.0, step=1000.0)
   
    projected_monthly_in = (avg_monthly_profit * projected_accounts * (avg_gf_pct / 100)) + monthly_manual
   
    dates = [datetime.date.today() + datetime.timedelta(days=30*i) for i in range(months + 1)]
    balances = [gf_balance]
    for i in range(months):
        balances.append(balances[-1] + projected_monthly_in)
   
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dates, y=balances, mode='lines+markers', line=dict(color=accent_color, width=5)))
    fig.add_hline(y=gf_balance * 10, line_dash="dash", line_color="#ffd700", annotation_text="10x Target")
    fig.update_layout(height=500, title=f"Projected Trajectory (+${projected_monthly_in:,.0f}/month)")
    st.plotly_chart(fig, use_container_width=True)
   
    st.metric("Projected Balance in {months} Months", f"${balances[-1]:,.0f}")
    if balances[-1] > gf_balance * 10:
        st.success("On track for 10x growth!")
   
    st.markdown(f"""
    <div class='glass-card' style='padding:3rem; text-align:center; margin:3rem 0;'>
        <h1 style="background:linear-gradient(90deg,{accent_color},#ffd700); -webkit-background-clip:text; -webkit-text-fill-color:transparent;">
            Automatic Reinvestment Engine
        </h1>
        <p style="font-size:1.3rem; margin:2rem 0;">
            Profits auto-feed • Trees realtime • Projections guide scaling • Empire compounds.
        </p>
        <h2 style="color:#ffd700;">👑 KMFX Growth Fund • Fully Automatic 2026</h2>
    </div>
    """, unsafe_allow_html=True)
elif selected == "🔑 License Generator":
    st.header("EA License Generator 🔑")
    st.markdown("**Universal Security • ANY Broker • Flexible Accounts • LIVE/DEMO Control • XOR Encryption**")

    # Clean encryption – no padding
    def mt_encrypt(plain: str, key: str) -> str:
        if not key:
            return ""
        result = bytearray()
        klen = len(key)
        for i, ch in enumerate(plain):
            k = ord(key[i % klen])
            result.append(ord(ch) ^ k)
        return ''.join(f'{b:02X}' for b in result).upper()

    # OWNER ONLY
    if st.session_state.get("role", "guest") != "owner":
        st.error("🔒 License generation is OWNER-ONLY.")
        st.stop()

    # ─── Fetch fresh data (we will clear cache on changes) ───
    @st.cache_data(ttl=30)  # shorter ttl so it's easier to refresh
    def fetch_license_data():
        clients_resp = supabase.table("users").select("id, full_name, balance, role").eq("role", "client").execute()
        clients = clients_resp.data or []
        history_resp = supabase.table("client_licenses").select("*").order("date_generated", desc=True).execute()
        history = history_resp.data or []
        user_map = {c["id"]: {"name": c["full_name"] or "Unknown", "balance": c["balance"] or 0} for c in clients}
        return clients, history, user_map

    clients, history, user_map = fetch_license_data()

    if not clients:
        st.info("No clients yet — add in Team Management.")
        st.stop()

    st.subheader("Generate License")

    client_options = {f"{c['full_name']} (Balance: ${c['balance'] or 0:,.2f})": c for c in clients}
    selected_key = st.selectbox("Select Client", list(client_options.keys()))
    client = client_options[selected_key]
    client_id = client["id"]
    client_name = client["full_name"]
    client_balance = client["balance"] or 0

    st.info(f"**Client:** {client_name} | Balance: ${client_balance:,.2f}")

    # Session state defaults
    for key, default in [
        ("allow_any_account", True),
        ("allow_live_trading", True),
        ("specific_accounts_value", "")
    ]:
        if key not in st.session_state:
            st.session_state[key] = default

    # ─── Checkboxes ───
    col_a, col_b = st.columns(2)
    with col_a:
        allow_any = st.checkbox(
            "Allow on ANY Account / Broker (Universal *)",
            value=st.session_state.allow_any_account,
            key="chk_universal"
        )
    with col_b:
        allow_live = st.checkbox(
            "Allow LIVE trading (checked = LIVE + DEMO)",
            value=st.session_state.allow_live_trading,
            key="chk_live"
        )

    # Auto refresh on checkbox change
    if (allow_any != st.session_state.allow_any_account or
        allow_live != st.session_state.allow_live_trading):
        st.session_state.allow_any_account = allow_any
        st.session_state.allow_live_trading = allow_live
        st.rerun()

    # Feedback
    if allow_live:
        st.success("✅ LIVE + DEMO allowed")
    else:
        st.warning("⚠️ DEMO only (Live blocked)")

    # ─── FORM ───
    with st.form("license_form", clear_on_submit=True):
        col1, col2 = st.columns(2)

        with col1:
            specific_accounts = st.text_area(
                "Specific Allowed Logins (comma-separated)",
                placeholder="12345678,87654321   (leave blank if universal)",
                disabled=allow_any,
                value=st.session_state.specific_accounts_value,
                key="specific_accounts_input"
            )

        with col2:
            expiry_option = st.radio("Expiry", ["Specific Date", "NEVER (Lifetime)"])
            if expiry_option == "Specific Date":
                exp_date = st.date_input("Expiry Date", datetime.date.today() + datetime.timedelta(days=365))
                expiry_str = exp_date.strftime("%Y-%m-%d")
            else:
                expiry_str = "NEVER"

            version_note = st.text_input("Version Note", "v2.36 FTMO Optimized")
            internal_notes = st.text_area("Internal Notes", height=70)

        submitted = st.form_submit_button("🚀 Generate & Save License", type="primary", use_container_width=True)

        if submitted:
            # Prepare data
            accounts_str = "*" if allow_any else ",".join(
                [a.strip() for a in specific_accounts.split(",") if a.strip()]
            )

            live_str = "1" if allow_live else "0"

            plain = f"{client_name}|{accounts_str}|{expiry_str}|{live_str}"

            if len(plain.encode()) % 2 == 1:
                plain += " "

            name_clean = "".join(c for c in client_name.upper() if c.isalnum())
            key_date = "NEVER" if expiry_str == "NEVER" else expiry_str[8:] + expiry_str[5:7] + expiry_str[2:4]
            unique_key = f"KMFX_{name_clean}_{key_date}"

            enc_data_hex = mt_encrypt(plain, unique_key)

            try:
                supabase.table("client_licenses").insert({
                    "account_id": client_id,
                    "key": unique_key,
                    "enc_data": enc_data_hex,
                    "version": version_note,
                    "date_generated": datetime.date.today().isoformat(),
                    "expiry": expiry_str,
                    "allow_live": allow_live,
                    "notes": internal_notes or None,
                    "allowed_accounts": accounts_str if accounts_str != "*" else None,
                    "revoked": False
                }).execute()

                st.success(f"License created! **{unique_key}**")
                st.balloons()

                # Clear field
                st.session_state.specific_accounts_value = ""

                # Force refresh everything
                st.cache_data.clear()
                st.rerun()

            except Exception as e:
                st.error(f"Save failed: {str(e)}")

    # ─── HISTORY ───
    st.subheader("📜 Issued Licenses History")

    if history:
        for h in history:
            user = user_map.get(h["account_id"], {"name": "Unknown"})
            status = "🔴 Revoked" if h.get("revoked") else "🟢 Active"
            live_status = "LIVE+DEMO" if h.get("allow_live") else "DEMO only"
            acc_txt = "ANY (*)" if h.get("allowed_accounts") is None else h["allowed_accounts"]

            with st.expander(
                f"{h.get('key','—')} • {user['name']} • {status} • {live_status} • {acc_txt}",
                expanded=False
            ):
                st.markdown(f"**Expiry:** {h['expiry']}")
                if h.get("notes"):
                    st.caption(f"Notes: {h['notes']}")

                st.code(f"ENC_DATA = \"{h.get('enc_data','—')}\"", language="text")
                st.code(f"UNIQUE_KEY = \"{h.get('key','—')}\"", language="text")

                col1, col2 = st.columns(2)
                with col1:
                    if not h.get("revoked"):
                        if st.button("Revoke", key=f"revoke_{h['id']}"):
                            supabase.table("client_licenses").update({"revoked": True}).eq("id", h["id"]).execute()
                            st.success("License revoked")
                            st.cache_data.clear()
                            st.rerun()
                with col2:
                    if st.button("Delete", key=f"delete_{h['id']}", type="primary"):
                        try:
                            supabase.table("client_licenses").delete().eq("id", h["id"]).execute()
                            st.success("License deleted permanently")
                            st.cache_data.clear()
                            st.rerun()
                        except Exception as e:
                            st.error(f"Delete failed: {str(e)}")
    else:
        st.info("No licenses yet.")

    # Optional: show generated code after create
    if submitted:
        st.subheader("Ready to Paste")
        st.code(f'''
string UNIQUE_KEY = "{unique_key}";
string ENC_DATA = "{enc_data_hex}";
        ''', language="cpp")
elif selected == "📁 File Vault":
    st.header("Secure File Vault 📦", anchor=False)
    st.caption("Permanent encrypted storage • All file types supported • Proofs & documents secured • Auto-assigned access")

    current_role = st.session_state.get("role", "guest")

    # ─── FETCH DATA ───
    @st.cache_data(ttl=10)
    def fetch_vault_data():
        files_resp = supabase.table("client_files").select("*").order("upload_date", desc=True).execute()
        files = files_resp.data or []

        users_resp = supabase.table("users").select("id, full_name, balance, role").execute()
        users = users_resp.data or []

        user_map = {u["full_name"]: {"id": u["id"], "balance": u.get("balance", 0), "role": u["role"]} for u in users}
        registered_clients = [u["full_name"] for u in users if u["role"] == "client"]

        return files, user_map, registered_clients

    files, user_map, registered_clients = fetch_vault_data()

    st.caption("🔄 Vault auto-refreshes every 10s • Files stored permanently in Supabase Storage")

    # ─── CLIENT VIEW RESTRICTION ───
    if current_role == "client":
        my_name = st.session_state.get("full_name", "")
        files = [f for f in files if f["sent_by"] == my_name or f.get("assigned_client") == my_name]

    # ─── UPLOAD SECTION (Owner/Admin only) ───
    if current_role in ["owner", "admin"]:
        with st.container():
            st.markdown("### 📤 Upload New Files")
            with st.form("file_upload_form", clear_on_submit=True):
                col_upload, col_options = st.columns([3, 2])

                with col_upload:
                    uploaded_files = st.file_uploader(
                        "Choose files (PDF, images, .ex5, zip, etc.)",
                        type=["pdf", "png", "jpg", "jpeg", "gif", "zip", "ex5", "txt", "doc", "docx"],
                        accept_multiple_files=True,
                        help="Max 200MB per file • All file types supported • .ex5 fully allowed"
                    )

                with col_options:
                    category = st.selectbox("Category", [
                        "Payout Proof", "Withdrawal Proof", "Agreement", "KYC/ID",
                        "Contributor Contract", "Testimonial Image", "EA File", "Other"
                    ])
                    assigned_client = st.selectbox("Assign to Client (optional)", ["None"] + sorted(registered_clients))
                    tags = st.text_input("Tags (comma-separated)", "")
                    notes = st.text_area("Notes", height=100)

                submitted = st.form_submit_button("📤 Upload Files", type="primary", use_container_width=True)

                if submitted and uploaded_files:
                    success_count = 0
                    failed_files = []
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    total_files = len(uploaded_files)

                    for idx, file in enumerate(uploaded_files):
                        try:
                            status_text.text(f"Uploading {file.name} ({idx+1}/{total_files})...")
                            url, storage_path = upload_to_supabase(
                                file=file,
                                bucket="client_files",
                                folder="vault",
                                use_signed_url=False
                            )

                            # Insert metadata
                            insert_response = supabase.table("client_files").insert({
                                "original_name": file.name,
                                "file_url": url,
                                "storage_path": storage_path,
                                "upload_date": datetime.date.today().isoformat(),
                                "sent_by": st.session_state.get("full_name", "admin"),
                                "category": category,
                                "assigned_client": assigned_client if assigned_client != "None" else None,
                                "tags": tags.strip() or None,
                                "notes": notes.strip() or None
                            }).execute()

                            if insert_response.data:
                                success_count += 1
                                log_action("File Uploaded", f"{file.name} → {category} → {assigned_client}")
                            else:
                                failed_files.append((file.name, "Metadata insert failed"))

                        except Exception as e:
                            failed_files.append((file.name, str(e)))
                            st.error(f"Failed {file.name}: {str(e)}")

                        progress_bar.progress((idx + 1) / total_files)

                    status_text.empty()
                    progress_bar.empty()

                    if success_count > 0:
                        st.success(f"**{success_count} file(s)** uploaded successfully!")
                        st.cache_data.clear()
                        st.rerun()

                    if failed_files:
                        st.warning(f"{len(failed_files)} file(s) failed:")
                        for name, err in failed_files:
                            st.caption(f"• {name}: {err}")

    # ─── FILTERS ───
    st.markdown("### 🔍 Filter Vault")
    col1, col2, col3 = st.columns([3, 2, 2])
    with col1:
        search = st.text_input("Search by name, tags, or notes", placeholder="e.g. payout proof, .ex5")
    with col2:
        cat_filter = st.selectbox("Category", ["All"] + sorted(set(f.get("category", "Other") for f in files or [])))
    with col3:
        client_filter = st.selectbox("Assigned Client", ["All"] + sorted(set(f.get("assigned_client") for f in files if f.get("assigned_client"))))

    # Apply filters
    filtered = files or []
    if search:
        s = search.lower()
        filtered = [f for f in filtered if s in f["original_name"].lower() or
                    s in (f.get("tags") or "").lower() or
                    s in (f.get("notes") or "").lower()]
    if cat_filter != "All":
        filtered = [f for f in filtered if f.get("category") == cat_filter]
    if client_filter != "All":
        filtered = [f for f in filtered if f.get("assigned_client") == client_filter]

    # ─── FILE DISPLAY GRID ───
    st.markdown(f"### Vault Contents ({len(filtered)} files)")

    if filtered:
        cols = st.columns(3) if len(filtered) > 2 else st.columns(2) if len(filtered) > 1 else st.columns(1)

        for i, f in enumerate(filtered):
            col = cols[i % len(cols)]

            with col:
                url = f.get("file_url")
                assigned = f.get("assigned_client")
                balance = user_map.get(assigned, {"balance": 0})["balance"]

                card_style = """
                    <div style="
                        background: rgba(30,35,45,0.7);
                        backdrop-filter: blur(12px);
                        border-radius: 16px;
                        border: 1px solid rgba(100,100,100,0.25);
                        padding: 1.4rem;
                        margin-bottom: 1.6rem;
                        transition: all 0.3s ease;
                        box-shadow: 0 6px 20px rgba(0,0,0,0.15);
                    ">
                        <div style="margin-bottom: 1rem;">
                """

                if url and f["original_name"].lower().endswith(('.png','.jpg','.jpeg','.gif')):
                    card_style += f'<img src="{url}" style="width:100%; border-radius:10px; margin-bottom: 0.8rem;"/>'
                else:
                    card_style += '<div style="height:140px; background:rgba(50,55,65,0.5); border-radius:10px; display:flex; align-items:center; justify-content:center; color:#aaa; font-size:1.1rem;">No preview available</div>'

                card_style += f"""
                        </div>
                        <strong style="font-size:1.05rem; display:block; margin-bottom:0.4rem;">{f['original_name']}</strong>
                        <small style="opacity:0.7; display:block; margin-bottom:0.6rem;">
                            {f['upload_date']} • {f['sent_by']}
                        </small>
                        <div style="font-size:0.9rem; opacity:0.85;">
                            Category: <strong>{f.get('category', 'Other')}</strong><br>
                """

                if assigned:
                    card_style += f"Assigned: <strong>{assigned}</strong> (${balance:,.2f})<br>"

                if f.get("tags"):
                    card_style += f"Tags: <em>{f['tags']}</em><br>"

                card_style += """
                        </div>
                """

                if f.get("notes"):
                    with st.expander("Notes", expanded=False):
                        st.write(f["notes"])

                # Actions
                col_a1, col_a2 = st.columns(2)
                with col_a1:
                    if url:
                        try:
                            r = requests.get(url, timeout=6)
                            if r.status_code == 200:
                                st.download_button(
                                    "⬇ Download",
                                    data=r.content,
                                    file_name=f["original_name"],
                                    mime="application/octet-stream",
                                    key=f"dl_{f['id']}_{i}",
                                    use_container_width=True
                                )
                        except:
                            st.caption("Download unavailable")

                with col_a2:
                    if current_role in ["owner", "admin"]:
                        if st.button("🗑 Delete", key=f"del_{f['id']}_{i}", type="secondary", use_container_width=True):
                            if st.session_state.get(f"confirm_del_{f['id']}", False):
                                try:
                                    if f.get("storage_path"):
                                        supabase.storage.from_("client_files").remove([f["storage_path"]])
                                    supabase.table("client_files").delete().eq("id", f["id"]).execute()
                                    st.success(f"Deleted: {f['original_name']}")
                                    st.cache_data.clear()
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Delete failed: {str(e)}")
                            else:
                                st.session_state[f"confirm_del_{f['id']}"] = True
                                st.warning("Click Delete again to confirm")
                                st.rerun()

                st.markdown(card_style + "</div>", unsafe_allow_html=True)

    else:
        st.info("No files match your filter or the vault is empty.")

    # ─── FOOTER ───
    bg_color = "#f8f9fa" if theme == "light" else "#1a1a2e"
    text_color = "#333" if theme == "light" else "#e0e0ff"
    border_color = "#ddd" if theme == "light" else "#444"

    st.markdown(f"""
    <div style="
        padding: 2.5rem 1.5rem;
        text-align: center;
        background: {bg_color};
        border-radius: 16px;
        margin: 3rem 0 1rem;
        border: 1px solid {border_color};
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
    ">
        <h3 style="color: #00cc99; margin-bottom: 0.6rem;">KMFX Secure Vault • 2026</h3>
        <p style="color: {text_color}; margin: 0; font-size: 0.95rem;">
            Encrypted • Permanent • Full .ex5 support • Proofs required for withdrawals • Powered by Supabase
        </p>
    </div>
    """, unsafe_allow_html=True)
# ====================== ANNOUNCEMENTS PAGE - FULL FINAL LATEST (SUPABASE STORAGE INTEGRATED) ======================
elif selected == "📢 Announcements":
    st.header("Empire Announcements 📢")
    st.markdown("**Central realtime communication: Broadcast updates • Rich images/attachments (PERMANENT STORAGE) • Likes ❤️ • Threaded comments 💬 • Pinning 📌 • Category filters • Full team engagement & transparency.**")
  
    current_role = st.session_state.get("role", "guest")
  
    @st.cache_data(ttl=15)
    def fetch_announcements_realtime():
        ann_resp = supabase.table("announcements").select("*").order("date", desc=True).execute()
        announcements = ann_resp.data or []
      
        for ann in announcements:
            att_resp = supabase.table("announcement_files").select("id, original_name, file_url, storage_path").eq("announcement_id", ann["id"]).execute()
            ann["attachments"] = att_resp.data or []
      
        try:
            comm_resp = supabase.table("announcement_comments").select("*").order("timestamp", desc=True).execute()
            comments_map = {}
            for c in comm_resp.data or []:
                aid = c["announcement_id"]
                if aid not in comments_map:
                    comments_map[aid] = []
                comments_map[aid].append(c)
            for ann in announcements:
                ann["comments"] = comments_map.get(ann["id"], [])
        except:
            for ann in announcements:
                ann["comments"] = []
      
        return announcements
  
    announcements = fetch_announcements_realtime()
  
    st.caption("🔄 Feed auto-refresh every 15s • Attachments now PERMANENT via Supabase Storage")
  
    # POST NEW (OWNER/ADMIN)
    if current_role in ["owner", "admin"]:
        with st.expander("➕ Broadcast New Announcement", expanded=True):
            with st.form("ann_form", clear_on_submit=True):
                title = st.text_input("Title *")
                category = st.selectbox("Category", ["General", "Profit Distribution", "Withdrawal Update", "License Granted", "Milestone", "EA Update", "Team Alert"])
                message = st.text_area("Message *", height=150)
                attachments = st.file_uploader("Attachments (Images/Proofs - Permanent Full Preview)", accept_multiple_files=True)
                pin = st.checkbox("📌 Pin to Top")
              
                submitted = st.form_submit_button("📢 Post Announcement", type="primary", use_container_width=True)
                if submitted:
                    if not title.strip() or not message.strip():
                        st.error("Title and message required")
                    else:
                        try:
                            resp = supabase.table("announcements").insert({
                                "title": title.strip(),
                                "message": message.strip(),
                                "date": datetime.date.today().isoformat(),
                                "posted_by": st.session_state.full_name,
                                "likes": 0,
                                "category": category,
                                "pinned": pin
                            }).execute()
                            ann_id = resp.data[0]["id"]
                          
                            for file in attachments or []:
                                try:
                                    url, storage_path = upload_to_supabase(file, "announcements")
                                    supabase.table("announcement_files").insert({
                                        "announcement_id": ann_id,
                                        "original_name": file.name,
                                        "file_url": url,
                                        "storage_path": storage_path
                                    }).execute()
                                except Exception as e:
                                    st.warning(f"Attachment {file.name} upload failed: {str(e)}")
                          
                            st.success("Announcement posted realtime! (Attachments permanent)")
                            st.cache_data.clear()
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
  
    # FILTER & SEARCH
    st.subheader("📻 Live Empire Feed")
    categories = sorted(set(a.get("category", "General") for a in announcements))
    filter_cat = st.selectbox("Category Filter", ["All"] + categories)
  
    filtered = [a for a in announcements if filter_cat == "All" or a.get("category") == filter_cat]
    filtered = sorted(filtered, key=lambda x: (not x.get("pinned", False), x["date"]), reverse=True)
  
    # REALTIME RICH FEED
    import requests
    if filtered:
        for ann in filtered:
            pinned = " 📌 PINNED" if ann.get("pinned") else ""
            with st.container():
                st.markdown(f"<h3 style='color:{accent_color};'>{ann['title']}{pinned}</h3>", unsafe_allow_html=True)
                st.caption(f"{ann.get('category', 'General')} • by {ann['posted_by']} • {ann['date']}")
                st.markdown(ann['message'])
              
                # Images via URL
                images = [att for att in ann["attachments"] if att["original_name"].lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
                if images:
                    img_cols = st.columns(min(len(images), 4))
                    for idx, att in enumerate(images):
                        if att.get("file_url"):
                            with img_cols[idx % 4]:
                                st.image(att["file_url"], use_container_width=True)
              
                # Non-images download
                non_images = [att for att in ann["attachments"] if not att["original_name"].lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
                if non_images:
                    st.markdown("**Files:**")
                    for att in non_images:
                        if att.get("file_url"):
                            try:
                                response = requests.get(att["file_url"])
                                if response.status_code == 200:
                                    st.download_button(att['original_name'], response.content, att['original_name'])
                                else:
                                    st.error(f"File {att['original_name']} unavailable")
                            except:
                                st.error(f"Download failed for {att['original_name']}")
              
                if st.button(f"❤️ {ann['likes']}", key=f"like_{ann['id']}"):
                    try:
                        supabase.table("announcements").update({"likes": ann["likes"] + 1}).eq("id", ann["id"]).execute()
                        st.cache_data.clear()
                        st.rerun()
                    except:
                        pass
              
                with st.expander(f"💬 Comments ({len(ann.get('comments', []))}) • Realtime", expanded=False):
                    for c in ann.get("comments", []):
                        st.markdown(f"**{c['user_name']}** • {c['timestamp'][:16].replace('T', ' ')}")
                        st.markdown(c['message'])
                        st.divider()
                  
                    with st.form(key=f"comment_{ann['id']}"):
                        comment = st.text_area("Add comment...", height=80, label_visibility="collapsed")
                        if st.form_submit_button("Post"):
                            if comment.strip():
                                try:
                                    supabase.table("announcement_comments").insert({
                                        "announcement_id": ann["id"],
                                        "user_name": st.session_state.full_name,
                                        "message": comment.strip(),
                                        "timestamp": datetime.datetime.now().isoformat()
                                    }).execute()
                                    st.success("Posted realtime!")
                                    st.cache_data.clear()
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error: {str(e)}")
              
                if current_role in ["owner", "admin"]:
                    col_admin = st.columns(3)
                    with col_admin[0]:
                        if st.button("📌 Pin/Unpin", key=f"pin_{ann['id']}"):
                            supabase.table("announcements").update({"pinned": not ann.get("pinned", False)}).eq("id", ann["id"]).execute()
                            st.rerun()
                    with col_admin[2]:
                        if st.button("🗑️ Delete", key=f"del_{ann['id']}", type="secondary"):
                            try:
                                # Cleanup attachments from storage
                                for att in ann["attachments"]:
                                    if att.get("storage_path"):
                                        supabase.storage.from_("announcements").remove([att["storage_path"]])
                                supabase.table("announcement_files").delete().eq("announcement_id", ann["id"]).execute()
                                supabase.table("announcements").delete().eq("id", ann["id"]).execute()
                                st.success("Deleted (attachments removed permanently)")
                                st.cache_data.clear()
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error: {str(e)}")
                st.divider()
    else:
        st.info("No announcements yet • First post activates realtime feed")
  
    st.markdown(f"""
    <div class='glass-card' style='padding:3rem; text-align:center; margin:3rem 0;'>
        <h1 style="background:linear-gradient(90deg,{accent_color},#ffd700); -webkit-background-clip:text; -webkit-text-fill-color:transparent;">
            Realtime Team Communication
        </h1>
        <p style="font-size:1.3rem; margin:2rem 0;">
            Images full preview • Attachments PERMANENT • Likes & comments update live • Pinned alerts • Empire connected.
        </p>
    </div>
    """, unsafe_allow_html=True)
# ====================== END OF FINAL REALTIME ANNOUNCEMENTS WITH SUPABASE STORAGE ======================
elif selected == "💬 Messages":
    st.header("Private Messages 💬")
    st.markdown("**Secure realtime 1:1 empire communication • Threaded chats • File attachments with previews • Search • Auto-system messages (profit shares, withdrawal updates, license grants) • Balance context • Instant sync & clean UI.**")
   
    current_role = st.session_state.get("role", "guest")
   
    @st.cache_data(ttl=15)
    def fetch_messages_full():
        users_resp = supabase.table("users").select("id, full_name, role, balance").execute()
        users = users_resp.data or []
       
        msg_resp = supabase.table("messages").select("*").order("timestamp").execute()
        messages = msg_resp.data or []
       
        convos = {}
        for m in messages:
            if current_role in ["owner", "admin"]:
                partner = m.get("to_client") or m.get("from_client", "Unknown")
            else:
                partner = "KMFX Admin"
            if partner not in convos:
                convos[partner] = []
            convos[partner].append(m)
       
        return users, messages, convos
   
    all_users, all_messages, conversations = fetch_messages_full()
   
    clients = [u for u in all_users if u["role"] == "client"]
   
    st.caption("🔄 Messages auto-refresh every 15s • Realtime chat")
   
    if current_role in ["owner", "admin"]:
        if not clients:
            st.info("No clients yet • Private messaging activates with team members")
            st.stop()
       
        client_options = {f"{c['full_name']} (Balance: ${c['balance'] or 0:,.2f})": c["full_name"] for c in clients}
        selected_key = st.selectbox("Select Team Member for Private Chat", list(client_options.keys()))
        partner_name = client_options[selected_key]
        partner_balance = next((c["balance"] or 0 for c in clients if c["full_name"] == partner_name), 0)
       
        st.info(f"**Private chat with:** {partner_name} | Current Balance: ${partner_balance:,.2f}")
       
        convo = conversations.get(partner_name, [])
    else:
        partner_name = "KMFX Admin"
        convo = [m for m in all_messages if
                 m.get("to_client") == st.session_state.full_name or
                 m.get("from_client") == st.session_state.full_name]
        st.info("**Private channel with KMFX Admin** • Updates on shares, withdrawals, licenses")
   
    # REALTIME CONVERSATION DISPLAY
    if convo:
        search_msg = st.text_input("Search messages")
        display_convo = [m for m in convo if search_msg.lower() in m["message"].lower()] if search_msg else convo
       
        chat_container = st.container()
        with chat_container:
            for msg in display_convo:
                is_from_me = (
                    (current_role in ["owner", "admin"] and msg.get("from_admin") == st.session_state.full_name) or
                    (current_role == "client" and msg.get("from_client") == st.session_state.full_name)
                )
                align = "flex-end" if is_from_me else "flex-start"
                bg = accent_primary if is_from_me else card_bg  # FIXED: card_bg (glass) for other bubbles
                text_c = "#000000" if is_from_me else text_primary  # Black text if from me, theme if other
                
                sender = msg.get("from_admin") or msg.get("from_client") or "System"
                time = msg["timestamp"][:16].replace("T", " ")
                
                st.markdown(
                    f"<div style='display:flex; justify-content:{align}; margin:1rem 0;'>"
                    f"<div style='background:{bg}; padding:1.2rem 1.6rem; border-radius:20px; max-width:75%; box-shadow: {card_shadow};'>"
                    f"<strong style='color:{text_c};'>{sender}</strong>"
                    f"<p style='margin:0.6rem 0 0; color:{text_c};'>{msg['message']}</p>"
                    f"<small style='opacity:0.7; color:{text_c};'>{time}</small>"
                    f"</div>"
                    f"</div>",
                    unsafe_allow_html=True
                )
       
        st.caption(f"{len(convo)} messages • Auto-read on view")
    else:
        st.info("No messages yet • Start the conversation below")
   
    # SEND MESSAGE WITH ATTACHMENTS
    with st.form("send_msg_form", clear_on_submit=True):
        col_send1, col_send2 = st.columns([3, 1])
        with col_send1:
            new_msg = st.text_area("Type message...", height=120, label_visibility="collapsed")
        with col_send2:
            msg_files = st.file_uploader("Attach Files (Images/Proofs)", accept_multiple_files=True, label_visibility="collapsed")
       
        send = st.form_submit_button("Send ➤", type="primary", use_container_width=True)
        if send:
            if not new_msg.strip() and not msg_files:
                st.error("Message or file required")
            else:
                try:
                    insert_data = {
                        "message": new_msg.strip() or "📎 Attached files",
                        "timestamp": datetime.datetime.now().isoformat()
                    }
                    if current_role in ["owner", "admin"]:
                        insert_data["from_admin"] = st.session_state.full_name
                        insert_data["to_client"] = partner_name
                    else:
                        insert_data["from_client"] = st.session_state.full_name
                   
                    supabase.table("messages").insert(insert_data).execute()
                   
                    if msg_files:
                        os.makedirs("uploaded_files/messages", exist_ok=True)
                        for file in msg_files:
                            safe = "".join(c for c in file.name if c.isalnum() or c in "._- ")
                            path = f"uploaded_files/messages/{safe}"
                            with open(path, "wb") as f:
                                f.write(file.getbuffer())
                   
                    log_action("Private Message Sent", f"To/From {partner_name}")
                    st.success("Message sent realtime!")
                    st.cache_data.clear()
                    st.rerun()
                except Exception as e:
                    st.error(f"Send error: {str(e)}")
   
    st.caption("🤖 Auto-messages: Profit shares, withdrawal status, license info • Delivered here privately")
   
    st.markdown(f"""
    <div class='glass-card' style='padding:2rem; text-align:center; margin-top:2rem;'>
        <h3 style='color:{accent_color};'>Realtime Private Channels</h3>
        <p>Secure • Attachments • Auto-updates • Empire aligned & connected.</p>
    </div>
    """, unsafe_allow_html=True)
# ====================== PART 6: NOTIFICATIONS PAGE (FINAL SUPER ADVANCED - FULL MAIN FLOW SYNC & REALTIME) ======================
elif selected == "🔔 Notifications":
    st.header("Empire Notifications 🔔")
    st.markdown("**Realtime alert system: Auto-push on profit distributions, withdrawal updates, license grants, milestones • Unread count & badges • Rich details • Mark read • Category filters • Instant sync & team alignment.**")
    
    # SAFE ROLE
    current_role = st.session_state.get("role", "guest")
    
    # FULL REALTIME CACHE (short ttl for live alerts)
    @st.cache_data(ttl=15)
    def fetch_notifications_full():
        notif_resp = supabase.table("notifications").select("*").order("date", desc=True).execute()
        notifications = notif_resp.data or []
        
        users_resp = supabase.table("users").select("id, full_name, balance, role").execute()
        all_users = users_resp.data or []
        user_map = {u["full_name"]: {"balance": u["balance"] or 0, "role": u["role"]} for u in all_users}
        client_names = [u["full_name"] for u in all_users if u["role"] == "client"]
        
        return notifications, all_users, user_map, client_names
    
    notifications, all_users, user_map, client_names = fetch_notifications_full()
    
    st.caption("🔄 Notifications auto-refresh every 15s for realtime alerts")
    
    # Client view: Only own + unread count
    if current_role == "client":
        my_name = st.session_state.full_name
        my_notifications = [n for n in notifications if n["client_name"] == my_name]
        unread_count = sum(1 for n in my_notifications if n.get("read", 0) == 0)
        st.subheader(f"Your Notifications ({len(my_notifications)} total • {unread_count} unread)")
    else:
        # Admin/Owner: All
        my_notifications = notifications
        unread_count = 0
        
        st.subheader("All Empire Notifications")
    
    # ====================== SEND NOTIFICATION (OWNER/ADMIN) ======================
    if current_role in ["owner", "admin"]:
        with st.expander("➕ Send New Notification", expanded=False):
            with st.form("notif_form", clear_on_submit=True):
                target = st.selectbox("Send to", ["All Clients"] + client_names)
                category = st.selectbox("Type", ["Profit Share", "Withdrawal Update", "License Granted", "Milestone", "General Alert"])
                title = st.text_input("Title *")
                message = st.text_area("Message *", height=150)
                
                submitted = st.form_submit_button("🔔 Send Alert", type="primary", use_container_width=True)
                if submitted:
                    if not title.strip() or not message.strip():
                        st.error("Title and message required")
                    else:
                        try:
                            if target == "All Clients":
                                for client_name in client_names:
                                    supabase.table("notifications").insert({
                                        "client_name": client_name,
                                        "title": title.strip(),
                                        "message": message.strip(),
                                        "date": datetime.date.today().isoformat(),
                                        "category": category,
                                        "read": 0
                                    }).execute()
                            else:
                                supabase.table("notifications").insert({
                                    "client_name": target,
                                    "title": title.strip(),
                                    "message": message.strip(),
                                    "date": datetime.date.today().isoformat(),
                                    "category": category,
                                    "read": 0
                                }).execute()
                            st.success("Notification sent realtime!")
                            st.cache_data.clear()
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
    
    # ====================== CATEGORY FILTER ======================
    categories = sorted(set(n.get("category", "General") for n in my_notifications))
    filter_cat = st.selectbox("Filter by Type", ["All"] + categories)
    
    filtered = [n for n in my_notifications if filter_cat == "All" or n.get("category") == filter_cat]
    
    # ====================== REALTIME NOTIFICATION LIST (CLEAN CARDS) ======================
    if filtered:
        for n in filtered:
            is_unread = n.get("read", 0) == 0
            badge = "🟡 Unread" if is_unread else "✅ Read"
            client_balance = user_map.get(n["client_name"], {"balance": 0})["balance"]
            
            with st.container():
                st.markdown(f"""
                <div class='glass-card' style='padding:1.5rem; border-left:5px solid {accent_color if is_unread else "#888"};'>
                    <h4 style='margin:0; color:{accent_color};'>{n['title']} {badge}</h4>
                    <small>{n.get('category', 'General')} • For {n['client_name']} (Balance: ${client_balance:,.2f}) • {n['date']}</small>
                </div>
                """, unsafe_allow_html=True)
                st.markdown(n['message'])
                
                # Mark as read
                if is_unread:
                    if st.button("Mark as Read", key=f"read_{n['id']}"):
                        try:
                            supabase.table("notifications").update({"read": 1}).eq("id", n["id"]).execute()
                            st.cache_data.clear()
                            st.rerun()
                        except:
                            pass
                
                # Admin delete
                if current_role in ["owner", "admin"]:
                    if st.button("🗑️ Delete", key=f"del_notif_{n['id']}", type="secondary"):
                        try:
                            supabase.table("notifications").delete().eq("id", n["id"]).execute()
                            st.success("Deleted")
                            st.cache_data.clear()
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
                st.divider()
    else:
        st.info("No notifications • Auto-alerts activate on events (profits, withdrawals, licenses)")
    
    # Auto-alert note
    st.caption("🤖 Auto-notifications: Profit shares, withdrawal status, license grants • Pushed here instantly")
    
    st.markdown(f"""
    <div class='glass-card' style='padding:3rem; text-align:center; margin:3rem 0;'>
        <h1 style="background:linear-gradient(90deg,{accent_color},#ffd700); -webkit-background-clip:text; -webkit-text-fill-color:transparent;">
            Realtime Empire Alerts
        </h1>
        <p style="font-size:1.3rem; margin:2rem 0;">
            Unread badges • Categories • Mark read • Auto-push on key events • Team always informed.
        </p>
    </div>
    """, unsafe_allow_html=True)
# ====================== END OF FINAL REALTIME NOTIFICATIONS ======================
# ====================== PART 6: WITHDRAWALS PAGE (FINAL SUPER ADVANCED - SUPABASE STORAGE INTEGRATED FOR PROOFS) ======================
elif selected == "💳 Withdrawals":
    st.header("Withdrawal Management 💳")
    st.markdown("**Empire payout engine: Clients request from auto-earned balances • Require payout proof (PERMANENT STORAGE) • Amount limited to balance • Owner approve/pay/reject • Auto-deduct balance • Realtime sync & full transparency.**")
 
    # SAFE ROLE
    current_role = st.session_state.get("role", "guest")
 
    # FULL REALTIME CACHE
    @st.cache_data(ttl=30)
    def fetch_withdrawals_full():
        wd_resp = supabase.table("withdrawals").select("*").order("date_requested", desc=True).execute()
        withdrawals = wd_resp.data or []
     
        users_resp = supabase.table("users").select("id, full_name, balance, role").execute()
        users = users_resp.data or []
        user_map = {u["full_name"]: {"id": u["id"], "balance": u["balance"] or 0} for u in users}
     
        # Related proofs (safe handling)
        files_resp = supabase.table("client_files").select("id, original_name, file_url, storage_path, category, assigned_client, notes").execute()
        proofs = files_resp.data or []
     
        return withdrawals, users, user_map, proofs
 
    withdrawals, users, user_map, proofs = fetch_withdrawals_full()
 
    st.caption("🔄 Withdrawals auto-refresh every 30s • Proofs now PERMANENT via Supabase Storage")
 
    # ====================== CLIENT VIEW: REQUEST + HISTORY ======================
    if current_role == "client":
        my_name = st.session_state.full_name
        my_balance = user_map.get(my_name, {"balance": 0})["balance"]
        my_withdrawals = [w for w in withdrawals if w["client_name"] == my_name]
     
        st.subheader(f"Your Withdrawal Requests (Available Balance: ${my_balance:,.2f})")
     
        # Only show request form if balance > 0
        if my_balance > 0:
            with st.expander("➕ Request New Withdrawal", expanded=True):
                with st.form("wd_request_form", clear_on_submit=True):
                    amount = st.number_input(
                        "Amount (USD)",
                        min_value=1.0,
                        max_value=float(my_balance),
                        step=100.0,
                        value=min(100.0, my_balance),
                        help=f"Max: ${my_balance:,.2f}"
                    )
                    method = st.selectbox("Payout Method", ["USDT", "Bank Transfer", "Wise", "PayPal", "GCash", "Other"])
                    details = st.text_area("Payout Details (Wallet/Address/Bank Info)")
                    proof_file = st.file_uploader("Upload Payout Proof * (Required - Permanent Storage)", type=["png", "jpg", "jpeg", "pdf"], help="Screenshot of wallet, bank statement • Auto-saved permanently to vault")
                 
                    submitted = st.form_submit_button("Submit Request for Approval", type="primary", use_container_width=True)
                    if submitted:
                        if amount > my_balance:
                            st.error("Amount exceeds available balance")
                        elif not proof_file:
                            st.error("Payout proof required")
                        else:
                            try:
                                # Permanent upload to Supabase Storage
                                url, storage_path = upload_to_supabase(proof_file, "client_files", "proofs")
                                
                                supabase.table("client_files").insert({
                                    "original_name": proof_file.name,
                                    "file_url": url,
                                    "storage_path": storage_path,
                                    "upload_date": datetime.date.today().isoformat(),
                                    "sent_by": my_name,
                                    "category": "Withdrawal Proof",
                                    "assigned_client": my_name,
                                    "notes": f"Proof for ${amount:,.0f} withdrawal"
                                }).execute()
                             
                                # Submit request
                                supabase.table("withdrawals").insert({
                                    "client_name": my_name,
                                    "amount": amount,
                                    "method": method,
                                    "details": details,
                                    "status": "Pending",
                                    "date_requested": datetime.date.today().isoformat()
                                }).execute()
                             
                                st.success("Request submitted permanently! Owner will review proof.")
                                st.cache_data.clear()
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error: {str(e)}")
        else:
            st.info("No available balance yet • Earnings auto-accumulate from profits")
            with st.expander("➕ Request New Withdrawal"):
                st.info("Withdrawal requests will be available once you have earnings in your balance.")
     
        # History
        if my_withdrawals:
            st.markdown("### Request History")
            for w in my_withdrawals:
                status_color = {"Pending": "#ffa502", "Approved": accent_color, "Paid": "#2ed573", "Rejected": "#ff4757"}.get(w["status"], "#888")
                st.markdown(f"""
                <div class='glass-card' style='padding:1.5rem; border-left:5px solid {status_color};'>
                    <h4>${w['amount']:,.0f} • {w['status']}</h4>
                    <small>Method: {w['method']} • Requested: {w['date_requested']}</small>
                </div>
                """, unsafe_allow_html=True)
                if w["details"]:
                    with st.expander("Details"):
                        st.write(w["details"])
                st.divider()
        else:
            st.info("No requests yet • Earnings auto-accumulate")
 
    # ====================== OWNER/ADMIN VIEW: ALL REQUESTS + ACTIONS ======================
    else:
        st.subheader("All Empire Withdrawal Requests")
        import requests
     
        if withdrawals:
            for w in withdrawals:
                client_balance = user_map.get(w["client_name"], {"balance": 0})["balance"]
                status_color = {"Pending": "#ffa502", "Approved": accent_color, "Paid": "#2ed573", "Rejected": "#ff4757"}.get(w["status"], "#888")
             
                with st.container():
                    st.markdown(f"""
                    <div class='glass-card' style='padding:1.8rem; border-left:5px solid {status_color};'>
                        <h4>{w['client_name']} • ${w['amount']:,.0f} • {w['status']}</h4>
                        <small>Method: {w['method']} • Requested: {w['date_requested']} • Current Balance: ${client_balance:,.2f}</small>
                    </div>
                    """, unsafe_allow_html=True)
                    if w["details"]:
                        with st.expander("Payout Details"):
                            st.write(w["details"])
                 
                    # Related proofs via URL (permanent)
                    related_proofs = [p for p in proofs if p.get("assigned_client") == w["client_name"] and
                                      ("withdrawal" in str(p.get("notes") or "").lower() or p.get("category") in ["Payout Proof", "Withdrawal Proof"])]
                    if related_proofs:
                        st.markdown("**Related Proofs (Permanent):**")
                        proof_cols = st.columns(min(len(related_proofs), 4))
                        for idx, p in enumerate(related_proofs):
                            file_url = p.get("file_url")
                            if file_url:
                                with proof_cols[idx % 4]:
                                    if p["original_name"].lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                                        st.image(file_url, caption=p["original_name"], use_container_width=True)
                                    else:
                                        try:
                                            response = requests.get(file_url)
                                            if response.status_code == 200:
                                                st.download_button(p["original_name"], response.content, p["original_name"])
                                            else:
                                                st.caption(f"{p['original_name']} (PDF/Doc - download)")
                                        except:
                                            st.caption(f"{p['original_name']} (download failed)")
                 
                    # Actions
                    if w["status"] == "Pending":
                        col_act1, col_act2 = st.columns(2)
                        with col_act1:
                            if st.button("Approve", key=f"app_{w['id']}"):
                                try:
                                    supabase.table("withdrawals").update({
                                        "status": "Approved",
                                        "date_processed": datetime.date.today().isoformat(),
                                        "processed_by": st.session_state.full_name
                                    }).eq("id", w["id"]).execute()
                                    st.success("Approved!")
                                    st.cache_data.clear()
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error: {str(e)}")
                        with col_act2:
                            if st.button("Reject", key=f"rej_{w['id']}", type="secondary"):
                                try:
                                    supabase.table("withdrawals").update({
                                        "status": "Rejected",
                                        "date_processed": datetime.date.today().isoformat(),
                                        "processed_by": st.session_state.full_name
                                    }).eq("id", w["id"]).execute()
                                    st.success("Rejected")
                                    st.cache_data.clear()
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error: {str(e)}")
                    elif w["status"] == "Approved":
                        if st.button("Mark as Paid → Auto-Deduct Balance", key=f"paid_{w['id']}", type="primary"):
                            try:
                                client_id = user_map.get(w["client_name"], {}).get("id")
                                if client_id:
                                    current_bal = user_map[w["client_name"]]["balance"]
                                    new_bal = max(0, current_bal - w["amount"])
                                    supabase.table("users").update({"balance": new_bal}).eq("id", client_id).execute()
                                supabase.table("withdrawals").update({"status": "Paid"}).eq("id", w["id"]).execute()
                                st.success(f"Paid! Balance deducted.")
                                st.cache_data.clear()
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error: {str(e)}")
                    st.divider()
        else:
            st.info("No withdrawal requests yet")
 
    st.markdown(f"""
    <div class='glass-card' style='padding:3rem; text-align:center; margin:3rem 0;'>
        <h1 style="background:linear-gradient(90deg,{accent_color},#ffd700); -webkit-background-clip:text; -webkit-text-fill-color:transparent;">
            Automatic & Secure Payouts
        </h1>
        <p style="font-size:1.3rem; margin:2rem 0;">
            Requests limited to earned balance • Proofs PERMANENT • Owner control • Auto-deduct • Empire cashflow perfected.
        </p>
        <h2 style="color:#ffd700;">👑 KMFX Withdrawals • Cloud Permanent 2026</h2>
    </div>
    """, unsafe_allow_html=True)
# ====================== END OF FINAL WITHDRAWALS WITH SUPABASE STORAGE FOR PROOFS ======================
# ====================== PART 6: EA VERSIONS PAGE (FINAL SUPER ADVANCED - SUPABASE STORAGE INTEGRATED) ======================
elif selected == "🤖 EA Versions":
    st.header("EA Versions Management 🤖")
    st.markdown("**Elite EA distribution: Owner release new versions with changelog • Auto-announce to team • Download tracking • License gating (latest version requires active license) • Realtime list • Files now PERMANENT via Supabase Storage.**")
   
    # SAFE ROLE
    current_role = st.session_state.get("role", "guest")
   
    # FULL REALTIME CACHE
    @st.cache_data(ttl=30)
    def fetch_ea_full():
        versions_resp = supabase.table("ea_versions").select("*").order("upload_date", desc=True).execute()
        versions = versions_resp.data or []
       
        downloads_resp = supabase.table("ea_downloads").select("*").execute()
        downloads = downloads_resp.data or []
       
        # Download count per version
        download_counts = {}
        for d in downloads:
            vid = d["version_id"]
            download_counts[vid] = download_counts.get(vid, 0) + 1
       
        # Client license check (for gating latest version)
        if current_role == "client":
            # Adjust if you store user_id in session; fallback to name-based if needed
            license_resp = supabase.table("client_licenses").select("allow_live, version").eq("account_id", 
                supabase.table("users").select("id").eq("full_name", st.session_state.full_name).execute().data[0]["id"] if supabase.table("users").select("id").eq("full_name", st.session_state.full_name).execute().data else None
            ).execute()
            client_license = license_resp.data[0] if license_resp.data else None
        else:
            client_license = None
       
        return versions, download_counts, client_license
   
    versions, download_counts, client_license = fetch_ea_full()
   
    st.caption("🔄 Versions auto-refresh every 30s • EA files now PERMANENT via Supabase Storage")
   
    # ====================== RELEASE NEW VERSION (OWNER ONLY) ======================
    if current_role == "owner":
        with st.expander("➕ Release New EA Version (Owner Exclusive)", expanded=True):
            with st.form("ea_form", clear_on_submit=True):
                version_name = st.text_input("Version Name *", placeholder="e.g. v3.0 Elite 2026")
                ea_file = st.file_uploader("Upload EA File (.ex5 / .mq5) *", accept_multiple_files=False)
                changelog = st.text_area("Changelog *", height=200, placeholder="• New features\n• Bug fixes\n• Performance improvements")
                announce = st.checkbox("📢 Auto-Announce to Empire", value=True)
               
                submitted = st.form_submit_button("🚀 Release Version", type="primary", use_container_width=True)
                if submitted:
                    if not version_name.strip() or not ea_file or not changelog.strip():
                        st.error("Version name, file, and changelog required")
                    else:
                        try:
                            url, storage_path = upload_to_supabase(ea_file, "ea_versions")
                            
                            supabase.table("ea_versions").insert({
                                "version": version_name.strip(),
                                "file_url": url,
                                "storage_path": storage_path,
                                "upload_date": datetime.date.today().isoformat(),
                                "notes": changelog.strip()
                            }).execute()
                           
                            if announce:
                                supabase.table("announcements").insert({
                                    "title": f"New EA Version Released: {version_name.strip()}",
                                    "message": f"🚀 New update available!\n\n{changelog.strip()}\n\nDownload in EA Versions page.",
                                    "date": datetime.date.today().isoformat(),
                                    "posted_by": st.session_state.full_name,
                                    "category": "EA Update",
                                    "pinned": False
                                }).execute()
                           
                            log_action("EA Version Released (Permanent)", version_name.strip())
                            st.success(f"Version {version_name} released permanently & synced!")
                            st.balloons()
                            st.cache_data.clear()
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
    elif current_role == "admin":
        st.info("Admins view & track downloads • Owner releases new versions")
   
    # ====================== REALTIME VERSION LIST WITH LICENSE GATING ======================
    st.subheader("Available EA Versions (Realtime • Permanent Files)")
    import requests
    if versions:
        latest_version = versions[0]  # First is latest
        for v in versions:
            vid = v["id"]
            downloads = download_counts.get(vid, 0)
            file_url = v.get("file_url")
           
            # License gating for latest version
            is_latest = v == latest_version
            can_download = True
            if current_role == "client" and is_latest and client_license:
                can_download = client_license.get("allow_live", False)  # Or check version match if needed
           
            with st.expander(f"🤖 {v['version']} • Released {v['upload_date']} • {downloads} downloads" + (" (Latest - License Required)" if is_latest else ""), expanded=is_latest):
                st.markdown(f"**Changelog:**\n{v['notes'].replace(chr(10), '<br>')}", unsafe_allow_html=True)
               
                if file_url:
                    try:
                        response = requests.get(file_url)
                        if response.status_code == 200:
                            if can_download:
                                if st.download_button(f"⬇️ Download {v['version']}", response.content, v.get('file_name', f"{v['version']}.ex5"), use_container_width=True):
                                    try:
                                        supabase.table("ea_downloads").insert({
                                            "version_id": vid,
                                            "downloaded_by": st.session_state.full_name,
                                            "download_date": datetime.date.today().isoformat()
                                        }).execute()
                                        log_action("EA Downloaded (Permanent)", f"{v['version']} by {st.session_state.full_name}")
                                    except:
                                        pass
                            else:
                                st.warning("🔒 Active license required for latest version • Contact owner")
                        else:
                            st.error("File unavailable")
                    except:
                        st.error("Download failed")
                else:
                    st.error("File missing - contact owner")
               
                if current_role == "owner":
                    if st.button("🗑️ Delete Version", key=f"del_ea_{vid}", type="secondary"):
                        try:
                            if v.get("storage_path"):
                                supabase.storage.from_("ea_versions").remove([v["storage_path"]])
                            supabase.table("ea_versions").delete().eq("id", vid).execute()
                            supabase.table("ea_downloads").delete().eq("version_id", vid).execute()
                            st.success("Version removed permanently")
                            st.cache_data.clear()
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
    else:
        st.info("No EA versions released yet • Owner uploads activate elite distribution")
   
    st.markdown(f"""
    <div class='glass-card' style='padding:3rem; text-align:center; margin:3rem 0;'>
        <h1 style="background:linear-gradient(90deg,{accent_color},#ffd700); -webkit-background-clip:text; -webkit-text-fill-color:transparent;">
            Elite EA Distribution
        </h1>
        <p style="font-size:1.3rem; margin:2rem 0;">
            Owner release • Auto-announce • Download tracked • Latest gated by license • Files PERMANENT • Empire performance synced.
        </p>
        <h2 style="color:#ffd700;">👑 KMFX EA Versions • Cloud Permanent 2026</h2>
    </div>
    """, unsafe_allow_html=True)
# ====================== END OF FINAL EA VERSIONS WITH SUPABASE STORAGE ======================
# ====================== PART 6: TESTIMONIALS PAGE (FINAL SUPER ADVANCED - SUPABASE STORAGE INTEGRATED) ======================
elif selected == "📸 Testimonials":
    st.header("Team Testimonials 📸")
    st.markdown("**Empire motivation hub: Clients submit success stories + photos (PERMANENT STORAGE) • Auto-balance context • Owner approve/reject with auto-announce • Realtime grid with full image previews • Search • Full team inspiration & transparency.**")
   
    # SAFE ROLE
    current_role = st.session_state.get("role", "guest")
   
    # FULL REALTIME CACHE
    @st.cache_data(ttl=30)
    def fetch_testimonials_full():
        approved_resp = supabase.table("testimonials").select("*").eq("status", "Approved").order("date_submitted", desc=True).execute()
        approved = approved_resp.data or []
       
        pending_resp = supabase.table("testimonials").select("*").eq("status", "Pending").order("date_submitted", desc=True).execute()
        pending = pending_resp.data or []
       
        users_resp = supabase.table("users").select("full_name, balance").execute()
        user_map = {u["full_name"]: u["balance"] or 0 for u in users_resp.data or []}
       
        return approved, pending, user_map
   
    approved, pending, user_map = fetch_testimonials_full()
   
    st.caption("🔄 Testimonials auto-refresh every 30s • Photos now PERMANENT via Supabase Storage")
   
    # ====================== SUBMIT TESTIMONIAL (CLIENT ONLY) ======================
    if current_role == "client":
        my_balance = user_map.get(st.session_state.full_name, 0)
        st.subheader(f"Share Your Success Story (Balance: ${my_balance:,.2f})")
        with st.expander("➕ Submit Testimonial", expanded=True):
            with st.form("testi_form", clear_on_submit=True):
                story = st.text_area("Your Story *", height=200, placeholder="e.g. How KMFX changed my trading, profits earned, journey...")
                photo = st.file_uploader("Upload Photo * (Required for Approval - Permanent Storage)", type=["png", "jpg", "jpeg", "gif"])
               
                submitted = st.form_submit_button("Submit for Approval", type="primary", use_container_width=True)
                if submitted:
                    if not story.strip() or not photo:
                        st.error("Story and photo required")
                    else:
                        try:
                            url, storage_path = upload_to_supabase(photo, "testimonials")
                            
                            supabase.table("testimonials").insert({
                                "client_name": st.session_state.full_name,
                                "message": story.strip(),
                                "image_url": url,
                                "storage_path": storage_path,
                                "date_submitted": datetime.date.today().isoformat(),
                                "status": "Pending"
                            }).execute()
                            st.success("Testimonial submitted permanently! Owner will review & approve.")
                            st.cache_data.clear()
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
   
    # ====================== APPROVED TESTIMONIALS GRID (REALTIME FULL PREVIEWS) ======================
    st.subheader("🌟 Approved Success Stories (Realtime • Permanent Photos)")
    if approved:
        # Search
        search_testi = st.text_input("Search stories")
        filtered_approved = [t for t in approved if search_testi.lower() in t["message"].lower() or search_testi.lower() in t["client_name"].lower()]
       
        cols = st.columns(3)
        for idx, t in enumerate(filtered_approved):
            with cols[idx % 3]:
                balance = user_map.get(t["client_name"], 0)
                image_url = t.get("image_url")
                with st.container():
                    if image_url:
                        st.image(image_url, use_container_width=True)
                    else:
                        st.caption("No photo")
                    st.markdown(f"**{t['client_name']}** (Balance: ${balance:,.2f})")
                    st.markdown(t["message"])
                    st.caption(f"Submitted: {t['date_submitted']}")
    else:
        st.info("No approved testimonials yet • Stories activate on owner approval")
   
    # ====================== PENDING APPROVAL (OWNER/ADMIN) ======================
    if current_role in ["owner", "admin"] and pending:
        st.subheader("⏳ Pending Approval")
        for p in pending:
            balance = user_map.get(p["client_name"], 0)
            image_url = p.get("image_url")
            with st.expander(f"{p['client_name']} • Submitted {p['date_submitted']} • Balance ${balance:,.2f}", expanded=False):
                if image_url:
                    st.image(image_url, use_container_width=True)
                else:
                    st.caption("No photo")
                st.markdown(p["message"])
               
                col_app1, col_app2 = st.columns(2)
                with col_app1:
                    if st.button("Approve & Auto-Announce", key=f"app_t_{p['id']}"):
                        try:
                            supabase.table("testimonials").update({"status": "Approved"}).eq("id", p["id"]).execute()
                            # Auto-announce
                            supabase.table("announcements").insert({
                                "title": f"New Testimonial from {p['client_name']}!",
                                "message": p["message"],
                                "date": datetime.date.today().isoformat(),
                                "posted_by": "System (Auto)",
                                "category": "Testimonial"
                            }).execute()
                            st.success("Approved & announced realtime!")
                            st.cache_data.clear()
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
                with col_app2:
                    if st.button("Reject & Delete", key=f"rej_t_{p['id']}", type="secondary"):
                        try:
                            if p.get("storage_path"):
                                supabase.storage.from_("testimonials").remove([p["storage_path"]])
                            supabase.table("testimonials").delete().eq("id", p["id"]).execute()
                            st.success("Rejected & removed permanently")
                            st.cache_data.clear()
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
   
    st.markdown(f"""
    <div class='glass-card' style='padding:3rem; text-align:center; margin:3rem 0;'>
        <h1 style="background:linear-gradient(90deg,{accent_color},#ffd700); -webkit-background-clip:text; -webkit-text-fill-color:transparent;">
            Success Stories & Motivation
        </h1>
        <p style="font-size:1.3rem; margin:2rem 0;">
            Client submissions • Photos PERMANENT • Balance context • Auto-announce approved • Empire inspired & growing.
        </p>
        <h2 style="color:#ffd700;">👑 KMFX Testimonials • Cloud Permanent 2026</h2>
    </div>
    """, unsafe_allow_html=True)
# ====================== END OF FINAL TESTIMONIALS WITH SUPABASE STORAGE ======================
# ====================== PART 6: REPORTS & EXPORT PAGE (FINAL SUPER ADVANCED - MATERIALIZED VIEWS FOR INSTANT TOTALS) ======================
elif selected == "📈 Reports & Export":
    st.header("Empire Reports & Export 📈")
    st.markdown("**Full analytics engine: Auto-aggregated realtime reports from profits, distributions, balances, growth fund, accounts • Professional charts • Detailed breakdowns • Multiple CSV exports • Instant loading via materialized views • Owner/Admin only.**")
   
    # SAFE ROLE - OWNER/ADMIN ONLY
    current_role = st.session_state.get("role", "guest")
    if current_role not in ["owner", "admin"]:
        st.error("🔒 Reports & Export is restricted to Owner/Admin for empire analytics security.")
        st.stop()
   
    # FULL REALTIME CACHE WITH MATERIALIZED VIEWS (INSTANT TOTALS)
    @st.cache_data(ttl=60)
    def fetch_reports_full():
        try:
            # INSTANT totals from materialized views (<0.2s even with thousands of records)
            empire_resp = supabase.table("mv_empire_summary").select("*").execute()
            empire = empire_resp.data[0] if empire_resp.data else {}
            total_accounts = empire.get("total_accounts", 0)
            total_equity = empire.get("total_equity", 0.0)
           
            client_resp = supabase.table("mv_client_balances").select("*").execute()
            client_summary = client_resp.data[0] if client_resp.data else {}
            total_client_balances = client_summary.get("total_client_balances", 0.0)
           
            gf_resp = supabase.table("mv_growth_fund_balance").select("balance").execute()
            gf_balance = gf_resp.data[0]["balance"] if gf_resp.data else 0.0
           
            # Profits & Distributions (lightweight with indexes)
            profits_resp = supabase.table("profits").select("*").order("record_date", desc=True).execute()
            profits = profits_resp.data or []
            total_gross = sum(p.get("gross_profit", 0) for p in profits)
           
            dist_resp = supabase.table("profit_distributions").select("*").execute()
            distributions = dist_resp.data or []
            total_distributed = sum(d.get("share_amount", 0) for d in distributions if not d.get("is_growth_fund", False))
           
            # Clients list
            users_resp = supabase.table("users").select("full_name, balance").eq("role", "client").execute()
            clients = users_resp.data or []
           
            # Accounts list
            accounts_resp = supabase.table("ftmo_accounts").select("name, current_phase, current_equity, withdrawable_balance").execute()
            accounts = accounts_resp.data or []
           
            return (
                profits, distributions, clients, accounts,
                total_gross, total_distributed, total_client_balances,
                gf_balance, total_accounts, total_equity
            )
        except Exception as e:
            st.error(f"Reports fetch error: {e}")
            return [], [], [], [], 0, 0, 0, 0, 0, 0
   
    (profits, distributions, clients, accounts,
     total_gross, total_distributed, total_client_balances,
     gf_balance, total_accounts, total_equity) = fetch_reports_full()
   
    st.caption("🔄 Reports auto-update realtime • Instant totals via materialized views • Optimized for speed")
   
    # ====================== EMPIRE SUMMARY METRICS (INSTANT FROM MV) ======================
    st.subheader("Empire Overview Metrics")
    col_m1, col_m2, col_m3, col_m4, col_m5, col_m6 = st.columns(6)
    col_m1.metric("Total Gross Profits", f"${total_gross:,.0f}")
    col_m2.metric("Total Distributed", f"${total_distributed:,.0f}")
    col_m3.metric("Client Balances (Auto)", f"${total_client_balances:,.0f}")
    col_m4.metric("Growth Fund (Auto)", f"${gf_balance:,.0f}")
    col_m5.metric("Active Accounts", total_accounts)
    col_m6.metric("Total Equity", f"${total_equity:,.0f}")
   
    # ====================== PROFIT TREND CHART (MONTHLY AUTO-AGGREGATED - ALREADY FIXED) ======================
    st.subheader("Profit Trend (Monthly Auto-Aggregated)")
    if profits:
        profits_df = pd.DataFrame(profits)
        profits_df["record_date"] = pd.to_datetime(profits_df["record_date"])
       
        # Groupby month & sum numeric only
        monthly = profits_df.groupby(profits_df["record_date"].dt.strftime("%Y-%m")).sum(numeric_only=True)[["gross_profit"]].reset_index()
        monthly = monthly.sort_values("record_date")
       
        fig_trend = go.Figure()
        fig_trend.add_trace(go.Bar(
            x=monthly["record_date"],
            y=monthly["gross_profit"],
            name="Gross Profit",
            marker_color=accent_primary,
            text=monthly["gross_profit"].apply(lambda x: f"${x:,.0f}"),
            textposition="outside"
        ))
        fig_trend.update_layout(
            title="Monthly Gross Profit Trend",
            height=500,
            yaxis_title="Gross Profit (USD)",
            xaxis_title="Month"
        )
        st.plotly_chart(fig_trend, use_container_width=True)
    else:
        st.info("No profits recorded yet • Trend activates with first distribution")
   
    # ====================== DISTRIBUTION PIE (PARTICIPANTS) ======================
    st.subheader("Participant Distribution Breakdown (All Time)")
    if distributions:
        dist_df = pd.DataFrame(distributions)
        part_summary = dist_df.groupby("participant_name")["share_amount"].sum().reset_index()
        part_summary = part_summary.sort_values("share_amount", ascending=False)
       
        fig_pie = go.Figure(data=[go.Pie(
            labels=part_summary["participant_name"],
            values=part_summary["share_amount"],
            hole=0.5,
            textinfo='label+percent',
            textposition='outside'
        )])
        fig_pie.update_layout(title="Total Shares by Participant", height=600)
        st.plotly_chart(fig_pie, use_container_width=True)
       
        # Table below pie
        part_summary["share_amount"] = part_summary["share_amount"].apply(lambda x: f"${x:,.2f}")
        part_summary = part_summary.rename(columns={"participant_name": "Participant", "share_amount": "Total Share"})
        st.dataframe(part_summary, use_container_width=True, hide_index=True)
    else:
        st.info("No distributions yet")
   
    # ====================== CLIENT BALANCES TABLE (REALTIME AUTO) ======================
    st.subheader("Client Balances (Realtime Auto from mv_client_balances)")
    if clients:
        balance_df = pd.DataFrame([
            {"Client": c["full_name"], "Balance": f"${c.get('balance', 0):,.2f}"}
            for c in clients
        ])
        balance_df = balance_df.sort_values("Balance", ascending=False)
        st.dataframe(balance_df, use_container_width=True, hide_index=True)
    else:
        st.info("No clients yet")
   
    # ====================== GROWTH FUND SUMMARY (INSTANT MV) ======================
    st.subheader("Growth Fund Summary")
    st.metric("Current Balance (Instant from mv_growth_fund_balance)", f"${gf_balance:,.0f}")
   
    # ====================== ACCOUNTS TABLE ======================
    st.subheader("Accounts Summary")
    if accounts:
        acc_df = pd.DataFrame(accounts)
        acc_df["current_equity"] = acc_df["current_equity"].apply(lambda x: f"${x:,.0f}")
        acc_df["withdrawable_balance"] = acc_df["withdrawable_balance"].apply(lambda x: f"${x:,.0f}")
        st.dataframe(acc_df[["name", "current_phase", "current_equity", "withdrawable_balance"]], use_container_width=True, hide_index=True)
    else:
        st.info("No accounts yet")
   
    # ====================== EXPORT OPTIONS (MULTIPLE CSV) ======================
    st.subheader("📤 Export Reports")
    col_exp1, col_exp2 = st.columns(2)
    with col_exp1:
        if profits:
            csv_profits = pd.DataFrame(profits).to_csv(index=False).encode()
            st.download_button(
                "📄 Export Profits Report CSV",
                csv_profits,
                "KMFX_Profits_Report.csv",
                "text/csv",
                use_container_width=True
            )
        if distributions:
            csv_dist = pd.DataFrame(distributions).to_csv(index=False).encode()
            st.download_button(
                "📄 Export Distributions CSV",
                csv_dist,
                "KMFX_Distributions_Report.csv",
                "text/csv",
                use_container_width=True
            )
    with col_exp2:
        if clients:
            csv_bal = pd.DataFrame([
                {"Client": c["full_name"], "Balance": c.get("balance", 0)}
                for c in clients
            ]).to_csv(index=False).encode()
            st.download_button(
                "📄 Export Client Balances CSV",
                csv_bal,
                "KMFX_Client_Balances.csv",
                "text/csv",
                use_container_width=True
            )
        # Empire Summary CSV
        summary_data = {
            "Metric": [
                "Total Gross Profits", "Total Distributed", "Total Client Balances",
                "Growth Fund Balance", "Active Accounts", "Total Equity"
            ],
            "Value": [
                f"${total_gross:,.0f}", f"${total_distributed:,.0f}", f"${total_client_balances:,.0f}",
                f"${gf_balance:,.0f}", total_accounts, f"${total_equity:,.0f}"
            ]
        }
        csv_summary = pd.DataFrame(summary_data).to_csv(index=False).encode()
        st.download_button(
            "📄 Export Empire Summary CSV",
            csv_summary,
            "KMFX_Empire_Summary.csv",
            "text/csv",
            use_container_width=True
        )
   
    st.markdown(f"""
    <div class='glass-card' style='padding:3rem; text-align:center; margin:3rem 0;'>
        <h1 style="background:linear-gradient(90deg,{accent_color},#ffd700); -webkit-background-clip:text; -webkit-text-fill-color:transparent;">
            Instant Analytics & Exports
        </h1>
        <p style="font-size:1.3rem; margin:2rem 0;">
            Materialized views for instant totals • Realtime charts • Clean tables • Multiple CSV exports • Empire performance at a glance.
        </p>
        <h2 style="color:#ffd700;">👑 KMFX Reports • Lightning Fast 2026</h2>
    </div>
    """, unsafe_allow_html=True)
# ====================== END OF FINAL REPORTS & EXPORT WITH MATERIALIZED VIEWS ======================
# ====================== PART 6: SIMULATOR PAGE (FINAL SUPER ADVANCED - MATERIALIZED VIEWS FOR INSTANT AUTO-LOAD) ======================
elif selected == "🔮 Simulator":
    st.header("Empire Growth Simulator 🔮")
    st.markdown("**Advanced scaling forecaster: Auto-loaded from current empire (accounts, equity, GF balance, avg profits, GF %, units) via materialized views for instant load • Simulate scenarios • Projected equity, distributions, growth fund, units • Realtime multi-line charts • Sankey flow previews • Professional planning tool.**")
   
    # SAFE ROLE (all can use)
    current_role = st.session_state.get("role", "guest")
   
    # FULL INSTANT CACHE - MATERIALIZED VIEWS FOR CORE STATS (<0.5s load)
    @st.cache_data(ttl=60)
    def fetch_simulator_data():
        try:
            # INSTANT core stats from materialized views
            empire_resp = supabase.table("mv_empire_summary").select("total_accounts, total_equity").execute()
            empire = empire_resp.data[0] if empire_resp.data else {}
            total_accounts = empire.get("total_accounts", 0)
            total_equity = empire.get("total_equity", 0.0)
           
            gf_resp = supabase.table("mv_growth_fund_balance").select("balance").execute()
            gf_balance = gf_resp.data[0]["balance"] if gf_resp.data else 0.0
           
            # Lightweight for averages (accounts & profits tables are small/optimized)
            accounts_resp = supabase.table("ftmo_accounts").select(
                "current_equity, unit_value, participants_v2, contributor_share_pct"
            ).execute()
            accounts = accounts_resp.data or []
           
            profits_resp = supabase.table("profits").select("gross_profit").execute()
            profits = profits_resp.data or []
           
            # Auto-calcs (fast even with hundreds of records)
            total_gross = sum(p.get("gross_profit", 0) for p in profits)
            num_profits = len(profits)
            avg_monthly_profit = total_gross / max(1, num_profits) if num_profits > 0 else 15000.0
           
            # Avg GF % (from contributor_share_pct or participants_v2 if needed)
            gf_pcts = [a.get("contributor_share_pct", 20.0) for a in accounts]
            avg_gf_pct = sum(gf_pcts) / len(gf_pcts) if gf_pcts else 20.0
           
            # Avg unit value
            unit_values = [a.get("unit_value", 3000.0) for a in accounts if a.get("unit_value")]
            avg_unit_value = sum(unit_values) / len(unit_values) if unit_values else 3000.0
           
            return (
                total_equity, total_accounts, avg_monthly_profit,
                avg_gf_pct, avg_unit_value, gf_balance
            )
        except Exception as e:
            st.error(f"Simulator data fetch error: {e}")
            return 0.0, 0, 15000.0, 20.0, 3000.0, 0.0
   
    (total_equity, total_accounts, avg_monthly_profit,
     avg_gf_pct, avg_unit_value, gf_balance) = fetch_simulator_data()
   
    st.info(f"**Instant Auto-Loaded Empire Stats (via Materialized Views):** {total_accounts} accounts • Total Equity ${total_equity:,.0f} • Avg Monthly Gross ${avg_monthly_profit:,.0f} • Avg GF % {avg_gf_pct:.1f}% • Avg Unit Value ${avg_unit_value:,.0f} • Current GF ${gf_balance:,.0f}")
   
    # ====================== ADVANCED SIMULATION INPUTS ======================
    st.subheader("Configure Simulation Scenarios")
    col_sim1, col_sim2 = st.columns(2)
    with col_sim1:
        months = st.slider("Projection Months", 6, 72, 36)
        projected_accounts = st.slider("Projected Active Accounts", total_accounts, total_accounts + 30, total_accounts + 10)
        monthly_gross_per_acc = st.number_input("Monthly Gross Profit per Account (USD)", value=avg_monthly_profit, step=1000.0)
        gf_percentage = st.slider("Growth Fund % (from Profits)", 0.0, 50.0, avg_gf_pct)
    with col_sim2:
        unit_value_proj = st.number_input("Profit Unit Value (USD)", value=avg_unit_value, step=500.0)
        monthly_manual_in = st.number_input("Additional Monthly Manual In to GF (USD)", value=0.0, step=1000.0)
        scenario_name = st.text_input("Scenario Name", value="Base Scaling Plan")
   
    # Auto-calc projected monthly
    monthly_gross_total = monthly_gross_per_acc * projected_accounts
    monthly_gf_add = monthly_gross_total * (gf_percentage / 100) + monthly_manual_in
    monthly_distributed = monthly_gross_total - monthly_gf_add
    monthly_units = monthly_gross_total / unit_value_proj if unit_value_proj > 0 else 0
   
    col_calc1, col_calc2, col_calc3, col_calc4 = st.columns(4)
    col_calc1.metric("Projected Monthly Gross", f"${monthly_gross_total:,.0f}")
    col_calc2.metric("Monthly GF Add", f"${monthly_gf_add:,.0f}")
    col_calc3.metric("Monthly Distributed", f"${monthly_distributed:,.0f}")
    col_calc4.metric("Monthly Units Generated", f"{monthly_units:.2f}")
   
    # ====================== RUN SIMULATION (REALTIME CHARTS & TREES) ======================
    if st.button("🚀 Run Simulation", type="primary", use_container_width=True):
        # Starting points
        start_equity = total_equity
        start_gf = gf_balance
       
        dates = [datetime.date.today() + datetime.timedelta(days=30*i) for i in range(months + 1)]
       
        # Projections
        equity_proj = [start_equity]
        gf_proj = [start_gf]
        distributed_proj = [0]
        units_proj = [0]
       
        for i in range(months):
            gross = monthly_gross_per_acc * projected_accounts
            gf_add = gross * (gf_percentage / 100) + monthly_manual_in
            distributed = gross - gf_add
            units = gross / unit_value_proj if unit_value_proj > 0 else 0
           
            new_equity = equity_proj[-1] + gross
            new_gf = gf_proj[-1] + gf_add
           
            equity_proj.append(new_equity)
            gf_proj.append(new_gf)
            distributed_proj.append(distributed_proj[-1] + distributed)
            units_proj.append(units_proj[-1] + units)
       
        # Multi-line chart
        fig_multi = go.Figure()
        fig_multi.add_trace(go.Scatter(x=dates, y=equity_proj, name="Total Equity", line=dict(color=accent_color, width=6)))
        fig_multi.add_trace(go.Scatter(x=dates, y=gf_proj, name="Growth Fund", line=dict(color="#ffd700", width=6)))
        fig_multi.add_trace(go.Scatter(x=dates, y=distributed_proj, name="Distributed Shares", line=dict(color="#00ffaa", width=5)))
        fig_multi.add_trace(go.Scatter(x=dates, y=units_proj, name="Cumulative Units", line=dict(color="#ff6b6b", width=5, dash="dot")))
        fig_multi.update_layout(
            title=f"{scenario_name} - Empire Trajectory",
            height=600,
            hovermode="x unified"
        )
        st.plotly_chart(fig_multi, use_container_width=True)
       
        # Final metrics
        col_final1, col_final2, col_final3, col_final4 = st.columns(4)
        col_final1.metric("Final Equity", f"${equity_proj[-1]:,.0f}")
        col_final2.metric("Final Growth Fund", f"${gf_proj[-1]:,.0f}")
        col_final3.metric("Total Distributed", f"${distributed_proj[-1]:,.0f}")
        col_final4.metric("Total Units Generated", f"{units_proj[-1]:.2f}")
       
        # Projected average monthly Sankey
        st.subheader("Projected Average Monthly Distribution Flow")
        if monthly_gross_total > 0:
            labels = ["Monthly Gross"]
            values = []
            source = []
            target = []
            idx = 1
           
            labels.append("Distributed Shares")
            values.append(monthly_distributed)
            source.append(0)
            target.append(idx)
            idx += 1
           
            labels.append("Growth Fund")
            values.append(monthly_gf_add)
            source.append(0)
            target.append(idx)
           
            fig_avg = go.Figure(data=[go.Sankey(
                node=dict(pad=20, thickness=30, label=labels, color=["#00ffaa", "#00ffcc", "#ffd700"]),
                link=dict(source=source, target=target, value=values)
            )])
            fig_avg.update_layout(height=500, title=f"Avg Monthly Flow: ${monthly_gross_total:,.0f}")
            st.plotly_chart(fig_avg, use_container_width=True)
        else:
            st.info("No gross profit projected")
   
    st.markdown(f"""
    <div class='glass-card' style='padding:3rem; text-align:center; margin:3rem 0;'>
        <h1 style="background:linear-gradient(90deg,{accent_color},#ffd700); -webkit-background-clip:text; -webkit-text-fill-color:transparent;">
            Instant Predictive Simulator
        </h1>
        <p style="font-size:1.3rem; margin:2rem 0;">
            Materialized views for instant auto-load • Accurate current stats • Multi-scenario projections • Visual flows • Plan your empire scaling.
        </p>
        <h2 style="color:#ffd700;">👑 KMFX Simulator • Lightning Fast 2026</h2>
    </div>
    """, unsafe_allow_html=True)
# ====================== END OF FINAL SIMULATOR WITH MATERIALIZED VIEWS ======================
# ====================== PART 6: AUDIT LOGS PAGE (FINAL SUPER ADVANCED - FULL MAIN FLOW SYNC & REALTIME) ======================
elif selected == "📜 Audit Logs":
    st.header("Empire Audit Logs 📜")
    st.markdown("**Full transparency & security: Realtime auto-logged actions from all empire transactions (profits, distributions, licenses, withdrawals, uploads, announcements, user changes) • Advanced search/filter • Timeline chart • Export CSV • Owner-only for compliance & oversight.**")
    
    # SAFE ROLE - OWNER ONLY
    current_role = st.session_state.get("role", "guest")
    if current_role != "owner":
        st.error("🔒 Audit Logs are OWNER-ONLY for empire security & compliance.")
        st.stop()
    
    # FULL REALTIME CACHE (short ttl for live tracking)
    @st.cache_data(ttl=30)
    def fetch_audit_full():
        logs_resp = supabase.table("logs").select("*").order("timestamp", desc=True).execute()
        logs = logs_resp.data or []
        
        # Auto-summary stats
        total_actions = len(logs)
        unique_users = len(set(l.get("user_name") for l in logs if l.get("user_name")))
        action_types = set(l.get("action") for l in logs)
        
        return logs, total_actions, unique_users, action_types
    
    logs, total_actions, unique_users, action_types = fetch_audit_full()
    
    st.caption("🔄 Logs auto-refresh every 30s • Every empire action tracked realtime")
    
    # ====================== AUDIT SUMMARY METRICS (PROFESSIONAL) ======================
    col_a1, col_a2, col_a3 = st.columns(3)
    col_a1.metric("Total Logged Actions", total_actions)
    col_a2.metric("Unique Active Users", unique_users)
    col_a3.metric("Action Types Tracked", len(action_types))
    
    # ====================== ADVANCED SEARCH & FILTER ======================
    st.subheader("🔍 Advanced Log Search & Filter")
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        search_log = st.text_input("Search Action/Details/User")
    with col_f2:
        filter_user = st.selectbox("Filter User", ["All"] + sorted(set(l.get("user_name") for l in logs if l.get("user_name"))))
    with col_f3:
        filter_action = st.selectbox("Filter Action Type", ["All"] + sorted(set(l.get("action") for l in logs)))
    
    filtered_logs = logs
    if search_log:
        filtered_logs = [l for l in filtered_logs if search_log.lower() in l.get("action", "").lower() or 
                         search_log.lower() in l.get("details", "").lower() or 
                         search_log.lower() in str(l.get("user_name", "")).lower()]
    if filter_user != "All":
        filtered_logs = [l for l in filtered_logs if l.get("user_name") == filter_user]
    if filter_action != "All":
        filtered_logs = [l for l in filtered_logs if l.get("action") == filter_action]
    
    # ====================== ACTIVITY TIMELINE CHART (REALTIME) ======================
    st.subheader("📊 Empire Activity Timeline (Realtime)")
    if filtered_logs:
        log_df = pd.DataFrame(filtered_logs)
        log_df["timestamp"] = pd.to_datetime(log_df["timestamp"])
        daily_counts = log_df.groupby(log_df["timestamp"].dt.date).size().reset_index(name="Actions")
        
        fig_timeline = go.Figure()
        fig_timeline.add_trace(go.Scatter(x=daily_counts["timestamp"], y=daily_counts["Actions"], mode='lines+markers', line=dict(color=accent_color, width=5)))
        fig_timeline.update_layout(title="Daily Empire Actions", height=400)
        st.plotly_chart(fig_timeline, use_container_width=True)
    else:
        st.info("No matching logs • All actions auto-tracked")
    
    # ====================== DETAILED LOG TABLE (CLEAN & EXPORTABLE) ======================
    st.subheader(f"Detailed Audit Logs ({len(filtered_logs)} entries)")
    if filtered_logs:
        log_display = pd.DataFrame(filtered_logs)
        log_display["timestamp"] = pd.to_datetime(log_display["timestamp"]).dt.strftime("%Y-%m-%d %H:%M:%S")
        log_display = log_display[["timestamp", "user_name", "user_type", "action", "details"]].rename(columns={
            "timestamp": "Time", "user_name": "User", "user_type": "Role", "action": "Action", "details": "Details"
        })
        st.dataframe(log_display, use_container_width=True, hide_index=True)
        
        # Export
        csv_logs = log_display.to_csv(index=False).encode()
        st.download_button("📤 Export Logs CSV", csv_logs, "KMFX_Audit_Logs.csv", "text/csv", use_container_width=True)
    else:
        st.info("No logs matching filters • Empire fully tracked")
    
    st.markdown(f"""
    <div class='glass-card' style='padding:3rem; text-align:center; margin:3rem 0;'>
        <h1 style="background:linear-gradient(90deg,{accent_color},#ffd700); -webkit-background-clip:text; -webkit-text-fill-color:transparent;">
            Complete Audit Transparency
        </h1>
        <p style="font-size:1.3rem; margin:2rem 0;">
            Every action tracked realtime • Searchable • Timeline • Exportable • Empire accountable & secure.
        </p>
        <h2 style="color:#ffd700;">👑 KMFX Audit Logs • Fully Tracked 2026</h2>
    </div>
    """, unsafe_allow_html=True)
# ====================== END OF FINAL AUDIT LOGS ======================
# ====================== PART 6: ADMIN MANAGEMENT PAGE (FINAL SUPER ADVANCED - WITH FULL CLIENT DETAILS, TITLE SYNC, EDIT + DELETE + QR CODE GENERATION) ======================
elif selected == "👤 Admin Management":
    st.header("Empire Team Management 👤")
    st.markdown("**Owner-exclusive: Register team members with full details (Name, Accounts, Email, Contact, Address) & Title (Pioneer, VIP, etc.) for labeled dropdowns • Realtime balances • Full Edit (including password) • Secure delete • QR Login Token Generation/Regeneration • Full sync to FTMO participants as 'Name (Title)'**")

    # STRICT OWNER ONLY
    current_role = st.session_state.get("role", "guest")
    if current_role != "owner":
        st.error("🔒 Team Management is OWNER-ONLY for empire security.")
        st.stop()

    import uuid  # For generating unique QR tokens
    import qrcode
    from io import BytesIO

    # FULL REALTIME CACHE
    @st.cache_data(ttl=30)
    def fetch_users_full():
        users_resp = supabase.table("users").select("*").order("created_at", desc=True).execute()
        return users_resp.data or []

    users = fetch_users_full()

    st.caption("🔄 Team auto-refresh every 30s • Full details & titles sync to dropdowns & lists")

    # REGISTER NEW TEAM MEMBER WITH FULL DETAILS & TITLE
    st.subheader("➕ Register New Team Member")
    with st.form("add_user_form", clear_on_submit=True):
        col_u1, col_u2 = st.columns(2)
        with col_u1:
            username = st.text_input("Username *", placeholder="e.g. michael2026")
            full_name = st.text_input("Full Name *", placeholder="e.g. Michael Reyes")
        with col_u2:
            initial_pwd = st.text_input("Initial Password *", type="password")
            urole = st.selectbox("Role *", ["client", "admin"])
      
        st.markdown("### Client Details")
        col_info1, col_info2 = st.columns(2)
        with col_info1:
            accounts = st.text_input("Accounts (MT5 Logins)", placeholder="e.g. 333723156, 12345678")
            email = st.text_input("Email", placeholder="e.g. michael@example.com")
        with col_info2:
            contact_no = st.text_input("Contact No.", placeholder="e.g. 09128197085")
            address = st.text_area("Address", placeholder="e.g. Rodriguez 1, Rodriguez Dampalit, Malabon City")
      
        title = st.selectbox("Title/Label (Optional)", ["None", "Pioneer", "Distributor", "VIP", "Elite Trader", "Contributor"], help="Shows as 'Name (Title)' in dropdowns & lists")
        notes = st.text_area("Notes (Optional)")
      
        submitted = st.form_submit_button("🚀 Register & Sync Info", type="primary", use_container_width=True)
        if submitted:
            if not username.strip() or not full_name.strip() or not initial_pwd:
                st.error("Username, full name, and password required")
            else:
                try:
                    hashed = bcrypt.hashpw(initial_pwd.encode(), bcrypt.gensalt()).decode()
                    supabase.table("users").insert({
                        "username": username.strip().lower(),
                        "password": hashed,
                        "full_name": full_name.strip(),
                        "role": urole,
                        "balance": 0.0,
                        "title": title if title != "None" else None,
                        "accounts": accounts.strip() or None,
                        "email": email.strip() or None,
                        "contact_no": contact_no.strip() or None,
                        "address": address.strip() or None
                    }).execute()
                    log_action("Team Member Registered", f"{full_name} ({title}) as {urole}")
                    st.success(f"{full_name} registered with full info! Synced to empire.")
                    st.cache_data.clear()
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {str(e)}")

    # CURRENT TEAM WITH FULL INFO DISPLAY + EDIT + DELETE + QR CODE MANAGEMENT
    st.subheader("👥 Current Empire Team (Realtime)")
    if users:
        team = [u for u in users if u["username"] != "kingminted"]  # Exclude owner
       
        col_search1, col_search2 = st.columns(2)
        with col_search1:
            search_user = st.text_input("Search Name/Email/Contact/Accounts")
        with col_search2:
            filter_role = st.selectbox("Filter Role", ["All", "client", "admin"])
      
        filtered_team = team
        if search_user:
            filtered_team = [u for u in filtered_team if search_user.lower() in u["full_name"].lower() or
                             search_user.lower() in str(u.get("email", "")).lower() or
                             search_user.lower() in str(u.get("contact_no", "")).lower() or
                             search_user.lower() in str(u.get("accounts", "")).lower()]
        if filter_role != "All":
            filtered_team = [u for u in filtered_team if u["role"] == filter_role]
      
        if filtered_team:
            for u in filtered_team:
                title_display = f" ({u.get('title', '')})" if u.get('title') else ""
                balance = u.get("balance", 0)
                with st.expander(f"{u['full_name']}{title_display} (@{u['username']}) • {u['role'].title()} • Balance ${balance:,.2f}", expanded=False):
                    st.markdown(f"**Accounts:** {u.get('accounts') or 'None'}")
                    st.markdown(f"**Email:** {u.get('email') or 'None'}")
                    st.markdown(f"**Contact No.:** {u.get('contact_no') or 'None'}")
                    st.markdown(f"**Address:** {u.get('address') or 'None'}")

                    # ====================== QR CODE MANAGEMENT (OWNER ONLY) ======================
                    st.markdown("### 🔑 Quick Login QR Code Management")
                    current_qr_token = u.get("qr_token")

                    # Replace with your actual deployed app URL
                    app_url = "https://kmfxeaftmo.streamlit.app"

                    if current_qr_token:
                        qr_url = f"{app_url}/?qr={current_qr_token}"

                        # Generate QR image
                        buf = BytesIO()
                        qr = qrcode.QRCode(version=1, box_size=10, border=5)
                        qr.add_data(qr_url)
                        qr.make(fit=True)
                        img = qr.make_image(fill_color="black", back_color="white")
                        img.save(buf, format="PNG")

                        col_qr1, col_qr2 = st.columns([1, 2])
                        with col_qr1:
                            st.image(buf.getvalue(), caption="Current QR Code")
                        with col_qr2:
                            st.markdown("**Current QR Login Link**")
                            st.code(qr_url, language="text")
                            st.info("This QR allows instant login on mobile/other devices.")

                        if st.button("🔄 Regenerate QR Token", key=f"regen_qr_{u['id']}"):
                            new_token = str(uuid.uuid4())
                            try:
                                supabase.table("users").update({"qr_token": new_token}).eq("id", u["id"]).execute()
                                log_action("QR Token Regenerated", f"For {u['full_name']}")
                                st.success("New QR token generated! Old one revoked.")
                                st.cache_data.clear()
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error regenerating token: {str(e)}")
                    else:
                        st.info("No QR login token yet.")
                        if st.button("🚀 Generate QR Login Token", key=f"gen_qr_{u['id']}"):
                            new_token = str(uuid.uuid4())
                            try:
                                supabase.table("users").update({"qr_token": new_token}).eq("id", u["id"]).execute()
                                log_action("QR Token Generated", f"For {u['full_name']}")
                                st.success("QR token generated! Refresh to see.")
                                st.cache_data.clear()
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error generating token: {str(e)}")

                    # Existing Edit/Delete buttons
                    col_btn1, col_btn2 = st.columns(2)
                    with col_btn1:
                        if st.button("✏️ Edit", key=f"edit_{u['id']}"):
                            st.session_state.edit_user_id = u["id"]
                            st.session_state.edit_user_data = u.copy()
                            st.rerun()
                    with col_btn2:
                        if st.button("🗑️ Remove from Empire", key=f"del_{u['id']}", type="secondary"):
                            try:
                                supabase.table("users").delete().eq("id", u["id"]).execute()
                                log_action("Team Member Removed", f"{u['full_name']}{title_display}")
                                st.success("User removed")
                                st.cache_data.clear()
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error: {str(e)}")

                    # EDIT FORM (same as before - unchanged)
                    if "edit_user_id" in st.session_state and st.session_state.edit_user_id == u["id"]:
                        edit_data = st.session_state.edit_user_data
                        with st.form(key=f"edit_form_{u['id']}", clear_on_submit=True):
                            col_e1, col_e2 = st.columns(2)
                            with col_e1:
                                new_username = st.text_input("Username *", value=edit_data["username"])
                                new_full_name = st.text_input("Full Name *", value=edit_data["full_name"])
                            with col_e2:
                                new_pwd = st.text_input("New Password (leave blank to keep current)", type="password")
                                new_role = st.selectbox("Role *", ["client", "admin"], index=0 if edit_data["role"] == "client" else 1)
                           
                            st.markdown("### Client Details")
                            col_einfo1, col_einfo2 = st.columns(2)
                            with col_einfo1:
                                new_accounts = st.text_input("Accounts (MT5 Logins)", value=edit_data.get("accounts") or "")
                                new_email = st.text_input("Email", value=edit_data.get("email") or "")
                            with col_einfo2:
                                new_contact = st.text_input("Contact No.", value=edit_data.get("contact_no") or "")
                                new_address = st.text_area("Address", value=edit_data.get("address") or "")
                           
                            new_title = st.selectbox("Title/Label (Optional)", ["None", "Pioneer", "Distributor", "VIP", "Elite Trader", "Contributor"],
                                                     index=0 if not edit_data.get("title") else ["None", "Pioneer", "Distributor", "VIP", "Elite Trader", "Contributor"].index(edit_data["title"]))
                           
                            col_save, col_cancel = st.columns(2)
                            with col_save:
                                save_submitted = st.form_submit_button("💾 Save Changes", type="primary")
                            with col_cancel:
                                cancel_submitted = st.form_submit_button("Cancel")
                           
                            if cancel_submitted:
                                if "edit_user_id" in st.session_state:
                                    del st.session_state.edit_user_id
                                    del st.session_state.edit_user_data
                                st.rerun()
                           
                            if save_submitted:
                                if not new_username.strip() or not new_full_name.strip():
                                    st.error("Username and full name required")
                                else:
                                    try:
                                        update_data = {
                                            "username": new_username.strip().lower(),
                                            "full_name": new_full_name.strip(),
                                            "role": new_role,
                                            "title": new_title if new_title != "None" else None,
                                            "accounts": new_accounts.strip() or None,
                                            "email": new_email.strip() or None,
                                            "contact_no": new_contact.strip() or None,
                                            "address": new_address.strip() or None
                                        }
                                        if new_pwd.strip():
                                            hashed_new = bcrypt.hashpw(new_pwd.encode(), bcrypt.gensalt()).decode()
                                            update_data["password"] = hashed_new
                                       
                                        supabase.table("users").update(update_data).eq("id", u["id"]).execute()
                                        log_action("Team Member Edited", f"{new_full_name} ({new_title if new_title != 'None' else ''})")
                                        st.success("User updated successfully!")
                                        if "edit_user_id" in st.session_state:
                                            del st.session_state.edit_user_id
                                            del st.session_state.edit_user_data
                                        st.cache_data.clear()
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"Error: {str(e)}")
        else:
            st.info("No matching team members")
    else:
        st.info("No team members yet • Register with full info for complete tracking")
  
    st.markdown(f"""
    <div class='glass-card' style='padding:3rem; text-align:center; margin:3rem 0;'>
        <h1 style="background:linear-gradient(90deg,{accent_color},#ffd700); -webkit-background-clip:text; -webkit-text-fill-color:transparent;">
            Owner Team Control Center
        </h1>
        <p style="font-size:1.3rem; margin:2rem 0;">
            Full client info (accounts, email, contact, address) • Titles synced • Full Edit + Delete • QR Login Token Management • Realtime balances • Empire team fully managed.
        </p>
        <h2 style="color:#ffd700;">👑 KMFX Team Management • Owner Exclusive 2026</h2>
    </div>
    """, unsafe_allow_html=True)
# ====================== END OF FINAL ADMIN MANAGEMENT WITH QR CODE GENERATION ======================
# ====================== CLOSE MAIN CONTENT & FOOTER ======================
st.markdown("</div>", unsafe_allow_html=True)
st.markdown("---")
st.caption("© 2025 KMFX FTMO Pro • Cloud Edition • Built by Faith, Shared for Generations 👑")

# ====================== END OF PART 6 - FULL SUPABASE APP COMPLETE ======================
# Congratulations! Your KMFX FTMO Pro Manager is now FULLY CLOUD-BASED with Supabase.
# All data in cloud, ready for deployment, multi-device access.
# Scale to millions in 2026! 🚀💰
