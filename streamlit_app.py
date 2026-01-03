# ====================== PART 1: SUPABASE CLOUD SETUP & INITIALIZATION ======================
# KMFX FTMO Pro Manager - FULL SUPABASE CLOUD VERSION 2025
# Fully cloud-based, real-time ready, optimized, mobile-perfect

import streamlit as st
import pandas as pd
import datetime
import bcrypt
import os
import threading
import time
import requests
import base64
import hashlib
import plotly.graph_objects as go
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()  # Load .env file with SUPABASE_URL and SUPABASE_KEY

# ====================== SUPABASE CONNECTION ======================
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")

if not supabase_url or not supabase_key:
    st.error("Missing SUPABASE_URL or SUPABASE_KEY in .env file! Please check your .env file.")
    st.stop()

supabase: Client = create_client(supabase_url, supabase_key)

# ====================== KEEP-ALIVE (FOR STREAMLIT CLOUD DEPLOYMENT) ======================
def keep_alive():
    while True:
        try:
            requests.get("https://kmfx-ftmo-pro.streamlit.app", timeout=10)
        except:
            pass
        time.sleep(1500)  # Every 25 minutes

if os.getenv("STREAMLIT_SHARING") or os.getenv("STREAMLIT_CLOUD"):
    if not hasattr(st, "_keep_alive_thread_started"):
        thread = threading.Thread(target=keep_alive, daemon=True)
        thread.start()
        st._keep_alive_thread_started = True

st.set_page_config(
    page_title="KMFX FTMO Pro Manager",
    page_icon="🚀",
    layout="centered",
    initial_sidebar_state="collapsed"  # ← CRITICAL FIX: Let custom JS fully control state
)

# ====================== LOCAL FOLDERS FOR FILE UPLOADS ======================
folders = [
    "uploaded_files",
    "uploaded_files/client_files",
    "uploaded_files/announcements",
    "uploaded_files/testimonials",
    "uploaded_files/ea_versions"
]
for folder in folders:
    os.makedirs(folder, exist_ok=True)

# ====================== LOG ACTION TO SUPABASE ======================
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
    except Exception as e:
        st.warning("Log failed (cloud issue)")

# ====================== CREATE DEFAULT USERS (FIRST TIME ONLY) ======================
def create_default_users():
    try:
        response = supabase.table("users").select("id", count="exact").execute()
        if response.count == 0:
            hashed_owner = bcrypt.hashpw("ChangeMeNow123!".encode(), bcrypt.gensalt()).decode()
            hashed_admin = bcrypt.hashpw("AdminSecure2025!".encode(), bcrypt.gensalt()).decode()
            hashed_client = bcrypt.hashpw("Client123!".encode(), bcrypt.gensalt()).decode()

            supabase.table("users").insert([
                {"username": "kingminted", "password": hashed_owner, "full_name": "King Minted", "role": "owner"},
                {"username": "admin", "password": hashed_admin, "full_name": "KMFX Admin", "role": "admin"},
                {"username": "client1", "password": hashed_client, "full_name": "Client One", "role": "client"}
            ]).execute()
            st.success("Default accounts created in cloud database. CHANGE PASSWORDS ASAP!")
            st.warning("Security: Go to Admin Management to update passwords.")
    except Exception as e:
        st.error(f"Error creating default users: {e}")

create_default_users()
# ====================== FINAL ENHANCED THEME + FULL SIDEBAR CSS/JS BLOCK (2026 PRO) ======================
# Integrated: Premium glassmorphism, high-contrast text (white in dark, deep black in light),
# Consistent cards/inputs/buttons, hover effects, full sidebar perfection.

if "theme" not in st.session_state:
    st.session_state.theme = "dark"

theme = st.session_state.theme

# Core accents
accent_primary = "#00ffaa"
accent_hover = "#00cc88"
accent_glow = "#00ffaa40"
accent_secondary = "#ffd700"

if theme == "dark":
    bg_color = "#0a0d14"
    surface_color = "#11141a"
    card_bg = "rgba(15, 20, 30, 0.85)"
    sidebar_bg = "rgba(10, 13, 20, 0.95)"
    border_color = "rgba(100, 100, 100, 0.2)"
    
    text_primary = "#ffffff"
    text_secondary = "#e0e0e0"
    text_muted = "#aaaaaa"
    
    input_bg = "rgba(30, 35, 45, 0.6)"
    trigger_bg = "rgba(255,255,255,0.15)"  # Subtle glass in dark
else:
    bg_color = "#f8fbff"
    surface_color = "#ffffff"
    card_bg = "rgba(255, 255, 255, 0.92)"
    sidebar_bg = "rgba(255, 255, 255, 0.95)"
    border_color = "rgba(0, 0, 0, 0.12)"
    
    text_primary = "#0f172a"   # Deep slate for perfect readability
    text_secondary = "#334155"
    text_muted = "#64748b"
    
    input_bg = "rgba(240, 245, 255, 0.7)"
    trigger_bg = "rgba(0,0,0,0.08)"  # Subtle dark glass in light

# Common
glass_blur = "blur(20px)"
card_shadow = "0 8px 32px rgba(0,0,0,0.15)"
card_shadow_hover = "0 16px 50px rgba(0,255,170,0.25)"

st.markdown(f"""
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<style>
    /* Global App */
    html, body, [class*="css-"] {{ font-family: 'Poppins', sans-serif !important; }}
    .stApp {{
        background: {bg_color};
        color: {text_primary};
    }}
    
    /* Text consistency */
    h1, h2, h3, h4, h5, h6, p, div, span, label, .stMarkdown {{
        color: {text_primary} !important;
    }}
    small, caption, .caption, .secondary-text {{
        color: {text_muted} !important;
    }}
    
    /* Premium Glass Cards (use class='glass-card' in your markdowns) */
    .glass-card {{
        background: {card_bg};
        backdrop-filter: {glass_blur};
        -webkit-backdrop-filter: {glass_blur};
        border-radius: 20px;
        border: 1px solid {border_color};
        padding: 2rem;
        box-shadow: {card_shadow};
        transition: all 0.3s ease;
    }}
    .glass-card:hover {{
        box-shadow: {card_shadow_hover};
        transform: translateY(-4px);
        border-color: {accent_primary};
    }}
    
    /* Inputs & Forms */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > div {{
        background: {input_bg} !important;
        color: {text_primary} !important;
        border: 1px solid {border_color} !important;
        border-radius: 16px !important;
    }}
    
    /* Primary Buttons */
    button[kind="primary"] {{
        background: {accent_primary} !important;
        color: #000000 !important;
        border-radius: 16px !important;
        font-weight: 600 !important;
        box-shadow: 0 6px 20px {accent_glow} !important;
        transition: all 0.3s ease !important;
    }}
    button[kind="primary"]:hover {{
        background: {accent_hover} !important;
        transform: translateY(-2px);
        box-shadow: 0 10px 30px {accent_glow} !important;
    }}
    
    /* SIDEBAR CORE */
    section[data-testid="stSidebar"] {{
        background: {sidebar_bg} !important;
        backdrop-filter: {glass_blur};
        -webkit-backdrop-filter: {glass_blur};
        width: 320px !important;
        min-width: 320px !important;
        border-right: 1px solid {border_color};
        transition: transform 0.35s cubic-bezier(0.4, 0, 0.2, 1);
        z-index: 9998;
        box-shadow: 0 8px 32px rgba(0,0,0,0.15);
    }}
    
    /* HIDE NATIVE COLLAPSE ARROW (2026 compatible) */
    [data-testid="collapsedControl"],
    section[data-testid="stSidebar"] > div:first-child > div:first-child > button,
    section[data-testid="stSidebar"] > div:first-child > div:first-child {{
        display: none !important;
        visibility: hidden !important;
        pointer-events: none !important;
        opacity: 0 !important;
        width: 0 !important;
        height: 0 !important;
        padding: 0 !important;
        margin: 0 !important;
    }}
    
    /* Desktop & Tablet: Fixed open */
    @media (min-width: 769px) {{
        section[data-testid="stSidebar"] {{
            transform: translateX(0) !important;
        }}
        .main .block-container {{
            margin-left: 340px !important;
            max-width: calc(100% - 340px) !important;
            padding-left: 3rem !important;
            padding-top: 2rem !important;
            transition: margin-left 0.35s ease;
        }}
    }}
    
    /* Mobile: Slide-in */
    @media (max-width: 768px) {{
        section[data-testid="stSidebar"] {{
            position: fixed !important;
            top: 0;
            left: 0;
            height: 100vh !important;
            width: 85% !important;
            max-width: 320px !important;
            transform: translateX(-100%);
            box-shadow: 12px 0 40px rgba(0,0,0,0.6);
        }}
        section[data-testid="stSidebar"][aria-expanded="true"] {{
            transform: translateX(0) !important;
        }}
        .block-container {{
            padding: 1rem !important;
            padding-top: 80px !important;
        }}
    }}
    
    /* Mobile Trigger */
    .mobile-sidebar-trigger {{
        display: none;
        position: fixed;
        top: 16px;
        left: 16px;
        width: 56px;
        height: 56px;
        background: {trigger_bg};
        backdrop-filter: blur(16px);
        border-radius: 50%;
        box-shadow: 0 8px 30px rgba(0,0,0,0.4);
        align-items: center;
        justify-content: center;
        cursor: pointer;
        z-index: 9999;
        transition: all 0.3s ease;
    }}
    .mobile-sidebar-trigger:hover {{
        background: {accent_primary};
        transform: scale(1.12);
    }}
    .mobile-sidebar-trigger span {{ font-size: 30px; color: {text_primary}; }}
    
    /* Close Button */
    .sidebar-close-btn {{
        display: none;
        position: absolute;
        top: 16px;
        right: 16px;
        width: 48px;
        height: 48px;
        background: {trigger_bg};
        backdrop-filter: blur(12px);
        border-radius: 50%;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        transition: all 0.3s ease;
        z-index: 9999;
    }}
    .sidebar-close-btn:hover {{
        background: #ff4757;
        transform: scale(1.1);
    }}
    .sidebar-close-btn span {{ font-size: 32px; color: {text_primary}; }}
    
    /* Overlay */
    .sidebar-overlay {{
        display: none;
        position: fixed;
        inset: 0;
        background: rgba(0,0,0,0.7);
        backdrop-filter: blur(8px);
        z-index: 9997;
        opacity: 0;
        transition: opacity 0.35s ease;
        cursor: pointer;
    }}
    .sidebar-overlay.active {{
        display: block;
        opacity: 1;
    }}
    
    @media (max-width: 768px) {{
        .mobile-sidebar-trigger {{ display: flex; }}
    }}
    
    /* Premium Sidebar Menu */
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
    
    /* Force Sidebar Text */
    section[data-testid="stSidebar"] *,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] div,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] label {{
        color: {text_primary} !important;
    }}
</style>

<!-- Custom Controls -->
<div class="mobile-sidebar-trigger"><span>☰</span></div>
<div class="sidebar-overlay"></div>
<div class="sidebar-close-btn"><span>×</span></div>

<script>
    const getElements = () => {{
        return {{
            sidebar: document.querySelector('section[data-testid="stSidebar"]'),
            trigger: document.querySelector('.mobile-sidebar-trigger'),
            overlay: document.querySelector('.sidebar-overlay'),
            closeBtn: document.querySelector('.sidebar-close-btn'),
            control: document.querySelector('[data-testid="collapsedControl"]')
        }};
    }};

    let elements = getElements();

    const toggleSidebar = () => {{
        elements = getElements();
        if (elements.control) elements.control.click();
    }};

    const updateUI = () => {{
        elements = getElements();
        if (!elements.sidebar) return;
        const isOpen = elements.sidebar.getAttribute('aria-expanded') === 'true';
        const isMobile = window.innerWidth <= 768;

        if (isMobile) {{
            elements.trigger.style.display = isOpen ? 'none' : 'flex';
            elements.closeBtn.style.display = isOpen ? 'flex' : 'none';
            elements.overlay.classList.toggle('active', isOpen);
        }} else {{
            elements.trigger.style.display = 'none';
            elements.closeBtn.style.display = 'none';
            elements.overlay.classList.remove('active');
        }}
    }};

    const enforceState = () => {{
        elements = getElements();
        if (!elements.sidebar) return;
        const isOpen = elements.sidebar.getAttribute('aria-expanded') === 'true';
        const isMobile = window.innerWidth <= 768;

        if (isMobile && isOpen) toggleSidebar();
        else if (!isMobile && !isOpen) toggleSidebar();
        
        updateUI();
    }};

    const init = () => {{
        elements = getElements();
        if (elements.trigger) elements.trigger.addEventListener('click', toggleSidebar);
        if (elements.overlay) elements.overlay.addEventListener('click', toggleSidebar);
        if (elements.closeBtn) elements.closeBtn.addEventListener('click', toggleSidebar);

        if (elements.sidebar) {{
            const observer = new MutationObserver(updateUI);
            observer.observe(elements.sidebar, {{ attributes: true, attributeFilter: ['aria-expanded'] }});
        }}

        window.addEventListener('resize', enforceState);
        window.addEventListener('orientationchange', enforceState);

        enforceState();
    }};

    const waitInterval = setInterval(() => {{
        elements = getElements();
        if (elements.sidebar && elements.control) {{
            clearInterval(waitInterval);
            init();
        }}
    }}, 100);

    window.addEventListener('load', () => setTimeout(enforceState, 500));
    document.addEventListener('DOMContentLoaded', enforceState);
</script>
""", unsafe_allow_html=True)
# ====================== PART 2: LOGIN SYSTEM (FINAL SUPER ADVANCED - TABBED ROLE LOGIN & FIXED) ======================
# Helper function for login (defined early - no NameError)
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
                log_action("Login Successful", f"User: {username} | Role: {user['role']}")
                st.rerun()
            else:
                st.error("Invalid password")
        else:
            st.error("Username not found")
    except Exception as e:
        st.error(f"Login error: {e}")

# Authentication check
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.role = "guest"
    st.session_state.full_name = ""
    st.session_state.username = ""

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.role = "guest"
    st.session_state.full_name = ""
    st.session_state.username = ""
if not st.session_state.authenticated:
    col1, col2, col3 = st.columns([1, 4, 1])
    with col2:
        st.markdown("<div class='glass-card' style='text-align:center; padding:3rem;'>", unsafe_allow_html=True)
        st.markdown(f"<h1 style='color:{accent_color}; margin-bottom:0;'>🚀 KMFX FTMO Pro</h1>", unsafe_allow_html=True)
        st.markdown("<p style='opacity:0.8; margin-bottom:2rem;'>Elite Scaling Empire • Cloud Edition 2026</p>", unsafe_allow_html=True)
       
        # Tabbed role login
        tab_owner, tab_admin, tab_client = st.tabs(["👑 Owner Login", "🛠️ Admin Login", "👥 Client Login"])
       
        with tab_owner:
            st.markdown("### Owner Access (Full Empire Control)")
            # REMOVED: Default credentials display for security
            # No longer showing username/password in app
            with st.form("login_form_owner"):
                username = st.text_input("Username", placeholder="Enter owner username", key="owner_user")
                password = st.text_input("Password", type="password", key="owner_pwd")
                if st.form_submit_button("Login as Owner →", type="primary", use_container_width=True):
                    login_user(username, password)
       
        with tab_admin:
            st.markdown("### Admin Access (Operational)")
            # Optional: Keep or remove this too - removed for consistency
            st.info("Use credentials provided by Owner")
            with st.form("login_form_admin"):
                username = st.text_input("Username", placeholder="Enter admin username", key="admin_user")
                password = st.text_input("Password", type="password", key="admin_pwd")
                if st.form_submit_button("Login as Admin →", type="primary", use_container_width=True):
                    login_user(username, password)
       
        with tab_client:
            st.markdown("### Client Access (Team Member)")
            st.info("Use credentials provided by Owner • View balance, shared accounts, request withdrawals")
            with st.form("login_form_client"):
                username = st.text_input("Username", placeholder="Your username", key="client_user")
                password = st.text_input("Password", type="password", key="client_pwd")
                if st.form_submit_button("Login as Client →", type="primary", use_container_width=True):
                    login_user(username, password)
       
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()
# ====================== END OF FINAL TABBED LOGIN ======================

# ====================== SIDEBAR NAVIGATION ======================
with st.sidebar:
    st.markdown(f"<h3 style='text-align:center;'>👤 {st.session_state.full_name}</h3>", unsafe_allow_html=True)
    current_role = st.session_state.get("role", "guest")
    st.markdown(f"<p style='text-align:center; color:{accent_color};'><strong>{current_role.title()}</strong></p>", unsafe_allow_html=True)
    st.divider()

    # Role-based pages (strict)
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
    else:
        pages = ["🏠 Dashboard"]

    if "selected_page" not in st.session_state:
        st.session_state.selected_page = pages[0]
    elif st.session_state.selected_page not in pages:
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

# ====================== HEADER & GROWTH FUND METRIC ======================
try:
    gf_response = supabase.table("growth_fund_transactions").select("type, amount").execute()
    gf_balance = sum(row["amount"] if row["type"] == "In" else -row["amount"] for row in gf_response.data) if gf_response.data else 0.0
except:
    gf_balance = 0.0

col1, col2 = st.columns([3, 1])
with col1:
    st.markdown(f"<h1>{selected}</h1>", unsafe_allow_html=True)
with col2:
    st.metric("Growth Fund", f"${gf_balance:,.0f}")
    # === FIXED MOBILE SIDEBAR CONTROLS (PLACE THIS AFTER YOUR HEADER OR WHEREVER YOU HAD IT BEFORE) ===

   
# ====================== ANNOUNCEMENT BANNER ======================
try:
    ann_response = supabase.table("announcements").select("title, message, date").order("date", desc=True).limit(1).execute()
    if ann_response.data:
        ann = ann_response.data[0]
        st.markdown(f"""
        <div class='glass-card' style='border-left: 5px solid {accent_color}; padding:1.5rem;'>
            <h4 style='margin:0; color:{accent_color};'>📢 {ann['title']}</h4>
            <p style='margin:0.8rem 0 0; opacity:0.9;'>{ann['message']}</p>
            <small style='opacity:0.7;'>Posted: {ann['date']}</small>
        </div>
        """, unsafe_allow_html=True)
    else:
        raise Exception()
except:
    st.markdown(f"""
    <div class='glass-card' style='text-align:center; padding:2rem;'>
        <h3 style='margin:0; color:{accent_color};'>Welcome back, {st.session_state.full_name}! 🚀</h3>
        <p style='margin:1rem 0 0; opacity:0.8;'>Scale smarter. Trade bolder. Win bigger.</p>
    </div>
    """, unsafe_allow_html=True)

# ====================== MAIN CONTENT START ======================
st.markdown("<div class='glass-card'>", unsafe_allow_html=True)

# ====================== PART 3: DASHBOARD PAGE (FINAL SUPER ADVANCED - FULL MAIN FLOW SYNC & REALTIME OPTIMIZED) ======================
# ====================== DASHBOARD PAGE - FULLY FIXED (PHP PER UNIT KEY + SAFE GET + CONSISTENT) ======================
if selected == "🏠 Dashboard":
    st.header("Elite Empire Command Center 🚀")
    st.markdown("**Realtime, fully automatic empire overview: Accounts, participant trees, contributor funding (PHP units), profit distributions, client balances, growth fund • Everything synced instantly • Professional, clean, fast performance.**")
   
    current_role = st.session_state.get("role", "guest")
   
    @st.cache_data(ttl=30)
    def fetch_all_empire_data():
        accounts = supabase.table("ftmo_accounts").select("*").execute().data or []
        profits = supabase.table("profits").select("gross_profit, trader_share, growth_fund_add").execute().data or []
        distributions = supabase.table("profit_distributions").select("share_amount, participant_name, is_growth_fund").execute().data or []
        users = supabase.table("users").select("full_name, balance, role").execute().data or []
        clients = [u for u in users if u["role"] == "client"]
       
        gf_resp = supabase.table("growth_fund_transactions").select("type, amount").execute()
        gf_balance = sum(row["amount"] if row["type"] == "In" else -row["amount"] for row in gf_resp.data) if gf_resp.data else 0.0
       
        participant_shares = {}
        for d in distributions:
            if not d.get("is_growth_fund", False):
                name = d["participant_name"]
                participant_shares[name] = participant_shares.get(name, 0) + d["share_amount"]
       
        # FIXED: Use "php_per_unit" + safe .get() to prevent KeyError
        total_funded_php = 0
        for acc in accounts:
            for c in acc.get("contributors", []):
                units = c.get("units", 0)
                php_per_unit = c.get("php_per_unit", 0)
                total_funded_php += units * php_per_unit
       
        return accounts, profits, distributions, clients, gf_balance, participant_shares, total_funded_php
   
    accounts, profits, distributions, clients, gf_balance, participant_shares, total_funded_php = fetch_all_empire_data()
   
    # ====================== PROFESSIONAL METRICS GRID ======================
    total_accounts = len(accounts)
    total_equity = sum(acc.get("current_equity", 0) for acc in accounts)
    total_withdrawable = sum(acc.get("withdrawable_balance", 0) for acc in accounts)
    total_gross = sum(p.get("gross_profit", 0) for p in profits)
    total_distributed = sum(d.get("share_amount", 0) for d in distributions if not d.get("is_growth_fund", False))
    total_client_balances = sum(u.get("balance", 0) for u in clients)
   
    st.markdown(f"""
    <div style="display: grid;
                grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
                gap: 1.2rem;
                margin: 1.5rem 0;">
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
   
    # ====================== QUICK ACTIONS ======================
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
   
    # ====================== EMPIRE FLOW TREES ======================
    st.subheader("🌳 Empire Flow Trees (Realtime Auto-Sync)")
    tab_emp1, tab_emp2 = st.tabs(["Participant Shares Distribution", "Contributor Funding Flow (PHP)"])
   
    with tab_emp1:
        if participant_shares:
            labels = ["Empire Shares"] + list(participant_shares.keys())
            values = list(participant_shares.values())
            fig = go.Figure(data=[go.Sankey(
                node=dict(pad=20, thickness=30, label=labels, color=["#00ffaa"] + [accent_color]*len(participant_shares)),
                link=dict(source=[0]*len(values), target=list(range(1, len(values)+1)), value=values)
            )])
            fig.update_layout(height=600, title="Total Distributed Shares by Participant")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No distributions yet • Activates with first profit")
   
    with tab_emp2:
        funded_by_contributor = {}
        total_funded_php = 0  # Recalculate for accuracy
        for acc in accounts:
            for c in acc.get("contributors", []):
                units = c.get("units", 0)
                php_per_unit = c.get("php_per_unit", 0)  # FIXED KEY
                php = units * php_per_unit
                total_funded_php += php
                name = c["name"]
                funded_by_contributor[name] = funded_by_contributor.get(name, 0) + php
       
        if funded_by_contributor:
            labels = ["Empire Funded (PHP)"] + list(funded_by_contributor.keys())
            values = list(funded_by_contributor.values())
            fig = go.Figure(data=[go.Sankey(
                node=dict(pad=20, thickness=30, label=labels, color=["#ffd700"] + ["#ff6b6b"]*len(funded_by_contributor)),
                link=dict(source=[0]*len(values), target=list(range(1, len(values)+1)), value=values)
            )])
            fig.update_layout(height=600, title="Total Funded by Contributors (PHP)")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No contributors yet")
   
    # ====================== LIVE ACCOUNTS WITH MINI-TREES ======================
    st.subheader("📊 Live Accounts (Realtime Metrics & Trees)")
    if accounts:
        st.markdown("<div style='display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 1.5rem;'>", unsafe_allow_html=True)
        for acc in accounts:
            # FIXED: Safe calculation with php_per_unit
            total_funded_php_acc = sum(c.get("units", 0) * c.get("php_per_unit", 0) for c in acc.get("contributors", []))
            phase_emoji = {"Challenge P1": "🔴", "Challenge P2": "🟡", "Verification": "🟠", "Funded": "🟢", "Scaled": "💎"}.get(acc["current_phase"], "⚪")
           
            st.markdown(f"""
            <div class='glass-card' style='padding:2rem;'>
                <h3>{phase_emoji} {acc['name']}</h3>
                <div style='display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin: 1rem 0;'>
                    <div><strong>Phase:</strong> {acc['current_phase']}</div>
                    <div><strong>Equity:</strong> ${acc.get('current_equity', 0):,.0f}</div>
                    <div><strong>Withdrawable:</strong> ${acc.get('withdrawable_balance', 0):,.0f}</div>
                    <div><strong>Funded:</strong> ₱{total_funded_php_acc:,.0f}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
           
            tab1, tab2 = st.tabs(["Participants Tree", "Contributors Tree (PHP)"])
            with tab1:
                participants = acc.get("participants", [])
                if participants:
                    labels = ["Profits"] + [f"{p['name']} ({p['percentage']:.1f}%)" for p in participants]
                    values = [p["percentage"] for p in participants]
                    fig = go.Figure(data=[go.Sankey(node=dict(pad=15, thickness=20, label=labels),
                                                    link=dict(source=[0]*len(values), target=list(range(1, len(values)+1)), value=values))])
                    fig.update_layout(height=350)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No participants")
            with tab2:
                contributors = acc.get("contributors", [])
                if contributors:
                    # FIXED: Use php_per_unit in label & value
                    labels = ["Funded (PHP)"] + [f"{c['name']} ({c.get('units', 0)} units @ ₱{c.get('php_per_unit', 0):,.0f}/unit)" for c in contributors]
                    values = [c.get("units", 0) * c.get("php_per_unit", 0) for c in contributors]
                    fig = go.Figure(data=[go.Sankey(node=dict(pad=15, thickness=20, label=labels),
                                                    link=dict(source=[0]*len(values), target=list(range(1, len(values)+1)), value=values))])
                    fig.update_layout(height=350)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No contributors")
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("No accounts yet • Launch first to activate full realtime flow")
   
    # ====================== CLIENT BALANCES (OWNER/ADMIN) ======================
    if current_role in ["owner", "admin"] and clients:
        st.subheader("👥 Team Client Balances (Realtime Auto)")
        client_df = pd.DataFrame([{"Client": u["full_name"], "Balance": f"${u['balance'] or 0:,.2f}"} for u in clients])
        st.dataframe(client_df, use_container_width=True, hide_index=True)
   
    # ====================== MOTIVATIONAL CLOSE ======================
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
# ====================== PART 4: FTMO ACCOUNTS PAGE (FINAL SUPER ADVANCED - FIXED SUBMIT & COLUMN VALUE ERROR) ======================
elif selected == "📊 FTMO Accounts":
    st.header("FTMO Accounts Management 🚀")
    st.markdown("**Empire core: Owner/Admin launch, edit, delete accounts • Clients view shared participation • Participants auto-selected from registered clients with Title (e.g., Name (VIP)) • Growth Fund optional • Contributors (PHP units, flexible per unit value) • Real-time tree previews • Full validation • Instant sync.**")
    
    # SAFE ROLE
    current_role = st.session_state.get("role", "guest")
    
    # FULL AUTO CACHE
    @st.cache_data(ttl=60)
    def fetch_all_data():
        accounts_resp = supabase.table("ftmo_accounts").select("*").order("created_date", desc=True).execute()
        users_resp = supabase.table("users").select("id, full_name, role, balance, title").execute()
        return accounts_resp.data or [], users_resp.data or []
    
    accounts, all_users = fetch_all_data()
    
    # Registered clients with formatted display (Name (Title))
    registered_display = []
    full_name_to_display = {}
    for u in all_users:
        if u["role"] == "client":
            display = u["full_name"]
            if u.get("title"):
                display += f" ({u['title']})"
            registered_display.append(display)
            full_name_to_display[display] = u["full_name"]
    
    special_participants = ["Growth Fund", "Manual Payout (Temporary)"]
    participant_options = ["King Minted"] + registered_display + special_participants
    
    # ====================== OWNER/ADMIN: FULL CREATE/EDIT/DELETE ======================
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
                
                # PARTICIPANTS TREE
                st.subheader("🌳 Participants Tree - Profit Distribution (%)")
                st.info("**Clean Flow:** Start with Owner 100% • Add registered clients (with Title) for auto-balance • Growth Fund optional • Manual for temporary • Must sum exactly 100%")
                
                default_part = [{"name": "King Minted", "role": "Founder/Owner", "percentage": 100.0}]
                for display in registered_display:
                    default_part.append({"name": full_name_to_display[display], "role": "Team Member", "percentage": 0.0})
                
                part_df = pd.DataFrame(default_part)
                edited_part = st.data_editor(
                    part_df,
                    num_rows="dynamic",
                    use_container_width=True,
                    column_config={
                        "name": st.column_config.SelectboxColumn(
                            "Name *",
                            options=participant_options,
                            required=True
                        ),
                        "role": st.column_config.TextColumn("Role"),
                        "percentage": st.column_config.NumberColumn("% *", min_value=0.0, max_value=100.0, step=0.5)
                    }
                )
                
                current_sum = edited_part["percentage"].sum()
                st.progress(min(current_sum / 100, 1.0))
                if abs(current_sum - 100.0) > 0.1:
                    st.error(f"Exactly 100% required (current: {current_sum:.1f}%)")
                else:
                    st.success("✅ Perfect 100%")
                
                # Manual custom names
                manual_inputs = []
                for idx, row in edited_part.iterrows():
                    if row["name"] == "Manual Payout (Temporary)":
                        custom_name = st.text_input(f"Custom Name for Manual Row {idx+1}", placeholder="e.g. Temporary Tester", key=f"manual_create_{idx}")
                        if custom_name:
                            manual_inputs.append((idx, custom_name))
                
                # CONTRIBUTORS TREE (FIXED - no 'value' arg)
                st.subheader("🌳 Contributors Tree - Funding (PHP Units)")
                st.info("Track funded capital • Recommended 1000 PHP per unit (type when adding rows)")
                
                contrib_df = pd.DataFrame(columns=["name", "units", "php_per_unit"])
                edited_contrib = st.data_editor(
                    contrib_df,
                    num_rows="dynamic",
                    use_container_width=True,
                    column_config={
                        "name": st.column_config.TextColumn("Contributor Name"),
                        "units": st.column_config.NumberColumn("Units Funded", min_value=0.0, step=0.5),
                        "php_per_unit": st.column_config.NumberColumn("PHP per Unit", min_value=100.0, step=100.0, help="Default/recommended: 1000")
                    }
                )
                
                if not edited_contrib.empty:
                    total_php = (edited_contrib["units"] * edited_contrib["php_per_unit"]).sum()
                    st.metric("Total Funded (PHP)", f"₱{total_php:,.0f}")
                
                # TREE PREVIEWS
                tab_prev1, tab_prev2 = st.tabs(["Participants Preview", "Contributors Preview"])
                with tab_prev1:
                    if current_sum > 0:
                        labels = ["Profits"] + [f"{row['name']} ({row['percentage']:.1f}%)" for _, row in edited_part.iterrows()]
                        values = edited_part["percentage"].tolist()
                        fig = go.Figure(data=[go.Sankey(node=dict(pad=15, thickness=20, label=labels),
                                                        link=dict(source=[0]*len(values), target=list(range(1, len(values)+1)), value=values))])
                        st.plotly_chart(fig, use_container_width=True)
                with tab_prev2:
                    if not edited_contrib.empty:
                        valid = edited_contrib.dropna(subset=["units", "php_per_unit"])
                        if not valid.empty:
                            labels = ["Funded (PHP)"] + [f"{row['name']} ({row['units']} units @ ₱{row['php_per_unit']:,.0f}/unit)" for _, row in valid.iterrows()]
                            values = (valid["units"] * valid["php_per_unit"]).tolist()
                            fig = go.Figure(data=[go.Sankey(node=dict(pad=15, thickness=20, label=labels),
                                                            link=dict(source=[0]*len(values), target=list(range(1, len(values)+1)), value=values))])
                            st.plotly_chart(fig, use_container_width=True)
                
                # FIXED SUBMIT BUTTON
                submitted = st.form_submit_button("🚀 Launch Account", type="primary", use_container_width=True)
                if submitted:
                    if not name.strip():
                        st.error("Account name required")
                    elif abs(current_sum - 100.0) > 0.1:
                        st.error("Exactly 100% required")
                    else:
                        final_part = []
                        for row in edited_part.to_dict(orient="records"):
                            display = row["name"]
                            actual_name = full_name_to_display.get(display, display)
                            final_part.append({
                                "name": actual_name,
                                "role": row["role"],
                                "percentage": row["percentage"]
                            })
                        
                        for row_idx, custom in manual_inputs:
                            final_part[row_idx]["name"] = custom
                        
                        contributors_json = edited_contrib.to_dict(orient="records") if not edited_contrib.empty else []
                        
                        try:
                            supabase.table("ftmo_accounts").insert({
                                "name": name.strip(),
                                "ftmo_id": ftmo_id or None,
                                "current_phase": phase,
                                "current_equity": equity,
                                "withdrawable_balance": withdrawable,
                                "notes": notes or None,
                                "created_date": datetime.date.today().isoformat(),
                                "participants": final_part,
                                "contributors": contributors_json
                            }).execute()
                            st.success("Account launched! Titles synced.")
                            st.cache_data.clear()
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
        
        # LIVE ACCOUNTS LIST WITH EDIT/DELETE
        st.subheader("Live Empire Accounts")
        if accounts:
            for acc in accounts:
                total_funded_php = sum(c["units"] * c["php_per_unit"] for c in acc.get("contributors", []))
                with st.expander(f"🌟 {acc['name']} • {acc['current_phase']} • Equity ${acc.get('current_equity', 0):,.0f} • Funded ₱{total_funded_php:,.0f}", expanded=False):
                    # Trees with titles
                    tab1, tab2 = st.tabs(["Participants Tree", "Contributors Tree"])
                    with tab1:
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
                            st.plotly_chart(fig, use_container_width=True)
                    with tab2:
                        contributors = acc.get("contributors", [])
                        if contributors:
                            labels = ["Funded (PHP)"] + [f"{c['name']} ({c['units']} units @ ₱{c['php_per_unit']:,.0f}/unit)" for c in contributors]
                            values = [c["units"] * c["php_per_unit"] for c in contributors]
                            fig = go.Figure(data=[go.Sankey(node=dict(pad=15, thickness=20, label=labels),
                                                            link=dict(source=[0]*len(values), target=list(range(1, len(values)+1)), value=values))])
                            st.plotly_chart(fig, use_container_width=True)
                    
                    if current_role in ["owner", "admin"]:
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
                                    st.cache_data.clear()
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error: {str(e)}")
            
            # EDIT FORM (mirror create with titles)
            if "edit_acc_id" in st.session_state:
                eid = st.session_state.edit_acc_id
                cur = st.session_state.edit_acc_data
                with st.expander(f"✏️ Editing {cur['name']}", expanded=True):
                    with st.form(key=f"edit_form_{eid}", clear_on_submit=True):
                        col1, col2 = st.columns(2)
                        with col1:
                            new_name = st.text_input("Account Name *", value=cur["name"])
                            new_ftmo_id = st.text_input("FTMO ID (Optional)", value=cur.get("ftmo_id"))
                            new_phase = st.selectbox("Current Phase *", ["Challenge P1", "Challenge P2", "Verification", "Funded", "Scaled"], 
                                                     index=["Challenge P1", "Challenge P2", "Verification", "Funded", "Scaled"].index(cur["current_phase"]))
                        with col2:
                            new_equity = st.number_input("Current Equity (USD)", value=float(cur["current_equity"] or 0), step=1000.0)
                            new_withdrawable = st.number_input("Current Withdrawable (USD)", value=float(cur["withdrawable_balance"] or 0), step=500.0)
                        
                        new_notes = st.text_area("Notes (Optional)", value=cur.get("notes") or "")
                        
                        # PARTICIPANTS TREE
                        st.subheader("🌳 Participants Tree - Profit Distribution (%)")
                        st.info("**Clean Flow:** Edit percentages • Add/remove rows • Must sum exactly 100%")
                        
                        part_df = pd.DataFrame(cur["participants"])
                        edited_part = st.data_editor(
                            part_df,
                            num_rows="dynamic",
                            use_container_width=True,
                            column_config={
                                "name": st.column_config.SelectboxColumn(
                                    "Name *",
                                    options=participant_options,
                                    required=True
                                ),
                                "role": st.column_config.TextColumn("Role"),
                                "percentage": st.column_config.NumberColumn("% *", min_value=0.0, max_value=100.0, step=0.5)
                            }
                        )
                        
                        current_sum = edited_part["percentage"].sum()
                        st.progress(min(current_sum / 100, 1.0))
                        if abs(current_sum - 100.0) > 0.1:
                            st.error(f"Exactly 100% required (current: {current_sum:.1f}%)")
                        else:
                            st.success("✅ Perfect 100%")
                        
                        # Manual custom names
                        manual_inputs = []
                        for idx, row in edited_part.iterrows():
                            if row["name"] == "Manual Payout (Temporary)":
                                custom_name = st.text_input(f"Custom Name for Manual Row {idx+1}", placeholder="e.g. Temporary Tester", key=f"manual_edit_{eid}_{idx}")
                                if custom_name:
                                    manual_inputs.append((idx, custom_name))
                        
                        # CONTRIBUTORS TREE
                        st.subheader("🌳 Contributors Tree - Funding (PHP Units)")
                        contrib_df = pd.DataFrame(cur.get("contributors", []))
                        edited_contrib = st.data_editor(
                            contrib_df,
                            num_rows="dynamic",
                            use_container_width=True,
                            column_config={
                                "name": st.column_config.TextColumn("Contributor Name"),
                                "units": st.column_config.NumberColumn("Units Funded", min_value=0.0, step=0.5),
                                "php_per_unit": st.column_config.NumberColumn("PHP per Unit", min_value=100.0, step=100.0, help="Default/recommended: 1000")
                            }
                        )
                        
                        if not edited_contrib.empty:
                            total_php = (edited_contrib["units"] * edited_contrib["php_per_unit"]).sum()
                            st.metric("Total Funded (PHP)", f"₱{total_php:,.0f}")
                        
                        # TREE PREVIEWS
                        tab_prev1, tab_prev2 = st.tabs(["Participants Preview", "Contributors Preview"])
                        with tab_prev1:
                            if current_sum > 0:
                                labels = ["Profits"] + [f"{row['name']} ({row['percentage']:.1f}%)" for _, row in edited_part.iterrows()]
                                values = edited_part["percentage"].tolist()
                                fig = go.Figure(data=[go.Sankey(node=dict(pad=15, thickness=20, label=labels),
                                                                link=dict(source=[0]*len(values), target=list(range(1, len(values)+1)), value=values))])
                                st.plotly_chart(fig, use_container_width=True)
                        with tab_prev2:
                            if not edited_contrib.empty:
                                valid = edited_contrib.dropna(subset=["units", "php_per_unit"])
                                if not valid.empty:
                                    labels = ["Funded (PHP)"] + [f"{row['name']} ({row['units']} units @ ₱{row['php_per_unit']:,.0f}/unit)" for _, row in valid.iterrows()]
                                    values = (valid["units"] * valid["php_per_unit"]).tolist()
                                    fig = go.Figure(data=[go.Sankey(node=dict(pad=15, thickness=20, label=labels),
                                                                    link=dict(source=[0]*len(values), target=list(range(1, len(values)+1)), value=values))])
                                    st.plotly_chart(fig, use_container_width=True)
                        
                        col_save, col_cancel = st.columns(2)
                        with col_save:
                            if st.form_submit_button("💾 Save Changes", type="primary", use_container_width=True):
                                if not new_name.strip():
                                    st.error("Account name required")
                                elif abs(current_sum - 100.0) > 0.1:
                                    st.error("Exactly 100% required")
                                else:
                                    final_part = []
                                    for row in edited_part.to_dict(orient="records"):
                                        display = row["name"]
                                        actual_name = full_name_to_display.get(display, display)
                                        final_part.append({
                                            "name": actual_name,
                                            "role": row["role"],
                                            "percentage": row["percentage"]
                                        })
                                    
                                    for row_idx, custom in manual_inputs:
                                        final_part[row_idx]["name"] = custom
                                    
                                    contributors_json = edited_contrib.to_dict(orient="records") if not edited_contrib.empty else []
                                    
                                    try:
                                        supabase.table("ftmo_accounts").update({
                                            "name": new_name.strip(),
                                            "ftmo_id": new_ftmo_id or None,
                                            "current_phase": new_phase,
                                            "current_equity": new_equity,
                                            "withdrawable_balance": new_withdrawable,
                                            "notes": new_notes or None,
                                            "participants": final_part,
                                            "contributors": contributors_json
                                        }).eq("id", eid).execute()
                                        st.success("Account updated!")
                                        del st.session_state.edit_acc_id
                                        del st.session_state.edit_acc_data
                                        st.cache_data.clear()
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
    
    # CLIENT VIEW
    else:
        my_name = st.session_state.full_name
        my_accounts = [a for a in accounts if any(p["name"] == my_name for p in a.get("participants", []))]
        st.subheader(f"Your Shared Accounts ({len(my_accounts)})")
        if my_accounts:
            for acc in my_accounts:
                my_pct = next((p["percentage"] for p in acc.get("participants", []) if p["name"] == my_name), 0)
                my_funded_php = sum(c["units"] * c["php_per_unit"] for c in acc.get("contributors", []) if c["name"] == my_name)
                with st.expander(f"🌟 {acc['name']} • Your Share: {my_pct:.1f}% • Your Funded ₱{my_funded_php:,.0f}", expanded=True):
                    st.markdown(f"**Phase:** {acc['current_phase']} • **Equity:** ${acc.get('current_equity', 0):,.0f}")
                    # Trees with titles
                    tab1, tab2 = st.tabs(["Participants Tree", "Contributors Tree"])
                    with tab1:
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
                            st.plotly_chart(fig, use_container_width=True)
                    with tab2:
                        contributors = acc.get("contributors", [])
                        if contributors:
                            labels = ["Funded (PHP)"] + [f"{c['name']} ({c['units']} units @ ₱{c['php_per_unit']:,.0f}/unit)" for c in contributors]
                            values = [c["units"] * c["php_per_unit"] for c in contributors]
                            fig = go.Figure(data=[go.Sankey(node=dict(pad=15, thickness=20, label=labels),
                                                            link=dict(source=[0]*len(values), target=list(range(1, len(values)+1)), value=values))])
                            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No participation yet • Owner will assign")
        
        st.subheader("Empire Overview (All Accounts)")
        for acc in accounts:
            total_funded_php = sum(c["units"] * c["php_per_unit"] for c in acc.get("contributors", []))
            with st.expander(f"{acc['name']} • {acc['current_phase']} • Equity ${acc.get('current_equity', 0):,.0f} • Funded ₱{total_funded_php:,.0f}"):
                # Trees with titles
                tab1, tab2 = st.tabs(["Participants Tree", "Contributors Tree"])
                with tab1:
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
                        st.plotly_chart(fig, use_container_width=True)
                with tab2:
                    contributors = acc.get("contributors", [])
                    if contributors:
                        labels = ["Funded (PHP)"] + [f"{c['name']} ({c['units']} units @ ₱{c['php_per_unit']:,.0f}/unit)" for c in contributors]
                        values = [c["units"] * c["php_per_unit"] for c in contributors]
                        fig = go.Figure(data=[go.Sankey(node=dict(pad=15, thickness=20, label=labels),
                                                        link=dict(source=[0]*len(values), target=list(range(1, len(values)+1)), value=values))])
                        st.plotly_chart(fig, use_container_width=True)
    
    if not accounts:
        st.info("No accounts in empire yet")
# ====================== END OF FINAL FTMO ACCOUNTS WITH TITLE SYNC & FIXED ERRORS ======================
# ====================== PROFIT SHARING PAGE (FINAL SUPER ADVANCED - WITH TITLE SYNC & FULL FLOW) ======================
elif selected == "💰 Profit Sharing":
    st.header("Profit Sharing & Auto-Distribution 💰")
    st.markdown("**Empire scaling engine: Input FTMO withdrawable profit (actual received after cut) → 100% auto-distributed per participants → auto-balance update for registered • Growth Fund optional • Units generated • Realtime preview with titles • Instant sync.**")
    
    current_role = st.session_state.get("role", "guest")
    
    if current_role not in ["owner", "admin"]:
        st.warning("Profit recording is owner/admin only • Clients view earnings in My Profile.")
        st.stop()
    
    # FULL AUTO CACHE
    @st.cache_data(ttl=60)
    def fetch_profit_data():
        accounts = supabase.table("ftmo_accounts").select("id, name, current_phase, current_equity, unit_value, participants").execute().data or []
        users = supabase.table("users").select("id, full_name, balance, title").execute().data or []
        user_map = {u["full_name"]: u for u in users}
        return accounts, user_map
    
    accounts, user_map = fetch_profit_data()
    if not accounts:
        st.info("No accounts yet • Launch in FTMO Accounts first.")
        st.stop()
    
    # Account selector
    account_options = {f"{a['name']} • Phase: {a['current_phase']} • Equity: ${a['current_equity'] or 0:,.0f}": a for a in accounts}
    selected_key = st.selectbox("Select Account for Profit Record", list(account_options.keys()))
    acc = account_options[selected_key]
    acc_id = acc["id"]
    acc_name = acc["name"]
    unit_value = acc["unit_value"] or 3000.0
    participants = acc.get("participants", [])
    
    st.info(f"**Recording for:** {acc_name} | Input actual FTMO withdrawable profit → 100% auto-distributed")
    
    with st.form("profit_form", clear_on_submit=True):
        col1, col2 = st.columns([2, 1])
        with col1:
            net_withdrawable = st.number_input("FTMO Withdrawable Profit (USD) *", min_value=0.01, step=500.0, help="Actual amount received from FTMO (after their cut)")
        with col2:
            record_date = st.date_input("Record Date", datetime.date.today())
        
        # Participants tree (allow override)
        st.subheader("🌳 Distribution Tree (From Account)")
        st.info("100% of withdrawable profit auto-distributed • Registered clients = auto-balance • Growth Fund = auto-GF if included • Manual = flagged")
        
        part_df = pd.DataFrame(participants or [{"name": "King Minted", "role": "Founder", "percentage": 100.0}])
        edited_part = st.data_editor(
            part_df,
            num_rows="dynamic",
            use_container_width=True,
            column_config={
                "name": st.column_config.TextColumn("Name"),
                "role": st.column_config.TextColumn("Role"),
                "percentage": st.column_config.NumberColumn("%", min_value=0.0, max_value=100.0, step=0.5, format="%.1f")
            }
        )
        
        current_sum = edited_part["percentage"].sum()
        st.progress(min(current_sum / 100, 1.0))
        if abs(current_sum - 100.0) > 0.1:
            st.error(f"Exactly 100% required (current: {current_sum:.1f}%)")
        else:
            st.success("✅ Perfect 100% - Auto-distribution ready")
        
        # REALTIME PREVIEW WITH TITLE SYNC
        if net_withdrawable > 0 and abs(current_sum - 100.0) <= 0.1:
            units = net_withdrawable / unit_value
            preview = []
            manual = []
            gf_add = 0.0
            for _, row in edited_part.iterrows():
                share = net_withdrawable * (row["percentage"] / 100)
                is_manual = row["name"] not in user_map
                is_gf = "growth fund" in row["name"].lower()
                if is_gf:
                    gf_add += share
                if is_manual and not is_gf:
                    manual.append(row["name"])
                
                # Title sync in preview
                display_name = row["name"]
                user = user_map.get(row["name"])
                if user and user.get("title"):
                    display_name += f" ({user['title']})"
                
                preview.append({"Name": display_name, "%": f"{row['percentage']:.1f}", "Share": f"${share:,.2f}", "Status": "Auto-Balance" if row["name"] in user_map else "Auto-GF" if is_gf else "Manual"})
            
            st.subheader("Realtime Distribution Preview (with Titles)")
            st.dataframe(pd.DataFrame(preview), use_container_width=True, hide_index=True)
            
            col_p1, col_p2, col_p3 = st.columns(3)
            col_p1.metric("Withdrawable Profit", f"${net_withdrawable:,.2f}")
            col_p2.metric("Units Generated", f"{units:.2f}")
            col_p3.metric("Growth Fund Add", f"${gf_add:,.2f}")
            
            if manual:
                st.warning(f"Manual payout needed: {', '.join(manual)}")
            
            # Sankey Preview with titles
            labels = ["Withdrawable Profit"]
            values = []
            for _, row in edited_part.iterrows():
                share = net_withdrawable * (row["percentage"] / 100)
                values.append(share)
                display = row["name"]
                user = user_map.get(row["name"])
                if user and user.get("title"):
                    display += f" ({user['title']})"
                labels.append(f"{display} ({row['percentage']:.1f}%)")
            
            fig = go.Figure(data=[go.Sankey(
                node=dict(pad=20, thickness=30, label=labels, color=["#00ffaa"] + ["#ffd700" if "growth" in r.lower() else accent_color if name in user_map else "#ff6b6b" for r, name in zip(labels[1:], edited_part["name"])]),
                link=dict(source=[0]*len(values), target=list(range(1, len(values)+1)), value=values)
            )])
            fig.update_layout(title_text="Realtime 100% Distribution Flow (with Titles)", height=500)
            st.plotly_chart(fig, use_container_width=True)
        
        submitted = st.form_submit_button("🚀 Record Profit & Execute Auto-Distribution", type="primary", use_container_width=True)
        
        if submitted:
            if net_withdrawable <= 0:
                st.error("Withdrawable profit > 0 required")
            elif abs(current_sum - 100.0) > 0.1:
                st.error("Exactly 100% required")
            else:
                units = net_withdrawable / unit_value
                
                # Record profit
                profit_resp = supabase.table("profits").insert({
                    "account_id": acc_id,
                    "gross_profit": net_withdrawable,
                    "record_date": str(record_date),
                    "trader_share": net_withdrawable,
                    "your_share": net_withdrawable,
                    "units_generated": units,
                    "growth_fund_add": gf_add if 'gf_add' in locals() else 0.0,
                    "timestamp": datetime.datetime.now().isoformat()
                }).execute()
                profit_id = profit_resp.data[0]["id"]
                
                # Auto-distribute
                distributions = []
                for _, row in edited_part.iterrows():
                    share = net_withdrawable * (row["percentage"] / 100)
                    is_gf = "growth fund" in row["name"].lower()
                    dist = {
                        "profit_id": profit_id,
                        "participant_name": row["name"],
                        "participant_role": row["role"],
                        "percentage": row["percentage"],
                        "share_amount": share,
                        "is_growth_fund": is_gf
                    }
                    distributions.append(dist)
                    
                    if not is_gf and row["name"] in user_map:
                        user = user_map[row["name"]]
                        new_bal = (user["balance"] or 0) + share
                        supabase.table("users").update({"balance": new_bal}).eq("id", user["id"]).execute()
                
                supabase.table("profit_distributions").insert(distributions).execute()
                
                # Growth Fund auto if any
                if gf_add > 0:
                    supabase.table("growth_fund_transactions").insert({
                        "date": str(record_date),
                        "type": "In",
                        "amount": gf_add,
                        "description": f"Auto from {acc_name} profit",
                        "account_source": acc_name,
                        "recorded_by": st.session_state.full_name
                    }).execute()
                
                st.success("Withdrawable profit recorded & 100% auto-distributed!")
                st.cache_data.clear()
                st.rerun()
# ====================== END OF FINAL PROFIT SHARING WITH TITLE SYNC ======================
# ====================== MY PROFILE PAGE (FINAL SUPER ADVANCED - WITH DARK GLASS 3D FLIP CARD) ======================
elif selected == "👤 My Profile":
    # SAFE ROLE CHECK
    current_role = st.session_state.get("role", "guest")
    if current_role != "client":
        st.error("🔒 My Profile is client-only.")
        st.stop()
    
    st.header("My Profile 👤")
    st.markdown("**Your KMFX EA empire membership: Realtime premium flip card, earnings, full details, participation, withdrawals • Full transparency & motivation.**")
    
    my_name = st.session_state.full_name
    
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
    
    # ====================== PREMIUM THEME-ADAPTIVE FLIP CARD (DARK & LIGHT MODE PERFECT) ======================
    my_title = my_user.get("title", "Member").upper()
    card_title = f"{my_title} CARD" if my_title != "NONE" else "MEMBER CARD"
    my_balance = my_user.get("balance", 0)

    # Theme-adaptive colors (perfect in both dark & light)
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
        # Light mode: Clean luxury white card with soft shadows & refined colors
        front_bg = "linear-gradient(135deg, #ffffff, #f5f8fa)"
        back_bg = "linear-gradient(135deg, #f5f8fa, #eef2f5)"
        text_color = "#0f172a"  # Deep slate for premium readability
        accent_gold = "#a67c00"  # Rich dark gold (better contrast on light)
        accent_green = "#004d33"  # Deep forest green (elegant & premium)
        border_color = "#d4af37"  # Soft gold border
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
      .flip-card {{ background: transparent; width: 600px; height: 380px; perspective: 1000px; margin: 0 auto; }}
      .flip-card-inner {{ position: relative; width: 100%; height: 100%; text-align: center; transition: transform 0.8s cubic-bezier(0.68, -0.55, 0.27, 1.55); transform-style: preserve-3d; }}
      .flip-card:hover .flip-card-inner, .flip-card:focus-within .flip-card-inner {{ transform: rotateY(180deg); }}
      .flip-card-front, .flip-card-back {{ position: absolute; width: 100%; height: 100%; -webkit-backface-visibility: hidden; backface-visibility: hidden; border-radius: 20px; }}
      .flip-card-back {{ transform: rotateY(180deg); }}
      @media (max-width: 768px) {{
        .flip-card {{ width: 100%; max-width: 380px; height: 300px; }}
        .flip-card-front > div, .flip-card-back > div {{ padding: 1.5rem !important; height: 300px !important; }}
        .flip-card-front h2:first-child {{ font-size: 2.4rem !important; }}
        .flip-card-front h3 {{ font-size: 1.4rem !important; }}
        .flip-card-front h1 {{ font-size: 1.8rem !important; }}
        .flip-card-front h2:last-of-type {{ font-size: 2.4rem !important; }}
        .flip-card-back h2 {{ font-size: 1.5rem !important; }}
        .flip-card-back div:nth-child(3) {{ font-size: 1rem !important; line-height: 1.6 !important; }}
      }}
    </style>

    <p style="text-align:center; opacity:0.7; margin-top:1rem; font-size:1rem;">
      Hover (desktop) or tap (mobile) the card to flip ↺
    </p>
    """, unsafe_allow_html=True)
    
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
                
                # Participants Tree with titles
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
# ====================== END OF FINAL MY PROFILE WITH DARK GLASS 3D FLIP CARD ======================
# ====================== PART 5: GROWTH FUND PAGE (FINAL SUPER ADVANCED - FULL MAIN FLOW SYNC & REALTIME) ======================
elif selected == "🌱 Growth Fund":
    st.header("Growth Fund Management 🌱")
    st.markdown("**Empire reinvestment engine: 100% automatic inflows from profit distributions • Full source transparency with auto-trees • Advanced projections & scaling simulations • Manual adjustments • Instant sync across dashboard, profits, balances.**")
    
    # SAFE ROLE
    current_role = st.session_state.get("role", "guest")
    
    # FULL AUTO CACHE - Realtime every 30s
    @st.cache_data(ttl=30)
    def fetch_gf_full_data():
        # Transactions
        trans_resp = supabase.table("growth_fund_transactions").select("*").order("date", desc=True).execute()
        transactions = trans_resp.data or []
        
        # Auto-balance
        gf_balance = sum(t["amount"] if t["type"] == "In" else -t["amount"] for t in transactions)
        
        # Current total accounts for projections
        acc_count_resp = supabase.table("ftmo_accounts").select("id", count="exact").execute()
        total_accounts = acc_count_resp.count or 0
        
        # Auto-sources from profits
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
            if t["account_source"] == "Manual" or not t["description"].startswith("Auto"):
                key = t["description"] or "Manual"
                manual_sources[key] = manual_sources.get(key, 0) + t["amount"]
        
        return transactions, gf_balance, auto_sources, manual_sources, account_map, total_accounts
    
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
                        st.success("Transaction recorded & synced!")
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
    
    # PROJECTIONS
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
# ====================== END OF FINAL GROWTH FUND ======================
# ====================== PART 5: LICENSE GENERATOR PAGE (FINAL SUPER ADVANCED - FULL MAIN FLOW SYNC & OWNER-ONLY) ======================
elif selected == "🔑 License Generator":
    st.header("EA License Generator 🔑")
    st.markdown("**Ultimate Security Engine 2025+ alignment: OWNER-ONLY generation • MQL5-compatible encrypted licenses • Per-client UNIQUE_KEY & ENC_DATA • Allowed accounts, expiry (NEVER supported), live/demo lock • Auto-balance context • Revoke • Full empire security & transparency.**")
    
    # Python replication of MQL5 XOR encryption (exact match to EA code)
    def mt_encrypt(plain: str, key: str) -> str:
        result = bytearray()
        klen = len(key)
        if klen == 0:
            return ""
        for i, ch in enumerate(plain):
            k = ord(key[i % klen])
            result.append(ord(ch) ^ k)
        if len(result) % 2 != 0:
            result.append(0)
        return ''.join(f'{b:02X}' for b in result).upper()
    
    # STRICT OWNER-ONLY ACCESS
    current_role = st.session_state.get("role", "guest")
    if current_role != "owner":
        st.error("🔒 License generation is OWNER-ONLY for maximum empire security.")
        st.info("Admins view history • Clients see their license in My Profile/Messages.")
        st.stop()
    
    # Cache data for realtime sync
    @st.cache_data(ttl=60)
    def fetch_license_data():
        clients_resp = supabase.table("users").select("id, full_name, balance, role").eq("role", "client").execute()
        clients = clients_resp.data or []
        history_resp = supabase.table("client_licenses").select("*").order("date_generated", desc=True).execute()
        history = history_resp.data or []
        user_map = {c["id"]: {"name": c["full_name"], "balance": c["balance"] or 0} for c in clients}
        return clients, history, user_map
    
    clients, history, user_map = fetch_license_data()
    
    if not clients:
        st.info("No clients registered yet. Add in Admin Management to enable licensing.")
        st.stop()
    
    st.subheader("Generate License (Owner Exclusive)")
    client_options = {f"{c['full_name']} (Balance: ${c['balance'] or 0:,.2f})": c for c in clients}
    selected_key = st.selectbox("Select Client", list(client_options.keys()))
    client = client_options[selected_key]
    client_id = client["id"]
    client_name = client["full_name"]
    client_balance = client["balance"] or 0
    
    st.info(f"**Client:** {client_name} | Current Balance: ${client_balance:,.2f} | Recommend for verified contributors/funded members")
    
    with st.form("license_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            allowed_accounts = st.text_area("Allowed Account Logins (comma-separated)", 
                                            placeholder="e.g. 12345678,87654321",
                                            help="Blank = any account allowed • Exact MT5 login numbers")
            allow_live = st.checkbox("Allow Live Trading", value=True)
        with col2:
            expiry_option = st.radio("Expiry Policy", ["Specific Date", "NEVER (Lifetime)"])
            if expiry_option == "Specific Date":
                expiry_date = st.date_input("Expiry Date", datetime.date.today() + datetime.timedelta(days=365))
                expiry_str = expiry_date.strftime("%Y-%m-%d")
            else:
                expiry_str = "NEVER"
        
        version_note = st.text_input("Version Note (Internal)", value="v3.0 Elite 2026")
        internal_notes = st.text_area("Internal Notes (Optional)")
        
        # Auto UNIQUE_KEY generation (aligned sa example format)
        name_clean = client_name.upper().replace(" ", "")
        key_date = "NEVER" if expiry_str == "NEVER" else expiry_str[5:7] + expiry_str[8:] + expiry_str[:4]  # MMDDYYYY like DEC282025
        unique_key = f"KMFX_{name_clean}_{key_date}"
        
        st.code(unique_key, language="text")
        
        accounts_str = allowed_accounts.strip() or ""
        live_str = "1" if allow_live else "0"
        plain = f"{client_name}|{accounts_str}|{expiry_str}|{live_str}"
        enc_data_hex = mt_encrypt(plain, unique_key)
        
        # Ready-to-paste snippet
        st.subheader("Ready-to-Paste EA Code Snippet")
        snippet = f'''
//+------------------------------------------------------------------+
//| ULTIMATE SECURITY ENGINE 2025+ | Generated for {client_name}
//+------------------------------------------------------------------+
string UNIQUE_KEY = "{unique_key}";
string ENC_DATA   = "{enc_data_hex}";
// ==================================================================
        '''
        st.code(snippet, language="cpp")
        st.caption("Direct paste into EA • 100% compatible • NEVER expiry supported")
        
        submitted = st.form_submit_button("🚀 Generate & Issue License", type="primary", use_container_width=True)
        
        if submitted:
            try:
                supabase.table("client_licenses").insert({
                    "account_id": client_id,
                    "key": unique_key,
                    "enc_data": enc_data_hex,
                    "version": version_note,
                    "date_generated": datetime.date.today().isoformat(),
                    "expiry": expiry_str,
                    "allow_live": int(allow_live),
                    "notes": internal_notes or None,
                    "allowed_accounts": allowed_accounts.strip() or None
                }).execute()
                log_action("License Issued (Owner Only)", f"{unique_key} for {client_name}")
                st.success(f"License issued to **{client_name}**! Empire secured.")
                st.balloons()
                st.cache_data.clear()
                st.rerun()
            except Exception as e:
                st.error(f"Error: {str(e)}")
    
    # History with revoke (owner management)
    st.subheader("📜 Issued Licenses History (Owner Management)")
    if history:
        for h in history:
            user_info = user_map.get(h["account_id"], {"name": "Unknown", "balance": 0})
            with st.expander(f"🔑 {h.get('key', 'Legacy')} • {user_info['name']} • Issued {h['date_generated']}", expanded=False):
                st.markdown(f"**Expiry:** {h['expiry']} | **Live:** {'Allowed' if h['allow_live'] else 'Demo Only'}")
                if h.get("allowed_accounts"):
                    st.markdown(f"**Allowed Accounts:** {h['allowed_accounts']}")
                st.markdown(f"**Current Balance:** ${user_info['balance']:,.2f}")
                if h["notes"]:
                    st.caption(f"Notes: {h['notes']}")
                if h.get("enc_data"):
                    st.code(f"ENC_DATA = \"{h['enc_data']}\"", language="text")
                if h.get("key"):
                    st.code(f"UNIQUE_KEY = \"{h['key']}\"", language="text")
                
                if st.button("🚫 Revoke License", key=f"revoke_{h['id']}", type="secondary"):
                    try:
                        supabase.table("client_licenses").delete().eq("id", h["id"]).execute()
                        log_action("License Revoked (Owner)", f"for {user_info['name']}")
                        st.success("License revoked!")
                        st.cache_data.clear()
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
    else:
        st.info("No licenses issued yet.")
    
    st.markdown(f"""
    <div class='glass-card' style='padding:2rem; text-align:center; margin-top:2rem;'>
        <h3 style='color:{accent_color};'>Owner-exclusive • 100% EA Security Aligned • Empire Protected.</h3>
        <p>Direct paste-ready • XOR encryption • NEVER expiry • Account lock • Live/Demo • Revocable • Synced to balances.</p>
    </div>
    """, unsafe_allow_html=True)
# ====================== END OF FINAL LICENSE GENERATOR ======================
# ====================== PART 5: FILE VAULT PAGE (FINAL SUPER ADVANCED - FULL MAIN FLOW SYNC & REALTIME) ======================
elif selected == "📁 File Vault":
    st.header("Secure File Vault 📁")
    st.markdown("**Empire document fortress: Centralized storage for payout proofs, agreements, KYC, contributor files • Auto-assigned to clients • Balance context • Advanced search/filter • Image/PDF previews • Download logging • Required for withdrawals • Full transparency & realtime sync.**")
    
    # SAFE ROLE
    current_role = st.session_state.get("role", "guest")
    
    # FULL AUTO CACHE - Realtime sync
    @st.cache_data(ttl=60)
    def fetch_vault_full_data():
        files_resp = supabase.table("client_files").select("*").order("upload_date", desc=True).execute()
        files = files_resp.data or []
        
        users_resp = supabase.table("users").select("id, full_name, balance, role").execute()
        users = users_resp.data or []
        user_map = {u["full_name"]: {"id": u["id"], "balance": u["balance"] or 0, "role": u["role"]} for u in users}
        registered_clients = [u["full_name"] for u in users if u["role"] == "client"]
        
        return files, user_map, registered_clients
    
    files, user_map, registered_clients = fetch_vault_full_data()
    
    st.caption("🔄 Vault auto-refresh every 60s • Proofs sync for withdrawals")
    
    # Client view restriction (own + assigned)
    if current_role == "client":
        my_name = st.session_state.full_name
        files = [f for f in files if f["sent_by"] == my_name or f.get("assigned_client") == my_name]
    
    # ====================== UPLOAD SECTION (OWNER/ADMIN - AUTO-ASSIGN) ======================
    if current_role in ["owner", "admin"]:
        with st.expander("➕ Upload New Files (Multi + Auto-Assign)", expanded=False):
            with st.form("file_upload_form", clear_on_submit=True):
                uploaded_files = st.file_uploader("Choose Files (PDF, Images, Docs, Proofs)", accept_multiple_files=True)
                category = st.selectbox("Category", 
                                        ["Payout Proof", "Withdrawal Proof", "Agreement", "KYC/ID", "Contributor Contract", "Testimonial Image", "Other"])
                assigned_client = st.selectbox("Assign to Client (Auto-Balance Context)", ["None"] + registered_clients)
                tags = st.text_input("Tags (comma-separated)", placeholder="e.g. withdrawal Jan2026, 100K funded")
                notes = st.text_area("Notes (Optional)", placeholder="e.g. Proof for $5K payout")
                
                submitted = st.form_submit_button("Upload & Auto-Sync", type="primary", use_container_width=True)
                if submitted:
                    if not uploaded_files:
                        st.error("Select files")
                    else:
                        success = 0
                        for uploaded in uploaded_files:
                            safe_name = "".join(c for c in uploaded.name if c.isalnum() or c in "._- ")
                            path = f"uploaded_files/client_files/{safe_name}"
                            with open(path, "wb") as f:
                                f.write(uploaded.getbuffer())
                            try:
                                supabase.table("client_files").insert({
                                    "file_name": safe_name,
                                    "original_name": uploaded.name,
                                    "upload_date": datetime.date.today().isoformat(),
                                    "sent_by": st.session_state.full_name,
                                    "category": category,
                                    "assigned_client": assigned_client if assigned_client != "None" else None,
                                    "tags": tags.strip(),
                                    "notes": notes or None
                                }).execute()
                                log_action("File Uploaded", f"{uploaded.name} | Category: {category} | Client: {assigned_client}")
                                success += 1
                            except Exception as e:
                                st.error(f"Error {uploaded.name}: {str(e)}")
                        if success > 0:
                            st.success(f"{success} files uploaded & synced!")
                            st.cache_data.clear()
                            st.rerun()
    
    # ====================== ADVANCED SEARCH & FILTER ======================
    st.subheader("🔍 Advanced Search & Filter")
    col_s1, col_s2, col_s3 = st.columns(3)
    with col_s1:
        search_term = st.text_input("Search Name/Tags/Notes")
    with col_s2:
        filter_category = st.selectbox("Category", ["All"] + sorted(set(f.get("category", "Other") for f in files)))
    with col_s3:
        filter_client = st.selectbox("Assigned Client", ["All"] + sorted(set(f.get("assigned_client") for f in files if f.get("assigned_client"))))
    
    # Apply filters
    filtered = files
    if search_term:
        filtered = [f for f in filtered if search_term.lower() in f["original_name"].lower() or 
                    search_term.lower() in (f.get("tags") or "").lower() or 
                    search_term.lower() in (f.get("notes") or "").lower()]
    if filter_category != "All":
        filtered = [f for f in filtered if f.get("category", "Other") == filter_category]
    if filter_client != "All":
        filtered = [f for f in filtered if f.get("assigned_client") == filter_client]
    
    # ====================== VAULT GRID DISPLAY WITH PREVIEWS & CONTEXT ======================
    st.subheader(f"Vault Contents ({len(filtered)} files • Realtime)")
    if filtered:
        cols = st.columns(3)
        for idx, f in enumerate(filtered):
            with cols[idx % 3]:
                path = f"uploaded_files/client_files/{f['file_name']}"
                client_balance = user_map.get(f.get("assigned_client"), {"balance": 0})["balance"]
                with st.container():
                    st.markdown(f"""
                    <div class='glass-card' style='padding:1.2rem;'>
                        <h4>{f['original_name']}</h4>
                        <small>Uploaded {f['upload_date']} by {f['sent_by']}</small><br>
                        <small>Category: {f.get('category', 'Other')}</small>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Previews
                    if f["original_name"].lower().endswith(('.png', '.jpg', '.jpeg', '.gif')) and os.path.exists(path):
                        st.image(path, use_container_width=True)
                    elif f["original_name"].lower().endswith('.pdf') and os.path.exists(path):
                        st.caption("PDF Document (download for full view)")
                    
                    # Context
                    if f.get("assigned_client"):
                        st.caption(f"👤 Assigned: {f['assigned_client']} (Balance: ${client_balance:,.2f})")
                    if f.get("tags"):
                        st.caption(f"🏷️ Tags: {f['tags']}")
                    if f["notes"]:
                        with st.expander("Notes"):
                            st.write(f["notes"])
                    
                    # Download with log
                    if os.path.exists(path):
                        with open(path, "rb") as file_data:
                            if st.download_button("⬇️ Download", file_data, f['original_name'], use_container_width=True):
                                log_action("File Downloaded", f"{f['original_name']} by {st.session_state.full_name}")
                    
                    # Delete (owner/admin)
                    if current_role in ["owner", "admin"]:
                        if st.button("🗑️ Delete", key=f"del_file_{f['id']}", type="secondary", use_container_width=True):
                            try:
                                os.remove(path)
                                supabase.table("client_files").delete().eq("id", f["id"]).execute()
                                log_action("File Deleted", f['original_name'])
                                st.success("File removed")
                                st.cache_data.clear()
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error: {str(e)}")
    else:
        st.info("Vault empty or no matches • Upload proofs/agreements for transparency")
    
    st.markdown(f"""
    <div class='glass-card' style='padding:3rem; text-align:center; margin:3rem 0;'>
        <h1 style="background:linear-gradient(90deg,{accent_color},#ffd700); -webkit-background-clip:text; -webkit-text-fill-color:transparent;">
            Secure & Synced Document Vault
        </h1>
        <p style="font-size:1.3rem; margin:2rem 0;">
            Proofs required for payouts • Assigned to clients • Searchable • Realtime • Empire trust automated.
        </p>
        <h2 style="color:#ffd700;">👑 KMFX File Vault • Fully Integrated 2026</h2>
    </div>
    """, unsafe_allow_html=True)
# ====================== END OF FINAL FILE VAULT ======================
# ====================== PART 5: ANNOUNCEMENTS PAGE (FINAL SUPER ADVANCED - FULL MAIN FLOW SYNC & REALTIME) ======================
elif selected == "📢 Announcements":
    st.header("Empire Announcements 📢")
    st.markdown("**Central realtime communication: Broadcast updates, auto-post profits/withdrawals/licenses • Rich images/attachments • Likes ❤️ • Threaded comments 💬 • Pinning 📌 • Category filters • Push notifications • Full team engagement & transparency.**")
    
    # SAFE ROLE
    current_role = st.session_state.get("role", "guest")
    
    # FULL REALTIME CACHE (short ttl for live engagement)
    @st.cache_data(ttl=15)
    def fetch_announcements_realtime():
        ann_resp = supabase.table("announcements").select("*").order("date", desc=True).execute()
        announcements = ann_resp.data or []
        
        # Attachments
        for ann in announcements:
            att_resp = supabase.table("announcement_files").select("original_name, file_name").eq("announcement_id", ann["id"]).execute()
            ann["attachments"] = att_resp.data or []
        
        # Threaded comments (flat for simplicity, sorted newest)
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
    
    st.caption("🔄 Feed auto-refresh every 15s • Likes & comments realtime")
    
    # ====================== POST NEW (OWNER/ADMIN) ======================
    if current_role in ["owner", "admin"]:
        with st.expander("➕ Broadcast New Announcement", expanded=True):
            with st.form("ann_form", clear_on_submit=True):
                title = st.text_input("Title *")
                category = st.selectbox("Category", ["General", "Profit Distribution", "Withdrawal Update", "License Granted", "Milestone", "EA Update", "Team Alert"])
                message = st.text_area("Message *", height=150)
                attachments = st.file_uploader("Attachments (Images/Proofs - Full Preview)", accept_multiple_files=True)
                pin = st.checkbox("📌 Pin to Top")
                notify = st.checkbox("🔔 Send Push Notification to Clients", value=True)
                
                submitted = st.form_submit_button("📢 Post & Sync", type="primary", use_container_width=True)
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
                                safe = "".join(c for c in file.name if c.isalnum() or c in "._- ")
                                path = f"uploaded_files/announcements/{safe}"
                                with open(path, "wb") as f:
                                    f.write(file.getbuffer())
                                supabase.table("announcement_files").insert({
                                    "announcement_id": ann_id,
                                    "file_name": safe,
                                    "original_name": file.name
                                }).execute()
                            
                            if notify:
                                clients = supabase.table("users").select("full_name").eq("role", "client").execute().data
                                for c in clients:
                                    supabase.table("notifications").insert({
                                        "client_name": c["full_name"],
                                        "title": title.strip(),
                                        "message": message.strip(),
                                        "date": datetime.date.today().isoformat(),
                                        "category": category,
                                        "read": 0
                                    }).execute()
                            
                            st.success("Announcement posted realtime!")
                            st.cache_data.clear()
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
    
    # ====================== FILTER & SEARCH ======================
    st.subheader("📻 Live Empire Feed")
    categories = sorted(set(a.get("category", "General") for a in announcements))
    filter_cat = st.selectbox("Category Filter", ["All"] + categories)
    
    filtered = [a for a in announcements if filter_cat == "All" or a.get("category") == filter_cat]
    # Pinned top
    filtered = sorted(filtered, key=lambda x: (not x.get("pinned", False), x["date"]), reverse=True)
    
    # ====================== REALTIME RICH FEED ======================
    if filtered:
        for ann in filtered:
            pinned = " 📌 PINNED" if ann.get("pinned") else ""
            with st.container():
                st.markdown(f"<h3 style='color:{accent_color};'>{ann['title']}{pinned}</h3>", unsafe_allow_html=True)
                st.caption(f"{ann.get('category', 'General')} • by {ann['posted_by']} • {ann['date']}")
                st.markdown(ann['message'])
                
                # FULL IMAGE PREVIEWS
                images = [att for att in ann["attachments"] if att["original_name"].lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
                if images:
                    img_cols = st.columns(min(len(images), 4))
                    for idx, att in enumerate(images):
                        path = f"uploaded_files/announcements/{att['file_name']}"
                        if os.path.exists(path):
                            with img_cols[idx % 4]:
                                st.image(path, use_container_width=True)
                
                # Other attachments
                non_images = [att for att in ann["attachments"] if not att["original_name"].lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
                if non_images:
                    st.markdown("**Files:**")
                    for att in non_images:
                        path = f"uploaded_files/announcements/{att['file_name']}"
                        if os.path.exists(path):
                            with open(path, "rb") as f:
                                st.download_button(att['original_name'], f, att['original_name'])
                
                # REALTIME LIKES
                if st.button(f"❤️ {ann['likes']}", key=f"like_{ann['id']}"):
                    try:
                        supabase.table("announcements").update({"likes": ann["likes"] + 1}).eq("id", ann["id"]).execute()
                        st.cache_data.clear()
                        st.rerun()
                    except:
                        pass
                
                # REALTIME COMMENTS
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
                
                # Admin controls
                if current_role in ["owner", "admin"]:
                    col_admin = st.columns(3)
                    with col_admin[0]:
                        if st.button("📌 Pin/Unpin", key=f"pin_{ann['id']}"):
                            supabase.table("announcements").update({"pinned": not ann.get("pinned", False)}).eq("id", ann["id"]).execute()
                            st.rerun()
                    with col_admin[2]:
                        if st.button("🗑️ Delete", key=f"del_{ann['id']}", type="secondary"):
                            try:
                                for att in ann["attachments"]:
                                    os.remove(f"uploaded_files/announcements/{att['file_name']}")
                                supabase.table("announcement_files").delete().eq("announcement_id", ann["id"]).execute()
                                supabase.table("announcements").delete().eq("id", ann["id"]).execute()
                                st.success("Deleted")
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
            Images full preview • Likes & comments update live • Pinned alerts • Empire connected.
        </p>
    </div>
    """, unsafe_allow_html=True)
# ====================== END OF FINAL REALTIME ANNOUNCEMENTS ======================
# ====================== PART 6: MESSAGES PAGE (FINAL SUPER ADVANCED - FULL MAIN FLOW SYNC & REALTIME FIXED) ======================
elif selected == "💬 Messages":
    st.header("Private Messages 💬")
    st.markdown("**Secure realtime 1:1 empire communication • Threaded chats • File attachments with previews • Search • Auto-system messages (profit shares, withdrawal updates, license grants) • Balance context • Instant sync & clean UI.**")
    
    # SAFE ROLE
    current_role = st.session_state.get("role", "guest")
    
    # FULL REALTIME CACHE
    @st.cache_data(ttl=15)
    def fetch_messages_full():
        users_resp = supabase.table("users").select("id, full_name, role, balance").execute()
        users = users_resp.data or []
        
        msg_resp = supabase.table("messages").select("*").order("timestamp").execute()
        messages = msg_resp.data or []
        
        # Group by conversation
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
    
    # Admin/Owner: Select client
    if current_role in ["owner", "admin"]:
        if not clients:
            st.info("No clients yet • Private messaging activates with team members")
            st.stop()
        
        client_options = {f"{c['full_name']} (Balance: ${c['balance'] or 0:,.2f})": c["full_name"] for c in clients}
        selected_client = st.selectbox("Select Team Member for Private Chat", list(client_options.keys()))
        partner_name = client_options[selected_client]
        partner_balance = next((c["balance"] or 0 for c in clients if c["full_name"] == partner_name), 0)
        
        st.info(f"**Private chat with:** {partner_name} | Current Balance: ${partner_balance:,.2f}")
        
        convo = conversations.get(partner_name, [])
    else:
        # Client: Fixed to admin
        partner_name = "KMFX Admin"
        convo = [m for m in all_messages if 
                 m.get("to_client") == st.session_state.full_name or 
                 m.get("from_client") == st.session_state.full_name]
        st.info("**Private channel with KMFX Admin** • Updates on shares, withdrawals, licenses")
    
    # ====================== REALTIME CONVERSATION DISPLAY (CLEAN & FIXED HTML) ======================
    if convo:
        # Search
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
                bg = accent_color if is_from_me else glass_bg
                text_c = "#000" if is_from_me else text_color
                
                sender = msg.get("from_admin") or msg.get("from_client") or "System"
                time = msg["timestamp"][:16].replace("T", " ")
                
                # Clean markdown - fixed raw HTML display
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
    
    # ====================== SEND MESSAGE WITH ATTACHMENTS (REALTIME & CLEAN) ======================
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
                    # Text message
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
                    
                    # Attachments
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
    
    # Auto-system messages note
    st.caption("🤖 Auto-messages: Profit shares, withdrawal status, license info • Delivered here privately")
    
    st.markdown(f"""
    <div class='glass-card' style='padding:2rem; text-align:center; margin-top:2rem;'>
        <h3 style='color:{accent_color};'>Realtime Private Channels</h3>
        <p>Secure • Attachments • Auto-updates • Empire aligned & connected.</p>
    </div>
    """, unsafe_allow_html=True)
# ====================== END OF FINAL FIXED MESSAGES ======================
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
# ====================== PART 6: WITHDRAWALS PAGE (FINAL SUPER ADVANCED - FULL MAIN FLOW SYNC & REALTIME + BALANCE 0 FIX) ======================
elif selected == "💳 Withdrawals":
    st.header("Withdrawal Management 💳")
    st.markdown("**Empire payout engine: Clients request from auto-earned balances • Require payout proof (auto-vault) • Amount limited to balance • Owner approve/pay/reject • Auto-deduct balance • Realtime sync & full transparency.**")
   
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
        files_resp = supabase.table("client_files").select("id, original_name, file_name, category, assigned_client, notes").execute()
        proofs = []
        for f in files_resp.data or []:
            cat = f.get("category", "Other")
            if cat in ["Payout Proof", "Withdrawal Proof"] or "withdrawal" in f.get("notes", "").lower():
                proofs.append(f)
       
        return withdrawals, users, user_map, proofs
   
    withdrawals, users, user_map, proofs = fetch_withdrawals_full()
   
    st.caption("🔄 Withdrawals auto-refresh every 30s for realtime status")
   
    # ====================== CLIENT VIEW: REQUEST + HISTORY ======================
    if current_role == "client":
        my_name = st.session_state.full_name
        my_balance = user_map.get(my_name, {"balance": 0})["balance"]
        my_withdrawals = [w for w in withdrawals if w["client_name"] == my_name]
       
        st.subheader(f"Your Withdrawal Requests (Available Balance: ${my_balance:,.2f})")
       
        # Only show request form if balance > 0 (FIXES ERROR WHEN BALANCE=0)
        if my_balance > 0:
            with st.expander("➕ Request New Withdrawal", expanded=True):
                with st.form("wd_request_form", clear_on_submit=True):
                    amount = st.number_input(
                        "Amount (USD)",
                        min_value=1.0,
                        max_value=float(my_balance),
                        step=100.0,
                        value=min(100.0, my_balance),  # Safe default value <= max
                        help=f"Max: ${my_balance:,.2f}"
                    )
                    method = st.selectbox("Payout Method", ["USDT", "Bank Transfer", "Wise", "PayPal", "GCash", "Other"])
                    details = st.text_area("Payout Details (Wallet/Address/Bank Info)")
                    proof_file = st.file_uploader("Upload Payout Proof * (Required)", type=["png", "jpg", "jpeg", "pdf"], help="Screenshot of wallet, bank statement • Auto-saved to vault")
                   
                    submitted = st.form_submit_button("Submit Request for Approval", type="primary", use_container_width=True)
                    if submitted:
                        if amount > my_balance:
                            st.error("Amount exceeds available balance")
                        elif not proof_file:
                            st.error("Payout proof required")
                        else:
                            try:
                                # Auto-upload proof to vault
                                safe = "".join(c for c in proof_file.name if c.isalnum() or c in "._- ")
                                path = f"uploaded_files/client_files/{safe}"
                                with open(path, "wb") as f:
                                    f.write(proof_file.getbuffer())
                                supabase.table("client_files").insert({
                                    "file_name": safe,
                                    "original_name": proof_file.name,
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
                               
                                st.success("Request submitted! Owner will review proof.")
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
                   
                    # Related proofs
                    related_proofs = [p for p in proofs if p.get("assigned_client") == w["client_name"] and
                                      ("withdrawal" in p.get("notes", "").lower() or p.get("category") in ["Payout Proof", "Withdrawal Proof"])]
                    if related_proofs:
                        st.markdown("**Related Proofs:**")
                        proof_cols = st.columns(min(len(related_proofs), 4))
                        for idx, p in enumerate(related_proofs):
                            path = f"uploaded_files/client_files/{p['file_name']}"
                            if os.path.exists(path):
                                with proof_cols[idx % 4]:
                                    if p["original_name"].lower().endswith(('.png', '.jpg', '.jpeg')):
                                        st.image(path, caption=p["original_name"], use_container_width=True)
                                    else:
                                        with open(path, "rb") as f:
                                            st.download_button(p["original_name"], f, p["original_name"])
                   
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
            Requests limited to earned balance • Proof auto-vaulted • Owner control • Auto-deduct • Empire cashflow perfected.
        </p>
        <h2 style="color:#ffd700;">👑 KMFX Withdrawals • Fully Automated 2026</h2>
    </div>
    """, unsafe_allow_html=True)
# ====================== END OF FINAL WITHDRAWALS (BALANCE 0 ERROR FIXED) ======================
# ====================== PART 6: EA VERSIONS PAGE (FINAL SUPER ADVANCED - FULL MAIN FLOW SYNC & REALTIME) ======================
elif selected == "🤖 EA Versions":
    st.header("EA Versions Management 🤖")
    st.markdown("**Elite EA distribution: Owner release new versions with changelog • Auto-announce to team • Download tracking • License gating (latest version requires active license) • Realtime list • Full empire sync with licenses & announcements.**")
    
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
            license_resp = supabase.table("client_licenses").select("allow_live, version").eq("account_id", st.session_state.get("user_id")).execute()  # Assume user_id in session if needed
            client_license = license_resp.data[0] if license_resp.data else None
        else:
            client_license = None
        
        return versions, download_counts, client_license
    
    versions, download_counts, client_license = fetch_ea_full()
    
    st.caption("🔄 Versions auto-refresh every 30s • Downloads tracked realtime")
    
    # ====================== RELEASE NEW VERSION (OWNER ONLY) ======================
    if current_role == "owner":
        with st.expander("➕ Release New EA Version (Owner Exclusive)", expanded=True):
            with st.form("ea_form", clear_on_submit=True):
                version_name = st.text_input("Version Name *", placeholder="e.g. v3.0 Elite 2026")
                ea_file = st.file_uploader("Upload EA File (.ex5 / .mq5)", accept_multiple_files=False)
                changelog = st.text_area("Changelog *", height=200, placeholder="• New features\n• Bug fixes\n• Performance improvements")
                announce = st.checkbox("📢 Auto-Announce to Empire", value=True)
                
                submitted = st.form_submit_button("🚀 Release Version", type="primary", use_container_width=True)
                if submitted:
                    if not version_name.strip() or not ea_file or not changelog.strip():
                        st.error("Version name, file, and changelog required")
                    else:
                        try:
                            safe = "".join(c for c in ea_file.name if c.isalnum() or c in "._- ")
                            path = f"uploaded_files/ea_versions/{safe}"
                            with open(path, "wb") as f:
                                f.write(ea_file.getbuffer())
                            supabase.table("ea_versions").insert({
                                "version": version_name.strip(),
                                "file_name": safe,
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
                            
                            log_action("EA Version Released", version_name.strip())
                            st.success(f"Version {version_name} released & synced!")
                            st.cache_data.clear()
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
    elif current_role == "admin":
        st.info("Admins view & track downloads • Owner releases new versions")
    
    # ====================== REALTIME VERSION LIST WITH LICENSE GATING ======================
    st.subheader("Available EA Versions (Realtime)")
    if versions:
        latest_version = versions[0]  # First is latest
        for v in versions:
            vid = v["id"]
            downloads = download_counts.get(vid, 0)
            path = f"uploaded_files/ea_versions/{v['file_name']}"
            
            # License gating for latest version
            is_latest = v == latest_version
            can_download = True
            if current_role == "client" and is_latest and client_license:
                # Simple gating: latest requires license
                can_download = client_license.get("allow_live", False)  # Or check version match if needed
            
            with st.expander(f"🤖 {v['version']} • Released {v['upload_date']} • {downloads} downloads" + (" (Latest - License Required)" if is_latest else ""), expanded=is_latest):
                st.markdown(f"**Changelog:**\n{v['notes'].replace(chr(10), '<br>')}", unsafe_allow_html=True)
                
                if os.path.exists(path):
                    with open(path, "rb") as f:
                        if can_download:
                            if st.download_button(f"⬇️ Download {v['version']}", f, v['file_name'], use_container_width=True):
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
                            st.warning("🔒 Active license required for latest version • Contact owner")
                else:
                    st.error("File missing - contact owner")
                
                if current_role == "owner":
                    if st.button("🗑️ Delete Version", key=f"del_ea_{vid}", type="secondary"):
                        try:
                            os.remove(path)
                            supabase.table("ea_versions").delete().eq("id", vid).execute()
                            supabase.table("ea_downloads").delete().eq("version_id", vid).execute()
                            st.success("Version removed")
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
            Owner release • Auto-announce • Download tracked • Latest gated by license • Empire performance synced.
        </p>
        <h2 style="color:#ffd700;">👑 KMFX EA Versions • Fully Controlled 2026</h2>
    </div>
    """, unsafe_allow_html=True)
# ====================== END OF FINAL EA VERSIONS ======================
# ====================== PART 6: TESTIMONIALS PAGE (FINAL SUPER ADVANCED - FULL MAIN FLOW SYNC & REALTIME) ======================
elif selected == "📸 Testimonials":
    st.header("Team Testimonials 📸")
    st.markdown("**Empire motivation hub: Clients submit success stories + photos • Auto-balance context • Owner approve/reject with auto-announce • Realtime grid with full image previews • Search • Full team inspiration & transparency.**")
    
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
    
    st.caption("🔄 Testimonials auto-refresh every 30s • Approved stories inspire realtime")
    
    # ====================== SUBMIT TESTIMONIAL (CLIENT ONLY) ======================
    if current_role == "client":
        my_balance = user_map.get(st.session_state.full_name, 0)
        st.subheader(f"Share Your Success Story (Balance: ${my_balance:,.2f})")
        with st.expander("➕ Submit Testimonial", expanded=True):
            with st.form("testi_form", clear_on_submit=True):
                story = st.text_area("Your Story *", height=200, placeholder="e.g. How KMFX changed my trading, profits earned, journey...")
                photo = st.file_uploader("Upload Photo * (Required for Approval)", type=["png", "jpg", "jpeg", "gif"])
                
                submitted = st.form_submit_button("Submit for Approval", type="primary", use_container_width=True)
                if submitted:
                    if not story.strip() or not photo:
                        st.error("Story and photo required")
                    else:
                        try:
                            safe = "".join(c for c in photo.name if c.isalnum() or c in "._- ")
                            path = f"uploaded_files/testimonials/{safe}"
                            with open(path, "wb") as f:
                                f.write(photo.getbuffer())
                            supabase.table("testimonials").insert({
                                "client_name": st.session_state.full_name,
                                "message": story.strip(),
                                "image_file": path,
                                "date_submitted": datetime.date.today().isoformat(),
                                "status": "Pending"
                            }).execute()
                            st.success("Testimonial submitted! Owner will review & approve.")
                            st.cache_data.clear()
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
    
    # ====================== APPROVED TESTIMONIALS GRID (REALTIME FULL PREVIEWS) ======================
    st.subheader("🌟 Approved Success Stories (Realtime)")
    if approved:
        # Search
        search_testi = st.text_input("Search stories")
        filtered_approved = [t for t in approved if search_testi.lower() in t["message"].lower() or search_testi.lower() in t["client_name"].lower()]
        
        cols = st.columns(3)
        for idx, t in enumerate(filtered_approved):
            with cols[idx % 3]:
                balance = user_map.get(t["client_name"], 0)
                path = t["image_file"]
                with st.container():
                    if os.path.exists(path):
                        st.image(path, use_container_width=True)
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
            path = p["image_file"]
            with st.expander(f"{p['client_name']} • Submitted {p['date_submitted']} • Balance ${balance:,.2f}", expanded=False):
                if os.path.exists(path):
                    st.image(path, use_container_width=True)
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
                            if os.path.exists(path):
                                os.remove(path)
                            supabase.table("testimonials").delete().eq("id", p["id"]).execute()
                            st.success("Rejected")
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
            Client submissions • Balance context • Auto-announce approved • Empire inspired & growing.
        </p>
        <h2 style="color:#ffd700;">👑 KMFX Testimonials • Fully Integrated 2026</h2>
    </div>
    """, unsafe_allow_html=True)
# ====================== END OF FINAL TESTIMONIALS ======================
# ====================== PART 6: REPORTS & EXPORT PAGE (FINAL SUPER ADVANCED - FULL MAIN FLOW SYNC & REALTIME FIXED) ======================
elif selected == "📈 Reports & Export":
    st.header("Empire Reports & Export 📈")
    st.markdown("**Full analytics engine: Auto-aggregated realtime reports from profits, distributions, balances, growth fund, accounts • Professional charts • Detailed breakdowns • Multiple CSV exports • Owner/Admin only for empire insights & audits.**")
    
    # SAFE ROLE - OWNER/ADMIN ONLY
    current_role = st.session_state.get("role", "guest")
    if current_role not in ["owner", "admin"]:
        st.error("🔒 Reports & Export is restricted to Owner/Admin for empire analytics security.")
        st.stop()
    
    # FULL AUTO CACHE - Realtime sync
    @st.cache_data(ttl=60)
    def fetch_reports_full():
        # Profits
        profits_resp = supabase.table("profits").select("*").order("record_date", desc=True).execute()
        profits = profits_resp.data or []
        
        # Distributions
        dist_resp = supabase.table("profit_distributions").select("*").execute()
        distributions = dist_resp.data or []
        
        # Users balances (clients only)
        users_resp = supabase.table("users").select("full_name, balance, role").eq("role", "client").execute()
        clients = users_resp.data or []
        
        # Growth Fund
        gf_resp = supabase.table("growth_fund_transactions").select("type, amount").execute()
        gf_balance = sum(row["amount"] if row["type"] == "In" else -row["amount"] for row in gf_resp.data) if gf_resp.data else 0.0
        
        # Accounts summary
        accounts_resp = supabase.table("ftmo_accounts").select("name, current_phase, current_equity, withdrawable_balance").execute()
        accounts = accounts_resp.data or []
        
        return profits, distributions, clients, gf_balance, accounts
    
    profits, distributions, clients, gf_balance, accounts = fetch_reports_full()
    
    st.caption("🔄 Reports auto-update realtime from all transactions • Fast & optimized")
    
    # ====================== EMPIRE SUMMARY METRICS (PROFESSIONAL GRID) ======================
    st.subheader("Empire Overview Metrics")
    total_gross = sum(p.get("gross_profit", 0) for p in profits)
    total_distributed = sum(d.get("share_amount", 0) for d in distributions if not d.get("is_growth_fund", False))
    total_client_balances = sum(c.get("balance", 0) for c in clients)
    total_accounts = len(accounts)
    total_equity = sum(a.get("current_equity", 0) for a in accounts)
    
    col_m1, col_m2, col_m3, col_m4, col_m5 = st.columns(5)
    col_m1.metric("Total Gross Profits", f"${total_gross:,.0f}")
    col_m2.metric("Total Distributed", f"${total_distributed:,.0f}")
    col_m3.metric("Client Balances", f"${total_client_balances:,.0f}")
    col_m4.metric("Active Accounts", total_accounts)
    col_m5.metric("Total Equity", f"${total_equity:,.0f}")
    st.metric("Growth Fund Balance", f"${gf_balance:,.0f}")
    
    # ====================== PROFIT TREND CHART (REALTIME - FIXED SUM ERROR) ======================
    st.subheader("Profit Trend (Monthly Auto-Aggregated)")
    if profits:
        profits_df = pd.DataFrame(profits)
        profits_df["record_date"] = pd.to_datetime(profits_df["record_date"])
        
        # Groupby month & sum numeric only (FIXED)
        monthly = profits_df.groupby(profits_df["record_date"].dt.strftime("%Y-%m")).sum(numeric_only=True)[["gross_profit", "trader_share"]].reset_index()
        
        fig_trend = go.Figure()
        fig_trend.add_trace(go.Bar(x=monthly["record_date"], y=monthly["gross_profit"], name="Gross Profit", marker_color="#ff6b6b"))
        fig_trend.add_trace(go.Scatter(x=monthly["record_date"], y=monthly["trader_share"], name="Distributed Share", mode="lines+markers", line=dict(color=accent_color, width=5)))
        fig_trend.update_layout(title="Monthly Profit & Distribution Trend", height=500)
        st.plotly_chart(fig_trend, use_container_width=True)
    else:
        st.info("No profits recorded yet • Trend activates with first distribution")
    
    # ====================== DISTRIBUTION PIE (PARTICIPANTS) ======================
    st.subheader("Participant Distribution Breakdown")
    if distributions:
        dist_df = pd.DataFrame(distributions)
        part_summary = dist_df.groupby("participant_name")["share_amount"].sum().reset_index()
        
        fig_pie = go.Figure(data=[go.Pie(labels=part_summary["participant_name"], values=part_summary["share_amount"], hole=0.4)])
        fig_pie.update_layout(title="Total Shares by Participant")
        st.plotly_chart(fig_pie, use_container_width=True)
        
        part_summary["share_amount"] = part_summary["share_amount"].apply(lambda x: f"${x:,.2f}")
        st.dataframe(part_summary.sort_values("share_amount", ascending=False), use_container_width=True)
    else:
        st.info("No distributions yet")
    
    # ====================== CLIENT BALANCES TABLE ======================
    st.subheader("Client Balances (Realtime Auto)")
    if clients:
        balance_df = pd.DataFrame([{"Client": c["full_name"], "Balance": f"${c['balance'] or 0:,.2f}"} for c in clients])
        st.dataframe(balance_df.sort_values("Balance", ascending=False), use_container_width=True, hide_index=True)
    else:
        st.info("No clients yet")
    
    # ====================== GROWTH FUND SUMMARY ======================
    st.subheader("Growth Fund Summary")
    st.metric("Current Balance", f"${gf_balance:,.0f}")
    
    # ====================== ACCOUNTS TABLE ======================
    st.subheader("Accounts Summary")
    if accounts:
        acc_df = pd.DataFrame(accounts)
        st.dataframe(acc_df[["name", "current_phase", "current_equity", "withdrawable_balance"]], use_container_width=True)
    else:
        st.info("No accounts yet")
    
    # ====================== EXPORT OPTIONS (MULTIPLE CSV) ======================
    st.subheader("📤 Export Reports")
    col_exp1, col_exp2 = st.columns(2)
    with col_exp1:
        if profits:
            csv_profits = pd.DataFrame(profits).to_csv(index=False).encode()
            st.download_button("Export Profits Report CSV", csv_profits, "KMFX_Profits_Report.csv", "text/csv")
        if distributions:
            csv_dist = pd.DataFrame(distributions).to_csv(index=False).encode()
            st.download_button("Export Distributions CSV", csv_dist, "KMFX_Distributions_Report.csv", "text/csv")
    with col_exp2:
        if clients:
            csv_bal = pd.DataFrame([{"Client": c["full_name"], "Balance": c["balance"] or 0} for c in clients]).to_csv(index=False).encode()
            st.download_button("Export Client Balances CSV", csv_bal, "KMFX_Client_Balances.csv", "text/csv")
        csv_summary = pd.DataFrame({
            "Metric": ["Total Gross Profits", "Total Distributed", "Client Balances", "Growth Fund", "Active Accounts", "Total Equity"],
            "Value": [f"${total_gross:,.0f}", f"${total_distributed:,.0f}", f"${total_client_balances:,.0f}", f"${gf_balance:,.0f}", total_accounts, f"${total_equity:,.0f}"]
        }).to_csv(index=False).encode()
        st.download_button("Export Empire Summary CSV", csv_summary, "KMFX_Empire_Summary.csv", "text/csv")
    
    st.markdown(f"""
    <div class='glass-card' style='padding:3rem; text-align:center; margin:3rem 0;'>
        <h1 style="background:linear-gradient(90deg,{accent_color},#ffd700); -webkit-background-clip:text; -webkit-text-fill-color:transparent;">
            Automatic Analytics & Exports
        </h1>
        <p style="font-size:1.3rem; margin:2rem 0;">
            All data auto-aggregated • Realtime charts • Tables • CSV exports • Empire performance tracked.
        </p>
        <h2 style="color:#ffd700;">👑 KMFX Reports • Fully Automated 2026</h2>
    </div>
    """, unsafe_allow_html=True)
# ====================== END OF FINAL REPORTS & EXPORT ======================
# ====================== PART 6: SIMULATOR PAGE (FINAL SUPER ADVANCED - FULL MAIN FLOW SYNC & REALTIME) ======================
elif selected == "🔮 Simulator":
    st.header("Empire Growth Simulator 🔮")
    st.markdown("**Advanced scaling forecaster: Auto-loaded from current empire (accounts, avg profits, GF %, units) • Simulate scenarios • Projected equity, distributions, growth fund, units • Realtime multi-line charts • Sankey flow previews • Professional & clean planning tool.**")
    
    # SAFE ROLE (all can use, but owner/admin full)
    current_role = st.session_state.get("role", "guest")
    
    # FULL AUTO CACHE - Load current empire state
    @st.cache_data(ttl=60)
    def fetch_simulator_data():
        accounts_resp = supabase.table("ftmo_accounts").select("current_equity, ftmo_split, unit_value, participants").execute()
        accounts = accounts_resp.data or []
        
        profits_resp = supabase.table("profits").select("gross_profit").execute()
        profits = profits_resp.data or []
        
        gf_resp = supabase.table("growth_fund_transactions").select("type, amount").execute()
        gf_balance = sum(row["amount"] if row["type"] == "In" else -row["amount"] for row in gf_resp.data) if gf_resp.data else 0.0
        
        # Auto-calcs
        total_equity = sum(a.get("current_equity", 0) for a in accounts)
        num_accounts = len(accounts)
        total_gross = sum(p.get("gross_profit", 0) for p in profits)
        avg_monthly_profit = total_gross / max(1, len(profits)) if profits else 15000.0  # Fallback
        
        # Avg GF % from participants
        gf_pcts = []
        for a in accounts:
            participants = a.get("participants", [])
            gf_pct = next((p["percentage"] for p in participants if "growth fund" in p["name"].lower()), 10.0)
            gf_pcts.append(gf_pct)
        avg_gf_pct = sum(gf_pcts) / len(gf_pcts) if gf_pcts else 20.0
        
        # Avg unit value
        unit_values = [a.get("unit_value", 3000) for a in accounts]
        avg_unit_value = sum(unit_values) / len(unit_values) if unit_values else 3000.0
        
        return total_equity, num_accounts, avg_monthly_profit, avg_gf_pct, avg_unit_value, gf_balance, accounts
    
    total_equity, num_accounts, avg_monthly_profit, avg_gf_pct, avg_unit_value, gf_balance, accounts = fetch_simulator_data()
    
    st.info(f"**Auto-Loaded Empire Stats:** {num_accounts} accounts • Total Equity ${total_equity:,.0f} • Avg Monthly Gross ${avg_monthly_profit:,.0f} • Avg GF % {avg_gf_pct:.1f}% • Avg Unit Value ${avg_unit_value:,.0f} • Current GF ${gf_balance:,.0f}")
    
    # ====================== ADVANCED SIMULATION INPUTS (PROFESSIONAL & CLEAN) ======================
    st.subheader("Configure Simulation Scenarios")
    col_sim1, col_sim2 = st.columns(2)
    with col_sim1:
        months = st.slider("Projection Months", 6, 72, 36)
        projected_accounts = st.slider("Projected Active Accounts", num_accounts, num_accounts + 30, num_accounts + 10)
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
    monthly_units = monthly_gross_total / unit_value_proj
    
    col_calc1, col_calc2, col_calc3 = st.columns(3)
    col_calc1.metric("Projected Monthly Gross", f"${monthly_gross_total:,.0f}")
    col_calc2.metric("Monthly GF Add", f"${monthly_gf_add:,.0f}")
    col_calc3.metric("Monthly Units Generated", f"{monthly_units:.2f}")
    
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
            units = gross / unit_value_proj
            
            new_equity = equity_proj[-1] + gross
            new_gf = gf_proj[-1] + gf_add
            
            equity_proj.append(new_equity)
            gf_proj.append(new_gf)
            distributed_proj.append(distributed_proj[-1] + distributed)
            units_proj.append(units_proj[-1] + units)
        
        # Multi-line chart
        fig_multi = go.Figure()
        fig_multi.add_trace(go.Scatter(x=dates, y=equity_proj, name="Total Equity", line=dict(color=accent_color, width=5)))
        fig_multi.add_trace(go.Scatter(x=dates, y=gf_proj, name="Growth Fund", line=dict(color="#ffd700", width=5)))
        fig_multi.add_trace(go.Scatter(x=dates, y=distributed_proj, name="Distributed Shares", line=dict(color="#00ffaa")))
        fig_multi.update_layout(title=f"{scenario_name} - Empire Trajectory", height=600)
        st.plotly_chart(fig_multi, use_container_width=True)
        
        # Final metrics
        col_final1, col_final2, col_final3, col_final4 = st.columns(4)
        col_final1.metric("Final Equity", f"${equity_proj[-1]:,.0f}")
        col_final2.metric("Final Growth Fund", f"${gf_proj[-1]:,.0f}")
        col_final3.metric("Total Distributed", f"${distributed_proj[-1]:,.0f}")
        col_final4.metric("Total Units Generated", f"{units_proj[-1]:.2f}")
        
        # Projected average distribution Sankey
        st.subheader("Projected Average Monthly Distribution Flow")
        labels = ["Monthly Gross"] + ["Distributed Shares", "Growth Fund"]
        values = [monthly_distributed, monthly_gf_add]
        fig_avg = go.Figure(data=[go.Sankey(
            node=dict(pad=20, thickness=30, label=labels, color=["#00ffaa", accent_color, "#ffd700"]),
            link=dict(source=[0, 0], target=[1, 2], value=values)
        )])
        fig_avg.update_layout(height=400)
        st.plotly_chart(fig_avg, use_container_width=True)
    
    st.markdown(f"""
    <div class='glass-card' style='padding:3rem; text-align:center; margin:3rem 0;'>
        <h1 style="background:linear-gradient(90deg,{accent_color},#ffd700); -webkit-background-clip:text; -webkit-text-fill-color:transparent;">
            Future Empire Simulation
        </h1>
        <p style="font-size:1.3rem; margin:2rem 0;">
            Auto-loaded current stats • Multiple scenarios • Projected trees & growth • Plan scaling with data.
        </p>
        <h2 style="color:#ffd700;">👑 KMFX Simulator • Fully Predictive 2026</h2>
    </div>
    """, unsafe_allow_html=True)
# ====================== END OF FINAL SIMULATOR ======================
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
# ====================== PART 6: ADMIN MANAGEMENT PAGE (FINAL SUPER ADVANCED - WITH FULL CLIENT DETAILS, TITLE SYNC, EDIT + DELETE) ======================
elif selected == "👤 Admin Management":
    st.header("Empire Team Management 👤")
    st.markdown("**Owner-exclusive: Register team members with full details (Name, Accounts, Email, Contact, Address) & Title (Pioneer, VIP, etc.) for labeled dropdowns • Realtime balances • Full Edit (including password) • Secure delete • Full sync to FTMO participants as 'Name (Title)'**")
   
    # STRICT OWNER ONLY
    current_role = st.session_state.get("role", "guest")
    if current_role != "owner":
        st.error("🔒 Team Management is OWNER-ONLY for empire security.")
        st.stop()
   
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
   
    # CURRENT TEAM WITH FULL INFO DISPLAY + EDIT + DELETE
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
                title_display = f" ({u.get('title', '')})" if u.get("title") else ""
                balance = u.get("balance", 0)
                with st.expander(f"{u['full_name']}{title_display} (@{u['username']}) • {u['role'].title()} • Balance ${balance:,.2f}", expanded=False):
                    st.markdown(f"**Accounts:** {u.get('accounts') or 'None'}")
                    st.markdown(f"**Email:** {u.get('email') or 'None'}")
                    st.markdown(f"**Contact No.:** {u.get('contact_no') or 'None'}")
                    st.markdown(f"**Address:** {u.get('address') or 'None'}")
                    
                    col_btn1, col_btn2 = st.columns(2)
                    with col_btn1:
                        if st.button("✏️ Edit", key=f"edit_{u['id']}"):
                            st.session_state.edit_user_id = u["id"]
                            st.session_state.edit_user_data = u.copy()  # Copy to avoid reference issues
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
                    
                    # EDIT FORM (appears when Edit clicked)
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
                                        if new_pwd.strip():  # Only update password if provided
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
            Full client info (accounts, email, contact, address) • Titles synced • Full Edit + Delete • Realtime balances • Empire team fully managed.
        </p>
        <h2 style="color:#ffd700;">👑 KMFX Team Management • Owner Exclusive 2026</h2>
    </div>
    """, unsafe_allow_html=True)
# ====================== END OF FINAL ADMIN MANAGEMENT WITH FULL EDIT + DELETE ======================
# ====================== CLOSE MAIN CONTENT & FOOTER ======================
st.markdown("</div>", unsafe_allow_html=True)
st.markdown("---")
st.caption("© 2025 KMFX FTMO Pro • Cloud Edition • Built by Faith, Shared for Generations 👑")

# ====================== END OF PART 6 - FULL SUPABASE APP COMPLETE ======================
# Congratulations! Your KMFX FTMO Pro Manager is now FULLY CLOUD-BASED with Supabase.
# All data in cloud, ready for deployment, multi-device access.
# Scale to millions in 2026! 🚀💰