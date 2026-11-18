"""
Streamlit QR Code Studio - Precision Indigo SaaS Platform
Upgraded to match Stitch UI Specification (Precision Indigo Design System).
Features:
- Enterprise SaaS Header with Workspace status and Navigation (Dashboard, Create QR, My QRs, Analytics, Settings)
- Dashboard View: Hero Card, Quick Stats 2x2 grid, Quick Utilities, Recent QR Codes activity feed
- Create QR Studio: 3-Step Stepper (Type -> Content -> Design & Export)
- QR Type Switcher: Dynamic QR (Recommended) vs Static QR
- 10 Payload Formats with validation, format helpers, and SSL / format verification
- Live QR Stage: High-contrast Viewport, Zoom, Invert, Simulate Scan micro-interaction, WCAG Contrast Check
- Precision Indigo Styling: Dot Styles (Square, Rounded, Circle), Color Presets & Custom Hex, Logo Uploader & Presets
- ECC Redundancy (L, M, Q, H) and Resolution scaling (512px to 4096px)
- Multi-format exports: High-Res PNG, Vector SVG, Print-Ready PDF, JPG, and Copy Image to Clipboard
- Success Flow: Confetti animation, permanent dynamic short-link, direct download options
- My QR Codes Repository & Telemetry Analytics dashboard
"""

import io
import os
import sys
import re
import base64
from datetime import datetime

# Ensure current directory is in sys.path for local module resolution
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

import streamlit as st
import streamlit.components.v1 as components
from PIL import Image

# Payload Builders (10 formats)
from qr_builders import (
    build_url,
    build_text,
    build_wifi,
    build_vcard,
    build_email,
    build_phone,
    build_sms,
    build_whatsapp,
    build_upi,
    build_image_data_uri,
)

# Phase 1 Modular Architecture
from utils.validators import validate_logo, contrast_ratio, hex_to_rgb
from utils.qr_builder import build_qr
from utils.exporter import to_png, to_jpg, to_pdf, to_svg


# =========================================================================
# PAGE CONFIGURATION
# =========================================================================
st.set_page_config(
    page_title="QR Studio | Precision Indigo SaaS",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Custom High-End Styling: Precision Indigo Design System
st.markdown(
    """
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@500;600;700;800&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200" />

    <style>
    /* Global Base */
    html, body, [class*="css"], .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        background-color: #FAF8FF !important;
        color: #131B2E !important;
    }

    h1, h2, h3, h4, h5, h6, .brand-title, .headline {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        color: #131B2E !important;
    }

    /* Top Navigation Header */
    .top-navbar {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(12px);
        border-bottom: 1px solid #E2E8F0;
        padding: 0.75rem 1.5rem;
        margin: -1rem -1rem 1.25rem -1rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        border-radius: 0 0 16px 16px;
        box-shadow: 0 1px 3px 0 rgba(15, 23, 42, 0.04);
    }

    .brand-group {
        display: flex;
        align-items: center;
        gap: 12px;
    }

    .brand-logo-icon {
        width: 38px;
        height: 38px;
        background: linear-gradient(135deg, #3525CD 0%, #4F46E5 100%);
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #FFFFFF;
        box-shadow: 0 4px 12px rgba(79, 70, 229, 0.25);
    }

    .brand-name {
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 1.25rem;
        font-weight: 700;
        letter-spacing: -0.02em;
        color: #131B2E;
        line-height: 1;
    }

    .workspace-pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: #F2F3FF;
        border: 1px solid #E2E7FF;
        color: #3525CD;
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.05em;
        text-transform: uppercase;
    }

    .status-dot-pulse {
        width: 7px;
        height: 7px;
        background-color: #16A34A;
        border-radius: 50%;
        display: inline-block;
        box-shadow: 0 0 0 0 rgba(22, 163, 74, 0.7);
        animation: pulse-green 2s infinite;
    }

    @keyframes pulse-green {
        0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(22, 163, 74, 0.7); }
        70% { transform: scale(1); box-shadow: 0 0 0 6px rgba(22, 163, 74, 0); }
        100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(22, 163, 74, 0); }
    }

    /* Hero Banner Card */
    .hero-banner {
        position: relative;
        overflow: hidden;
        border-radius: 16px;
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        padding: 1.5rem 1.75rem;
        margin-bottom: 1.25rem;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04);
    }

    .hero-glow {
        position: absolute;
        top: -60px;
        right: -60px;
        width: 220px;
        height: 220px;
        background: radial-gradient(circle, rgba(79, 70, 229, 0.15) 0%, rgba(99, 102, 241, 0.08) 50%, transparent 70%);
        border-radius: 50%;
        pointer-events: none;
        filter: blur(20px);
    }

    .hero-title {
        font-size: 1.65rem;
        font-weight: 700;
        color: #131B2E;
        letter-spacing: -0.02em;
        margin-bottom: 0.35rem;
    }

    .hero-subtitle {
        color: #64748B;
        font-size: 0.92rem;
        max-width: 600px;
        line-height: 1.5;
        margin-bottom: 0.85rem;
    }

    /* Metric Stat Cards */
    .stat-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 14px;
        padding: 1rem 1.15rem;
        box-shadow: 0 1px 2px rgba(15, 23, 42, 0.03);
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }

    .stat-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(15, 23, 42, 0.06);
    }

    .stat-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 0.5rem;
    }

    .stat-label {
        font-size: 0.75rem;
        font-weight: 600;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    .stat-icon-box {
        width: 32px;
        height: 32px;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.1rem;
    }

    .stat-val {
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 1.65rem;
        font-weight: 700;
        color: #131B2E;
        line-height: 1.2;
    }

    .stat-trend {
        font-size: 0.75rem;
        font-weight: 600;
        display: inline-flex;
        align-items: center;
        gap: 3px;
        margin-top: 4px;
    }

    .trend-up { color: #16A34A; }
    .trend-neutral { color: #64748B; }
    .trend-indigo { color: #4F46E5; }

    /* Stepper Header */
    .stepper-container {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 14px;
        padding: 0.85rem 1.25rem;
        margin-bottom: 1.25rem;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.03);
        display: flex;
        align-items: center;
        justify-content: space-between;
    }

    .step-item {
        display: flex;
        align-items: center;
        gap: 10px;
    }

    .step-num {
        width: 28px;
        height: 28px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.8rem;
        font-weight: 700;
    }

    .step-num.active {
        background: #4F46E5;
        color: #FFFFFF;
        box-shadow: 0 0 0 4px rgba(79, 70, 229, 0.15);
    }

    .step-num.completed {
        background: #16A34A;
        color: #FFFFFF;
    }

    .step-num.inactive {
        background: #EAEDFF;
        color: #64748B;
    }

    .step-text-title {
        font-size: 0.88rem;
        font-weight: 600;
        color: #131B2E;
        line-height: 1.1;
    }

    .step-text-sub {
        font-size: 0.72rem;
        color: #64748B;
    }

    .stepper-line {
        flex: 1;
        height: 2px;
        background: #E2E8F0;
        margin: 0 1rem;
        border-radius: 9999px;
    }

    /* QR Type Select Cards */
    .type-card {
        border: 1.5px solid #E2E8F0;
        background: #FFFFFF;
        border-radius: 14px;
        padding: 1rem 1.2rem;
        cursor: pointer;
        transition: all 0.2s ease;
        position: relative;
    }

    .type-card.selected {
        border-color: #4F46E5;
        background: #F8FAFF;
        box-shadow: 0 4px 14px rgba(79, 70, 229, 0.1);
    }

    .badge-recommended {
        background: #4F46E5;
        color: #FFFFFF;
        font-size: 0.68rem;
        font-weight: 700;
        padding: 2px 7px;
        border-radius: 9999px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    /* Live QR Stage Viewport */
    .qr-stage-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 18px;
        padding: 1.4rem;
        text-align: center;
        box-shadow: 0 4px 18px rgba(15, 23, 42, 0.05);
        position: sticky;
        top: 1rem;
    }

    .stage-header-bar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 8px;
        margin-bottom: 1rem;
    }

    .dynamic-active-pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(22, 163, 74, 0.1);
        color: #16A34A;
        border: 1px solid rgba(22, 163, 74, 0.25);
        padding: 4px 9px;
        border-radius: 9999px;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.05em;
        text-transform: uppercase;
    }

    .target-url-badge {
        display: inline-flex;
        align-items: center;
        gap: 5px;
        background: #F2F3FF;
        color: #464555;
        padding: 3px 10px;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-family: monospace;
        max-width: 220px;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }

    .qr-viewport-frame {
        background: #FFFFFF;
        padding: 16px;
        border-radius: 16px;
        display: inline-block;
        border: 1px solid #E2E8F0;
        box-shadow: 0 4px 16px rgba(15, 23, 42, 0.04);
        margin-bottom: 0.85rem;
        transition: transform 0.25s ease;
    }

    .qr-viewport-frame.zoomed {
        transform: scale(1.15);
    }

    .qr-viewport-frame.inverted {
        background: #131B2E;
    }

    .floating-pill-toolbar {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: #F2F3FF;
        border: 1px solid #E2E7FF;
        border-radius: 9999px;
        padding: 4px 12px;
        margin-top: 0.5rem;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04);
    }

    .toolbar-tool {
        font-size: 0.75rem;
        font-weight: 600;
        color: #464555;
        display: inline-flex;
        align-items: center;
        gap: 4px;
        cursor: pointer;
        background: transparent;
        border: none;
        padding: 3px 6px;
        border-radius: 6px;
    }

    .toolbar-tool:hover {
        color: #4F46E5;
        background: #FFFFFF;
    }

    /* Scan Simulation Banner */
    .scan-simulator-banner {
        background: #DCFCE7;
        border: 1px solid #BBF7D0;
        color: #16A34A;
        border-radius: 10px;
        padding: 8px 14px;
        margin-top: 0.75rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        font-size: 0.82rem;
        font-weight: 600;
        animation: fadeIn 0.3s ease;
    }

    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(-4px); }
        to { opacity: 1; transform: translateY(0); }
    }

    /* WCAG Contrast Badge */
    .contrast-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 5px 12px;
        border-radius: 8px;
        font-size: 0.82rem;
        font-weight: 600;
        margin: 0.5rem 0;
    }

    .contrast-pass {
        background: #DCFCE7;
        border: 1px solid #BBF7D0;
        color: #16A34A;
    }

    .contrast-fail {
        background: #FEF3C7;
        border: 1px solid #FDE68A;
        color: #B45309;
    }

    /* Field Errors */
    .field-error {
        background: #FEE2E2;
        border: 1px solid #FECACA;
        color: #DC2626;
        font-size: 0.82rem;
        padding: 6px 12px;
        border-radius: 8px;
        margin-top: -0.25rem;
        margin-bottom: 0.65rem;
        font-weight: 500;
        display: flex;
        align-items: center;
        gap: 6px;
    }

    /* Form Fields & Controls */
    div[data-baseweb="input"] > div,
    div[data-baseweb="select"] > div,
    div[data-baseweb="textarea"] > div,
    input, textarea {
        background-color: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        color: #131B2E !important;
        border-radius: 8px !important;
    }

    div[data-baseweb="input"]:focus-within > div,
    div[data-baseweb="textarea"]:focus-within > div,
    div[data-baseweb="select"]:focus-within > div {
        border-color: #4F46E5 !important;
        box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.12) !important;
    }

    label p {
        color: #131B2E !important;
        font-weight: 600 !important;
        font-size: 0.88rem !important;
    }

    /* Buttons */
    button[kind="primary"] {
        background: #4F46E5 !important;
        color: #FFFFFF !important;
        border: 1px solid transparent !important;
        border-radius: 8px !important;
        padding: 0.65rem 1.25rem !important;
        font-weight: 600 !important;
        letter-spacing: 0.01em !important;
        box-shadow: 0 2px 8px rgba(79, 70, 229, 0.25) !important;
        transition: all 0.18s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }

    button[kind="primary"]:hover {
        background: #4338CA !important;
        box-shadow: 0 4px 14px rgba(79, 70, 229, 0.35) !important;
        transform: translateY(-1px) !important;
    }

    button[kind="secondary"] {
        background: #FFFFFF !important;
        color: #131B2E !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        box-shadow: 0 1px 2px rgba(15, 23, 42, 0.03) !important;
        transition: all 0.15s ease !important;
    }

    button[kind="secondary"]:hover {
        background: #F8FAFC !important;
        border-color: #CBD5E1 !important;
        color: #4F46E5 !important;
    }

    /* Expanders / Accordion Styling */
    .streamlit-expanderHeader {
        background-color: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 10px !important;
        color: #131B2E !important;
        font-weight: 600 !important;
        font-size: 0.92rem !important;
        box-shadow: 0 1px 2px rgba(15, 23, 42, 0.02) !important;
    }

    div[data-testid="stExpanderDetails"] {
        background-color: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-top: none !important;
        border-radius: 0 0 10px 10px !important;
        padding: 1.1rem !important;
    }

    /* Recent QR Code Feed Card */
    .recent-qr-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 0.9rem 1.1rem;
        margin-bottom: 0.75rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        box-shadow: 0 1px 2px rgba(15, 23, 42, 0.02);
        transition: all 0.15s ease;
    }

    .recent-qr-card:hover {
        border-color: #CBD5E1;
        box-shadow: 0 3px 10px rgba(15, 23, 42, 0.05);
    }

    /* Success Card & Confetti */
    .success-hero-box {
        background: linear-gradient(180deg, #FFFFFF 0%, #FAF8FF 100%);
        border: 1.5px solid #BBF7D0;
        border-radius: 18px;
        padding: 1.75rem;
        text-align: center;
        box-shadow: 0 6px 24px rgba(22, 163, 74, 0.1);
        margin-bottom: 1.5rem;
    }

    .shortlink-pill {
        background: #F2F3FF;
        border: 1px solid #E2E7FF;
        padding: 6px 14px;
        border-radius: 8px;
        font-family: monospace;
        font-size: 1.05rem;
        font-weight: 700;
        color: #4F46E5;
        display: inline-block;
        margin: 0.5rem 0;
    }

    /* Tabs Bar */
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        border-bottom: 1px solid #E2E8F0;
        padding-bottom: 4px;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 8px 16px;
        font-weight: 600;
        font-size: 0.9rem;
        color: #64748B;
        background: transparent;
        border: none;
    }

    .stTabs [aria-selected="true"] {
        background: #F2F3FF !important;
        color: #4F46E5 !important;
    }

    hr {
        border-color: #E2E8F0 !important;
        margin: 1.15rem 0 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================================
# SESSION STATE INITIALIZATION
# =========================================================================
QR_TYPES = [
    "🌐 Website URL",
    "📝 Plain Text",
    "📶 Wi-Fi Network",
    "👤 vCard Profile",
    "💬 WhatsApp Chat",
    "✉️ Email Message",
    "📞 Phone Dial",
    "💬 SMS Message",
    "💳 UPI Payment",
    "🖼️ Image (Upload)",
]

DEFAULT_STATES = {
    "nav_view": "Dashboard",
    "create_step": 1,
    "qr_mode": "Dynamic",
    "campaign_name": "Summer Promo Menu",
    "qr_type": QR_TYPES[0],
    # Form fields
    "url_input": "https://qrstudio.app/promo/summer25",
    "text_input": "",
    "img_encoding_mode": "Direct Embedded Data URI (Self-Contained)",
    "img_max_dimension": 48,
    "img_quality": 65,
    "img_hosted_url": "",
    "wifi_ssid": "StoreGuest_WiFi",
    "wifi_password": "GuestSecretPass",
    "wifi_security": "WPA/WPA2",
    "wifi_show_password": False,
    "wifi_hidden": False,
    "vcard_first_name": "Ravi",
    "vcard_last_name": "Kumar",
    "vcard_phone": "+919876543210",
    "vcard_email": "ravi@example.com",
    "vcard_company": "Acme Technologies",
    "vcard_job_title": "Lead Architect",
    "vcard_website": "https://portfolio.io",
    "vcard_address": "128 Tech Park, Bengaluru",
    "email_to": "support@company.com",
    "email_subject": "Product Inquiry",
    "email_body": "Hello, I would like to inquire about your product.",
    "phone_cc": "+91",
    "phone_number": "9876543210",
    "sms_number": "9876543210",
    "sms_message": "Hello, confirming our meeting at 4 PM.",
    "wa_cc": "+91",
    "wa_phone": "9876543210",
    "wa_message": "Hello, I would like to inquire about...",
    "upi_id": "merchant@okhdfcbank",
    "upi_name": "Acme Official Store",
    "upi_amount": "750.00",
    "upi_note": "Invoice #5021",
    "password_protect": False,
    "password_value": "",
    "expiration_date": False,
    # Feature 1: Logo State
    "logo_bytes": None,
    "logo_filename": "",
    # Feature 2: Styling State
    "qr_style": "Rounded",
    "qr_fg_color": "#4F46E5",
    "qr_bg_color": "#FFFFFF",
    "qr_box_size": 10,
    "ecc_level": "H",
    "allow_low_contrast": False,
    # Micro-interaction Toggles
    "stage_zoom": False,
    "stage_invert": False,
    "simulate_scan_active": False,
    "show_success_card": False,
    # Mock Repository of Recent QRs
    "recent_qrs": [
        {
            "id": "QR-94821",
            "name": "Summer Campaign 2025",
            "type": "Dynamic",
            "date": "May 18, 2025",
            "scans": "3,420",
            "status": "Active",
            "url": "https://qrstudio.app/promo/summer25",
        },
        {
            "id": "QR-94812",
            "name": "Store Wi-Fi Guest",
            "type": "Static",
            "date": "May 12, 2025",
            "scans": "Unmetered",
            "status": "Active",
            "url": "WIFI:S:StoreGuest;P:GuestPass123;;",
        },
        {
            "id": "QR-94755",
            "name": "Menu PDF - Downtown",
            "type": "Dynamic",
            "date": "Apr 29, 2025",
            "scans": "8,912",
            "status": "Active",
            "url": "https://qrstudio.app/menu/downtown",
        },
        {
            "id": "QR-94610",
            "name": "Product Launch Linktree",
            "type": "Dynamic",
            "date": "Apr 10, 2025",
            "scans": "1,958",
            "status": "Paused",
            "url": "https://qrstudio.app/launch",
        },
    ],
}

for k, v in DEFAULT_STATES.items():
    if k not in st.session_state:
        st.session_state[k] = v

EMAIL_REGEX = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
UPI_REGEX = r"^[\w.-]+@[\w.-]+$"

def render_field_error(msg: str):
    st.markdown(f'<div class="field-error">⚠️ {msg}</div>', unsafe_allow_html=True)


def render_clipboard_component(png_bytes: bytes):
    """Render modern copy-to-clipboard button using browser Clipboard API."""
    b64_png = base64.b64encode(png_bytes).decode("utf-8")
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8">
      <style>
        body {{
          margin: 0;
          padding: 0;
          background: transparent;
          font-family: 'Inter', -apple-system, sans-serif;
        }}
        .clip-btn {{
          width: 100%;
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 8px;
          background: #FFFFFF;
          color: #131B2E;
          border: 1px solid #E2E8F0;
          border-radius: 8px;
          padding: 0.65rem 1rem;
          font-size: 0.88rem;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.15s ease;
          box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04);
        }}
        .clip-btn:hover {{
          background: #F8FAFC;
          border-color: #4F46E5;
          color: #4F46E5;
        }}
        .clip-btn.success {{
          background: #DCFCE7;
          border-color: #BBF7D0;
          color: #16A34A;
        }}
        .fallback-note {{
          display: none;
          margin-top: 6px;
          font-size: 0.78rem;
          color: #DC2626;
          text-align: center;
        }}
      </style>
    </head>
    <body>
      <button id="clip-btn" class="clip-btn" onclick="copyImage()">
        <span>📋</span> Copy Image to Clipboard
      </button>
      <div id="fallback" class="fallback-note">
        ⚠️ Clipboard blocked. Right-click QR code above and choose "Copy Image".
      </div>
      <script>
        async function copyImage() {{
          const btn = document.getElementById('clip-btn');
          const fallback = document.getElementById('fallback');
          try {{
            fallback.style.display = 'none';
            const dataUrl = "data:image/png;base64,{b64_png}";
            const res = await fetch(dataUrl);
            const blob = await res.blob();
            const item = new ClipboardItem({{ 'image/png': blob }});
            await navigator.clipboard.write([item]);
            btn.innerHTML = "<span>✅</span> Copied Image to Clipboard!";
            btn.classList.add('success');
            setTimeout(() => {{
              btn.innerHTML = "<span>📋</span> Copy Image to Clipboard";
              btn.classList.remove('success');
            }}, 2500);
          }} catch (err) {{
            fallback.style.display = 'block';
          }}
        }}
      </script>
    </body>
    </html>
    """
    components.html(html_code, height=52)


# =========================================================================
# TOP NAVIGATION BAR (Enterprise SaaS Header)
# =========================================================================
c_nav_left, c_nav_right = st.columns([1.5, 2.5])

with c_nav_left:
    st.markdown(
        """
        <div class="brand-group">
            <div class="brand-logo-icon">
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                    <rect x="3" y="3" width="7" height="7"></rect>
                    <rect x="14" y="3" width="7" height="7"></rect>
                    <rect x="14" y="14" width="7" height="7"></rect>
                    <rect x="3" y="14" width="7" height="7"></rect>
                </svg>
            </div>
            <div>
                <div class="brand-name">QR Studio</div>
                <div style="font-size: 0.72rem; color: #64748B; font-weight: 500;">Precision Indigo Platform</div>
            </div>
            <div class="workspace-pill">
                <span class="status-dot-pulse"></span>
                <span>Pro Workspace</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with c_nav_right:
    nav_tabs = ["📊 Dashboard", "⚡ Create QR Code", "📁 My QR Codes", "📈 Analytics", "⚙️ Settings"]
    current_idx = 0
    if st.session_state["nav_view"] == "Create QR Code":
        current_idx = 1
    elif st.session_state["nav_view"] == "My QR Codes":
        current_idx = 2
    elif st.session_state["nav_view"] == "Analytics":
        current_idx = 3
    elif st.session_state["nav_view"] == "Settings":
        current_idx = 4

    selected_nav = st.radio(
        "Navigation",
        options=nav_tabs,
        index=current_idx,
        horizontal=True,
        label_visibility="collapsed",
    )
    # Map back to view
    clean_view = selected_nav.split()[-1]
    if "Dashboard" in selected_nav:
        st.session_state["nav_view"] = "Dashboard"
    elif "Create" in selected_nav:
        st.session_state["nav_view"] = "Create QR Code"
    elif "My" in selected_nav:
        st.session_state["nav_view"] = "My QR Codes"
    elif "Analytics" in selected_nav:
        st.session_state["nav_view"] = "Analytics"
    elif "Settings" in selected_nav:
        st.session_state["nav_view"] = "Settings"

st.markdown("<hr style='margin-top: 0.5rem;'>", unsafe_allow_html=True)


# =========================================================================
# VIEW 1: DASHBOARD (Stitch dashboard/code.html)
# =========================================================================
if st.session_state["nav_view"] == "Dashboard":
    # 1. Welcome Hero Banner
    c_hero_txt, c_hero_cta = st.columns([2.8, 1.2])
    with c_hero_txt:
        st.markdown(
            """
            <div class="hero-banner">
                <div class="hero-glow"></div>
                <div style="display: inline-flex; align-items: center; gap: 6px; background: #F2F3FF; padding: 3px 10px; border-radius: 9999px; font-size: 0.72rem; font-weight: 700; color: #4F46E5; text-transform: uppercase; margin-bottom: 0.5rem;">
                    <span class="status-dot-pulse"></span>
                    <span>Live Telemetry Active</span>
                </div>
                <div class="hero-title">Welcome to QR Studio</div>
                <div class="hero-subtitle">
                    Create, customize, and deploy high-fidelity QR codes with instant vector exports, live scan telemetry, and dynamic destination routing.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c_hero_cta:
        st.write("")
        st.write("")
        if st.button("➕ Create New QR Code", type="primary", use_container_width=True):
            st.session_state["nav_view"] = "Create QR Code"
            st.session_state["create_step"] = 1
            st.rerun()
        if st.button("🔍 Scan & Test Simulator", use_container_width=True):
            st.session_state["nav_view"] = "Create QR Code"
            st.session_state["simulate_scan_active"] = True
            st.rerun()

    # 2. Quick Stats Grid (4 columns)
    st.markdown("<div style='font-size: 0.78rem; font-weight: 700; color: #64748B; text-transform: uppercase; letter-spacing: 0.05em; margin: 0.5rem 0;'>Workspace Telemetry</div>", unsafe_allow_html=True)
    sc1, sc2, sc3, sc4 = st.columns(4)
    with sc1:
        st.markdown(
            """
            <div class="stat-card">
                <div class="stat-header">
                    <span class="stat-label">Total QRs</span>
                    <div class="stat-icon-box" style="background: #F2F3FF; color: #4F46E5;">📦</div>
                </div>
                <div class="stat-val">48</div>
                <div class="stat-trend trend-up">▲ +12% this month</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with sc2:
        st.markdown(
            """
            <div class="stat-card">
                <div class="stat-header">
                    <span class="stat-label">Static QRs</span>
                    <div class="stat-icon-box" style="background: #F1F5F9; color: #475569;">🔒</div>
                </div>
                <div class="stat-val">18</div>
                <div class="stat-trend trend-neutral">Permanent Encodings</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with sc3:
        st.markdown(
            """
            <div class="stat-card">
                <div class="stat-header">
                    <span class="stat-label">Dynamic QRs</span>
                    <div class="stat-icon-box" style="background: #E2DFFF; color: #3525CD;">⚡</div>
                </div>
                <div class="stat-val">30</div>
                <div class="stat-trend trend-indigo">● Live Editable Routes</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with sc4:
        st.markdown(
            """
            <div class="stat-card">
                <div class="stat-header">
                    <span class="stat-label">Total Scans</span>
                    <div class="stat-icon-box" style="background: #DCFCE7; color: #16A34A;">📈</div>
                </div>
                <div class="stat-val">14,290</div>
                <div class="stat-trend trend-up">▲ +28.4% growth</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.write("")
    # 3. Quick Utilities Row
    st.markdown("<div style='font-size: 0.78rem; font-weight: 700; color: #64748B; text-transform: uppercase; letter-spacing: 0.05em; margin: 0.75rem 0 0.35rem 0;'>Quick Utilities</div>", unsafe_allow_html=True)
    u1, u2, u3 = st.columns(3)
    with u1:
        if st.button("🎯 Scan & Test Integrity", use_container_width=True, help="Validate scan speed and camera decoding"):
            st.session_state["nav_view"] = "Create QR Code"
            st.session_state["simulate_scan_active"] = True
            st.rerun()
    with u2:
        if st.button("📊 View Full Analytics", use_container_width=True, help="Inspect scan telemetry and devices"):
            st.session_state["nav_view"] = "Analytics"
            st.rerun()
    with u3:
        if st.button("🔑 Manage Workspace API Keys", use_container_width=True, help="Access Developer API tokens"):
            st.session_state["nav_view"] = "Settings"
            st.rerun()

    # 4. Recent QR Codes Feed
    st.write("")
    c_rec_h, c_rec_act = st.columns([3, 1])
    with c_rec_h:
        st.markdown("<div style='font-size: 1.15rem; font-weight: 700; color: #131B2E; display: flex; align-items: center; gap: 8px;'>Recent QR Codes <span style='background: #EAEDFF; color: #3525CD; font-size: 0.75rem; padding: 2px 8px; border-radius: 9999px;'>48 Total</span></div>", unsafe_allow_html=True)
    with c_rec_act:
        if st.button("View All QRs →", use_container_width=True):
            st.session_state["nav_view"] = "My QR Codes"
            st.rerun()

    for item in st.session_state["recent_qrs"]:
        st.markdown(
            f"""
            <div class="recent-qr-card">
                <div style="display: flex; align-items: center; gap: 14px;">
                    <div style="width: 42px; height: 42px; background: #F2F3FF; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 1.3rem;">
                        ⚡
                    </div>
                    <div>
                        <div style="font-weight: 600; font-size: 0.95rem; color: #131B2E;">{item['name']}</div>
                        <div style="display: flex; align-items: center; gap: 8px; font-size: 0.76rem; color: #64748B; margin-top: 2px;">
                            <span style="background: {'#E2DFFF' if item['type']=='Dynamic' else '#F1F5F9'}; color: {'#3525CD' if item['type']=='Dynamic' else '#475569'}; padding: 1px 6px; border-radius: 4px; font-weight: 700; text-transform: uppercase;">{item['type']}</span>
                            <span>• Created {item['date']}</span>
                            <span>• <strong style="color: #4F46E5;">{item['scans']}</strong> scans</span>
                        </div>
                    </div>
                </div>
                <div style="display: flex; align-items: center; gap: 10px;">
                    <span style="background: {'#DCFCE7' if item['status']=='Active' else '#FEE2E2'}; color: {'#16A34A' if item['status']=='Active' else '#DC2626'}; padding: 3px 10px; border-radius: 9999px; font-size: 0.74rem; font-weight: 700;">
                        {'● Active' if item['status']=='Active' else '⏸ Paused'}
                    </span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# =========================================================================
# VIEW 2: CREATE QR CODE STUDIO (Stitch create_qr_code_type_content & preview)
# =========================================================================
elif st.session_state["nav_view"] == "Create QR Code":
    # 1. Stepper Header
    st.markdown(
        """
        <div class="stepper-container">
            <div class="step-item">
                <div class="step-num active">1</div>
                <div>
                    <div class="step-text-title">QR Type</div>
                    <div class="step-text-sub">Routing Mode</div>
                </div>
            </div>
            <div class="stepper-line"></div>
            <div class="step-item">
                <div class="step-num active">2</div>
                <div>
                    <div class="step-text-title">Payload Content</div>
                    <div class="step-text-sub">10 Formats</div>
                </div>
            </div>
            <div class="stepper-line"></div>
            <div class="step-item">
                <div class="step-num active">3</div>
                <div>
                    <div class="step-text-title">Design & Exports</div>
                    <div class="step-text-sub">Live Viewport</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Success Flow Celebration if Triggered
    if st.session_state.get("show_success_card", False):
        st.markdown(
            f"""
            <div class="success-hero-box">
                <div style="font-size: 2.2rem; margin-bottom: 0.35rem;">🎉</div>
                <div style="font-size: 1.4rem; font-weight: 700; color: #131B2E; letter-spacing: -0.02em;">
                    Your Dynamic QR is Live!
                </div>
                <div style="color: #64748B; font-size: 0.9rem; margin-top: 4px;">
                    <strong>{st.session_state.get('campaign_name', 'Campaign')}</strong> is fully generated, SSL-verified, and tracking real-time scans.
                </div>
                <div style="margin: 0.85rem 0;">
                    <span class="shortlink-pill">qr.st/d/summer25</span>
                </div>
                <div style="font-size: 0.8rem; color: #16A34A; font-weight: 600;">
                    ✅ Changes propagate to edge CDN within ~80ms without re-printing.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Responsive Studio Layout: Left (Configuration) & Right (Live Stage Viewport)
    col_form, col_stage = st.columns([1.18, 0.82], gap="large")

    # ---------------------------------------------------------------------
    # LEFT COLUMN: STEP 1 TYPE, STEP 2 CONTENT, STEP 3 CUSTOMIZATION
    # ---------------------------------------------------------------------
    with col_form:
        # STEP 1: CHOOSE QR TYPE
        st.markdown(
            """
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.65rem;">
                <div style="display: flex; align-items: center; gap: 8px;">
                    <span style="background: #E2DFFF; color: #3525CD; font-weight: 700; font-size: 0.72rem; padding: 2px 7px; border-radius: 4px;">STEP 1</span>
                    <span style="font-size: 1.05rem; font-weight: 700; color: #131B2E;">Choose QR Type</span>
                </div>
                <span style="font-size: 0.72rem; color: #4F46E5; font-weight: 700; text-transform: uppercase;">Required</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        t_col1, t_col2 = st.columns(2)
        with t_col1:
            is_dynamic = st.session_state["qr_mode"] == "Dynamic"
            st.markdown(
                f"""
                <div class="type-card {'selected' if is_dynamic else ''}">
                    <div style="display: flex; align-items: flex-start; justify-content: space-between;">
                        <div style="display: flex; align-items: center; gap: 8px;">
                            <div style="width: 36px; height: 36px; background: #4F46E5; color: white; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 1.1rem;">⚡</div>
                            <div>
                                <div style="font-weight: 700; font-size: 0.95rem;">Dynamic QR</div>
                                <span class="badge-recommended">Recommended</span>
                            </div>
                        </div>
                        <span style="color: {'#4F46E5' if is_dynamic else '#CBD5E1'}; font-size: 1.2rem;">{'●' if is_dynamic else '○'}</span>
                    </div>
                    <div style="font-size: 0.78rem; color: #64748B; margin-top: 8px; line-height: 1.4;">
                        Editable destination anytime • Full scan analytics • Instant edge sync.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button("Select Dynamic QR", key="btn_select_dyn", use_container_width=True):
                st.session_state["qr_mode"] = "Dynamic"
                st.rerun()

        with t_col2:
            is_static = st.session_state["qr_mode"] == "Static"
            st.markdown(
                f"""
                <div class="type-card {'selected' if is_static else ''}">
                    <div style="display: flex; align-items: flex-start; justify-content: space-between;">
                        <div style="display: flex; align-items: center; gap: 8px;">
                            <div style="width: 36px; height: 36px; background: #EAEDFF; color: #464555; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 1.1rem;">🔒</div>
                            <div>
                                <div style="font-weight: 700; font-size: 0.95rem;">Static QR</div>
                                <span style="background: #F1F5F9; color: #475569; font-size: 0.68rem; font-weight: 700; padding: 2px 7px; border-radius: 9999px; text-transform: uppercase;">Permanent</span>
                            </div>
                        </div>
                        <span style="color: {'#4F46E5' if is_static else '#CBD5E1'}; font-size: 1.2rem;">{'●' if is_static else '○'}</span>
                    </div>
                    <div style="font-size: 0.78rem; color: #64748B; margin-top: 8px; line-height: 1.4;">
                        Non-editable hardcoded data • Free unlimited offline scans.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button("Select Static QR", key="btn_select_stat", use_container_width=True):
                st.session_state["qr_mode"] = "Static"
                st.rerun()

        st.markdown("<hr>", unsafe_allow_html=True)

        # STEP 2: CHOOSE CONTENT TYPE & DETAILS
        st.markdown(
            """
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.65rem;">
                <div style="display: flex; align-items: center; gap: 8px;">
                    <span style="background: #E2DFFF; color: #3525CD; font-weight: 700; font-size: 0.72rem; padding: 2px 7px; border-radius: 4px;">STEP 2</span>
                    <span style="font-size: 1.05rem; font-weight: 700; color: #131B2E;">Payload Content Configuration</span>
                </div>
                <span style="font-size: 0.75rem; color: #64748B;">10 Types Supported</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        c_ptype, c_pclear = st.columns([3.2, 1.2])
        with c_ptype:
            selected_type = st.selectbox(
                "Select QR Format",
                options=QR_TYPES,
                key="qr_type",
                label_visibility="collapsed",
            )
        with c_pclear:
            if st.button("🧹 Clear Form", use_container_width=True, help="Reset form fields"):
                if "URL" in selected_type: st.session_state["url_input"] = ""
                elif "Text" in selected_type: st.session_state["text_input"] = ""
                elif "Wi-Fi" in selected_type:
                    st.session_state["wifi_ssid"] = ""
                    st.session_state["wifi_password"] = ""
                st.rerun()

        # Campaign Name field
        st.text_input("Campaign / QR Code Name", key="campaign_name", placeholder="e.g. Summer Promo Menu", help="Internal identifier for your dashboard tracking.")

        errors = {}
        payload_data = ""
        clean_type_name = selected_type.split()[-1].lower()

        # Render Content Form Fields based on Type
        # ========================== 1. URL ==========================
        if "URL" in selected_type:
            st.text_input(
                "Target Destination URL *",
                key="url_input",
                placeholder="https://yourdomain.com/landing",
                help="The destination address loaded when scanned.",
            )
            raw_url = st.session_state["url_input"].strip()
            if not raw_url:
                errors["url"] = "Target URL cannot be empty."
                render_field_error(errors["url"])
            else:
                payload_data = build_url(raw_url)
                st.markdown(
                    """
                    <div style="display: flex; align-items: center; gap: 6px; font-size: 0.75rem; color: #16A34A; font-weight: 600; margin-top: -0.25rem;">
                        <span>✓</span> Valid SSL Gateway Destination URL
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        # ========================== 2. Plain Text ==========================
        elif "Text" in selected_type:
            st.text_area(
                "Plain Text Payload *",
                key="text_input",
                placeholder="Enter unformatted plaintext, serial numbers, tokens...",
                height=110,
            )
            text_val = st.session_state["text_input"]
            char_count = len(text_val)
            st.markdown(f"<div style='font-size: 0.75rem; color: #64748B; text-align: right;'>{char_count} / 2,000 characters</div>", unsafe_allow_html=True)
            if not text_val.strip():
                errors["text"] = "Text payload cannot be empty."
                render_field_error(errors["text"])
            elif char_count > 2000:
                errors["text"] = "Text exceeds the 2,000 character ceiling."
                render_field_error(errors["text"])
            else:
                payload_data = build_text(text_val)

        # ========================== 3. Wi-Fi ==========================
        elif "Wi-Fi" in selected_type:
            st.text_input("Network Name (SSID) *", key="wifi_ssid", placeholder="StoreGuest_5G")
            ssid_val = st.session_state["wifi_ssid"].strip()
            if not ssid_val:
                errors["wifi_ssid"] = "Wi-Fi SSID is required."
                render_field_error(errors["wifi_ssid"])

            w_c1, w_c2 = st.columns([1.5, 1])
            with w_c1:
                st.text_input("Wi-Fi Password", key="wifi_password", type="default" if st.session_state.get("wifi_show_password") else "password")
            with w_c2:
                st.selectbox("Security Encryption", options=["WPA/WPA2", "WEP", "Open (nopass)"], key="wifi_security")

            wc_chk1, wc_chk2 = st.columns(2)
            with wc_chk1:
                st.checkbox("Show password plaintext", key="wifi_show_password")
            with wc_chk2:
                st.checkbox("Hidden network SSID", key="wifi_hidden")

            if not errors:
                payload_data = build_wifi(
                    ssid=ssid_val,
                    password=st.session_state["wifi_password"],
                    security=st.session_state["wifi_security"],
                    hidden=st.session_state["wifi_hidden"],
                )

        # ========================== 4. vCard Profile ==========================
        elif "Contact" in selected_type or "vCard" in selected_type:
            vc1, vc2 = st.columns(2)
            with vc1: st.text_input("First Name *", key="vcard_first_name")
            with vc2: st.text_input("Last Name", key="vcard_last_name")

            if not st.session_state["vcard_first_name"].strip():
                errors["vcard_fn"] = "First name is required."
                render_field_error(errors["vcard_fn"])

            vc3, vc4 = st.columns(2)
            with vc3: st.text_input("Primary Mobile Number *", key="vcard_phone")
            with vc4: st.text_input("Email Address", key="vcard_email")

            if not st.session_state["vcard_phone"].strip():
                errors["vcard_ph"] = "Phone number is required."
                render_field_error(errors["vcard_ph"])

            vc5, vc6 = st.columns(2)
            with vc5: st.text_input("Organization / Company", key="vcard_company")
            with vc6: st.text_input("Designation / Title", key="vcard_job_title")

            st.text_input("Website Portfolio Link", key="vcard_website")
            st.text_input("Office / Postal Address", key="vcard_address")

            if not errors:
                payload_data = build_vcard(
                    first_name=st.session_state["vcard_first_name"],
                    last_name=st.session_state["vcard_last_name"],
                    phone=st.session_state["vcard_phone"],
                    email=st.session_state["vcard_email"],
                    company=st.session_state["vcard_company"],
                    job_title=st.session_state["vcard_job_title"],
                    website=st.session_state["vcard_website"],
                    address=st.session_state["vcard_address"],
                )

        # ========================== 5. WhatsApp ==========================
        elif "WhatsApp" in selected_type:
            wa_c1, wa_c2 = st.columns([1, 2.2])
            with wa_c1: st.selectbox("Country Code", options=["+91", "+1", "+44", "+61", "+81", "+49", "+971"], key="wa_cc")
            with wa_c2: st.text_input("WhatsApp Mobile Number *", key="wa_phone", placeholder="9876543210")

            num_val = st.session_state["wa_phone"].strip()
            digits = re.sub(r"\D", "", num_val)
            if not num_val:
                errors["wa_phone"] = "WhatsApp number is required."
                render_field_error(errors["wa_phone"])
            elif len(digits) < 10:
                errors["wa_phone"] = "Enter a valid phone number (at least 10 digits)."
                render_field_error(errors["wa_phone"])

            st.text_area("Prefilled Chat Message", key="wa_message", placeholder="Hello, I would like to inquire about...", height=85)
            if not errors:
                payload_data = build_whatsapp(f"{st.session_state['wa_cc']}{num_val}", message=st.session_state["wa_message"])

        # ========================== 6. Email ==========================
        elif "Email" in selected_type:
            st.text_input("Recipient Email Address *", key="email_to", placeholder="support@company.com")
            to_val = st.session_state["email_to"].strip()
            if not to_val or not re.match(EMAIL_REGEX, to_val):
                errors["email"] = "Please enter a valid email address."
                render_field_error(errors["email"])

            st.text_input("Subject Line", key="email_subject", placeholder="Product Inquiry")
            st.text_area("Message Body Content", key="email_body", placeholder="Write your prefilled email draft here...", height=90)
            if not errors:
                payload_data = build_email(to=to_val, subject=st.session_state["email_subject"], body=st.session_state["email_body"])

        # ========================== 7. Phone Call ==========================
        elif "Phone" in selected_type:
            p_c1, p_c2 = st.columns([1, 2.2])
            with p_c1: st.selectbox("Country Code", options=["+91", "+1", "+44", "+61", "+81", "+49"], key="phone_cc")
            with p_c2: st.text_input("Telephone Number *", key="phone_number", placeholder="9876543210")

            num_val = st.session_state["phone_number"].strip()
            if not num_val:
                errors["phone"] = "Phone number is required."
                render_field_error(errors["phone"])
            else:
                payload_data = build_phone(num_val, country_code=st.session_state["phone_cc"])

        # ========================== 8. SMS ==========================
        elif "SMS" in selected_type:
            st.text_input("Target Mobile Number *", key="sms_number", placeholder="+919876543210")
            num_val = st.session_state["sms_number"].strip()
            if not num_val:
                errors["sms"] = "Target phone number is required."
                render_field_error(errors["sms"])
            st.text_area("Pre-filled Text Message", key="sms_message", placeholder="Hello, confirming our meeting at 4 PM.", height=80)
            if not errors:
                payload_data = build_sms(num_val, message=st.session_state["sms_message"])

        # ========================== 9. UPI Payment ==========================
        elif "UPI" in selected_type:
            st.text_input("Merchant UPI ID (VPA) *", key="upi_id", placeholder="merchant@okhdfcbank")
            upi_val = st.session_state["upi_id"].strip()
            if not upi_val or not re.match(UPI_REGEX, upi_val):
                errors["upi_id"] = "Invalid UPI ID (e.g. name@bank)."
                render_field_error(errors["upi_id"])

            st.text_input("Payee Account Name *", key="upi_name", placeholder="Acme Official Store")
            if not st.session_state["upi_name"].strip():
                errors["upi_name"] = "Payee name is required."
                render_field_error(errors["upi_name"])

            u_c1, u_c2 = st.columns(2)
            with u_c1: st.text_input("Amount in INR (Optional)", key="upi_amount", placeholder="750.00")
            with u_c2: st.text_input("Payment Note / Reference", key="upi_note", placeholder="Invoice #5021")

            if not errors:
                payload_data = build_upi(
                    upi_id=upi_val,
                    payee_name=st.session_state["upi_name"],
                    amount=st.session_state["upi_amount"],
                    note=st.session_state["upi_note"],
                )

        # ========================== 10. Image ==========================
        elif "Image" in selected_type:
            st.caption("Upload an image (PNG, JPG, WebP) to encode or provide a hosted URL.")
            up_img = st.file_uploader("Upload Image", type=["png", "jpg", "jpeg", "webp"], key="img_uploader")
            if up_img:
                try:
                    payload_data = build_image_data_uri(up_img.getvalue(), max_dimension=st.session_state.get("img_max_dimension", 48))
                    st.success("✅ Image converted to lightweight Data URI")
                except Exception as e:
                    errors["img"] = str(e)
                    render_field_error(errors["img"])
            else:
                st.text_input("Or Hosted Image URL", key="img_hosted_url", placeholder="https://example.com/asset.png")
                if st.session_state["img_hosted_url"]:
                    payload_data = build_url(st.session_state["img_hosted_url"])

        # Advanced Security & Rules Toggles (Matches Stitch)
        with st.expander("🛡️ Security & Access Rules", expanded=False):
            sec_c1, sec_c2 = st.columns(2)
            with sec_c1:
                st.checkbox("Password Protection", key="password_protect", help="Require pin code to view content")
                if st.session_state.get("password_protect"):
                    st.text_input("Access PIN Code", key="password_value", type="password", placeholder="e.g. 4821")
            with sec_c2:
                st.checkbox("Scan Expiration Date", key="expiration_date", help="Deactivate code after date")
                if st.session_state.get("expiration_date"):
                    st.date_input("Deactivate After", key="expiry_date_val")

        st.markdown("<hr>", unsafe_allow_html=True)

        # =================================================================
        # STEP 3 CUSTOMIZATION ACCORDIONS (Colors, Pattern, Logo, Size)
        # =================================================================
        st.markdown(
            """
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.65rem;">
                <div style="display: flex; align-items: center; gap: 8px;">
                    <span style="background: #E2DFFF; color: #3525CD; font-weight: 700; font-size: 0.72rem; padding: 2px 7px; border-radius: 4px;">STEP 3</span>
                    <span style="font-size: 1.05rem; font-weight: 700; color: #131B2E;">Design & Studio Customization</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Accordion 1: Colors & Finish
        with st.expander("🎨 Colors & Canvas Finish", expanded=True):
            st.caption("Foreground and background palette.")
            # Color Preset Swatches
            swatch_cols = st.columns(5)
            preset_palette = [
                ("#4F46E5", "Indigo"),
                ("#131B2E", "Slate"),
                ("#00702F", "Forest"),
                ("#BA1A1A", "Crimson"),
                ("#2C3480", "Cobalt"),
            ]
            for idx, (p_hex, p_name) in enumerate(preset_palette):
                with swatch_cols[idx]:
                    if st.button(f"● {p_name}", key=f"swatch_{p_name}", use_container_width=True):
                        st.session_state["qr_fg_color"] = p_hex
                        st.rerun()

            c_fg, c_bg = st.columns(2)
            with c_fg:
                fg_col = st.color_picker("Foreground (Matrix Dots)", value=st.session_state.get("qr_fg_color", "#4F46E5"))
                st.session_state["qr_fg_color"] = fg_col
            with c_bg:
                bg_col = st.color_picker("Background Canvas", value=st.session_state.get("qr_bg_color", "#FFFFFF"))
                st.session_state["qr_bg_color"] = bg_col

            # WCAG Contrast Ratio Check
            ratio = contrast_ratio(fg_col, bg_col)
            is_contrast_ok = ratio >= 3.0
            if is_contrast_ok:
                st.markdown(f'<div class="contrast-badge contrast-pass">✅ Contrast Ratio: <strong>{ratio:.1f}:1</strong> (Passes WCAG ≥ 3:1)</div>', unsafe_allow_html=True)
                st.session_state["allow_low_contrast"] = False
            else:
                st.markdown(f'<div class="contrast-badge contrast-fail">⚠️ Low Contrast: <strong>{ratio:.1f}:1</strong> (&lt; 3:1 minimum)</div>', unsafe_allow_html=True)
                st.session_state["allow_low_contrast"] = st.checkbox("Proceed with low contrast download anyway", value=st.session_state.get("allow_low_contrast", False))

        # Accordion 2: Pattern & Dots Geometry
        with st.expander("💠 Pattern & Dot Geometry", expanded=True):
            style_choice = st.radio(
                "Matrix Module Dot Geometry",
                options=["Square", "Rounded", "Circle"],
                index=["Square", "Rounded", "Circle"].index(st.session_state.get("qr_style", "Rounded")),
                horizontal=True,
                help="Square classic, Modern rounded corners, or elegant smooth circles.",
            )
            st.session_state["qr_style"] = style_choice

        # Accordion 3: Center Logo & Watermark
        with st.expander("🖼️ Center Logo & Presets", expanded=bool(st.session_state.get("logo_bytes"))):
            st.caption("Upload custom logo (PNG/JPG up to 2 MB) or select quick preset.")
            logo_up = st.file_uploader("Upload Brand Logo", type=["png", "jpg", "jpeg"], key="logo_file_input", label_visibility="collapsed")
            if logo_up is not None:
                is_valid_logo, logo_err, valid_bytes = validate_logo(logo_up)
                if is_valid_logo:
                    st.session_state["logo_bytes"] = valid_bytes
                    st.session_state["logo_filename"] = logo_up.name
                else:
                    render_field_error(logo_err)

            if st.session_state.get("logo_bytes") is not None:
                c_prev_l, c_act_l = st.columns([1, 2])
                with c_prev_l:
                    st.image(st.session_state["logo_bytes"], width=75, caption="Active Logo")
                with c_act_l:
                    st.markdown(f"**Logo Attached:** `{st.session_state.get('logo_filename', 'brand_logo')}`")
                    if st.button("🗑️ Remove Logo", use_container_width=True):
                        st.session_state["logo_bytes"] = None
                        st.session_state["logo_filename"] = ""
                        st.rerun()

                st.markdown(
                    """
                    <div style="background: #F2F3FF; border-left: 3px solid #4F46E5; padding: 6px 10px; border-radius: 0 6px 6px 0; font-size: 0.78rem; color: #464555; margin-top: 6px;">
                        ℹ️ <strong>Auto-Protection Active:</strong> Error Correction Level H (30% recovery) is automatically enforced for guaranteed scanning with center logo.
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        # Accordion 4: Size & Redundancy
        with st.expander("⚙️ Size & Error Correction", expanded=False):
            c_ecc, c_res = st.columns(2)
            with c_ecc:
                ecc_sel = st.selectbox("Error Correction (ECC)", options=["H (30% - Best)", "Q (25%)", "M (15% - Standard)", "L (7%)"], index=0)
                st.session_state["ecc_level"] = ecc_sel[0]
            with c_res:
                b_size = st.slider("Module Pixel Scale", min_value=6, max_value=16, value=st.session_state.get("qr_box_size", 10))
                st.session_state["qr_box_size"] = b_size

    # ---------------------------------------------------------------------
    # RIGHT COLUMN: LIVE QR STAGE VIEWPORT & MULTI-FORMAT EXPORT
    # ---------------------------------------------------------------------
    with col_stage:
        st.markdown(
            """
            <div style="font-size: 1.05rem; font-weight: 700; color: #131B2E; margin-bottom: 0.65rem;">
                Live QR Stage & Exports
            </div>
            """,
            unsafe_allow_html=True,
        )

        is_payload_valid = len(errors) == 0 and bool(payload_data)

        if is_payload_valid:
            try:
                # Build Styled QR Image
                pil_qr = build_qr(
                    data=payload_data,
                    size=st.session_state.get("qr_box_size", 10),
                    fg=st.session_state.get("qr_fg_color", "#4F46E5"),
                    bg=st.session_state.get("qr_bg_color", "#FFFFFF"),
                    style=st.session_state.get("qr_style", "Rounded"),
                    logo_bytes=st.session_state.get("logo_bytes"),
                )

                png_bytes = to_png(pil_qr)
                b64_png = base64.b64encode(png_bytes).decode("utf-8")

                mode_label = st.session_state.get("qr_mode", "Dynamic")
                dest_preview = payload_data[:34] + ("..." if len(payload_data) > 34 else "")

                # QR Stage Viewport Container
                zoomed_class = "zoomed" if st.session_state.get("stage_zoom") else ""
                inverted_class = "inverted" if st.session_state.get("stage_invert") else ""

                st.markdown(
                    f"""
                    <div class="qr-stage-card">
                        <div class="stage-header-bar">
                            <div class="dynamic-active-pill">
                                <span class="status-dot-pulse"></span>
                                <span>{mode_label}</span>
                            </div>
                            <div class="target-url-badge" title="{payload_data}">
                                <span>🔗</span> {dest_preview}
                            </div>
                        </div>
                        <div class="qr-viewport-frame {zoomed_class} {inverted_class}">
                            <img src="data:image/png;base64,{b64_png}" style="width: 230px; height: 230px; display: block; border-radius: 8px;" alt="QR Code" />
                        </div>
                        <div style="font-size: 0.8rem; color: #64748B; font-weight: 500;">
                            Scan with any smartphone camera lens
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                # Floating Action Pill Toolbar (Zoom, Invert, Simulate Scan)
                t_b1, t_b2, t_b3 = st.columns(3)
                with t_b1:
                    if st.button("🔍 Zoom Toggle", use_container_width=True):
                        st.session_state["stage_zoom"] = not st.session_state.get("stage_zoom", False)
                        st.rerun()
                with t_b2:
                    if st.button("🌓 Invert Colors", use_container_width=True):
                        st.session_state["stage_invert"] = not st.session_state.get("stage_invert", False)
                        st.rerun()
                with t_b3:
                    if st.button("🎯 Simulate Scan", use_container_width=True):
                        st.session_state["simulate_scan_active"] = True
                        st.rerun()

                # Scan Simulator Banner Notification
                if st.session_state.get("simulate_scan_active"):
                    st.markdown(
                        """
                        <div class="scan-simulator-banner">
                            <div style="display: flex; align-items: center; gap: 6px;">
                                <span>✅</span>
                                <span>Optimal 100% Scan Integrity</span>
                            </div>
                            <span style="font-size: 0.75rem; background: #FFFFFF; padding: 2px 7px; border-radius: 4px; color: #16A34A;">120ms</span>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                st.write("")

                # Generate / Save CTA Button
                if st.button("⚡ Generate & Publish QR Code", type="primary", use_container_width=True):
                    st.session_state["show_success_card"] = True
                    # Add to mock repository
                    new_entry = {
                        "id": f"QR-{int(datetime.now().timestamp()) % 100000}",
                        "name": st.session_state.get("campaign_name", "New QR Code"),
                        "type": st.session_state.get("qr_mode", "Dynamic"),
                        "date": datetime.now().strftime("%b %d, %Y"),
                        "scans": "0",
                        "status": "Active",
                        "url": payload_data,
                    }
                    st.session_state["recent_qrs"].insert(0, new_entry)
                    st.rerun()

                # Multi-Format Downloads Grid
                st.markdown("<div style='font-size: 0.88rem; font-weight: 700; color: #131B2E; margin: 0.75rem 0 0.35rem 0;'>Direct Export Formats</div>", unsafe_allow_html=True)
                timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
                file_base = f"qr_{clean_type_name}_{timestamp_str}"

                can_download = is_contrast_ok or st.session_state.get("allow_low_contrast", False)
                jpg_bytes = to_jpg(pil_qr)
                pdf_bytes = to_pdf(pil_qr)
                svg_bytes = to_svg(
                    payload_data,
                    fg=st.session_state.get("qr_fg_color", "#4F46E5"),
                    bg=st.session_state.get("qr_bg_color", "#FFFFFF"),
                    scale=st.session_state.get("qr_box_size", 10),
                )

                d_c1, d_c2 = st.columns(2)
                with d_c1:
                    st.download_button(
                        label="⬇️ PNG (High-Res)",
                        data=png_bytes,
                        file_name=f"{file_base}.png",
                        mime="image/png",
                        type="primary",
                        disabled=not can_download,
                        use_container_width=True,
                    )
                    st.download_button(
                        label="⬇️ SVG (Vector Math)",
                        data=svg_bytes,
                        file_name=f"{file_base}.svg",
                        mime="image/svg+xml",
                        disabled=not can_download,
                        use_container_width=True,
                    )
                with d_c2:
                    st.download_button(
                        label="⬇️ JPG (Raster)",
                        data=jpg_bytes,
                        file_name=f"{file_base}.jpg",
                        mime="image/jpeg",
                        disabled=not can_download,
                        use_container_width=True,
                    )
                    st.download_button(
                        label="⬇️ PDF (Print Package)",
                        data=pdf_bytes,
                        file_name=f"{file_base}.pdf",
                        mime="application/pdf",
                        disabled=not can_download,
                        use_container_width=True,
                    )

                # Clipboard Copy component
                st.write("")
                render_clipboard_component(png_bytes)

                # Inspect Raw Payload
                with st.expander("🔍 Inspect Encoded Matrix Payload", expanded=False):
                    st.code(payload_data, language="text")

            except Exception as e:
                st.error(f"Error compiling styled QR code: {str(e)}")

        else:
            st.markdown(
                """
                <div style="background: #FFFFFF; border: 2px dashed #E2E8F0; border-radius: 16px; padding: 3rem 1.5rem; text-align: center; color: #64748B;">
                    <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">⚡</div>
                    <div style="font-weight: 700; color: #131B2E; font-size: 1.05rem;">Awaiting Valid Input</div>
                    <div style="font-size: 0.82rem; color: #64748B; max-width: 240px; margin: 4px auto 0 auto;">
                        Fill in all required fields on the left to render your styled live preview.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )


# =========================================================================
# VIEW 3: MY QR CODES REPOSITORY
# =========================================================================
elif st.session_state["nav_view"] == "My QR Codes":
    st.markdown("<div style='font-size: 1.4rem; font-weight: 700; color: #131B2E;'>My QR Codes Repository</div>", unsafe_allow_html=True)
    st.markdown("<div style='font-size: 0.88rem; color: #64748B; margin-bottom: 1rem;'>Manage, route, monitor and download your active QR campaign assets.</div>", unsafe_allow_html=True)

    # Filter chips
    f1, f2, f3, f4 = st.columns([1, 1, 1, 3])
    with f1: st.button("All Codes (48)", use_container_width=True)
    with f2: st.button("⚡ Dynamic (30)", use_container_width=True)
    with f3: st.button("🔒 Static (18)", use_container_width=True)

    st.write("")
    for item in st.session_state["recent_qrs"]:
        with st.container():
            st.markdown(
                f"""
                <div class="recent-qr-card">
                    <div style="display: flex; align-items: center; gap: 14px;">
                        <div style="width: 44px; height: 44px; background: #F2F3FF; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 1.3rem;">
                            ⚡
                        </div>
                        <div>
                            <div style="font-weight: 700; font-size: 1rem; color: #131B2E;">{item['name']} <span style="font-size: 0.75rem; color: #4F46E5; font-weight: 600;">#{item['id']}</span></div>
                            <div style="font-size: 0.8rem; color: #64748B; margin-top: 2px;">
                                Destination: <code style="background: #F1F5F9; padding: 2px 6px; border-radius: 4px; color: #131B2E;">{item['url']}</code>
                            </div>
                            <div style="display: flex; align-items: center; gap: 10px; font-size: 0.75rem; color: #64748B; margin-top: 4px;">
                                <span style="background: {'#E2DFFF' if item['type']=='Dynamic' else '#F1F5F9'}; color: {'#3525CD' if item['type']=='Dynamic' else '#475569'}; padding: 1px 6px; border-radius: 4px; font-weight: 700;">{item['type']}</span>
                                <span>• Created: {item['date']}</span>
                                <span>• Total Scans: <strong style="color: #4F46E5;">{item['scans']}</strong></span>
                            </div>
                        </div>
                    </div>
                    <div style="display: flex; align-items: center; gap: 10px;">
                        <span style="background: {'#DCFCE7' if item['status']=='Active' else '#FEE2E2'}; color: {'#16A34A' if item['status']=='Active' else '#DC2626'}; padding: 4px 12px; border-radius: 9999px; font-size: 0.75rem; font-weight: 700;">
                            {'● Active' if item['status']=='Active' else '⏸ Paused'}
                        </span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )


# =========================================================================
# VIEW 4: ANALYTICS DASHBOARD
# =========================================================================
elif st.session_state["nav_view"] == "Analytics":
    st.markdown("<div style='font-size: 1.4rem; font-weight: 700; color: #131B2E;'>Live Scan Telemetry & Analytics</div>", unsafe_allow_html=True)
    st.markdown("<div style='font-size: 0.88rem; color: #64748B; margin-bottom: 1rem;'>Real-time performance analytics across all dynamic QR campaigns.</div>", unsafe_allow_html=True)

    a1, a2, a3, a4 = st.columns(4)
    with a1:
        st.markdown(
            """
            <div class="stat-card">
                <span class="stat-label">Total Impressions</span>
                <div class="stat-val">14,290</div>
                <div class="stat-trend trend-up">▲ +28.4% this week</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with a2:
        st.markdown(
            """
            <div class="stat-card">
                <span class="stat-label">Unique Scanners</span>
                <div class="stat-val">11,420</div>
                <div class="stat-trend trend-up">▲ 79.9% unique rate</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with a3:
        st.markdown(
            """
            <div class="stat-card">
                <span class="stat-label">Avg Routing Latency</span>
                <div class="stat-val">84 ms</div>
                <div class="stat-trend trend-up">⚡ Global edge CDN</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with a4:
        st.markdown(
            """
            <div class="stat-card">
                <span class="stat-label">Top Location</span>
                <div class="stat-val">United States</div>
                <div class="stat-trend trend-indigo">42% total traffic</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.write("")
    # Chart Mockup
    c_cht1, c_cht2 = st.columns([2, 1])
    with c_cht1:
        st.markdown("<div style='font-weight: 700; margin-bottom: 0.5rem;'>Scans Over Past 7 Days</div>", unsafe_allow_html=True)
        # Using Streamlit native bar chart
        import pandas as pd
        sample_data = pd.DataFrame(
            {"Scans": [1420, 1890, 2150, 1780, 2430, 2980, 3140]},
            index=["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
        )
        st.bar_chart(sample_data, color="#4F46E5")

    with c_cht2:
        st.markdown("<div style='font-weight: 700; margin-bottom: 0.5rem;'>Device Distribution</div>", unsafe_allow_html=True)
        dev_data = pd.DataFrame(
            {"Percentage": [58, 37, 5]},
            index=["Apple iOS", "Android OS", "Desktop/Web"],
        )
        st.bar_chart(dev_data, color="#3525CD")


# =========================================================================
# VIEW 5: SETTINGS & API
# =========================================================================
elif st.session_state["nav_view"] == "Settings":
    st.markdown("<div style='font-size: 1.4rem; font-weight: 700; color: #131B2E;'>Workspace Settings & API Keys</div>", unsafe_allow_html=True)
    st.markdown("<div style='font-size: 0.88rem; color: #64748B; margin-bottom: 1rem;'>Manage workspace team access, custom short-link domains, and developer REST API tokens.</div>", unsafe_allow_html=True)

    with st.expander("🔑 Developer REST API Keys", expanded=True):
        st.text_input("Active Secret Token", value="qr_live_sk_89432890432894109432", type="password", disabled=True)
        c_k1, c_k2 = st.columns(2)
        with c_k1:
            if st.button("Generate New API Key", use_container_width=True):
                st.success("New token generated: qr_live_sk_99182371928371928371")
        with c_k2:
            st.button("Revoke Compromised Key", use_container_width=True)

    with st.expander("🌐 Custom Domain Routing", expanded=False):
        st.text_input("Custom Short-Link Domain", value="qr.yourbrand.com", placeholder="qr.brand.com")
        st.caption("Point CNAME record to cdn.qrstudio.app to activate SSL custom routing.")

    with st.expander("🏢 Workspace Profile", expanded=False):
        st.text_input("Organization Name", value="Acme Enterprise")
        st.text_input("Admin Billing Email", value="admin@acme.com")
