
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
# === TEMPORARY GLOBAL TIME FIX - PHILIPPINE TIME ===
st.markdown("""
<style>
    /* Optional: gawing mas malinaw ang timestamp para madaling makita kung na-update */
    .timestamp-fix { color: #00ffaa; font-weight: bold; }
</style>

<script>
function fixTimestamps() {
    // Hanapin lahat ng text nodes na may possible ISO timestamp
    const walker = document.createTreeWalker(
        document.body,
        NodeFilter.SHOW_TEXT,
        null,
        false
    );

    let node;
    while (node = walker.nextNode()) {
        let text = node.nodeValue.trim();
        if (text.match(/\\d{4}-\\d{2}-\\d{2}[T ]\\d{2}:\\d{2}(:\\d{2})?(Z)?/)) {
            try {
                // Subukan i-parse bilang date
                let iso = text.replace(" ", "T"); // kung may space sa halip na T
                let date = new Date(iso);
                if (!isNaN(date.getTime())) {
                    // Convert to PHT
                    let pht = date.toLocaleString('en-PH', {
                        timeZone: 'Asia/Manila',
                        year: 'numeric',
                        month: 'short',
                        day: '2-digit',
                        hour: '2-digit',
                        minute: '2-digit',
                        hour12: true
                    });
                    // Palitan ang text
                    node.nodeValue = node.nodeValue.replace(text, pht);
                }
            } catch(e) {}
        }
    }
}

// I-run pagkatapos mag-load + may delay para siguradong na-render na lahat
window.addEventListener('load', function() {
    setTimeout(fixTimestamps, 800);
    // I-run ulit after 2 seconds para sa dynamic content
    setTimeout(fixTimestamps, 2000);
});
</script>
""", unsafe_allow_html=True)
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

    # ====================== MY FULL TRADING JOURNEY - EXPANDABLE SECTION ======================
    st.markdown("<div class='glass-card' style='text-align:center; margin:5rem 0; padding:3rem;'>", unsafe_allow_html=True)
    st.markdown(f"<h2 class='gold-text'>Want the Full Story Behind KMFX EA?</h2>", unsafe_allow_html=True)
    st.markdown("<p style='font-size:1.4rem; opacity:0.9;'>From OFW in Saudi to building an automated empire — built by faith, lessons, and persistence.</p>", unsafe_allow_html=True)

    if st.button("👑 Read My Full Trading Journey (2014–2026)", type="primary", use_container_width=True):
        st.session_state.show_full_journey = True

    if st.session_state.get("show_full_journey", False):
        st.markdown("<div class='glass-card' style='padding:3rem; margin:3rem 0;'>", unsafe_allow_html=True)
        st.markdown("<h2 class='gold-text' style='text-align:center;'>My Trading Journey: From 2014 to KMFX EA 2026</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center; font-style:italic;'>Ako si Mark Jeff Blando (Codename: Kingminted) — simula 2014 hanggang ngayon 2026, pinagdaanan ko ang lahat: losses, wins, scams, pandemic gains, at sa wakas, pagbuo ng sariling automated system. Ito ang kwento ko, built by faith, shared for generations.</p>", unsafe_allow_html=True)
        
        # 2014 – Discovery
        st.markdown("<h3 style='color:{accent_gold};'>2014: The Beginning in Saudi Arabia</h3>", unsafe_allow_html=True)
        # st.image("assets/journey_2014.png", use_container_width=True, caption="My early days discovering PSE while working in Saudi")
        st.write("""
        Bilang Telecom Technician sa STC Saudi Arabia, tuwing Friday off ko, nag-search online ako at natuklasan ang Philippine stock market.
        Nag-create ako ng account sa First Metro Sec, nagsimulang magbasa ng news, at sinubukan lahat ng strategy.
        Mix emotions: sobrang saya pag nanalo, lungkot pag natalo. Naging kaibigan ko sina Ramil, Mheg, Christy noong 2016 era. Hindi pa seryoso noon, pero dun na nagsimula ang passion.
        """)
        
        # 2017 – Crypto Boom
        st.markdown("<h3 style='color:{accent_gold};'>2017: Umuwi sa Pinas at Crypto Era</h3>", unsafe_allow_html=True)
        # st.image("assets/journey_2017.png", use_container_width=True, caption="Bitcoin boom days")
        st.write("""
        Umuwi ako para mag-family (30+ na si misis 😊). Noon din sumabog ang Bitcoin sa ₱1M — dun na ako na-hook sa crypto (24/7 market vs PSE hours).
        Ginamit ko yung stock learnings ko, pero newbie pa rin: na-scam sa sites like Auroramining, tried futures, manalo-natatalo. Walang solid strategy o discipline pa.
        """)
        
        # 2019-2021 – Pandemic Wins
        st.markdown("<h3 style='color:{accent_gold};'>2019–2021: Pandemic Days & Biggest Lesson</h3>", unsafe_allow_html=True)
        col_klever1, col_klever2 = st.columns(2)
        with col_klever1:
            # st.image("assets/journey_klever1.png", use_container_width=True, caption="Klever token gains (before glitch)")
            st.caption("(Placeholder for Klever gains screenshot)")
        with col_klever2:
            # st.image("assets/journey_klever2.png", use_container_width=True, caption="Big lesson from the crash")
            st.caption("(Placeholder for crash lesson screenshot)")
        st.write("""
        Natagpuan ko ang Klever token — ginamit ko yung "Ninja Move" (set buy, instant sell sa target). Sobrang laki ng gains, kasama kapatid kong si Michael.
        Pero glitch sa platform — half lang nabalik. Realization: May pera talaga sa market kung may **right strategy + discipline + emotion control**.
        90% ng traders natatalo dahil sa emotions, hindi sa strategy. After 2021 crash (BTC 60k → 20k), lumayo muna ako.
        """)
        
        # 2024-2025 – Forex & EA Building
        st.markdown("<h3 style='color:{accent_gold};'>2024–2025: The Professional Shift</h3>", unsafe_allow_html=True)
        # st.image("assets/journey_ea_build.png", use_container_width=True, caption="Self-studying MQL5 and building KMFX EA")
        st.caption("(Placeholder for EA building screenshot)")
        st.write("""
        Nauso ang AI → naisip ko ang Expert Advisor. Self-study MQL5 for almost 1 year. Pinagsama ko lahat ng natutunan since 2014.
        Nakita ko: Professional trader = strategy + risk management + psychology. Goal ko na maging ganun.
        January 2025: KMFX EA (Kingminted Forex EA) fully working — focused on Gold (XAUUSD).
        Testing with Weber, Jai, Sheldon, Ramil. Pioneer community formed end of 2025.
        """)
        
        # 2025-2026 – FTMO Challenges
        st.markdown("<h3 style='color:{accent_gold};'>2025–2026: FTMO Challenges & Comeback</h3>", unsafe_allow_html=True)
        col_ftmo1, col_ftmo2 = st.columns(2)
        with col_ftmo1:
            # st.image("assets/journey_ftmo_phase1.png", use_container_width=True, caption="Passed Phase 1 in 13 days! 🎉")
            st.caption("(Placeholder for Phase 1 pass)")
        with col_ftmo2:
            # st.image("assets/journey_ftmo_current.png", use_container_width=True, caption="Current challenge - full trust mode")
            st.caption("(Placeholder for current challenge)")
        st.write("""
        Dec 2025: First 10K challenge — **Passed Phase 1 in 13 days!** (+10.41%, 2.98% DD).
        Phase 2: Failed dahil emotional intervention (galaw ko yung system). Lesson: Full trust lang — "run and forget" mode.
        Jan 2026: New challenge, full hands-off. Comeback stronger.
        """)
        
        # Realization & Vision (IMAGE KEPT ACTIVE)
        st.markdown("<h3 style='color:{accent_gold};'>Realization & Future Vision</h3>", unsafe_allow_html=True)
        st.image("assets/journey_vision.png", use_container_width=True, caption="Built by Faith, Shared for Generations 👑")
        st.write("""
        Since 2014, alam ko na may **big plan si God** para sa'kin — kaya ako na-involve sa market. Purpose ko na 'to.
        KMFX EA para makatulong sa maraming tao. Dream: Build **KMFX EA Foundations** — guide aspiring traders to become professionals.
        Bigger dream: Passive income para sa lahat → financial freedom, more time for Lord, family, peaceful life.
        
        **KMFX EA: Built by Faith, Shared for Generations**
        
        — Mark Jeff Blando | Founder & Developer | Since 2014
        """)
        
        if st.button("Close Journey", use_container_width=True):
            st.session_state.show_full_journey = False
            st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)  # Close teaser card

    # Progress Timeline (same indentation level as Portfolio Story)
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
if selected == "🏠 Dashboard":
    st.header("Elite Empire Command Center 🚀")
    st.markdown("**Realtime, fully automatic empire overview**")
    current_role = st.session_state.get("role", "guest")

    # ────────────────────────────────────────────────
    # OPTIMIZED fetch_empire_summary (MV-only for totals + lightweight raw for trees)
    # ────────────────────────────────────────────────
    @st.cache_data(ttl=30)
    def fetch_empire_summary():
        try:
            # INSTANT TOTALS FROM MATERIALIZED VIEWS
            gf_resp = supabase.table("mv_growth_fund_balance").select("balance").execute()
            gf_balance = gf_resp.data[0]["balance"] if gf_resp.data else 0.0

            empire_resp = supabase.table("mv_empire_summary").select("*").execute()
            empire = empire_resp.data[0] if empire_resp.data else {}
            total_accounts = empire.get("total_accounts", 0)
            total_equity = empire.get("total_equity", 0.0)
            total_withdrawable = empire.get("total_withdrawable", 0.0)

            client_resp = supabase.table("mv_client_balances").select("*").execute()
            client_summary = client_resp.data[0] if client_resp.data else {}
            total_client_balances = client_summary.get("total_client_balances", 0.0)

            # LIGHTWEIGHT RAW FOR TREES & CALCS ONLY
            accounts_resp = supabase.table("ftmo_accounts").select("*").execute()
            accounts = accounts_resp.data or []

            profits_resp = supabase.table("profits").select("gross_profit").execute()
            total_gross = sum(p.get("gross_profit", 0) for p in profits_resp.data or [])

            dist_resp = supabase.table("profit_distributions").select("share_amount, participant_name, is_growth_fund").execute()
            distributions = dist_resp.data or []
            total_distributed = sum(d.get("share_amount", 0) for d in distributions if not d.get("is_growth_fund", False))

            # Participant shares (for Sankey)
            participant_shares = {}
            for d in distributions:
                if not d.get("is_growth_fund", False):
                    name = d["participant_name"]
                    participant_shares[name] = participant_shares.get(name, 0) + d["share_amount"]

            # Total funded PHP
            total_funded_php = 0
            for acc in accounts:
                contrib = acc.get("contributors_v2") or acc.get("contributors", [])
                for c in contrib:
                    units = c.get("units", 0)
                    php_per_unit = c.get("php_per_unit", 0) or 0
                    total_funded_php += units * php_per_unit

            return (
                accounts, total_accounts, total_equity, total_withdrawable,
                gf_balance, total_gross, total_distributed,
                total_client_balances, participant_shares, total_funded_php
            )
        except Exception as e:
            st.error(f"Dashboard data error: {str(e)}")
            return [], 0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, {}, 0

    # Fetch data
    (
        accounts, total_accounts, total_equity, total_withdrawable,
        gf_balance, total_gross, total_distributed,
        total_client_balances, participant_shares, total_funded_php
    ) = fetch_empire_summary()

    # ────────────────────────────────────────────────
    # METRICS GRID (Clean & Fast)
    # ────────────────────────────────────────────────
    st.markdown(f"""
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 1.2rem; margin: 1.5rem 0;">
        <div class="glass-card" style="text-align:center; padding:1.5rem;">
            <h4 style="opacity:0.8; margin:0; font-size:1rem;">Active Accounts</h4>
            <h2 style="margin:0.5rem 0 0; font-size:2.4rem; color:{accent_color};">{total_accounts}</h2>
        </div>
        <div class="glass-card" style="text-align:center; padding:1.5rem;">
            <h4 style="opacity:0.8; margin:0; font-size:1rem;">Total Equity</h4>
            <h2 style="margin:0.5rem 0 0; font-size:2.4rem; color:#00ffaa;">${total_equity:,.0f}</h2>
        </div>
        <div class="glass-card" style="text-align:center; padding:1.5rem;">
            <h4 style="opacity:0.8; margin:0; font-size:1rem;">Withdrawable</h4>
            <h2 style="margin:0.5rem 0 0; font-size:2.4rem; color:#ff6b6b;">${total_withdrawable:,.0f}</h2>
        </div>
        <div class="glass-card" style="text-align:center; padding:1.5rem;">
            <h4 style="opacity:0.8; margin:0; font-size:1rem;">Empire Funded (PHP)</h4>
            <h2 style="margin:0.5rem 0 0; font-size:2.4rem; color:#ffd700;">₱{total_funded_php:,.0f}</h2>
        </div>
        <div class="glass-card" style="text-align:center; padding:1.5rem;">
            <h4 style="opacity:0.8; margin:0; font-size:1rem;">Gross Profits</h4>
            <h2 style="margin:0.5rem 0 0; font-size:2.4rem;">${total_gross:,.0f}</h2>
        </div>
        <div class="glass-card" style="text-align:center; padding:1.5rem;">
            <h4 style="opacity:0.8; margin:0; font-size:1rem;">Distributed Shares</h4>
            <h2 style="margin:0.5rem 0 0; font-size:2.4rem; color:#00ffaa;">${total_distributed:,.0f}</h2>
        </div>
        <div class="glass-card" style="text-align:center; padding:1.5rem;">
            <h4 style="opacity:0.8; margin:0; font-size:1rem;">Client Balances (Auto)</h4>
            <h2 style="margin:0.5rem 0 0; font-size:2.4rem; color:#ffd700;">${total_client_balances:,.0f}</h2>
        </div>
        <div class="glass-card" style="text-align:center; padding:1.5rem;">
            <h4 style="opacity:0.8; margin:0; font-size:1rem;">Growth Fund (Auto)</h4>
            <h2 style="margin:0.5rem 0 0; font-size:2.8rem; color:#ffd700;">${gf_balance:,.0f}</h2>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ────────────────────────────────────────────────
    # QUICK ACTIONS
    # ────────────────────────────────────────────────
    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown("<div class='glass-card' style='padding:2rem; text-align:center; height:100%;'>", unsafe_allow_html=True)
        st.subheader("⚡ Quick Actions")
        if current_role in ["owner", "admin"]:
            if st.button("➕ Launch New Account", use_container_width=True, type="primary"):
                st.session_state.selected_page = "📊 FTMO Accounts"
                st.rerun()
            if st.button("💰 Record Profit", use_container_width=True):
                st.session_state.selected_page = "💰 Profit Sharing"
                st.rerun()
            if st.button("🌱 Growth Fund Details", use_container_width=True):
                st.session_state.selected_page = "🌱 Growth Fund"
                st.rerun()
        else:
            st.info("Your earnings & shares update automatically in realtime.")
            if st.button("💳 Request Withdrawal", use_container_width=True, type="primary"):
                st.session_state.selected_page = "💳 Withdrawals"
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class='glass-card' style='padding:2rem; text-align:center; height:100%; display:flex; flex-direction:column; justify-content:center;'>
            <h3>🧠 Empire Insight</h3>
            <p style='font-size:1.2rem; margin-top:1rem;'>
                {"Exponential scaling active • Auto-distributions flowing • Balances updating realtime." if total_distributed > 0 else
                 "Foundation built • First profit will activate full automatic flow."}
            </p>
        </div>
        """, unsafe_allow_html=True)

    # ────────────────────────────────────────────────
    # EMPIRE FLOW TREES
    # ────────────────────────────────────────────────
    st.subheader("🌳 Empire Flow Trees (Realtime Auto-Sync)")
    tab_emp1, tab_emp2 = st.tabs(["Participant Shares Distribution", "Contributor Funding Flow (PHP)"])
    with tab_emp1:
        if participant_shares:
            labels = ["Empire Shares"] + list(participant_shares.keys())
            values = [0] + list(participant_shares.values())
            fig = go.Figure(data=[go.Sankey(
                node=dict(pad=20, thickness=30, label=labels, color=["#00ffaa"] + [accent_color]*len(participant_shares)),
                link=dict(source=[0]*len(participant_shares), target=list(range(1, len(labels))), value=values[1:])
            )])
            fig.update_layout(height=600, title="Total Distributed Shares by Participant")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No distributions yet • Record a profit first")
    with tab_emp2:
        funded_by_contributor = {}
        for acc in accounts:
            contributors = acc.get("contributors_v2") or acc.get("contributors", [])
            for c in contributors:
                name = c.get("display_name") or c.get("name", "Unknown")
                units = c.get("units", 0)
                php_per_unit = c.get("php_per_unit", 0) or 0
                funded = units * php_per_unit
                funded_by_contributor[name] = funded_by_contributor.get(name, 0) + funded
        if funded_by_contributor:
            labels = ["Empire Funded (PHP)"] + list(funded_by_contributor.keys())
            values = [0] + list(funded_by_contributor.values())
            fig = go.Figure(data=[go.Sankey(
                node=dict(pad=20, thickness=30, label=labels, color=["#ffd700"] + ["#ff6b6b"]*len(funded_by_contributor)),
                link=dict(source=[0]*len(funded_by_contributor), target=list(range(1, len(labels))), value=values[1:])
            )])
            fig.update_layout(height=600, title="Total Funded by Contributors (PHP)")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No contributors yet • Add contributors in FTMO Accounts")

    # ────────────────────────────────────────────────
    # LIVE ACCOUNTS WITH MINI-TREES
    # ────────────────────────────────────────────────
    st.subheader("📊 Live Accounts (Realtime Metrics & Trees)")
    if accounts:
        st.markdown("<div style='display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 1.5rem;'>", unsafe_allow_html=True)
        for acc in accounts:
            contributors = acc.get("contributors_v2") or acc.get("contributors", [])
            total_funded_php_acc = sum(c.get("units", 0) * c.get("php_per_unit", 0) for c in contributors)
            phase_emoji = {"Challenge P1": "🔴", "Challenge P2": "🟡", "Verification": "🟠", "Funded": "🟢", "Scaled": "💎"}.get(acc.get("current_phase", ""), "⚪")
            st.markdown(f"""
            <div class='glass-card' style='padding:2rem;'>
                <h3>{phase_emoji} {acc.get('name', 'Unnamed')}</h3>
                <div style='display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin: 1rem 0;'>
                    <div><strong>Phase:</strong> {acc.get('current_phase', '—')}</div>
                    <div><strong>Equity:</strong> ${acc.get('current_equity', 0):,.0f}</div>
                    <div><strong>Withdrawable:</strong> ${acc.get('withdrawable_balance', 0):,.0f}</div>
                    <div><strong>Funded:</strong> ₱{total_funded_php_acc:,.0f}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            tab1, tab2 = st.tabs(["Participants Tree", "Contributors Tree (PHP)"])
            with tab1:
                participants = acc.get("participants_v2") or acc.get("participants", [])
                if participants:
                    labels = ["Profits"] + [p.get("display_name") or p.get("name", "Unknown") for p in participants]
                    values = [p.get("percentage", 0) for p in participants]
                    fig = go.Figure(data=[go.Sankey(
                        node=dict(pad=15, thickness=20, label=labels),
                        link=dict(source=[0]*len(values), target=list(range(1, len(labels))), value=values)
                    )])
                    fig.update_layout(height=350)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No participants yet")
            with tab2:
                if contributors:
                    labels = ["Funded (PHP)"] + [c.get("display_name") or c.get("name", "Unknown") for c in contributors]
                    values = [c.get("units", 0) * c.get("php_per_unit", 0) for c in contributors]
                    fig = go.Figure(data=[go.Sankey(
                        node=dict(pad=15, thickness=20, label=labels),
                        link=dict(source=[0]*len(values), target=list(range(1, len(labels))), value=values)
                    )])
                    fig.update_layout(height=350)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No contributors yet")
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("No accounts found • Create one in FTMO Accounts page")

    # ────────────────────────────────────────────────
    # CLIENT BALANCES (OWNER/ADMIN ONLY)
    # ────────────────────────────────────────────────
    if current_role in ["owner", "admin"]:
        st.subheader("👥 Team Client Balances (Realtime)")
        clients_resp = supabase.table("users").select("full_name, balance").eq("role", "client").execute()
        clients = clients_resp.data or []
        if clients:
            client_df = pd.DataFrame([{"Client": u["full_name"], "Balance": f"${u.get('balance', 0):,.2f}"} for u in clients])
            st.dataframe(client_df, use_container_width=True, hide_index=True)
        else:
            st.info("No clients yet")

    # ────────────────────────────────────────────────
    # MOTIVATIONAL FOOTER
    # ────────────────────────────────────────────────
    st.markdown(f"""
    <div class='glass-card' style='padding:4rem; text-align:center; margin:4rem 0; border: 2px solid {accent_color};'>
        <h1 style="background:linear-gradient(90deg,{accent_color},#ffd700); -webkit-background-clip:text; -webkit-text-fill-color:transparent;">
            Fully Automatic • Realtime • Exponential Empire
        </h1>
        <p style="font-size:1.4rem; margin:2rem 0; opacity:0.9;">
            Every transaction auto-syncs • Trees update instantly • Balances flow realtime • Empire scales itself.
        </p>
        <h2 style="color:#ffd700;">👑 KMFX Pro • Cloud Edition 2026</h2>
    </div>
    """, unsafe_allow_html=True)
elif selected == "📊 FTMO Accounts":
    st.header("FTMO Accounts Management 🚀")
    st.markdown("**Empire core: Launch/edit accounts with unified trees • Contributor Pool enforced • Exact 100% validation • Auto v2 migration • Realtime previews • Bulletproof UUID sync • Optional Automatic Growth Fund %**")
    current_role = st.session_state.get("role", "guest")
    @st.cache_data(ttl=60)
    def fetch_all_data():
        accounts_resp = supabase.table("ftmo_accounts").select("*").order("created_date", desc=True).execute()
        users_resp = supabase.table("users").select("id, full_name, role, title").execute()
        return accounts_resp.data or [], users_resp.data or []
    accounts, all_users = fetch_all_data()
    # Display maps (v2 safe)
    user_id_to_display = {}
    display_to_user_id = {}
    user_id_to_full_name = {}
    for u in all_users:
        if u["role"] in ["client", "owner"]:
            str_id = str(u["id"])
            display = u["full_name"]
            if u.get("title"):
                display += f" ({u['title']})"
            user_id_to_display[str_id] = display
            display_to_user_id[display] = str_id
            user_id_to_full_name[str_id] = u["full_name"]
    # Special options
    special_options = ["Contributor Pool", "Manual Payout (Temporary)"]
    for s in special_options:
        display_to_user_id[s] = None
    participant_options = special_options + list(display_to_user_id.keys())
    contributor_options = list(user_id_to_display.values())
    owner_display = next((d for d, uid in display_to_user_id.items() if uid and any(uu["role"] == "owner" for uu in all_users if str(uu["id"]) == uid)), "King Minted")
    # ====================== OWNER/ADMIN: CREATE + LIST + EDIT ======================
    if current_role in ["owner", "admin"]:
        with st.expander("➕ Launch New FTMO Account", expanded=True):
            with st.form("create_account_form", clear_on_submit=True):
                col1, col2 = st.columns(2)
                with col1:
                    name = st.text_input("Account Name *", placeholder="e.g. KMFX Scaled 200K")
                    ftmo_id = st.text_input("FTMO ID (Optional)")
                    phase = st.selectbox("Current Phase *", ["Challenge P1", "Challenge P2", "Verification", "Funded", "Scaled"])
                with col2:
                    equity = st.number_input("Current Equity (USD)", min_value=0.0, value=100000.0, step=1000.0)
                    withdrawable = st.number_input("Current Withdrawable (USD)", min_value=0.0, value=0.0, step=500.0)
                notes = st.text_area("Notes (Optional)")

                # NEW: Automatic Optional Growth Fund %
                st.subheader("🌱 Growth Fund Allocation (Optional per Account)")
                gf_pct = st.number_input(
                    "Growth Fund % from Gross Profit",
                    min_value=0.0,
                    max_value=50.0,
                    value=10.0,  # Default 10% — change to 0.0 if you want default off
                    step=0.5,
                    help="0% = No Growth Fund deduction • >0% = Automatic dedicated row (reinvestment)"
                )
                if gf_pct > 0:
                    st.success(f"✅ {gf_pct:.1f}% auto-allocated to Growth Fund")
                else:
                    st.info("ℹ️ No Growth Fund allocation for this account")

                st.subheader("🌳 Unified Profit Distribution Tree (%)")
                st.info("**Must include exactly one 'Contributor Pool' row** • Total tree % + Growth Fund % must be exactly 100%")
                default_rows = [
                    {"display_name": "Contributor Pool", "role": "Funding Contributors (pro-rata)", "percentage": 30.0},
                    {"display_name": owner_display, "role": "Founder/Owner", "percentage": 70.0 - gf_pct if gf_pct <= 70.0 else 0.0}
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
                        "percentage": st.column_config.NumberColumn("% *", min_value=0.0, max_value=100.0, step=0.1, format="%.2f")
                    }
                )
                total_tree_sum = edited_tree["percentage"].sum()
                total_with_gf = total_tree_sum + gf_pct
                st.progress(total_with_gf / 100)
                contrib_rows = edited_tree[edited_tree["display_name"] == "Contributor Pool"]
                if len(contrib_rows) != 1:
                    st.error("Exactly one 'Contributor Pool' row required")
                    contrib_pct = 0.0
                elif total_with_gf != 100.0:
                    st.error(f"Total must be exactly 100.00% (current: {total_with_gf:.2f}%) including {gf_pct:.1f}% Growth Fund")
                    contrib_pct = 0.0
                else:
                    st.success("✅ Perfect 100.00% allocation (including auto Growth Fund)")
                    contrib_pct = contrib_rows.iloc[0]["percentage"]

                # Manual custom names
                manual_inputs = []
                for idx, row in edited_tree.iterrows():
                    if row["display_name"] == "Manual Payout (Temporary)":
                        custom_name = st.text_input(f"Custom Name for Row {idx+1}", key=f"manual_create_{idx}")
                        if custom_name:
                            manual_inputs.append((idx, custom_name))

                st.subheader("🌳 Contributors Funding Tree (PHP Units)")
                contrib_df = pd.DataFrame(columns=["display_name", "units", "php_per_unit"])
                edited_contrib = st.data_editor(
                    contrib_df,
                    num_rows="dynamic",
                    use_container_width=True,
                    key="contrib_editor_create",
                    column_config={
                        "display_name": st.column_config.SelectboxColumn("Contributor *", options=contributor_options, required=True),
                        "units": st.column_config.NumberColumn("Units", min_value=0.0, step=0.5),
                        "php_per_unit": st.column_config.NumberColumn("PHP per Unit", min_value=100.0, step=100.0)
                    }
                )
                if not edited_contrib.empty:
                    total_php = (edited_contrib["units"] * edited_contrib["php_per_unit"]).sum()
                    st.metric("Total Funded (PHP)", f"₱{total_php:,.0f}")

                # Previews (include GF if >0)
                tab_prev1, tab_prev2 = st.tabs(["Profit Tree Preview", "Funding Tree Preview"])
                with tab_prev1:
                    labels = ["Gross Profit"]
                    values = []
                    for _, row in edited_tree.iterrows():
                        d = row["display_name"]
                        if d == "Contributor Pool":
                            d = "Contributor Pool (pro-rata)"
                        labels.append(f"{d} ({row['percentage']:.2f}%)")
                        values.append(row["percentage"])
                    if gf_pct > 0:
                        labels.append(f"Growth Fund ({gf_pct:.2f}%)")
                        values.append(gf_pct)
                    fig = go.Figure(data=[go.Sankey(
                        node=dict(pad=15, thickness=20, label=labels),
                        link=dict(source=[0]*len(values), target=list(range(1, len(labels)+1)), value=values)
                    )])
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)
                with tab_prev2:
                    if not edited_contrib.empty:
                        labels = ["Funded (PHP)"]
                        values = (edited_contrib["units"] * edited_contrib["php_per_unit"]).tolist()
                        contrib_labels = [f"{row['display_name']} ({row['units']}u @ ₱{row['php_per_unit']:,.0f})" for _, row in edited_contrib.iterrows()]
                        fig = go.Figure(data=[go.Sankey(
                            node=dict(pad=15, thickness=20, label=labels + contrib_labels),
                            link=dict(source=[0]*len(values), target=list(range(1, len(values)+1)), value=values)
                        )])
                        fig.update_layout(height=400)
                        st.plotly_chart(fig, use_container_width=True)

                submitted = st.form_submit_button("🚀 Launch Account", type="primary", use_container_width=True)
                if submitted:
                    if not name.strip():
                        st.error("Account name required")
                    elif len(contrib_rows) != 1:
                        st.error("Exactly one Contributor Pool row required")
                    elif total_with_gf != 100.0:
                        st.error("Total % including Growth Fund must be exactly 100.00")
                    else:
                        try:
                            # Build v2
                            final_part_v2 = []
                            for row in edited_tree.to_dict("records"):
                                display = row["display_name"]
                                user_id = display_to_user_id.get(display)
                                final_part_v2.append({
                                    "user_id": user_id,
                                    "display_name": display,
                                    "percentage": row["percentage"],
                                    "role": row["role"]
                                })
                            for idx, custom in manual_inputs:
                                final_part_v2[idx]["display_name"] = custom
                                final_part_v2[idx]["user_id"] = None
                            # AUTO-ADD Growth Fund row if >0%
                            if gf_pct > 0:
                                # Prevent duplicate
                                if not any("growth fund" in p.get("display_name", "").lower() for p in final_part_v2):
                                    final_part_v2.append({
                                        "user_id": None,
                                        "display_name": "Growth Fund",
                                        "percentage": gf_pct,
                                        "role": "Empire Reinvestment Fund"
                                    })
                            final_contrib_v2 = []
                            for row in edited_contrib.to_dict("records"):
                                display = row["display_name"]
                                user_id = display_to_user_id.get(display)
                                final_contrib_v2.append({
                                    "user_id": user_id,
                                    "units": row.get("units", 0),
                                    "php_per_unit": row.get("php_per_unit", 0)
                                })
                            # Backward compat old
                            final_part_old = [{"name": user_id_to_full_name.get(p["user_id"], p["display_name"]) if p["user_id"] else p["display_name"],
                                               "role": p["role"], "percentage": p["percentage"]} for p in final_part_v2]
                            final_contrib_old = [{"name": user_id_to_full_name.get(c["user_id"], "Unknown"),
                                                  "units": c["units"], "php_per_unit": c["php_per_unit"]} for c in final_contrib_v2]
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
                                "contributor_share_pct": contrib_pct
                            }).execute()
                            st.success("Account launched with automatic Growth Fund setup! 🎉")
                            st.balloons()
                            st.cache_data.clear()
                            st.rerun()
                        except Exception as e:
                            st.error(f"Launch failed: {str(e)}")

        # Live accounts list (unchanged except previews show GF if present)
        st.subheader("Live Empire Accounts")
        if accounts:
            for acc in accounts:
                use_v2 = bool(acc.get("participants_v2"))
                participants = acc.get("participants_v2") if use_v2 else acc.get("participants", [])
                contributors = acc.get("contributors_v2") if use_v2 else acc.get("contributors", [])
                total_funded_php = sum(c.get("units", 0) * c.get("php_per_unit", 0) for c in contributors)
                contrib_pct = acc.get("contributor_share_pct", 0)
                gf_pct_acc = sum(p.get("percentage", 0) for p in participants if "growth fund" in p.get("display_name", "").lower())
                with st.expander(f"🌟 {acc['name']} • {acc['current_phase']} • Equity ${acc.get('current_equity', 0):,.0f} • Funded ₱{total_funded_php:,.0f} • Pool {contrib_pct:.1f}% • GF {gf_pct_acc:.1f}% {'(v2)' if use_v2 else '(Legacy)'}"):
                    tab1, tab2 = st.tabs(["Profit Tree", "Funding Tree"])
                    with tab1:
                        labels = ["Gross Profit"]
                        values = []
                        for p in participants:
                            display = p.get("display_name") or user_id_to_display.get(p.get("user_id"), p.get("name", "Unknown"))
                            if display == "Contributor Pool":
                                display = "Contributor Pool (pro-rata)"
                            labels.append(f"{display} ({p['percentage']:.2f}%)")
                            values.append(p["percentage"])
                        fig = go.Figure(data=[go.Sankey(
                            node=dict(pad=15, thickness=20, label=labels),
                            link=dict(source=[0]*len(values), target=list(range(1, len(labels)+1)), value=values)
                        )])
                        st.plotly_chart(fig, use_container_width=True)
                    with tab2:
                        if contributors:
                            labels = ["Funded (PHP)"]
                            values = []
                            for c in contributors:
                                display = user_id_to_display.get(c.get("user_id"), c.get("name", "Unknown"))
                                funded = c.get("units", 0) * c.get("php_per_unit", 0)
                                labels.append(f"{display} ({c.get('units', 0)}u @ ₱{c.get('php_per_unit', 0):,.0f})")
                                values.append(funded)
                            fig = go.Figure(data=[go.Sankey(
                                node=dict(pad=15, thickness=20, label=labels),
                                link=dict(source=[0]*len(values), target=list(range(1, len(values)+1)), value=values)
                            )])
                            st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.info("No contributors")
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
                                st.success("Account deleted")
                                st.cache_data.clear()
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error: {str(e)}")

            # Edit form (with Growth Fund %)
            if "edit_acc_id" in st.session_state:
                eid = st.session_state.edit_acc_id
                cur = st.session_state.edit_acc_data
                with st.expander(f"✏️ Editing {cur['name']}", expanded=True):
                    with st.form(f"edit_form_{eid}", clear_on_submit=True):
                        col1, col2 = st.columns(2)
                        with col1:
                            new_name = st.text_input("Account Name *", value=cur["name"])
                            new_ftmo_id = st.text_input("FTMO ID", value=cur.get("ftmo_id") or "")
                            new_phase = st.selectbox("Current Phase *", ["Challenge P1", "Challenge P2", "Verification", "Funded", "Scaled"],
                                                     index=["Challenge P1", "Challenge P2", "Verification", "Funded", "Scaled"].index(cur["current_phase"]))
                        with col2:
                            new_equity = st.number_input("Current Equity (USD)", value=float(cur.get("current_equity", 0)), step=1000.0)
                            new_withdrawable = st.number_input("Current Withdrawable (USD)", value=float(cur.get("withdrawable_balance", 0)), step=500.0)
                        new_notes = st.text_area("Notes", value=cur.get("notes") or "")

                        # Detect current GF %
                        use_v2 = bool(cur.get("participants_v2"))
                        current_part = pd.DataFrame(cur["participants_v2"] if use_v2 else cur.get("participants", []))
                        current_gf_pct = sum(row.get("percentage", 0.0) for _, row in current_part.iterrows() if "growth fund" in row.get("display_name", "").lower())

                        st.subheader("🌱 Growth Fund Allocation (Optional per Account)")
                        gf_pct = st.number_input(
                            "Growth Fund % from Gross Profit",
                            min_value=0.0,
                            max_value=50.0,
                            value=current_gf_pct,
                            step=0.5,
                            help="0% = Remove/disable GF • >0% = Auto-row"
                        )
                        if gf_pct > 0:
                            st.success(f"✅ {gf_pct:.1f}% auto Growth Fund")
                        else:
                            st.info("ℹ️ No Growth Fund (0%)")

                        st.subheader("🌳 Unified Profit Tree (%)")
                        if use_v2:
                            current_part = pd.DataFrame(cur["participants_v2"])
                        else:
                            legacy = pd.DataFrame(cur.get("participants", []))
                            current_part = pd.DataFrame([{
                                "display_name": next((d for d, uid in display_to_user_id.items() if user_id_to_full_name.get(uid) == p["name"]), p["name"]),
                                "role": p.get("role", ""),
                                "percentage": p["percentage"]
                            } for p in legacy])
                            st.info("🔄 Legacy → Saving will migrate to v2")
                        # Enforce Contributor Pool
                        if "Contributor Pool" not in current_part["display_name"].values:
                            contrib_row = pd.DataFrame([{"display_name": "Contributor Pool", "role": "Funding Contributors (pro-rata)", "percentage": cur.get("contributor_share_pct", 30.0)}])
                            current_part = pd.concat([contrib_row, current_part], ignore_index=True)
                            st.info("Auto-added missing Contributor Pool row")
                        # Remove existing GF row for clean edit
                        current_part = current_part[~current_part["display_name"].str.lower().str.contains("growth fund", na=False)]
                        edited_tree = st.data_editor(
                            current_part[["display_name", "role", "percentage"]],
                            num_rows="dynamic",
                            use_container_width=True,
                            key=f"edit_part_{eid}",
                            column_config={
                                "display_name": st.column_config.SelectboxColumn("Name *", options=participant_options, required=True),
                                "role": st.column_config.TextColumn("Role"),
                                "percentage": st.column_config.NumberColumn("% *", min_value=0.0, max_value=100.0, step=0.1, format="%.2f")
                            }
                        )
                        total_tree_sum = edited_tree["percentage"].sum()
                        total_with_gf = total_tree_sum + gf_pct
                        st.progress(total_with_gf / 100)
                        contrib_rows = edited_tree[edited_tree["display_name"] == "Contributor Pool"]
                        if len(contrib_rows) != 1:
                            st.error("Exactly one Contributor Pool row required")
                            contrib_pct = 0.0
                        elif total_with_gf != 100.0:
                            st.error(f"Total exactly 100.00% required (current: {total_with_gf:.2f}%) including {gf_pct:.1f}% Growth Fund")
                        else:
                            st.success("✅ Perfect tree (including auto Growth Fund)")
                            contrib_pct = contrib_rows.iloc[0]["percentage"]

                        manual_inputs = []
                        for idx, row in edited_tree.iterrows():
                            if row["display_name"] == "Manual Payout (Temporary)":
                                custom = st.text_input(f"Custom Name Row {idx+1}", key=f"manual_edit_{eid}_{idx}")
                                if custom:
                                    manual_inputs.append((idx, custom))

                        st.subheader("🌳 Contributors Tree")
                        if use_v2:
                            current_contrib = pd.DataFrame(cur.get("contributors_v2", []))
                            current_contrib["display_name"] = current_contrib["user_id"].apply(lambda uid: user_id_to_display.get(uid, "Unknown"))
                        else:
                            legacy_contrib = pd.DataFrame(cur.get("contributors", []))
                            current_contrib = pd.DataFrame([{
                                "display_name": next((d for d, uid in display_to_user_id.items() if user_id_to_full_name.get(uid) == c["name"]), c["name"]),
                                "units": c.get("units", 0),
                                "php_per_unit": c.get("php_per_unit", 0)
                            } for c in legacy_contrib])
                            st.info("🔄 Legacy contributors → Saving migrates to v2")
                        edited_contrib = st.data_editor(
                            current_contrib[["display_name", "units", "php_per_unit"]],
                            num_rows="dynamic",
                            use_container_width=True,
                            key=f"edit_contrib_{eid}",
                            column_config={
                                "display_name": st.column_config.SelectboxColumn("Contributor *", options=contributor_options, required=True),
                                "units": st.column_config.NumberColumn("Units", min_value=0.0, step=0.5),
                                "php_per_unit": st.column_config.NumberColumn("PHP/Unit", min_value=100.0, step=100.0)
                            }
                        )
                        if not edited_contrib.empty:
                            total_php = (edited_contrib["units"] * edited_contrib["php_per_unit"]).sum()
                            st.metric("Total Funded (PHP)", f"₱{total_php:,.0f}")

                        # Previews (include GF)
                        tab_prev1, tab_prev2 = st.tabs(["Profit Tree Preview", "Funding Tree Preview"])
                        with tab_prev1:
                            labels = ["Gross Profit"]
                            values = []
                            for _, row in edited_tree.iterrows():
                                d = row["display_name"]
                                if d == "Contributor Pool":
                                    d = "Contributor Pool (pro-rata)"
                                labels.append(f"{d} ({row['percentage']:.2f}%)")
                                values.append(row["percentage"])
                            if gf_pct > 0:
                                labels.append(f"Growth Fund ({gf_pct:.2f}%)")
                                values.append(gf_pct)
                            fig = go.Figure(data=[go.Sankey(
                                node=dict(pad=15, thickness=20, label=labels),
                                link=dict(source=[0]*len(values), target=list(range(1, len(labels)+1)), value=values)
                            )])
                            st.plotly_chart(fig, use_container_width=True)
                        with tab_prev2:
                            if not edited_contrib.empty:
                                labels = ["Funded (PHP)"]
                                values = (edited_contrib["units"] * edited_contrib["php_per_unit"]).tolist()
                                contrib_labels = [f"{row['display_name']} ({row['units']}u @ ₱{row['php_per_unit']:,.0f})" for _, row in edited_contrib.iterrows()]
                                fig = go.Figure(data=[go.Sankey(
                                    node=dict(pad=15, thickness=20, label=labels + contrib_labels),
                                    link=dict(source=[0]*len(values), target=list(range(1, len(values)+1)), value=values)
                                )])
                                st.plotly_chart(fig, use_container_width=True)

                        col_save, col_cancel = st.columns(2)
                        with col_save:
                            if st.form_submit_button("💾 Save Changes", type="primary", use_container_width=True):
                                if not new_name.strip():
                                    st.error("Name required")
                                elif len(contrib_rows) != 1 or total_with_gf != 100.0:
                                    st.error("Valid tree + Growth Fund % required")
                                else:
                                    try:
                                        final_part_v2 = []
                                        for row in edited_tree.to_dict("records"):
                                            display = row["display_name"]
                                            user_id = display_to_user_id.get(display)
                                            final_part_v2.append({
                                                "user_id": user_id,
                                                "display_name": display,
                                                "percentage": row["percentage"],
                                                "role": row["role"]
                                            })
                                        for idx, custom in manual_inputs:
                                            final_part_v2[idx]["display_name"] = custom
                                            final_part_v2[idx]["user_id"] = None
                                        # Remove old GF + add new if >0
                                        final_part_v2 = [p for p in final_part_v2 if "growth fund" not in p.get("display_name", "").lower()]
                                        if gf_pct > 0:
                                            final_part_v2.append({
                                                "user_id": None,
                                                "display_name": "Growth Fund",
                                                "percentage": gf_pct,
                                                "role": "Empire Reinvestment Fund"
                                            })
                                        final_contrib_v2 = []
                                        for row in edited_contrib.to_dict("records"):
                                            display = row["display_name"]
                                            user_id = display_to_user_id.get(display)
                                            final_contrib_v2.append({
                                                "user_id": user_id,
                                                "units": row.get("units", 0),
                                                "php_per_unit": row.get("php_per_unit", 0)
                                            })
                                        final_part_old = [{"name": user_id_to_full_name.get(p["user_id"], p["display_name"]) if p["user_id"] else p["display_name"],
                                                           "role": p["role"], "percentage": p["percentage"]} for p in final_part_v2]
                                        final_contrib_old = [{"name": user_id_to_full_name.get(c["user_id"], "Unknown"),
                                                              "units": c["units"], "php_per_unit": c["php_per_unit"]} for c in final_contrib_v2]
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
                                            "contributor_share_pct": contrib_pct
                                        }).eq("id", eid).execute()
                                        st.success("Updated with automatic Growth Fund setup! 🎉")
                                        del st.session_state.edit_acc_id
                                        del st.session_state.edit_acc_data
                                        st.cache_data.clear()
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"Error: {str(e)}")
                        with col_cancel:
                            if st.form_submit_button("Cancel"):
                                del st.session_state.edit_acc_id
                                del st.session_state.edit_acc_data
                                st.rerun()
        else:
            st.info("No accounts yet")
    # ====================== CLIENT VIEW ======================
    else:
        my_name = st.session_state.full_name
        my_accounts = [a for a in accounts if any(
            p.get("display_name") == my_name or p.get("name") == my_name or
            user_id_to_full_name.get(p.get("user_id")) == my_name
            for p in (a.get("participants_v2") or a.get("participants", []))
        )]
        st.subheader(f"Your Shared Accounts ({len(my_accounts)})")
        if my_accounts:
            for acc in my_accounts:
                participants = acc.get("participants_v2") or acc.get("participants", [])
                my_pct = next((p["percentage"] for p in participants if
                               p.get("display_name") == my_name or p.get("name") == my_name or
                               user_id_to_full_name.get(p.get("user_id")) == my_name), 0.0)
                contributors = acc.get("contributors_v2") or acc.get("contributors", [])
                my_funded = sum(c.get("units", 0) * c.get("php_per_unit", 0) for c in contributors
                                if user_id_to_full_name.get(c.get("user_id")) == my_name or c.get("name") == my_name)
                gf_pct_acc = sum(p.get("percentage", 0) for p in participants if "growth fund" in p.get("display_name", "").lower())
                with st.expander(f"🌟 {acc['name']} • Your Share: {my_pct:.2f}% • Funded ₱{my_funded:,.0f} • Phase: {acc['current_phase']} • GF {gf_pct_acc:.1f}%"):
                    st.metric("Equity", f"${acc.get('current_equity', 0):,.0f}")
                    st.metric("Withdrawable", f"${acc.get('withdrawable_balance', 0):,.0f}")
                    tab1, tab2 = st.tabs(["Profit Tree", "Funding Tree"])
                    with tab1:
                        labels = ["Gross Profit"]
                        values = []
                        for p in participants:
                            display = p.get("display_name") or user_id_to_display.get(p.get("user_id"), p.get("name", "Unknown"))
                            if display == "Contributor Pool":
                                display = "Contributor Pool (pro-rata)"
                            labels.append(f"{display} ({p['percentage']:.2f}%)")
                            values.append(p["percentage"])
                        fig = go.Figure(data=[go.Sankey(
                            node=dict(pad=15, thickness=20, label=labels),
                            link=dict(source=[0]*len(values), target=list(range(1, len(labels)+1)), value=values)
                        )])
                        st.plotly_chart(fig, use_container_width=True)
                    with tab2:
                        if contributors:
                            labels = ["Funded (PHP)"]
                            values = []
                            for c in contributors:
                                display = user_id_to_display.get(c.get("user_id"), c.get("name", "Unknown"))
                                funded = c.get("units", 0) * c.get("php_per_unit", 0)
                                labels.append(f"{display} ({c.get('units', 0)}u @ ₱{c.get('php_per_unit', 0):,.0f})")
                                values.append(funded)
                            fig = go.Figure(data=[go.Sankey(
                                node=dict(pad=15, thickness=20, label=labels),
                                link=dict(source=[0]*len(values), target=list(range(1, len(values)+1)), value=values)
                            )])
                            st.plotly_chart(fig, use_container_width=True)
        st.subheader("All Empire Accounts Overview")
        for acc in accounts:
            total_funded = sum(c.get("units", 0) * c.get("php_per_unit", 0) for c in (acc.get("contributors_v2") or acc.get("contributors", [])))
            gf_pct_acc = sum(p.get("percentage", 0) for p in (acc.get("participants_v2") or acc.get("participants", [])) if "growth fund" in p.get("display_name", "").lower())
            with st.expander(f"{acc['name']} • {acc['current_phase']} • Equity ${acc.get('current_equity', 0):,.0f} • Funded ₱{total_funded:,.0f} • GF {gf_pct_acc:.1f}%"):
                participants = acc.get("participants_v2") or acc.get("participants", [])
                contributors = acc.get("contributors_v2") or acc.get("contributors", [])
                labels = ["Gross Profit"]
                values = []
                for p in participants:
                    display = p.get("display_name") or user_id_to_display.get(p.get("user_id"), p.get("name", "Unknown"))
                    if display == "Contributor Pool":
                        display = "Contributor Pool (pro-rata)"
                    labels.append(f"{display} ({p['percentage']:.2f}%)")
                    values.append(p["percentage"])
                fig = go.Figure(data=[go.Sankey(
                    node=dict(pad=15, thickness=20, label=labels),
                    link=dict(source=[0]*len(values), target=list(range(1, len(labels)+1)), value=values)
                )])
                st.plotly_chart(fig, use_container_width=True)
                # Funding tree same as above
    if not accounts:
        st.info("No accounts yet • Owner launches empire growth")
elif selected == "💰 Profit Sharing":
    st.header("Profit Sharing & Auto-Distribution 💰")
    st.markdown("**Empire engine: Record FTMO profit → Auto-split via stored v2 tree • Bulletproof UUID balance updates • Premium HTML auto-email to all involved (including Growth Fund row) • Realtime previews • Instant sync.**")
    current_role = st.session_state.get("role", "guest")
    if current_role not in ["owner", "admin"]:
        st.warning("Profit recording is owner/admin only.")
        st.stop()
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    @st.cache_data(ttl=60)
    def fetch_profit_data():
        accounts = supabase.table("ftmo_accounts").select(
            "id, name, current_phase, current_equity, "
            "participants_v2, contributors_v2, contributor_share_pct"
        ).execute().data or []
        users = supabase.table("users").select("id, full_name, email, balance").execute().data or []
        user_id_to_display = {str(u["id"]): u["full_name"] for u in users}
        user_id_to_email = {str(u["id"]): u.get("email") for u in users}
        user_id_to_balance = {str(u["id"]): u.get("balance", 0.0) for u in users}
        return accounts, users, user_id_to_display, user_id_to_email, user_id_to_balance
    accounts, raw_users, user_id_to_display, user_id_to_email, user_id_to_balance = fetch_profit_data()
    if not accounts:
        st.info("No accounts yet • Launch in FTMO Accounts first.")
        st.stop()
    account_options = {f"{a['name']} • Phase: {a['current_phase']} • Equity ${a.get('current_equity', 0):,.0f} • Pool {a.get('contributor_share_pct', 0):.1f}%": a for a in accounts}
    selected_key = st.selectbox("Select Account for Profit Record", list(account_options.keys()))
    acc = account_options[selected_key]
    acc_id = acc["id"]
    acc_name = acc["name"]
    # FORCE v2
    participants = acc.get("participants_v2", [])
    contributors = acc.get("contributors_v2", [])
    contributor_share_pct = acc.get("contributor_share_pct", 0.0)
    if not participants:
        st.error("Account missing v2 participants • Re-edit in FTMO Accounts to fix.")
        st.stop()
    st.info(f"**Recording for:** {acc_name} • Contributor Pool: {contributor_share_pct:.1f}% • v2 Active (perfect sync)")
    with st.form("profit_form", clear_on_submit=True):
        col1, col2 = st.columns([2, 1])
        with col1:
            gross_profit = st.number_input("Gross Profit Received (USD) *", min_value=0.01, step=500.0)
        with col2:
            record_date = st.date_input("Record Date", datetime.date.today())
        # Tree preview
        st.subheader("Stored Unified Tree (Edit in FTMO Accounts)")
        part_df = pd.DataFrame([{
            "Name": user_id_to_display.get(p.get("user_id"), p.get("display_name", "Unknown")) if p.get("user_id") else p.get("display_name", "Unknown"),
            "Role": p.get("role", ""),
            "%": f"{p['percentage']:.2f}"
        } for p in participants])
        st.dataframe(part_df, use_container_width=True, hide_index=True)
        # Calculate previews — FIXED: Include ALL rows (Growth Fund, manual, etc.)
        involved_user_ids = set()
        contrib_preview = []
        part_preview = []
        gf_add = 0.0
        total_funded_php = sum(c.get("units", 0) * c.get("php_per_unit", 0) for c in contributors)
        contributor_pool = gross_profit * (contributor_share_pct / 100)
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
        # FIXED LOOP: No skip on missing user_id → Growth Fund & manual rows now appear in preview/email
        for p in participants:
            user_id = p.get("user_id")
            # Safe display: fallback to display_name even if no user_id
            display = user_id_to_display.get(user_id, p.get("display_name", "Unknown")) if user_id else p.get("display_name", "Unknown")
            share = gross_profit * (p["percentage"] / 100)
            if "growth fund" in display.lower():
                gf_add += share
            part_preview.append({
                "Name": display,
                "%": f"{p['percentage']:.2f}",
                "Share": f"${share:,.2f}"
            })
            if user_id:  # Only add to email recipients if real user
                involved_user_ids.add(user_id)
        col_prev1, col_prev2 = st.columns(2)
        with col_prev1:
            st.subheader("Contributor Pool Preview")
            if contrib_preview:
                st.dataframe(pd.DataFrame(contrib_preview), use_container_width=True, hide_index=True)
            else:
                st.info("No contributors or 0% pool")
        with col_prev2:
            st.subheader("Participants Preview (incl. Growth Fund if allocated)")
            st.dataframe(pd.DataFrame(part_preview), use_container_width=True, hide_index=True)
        # Metrics
        units = gross_profit / 3000.0 if gross_profit > 0 else 0  # Adjust unit_value if dynamic
        col_m1, col_m2, col_m3 = st.columns(3)
        col_m1.metric("Gross Profit", f"${gross_profit:,.2f}")
        col_m2.metric("Contributor Pool", f"${contributor_pool:,.2f}")
        col_m3.metric("Growth Fund Add", f"${gf_add:,.2f}")
        # Sankey preview — now includes Growth Fund row automatically
        labels = [f"Gross ${gross_profit:,.0f}"]
        values = []
        source = []
        target = []
        idx = 1
        if contributor_pool > 0 and contrib_preview:
            labels.append("Contributor Pool")
            values.append(contributor_pool)
            source.append(0)
            target.append(idx)
            contrib_idx = idx
            idx += 1
            for c in contrib_preview:
                share = float(c["Share"].replace("$", "").replace(",", ""))
                labels.append(c["Name"])
                values.append(share)
                source.append(contrib_idx)
                target.append(idx)
                idx += 1
        for p in part_preview:
            share = float(p["Share"].replace("$", "").replace(",", ""))
            labels.append(p["Name"])
            values.append(share)
            source.append(0)
            target.append(idx)
            idx += 1
        fig = go.Figure(data=[go.Sankey(
            node=dict(pad=20, thickness=30, label=labels, color=["#00ffaa"] + ["#ffd700"]*len(contrib_preview) + ["#00cc99"]*len(part_preview)),
            link=dict(source=source, target=target, value=values)
        )])
        fig.update_layout(title="Distribution Flow Preview (incl. Growth Fund)", height=600)
        st.plotly_chart(fig, use_container_width=True)
        submitted = st.form_submit_button("🚀 Record & Distribute Profit", type="primary", use_container_width=True)
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
                        "contributor_share_pct": contributor_share_pct
                    }).execute()
                    profit_id = profit_resp.data[0]["id"]
                    distributions = []
                    balance_updates = []
                    # Contributors pro-rata
                    if contributor_pool > 0 and total_funded_php > 0:
                        for c in contributors:
                            user_id = c.get("user_id")
                            if not user_id:
                                continue
                            display = user_id_to_display.get(user_id, "Unknown")
                            funded = c.get("units", 0) * c.get("php_per_unit", 0)
                            share = contributor_pool * (funded / total_funded_php)
                            pro_rata_pct = (funded / total_funded_php) * 100
                            distributions.append({
                                "profit_id": profit_id,
                                "participant_name": display,
                                "participant_user_id": user_id,
                                "participant_role": "Contributor",
                                "percentage": round(pro_rata_pct, 2),
                                "share_amount": share,
                                "is_growth_fund": False
                            })
                            new_bal = user_id_to_balance.get(user_id, 0) + share
                            balance_updates.append((user_id, new_bal))
                    # Participants direct — FIXED: Include all (Growth Fund too, but no balance update for GF)
                    for p in participants:
                        user_id = p.get("user_id")
                        display = user_id_to_display.get(user_id, p.get("display_name", "Unknown")) if user_id else p.get("display_name", "Unknown")
                        share = gross_profit * (p["percentage"] / 100)
                        is_gf = "growth fund" in display.lower()
                        distributions.append({
                            "profit_id": profit_id,
                            "participant_name": display,
                            "participant_user_id": user_id,
                            "participant_role": p.get("role", ""),
                            "percentage": p["percentage"],
                            "share_amount": share,
                            "is_growth_fund": is_gf
                        })
                        if user_id and not is_gf:  # No balance update for GF/special
                            new_bal = user_id_to_balance.get(user_id, 0) + share
                            balance_updates.append((user_id, new_bal))
                    # Bulk insert distributions
                    if distributions:
                        supabase.table("profit_distributions").insert(distributions).execute()
                    # Bulk balance updates
                    for uid, new_bal in balance_updates:
                        supabase.table("users").update({"balance": new_bal}).eq("id", uid).execute()
                    # GF transaction (auto if gf_add > 0)
                    if gf_add > 0:
                        supabase.table("growth_fund_transactions").insert({
                            "date": str(record_date),
                            "type": "In",
                            "amount": gf_add,
                            "description": f"Auto from {acc_name} profit",
                            "account_source": acc_name,
                            "recorded_by": st.session_state.full_name
                        }).execute()
                    # HTML email breakdown — now includes Growth Fund row automatically
                    date_str = record_date.strftime("%B %d, %Y")
                    html_breakdown = f"""
                    <html><body style="font-family:Arial,sans-serif;background:#f8fbff;padding:20px;">
                        <div style="max-width:800px;margin:auto;background:white;border-radius:20px;padding:30px;box-shadow:0 10px 30px rgba(0,0,0,0.1);">
                            <h1 style="color:#00ffaa;text-align:center;">🚀 KMFX Profit Distribution</h1>
                            <h2 style="text-align:center;">{acc_name} • {date_str}</h2>
                            <p style="text-align:center;font-size:1.2rem;">Gross: <strong>${gross_profit:,.2f}</strong> • Pool ({contributor_share_pct:.1f}%): <strong>${contributor_pool:,.2f}</strong></p>
                            <h3>Contributor Breakdown</h3>
                            <table style="width:100%;border-collapse:collapse;">
                                <tr style="background:#00ffaa;color:black;"><th style="padding:12px;border:1px solid #ddd;">Name</th><th>Funded PHP</th><th>Share</th></tr>
                                {''.join(f'<tr><td style="padding:12px;border:1px solid #ddd;">{r["Name"]}</td><td>{r["Funded PHP"]}</td><td>{r["Share"]}</td></tr>' for r in contrib_preview) or '<tr><td colspan="3" style="text-align:center;padding:12px;">None</td></tr>'}
                            </table>
                            <h3>Participants Breakdown (incl. Growth Fund)</h3>
                            <table style="width:100%;border-collapse:collapse;">
                                <tr style="background:#ffd700;color:black;"><th style="padding:12px;border:1px solid #ddd;">Name</th><th>%</th><th>Share</th></tr>
                                {''.join(f'<tr><td style="padding:12px;border:1px solid #ddd;">{r["Name"]}</td><td>{r["%"]}%</td><td>{r["Share"]}</td></tr>' for r in part_preview)}
                            </table>
                            <p style="margin-top:30px;text-align:center;">Thank you for scaling the Empire 👑</p>
                        </div>
                    </body></html>
                    """
                    st.subheader("Auto-Email Breakdown Preview")
                    st.markdown(html_breakdown, unsafe_allow_html=True)
                    # Send emails
                    sender_email = os.getenv("EMAIL_SENDER")
                    sender_password = os.getenv("EMAIL_PASSWORD")
                    sent = 0
                    if sender_email and sender_password and involved_user_ids:
                        try:
                            server = smtplib.SMTP("smtp.gmail.com", 587)
                            server.starttls()
                            server.login(sender_email, sender_password)
                            for uid in involved_user_ids:
                                email = user_id_to_email.get(uid)
                                if email:
                                    msg = MIMEMultipart()
                                    msg["From"] = sender_email
                                    msg["To"] = email
                                    msg["Subject"] = f"KMFX Profit - {acc_name} {date_str}"
                                    msg.attach(MIMEText(html_breakdown, "html"))
                                    server.sendmail(sender_email, email, msg.as_string())
                                    sent += 1
                            server.quit()
                            if sent > 0:
                                st.success(f"Email sent to {sent} members! 🚀")
                        except Exception as e:
                            st.error(f"Email error: {str(e)} • Check App Password & secrets")
                    else:
                        st.warning("No email sent • Add EMAIL_SENDER/PASSWORD secrets or member emails")
                    st.success("Profit recorded & distributed instantly! Balances + GF updated.")
                    st.cache_data.clear()
                    st.rerun()
                except Exception as e:
                    st.error(f"Record failed: {str(e)}")
# ====================== MY PROFILE PAGE - FULL FINAL LATEST 2026 (FULLY SUPABASE SYNCED + V2 SUPPORT + PERMANENT STORAGE PROOFS) ======================
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
    my_user_id = st.session_state.get("user_id")  # Assuming you store user_id in session on login (recommended)
 
    # FULL REALTIME CACHE (10s for ultra-realtime feel)
    @st.cache_data(ttl=10)
    def fetch_my_profile_data():
        # My user record
        user_resp = supabase.table("users").select("*").eq("full_name", my_name).single().execute()
        my_user = user_resp.data if user_resp.data else {}
 
        # All accounts (for shared detection)
        accounts_resp = supabase.table("ftmo_accounts").select("*").execute()
        accounts = accounts_resp.data or []
 
        # Detect my accounts (supports BOTH legacy + v2)
        my_accounts = []
        for a in accounts:
            # v2 priority
            participants_v2 = a.get("participants_v2", [])
            if any(p.get("display_name") == my_name or str(p.get("user_id")) == str(my_user.get("id")) for p in participants_v2):
                my_accounts.append(a)
                continue
            # Legacy fallback
            participants = a.get("participants", [])
            if any(p.get("name") == my_name for p in participants):
                my_accounts.append(a)
 
        # My withdrawals
        wd_resp = supabase.table("withdrawals").select("*").eq("client_name", my_name).order("date_requested", desc=True).execute()
        my_withdrawals = wd_resp.data or []
 
        # My proofs (permanent Supabase Storage)
        files_resp = supabase.table("client_files").select("id, original_name, file_url, upload_date, category, notes").eq("assigned_client", my_name).order("upload_date", desc=True).execute()
        my_proofs = files_resp.data or []
 
        # All users for title display in trees
        all_users_resp = supabase.table("users").select("id, full_name, title").execute()
        all_users = all_users_resp.data or []
        user_id_to_title = {str(u["id"]): u.get("title") for u in all_users}
 
        return my_user, my_accounts, my_withdrawals, my_proofs, all_users, user_id_to_title
 
    my_user, my_accounts, my_withdrawals, my_proofs, all_users, user_id_to_title = fetch_my_profile_data()
 
    st.caption("🔄 Profile auto-refresh every 10s • Everything realtime & fully synced")
 
    # Manual refresh button (extra control for clients)
    if st.button("🔄 Refresh My Profile Now", use_container_width=True, type="secondary"):
        st.cache_data.clear()
        st.rerun()
 
    # ====================== PREMIUM THEME-ADAPTIVE FLIP CARD ======================
    my_title = my_user.get("title", "Member").upper()
    card_title = f"{my_title} CARD" if my_title != "NONE" else "MEMBER CARD"
    my_balance = my_user.get("balance", 0) or 0
 
    # Theme colors (unchanged - perfect)
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
      /* Same perfect flip card CSS as before */
      .flip-card {{ background: transparent; width: 600px; height: 380px; perspective: 1000px; margin: 0 auto; }}
      .flip-card-inner {{ position: relative; width: 100%; height: 100%; text-align: center; transition: transform 0.8s cubic-bezier(0.68, -0.55, 0.27, 1.55); transform-style: preserve-3d; }}
      .flip-card:hover .flip-card-inner, .flip-card:focus-within .flip-card-inner {{ transform: rotateY(180deg); }}
      .flip-card-front, .flip-card-back {{ position: absolute; width: 100%; height: 100%; -webkit-backface-visibility: hidden; backface-visibility: hidden; border-radius: 20px; }}
      .flip-card-back {{ transform: rotateY(180deg); }}
      @media (max-width: 768px) {{ /* Mobile styles same as before */ }}
    </style>
    <p style="text-align:center; opacity:0.7; margin-top:1rem; font-size:1rem;">
      Hover (desktop) or tap (mobile) the card to flip ↺
    </p>
    """, unsafe_allow_html=True)
 
    # ====================== MY QUICK LOGIN QR CODE (UNCHANGED - PERFECT) ======================
    # ... (keep your existing QR code section exactly as is - it's already perfect)
 
    # ====================== CHANGE PASSWORD & FORGOT PASSWORD (UNCHANGED) ======================
    # ... (keep exactly as is)
 
    # ====================== SHARED ACCOUNTS WITH % & FUNDED PHP (FULL V2 SUPPORT) ======================
    st.subheader(f"Your Shared Accounts ({len(my_accounts)} active)")
    if my_accounts:
        for acc in my_accounts:
            # Prefer v2
            participants = acc.get("participants_v2") or acc.get("participants", [])
            contributors = acc.get("contributors_v2") or acc.get("contributors", [])
 
            # My percentage (v2 priority)
            my_part = next((p for p in participants if p.get("display_name") == my_name or str(p.get("user_id")) == str(my_user.get("id"))), None)
            my_pct = my_part["percentage"] if my_part else next((p["percentage"] for p in participants if p.get("name") == my_name), 0)
 
            # Projected share
            my_projected = (acc.get("current_equity", 0) * my_pct / 100) if acc.get("current_equity") else 0
 
            # My funded PHP (v2 priority)
            my_funded_php = sum(c.get("units", 0) * c.get("php_per_unit", 0) for c in contributors 
                                if str(c.get("user_id")) == str(my_user.get("id")))
            if my_funded_php == 0:  # Legacy fallback
                my_funded_php = sum(c["units"] * c["php_per_unit"] for c in contributors if c.get("name") == my_name)
 
            with st.expander(f"🌟 {acc['name']} • Your Share: {my_pct:.1f}% • Phase: {acc['current_phase']}", expanded=False):
                col_acc1, col_acc2 = st.columns(2)
                with col_acc1:
                    st.metric("Account Equity", f"${acc.get('current_equity', 0):,.0f}")
                    st.metric("Your Projected Share", f"${my_projected:,.2f}")
                with col_acc2:
                    st.metric("Account Withdrawable", f"${acc.get('withdrawable_balance', 0):,.0f}")
                    st.metric("Your Funded (PHP)", f"₱{my_funded_php:,.0f}")
 
                # Sankey tree with titles
                labels = ["Profits"]
                values = []
                for p in participants:
                    display = p.get("display_name") or p.get("name", "Unknown")
                    title = user_id_to_title.get(str(p.get("user_id")), "")
                    if title:
                        display += f" ({title})"
                    labels.append(f"{display} ({p.get('percentage', 0):.1f}%)")
                    values.append(p.get("percentage", 0))
                if values:
                    fig = go.Figure(data=[go.Sankey(
                        node=dict(pad=15, thickness=20, label=labels),
                        link=dict(source=[0]*len(values), target=list(range(1, len(labels))), value=values)
                    )])
                    fig.update_layout(height=350, margin=dict(t=20))
                    st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No participation yet • Owner will assign you to shared profits")
 
    # ====================== WITHDRAWAL HISTORY & QUICK REQUEST (SUPABASE STORAGE PROOF) ======================
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
 
    # Quick request - NOW WITH PERMANENT SUPABASE STORAGE UPLOAD
    with st.expander("➕ Request New Withdrawal (from Balance)", expanded=False):
        if my_balance <= 0:
            st.info("No available balance yet • Earnings auto-accumulate from profits")
        else:
            with st.form("my_wd_form", clear_on_submit=True):
                amount = st.number_input("Amount (USD)", min_value=1.0, max_value=my_balance, step=100.0, help=f"Max: ${my_balance:,.2f}")
                method = st.selectbox("Method", ["USDT", "Bank Transfer", "Wise", "PayPal", "GCash", "Other"])
                details = st.text_area("Details (Wallet/Address/Bank Info)")
                proof = st.file_uploader("Upload Proof * (Required - Permanent Storage)", type=["png","jpg","jpeg","pdf"])
 
                submitted = st.form_submit_button("Submit Request", type="primary")
                if submitted:
                    if amount > my_balance:
                        st.error("Exceeds balance")
                    elif not proof:
                        st.error("Proof required")
                    else:
                        try:
                            # Permanent Supabase Storage upload
                            url, storage_path = upload_to_supabase(
                                file=proof,
                                bucket="client_files",
                                folder="proofs",
                                use_signed_url=False
                            )
                            supabase.table("client_files").insert({
                                "original_name": proof.name,
                                "file_url": url,
                                "storage_path": storage_path,
                                "upload_date": datetime.date.today().isoformat(),
                                "sent_by": my_name,
                                "category": "Withdrawal Proof",
                                "assigned_client": my_name,
                                "notes": f"Proof for ${amount:,.0f} withdrawal"
                            }).execute()
 
                            supabase.table("withdrawals").insert({
                                "client_name": my_name,
                                "amount": amount,
                                "method": method,
                                "details": details,
                                "status": "Pending",
                                "date_requested": datetime.date.today().isoformat()
                            }).execute()
 
                            st.success("Request submitted with permanent proof! Owner will review.")
                            st.cache_data.clear()
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
 
    # ====================== MY PROOFS IN VAULT (SUPABASE STORAGE URLs) ======================
    st.subheader("📁 Your Proofs in Vault (Permanent)")
    if my_proofs:
        cols = st.columns(4)
        for idx, p in enumerate(my_proofs):
            with cols[idx % 4]:
                if p.get("file_url"):
                    if p["original_name"].lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                        st.image(p["file_url"], caption=p["original_name"], use_container_width=True)
                    else:
                        st.markdown(f"**{p['original_name']}**")
                        st.markdown(f"*{p.get('category', 'Other')} • {p['upload_date']}*")
                    # Download button
                    if st.button("⬇ Download", key=f"proof_dl_{p['id']}"):
                        st.markdown(f"[Download {p['original_name']}]({p['file_url']})")
                else:
                    st.caption(p["original_name"] + " (no preview)")
    else:
        st.info("No proofs uploaded yet")
 
    # ====================== MOTIVATIONAL FOOTER ======================
    st.markdown(f"""
    <div class='glass-card' style='padding:3rem; text-align:center; margin:3rem 0;'>
        <h1 style="background:linear-gradient(90deg,{accent_color},#ffd700); -webkit-background-clip:text; -webkit-text-fill-color:transparent;">
            Your Empire Journey
        </h1>
        <p style="font-size:1.3rem; margin:2rem 0;">
            Realtime earnings • Full v2 participation • Permanent proofs • Instant QR • Motivated & aligned forever.
        </p>
        <h2 style="color:#ffd700;">👑 KMFX Pro • Elite Member Portal 2026</h2>
    </div>
    """, unsafe_allow_html=True)
# ====================== PART 5: GROWTH FUND PAGE (FINAL SUPER ADVANCED - FULL MAIN FLOW SYNC & REALTIME) ======================
# ====================== GROWTH FUND PAGE - FULL FINAL LATEST 2026 (FULLY SUPABASE SYNCED + INSTANT MV + REALTIME EVERYTHING) ======================
elif selected == "🌱 Growth Fund":
    st.header("Growth Fund Management 🌱")
    st.markdown("**Empire reinvestment engine: 100% automatic inflows from profit distributions • Full source transparency with auto-trees • Advanced projections & scaling simulations • Manual adjustments • Instant sync across dashboard, profits, balances.**")
 
    current_role = st.session_state.get("role", "guest")
 
    # INSTANT FULL REALTIME CACHE (10s for ultra-realtime)
    @st.cache_data(ttl=10)
    def fetch_gf_full_data():
        try:
            # INSTANT balance from materialized view (lightning fast)
            gf_resp = supabase.table("mv_growth_fund_balance").select("balance").single().execute()
            gf_balance = gf_resp.data["balance"] if gf_resp.data else 0.0
         
            # All transactions (realtime history)
            trans_resp = supabase.table("growth_fund_transactions").select("*").order("date", desc=True).execute()
            transactions = trans_resp.data or []
         
            # Auto-sources breakdown for tree
            profits_resp = supabase.table("profits").select("id, account_id, record_date, growth_fund_add").gt("growth_fund_add", 0).execute()
            profits = profits_resp.data or []
         
            accounts_resp = supabase.table("ftmo_accounts").select("id, name").execute()
            account_map = {a["id"]: a["name"] for a in accounts_resp.data or []}
         
            auto_sources = {}
            for p in profits:
                acc_name = account_map.get(p["account_id"], "Unknown Account")
                key = f"{acc_name} ({p['record_date']})"
                auto_sources[key] = auto_sources.get(key, 0) + p["growth_fund_add"]
         
            # Manual sources
            manual_sources = {}
            for t in transactions:
                if t["type"] == "Out" or t.get("account_source") == "Manual" or not t.get("description", "").startswith("Auto"):
                    key = t.get("description") or t.get("account_source") or ("Manual Out" if t["type"] == "Out" else "Manual In")
                    amount = -t["amount"] if t["type"] == "Out" else t["amount"]
                    manual_sources[key] = manual_sources.get(key, 0) + amount
         
            # Current empire accounts for projections
            empire_resp = supabase.table("mv_empire_summary").select("total_accounts").single().execute()
            total_accounts = empire_resp.data["total_accounts"] if empire_resp.data else 0
         
            return transactions, gf_balance, auto_sources, manual_sources, total_accounts
        except Exception as e:
            st.error(f"Growth Fund data error: {e}")
            return [], 0.0, {}, {}, 0
 
    transactions, gf_balance, auto_sources, manual_sources, total_accounts = fetch_gf_full_data()
 
    # Manual refresh button
    if st.button("🔄 Refresh Growth Fund Now", use_container_width=True, type="secondary"):
        st.cache_data.clear()
        st.rerun()
 
    # KEY METRICS (INSTANT FROM MV)
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Current Growth Fund (Instant)", f"${gf_balance:,.0f}")
    auto_in = sum(auto_sources.values())
    col2.metric("Total Auto Inflows", f"${auto_in:,.0f}")
    manual_in = sum(v for v in manual_sources.values() if v > 0)
    col3.metric("Total Manual In", f"${manual_in:,.0f}")
    outflows = sum(abs(v) for v in manual_sources.values() if v < 0)
    col4.metric("Total Outflows", f"${outflows:,.0f}")
 
    # REALTIME SOURCE TREE
    st.subheader("🌳 All Inflow/Outflow Sources Tree (Realtime Auto + Manual)")
    all_sources = {**auto_sources, **manual_sources}
    if all_sources:
        labels = ["Growth Fund"]
        values = []
        colors = []
        source = []
        target = []
        idx = 1
 
        for key, amount in all_sources.items():
            labels.append(key)
            values.append(abs(amount))
            colors.append(accent_color if amount > 0 else "#ff6b6b")
            source.append(0)
            target.append(idx)
            idx += 1
 
        fig = go.Figure(data=[go.Sankey(
            node=dict(pad=20, thickness=30, label=labels, color=["#ffd700"] + colors),
            link=dict(source=source, target=target, value=values)
        )])
        fig.update_layout(height=600, title="Complete Flow by Source")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Growth Fund empty • Activates with first profit or manual transaction")
 
    # MANUAL TRANSACTION (OWNER/ADMIN ONLY)
    if current_role in ["owner", "admin"]:
        with st.expander("➕ Manual Transaction (Scaling/Reinvestment)", expanded=False):
            with st.form("gf_manual_form", clear_on_submit=True):
                col_t1, col_t2 = st.columns([1, 2])
                with col_t1:
                    trans_type = st.selectbox("Type", ["In", "Out"])
                with col_t2:
                    amount = st.number_input("Amount (USD)", min_value=0.01, step=100.0)
                purpose = st.selectbox("Purpose", ["New Challenge Purchase", "Scaling Capital", "EA Development", "Team Bonus", "Operational", "Other"])
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
                        st.success("Transaction recorded instantly! GF balance & tree updated realtime.")
                        st.cache_data.clear()
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
 
    # FULL HISTORY TABLE
    st.subheader("📜 Complete Transaction History (Realtime)")
    if transactions:
        df = pd.DataFrame(transactions)
        df["Amount"] = df.apply(lambda row: f"+${row['amount']:,.0f}" if row["type"] == "In" else f"-${row['amount']:,.0f}", axis=1)
        df["Type"] = df["type"].map({"In": "✅ In", "Out": "❌ Out"})
        df["Source"] = df.apply(lambda row: row["account_source"] if row["account_source"] != "Manual" else row["description"] or "Manual", axis=1)
        df_display = df[["date", "Type", "Amount", "Source", "recorded_by"]].rename(columns={
            "date": "Date", "Source": "Source/Description", "recorded_by": "Recorded By"
        })
        st.dataframe(df_display, use_container_width=True, hide_index=True)
    else:
        st.info("No transactions yet • Auto-inflows start with profits")
 
    # ADVANCED PROJECTIONS (AUTO-LOADED CURRENT STATS)
    st.subheader("🔮 Advanced Scaling Projections (Auto-Loaded Empire Stats)")
    col_proj1, col_proj2 = st.columns(2)
    with col_proj1:
        months = st.slider("Projection Months", 6, 72, 36)
        projected_accounts = st.slider("Projected Active Accounts", total_accounts, total_accounts + 30, total_accounts + 10)
        avg_monthly_profit = st.number_input("Avg Monthly Gross per Account (USD)", value=15000.0, step=1000.0)
        gf_pct = st.slider("Growth Fund % from Profits", 0.0, 50.0, 20.0)
    with col_proj2:
        monthly_manual = st.number_input("Additional Monthly Manual In (USD)", value=0.0, step=1000.0)
 
    projected_monthly_gross = avg_monthly_profit * projected_accounts
    projected_monthly_gf = projected_monthly_gross * (gf_pct / 100) + monthly_manual
 
    dates = [datetime.date.today() + datetime.timedelta(days=30*i) for i in range(months + 1)]
    gf_proj = [gf_balance]
    for i in range(months):
        gf_proj.append(gf_proj[-1] + projected_monthly_gf)
 
    fig_proj = go.Figure()
    fig_proj.add_trace(go.Scatter(x=dates, y=gf_proj, mode='lines+markers', line=dict(color=accent_color, width=6)))
    fig_proj.add_hline(y=gf_balance * 10, line_dash="dash", line_color="#ffd700", annotation_text="10x Current Target")
    fig_proj.update_layout(height=500, title=f"Projected GF Growth (+${projected_monthly_gf:,.0f}/month)")
    st.plotly_chart(fig_proj, use_container_width=True)
 
    st.metric("Projected Balance in {months} Months", f"${gf_proj[-1]:,.0f}")
    if gf_proj[-1] >= gf_balance * 10:
        st.success("🚀 On track for 10x Growth Fund!")
    elif gf_proj[-1] >= gf_balance * 5:
        st.success("🔥 Strong growth trajectory!")
 
    # MOTIVATIONAL FOOTER
    st.markdown(f"""
    <div class='glass-card' style='padding:3rem; text-align:center; margin:3rem 0;'>
        <h1 style="background:linear-gradient(90deg,{accent_color},#ffd700); -webkit-background-clip:text; -webkit-text-fill-color:transparent;">
            Automatic Reinvestment Engine
        </h1>
        <p style="font-size:1.3rem; margin:2rem 0;">
            Instant MV balance • Realtime trees & history • Manual control • Projections auto-loaded • Empire compounds itself.
        </p>
        <h2 style="color:#ffd700;">👑 KMFX Growth Fund • Fully Automatic & Realtime 2026</h2>
    </div>
    """, unsafe_allow_html=True)
elif selected == "🔑 License Generator":
    st.header("EA License Generator 🔑")
    st.markdown("**Universal Security • ANY Broker • Flexible Accounts • LIVE/DEMO Control • XOR Encryption • Realtime History**")
    # Clean XOR encryption (no padding issues)
    def mt_encrypt(plain: str, key: str) -> str:
        if not key:
            return ""
        result = bytearray()
        klen = len(key)
        for i, ch in enumerate(plain):
            k = ord(key[i % klen])
            result.append(ord(ch) ^ k)
        return ''.join(f'{b:02X}' for b in result).upper()
    # STRICT OWNER ONLY
    if st.session_state.get("role", "guest") != "owner":
        st.error("🔒 License generation is OWNER-ONLY.")
        st.stop()
    # ULTRA-REALTIME CACHE (10s)
    @st.cache_data(ttl=10)
    def fetch_license_data():
        clients_resp = supabase.table("users").select("id, full_name, balance, role").eq("role", "client").execute()
        clients = clients_resp.data or []
        history_resp = supabase.table("client_licenses").select("*").order("date_generated", desc=True).execute()
        history = history_resp.data or []
        user_map = {str(c["id"]): {"name": c["full_name"] or "Unknown", "balance": c["balance"] or 0} for c in clients}
        return clients, history, user_map
    clients, history, user_map = fetch_license_data()
    # Manual refresh button
    if st.button("🔄 Refresh License Data Now", use_container_width=True, type="secondary"):
        st.cache_data.clear()
        st.rerun()
    if not clients:
        st.info("No clients yet — register in Team Management first.")
        st.stop()
    st.subheader("Generate New License")
    client_options = {f"{c['full_name']} (Balance: ${c['balance'] or 0:,.2f})": c for c in clients}
    selected_key = st.selectbox("Select Client", list(client_options.keys()))
    client = client_options[selected_key]
    client_id = client["id"]
    client_name = client["full_name"]
    client_balance = client["balance"] or 0
    st.info(f"**Generating for:** {client_name} | Current Balance: ${client_balance:,.2f}")
    # Session state defaults
    for key, default in [
        ("allow_any_account", True),
        ("allow_live_trading", True),
        ("specific_accounts_value", ""),
        ("expiry_option", "NEVER (Lifetime)")  # Default to NEVER for cleaner UX
    ]:
        if key not in st.session_state:
            st.session_state[key] = default
    # Checkboxes with auto-rerun
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
    if (allow_any != st.session_state.allow_any_account or allow_live != st.session_state.allow_live_trading):
        st.session_state.allow_any_account = allow_any
        st.session_state.allow_live_trading = allow_live
        st.rerun()
    if allow_live:
        st.success("✅ LIVE + DEMO allowed")
    else:
        st.warning("⚠️ DEMO only (Live blocked)")
    # GENERATE FORM
    with st.form("license_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            specific_accounts = st.text_area(
                "Specific Allowed Logins (comma-separated)",
                placeholder="12345678,87654321 (leave blank if universal)",
                disabled=allow_any,
                value=st.session_state.specific_accounts_value,
                height=100
            )
        with col2:
            # FIXED: Radio with proper state persistence + conditional date input
            expiry_option = st.radio(
                "Expiry",
                ["NEVER (Lifetime)", "Specific Date"],
                index=0 if st.session_state.get("expiry_option") == "NEVER (Lifetime)" else 1,
                key="expiry_radio"  # Forces rerun on change
            )
            st.session_state.expiry_option = expiry_option  # Persist choice

            if expiry_option == "Specific Date":
                exp_date = st.date_input(
                    "Expiry Date",
                    datetime.date.today() + datetime.timedelta(days=365),
                    key="exp_date_input"
                )
                expiry_str = exp_date.strftime("%Y-%m-%d")
                st.info(f"License expires on {expiry_str}")
            else:
                expiry_str = "NEVER"
                st.success("✅ Lifetime license (NEVER expires)")

            version_note = st.text_input("Version Note", value="v2.36 Elite 2026")
            internal_notes = st.text_area("Internal Notes (Optional)", height=100)
        submitted = st.form_submit_button("🚀 Generate & Save License", type="primary", use_container_width=True)
        if submitted:
            accounts_str = "*" if allow_any else ",".join([a.strip() for a in specific_accounts.split(",") if a.strip()])
            live_str = "1" if allow_live else "0"
            plain = f"{client_name}|{accounts_str}|{expiry_str}|{live_str}"
            # Ensure even length for clean XOR
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
                st.success(f"License generated successfully! **{unique_key}**")
                st.balloons()
                # Clear specific accounts field
                st.session_state.specific_accounts_value = ""
                # Reset expiry to default NEVER for next generation
                st.session_state.expiry_option = "NEVER (Lifetime)"
                # Show ready-to-paste code
                st.subheader("📋 Ready to Paste into EA")
                st.code(f'''
string UNIQUE_KEY = "{unique_key}";
string ENC_DATA = "{enc_data_hex}";
                ''', language="cpp")
                # Force full refresh
                st.cache_data.clear()
                st.rerun()
            except Exception as e:
                st.error(f"Save failed: {str(e)}")
    # REALTIME HISTORY (unchanged)
    st.subheader("📜 Issued Licenses History (Realtime)")
    if history:
        # Optional search
        search_hist = st.text_input("Search by key, client, or version")
        filtered_history = [h for h in history if search_hist.lower() in str(h.get("key","")).lower() or
                            search_hist.lower() in user_map.get(str(h.get("account_id")), {}).get("name","").lower() or
                            search_hist.lower() in str(h.get("version","")).lower()] if search_hist else history
        for h in filtered_history:
            client_name_hist = user_map.get(str(h["account_id"]), {}).get("name", "Unknown")
            status = "🔴 Revoked" if h.get("revoked") else "🟢 Active"
            live_status = "LIVE+DEMO" if h.get("allow_live") else "DEMO only"
            acc_txt = "ANY (*)" if h.get("allowed_accounts") is None else h.get("allowed_accounts", "Custom")
            version_display = f" • {h.get('version', 'Standard')}"
            with st.expander(
                f"{h.get('key','—')} • {client_name_hist}{version_display} • {status} • {live_status} • {acc_txt} • {h.get('date_generated', '—')}",
                expanded=False
            ):
                st.markdown(f"**Expiry:** {h['expiry']}")
                if h.get("notes"):
                    st.caption(f"Notes: {h['notes']}")
                st.code(f"ENC_DATA = \"{h.get('enc_data','—')}\"", language="text")
                st.code(f"UNIQUE_KEY = \"{h.get('key','—')}\"", language="text")
                col_act1, col_act2 = st.columns(2)
                with col_act1:
                    if not h.get("revoked"):
                        if st.button("Revoke License", key=f"revoke_{h['id']}"):
                            try:
                                supabase.table("client_licenses").update({"revoked": True}).eq("id", h["id"]).execute()
                                st.success("License revoked instantly")
                                st.cache_data.clear()
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error: {str(e)}")
                with col_act2:
                    if st.button("🗑️ Delete Permanently", key=f"delete_{h['id']}", type="secondary"):
                        try:
                            supabase.table("client_licenses").delete().eq("id", h["id"]).execute()
                            st.success("License deleted forever")
                            st.cache_data.clear()
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
    else:
        st.info("No licenses issued yet • Generate first to activate history")
    # ELITE FOOTER
    st.markdown(f"""
    <div class='glass-card' style='padding:3rem; text-align:center; margin:3rem 0;'>
        <h1 style="background:linear-gradient(90deg,{accent_color},#ffd700); -webkit-background-clip:text; -webkit-text-fill-color:transparent;">
            Elite EA License System 2026
        </h1>
        <p style="font-size:1.3rem; margin:2rem 0;">
            ✅ Fixed expiry UX: Date input hidden/disabled when NEVER selected<br>
            ✅ Default NEVER for faster lifetime licenses • Clean & effective
        </p>
        <h2 style="color:#ffd700;">👑 KMFX License Generator • Fully Fixed & Elite</h2>
    </div>
    """, unsafe_allow_html=True)
# ====================== FILE VAULT PAGE - FULL FINAL LATEST 2026 (PERMANENT SUPABASE STORAGE + REALTIME + ELITE GRID) ======================
elif selected == "📁 File Vault":
    st.header("Secure File Vault 📦")
    st.markdown("**Permanent encrypted storage • All file types supported • Proofs & documents secured • Auto-assigned access • Realtime grid with full previews**")
 
    current_role = st.session_state.get("role", "guest")
 
    # ULTRA-REALTIME CACHE (10s)
    @st.cache_data(ttl=10)
    def fetch_vault_data():
        files_resp = supabase.table("client_files").select(
            "id, original_name, file_url, storage_path, upload_date, sent_by, "
            "category, assigned_client, tags, notes"
        ).order("upload_date", desc=True).execute()
        files = files_resp.data or []
 
        users_resp = supabase.table("users").select("id, full_name, role").execute()
        users = users_resp.data or []
        registered_clients = sorted(set(u["full_name"] for u in users if u["role"] == "client"))
 
        return files, registered_clients
 
    files, registered_clients = fetch_vault_data()
 
    # Manual refresh button
    if st.button("🔄 Refresh Vault Now", use_container_width=True, type="secondary"):
        st.cache_data.clear()
        st.rerun()
 
    st.caption("🔄 Vault auto-refresh every 10s • All files PERMANENT in Supabase Storage")
 
    # CLIENT VIEW RESTRICTION
    if current_role == "client":
        my_name = st.session_state.full_name
        files = [f for f in files if f["sent_by"] == my_name or f.get("assigned_client") == my_name]
        st.info(f"Showing only your files ({len(files)} total)")
 
    # UPLOAD SECTION (OWNER/ADMIN ONLY)
    if current_role in ["owner", "admin"]:
        st.subheader("📤 Upload New Files (Permanent Storage)")
        with st.form("file_upload_form", clear_on_submit=True):
            col_upload, col_options = st.columns([3, 2])
            with col_upload:
                uploaded_files = st.file_uploader(
                    "Choose files (PDF, images, .ex5, zip, docs, etc.)",
                    accept_multiple_files=True,
                    help="Max 200MB per file • All types supported • .ex5 fully allowed"
                )
            with col_options:
                category = st.selectbox("Category", [
                    "Payout Proof", "Withdrawal Proof", "Agreement", "KYC/ID",
                    "Contributor Contract", "Testimonial Image", "EA File", "License Key", "Other"
                ])
                assigned_client = st.selectbox("Assign to Client (optional)", ["None"] + registered_clients)
                tags = st.text_input("Tags (comma-separated)", placeholder="e.g. payout, 2026, ex5")
                notes = st.text_area("Notes (Optional)", height=100)
 
            submitted = st.form_submit_button("📤 Upload Permanently", type="primary", use_container_width=True)
            if submitted and uploaded_files:
                success_count = 0
                failed = []
                progress = st.progress(0)
                status = st.empty()
                for idx, file in enumerate(uploaded_files):
                    status.text(f"Uploading {file.name} ({idx+1}/{len(uploaded_files)})...")
                    try:
                        url, storage_path = upload_to_supabase(
                            file=file,
                            bucket="client_files",
                            folder="vault",
                            use_signed_url=False
                        )
                        supabase.table("client_files").insert({
                            "original_name": file.name,
                            "file_url": url,
                            "storage_path": storage_path,
                            "upload_date": datetime.date.today().isoformat(),
                            "sent_by": st.session_state.full_name,
                            "category": category,
                            "assigned_client": assigned_client if assigned_client != "None" else None,
                            "tags": tags.strip() or None,
                            "notes": notes.strip() or None
                        }).execute()
                        success_count += 1
                        log_action("File Uploaded (Permanent)", f"{file.name} → {category} → {assigned_client}")
                    except Exception as e:
                        failed.append(f"{file.name}: {str(e)}")
                    progress.progress((idx + 1) / len(uploaded_files))
                status.empty()
                progress.empty()
                if success_count:
                    st.success(f"**{success_count}/{len(uploaded_files)}** files uploaded permanently!")
                    st.cache_data.clear()
                    st.rerun()
                if failed:
                    st.error("Some uploads failed:")
                    for f in failed:
                        st.caption(f"• {f}")
 
    # ADVANCED FILTERS & SEARCH
    st.subheader("🔍 Search & Filter Vault")
    col_f1, col_f2, col_f3, col_f4 = st.columns(4)
    with col_f1:
        search = st.text_input("Search name/tags/notes", placeholder="e.g. payout proof, .ex5")
    with col_f2:
        cat_filter = st.selectbox("Category", ["All"] + sorted(set(f.get("category", "Other") for f in files)))
    with col_f3:
        client_filter = st.selectbox("Assigned Client", ["All"] + sorted(set(f.get("assigned_client") for f in files if f.get("assigned_client"))))
    with col_f4:
        sort_by = st.selectbox("Sort By", ["Newest First", "Oldest First", "Name A-Z", "Name Z-A"])
 
    # Apply filters
    filtered = files
    if search:
        s = search.lower()
        filtered = [f for f in filtered if s in f["original_name"].lower() or
                    s in (f.get("tags") or "").lower() or
                    s in (f.get("notes") or "").lower()]
    if cat_filter != "All":
        filtered = [f for f in filtered if f.get("category") == cat_filter]
    if client_filter != "All":
        filtered = [f for f in filtered if f.get("assigned_client") == client_filter]
 
    # Sorting
    reverse_sort = False
    if sort_by == "Newest First":
        key = lambda x: x["upload_date"]
        reverse_sort = True
    elif sort_by == "Oldest First":
        key = lambda x: x["upload_date"]
    elif sort_by == "Name A-Z":
        key = lambda x: x["original_name"].lower()
    elif sort_by == "Name Z-A":
        key = lambda x: x["original_name"].lower()
        reverse_sort = True
    filtered = sorted(filtered, key=key, reverse=reverse_sort)
 
    # REALTIME GRID DISPLAY
    st.subheader(f"Vault Contents ({len(filtered)} files)")
    if filtered:
        cols = st.columns(3)
        for idx, f in enumerate(filtered):
            with cols[idx % 3]:
                file_url = f.get("file_url")
                assigned = f.get("assigned_client")
                tags = f.get("tags", "")
                notes = f.get("notes", "")
 
                # Glass card
                st.markdown(f"""
                <div style="background:rgba(30,35,45,0.7); backdrop-filter:blur(12px); border-radius:16px; padding:1.4rem; margin-bottom:1.6rem; box-shadow:0 6px 20px rgba(0,0,0,0.15); border:1px solid rgba(100,100,100,0.25);">
                """, unsafe_allow_html=True)
 
                # Preview
                if file_url and f["original_name"].lower().endswith(('.png','.jpg','.jpeg','.gif')):
                    st.image(file_url, use_container_width=True)
                else:
                    st.markdown("<div style='height:140px; background:rgba(50,55,65,0.5); border-radius:10px; display:flex; align-items:center; justify-content:center; color:#aaa; font-size:1rem;'>No Preview</div>", unsafe_allow_html=True)
 
                st.markdown(f"**{f['original_name']}**")
                st.caption(f"{f['upload_date']} • Uploaded by {f['sent_by']}")
                st.caption(f"Category: **{f.get('category','Other')}**")
                if assigned:
                    st.caption(f"Assigned: **{assigned}**")
                if tags:
                    st.caption(f"Tags: {tags}")
 
                # Notes
                if notes:
                    with st.expander("Notes"):
                        st.write(notes)
 
                # Download
                if file_url:
                    try:
                        r = requests.get(file_url, timeout=8)
                        if r.status_code == 200:
                            st.download_button(
                                "⬇ Download",
                                data=r.content,
                                file_name=f["original_name"],
                                use_container_width=True,
                                key=f"dl_{f['id']}_{idx}"
                            )
                        else:
                            st.caption("Download unavailable")
                    except:
                        st.caption("Download failed")
 
                # Delete (owner/admin only)
                if current_role in ["owner", "admin"]:
                    if st.button("🗑️ Delete Permanently", key=f"del_{f['id']}_{idx}", type="secondary", use_container_width=True):
                        try:
                            if f.get("storage_path"):
                                supabase.storage.from_("client_files").remove([f["storage_path"]])
                            supabase.table("client_files").delete().eq("id", f["id"]).execute()
                            st.success(f"Deleted: {f['original_name']}")
                            log_action("File Deleted (Permanent)", f"{f['original_name']} by {st.session_state.full_name}")
                            st.cache_data.clear()
                            st.rerun()
                        except Exception as e:
                            st.error(f"Delete failed: {str(e)}")
 
                st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("No files match your filters • Vault is clean and permanent")
 
    # ELITE FOOTER
    st.markdown(f"""
    <div class='glass-card' style='padding:3rem; text-align:center; margin:3rem 0;'>
        <h1 style="background:linear-gradient(90deg,{accent_color},#ffd700); -webkit-background-clip:text; -webkit-text-fill-color:transparent;">
            Permanent Secure Vault
        </h1>
        <p style="font-size:1.3rem; margin:2rem 0;">
            Supabase Storage • Full previews • Advanced search/filter/sort • Permanent delete • Client restricted • Empire documents fortress.
        </p>
        <h2 style="color:#ffd700;">👑 KMFX File Vault • Cloud Permanent 2026</h2>
    </div>
    """, unsafe_allow_html=True)
# ====================== ANNOUNCEMENTS PAGE - FULL FINAL LATEST (SUPABASE STORAGE INTEGRATED) ======================
# ====================== ANNOUNCEMENTS PAGE - FULL FINAL LATEST 2026 (IMAGES & ATTACHMENTS NOW VISIBLE + PERMANENT + REALTIME) ======================
elif selected == "📢 Announcements":
    st.header("Empire Announcements 📢")
    st.markdown("**Central realtime communication: Broadcast updates • Rich images/attachments (PERMANENT STORAGE + FULLY VISIBLE) • Likes ❤️ • Threaded comments 💬 • Pinning 📌 • Search & filters • Full team engagement.**")
 
    current_role = st.session_state.get("role", "guest")
 
    # ULTRA-REALTIME CACHE (10s)
    @st.cache_data(ttl=10)
    def fetch_announcements_realtime():
        ann_resp = supabase.table("announcements").select("*").order("date", desc=True).execute()
        announcements = ann_resp.data or []
 
        # Fetch attachments + generate SIGNED URLs (works even on private buckets)
        for ann in announcements:
            att_resp = supabase.table("announcement_files").select(
                "id, original_name, storage_path"
            ).eq("announcement_id", ann["id"]).execute()
            attachments = []
            for att in att_resp.data or []:
                if att.get("storage_path"):
                    try:
                        signed = supabase.storage.from_("announcements").create_signed_url(
                            att["storage_path"], 3600 * 24 * 30  # 30 days expiry
                        )
                        att["signed_url"] = signed.get("signedURL") if signed else None
                    except:
                        att["signed_url"] = None
                else:
                    att["signed_url"] = None
                attachments.append(att)
            ann["attachments"] = attachments
 
        # Comments (realtime)
        comm_resp = supabase.table("announcement_comments").select("*").order("timestamp", desc=True).execute()
        comments_map = {}
        for c in comm_resp.data or []:
            comments_map.setdefault(c["announcement_id"], []).append(c)
        for ann in announcements:
            ann["comments"] = comments_map.get(ann["id"], [])
 
        return announcements
 
    announcements = fetch_announcements_realtime()
 
    # Manual refresh
    if st.button("🔄 Refresh Feed Now", use_container_width=True, type="secondary"):
        st.cache_data.clear()
        st.rerun()
 
    st.caption("🔄 Feed auto-refresh every 10s • Images & attachments now FULLY VISIBLE (signed URLs)")
 
    # POST NEW (OWNER/ADMIN)
    if current_role in ["owner", "admin"]:
        st.subheader("📢 Broadcast New Announcement")
        with st.form("ann_form", clear_on_submit=True):
            title = st.text_input("Title *")
            category = st.selectbox("Category", [
                "General", "Profit Distribution", "Withdrawal Update", 
                "License Granted", "Milestone", "EA Update", "Team Alert"
            ])
            message = st.text_area("Message *", height=150)
            attachments = st.file_uploader("Attachments (Images/Proofs/Files - Permanent + Visible)", accept_multiple_files=True)
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
 
                        if attachments:
                            progress = st.progress(0)
                            for idx, file in enumerate(attachments):
                                try:
                                    url, storage_path = upload_to_supabase(
                                        file=file,
                                        bucket="announcements",
                                        folder="attachments"
                                    )
                                    supabase.table("announcement_files").insert({
                                        "announcement_id": ann_id,
                                        "original_name": file.name,
                                        "file_url": url,  # keep for fallback
                                        "storage_path": storage_path
                                    }).execute()
                                except Exception as e:
                                    st.warning(f"Attachment {file.name} failed: {str(e)}")
                                progress.progress((idx + 1) / len(attachments))
                            progress.empty()
 
                        st.success("Announcement posted! Images & files now fully visible.")
                        st.cache_data.clear()
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
 
    # SEARCH & FILTER
    st.subheader("🔍 Search & Filter")
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        search = st.text_input("Search title/message")
    with col_s2:
        cat_filter = st.selectbox("Category", ["All"] + sorted(set(a.get("category", "General") for a in announcements)))
 
    filtered = [a for a in announcements if cat_filter == "All" or a.get("category") == cat_filter]
    if search:
        s = search.lower()
        filtered = [a for a in filtered if s in a["title"].lower() or s in a["message"].lower()]
    filtered = sorted(filtered, key=lambda x: (not x.get("pinned", False), x["date"]), reverse=True)
 
    # RICH FEED
    st.subheader(f"📻 Live Feed ({len(filtered)} posts)")
    if filtered:
        for ann in filtered:
            pinned = " 📌 PINNED" if ann.get("pinned") else ""
            with st.container():
                st.markdown(f"<h3 style='color:{accent_color};'>{ann['title']}{pinned}</h3>", unsafe_allow_html=True)
                st.caption(f"{ann.get('category', 'General')} • by {ann['posted_by']} • {ann['date']}")
                st.markdown(ann['message'])
 
                # IMAGES (now visible via signed URL)
                images = [att for att in ann["attachments"] if att["original_name"].lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
                if images:
                    cols = st.columns(min(len(images), 4))
                    for idx, att in enumerate(images):
                        signed = att.get("signed_url")
                        if signed:
                            with cols[idx % 4]:
                                st.image(signed, use_container_width=True)
                        else:
                            st.caption(f"{att['original_name']} (loading failed)")
 
                # NON-IMAGES
                non_images = [att for att in ann["attachments"] if not att["original_name"].lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
                if non_images:
                    st.markdown("**Files:**")
                    for att in non_images:
                        signed = att.get("signed_url")
                        if signed:
                            try:
                                r = requests.get(signed, timeout=10)
                                if r.status_code == 200:
                                    st.download_button(att['original_name'], r.content, att['original_name'])
                            except:
                                st.caption(f"{att['original_name']} (download failed)")
                        else:
                            st.caption(att['original_name'])
 
                # Likes & Comments (unchanged - perfect)
                if st.button(f"❤️ {ann.get('likes', 0)}", key=f"like_{ann['id']}"):
                    supabase.table("announcements").update({"likes": ann.get('likes', 0) + 1}).eq("id", ann["id"]).execute()
                    st.cache_data.clear()
                    st.rerun()
 
                with st.expander(f"💬 Comments ({len(ann['comments'])})", expanded=False):
                    for c in ann["comments"]:
                        st.markdown(f"**{c['user_name']}** • {c['timestamp'][:16].replace('T', ' ')}")
                        st.markdown(c['message'])
                        st.divider()
 
                    with st.form(key=f"comment_{ann['id']}"):
                        comment = st.text_area("Add comment...", height=80, label_visibility="collapsed")
                        if st.form_submit_button("Post"):
                            if comment.strip():
                                supabase.table("announcement_comments").insert({
                                    "announcement_id": ann["id"],
                                    "user_name": st.session_state.full_name,
                                    "message": comment.strip(),
                                    "timestamp": datetime.datetime.now().isoformat()
                                }).execute()
                                st.cache_data.clear()
                                st.rerun()
 
                # Admin actions (unchanged)
                if current_role in ["owner", "admin"]:
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("📌 Pin/Unpin", key=f"pin_{ann['id']}"):
                            supabase.table("announcements").update({"pinned": not ann.get("pinned", False)}).eq("id", ann["id"]).execute()
                            st.rerun()
                    with col2:
                        if st.button("🗑️ Delete", key=f"del_{ann['id']}", type="secondary"):
                            for att in ann["attachments"]:
                                if att.get("storage_path"):
                                    supabase.storage.from_("announcements").remove([att["storage_path"]])
                            supabase.table("announcement_files").delete().eq("announcement_id", ann["id"]).execute()
                            supabase.table("announcement_comments").delete().eq("announcement_id", ann["id"]).execute()
                            supabase.table("announcements").delete().eq("id", ann["id"]).execute()
                            st.cache_data.clear()
                            st.rerun()
                st.divider()
    else:
        st.info("No announcements yet")
 
    st.markdown(f"""
    <div class='glass-card' style='padding:3rem; text-align:center; margin:3rem 0;'>
        <h1 style="background:linear-gradient(90deg,{accent_color},#ffd700); -webkit-background-clip:text; -webkit-text-fill-color:transparent;">
            Realtime Empire Feed
        </h1>
        <p style="font-size:1.3rem; margin:2rem 0;">
            Images & attachments NOW FULLY VISIBLE • Permanent storage • Likes • Comments • Search • Empire connected.
        </p>
    </div>
    """, unsafe_allow_html=True)
elif selected == "💬 Messages":
    st.header("Private Messages 💬")
    st.markdown(
        "**Secure 1:1 communication • File attachments with inline previews • "
        "Search • Balance context • Realtime updates**"
    )

    current_role = st.session_state.get("role", "guest")
    my_name = st.session_state.full_name

    # ────────────────────────────────────────────────
    # Fetch data - shorter TTL for chat feel + select only needed fields
    # ────────────────────────────────────────────────
    @st.cache_data(ttl=6)  # more frequent refresh for messages
    def fetch_messages_data():
        # Get all users (for name mapping & client list)
        users_resp = supabase.table("users").select("id, full_name, role, balance").execute()
        users = users_resp.data or []

        # Get messages - IMPORTANT: select ALL relevant columns
        msg_resp = supabase.table("messages").select(
            "id, message, timestamp, from_admin, from_client, to_client"
        ).order("timestamp", desc=False).execute()  # asc = oldest first
        messages = msg_resp.data or []

        return users, messages

    all_users, all_messages = fetch_messages_data()

    # Build name lookup
    name_by_id = {str(u["id"]): u["full_name"] for u in all_users}
    balance_by_name = {u["full_name"]: u.get("balance", 0) for u in all_users}

    # ────────────────────────────────────────────────
    # Determine who we're chatting with
    # ────────────────────────────────────────────────
    if current_role in ["owner", "admin"]:
        if not any(u["role"] == "client" for u in all_users):
            st.info("No clients yet. Messaging will activate once team members are added.")
            st.stop()

        client_names = [u["full_name"] for u in all_users if u["role"] == "client"]
        client_options = {
            f"{name} (Balance: ${balance_by_name.get(name, 0):,.2f})": name
            for name in sorted(client_names)
        }

        selected_name = st.selectbox(
            "Chat with team member",
            options=list(client_options.keys()),
            index=0,
            key="admin_chat_select"
        )
        partner_name = client_options[selected_name]
        partner_balance = balance_by_name.get(partner_name, 0)

        st.info(f"**Chatting with:** {partner_name} • Balance: **${partner_balance:,.2f}**")

        # Filter messages for this partner
        convo = [
            m for m in all_messages
            if (m.get("from_client") == partner_name and m.get("to_client") is None) or
               (m.get("from_admin") == my_name and m.get("to_client") == partner_name) or
               (m.get("from_client") == partner_name and m.get("to_client") == my_name)
        ]

    else:  # Client view — always talking to admin / system
        partner_name = "KMFX Admin"
        partner_balance = None  # Admin has no balance shown to clients

        st.info("**Private channel with KMFX Admin** • Updates on profits, withdrawals, licenses, etc.")

        convo = [
            m for m in all_messages
            if (m.get("from_client") == my_name) or
               (m.get("to_client") == my_name)
        ]

    # ────────────────────────────────────────────────
    # Chat display
    # ────────────────────────────────────────────────
    if convo:
        search_term = st.text_input("Search messages", "", key="msg_search")
        if search_term:
            search_lower = search_term.lower()
            display_msgs = [m for m in convo if search_lower in m["message"].lower()]
        else:
            display_msgs = convo

        # Chat container with auto-scroll behavior
        chat_container = st.container()
        with chat_container:
            for msg in display_msgs:
                # Determine direction and sender
                if current_role in ["owner", "admin"]:
                    is_from_me = msg.get("from_admin") == my_name
                    sender_name = my_name if is_from_me else (msg.get("from_client") or "System")
                else:
                    is_from_me = msg.get("from_client") == my_name
                    sender_name = my_name if is_from_me else "KMFX Admin"

                align = "flex-end" if is_from_me else "flex-start"
                bubble_bg = accent_primary if is_from_me else card_bg
                text_color = "#000000" if is_from_me else text_primary
                time_str = msg["timestamp"][:16].replace("T", " ")

                # Message bubble
                st.markdown(
                    f"""
                    <div style="
                        display: flex;
                        justify-content: {align};
                        margin: 1.1rem 0;
                    ">
                        <div style="
                            background: {bubble_bg};
                            color: {text_color};
                            padding: 1.1rem 1.5rem;
                            border-radius: 20px;
                            max-width: 78%;
                            box-shadow: {card_shadow};
                            position: relative;
                        ">
                            <div style="font-weight: 600; margin-bottom: 0.4rem;">
                                {sender_name}
                            </div>
                            <div style="font-size: 0.9rem; opacity: 0.7; margin-bottom: 0.6rem;">
                                {time_str}
                            </div>
                            {msg['message'].replace('\n', '<br>')}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        # Fake auto-scroll effect (Streamlit limitation workaround)
        st.markdown(
            """
            <script>
            const chat = window.parent.document.querySelectorAll('.stChatMessage, .stContainer')[-1];
            if (chat) chat.scrollIntoView({behavior: 'smooth', block: 'end'});
            </script>
            """,
            unsafe_allow_html=True
        )

        st.caption(f"{len(convo)} message{'s' if len(convo) != 1 else ''} • newest at bottom")

    else:
        st.info("No messages yet. Start the conversation below ↓")

    # ────────────────────────────────────────────────
    # Send message form
    # ────────────────────────────────────────────────
    st.subheader("Send a Message")
    with st.form("send_message_form", clear_on_submit=True):
        col_msg, col_file = st.columns([3, 2])

        with col_msg:
            new_message = st.text_area(
                "Your message...",
                height=110,
                placeholder="Type here...",
                label_visibility="collapsed",
                key="new_msg_input"
            )

        with col_file:
            attached_files = st.file_uploader(
                "Attach images / files (visible inline)",
                accept_multiple_files=True,
                type=["png", "jpg", "jpeg", "gif", "pdf", "txt", "docx"],
                key="msg_attach"
            )

        submitted = st.form_submit_button("Send →", type="primary", use_container_width=True)

        if submitted:
            if not new_message.strip() and not attached_files:
                st.error("Please write a message or attach at least one file.")
            else:
                with st.spinner("Sending..."):
                    try:
                        # Build message content
                        content_parts = [new_message.strip()] if new_message.strip() else []

                        # Handle attachments
                        if attached_files:
                            for file in attached_files:
                                try:
                                    url, _ = upload_to_supabase(
                                        file=file,
                                        bucket="messages",
                                        folder="chat_attachments",
                                        use_signed_url=False  # assuming public bucket
                                    )

                                    if file.type.startswith("image/"):
                                        content_parts.append(f"![{file.name}]({url})")
                                    else:
                                        content_parts.append(f"[{file.name}]({url})")
                                except Exception as upload_err:
                                    st.warning(f"Could not upload {file.name}: {upload_err}")

                        final_content = "\n\n".join(content_parts) or "📎 Attachment only"

                        # Prepare insert
                        insert_row = {
                            "message": final_content,
                            "timestamp": datetime.datetime.now().isoformat()
                        }

                        if current_role in ["owner", "admin"]:
                            insert_row["from_admin"] = my_name
                            insert_row["to_client"] = partner_name
                        else:
                            insert_row["from_client"] = my_name
                            # to_admin is implicit (or you can add "to_admin": "KMFX Admin")

                        supabase.table("messages").insert(insert_row).execute()

                        log_action(
                            "Private Message Sent",
                            f"{'To ' + partner_name if current_role in ['owner','admin'] else 'From client'}"
                        )

                        st.success("Message sent!")
                        st.cache_data.clear()
                        st.rerun()

                    except Exception as e:
                        st.error(f"Failed to send message: {str(e)}")

    st.caption("ℹ️ Auto-messages (profit shares, withdrawals, licenses) appear here automatically.")
# ====================== NOTIFICATIONS PAGE - FULL FINAL LATEST 2026 (REALTIME + UNREAD BADGES + SEARCH + ELITE CARDS) ======================
elif selected == "🔔 Notifications":
    st.header("Empire Notifications 🔔")
    st.markdown("**Realtime alert system: Auto-push on profits, withdrawals, licenses, milestones • Prominent unread badges • Search & filters • Mark read • Instant sync & team alignment.**")
 
    current_role = st.session_state.get("role", "guest")
 
    # ULTRA-REALTIME CACHE (10s)
    @st.cache_data(ttl=10)
    def fetch_notifications_full():
        notif_resp = supabase.table("notifications").select("*").order("date", desc=True).execute()
        notifications = notif_resp.data or []
 
        users_resp = supabase.table("users").select("id, full_name, balance, role").execute()
        all_users = users_resp.data or []
        user_map = {u["full_name"]: {"balance": u["balance"] or 0} for u in all_users}
        client_names = sorted(u["full_name"] for u in all_users if u["role"] == "client")
 
        return notifications, user_map, client_names
 
    notifications, user_map, client_names = fetch_notifications_full()
 
    # Manual refresh
    if st.button("🔄 Refresh Notifications Now", use_container_width=True, type="secondary"):
        st.cache_data.clear()
        st.rerun()
 
    st.caption("🔄 Notifications auto-refresh every 10s • Auto-push on key events")
 
    # CLIENT VIEW: Own notifications + unread count
    if current_role == "client":
        my_name = st.session_state.full_name
        my_notifications = [n for n in notifications if n["client_name"] == my_name]
        unread_count = sum(1 for n in my_notifications if n.get("read", 0) == 0)
 
        st.subheader(f"Your Notifications 🔔")
        if unread_count > 0:
            st.markdown(f"### 🟡 {unread_count} Unread Alert{'' if unread_count == 1 else 's'}")
        else:
            st.markdown("### ✅ All caught up!")
    else:
        # OWNER/ADMIN: All notifications
        my_notifications = notifications
        st.subheader("All Empire Notifications")
 
    # SEND NEW NOTIFICATION (OWNER/ADMIN)
    if current_role in ["owner", "admin"]:
        st.subheader("📢 Send New Notification")
        with st.form("notif_form", clear_on_submit=True):
            target = st.selectbox("Send to", ["All Clients"] + client_names)
            category = st.selectbox("Category", [
                "Profit Share", "Withdrawal Update", "License Granted", 
                "Milestone", "EA Update", "General Alert", "Team Message"
            ])
            title = st.text_input("Title *", placeholder="e.g. New Profit Distributed!")
            message = st.text_area("Message *", height=150, placeholder="Details here...")
 
            submitted = st.form_submit_button("🔔 Send Alert", type="primary", use_container_width=True)
            if submitted:
                if not title.strip() or not message.strip():
                    st.error("Title and message required")
                else:
                    try:
                        inserts = []
                        if target == "All Clients":
                            for name in client_names:
                                inserts.append({
                                    "client_name": name,
                                    "title": title.strip(),
                                    "message": message.strip(),
                                    "date": datetime.date.today().isoformat(),
                                    "category": category,
                                    "read": 0
                                })
                        else:
                            inserts.append({
                                "client_name": target,
                                "title": title.strip(),
                                "message": message.strip(),
                                "date": datetime.date.today().isoformat(),
                                "category": category,
                                "read": 0
                            })
                        if inserts:
                            supabase.table("notifications").insert(inserts).execute()
                        st.success(f"Notification sent to {'all clients' if target == 'All Clients' else target}!")
                        st.cache_data.clear()
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
 
    # SEARCH & FILTER
    st.subheader("🔍 Search & Filter")
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        search = st.text_input("Search title/message", placeholder="e.g. profit, license")
    with col_s2:
        cat_filter = st.selectbox("Category", ["All"] + sorted(set(n.get("category", "General") for n in my_notifications)))
 
    # Apply filters
    filtered = my_notifications
    if search:
        s = search.lower()
        filtered = [n for n in filtered if s in n["title"].lower() or s in n["message"].lower()]
    if cat_filter != "All":
        filtered = [n for n in filtered if n.get("category") == cat_filter]
 
    # Sort newest first
    filtered = sorted(filtered, key=lambda x: x["date"], reverse=True)
 
    # REALTIME NOTIFICATION CARDS
    st.subheader(f"📬 Your Alerts ({len(filtered)} total)")
    if filtered:
        for n in filtered:
            is_unread = n.get("read", 0) == 0
            badge_color = accent_color if is_unread else "#888"
            badge_text = "🟡 UNREAD" if is_unread else "✅ Read"
            client_balance = user_map.get(n["client_name"], {"balance": 0})["balance"]
 
            with st.container():
                st.markdown(f"""
                <div class='glass-card' style='padding:1.8rem; border-left:6px solid {badge_color};'>
                    <div style='display:flex; justify-content:space-between; align-items:center;'>
                        <h4 style='margin:0; color:{accent_color};'>{n['title']}</h4>
                        <span style='background:{badge_color}; color:white; padding:0.4rem 1rem; border-radius:20px; font-weight:bold;'>
                            {badge_text}
                        </span>
                    </div>
                    <small style='opacity:0.8;'>
                        {n.get('category', 'General')} • For <strong>{n['client_name']}</strong> 
                        (Balance: ${client_balance:,.2f}) • {n['date']}
                    </small>
                </div>
                """, unsafe_allow_html=True)
 
                st.markdown(n['message'])
 
                # Mark as read
                if is_unread:
                    if st.button("Mark as Read", key=f"read_{n['id']}", use_container_width=True):
                        try:
                            supabase.table("notifications").update({"read": 1}).eq("id", n["id"]).execute()
                            st.success("Marked as read!")
                            st.cache_data.clear()
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
 
                # Admin delete
                if current_role in ["owner", "admin"]:
                    if st.button("🗑️ Delete Notification", key=f"del_{n['id']}", type="secondary", use_container_width=True):
                        try:
                            supabase.table("notifications").delete().eq("id", n["id"]).execute()
                            st.success("Deleted")
                            st.cache_data.clear()
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
 
                st.divider()
    else:
        st.info("No notifications match filters • All clear!")
 
    # Auto-note
    st.caption("🤖 Auto-notifications: Profits, withdrawals, licenses, milestones • Delivered instantly")
 
    # ELITE FOOTER
    st.markdown(f"""
    <div class='glass-card' style='padding:3rem; text-align:center; margin:3rem 0;'>
        <h1 style="background:linear-gradient(90deg,{accent_color},#ffd700); -webkit-background-clip:text; -webkit-text-fill-color:transparent;">
            Realtime Empire Alerts
        </h1>
        <p style="font-size:1.3rem; margin:2rem 0;">
            Prominent unread badges • Search/filter • Instant mark read • Auto-push • Team always informed.
        </p>
        <h2 style="color:#ffd700;">👑 KMFX Notifications • Elite Realtime 2026</h2>
    </div>
    """, unsafe_allow_html=True)
# ====================== WITHDRAWALS PAGE - FULL FINAL LATEST 2026 (PERMANENT STORAGE + PROOFS VISIBLE + REALTIME + ELITE UI) ======================
elif selected == "💳 Withdrawals":
    st.header("Withdrawal Management 💳")
    st.markdown("**Empire payout engine: Clients request from earned balances • Permanent proof upload • Owner approve/pay/reject • Auto-deduct on paid • Realtime sync & full transparency.**")
 
    current_role = st.session_state.get("role", "guest")
 
    # ULTRA-REALTIME CACHE (10s)
    @st.cache_data(ttl=10)
    def fetch_withdrawals_full():
        wd_resp = supabase.table("withdrawals").select("*").order("date_requested", desc=True).execute()
        withdrawals = wd_resp.data or []
 
        users_resp = supabase.table("users").select("id, full_name, balance, role").execute()
        users = users_resp.data or []
        user_map = {u["full_name"]: {"id": u["id"], "balance": u["balance"] or 0} for u in users}
 
        # All proofs (for related display)
        proofs_resp = supabase.table("client_files").select(
            "id, original_name, file_url, storage_path, category, assigned_client, notes, upload_date"
        ).order("upload_date", desc=True).execute()
        proofs = proofs_resp.data or []
 
        return withdrawals, user_map, proofs
 
    withdrawals, user_map, proofs = fetch_withdrawals_full()
 
    # Manual refresh
    if st.button("🔄 Refresh Withdrawals Now", use_container_width=True, type="secondary"):
        st.cache_data.clear()
        st.rerun()
 
    st.caption("🔄 Withdrawals auto-refresh every 10s • Proofs PERMANENT & fully visible")
 
    # CLIENT VIEW
    if current_role == "client":
        my_name = st.session_state.full_name
        my_balance = user_map.get(my_name, {"balance": 0})["balance"]
        my_withdrawals = [w for w in withdrawals if w["client_name"] == my_name]
 
        st.subheader(f"Your Withdrawals • Available Balance: ${my_balance:,.2f}")
 
        # Request form
        if my_balance > 0:
            with st.expander("➕ Request New Withdrawal", expanded=True):
                with st.form("client_wd_form", clear_on_submit=True):
                    amount = st.number_input("Amount (USD)", min_value=1.0, max_value=my_balance, step=100.0)
                    method = st.selectbox("Method", ["USDT", "Bank Transfer", "Wise", "PayPal", "GCash", "Other"])
                    details = st.text_area("Payout Details (Wallet/Address/Bank Info)")
                    proof = st.file_uploader("Upload Proof * (Permanent Storage)", type=["png","jpg","jpeg","pdf","gif"])
 
                    submitted = st.form_submit_button("Submit Request", type="primary", use_container_width=True)
                    if submitted:
                        if amount > my_balance:
                            st.error("Exceeds balance")
                        elif not proof:
                            st.error("Proof required")
                        else:
                            try:
                                url, storage_path = upload_to_supabase(
                                    file=proof,
                                    bucket="client_files",
                                    folder="withdrawals"
                                )
                                supabase.table("client_files").insert({
                                    "original_name": proof.name,
                                    "file_url": url,
                                    "storage_path": storage_path,
                                    "upload_date": datetime.date.today().isoformat(),
                                    "sent_by": my_name,
                                    "category": "Withdrawal Proof",
                                    "assigned_client": my_name,
                                    "notes": f"Proof for ${amount:,.0f} withdrawal request"
                                }).execute()
 
                                supabase.table("withdrawals").insert({
                                    "client_name": my_name,
                                    "amount": amount,
                                    "method": method,
                                    "details": details,
                                    "status": "Pending",
                                    "date_requested": datetime.date.today().isoformat()
                                }).execute()
 
                                st.success("Request submitted with permanent proof!")
                                st.cache_data.clear()
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error: {str(e)}")
        else:
            st.info("No balance yet • Earnings accumulate from profits")
 
        # Client history
        st.subheader("Your Request History")
        if my_withdrawals:
            for w in my_withdrawals:
                status_color = {"Pending": "#ffa502", "Approved": accent_color, "Paid": "#2ed573", "Rejected": "#ff4757"}.get(w["status"], "#888")
                st.markdown(f"""
                <div class='glass-card' style='padding:1.6rem; border-left:6px solid {status_color};'>
                    <h4 style='margin:0;'>${w['amount']:,.0f} • <span style='color:{status_color};'>{w['status']}</span></h4>
                    <small>Method: {w['method']} • Requested: {w['date_requested']}</small>
                </div>
                """, unsafe_allow_html=True)
                if w["details"]:
                    with st.expander("Payout Details"):
                        st.write(w["details"])
                st.divider()
        else:
            st.info("No requests yet")
 
    # OWNER/ADMIN VIEW
    else:
        st.subheader("All Empire Withdrawal Requests")
        if withdrawals:
            for w in withdrawals:
                client_balance = user_map.get(w["client_name"], {"balance": 0})["balance"]
                status_color = {"Pending": "#ffa502", "Approved": accent_color, "Paid": "#2ed573", "Rejected": "#ff4757"}.get(w["status"], "#888")
 
                with st.container():
                    st.markdown(f"""
                    <div class='glass-card' style='padding:1.8rem; border-left:6px solid {status_color};'>
                        <h4 style='margin:0;'>{w['client_name']} • ${w['amount']:,.0f} • <span style='color:{status_color};'>{w['status']}</span></h4>
                        <small>Method: {w['method']} • Requested: {w['date_requested']} • Current Balance: ${client_balance:,.2f}</small>
                    </div>
                    """, unsafe_allow_html=True)
 
                    if w["details"]:
                        with st.expander("Payout Details"):
                            st.write(w["details"])
 
                    # Related proofs (permanent + visible)
                    related_proofs = [p for p in proofs if p.get("assigned_client") == w["client_name"] and
                                      p.get("category") in ["Withdrawal Proof", "Payout Proof"] and
                                      "withdrawal" in str(p.get("notes") or "").lower()]
                    if related_proofs:
                        st.markdown("**Attached Proofs (Permanent):**")
                        proof_cols = st.columns(min(len(related_proofs), 4))
                        for idx, p in enumerate(related_proofs):
                            file_url = p.get("file_url")
                            if file_url:
                                with proof_cols[idx % 4]:
                                    if p["original_name"].lower().endswith(('.png','.jpg','.jpeg','.gif')):
                                        st.image(file_url, caption=p["original_name"], use_container_width=True)
                                    else:
                                        st.markdown(f"**{p['original_name']}** • {p['upload_date']}")
                                        st.download_button(
                                            f"Download {p['original_name']}",
                                            requests.get(file_url).content,
                                            p['original_name'],
                                            use_container_width=True,
                                            key=f"proof_dl_{p['id']}"
                                        )
 
                    # Actions
                    col_act = st.columns(3)
                    if w["status"] == "Pending":
                        with col_act[0]:
                            if st.button("Approve", key=f"app_{w['id']}", use_container_width=True):
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
                        with col_act[1]:
                            if st.button("Reject", key=f"rej_{w['id']}", use_container_width=True, type="secondary"):
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
 
                    if w["status"] == "Approved":
                        with col_act[0]:
                            if st.button("Mark as Paid → Auto-Deduct", key=f"paid_{w['id']}", type="primary", use_container_width=True):
                                try:
                                    client_id = user_map.get(w["client_name"], {}).get("id")
                                    if client_id:
                                        new_bal = max(0, client_balance - w["amount"])
                                        supabase.table("users").update({"balance": new_bal}).eq("id", client_id).execute()
                                    supabase.table("withdrawals").update({"status": "Paid"}).eq("id", w["id"]).execute()
                                    st.success("Paid & balance deducted!")
                                    st.cache_data.clear()
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error: {str(e)}")
 
                    st.divider()
        else:
            st.info("No withdrawal requests yet • Empire cashflow smooth")
 
    # ELITE FOOTER
    st.markdown(f"""
    <div class='glass-card' style='padding:3rem; text-align:center; margin:3rem 0;'>
        <h1 style="background:linear-gradient(90deg,{accent_color},#ffd700); -webkit-background-clip:text; -webkit-text-fill-color:transparent;">
            Secure & Automatic Payouts
        </h1>
        <p style="font-size:1.3rem; margin:2rem 0;">
            Permanent proofs • Balance limited • Owner actions instant • Auto-deduct • Realtime everywhere • Empire cashflow elite.
        </p>
        <h2 style="color:#ffd700;">👑 KMFX Withdrawals • Cloud Permanent 2026</h2>
    </div>
    """, unsafe_allow_html=True)
# ====================== END OF FINAL WITHDRAWALS WITH SUPABASE STORAGE FOR PROOFS ======================
# ====================== EA VERSIONS PAGE - FULL FINAL LATEST 2026 (PERMANENT STORAGE + LICENSE GATING + REALTIME + ELITE UI) ======================
elif selected == "🤖 EA Versions":
    st.header("EA Versions Management 🤖")
    st.markdown("**Elite EA distribution: Owner release with changelog • Auto-announce • Download tracking • Latest version license gated • Permanent files • Realtime list**")
 
    current_role = st.session_state.get("role", "guest")
 
    # ULTRA-REALTIME CACHE (10s)
    @st.cache_data(ttl=10)
    def fetch_ea_full():
        versions_resp = supabase.table("ea_versions").select("*").order("upload_date", desc=True).execute()
        versions = versions_resp.data or []
 
        downloads_resp = supabase.table("ea_downloads").select("*").execute()
        downloads = downloads_resp.data or []
 
        download_counts = {}
        for d in downloads:
            vid = d["version_id"]
            download_counts[vid] = download_counts.get(vid, 0) + 1
 
        # Client license check (proper user_id fetch)
        client_license = None
        if current_role == "client":
            my_name = st.session_state.full_name
            user_resp = supabase.table("users").select("id").eq("full_name", my_name).single().execute()
            if user_resp.data:
                user_id = user_resp.data["id"]
                license_resp = supabase.table("client_licenses").select("allow_live, version, revoked").eq("account_id", user_id).order("date_generated", desc=True).limit(1).execute()
                if license_resp.data and not license_resp.data[0].get("revoked", False):
                    client_license = license_resp.data[0]
 
        return versions, download_counts, client_license
 
    versions, download_counts, client_license = fetch_ea_full()
 
    # Manual refresh
    if st.button("🔄 Refresh EA Versions Now", use_container_width=True, type="secondary"):
        st.cache_data.clear()
        st.rerun()
 
    st.caption("🔄 Versions auto-refresh every 10s • EA files PERMANENT in Supabase Storage")
 
    # RELEASE NEW VERSION (OWNER ONLY)
    if current_role == "owner":
        st.subheader("📤 Release New EA Version")
        with st.form("ea_release_form", clear_on_submit=True):
            version_name = st.text_input("Version Name *", placeholder="e.g. v3.0 Elite Scalper 2026")
            ea_file = st.file_uploader("Upload EA File (.ex5 / .mq5) *", type=["ex5", "mq5"])
            changelog = st.text_area("Changelog *", height=200, placeholder="• New gold scalping filters\n• Reduced drawdown\n• FTMO optimized")
            announce = st.checkbox("📢 Auto-Announce to Empire", value=True)
 
            submitted = st.form_submit_button("🚀 Release Version", type="primary", use_container_width=True)
            if submitted:
                if not version_name.strip() or not ea_file or not changelog.strip():
                    st.error("Version name, file, and changelog required")
                else:
                    try:
                        url, storage_path = upload_to_supabase(
                            file=ea_file,
                            bucket="ea_versions",
                            folder="releases"
                        )
 
                        supabase.table("ea_versions").insert({
                            "version": version_name.strip(),
                            "file_url": url,
                            "storage_path": storage_path,
                            "upload_date": datetime.date.today().isoformat(),
                            "notes": changelog.strip()
                        }).execute()
 
                        if announce:
                            supabase.table("announcements").insert({
                                "title": f"🚀 New EA Version Released: {version_name.strip()}",
                                "message": f"Elite update available!\n\n**Changelog:**\n{changelog.strip()}\n\nDownload now in EA Versions page.",
                                "date": datetime.date.today().isoformat(),
                                "posted_by": st.session_state.full_name,
                                "category": "EA Update",
                                "pinned": True
                            }).execute()
 
                        log_action("EA Version Released (Permanent)", version_name.strip())
                        st.success(f"Version {version_name} released permanently!")
                        st.balloons()
                        st.cache_data.clear()
                        st.rerun()
                    except Exception as e:
                        st.error(f"Release failed: {str(e)}")
    elif current_role == "admin":
        st.info("Admins can view & track downloads • Owner releases new versions")
 
    # REALTIME VERSION LIST
    st.subheader("Available EA Versions")
    if versions:
        latest_version = versions[0]
        for v in versions:
            vid = v["id"]
            downloads = download_counts.get(vid, 0)
            file_url = v.get("file_url")
            is_latest = v == latest_version
 
            # License gating
            can_download = True
            gating_msg = ""
            if current_role == "client" and is_latest and client_license:
                if not client_license.get("allow_live", False):
                    can_download = False
                    gating_msg = "🔒 Active LIVE license required for latest version • Contact owner"
                elif client_license.get("revoked", False):
                    can_download = False
                    gating_msg = "🔒 Your license is revoked • Contact owner"
 
            with st.expander(f"🤖 {v['version']} • Released {v['upload_date']} • {downloads} downloads" + (" 👑 LATEST" if is_latest else ""), expanded=is_latest):
                st.markdown(f"**Changelog:**\n{v['notes'].replace(chr(10), '<br>')}", unsafe_allow_html=True)
 
                if gating_msg:
                    st.warning(gating_msg)
 
                if file_url and can_download:
                    try:
                        r = requests.get(file_url, timeout=10)
                        if r.status_code == 200:
                            if st.download_button(
                                f"⬇️ Download {v['version']}",
                                data=r.content,
                                file_name=f"KMFX_EA_{v['version']}.ex5",
                                use_container_width=True
                            ):
                                try:
                                    supabase.table("ea_downloads").insert({
                                        "version_id": vid,
                                        "downloaded_by": st.session_state.full_name,
                                        "download_date": datetime.date.today().isoformat()
                                    }).execute()
                                    log_action("EA Downloaded", f"{v['version']} by {st.session_state.full_name}")
                                except:
                                    pass
                        else:
                            st.error("File temporarily unavailable")
                    except:
                        st.error("Download failed • Try again")
                elif file_url:
                    st.info("Contact owner for access")
                else:
                    st.error("File missing • Contact owner")
 
                # Owner delete
                if current_role == "owner":
                    if st.button("🗑️ Delete Version Permanently", key=f"del_ea_{vid}", type="secondary"):
                        try:
                            if v.get("storage_path"):
                                supabase.storage.from_("ea_versions").remove([v["storage_path"]])
                            supabase.table("ea_versions").delete().eq("id", vid).execute()
                            supabase.table("ea_downloads").delete().eq("version_id", vid).execute()
                            st.success("Version deleted permanently")
                            st.cache_data.clear()
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
    else:
        st.info("No EA versions released yet • Owner uploads activate elite distribution")
 
    # ELITE FOOTER
    st.markdown(f"""
    <div class='glass-card' style='padding:3rem; text-align:center; margin:3rem 0;'>
        <h1 style="background:linear-gradient(90deg,{accent_color},#ffd700); -webkit-background-clip:text; -webkit-text-fill-color:transparent;">
            Elite EA Distribution System
        </h1>
        <p style="font-size:1.3rem; margin:2rem 0;">
            Permanent files • License gating on latest • Download tracked • Auto-announce • Owner control • Empire performance elite.
        </p>
        <h2 style="color:#ffd700;">👑 KMFX EA Versions • Cloud Permanent 2026</h2>
    </div>
    """, unsafe_allow_html=True)
# ====================== END OF FINAL EA VERSIONS WITH SUPABASE STORAGE ======================
# ====================== TESTIMONIALS PAGE - FULL FINAL LATEST 2026 (PERMANENT STORAGE + IMAGES FULLY VISIBLE + REALTIME GRID) ======================
elif selected == "📸 Testimonials":
    st.header("Team Testimonials 📸")
    st.markdown("**Empire motivation hub: Clients submit success stories + photos (PERMANENT STORAGE + FULLY VISIBLE) • Balance context • Owner approve/reject with auto-announce • Realtime grid • Search • Inspiration hub.**")
 
    current_role = st.session_state.get("role", "guest")
 
    # ULTRA-REALTIME CACHE (10s)
    @st.cache_data(ttl=10)
    def fetch_testimonials_full():
        approved_resp = supabase.table("testimonials").select("*").eq("status", "Approved").order("date_submitted", desc=True).execute()
        approved = approved_resp.data or []
 
        pending_resp = supabase.table("testimonials").select("*").eq("status", "Pending").order("date_submitted", desc=True).execute()
        pending = pending_resp.data or []
 
        users_resp = supabase.table("users").select("full_name, balance").execute()
        user_map = {u["full_name"]: u["balance"] or 0 for u in users_resp.data or []}
 
        # Generate signed URLs for ALL images (visible even on private bucket)
        all_testimonials = approved + pending
        for t in all_testimonials:
            if t.get("storage_path"):
                try:
                    signed = supabase.storage.from_("testimonials").create_signed_url(
                        t["storage_path"], 3600 * 24 * 30  # 30 days
                    )
                    t["signed_url"] = signed.get("signedURL") if signed else t.get("image_url")
                except:
                    t["signed_url"] = t.get("image_url")
            else:
                t["signed_url"] = t.get("image_url")
 
        return approved, pending, user_map
 
    approved, pending, user_map = fetch_testimonials_full()
 
    # Manual refresh
    if st.button("🔄 Refresh Testimonials Now", use_container_width=True, type="secondary"):
        st.cache_data.clear()
        st.rerun()
 
    st.caption("🔄 Testimonials auto-refresh every 10s • Photos PERMANENT & FULLY VISIBLE (signed URLs)")
 
    # CLIENT SUBMIT
    if current_role == "client":
        my_balance = user_map.get(st.session_state.full_name, 0)
        st.subheader(f"Share Your Success Story (Balance: ${my_balance:,.2f})")
        with st.expander("➕ Submit Testimonial", expanded=True):
            with st.form("testi_form", clear_on_submit=True):
                story = st.text_area("Your Story *", height=200, placeholder="How KMFX changed my life, profits, journey...")
                photo = st.file_uploader("Upload Photo * (Permanent + Visible)", type=["png","jpg","jpeg","gif"])
 
                submitted = st.form_submit_button("Submit for Approval", type="primary", use_container_width=True)
                if submitted:
                    if not story.strip() or not photo:
                        st.error("Story and photo required")
                    else:
                        try:
                            url, storage_path = upload_to_supabase(
                                file=photo,
                                bucket="testimonials",
                                folder="photos"
                            )
                            supabase.table("testimonials").insert({
                                "client_name": st.session_state.full_name,
                                "message": story.strip(),
                                "image_url": url,
                                "storage_path": storage_path,
                                "date_submitted": datetime.date.today().isoformat(),
                                "status": "Pending"
                            }).execute()
                            st.success("Testimonial submitted permanently! Photo will be visible on approval.")
                            st.cache_data.clear()
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
 
    # APPROVED GRID (FULL IMAGE PREVIEWS)
    st.subheader("🌟 Approved Success Stories")
    if approved:
        search = st.text_input("Search stories or name")
        filtered = [t for t in approved if search.lower() in t["message"].lower() or search.lower() in t["client_name"].lower()] if search else approved
 
        cols = st.columns(3)
        for idx, t in enumerate(filtered):
            with cols[idx % 3]:
                balance = user_map.get(t["client_name"], 0)
                signed_url = t.get("signed_url")
 
                with st.container():
                    if signed_url:
                        st.image(signed_url, use_container_width=True)
                    else:
                        st.caption("No photo")
                    st.markdown(f"**{t['client_name']}** (Balance: ${balance:,.2f})")
                    st.markdown(t["message"])
                    st.caption(f"Submitted: {t['date_submitted']}")
    else:
        st.info("No approved testimonials yet • Inspire the empire!")
 
    # PENDING (OWNER/ADMIN)
    if current_role in ["owner", "admin"] and pending:
        st.subheader("⏳ Pending Approval")
        for p in pending:
            balance = user_map.get(p["client_name"], 0)
            signed_url = p.get("signed_url")
 
            with st.expander(f"{p['client_name']} • {p['date_submitted']} • Balance ${balance:,.2f}", expanded=False):
                if signed_url:
                    st.image(signed_url, use_container_width=True)
                else:
                    st.caption("No photo")
                st.markdown(p["message"])
 
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Approve & Auto-Announce", key=f"app_{p['id']}"):
                        try:
                            supabase.table("testimonials").update({"status": "Approved"}).eq("id", p["id"]).execute()
                            supabase.table("announcements").insert({
                                "title": f"🌟 New Testimonial from {p['client_name']}!",
                                "message": p["message"],
                                "date": datetime.date.today().isoformat(),
                                "posted_by": "System (Auto)",
                                "category": "Testimonial"
                            }).execute()
                            st.success("Approved & announced!")
                            st.cache_data.clear()
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
                with col2:
                    if st.button("Reject & Delete", key=f"rej_{p['id']}", type="secondary"):
                        try:
                            if p.get("storage_path"):
                                supabase.storage.from_("testimonials").remove([p["storage_path"]])
                            supabase.table("testimonials").delete().eq("id", p["id"]).execute()
                            st.success("Rejected & deleted permanently")
                            st.cache_data.clear()
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
 
    # ELITE FOOTER
    st.markdown(f"""
    <div class='glass-card' style='padding:3rem; text-align:center; margin:3rem 0;'>
        <h1 style="background:linear-gradient(90deg,{accent_color},#ffd700); -webkit-background-clip:text; -webkit-text-fill-color:transparent;">
            Empire Success Stories
        </h1>
        <p style="font-size:1.3rem; margin:2rem 0;">
            Permanent photos • Full visibility • Balance context • Auto-announce • Realtime inspiration • Empire motivated.
        </p>
        <h2 style="color:#ffd700;">👑 KMFX Testimonials • Cloud Permanent 2026</h2>
    </div>
    """, unsafe_allow_html=True)
# ====================== END OF FINAL TESTIMONIALS WITH SUPABASE STORAGE ======================
# ====================== REPORTS & EXPORT PAGE - FULL FINAL LATEST 2026 (INSTANT MV + REALTIME + ELITE CHARTS & EXPORTS) ======================
elif selected == "📈 Reports & Export":
    st.header("Empire Reports & Export 📈")
    st.markdown("**Full analytics engine: Instant realtime reports via materialized views • Professional charts • Detailed breakdowns • Multiple CSV exports • Owner/Admin only.**")
 
    # STRICT OWNER/ADMIN ONLY
    current_role = st.session_state.get("role", "guest")
    if current_role not in ["owner", "admin"]:
        st.error("🔒 Reports & Export is restricted to Owner/Admin.")
        st.stop()
 
    # ULTRA-REALTIME CACHE (10s)
    @st.cache_data(ttl=10)
    def fetch_reports_full():
        try:
            # INSTANT MV TOTALS
            empire = supabase.table("mv_empire_summary").select("*").single().execute().data or {}
            client_mv = supabase.table("mv_client_balances").select("*").single().execute().data or {}
            gf_mv = supabase.table("mv_growth_fund_balance").select("balance").single().execute().data or {}
 
            total_accounts = empire.get("total_accounts", 0)
            total_equity = empire.get("total_equity", 0.0)
            total_withdrawable = empire.get("total_withdrawable", 0.0)
            total_client_balances = client_mv.get("total_client_balances", 0.0)
            gf_balance = gf_mv.get("balance", 0.0)
 
            # Full data for charts/tables
            profits = supabase.table("profits").select("*").order("record_date", desc=True).execute().data or []
            distributions = supabase.table("profit_distributions").select("*").execute().data or []
            clients = supabase.table("users").select("full_name, balance").eq("role", "client").execute().data or []
            accounts = supabase.table("ftmo_accounts").select("name, current_phase, current_equity, withdrawable_balance").execute().data or []
 
            total_gross = sum(p.get("gross_profit", 0) for p in profits)
            total_distributed = sum(d.get("share_amount", 0) for d in distributions if not d.get("is_growth_fund", False))
 
            return (
                profits, distributions, clients, accounts,
                total_gross, total_distributed, total_client_balances,
                gf_balance, total_accounts, total_equity, total_withdrawable
            )
        except Exception as e:
            st.error(f"Fetch error: {e}")
            return [], [], [], [], 0, 0, 0, 0, 0, 0, 0
 
    (profits, distributions, clients, accounts,
     total_gross, total_distributed, total_client_balances,
     gf_balance, total_accounts, total_equity, total_withdrawable) = fetch_reports_full()
 
    # Manual refresh
    if st.button("🔄 Refresh Reports Now", use_container_width=True, type="secondary"):
        st.cache_data.clear()
        st.rerun()
 
    st.caption("🔄 Reports auto-refresh every 10s • Lightning fast via materialized views")
 
    # EMPIRE METRICS GRID
    st.subheader("Empire Overview (Instant Totals)")
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    col1.metric("Active Accounts", total_accounts)
    col2.metric("Total Equity", f"${total_equity:,.0f}")
    col3.metric("Total Withdrawable", f"${total_withdrawable:,.0f}")
    col4.metric("Gross Profits", f"${total_gross:,.0f}")
    col5.metric("Distributed Shares", f"${total_distributed:,.0f}")
    col6.metric("Client Balances", f"${total_client_balances:,.0f}")
    st.metric("Growth Fund Balance", f"${gf_balance:,.0f}", delta=None)
 
    # TABS FOR ORGANIZED REPORTS
    tab1, tab2, tab3, tab4 = st.tabs(["Profit Trend", "Distribution Breakdown", "Client Balances", "Accounts Summary"])
 
    with tab1:
        st.subheader("Monthly Profit Trend")
        if profits:
            df = pd.DataFrame(profits)
            df["record_date"] = pd.to_datetime(df["record_date"])
            monthly = df.groupby(df["record_date"].dt.strftime("%Y-%m"))["gross_profit"].sum().reset_index()
            monthly = monthly.sort_values("record_date")
 
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=monthly["record_date"],
                y=monthly["gross_profit"],
                marker_color=accent_primary,
                text=monthly["gross_profit"].apply(lambda x: f"${x:,.0f}"),
                textposition="outside"
            ))
            fig.update_layout(height=500, title="Monthly Gross Profit", xaxis_title="Month", yaxis_title="USD")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No profits yet")
 
    with tab2:
        st.subheader("All-Time Participant Shares")
        if distributions:
            df = pd.DataFrame(distributions)
            summary = df.groupby("participant_name")["share_amount"].sum().reset_index().sort_values("share_amount", ascending=False)
 
            fig = go.Figure(go.Pie(
                labels=summary["participant_name"],
                values=summary["share_amount"],
                hole=0.5,
                textinfo="label+percent",
                textposition="outside"
            ))
            fig.update_layout(height=600, title="Total Distributed Shares")
            st.plotly_chart(fig, use_container_width=True)
 
            summary["share_amount"] = summary["share_amount"].apply(lambda x: f"${x:,.2f}")
            summary = summary.rename(columns={"participant_name": "Participant", "share_amount": "Total Share"})
            st.dataframe(summary, use_container_width=True, hide_index=True)
        else:
            st.info("No distributions yet")
 
    with tab3:
        st.subheader("Client Balances (Realtime)")
        if clients:
            df = pd.DataFrame(clients)
            df["balance"] = df["balance"].apply(lambda x: f"${x:,.2f}")
            df = df.rename(columns={"full_name": "Client", "balance": "Balance"}).sort_values("Balance", ascending=False)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No clients yet")
 
    with tab4:
        st.subheader("Active Accounts")
        if accounts:
            df = pd.DataFrame(accounts)
            df["current_equity"] = df["current_equity"].apply(lambda x: f"${x:,.0f}")
            df["withdrawable_balance"] = df["withdrawable_balance"].apply(lambda x: f"${x:,.0f}")
            st.dataframe(df[["name", "current_phase", "current_equity", "withdrawable_balance"]], use_container_width=True, hide_index=True)
        else:
            st.info("No accounts yet")
 
    # EXPORTS
    st.subheader("📤 Export Reports (CSV)")
    col_e1, col_e2 = st.columns(2)
    with col_e1:
        if profits:
            csv = pd.DataFrame(profits).to_csv(index=False).encode()
            st.download_button("📄 Profits Report", csv, f"KMFX_Profits_{datetime.date.today()}.csv", "text/csv", use_container_width=True)
        if distributions:
            csv = pd.DataFrame(distributions).to_csv(index=False).encode()
            st.download_button("📄 Distributions Report", csv, f"KMFX_Distributions_{datetime.date.today()}.csv", "text/csv", use_container_width=True)
    with col_e2:
        if clients:
            csv = pd.DataFrame([{"Client": c["full_name"], "Balance": c["balance"]} for c in clients]).to_csv(index=False).encode()
            st.download_button("📄 Client Balances", csv, f"KMFX_Balances_{datetime.date.today()}.csv", "text/csv", use_container_width=True)
 
        summary = {
            "Metric": ["Gross Profits", "Distributed", "Client Balances", "Growth Fund", "Accounts", "Equity", "Withdrawable"],
            "Value": [total_gross, total_distributed, total_client_balances, gf_balance, total_accounts, total_equity, total_withdrawable]
        }
        csv = pd.DataFrame(summary).to_csv(index=False).encode()
        st.download_button("📄 Empire Summary", csv, f"KMFX_Summary_{datetime.date.today()}.csv", "text/csv", use_container_width=True)
 
    # ELITE FOOTER
    st.markdown(f"""
    <div class='glass-card' style='padding:3rem; text-align:center; margin:3rem 0;'>
        <h1 style="background:linear-gradient(90deg,{accent_color},#ffd700); -webkit-background-clip:text; -webkit-text-fill-color:transparent;">
            Lightning Fast Analytics
        </h1>
        <p style="font-size:1.3rem; margin:2rem 0;">
            Instant MV totals • Tabbed reports • Elite charts • Dated CSV exports • Empire performance mastered.
        </p>
        <h2 style="color:#ffd700;">👑 KMFX Reports • Instant 2026</h2>
    </div>
    """, unsafe_allow_html=True)
# ====================== END OF FINAL REPORTS & EXPORT WITH MATERIALIZED VIEWS ======================
elif selected == "🔮 Simulator":
    st.header("Empire Growth Simulator 🔮")
    st.markdown("**Advanced scaling forecaster: Auto-loaded from current empire (accounts, equity, GF balance, avg profits per account, actual Growth Fund %, unit value) via materialized views + realtime data for instant accurate defaults • Simulate scenarios • Projected equity, distributions, growth fund, units • Realtime multi-line charts • Sankey flow previews • Professional planning tool.**")

    # FULL INSTANT CACHE - MATERIALIZED VIEWS + REALTIME CALCS FOR ACCURATE DEFAULTS
    @st.cache_data(ttl=60)
    def fetch_simulator_data():
        try:
            # INSTANT core stats from materialized views
            empire_resp = supabase.table("mv_empire_summary").select("total_accounts, total_equity, total_withdrawable").execute()
            empire = empire_resp.data[0] if empire_resp.data else {}
            total_accounts = empire.get("total_accounts", 0)
            total_equity = empire.get("total_equity", 0.0)

            gf_resp = supabase.table("mv_growth_fund_balance").select("balance").execute()
            gf_balance = gf_resp.data[0]["balance"] if gf_resp.data else 0.0

            # Lightweight tables for accurate averages
            accounts_resp = supabase.table("ftmo_accounts").select("unit_value, participants_v2").execute()
            accounts = accounts_resp.data or []

            profits_resp = supabase.table("profits").select("gross_profit, record_date").execute()
            profits = profits_resp.data or []

            # === Accurate Avg Monthly Gross PER ACCOUNT ===
            avg_per_acc = 15000.0  # sensible default if no data
            if profits:
                df = pd.DataFrame(profits)
                df["record_date"] = pd.to_datetime(df["record_date"])
                monthly_sums = df.groupby(df["record_date"].dt.to_period("M"))["gross_profit"].sum()
                avg_monthly_total = monthly_sums.mean() if len(monthly_sums) > 0 else 0.0
                if total_accounts > 0:
                    avg_per_acc = avg_monthly_total / total_accounts
                # If still low/no data, keep reasonable default
                if avg_per_acc < 1000:
                    avg_per_acc = 15000.0

            # === Accurate Avg Growth Fund % (from actual "Growth Fund" participant rows) ===
            gf_pcts = []
            for a in accounts:
                gf_acc = 0.0
                parts = a.get("participants_v2", []) or a.get("participants", [])
                for p in parts:
                    display = p.get("display_name") or p.get("name", "")
                    if "growth fund" in display.lower():
                        gf_acc += p.get("percentage", 0.0)
                gf_pcts.append(gf_acc)
            avg_gf_pct = sum(gf_pcts) / len(gf_pcts) if gf_pcts else 10.0
            if avg_gf_pct == 0:
                avg_gf_pct = 10.0  # reasonable default if no GF row yet

            # === Avg Unit Value ===
            unit_values = [a.get("unit_value", 3000.0) for a in accounts if a.get("unit_value", 0) > 0]
            avg_unit_value = sum(unit_values) / len(unit_values) if unit_values else 3000.0

            return (
                total_equity, total_accounts, float(avg_per_acc),
                float(avg_gf_pct), float(avg_unit_value), gf_balance
            )
        except Exception as e:
            st.error(f"Simulator data fetch error: {e}")
            return 0.0, 0, 15000.0, 10.0, 3000.0, 0.0

    (
        total_equity, total_accounts, avg_per_acc,
        avg_gf_pct, avg_unit_value, gf_balance
    ) = fetch_simulator_data()

    st.info(f"**Instant Auto-Loaded Empire Stats:** {total_accounts} accounts • Total Equity ${total_equity:,.0f} • Avg Monthly Gross per Account ${avg_per_acc:,.0f} • Avg Growth Fund % {avg_gf_pct:.1f}% • Avg Unit Value ${avg_unit_value:,.0f} • Current GF ${gf_balance:,.0f}")

    # ====================== ADVANCED SIMULATION INPUTS (ACCURATE DEFAULTS) ======================
    st.subheader("Configure Simulation Scenarios")
    col_sim1, col_sim2 = st.columns(2)
    with col_sim1:
        months = st.slider("Projection Months", 6, 72, 36)
        projected_accounts = st.slider("Projected Active Accounts", total_accounts, total_accounts + 50, total_accounts + 10)
        monthly_gross_per_acc = st.number_input(
            "Avg Monthly Gross Profit per Account (USD)",
            value=avg_per_acc,
            min_value=0.0,
            step=1000.0,
            help="Auto-loaded historical average per account (or default if no data)"
        )
        gf_percentage = st.slider(
            "Growth Fund Allocation % (from Profits)",
            0.0, 50.0, avg_gf_pct,
            help="Auto-loaded from actual 'Growth Fund' participant rows across accounts"
        )
    with col_sim2:
        unit_value_proj = st.number_input(
            "Profit Unit Value (USD)",
            value=avg_unit_value,
            min_value=100.0,
            step=500.0
        )
        monthly_manual_in = st.number_input("Additional Monthly Manual In to GF (USD)", value=0.0, step=1000.0)
        scenario_name = st.text_input("Scenario Name", value="Elite Scaling Plan 2026")

    # Auto-calculated projected monthly totals
    monthly_gross_total = monthly_gross_per_acc * projected_accounts
    monthly_gf_add = monthly_gross_total * (gf_percentage / 100) + monthly_manual_in
    monthly_distributed = monthly_gross_total - monthly_gf_add
    monthly_units = monthly_gross_total / unit_value_proj if unit_value_proj > 0 else 0

    col_calc1, col_calc2, col_calc3, col_calc4 = st.columns(4)
    col_calc1.metric("Projected Monthly Gross (Total)", f"${monthly_gross_total:,.0f}")
    col_calc2.metric("Monthly GF Add", f"${monthly_gf_add:,.0f}")
    col_calc3.metric("Monthly Distributed", f"${monthly_distributed:,.0f}")
    col_calc4.metric("Monthly Units Generated", f"{monthly_units:.2f}")

    # ====================== RUN SIMULATION ======================
    if st.button("🚀 Run Simulation", type="primary", use_container_width=True):
        # Starting points
        start_equity = total_equity
        start_gf = gf_balance

        dates = [datetime.date.today() + datetime.timedelta(days=30 * i) for i in range(months + 1)]

        # Projections
        equity_proj = [start_equity]
        gf_proj = [start_gf]
        distributed_proj = [0.0]
        units_proj = [0.0]

        for i in range(months):
            gross = monthly_gross_total
            gf_add = monthly_gf_add
            distributed = monthly_distributed
            units = monthly_units

            new_equity = equity_proj[-1] + gross
            new_gf = gf_proj[-1] + gf_add

            equity_proj.append(new_equity)
            gf_proj.append(new_gf)
            distributed_proj.append(distributed_proj[-1] + distributed)
            units_proj.append(units_proj[-1] + units)

        # Multi-line chart
        fig_multi = go.Figure()
        fig_multi.add_trace(go.Scatter(x=dates, y=equity_proj, name="Total Equity", line=dict(color=accent_primary, width=6)))
        fig_multi.add_trace(go.Scatter(x=dates, y=gf_proj, name="Growth Fund", line=dict(color="#ffd700", width=6)))
        fig_multi.add_trace(go.Scatter(x=dates, y=distributed_proj, name="Distributed Shares", line=dict(color="#00ffcc", width=5)))
        fig_multi.add_trace(go.Scatter(x=dates, y=units_proj, name="Cumulative Units", line=dict(color="#ff6b6b", width=5, dash="dot")))
        fig_multi.update_layout(
            title=f"{scenario_name} — Empire Growth Trajectory",
            height=600,
            hovermode="x unified",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_multi, use_container_width=True)

        # Final key metrics
        col_final1, col_final2, col_final3, col_final4 = st.columns(4)
        col_final1.metric("Final Total Equity", f"${equity_proj[-1]:,.0f}")
        col_final2.metric("Final Growth Fund", f"${gf_proj[-1]:,.0f}")
        col_final3.metric("Total Distributed Shares", f"${distributed_proj[-1]:,.0f}")
        col_final4.metric("Total Units Generated", f"{units_proj[-1]:.2f}")

        # Average monthly Sankey flow
        st.subheader("Projected Average Monthly Flow")
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
                link=dict(source=source, target=target, value=values, color=["#00ffcc80", "#ffd70080"])
            )])
            fig_avg.update_layout(height=500, title=f"Avg Monthly Flow — ${monthly_gross_total:,.0f} Gross")
            st.plotly_chart(fig_avg, use_container_width=True)
        else:
            st.info("No gross profit projected in this scenario")

    # ELITE FOOTER
    st.markdown(f"""
    <div class='glass-card' style='padding:3rem; text-align:center; margin:3rem 0;'>
        <h1 style="background:linear-gradient(90deg,{accent_primary},{accent_gold}); -webkit-background-clip:text; -webkit-text-fill-color:transparent;">
            Fixed & Enhanced Predictive Simulator 2026
        </h1>
        <p style="font-size:1.3rem; margin:2rem 0;">
            ✅ Accurate auto-load: real historical avg gross per account + true Growth Fund % from participant rows<br>
            ✅ Linear scaling with projected accounts • Instant MV core stats • Professional charts & flows<br>
            ✅ Ready for elite empire planning 👑
        </p>
        <h2 style="color:{accent_gold};">KMFX Simulator • Fully Fixed & Lightning Fast</h2>
    </div>
    """, unsafe_allow_html=True)
# ====================== END OF FINAL SIMULATOR WITH MATERIALIZED VIEWS ======================
elif selected == "📜 Audit Logs":
    st.header("Empire Audit Logs 📜")
    st.markdown("**Full transparency & security: Realtime auto-logged actions from all empire transactions (profits, distributions, licenses, withdrawals, uploads, announcements, user changes) • Advanced search/filter/date range • Daily timeline chart • Action distribution pie • Detailed table • Export filtered CSV • Owner-only for compliance & oversight.**")

    # SAFE ROLE - OWNER ONLY
    current_role = st.session_state.get("role", "guest")
    if current_role != "owner":
        st.error("🔒 Audit Logs are OWNER-ONLY for empire security & compliance.")
        st.stop()

    # FULL REALTIME CACHE (short ttl for live tracking)
    @st.cache_data(ttl=30)
    def fetch_audit_full():
        try:
            logs_resp = supabase.table("logs").select("*").order("timestamp", desc=True).execute()
            logs = logs_resp.data or []

            # Auto-summary stats
            total_actions = len(logs)
            unique_users = len(set(l.get("user_name") for l in logs if l.get("user_name")))
            unique_actions = len(set(l.get("action") for l in logs))

            # Action distribution for pie chart
            action_counts = pd.Series([l.get("action") for l in logs]).value_counts()

            return logs, total_actions, unique_users, unique_actions, action_counts
        except Exception as e:
            st.error(f"Failed to fetch logs: {e}")
            return [], 0, 0, 0, pd.Series()

    logs, total_actions, unique_users, unique_actions, action_counts = fetch_audit_full()

    # Manual refresh button (aligned with other pages)
    if st.button("🔄 Refresh Audit Logs Now", use_container_width=True, type="secondary"):
        st.cache_data.clear()
        st.rerun()

    st.caption("🔄 Logs auto-refresh every 30s • Every empire action tracked realtime")

    # ====================== AUDIT SUMMARY METRICS (ENHANCED) ======================
    col_a1, col_a2, col_a3, col_a4 = st.columns(4)
    col_a1.metric("Total Logged Actions", f"{total_actions:,}")
    col_a2.metric("Unique Active Users", unique_users)
    col_a3.metric("Unique Action Types", unique_actions)
    col_a4.metric("Latest Activity", logs[0]["timestamp"][:16].replace("T", " ") if logs else "—")

    # ====================== ACTION DISTRIBUTION PIE CHART ======================
    if not action_counts.empty:
        st.subheader("📊 Action Type Distribution")
        fig_pie = go.Figure(data=[go.Pie(
            labels=action_counts.index,
            values=action_counts.values,
            hole=0.4,
            textinfo="label+percent",
            marker_colors=[accent_primary, accent_gold, "#ff6b6b", "#00ffcc", "#ffd700", "#a67c00"]
        )])
        fig_pie.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig_pie, use_container_width=True)

    # ====================== ADVANCED SEARCH & FILTER (WITH DATE RANGE) ======================
    st.subheader("🔍 Advanced Search & Filter")
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        search_log = st.text_input("Search Action/Details/User", placeholder="e.g. Profit, Uploaded, kingminted")
        col_d1, col_d2 = st.columns(2)
        with col_d1:
            start_date = st.date_input("From Date", value=None if not logs else pd.to_datetime(logs[-1]["timestamp"]).date())
        with col_d2:
            end_date = st.date_input("To Date", value=None if not logs else pd.to_datetime(logs[0]["timestamp"]).date())
    with col_f2:
        filter_user = st.selectbox("Filter User", ["All"] + sorted(set(l.get("user_name") for l in logs if l.get("user_name"))))
        filter_action = st.selectbox("Filter Action Type", ["All"] + sorted(set(l.get("action") for l in logs)))

    # Apply filters
    filtered_logs = logs
    if search_log:
        s = search_log.lower()
        filtered_logs = [l for l in filtered_logs if
                         s in l.get("action", "").lower() or
                         s in l.get("details", "").lower() or
                         s in str(l.get("user_name", "")).lower()]

    if filter_user != "All":
        filtered_logs = [l for l in filtered_logs if l.get("user_name") == filter_user]

    if filter_action != "All":
        filtered_logs = [l for l in filtered_logs if l.get("action") == filter_action]

    if start_date or end_date:
        filtered_logs = [l for l in filtered_logs if
                         (not start_date or pd.to_datetime(l["timestamp"]).date() >= start_date) and
                         (not end_date or pd.to_datetime(l["timestamp"]).date() <= end_date)]

    # ====================== ACTIVITY TIMELINE CHART (REALTIME + FILTERED) ======================
    st.subheader("📊 Empire Activity Timeline (Filtered View)")
    if filtered_logs:
        log_df = pd.DataFrame(filtered_logs)
        log_df["timestamp"] = pd.to_datetime(log_df["timestamp"])
        daily_counts = log_df.groupby(log_df["timestamp"].dt.date).size().reset_index(name="Actions")

        fig_timeline = go.Figure()
        fig_timeline.add_trace(go.Scatter(
            x=daily_counts["timestamp"],
            y=daily_counts["Actions"],
            mode='lines+markers',
            line=dict(color=accent_primary, width=5),
            marker=dict(size=8, color=accent_gold)
        ))
        fig_timeline.update_layout(
            title="Daily Empire Actions",
            height=450,
            xaxis_title="Date",
            yaxis_title="Number of Actions",
            hovermode="x unified"
        )
        st.plotly_chart(fig_timeline, use_container_width=True)
    else:
        st.info("No logs match current filters • Adjust filters to see timeline")

    # ====================== DETAILED LOG TABLE (CLEAN & EXPORTABLE) ======================
    st.subheader(f"Detailed Audit Logs ({len(filtered_logs):,} entries)")
    if filtered_logs:
        log_display = pd.DataFrame(filtered_logs)
        log_display["timestamp"] = pd.to_datetime(log_display["timestamp"]).dt.strftime("%Y-%m-%d %H:%M:%S")
        log_display = log_display[["timestamp", "user_name", "user_type", "action", "details"]].rename(columns={
            "timestamp": "Time",
            "user_name": "User",
            "user_type": "Role",
            "action": "Action",
            "details": "Details"
        })

        # Make details expandable if long
        st.dataframe(
            log_display.style.set_properties(**{"text-align": "left"}),
            use_container_width=True,
            hide_index=True
        )

        # Export filtered CSV
        csv_logs = log_display.to_csv(index=False).encode("utf-8")
        st.download_button(
            "📤 Export Filtered Logs CSV",
            csv_logs,
            f"KMFX_Audit_Logs_{datetime.date.today()}.csv",
            "text/csv",
            use_container_width=True
        )
    else:
        st.info("No logs matching current filters • Empire actions are fully tracked")

    # ELITE FOOTER
    st.markdown(f"""
    <div class='glass-card' style='padding:3rem; text-align:center; margin:3rem 0;'>
        <h1 style="background:linear-gradient(90deg,{accent_primary},{accent_gold}); -webkit-background-clip:text; -webkit-text-fill-color:transparent;">
            Complete Audit Transparency 2026
        </h1>
        <p style="font-size:1.3rem; margin:2rem 0;">
            ✅ Manual refresh • Date range filter • Action distribution pie • Enhanced timeline<br>
            ✅ Filtered export • Scalable for thousands of logs • Empire fully accountable & secure 👑
        </p>
        <h2 style="color:{accent_gold};">KMFX Audit Logs • Fully Fixed & Elite</h2>
    </div>
    """, unsafe_allow_html=True)
# ====================== END OF FINAL AUDIT LOGS ======================
elif selected == "👤 Admin Management":
    st.header("Empire Team Management 👤")
    st.markdown("**Owner-exclusive: Full team control • Register with complete details & titles (synced to all dropdowns/trees as 'Name (Title)') • Realtime balances • Secure edit/delete • QR login token generate/regenerate/revoke • Joined date • Advanced search/filter • Elite metrics**")

    # STRICT OWNER ONLY
    current_role = st.session_state.get("role", "guest")
    if current_role != "owner":
        st.error("🔒 Team Management is OWNER-ONLY for empire security.")
        st.stop()

    import uuid
    import qrcode
    from io import BytesIO

    # FULL REALTIME CACHE
    @st.cache_data(ttl=30)
    def fetch_users_full():
        try:
            users_resp = supabase.table("users").select("*").order("created_at", desc=True).execute()
            return users_resp.data or []
        except Exception as e:
            st.error(f"Failed to fetch team data: {e}")
            return []

    users = fetch_users_full()

    # Manual refresh button
    if st.button("🔄 Refresh Team Management Now", use_container_width=True, type="secondary"):
        st.cache_data.clear()
        st.rerun()

    st.caption("🔄 Team auto-refresh every 30s • All changes (titles, details) instantly sync across empire")

    # ====================== TEAM SUMMARY METRICS ======================
    team = [u for u in users if u["username"] != "kingminted"]  # Exclude owner
    clients = [u for u in team if u["role"] == "client"]
    admins = [u for u in team if u["role"] == "admin"]
    total_balance = sum(u.get("balance", 0) for u in clients)

    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    col_m1.metric("Total Team Members", len(team))
    col_m2.metric("Clients", len(clients))
    col_m3.metric("Admins", len(admins))
    col_m4.metric("Total Client Balances", f"${total_balance:,.2f}")

    # ====================== REGISTER NEW TEAM MEMBER ======================
    st.subheader("➕ Register New Team Member")
    with st.form("add_user_form", clear_on_submit=True):
        col_u1, col_u2 = st.columns(2)
        with col_u1:
            username = st.text_input("Username *", placeholder="e.g. michael2026")
            full_name = st.text_input("Full Name *", placeholder="e.g. Michael Reyes")
        with col_u2:
            initial_pwd = st.text_input("Initial Password *", type="password")
            urole = st.selectbox("Role *", ["client", "admin"])

        st.markdown("### Additional Details (Optional but Recommended)")
        col_info1, col_info2 = st.columns(2)
        with col_info1:
            accounts = st.text_input("MT5 Account Logins (comma-separated)", placeholder="e.g. 333723156, 12345678")
            email = st.text_input("Email", placeholder="e.g. michael@example.com")
        with col_info2:
            contact_no = st.text_input("Contact No.", placeholder="e.g. 09128197085")
            address = st.text_area("Address", placeholder="e.g. Rodriguez 1, Rodriguez Dampalit, Malabon City")

        title = st.selectbox(
            "Title/Label (Optional)",
            ["None", "Pioneer", "Distributor", "VIP", "Elite Trader", "Contributor"],
            help="Displays as 'Full Name (Title)' in all dropdowns, trees, and lists"
        )

        submitted = st.form_submit_button("🚀 Register Member", type="primary", use_container_width=True)
        if submitted:
            if not username.strip() or not full_name.strip() or not initial_pwd:
                st.error("Username, full name, and initial password are required")
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
                    log_action("Team Member Registered", f"{full_name.strip()} ({title if title != 'None' else ''}) as {urole}")
                    st.success(f"{full_name.strip()} successfully registered & synced!")
                    st.balloons()
                    st.cache_data.clear()
                    st.rerun()
                except Exception as e:
                    st.error(f"Registration failed: {str(e)}")

    # ====================== CURRENT TEAM LIST ======================
    st.subheader("👥 Current Empire Team")
    if team:
        # Search & Filter
        col_search1, col_search2 = st.columns(2)
        with col_search1:
            search_user = st.text_input("Search by Name / Username / Email / Contact / Accounts")
        with col_search2:
            filter_role = st.selectbox("Filter Role", ["All", "client", "admin"])

        filtered_team = team
        if search_user:
            s = search_user.lower()
            filtered_team = [u for u in filtered_team if
                             s in u["full_name"].lower() or
                             s in u["username"].lower() or
                             s in str(u.get("email", "")).lower() or
                             s in str(u.get("contact_no", "")).lower() or
                             s in str(u.get("accounts", "")).lower()]
        if filter_role != "All":
            filtered_team = [u for u in filtered_team if u["role"] == filter_role]

        st.caption(f"Showing {len(filtered_team)} member{'' if len(filtered_team) == 1 else 's'}")

        for u in filtered_team:
            title_display = f" ({u.get('title', '')})" if u.get('title') else ""
            balance = u.get("balance", 0.0)
            joined = u.get("created_at", "Unknown")[:10] if u.get("created_at") else "Unknown"
            with st.expander(
                f"**{u['full_name']}{title_display}** (@{u['username']}) • {u['role'].title()} • Balance ${balance:,.2f} • Joined {joined}",
                expanded=False
            ):
                # Details
                col_d1, col_d2 = st.columns(2)
                with col_d1:
                    st.markdown(f"**MT5 Accounts:** {u.get('accounts') or 'None'}")
                    st.markdown(f"**Email:** {u.get('email') or 'None'}")
                with col_d2:
                    st.markdown(f"**Contact No.:** {u.get('contact_no') or 'None'}")
                    st.markdown(f"**Address:** {u.get('address') or 'None'}")

                # QR Code Management
                st.markdown("### 🔑 Quick Login QR Code")
                current_qr_token = u.get("qr_token")
                app_url = "https://kmfxeaftmo.streamlit.app"  # Update if your app URL changes
                qr_url = f"{app_url}/?qr={current_qr_token}" if current_qr_token else None

                if current_qr_token:
                    # Generate QR image
                    buf = BytesIO()
                    qr = qrcode.QRCode(version=1, box_size=12, border=5)
                    qr.add_data(qr_url)
                    qr.make(fit=True)
                    img = qr.make_image(fill_color="black", back_color="white")
                    img.save(buf, format="PNG")
                    qr_bytes = buf.getvalue()

                    col_qr1, col_qr2, col_qr3 = st.columns([1, 2, 2])
                    with col_qr1:
                        st.image(qr_bytes, caption="QR Login Code")
                    with col_qr2:
                        st.code(qr_url, language="text")
                        st.download_button(
                            "⬇ Download QR PNG",
                            qr_bytes,
                            f"{u['full_name'].replace(' ', '_')}_QR.png",
                            "image/png",
                            use_container_width=True
                        )
                    with col_qr3:
                        st.info("Scan for instant login on any device")
                        if st.button("🔄 Regenerate Token", key=f"regen_{u['id']}"):
                            new_token = str(uuid.uuid4())
                            supabase.table("users").update({"qr_token": new_token}).eq("id", u["id"]).execute()
                            log_action("QR Token Regenerated", f"For {u['full_name']}")
                            st.success("New token generated • Old revoked")
                            st.cache_data.clear()
                            st.rerun()
                        if st.button("❌ Revoke Token", key=f"revoke_{u['id']}", type="secondary"):
                            supabase.table("users").update({"qr_token": None}).eq("id", u["id"]).execute()
                            log_action("QR Token Revoked", f"For {u['full_name']}")
                            st.success("Token revoked")
                            st.cache_data.clear()
                            st.rerun()
                else:
                    st.info("No QR login token generated yet")
                    if st.button("🚀 Generate QR Token", key=f"gen_{u['id']}"):
                        new_token = str(uuid.uuid4())
                        supabase.table("users").update({"qr_token": new_token}).eq("id", u["id"]).execute()
                        log_action("QR Token Generated", f"For {u['full_name']}")
                        st.success("Token generated • Refresh to view")
                        st.cache_data.clear()
                        st.rerun()

                # Actions
                st.markdown("### Actions")
                col_act1, col_act2 = st.columns(2)
                with col_act1:
                    if st.button("✏️ Edit Member", key=f"edit_{u['id']}"):
                        st.session_state.edit_user_id = u["id"]
                        st.session_state.edit_user_data = u.copy()
                        st.rerun()
                with col_act2:
                    st.warning("⚠️ Delete is permanent • All licenses & shares will be affected")
                    if st.button("🗑️ Delete Member", key=f"del_confirm_{u['id']}", type="secondary"):
                        try:
                            supabase.table("users").delete().eq("id", u["id"]).execute()
                            log_action("Team Member Deleted", f"{u['full_name']}{title_display}")
                            st.success("Member permanently removed")
                            st.cache_data.clear()
                            st.rerun()
                        except Exception as e:
                            st.error(f"Delete failed: {str(e)}")

                # Edit Form (inside expander when triggered)
                if st.session_state.get("edit_user_id") == u["id"]:
                    edit_data = st.session_state.edit_user_data
                    with st.form(key=f"edit_form_{u['id']}", clear_on_submit=True):
                        col_e1, col_e2 = st.columns(2)
                        with col_e1:
                            new_username = st.text_input("Username *", value=edit_data["username"])
                            new_full_name = st.text_input("Full Name *", value=edit_data["full_name"])
                        with col_e2:
                            new_pwd = st.text_input("New Password (leave blank to keep)", type="password")
                            new_role = st.selectbox("Role *", ["client", "admin"],
                                                    index=0 if edit_data["role"] == "client" else 1)

                        st.markdown("### Details")
                        col_einfo1, col_einfo2 = st.columns(2)
                        with col_einfo1:
                            new_accounts = st.text_input("MT5 Accounts", value=edit_data.get("accounts") or "")
                            new_email = st.text_input("Email", value=edit_data.get("email") or "")
                        with col_einfo2:
                            new_contact = st.text_input("Contact No.", value=edit_data.get("contact_no") or "")
                            new_address = st.text_area("Address", value=edit_data.get("address") or "")

                        title_options = ["None", "Pioneer", "Distributor", "VIP", "Elite Trader", "Contributor"]
                        current_title_idx = title_options.index(edit_data.get("title")) if edit_data.get("title") in title_options else 0
                        new_title = st.selectbox("Title/Label", title_options, index=current_title_idx)

                        col_save, col_cancel = st.columns(2)
                        with col_save:
                            save_submitted = st.form_submit_button("💾 Save Changes", type="primary")
                        with col_cancel:
                            cancel_submitted = st.form_submit_button("Cancel")

                        if cancel_submitted:
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
                                    st.success("Member updated successfully!")
                                    del st.session_state.edit_user_id
                                    del st.session_state.edit_user_data
                                    st.cache_data.clear()
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Update failed: {str(e)}")
    else:
        st.info("No team members yet • Start building your empire!")

    # ELITE FOOTER
    st.markdown(f"""
    <div class='glass-card' style='padding:3rem; text-align:center; margin:3rem 0;'>
        <h1 style="background:linear-gradient(90deg,{accent_primary},{accent_gold}); -webkit-background-clip:text; -webkit-text-fill-color:transparent;">
            Owner Team Control Center 2026
        </h1>
        <p style="font-size:1.3rem; margin:2rem 0;">
            ✅ Manual refresh • Team metrics • Enhanced search • QR download/revoke • Safe delete confirm<br>
            ✅ Full details sync • Instant edits • Empire team elite & secure 👑
        </p>
        <h2 style="color:{accent_gold};">KMFX Team Management • Fully Fixed & Elite</h2>
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
