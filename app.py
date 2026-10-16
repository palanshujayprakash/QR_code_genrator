"""
Streamlit QR Code Studio - Phase 1 Implementation
Modular, high-performance QR code generator with:
- Feature 1: Logo QR (Memory-only Pillow verification, ~20% width, white rounded padding, auto Level H, remove button)
- Feature 2: Styled QR (Square, Rounded, Circle dot styles, foreground/background color, WCAG 3:1 contrast check)
- Feature 8: Multi-format export (PNG, JPG, SVG, PDF, clipboard copy, timestamped filenames)
Adheres to Black (#000000), White (#FFFFFF), and Cobalt Blue Deep (#2C3480) theme.
"""

import io
import re
import base64
from datetime import datetime
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
    page_title="QR Studio | Professional QR Code Generator",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Custom High-End Styling: Black (#000000), White (#FFFFFF), Cobalt Blue Deep (#2C3480)
st.markdown(
    """
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Space+Grotesk:wght@600;700&display=swap" rel="stylesheet">

    <style>
    /* Global Base */
    html, body, [class*="css"], .stApp {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
        background-color: #000000 !important;
        color: #FFFFFF !important;
    }

    /* Ambient Background Glow */
    .stApp {
        background-image: 
            radial-gradient(ellipse 70% 35% at 50% -10%, rgba(44, 52, 128, 0.35), transparent 70%),
            radial-gradient(circle 400px at 95% 85%, rgba(44, 52, 128, 0.12), transparent);
        background-attachment: fixed;
    }

    /* Header Banner */
    .header-container {
        padding: 1.25rem 0 1.75rem 0;
        margin-bottom: 1.5rem;
        border-bottom: 1px solid rgba(44, 52, 128, 0.35);
        display: flex;
        flex-direction: column;
        align-items: flex-start;
    }

    .brand-pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(44, 52, 128, 0.25);
        border: 1px solid #2C3480;
        color: #FFFFFF;
        padding: 5px 12px;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin-bottom: 0.75rem;
        box-shadow: 0 0 15px rgba(44, 52, 128, 0.3);
    }

    .brand-title {
        font-family: 'Space Grotesk', sans-serif !important;
        font-size: 2.3rem;
        font-weight: 700;
        letter-spacing: -0.02em;
        margin: 0;
        color: #FFFFFF;
        display: flex;
        align-items: center;
        gap: 10px;
    }

    .brand-title span.accent {
        color: #FFFFFF;
        background: linear-gradient(135deg, #FFFFFF 20%, #a5b4fc 60%, #2C3480 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .brand-subtitle {
        color: #cbd5e1;
        font-size: 0.95rem;
        margin-top: 0.4rem;
        max-width: 720px;
        line-height: 1.5;
    }

    /* Section Headings */
    .step-heading {
        display: flex;
        align-items: center;
        gap: 10px;
        font-size: 1.15rem;
        font-weight: 700;
        color: #FFFFFF;
        margin-bottom: 1rem;
    }

    .step-badge {
        background: #2C3480;
        color: #FFFFFF;
        font-size: 0.75rem;
        font-weight: 800;
        padding: 3px 8px;
        border-radius: 6px;
        letter-spacing: 0.05em;
    }

    /* Field Errors */
    .field-error {
        background: rgba(220, 38, 38, 0.12);
        border: 1px solid rgba(239, 68, 68, 0.4);
        color: #fca5a5;
        font-size: 0.82rem;
        padding: 6px 12px;
        border-radius: 8px;
        margin-top: -0.3rem;
        margin-bottom: 0.75rem;
        font-weight: 500;
        display: flex;
        align-items: center;
        gap: 6px;
    }

    /* Contrast Warnings & Badges */
    .contrast-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-top: 4px;
        margin-bottom: 8px;
    }

    .contrast-pass {
        background: rgba(34, 197, 94, 0.12);
        border: 1px solid rgba(34, 197, 94, 0.4);
        color: #86efac;
    }

    .contrast-fail {
        background: rgba(234, 179, 8, 0.14);
        border: 1px solid rgba(234, 179, 8, 0.45);
        color: #fde047;
    }

    /* Character Counter */
    .char-counter {
        font-size: 0.8rem;
        color: #94a3b8;
        text-align: right;
        margin-top: -0.4rem;
        margin-bottom: 0.6rem;
        font-weight: 500;
    }
    .char-counter-warn {
        color: #ef4444 !important;
        font-weight: 700;
    }

    /* Input & Widget Styling */
    div[data-baseweb="input"] > div,
    div[data-baseweb="select"] > div,
    div[data-baseweb="textarea"] > div,
    input, textarea {
        background-color: #0b0e1e !important;
        border-color: rgba(44, 52, 128, 0.45) !important;
        color: #FFFFFF !important;
        border-radius: 10px !important;
    }

    div[data-baseweb="input"]:focus-within > div,
    div[data-baseweb="textarea"]:focus-within > div,
    div[data-baseweb="select"]:focus-within > div {
        border-color: #2C3480 !important;
        box-shadow: 0 0 0 2px rgba(44, 52, 128, 0.5) !important;
    }

    label p {
        color: #FFFFFF !important;
        font-weight: 600 !important;
        font-size: 0.88rem !important;
    }

    /* File Uploader Container */
    div[data-testid="stFileUploader"] {
        background: #0b0e1e !important;
        border: 1px dashed rgba(44, 52, 128, 0.6) !important;
        border-radius: 12px !important;
        padding: 10px !important;
    }

    /* Buttons */
    button[kind="primary"] {
        background: linear-gradient(135deg, #2C3480 0%, #3b469e 100%) !important;
        color: #FFFFFF !important;
        border: 1px solid rgba(255, 255, 255, 0.25) !important;
        border-radius: 10px !important;
        padding: 0.65rem 1.25rem !important;
        font-weight: 700 !important;
        letter-spacing: 0.02em !important;
        box-shadow: 0 4px 18px rgba(44, 52, 128, 0.45) !important;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }

    button[kind="primary"]:hover {
        background: linear-gradient(135deg, #374198 0%, #4754b8 100%) !important;
        box-shadow: 0 6px 24px rgba(44, 52, 128, 0.65) !important;
        transform: translateY(-1px) !important;
    }

    button[kind="secondary"] {
        background: #0b0e1e !important;
        color: #FFFFFF !important;
        border: 1px solid rgba(44, 52, 128, 0.4) !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
    }

    button[kind="secondary"]:hover {
        background: rgba(44, 52, 128, 0.25) !important;
        border-color: #2C3480 !important;
        color: #FFFFFF !important;
    }

    /* QR Stage Container */
    .qr-stage {
        background: #080a15;
        border: 1px solid rgba(44, 52, 128, 0.45);
        border-radius: 20px;
        padding: 1.8rem 1.4rem;
        text-align: center;
        box-shadow: 0 16px 40px rgba(0, 0, 0, 0.7);
        position: sticky;
        top: 1.5rem;
    }

    .qr-canvas-holder {
        background: #FFFFFF;
        padding: 14px;
        border-radius: 16px;
        display: inline-block;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5), 0 0 20px rgba(44, 52, 128, 0.35);
        border: 3px solid #2C3480;
        margin-bottom: 1rem;
    }

    .placeholder-box {
        border: 2px dashed rgba(44, 52, 128, 0.4);
        border-radius: 16px;
        padding: 3.5rem 1.5rem;
        text-align: center;
        background: rgba(8, 10, 21, 0.6);
        color: #94a3b8;
    }

    .qr-badge {
        display: inline-block;
        background: rgba(44, 52, 128, 0.25);
        color: #FFFFFF;
        border: 1px solid #2C3480;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.78rem;
        font-weight: 600;
        margin-bottom: 0.75rem;
    }

    .info-note {
        background: rgba(44, 52, 128, 0.15);
        border-left: 3px solid #2C3480;
        padding: 8px 12px;
        border-radius: 0 8px 8px 0;
        font-size: 0.82rem;
        color: #cbd5e1;
        margin: 8px 0 12px 0;
        line-height: 1.45;
    }

    /* Expander Styling */
    .streamlit-expanderHeader {
        background-color: #0b0e1e !important;
        border: 1px solid rgba(44, 52, 128, 0.35) !important;
        border-radius: 10px !important;
        color: #FFFFFF !important;
        font-weight: 600 !important;
    }

    div[data-testid="stExpanderDetails"] {
        background-color: #060812 !important;
        border: 1px solid rgba(44, 52, 128, 0.3) !important;
        border-top: none !important;
        border-radius: 0 0 10px 10px !important;
    }

    hr {
        border-color: rgba(44, 52, 128, 0.25) !important;
        margin: 1.25rem 0 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Header Section
st.markdown(
    """
    <div class="header-container">
        <div class="brand-pill">⚡ Cobalt Studio • Phase 1 Enterprise</div>
        <div class="brand-title">QR <span class="accent">Generator</span></div>
        <div class="brand-subtitle">
            Generate high-resolution QR codes with custom dot styles (Square, Rounded, Circle), center logo embedding, WCAG contrast verification, and multi-format vector exports (PNG, JPG, SVG, PDF).
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Available Formats
QR_TYPES = [
    "🌐 URL",
    "📝 Plain Text",
    "🖼️ Image (Upload)",
    "📶 Wi-Fi Network",
    "👤 Contact Card (vCard)",
    "✉️ Email Message",
    "📞 Phone Call",
    "💬 SMS Message",
    "🟢 WhatsApp Chat",
    "💳 UPI Payment",
]

EMAIL_REGEX = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
UPI_REGEX = r"^[\w.-]+@[\w.-]+$"

def render_field_error(msg: str):
    st.markdown(f'<div class="field-error">⚠️ {msg}</div>', unsafe_allow_html=True)


def render_clipboard_component(png_bytes: bytes):
    """
    Render a modern 'Copy to clipboard' component using browser Clipboard API.
    Provides graceful fallback messaging when clipboard access is blocked.
    """
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
          font-family: 'Plus Jakarta Sans', -apple-system, sans-serif;
        }}
        .clip-btn {{
          width: 100%;
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 8px;
          background: #0b0e1e;
          color: #FFFFFF;
          border: 1px solid rgba(44, 52, 128, 0.5);
          border-radius: 10px;
          padding: 0.65rem 1rem;
          font-size: 0.88rem;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.2s ease;
          box-sizing: border-box;
        }}
        .clip-btn:hover {{
          background: rgba(44, 52, 128, 0.35);
          border-color: #2C3480;
        }}
        .clip-btn.success {{
          background: #1e3a8a;
          border-color: #3b82f6;
        }}
        .fallback-note {{
          display: none;
          margin-top: 6px;
          font-size: 0.78rem;
          color: #fca5a5;
          text-align: center;
          line-height: 1.4;
        }}
      </style>
    </head>
    <body>
      <button id="clip-btn" class="clip-btn" onclick="copyImage()">
        <span>📋</span> Copy Image to Clipboard
      </button>
      <div id="fallback" class="fallback-note">
        ⚠️ Browser blocked clipboard access. Right-click the QR image above and choose "Copy Image".
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
            btn.innerHTML = "<span>✅</span> Copied to Clipboard!";
            btn.classList.add('success');
            setTimeout(() => {{
              btn.innerHTML = "<span>📋</span> Copy Image to Clipboard";
              btn.classList.remove('success');
            }}, 3000);
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
# SESSION STATE INITIALIZATION
# =========================================================================
DEFAULT_STATES = {
    "qr_type": QR_TYPES[0],
    # Form fields
    "url_input": "https://example.com",
    "text_input": "",
    "img_encoding_mode": "Direct Embedded Data URI (Self-Contained)",
    "img_max_dimension": 48,
    "img_quality": 65,
    "img_hosted_url": "",
    "wifi_ssid": "",
    "wifi_password": "",
    "wifi_security": "WPA/WPA2",
    "wifi_show_password": False,
    "wifi_hidden": False,
    "vcard_first_name": "",
    "vcard_last_name": "",
    "vcard_phone": "",
    "vcard_email": "",
    "vcard_company": "",
    "vcard_job_title": "",
    "vcard_website": "",
    "vcard_address": "",
    "email_to": "",
    "email_subject": "",
    "email_body": "",
    "phone_cc": "+91",
    "phone_number": "",
    "sms_number": "",
    "sms_message": "",
    "wa_cc": "+91",
    "wa_phone": "",
    "wa_message": "",
    "upi_id": "",
    "upi_name": "",
    "upi_amount": "",
    "upi_note": "",
    # Feature 1: Logo State
    "logo_bytes": None,
    "logo_filename": "",
    # Feature 2: Styling State
    "qr_style": "Rounded",
    "qr_fg_color": "#2C3480",
    "qr_bg_color": "#FFFFFF",
    "qr_box_size": 10,
    "allow_low_contrast": False,
}

for key, val in DEFAULT_STATES.items():
    if key not in st.session_state:
        st.session_state[key] = val


def clear_current_form(selected_type: str):
    """Reset form fields for the currently selected payload type."""
    if "URL" in selected_type:
        st.session_state["url_input"] = ""
    elif "Text" in selected_type:
        st.session_state["text_input"] = ""
    elif "Image" in selected_type:
        st.session_state["img_hosted_url"] = ""
    elif "Wi-Fi" in selected_type:
        st.session_state["wifi_ssid"] = ""
        st.session_state["wifi_password"] = ""
        st.session_state["wifi_security"] = "WPA/WPA2"
        st.session_state["wifi_hidden"] = False
        st.session_state["wifi_show_password"] = False
    elif "Contact" in selected_type or "vCard" in selected_type:
        for k in ["first_name", "last_name", "phone", "email", "company", "job_title", "website", "address"]:
            st.session_state[f"vcard_{k}"] = ""
    elif "Email" in selected_type:
        st.session_state["email_to"] = ""
        st.session_state["email_subject"] = ""
        st.session_state["email_body"] = ""
    elif "Phone" in selected_type:
        st.session_state["phone_number"] = ""
    elif "SMS" in selected_type:
        st.session_state["sms_number"] = ""
        st.session_state["sms_message"] = ""
    elif "WhatsApp" in selected_type:
        st.session_state["wa_phone"] = ""
        st.session_state["wa_message"] = ""
    elif "UPI" in selected_type:
        st.session_state["upi_id"] = ""
        st.session_state["upi_name"] = ""
        st.session_state["upi_amount"] = ""
        st.session_state["upi_note"] = ""


# Responsive 2-Column Studio Layout
col_form, col_stage = st.columns([1.18, 0.82], gap="large")

# =========================================================================
# LEFT COLUMN: FORMAT SELECTION, PAYLOAD DETAILS & STYLING
# =========================================================================
with col_form:
    # 1. Type Selector
    st.markdown(
        """
        <div class="step-heading">
            <span class="step-badge">STEP 1</span> Select QR Code Payload Format
        </div>
        """,
        unsafe_allow_html=True,
    )

    c_type, c_clear = st.columns([3.2, 1.2])
    with c_type:
        selected_type = st.selectbox(
            "Select QR Format",
            options=QR_TYPES,
            key="qr_type",
            label_visibility="collapsed",
            help="Choose the data schema to embed inside your QR code.",
        )
    with c_clear:
        if st.button("🧹 Clear Form", use_container_width=True, help="Reset inputs for the current format"):
            clear_current_form(selected_type)
            st.rerun()

    st.markdown("<hr>", unsafe_allow_html=True)

    # 2. Payload Details
    st.markdown(
        """
        <div class="step-heading">
            <span class="step-badge">STEP 2</span> Enter Payload Information
        </div>
        """,
        unsafe_allow_html=True,
    )

    errors = {}
    payload_data = ""
    clean_type_name = selected_type.split()[1].lower() if len(selected_type.split()) > 1 else "code"

    # ========================== 1. URL ==========================
    if "URL" in selected_type:
        st.text_input(
            "Website Destination URL *",
            key="url_input",
            placeholder="https://example.com or example.com",
            help="Full web link. Auto-prefixes https:// if missing.",
        )
        url_val = st.session_state["url_input"].strip()
        if not url_val:
            errors["url"] = "Destination URL is required."
        else:
            payload_data = build_url(url_val)

        if "url" in errors:
            render_field_error(errors["url"])

    # ========================== 2. Plain Text ==========================
    elif "Plain Text" in selected_type:
        st.text_area(
            "Message / Content (Max 500 characters) *",
            key="text_input",
            max_chars=500,
            placeholder="Type your plain text message or notes here...",
            help="Plain text encoded directly into the QR matrix.",
            height=130,
        )
        text_val = st.session_state["text_input"]
        char_count = len(text_val)
        warn_cls = "char-counter-warn" if char_count >= 500 else ""
        st.markdown(
            f'<div class="char-counter {warn_cls}">{char_count} / 500 characters</div>',
            unsafe_allow_html=True,
        )

        if not text_val.strip():
            errors["text"] = "Message text cannot be empty."
        else:
            payload_data = build_text(text_val)

        if "text" in errors:
            render_field_error(errors["text"])

    # ========================== 3. Image (Upload) ==========================
    elif "Image" in selected_type:
        st.markdown("<p style='font-weight:600; font-size:0.9rem; margin-bottom: 0.25rem;'>Upload Image File (PNG, JPG, WEBP, GIF) *</p>", unsafe_allow_html=True)
        uploaded_img_file = st.file_uploader(
            "Upload Image File",
            type=["png", "jpg", "jpeg", "webp", "gif"],
            key="image_payload_uploader",
            help="Upload an image to encode or link into your QR code.",
            label_visibility="collapsed",
        )

        if uploaded_img_file is not None:
            file_bytes = uploaded_img_file.getvalue()
            orig_size_kb = len(file_bytes) / 1024

            c_img_thumb, c_img_meta = st.columns([1, 2.2])
            with c_img_thumb:
                st.image(file_bytes, caption="Uploaded Image", width=120)
            with c_img_meta:
                st.markdown(f"**File:** `{uploaded_img_file.name}`")
                st.markdown(f"**Size:** `{orig_size_kb:.1f} KB` • **Type:** `{uploaded_img_file.type}`")

            st.markdown("<hr style='margin:0.75rem 0;'>", unsafe_allow_html=True)

            enc_mode = st.radio(
                "Image Delivery Method",
                options=["Direct Embedded Data URI (Self-Contained)", "Hosted Image URL"],
                index=0 if "Direct Embedded" in st.session_state.get("img_encoding_mode", "") else 1,
                key="img_delivery_radio",
                horizontal=True,
            )
            st.session_state["img_encoding_mode"] = enc_mode

            if "Direct Embedded" in enc_mode:
                c_dim, c_q = st.columns(2)
                with c_dim:
                    dim_choice = st.select_slider(
                        "Pixel Resolution",
                        options=[24, 32, 40, 48, 56, 64],
                        value=st.session_state.get("img_max_dimension", 48),
                        key="img_max_dimension",
                        help="Standard QR codes hold up to ~2,800 bytes.",
                    )
                with c_q:
                    q_choice = st.slider(
                        "Compression Quality",
                        min_value=40,
                        max_value=90,
                        value=st.session_state.get("img_quality", 65),
                        step=5,
                        key="img_quality",
                    )

                try:
                    data_uri = build_image_data_uri(
                        file_bytes,
                        max_dimension=dim_choice,
                        quality=q_choice,
                    )
                    uri_len = len(data_uri)
                    
                    if uri_len > 2850:
                        errors["img_size"] = f"Payload size ({uri_len} bytes) exceeds QR capacity (2,850 bytes max). Reduce pixel resolution or quality."
                        render_field_error(errors["img_size"])
                    else:
                        payload_data = data_uri
                        st.caption(f"📦 Encoded payload size: **{uri_len} bytes** (fits standard QR code)")
                except Exception as ex:
                    errors["img_process"] = f"Unable to process image: {str(ex)}"
                    render_field_error(errors["img_process"])

            else:
                st.text_input(
                    "Destination Image Web Link (Required) *",
                    key="img_hosted_url",
                    placeholder="https://example.com/uploads/photo.jpg",
                )
                img_url_val = st.session_state["img_hosted_url"].strip()
                if not img_url_val:
                    errors["img_url"] = "Hosted image link is required."
                    render_field_error(errors["img_url"])
                else:
                    payload_data = build_url(img_url_val)
        else:
            errors["image"] = "Please select and upload an image file above."
            render_field_error(errors["image"])

    # ========================== 4. Wi-Fi Network ==========================
    elif "Wi-Fi" in selected_type:
        st.text_input(
            "Network SSID Name *",
            key="wifi_ssid",
            placeholder="e.g. Cobalt_Fiber_5G",
            help="Broadcasting name of the wireless access point.",
        )
        ssid_val = st.session_state["wifi_ssid"].strip()
        if not ssid_val:
            errors["ssid"] = "Network SSID is required."
            render_field_error(errors["ssid"])

        c_sec, c_hid = st.columns([1, 1])
        with c_sec:
            st.selectbox("Encryption Standard", options=["WPA/WPA2", "WEP", "None"], key="wifi_security")
        with c_hid:
            st.write("")
            st.write("")
            st.checkbox("Hidden Network", key="wifi_hidden")

        sec_val = st.session_state["wifi_security"]
        if sec_val != "None":
            st.checkbox("Reveal Password", key="wifi_show_password")
            pass_type = "default" if st.session_state["wifi_show_password"] else "password"
            st.text_input(
                "Wi-Fi Security Password *",
                type=pass_type,
                key="wifi_password",
                placeholder="Enter Wi-Fi network key",
            )
            pass_val = st.session_state["wifi_password"]
            if not pass_val:
                errors["wifi_pass"] = "Password is required for encrypted networks."
                render_field_error(errors["wifi_pass"])
        else:
            pass_val = ""

        if not errors:
            payload_data = build_wifi(
                ssid=ssid_val,
                password=pass_val,
                security=sec_val,
                hidden=st.session_state["wifi_hidden"],
            )

    # ========================== 5. Contact Card (vCard) ==========================
    elif "Contact" in selected_type or "vCard" in selected_type:
        c1, c2 = st.columns(2)
        with c1:
            st.text_input("First Name *", key="vcard_first_name", placeholder="Ravi")
            if not st.session_state["vcard_first_name"].strip():
                errors["vcard_first_name"] = "First name is required."
                render_field_error(errors["vcard_first_name"])
        with c2:
            st.text_input("Last Name", key="vcard_last_name", placeholder="Kumar")

        c3, c4 = st.columns(2)
        with c3:
            st.text_input("Phone Number *", key="vcard_phone", placeholder="+919876543210")
            phone_val = st.session_state["vcard_phone"].strip()
            digits = re.sub(r"\D", "", phone_val)
            if not phone_val:
                errors["vcard_phone"] = "Contact phone number is required."
                render_field_error(errors["vcard_phone"])
            elif len(digits) < 10:
                errors["vcard_phone"] = "Phone number must contain at least 10 digits."
                render_field_error(errors["vcard_phone"])

        with c4:
            st.text_input("Email Address", key="vcard_email", placeholder="ravi@example.com")
            email_val = st.session_state["vcard_email"].strip()
            if email_val and not re.match(EMAIL_REGEX, email_val):
                errors["vcard_email"] = "Invalid email format."
                render_field_error(errors["vcard_email"])

        c5, c6 = st.columns(2)
        with c5:
            st.text_input("Organization / Company", key="vcard_company", placeholder="Acme Technologies")
        with c6:
            st.text_input("Designation / Job Title", key="vcard_job_title", placeholder="Technical Director")

        st.text_input("Website Portfolio Link", key="vcard_website", placeholder="https://portfolio.io")
        st.text_input("Office / Postal Address", key="vcard_address", placeholder="128 Tech Park, Bengaluru")

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

    # ========================== 6. Email ==========================
    elif "Email" in selected_type:
        st.text_input("Recipient Email Address *", key="email_to", placeholder="support@company.com")
        to_val = st.session_state["email_to"].strip()
        if not to_val:
            errors["email_to"] = "Recipient email is required."
            render_field_error(errors["email_to"])
        elif not re.match(EMAIL_REGEX, to_val):
            errors["email_to"] = "Please enter a valid recipient email (e.g. name@domain.com)."
            render_field_error(errors["email_to"])

        st.text_input("Subject Line", key="email_subject", placeholder="Product Inquiry & Support")
        st.text_area("Message Body Content", key="email_body", placeholder="Write your pre-filled email draft here...", height=110)

        if not errors:
            payload_data = build_email(
                to=to_val,
                subject=st.session_state["email_subject"],
                body=st.session_state["email_body"],
            )

    # ========================== 7. Phone Call ==========================
    elif "Phone" in selected_type:
        c_cc, c_num = st.columns([1, 2.2])
        with c_cc:
            st.selectbox("Country Code", options=["+91", "+1", "+44", "+61", "+81", "+49", "+33", "+971"], key="phone_cc")
        with c_num:
            st.text_input("Mobile / Telephone Number *", key="phone_number", placeholder="9876543210")

        num_val = st.session_state["phone_number"].strip()
        digits = re.sub(r"\D", "", num_val)
        if not num_val:
            errors["phone"] = "Phone number is required."
            render_field_error(errors["phone"])
        elif len(digits) < 10:
            errors["phone"] = "Enter a valid phone number (at least 10 digits)."
            render_field_error(errors["phone"])
        else:
            payload_data = build_phone(num_val, country_code=st.session_state["phone_cc"])

    # ========================== 8. SMS Message ==========================
    elif "SMS" in selected_type:
        st.text_input("Target Mobile Number *", key="sms_number", placeholder="+919876543210 or 9876543210")
        num_val = st.session_state["sms_number"].strip()
        digits = re.sub(r"\D", "", num_val)
        if not num_val:
            errors["sms_num"] = "Target phone number is required."
            render_field_error(errors["sms_num"])
        elif len(digits) < 10:
            errors["sms_num"] = "Enter a valid phone number (at least 10 digits)."
            render_field_error(errors["sms_num"])

        st.text_area("Pre-filled Text Message", key="sms_message", placeholder="Hello, confirming our meeting at 4 PM.", height=90)

        if not errors:
            payload_data = build_sms(num_val, message=st.session_state["sms_message"])

    # ========================== 9. WhatsApp Chat ==========================
    elif "WhatsApp" in selected_type:
        c_cc, c_num = st.columns([1, 2.2])
        with c_cc:
            st.selectbox("Country Code", options=["+91", "+1", "+44", "+61", "+81", "+49", "+971"], key="wa_cc")
        with c_num:
            st.text_input("WhatsApp Mobile Number *", key="wa_phone", placeholder="9876543210")

        num_val = st.session_state["wa_phone"].strip()
        digits = re.sub(r"\D", "", num_val)
        if not num_val:
            errors["wa_phone"] = "WhatsApp phone number is required."
            render_field_error(errors["wa_phone"])
        elif len(digits) < 10:
            errors["wa_phone"] = "Phone number must contain at least 10 digits."
            render_field_error(errors["wa_phone"])

        st.text_area("Prefilled Chat Message", key="wa_message", placeholder="Hello, I would like to inquire about...", height=90)

        if not errors:
            full_number = f"{st.session_state['wa_cc']}{num_val}"
            payload_data = build_whatsapp(full_number, message=st.session_state["wa_message"])

    # ========================== 10. UPI Payment ==========================
    elif "UPI Payment" in selected_type:
        st.text_input(
            "Merchant / Payee UPI ID (VPA) *",
            key="upi_id",
            placeholder="merchant@okhdfcbank or user@upi",
            help="Unified Payments Virtual Payment Address.",
        )
        upi_val = st.session_state["upi_id"].strip()
        if not upi_val:
            errors["upi_id"] = "UPI ID is required."
            render_field_error(errors["upi_id"])
        elif not re.match(UPI_REGEX, upi_val):
            errors["upi_id"] = "Invalid UPI format. Must follow standard pattern (e.g. name@bank)."
            render_field_error(errors["upi_id"])

        st.text_input("Payee Account Name *", key="upi_name", placeholder="Acme Official Store")
        name_val = st.session_state["upi_name"].strip()
        if not name_val:
            errors["upi_name"] = "Payee name is required."
            render_field_error(errors["upi_name"])

        c_amt, c_note = st.columns(2)
        with c_amt:
            st.text_input("Amount in INR (Optional)", key="upi_amount", placeholder="e.g. 750.00")
            amt_val = st.session_state["upi_amount"].strip()
            if amt_val:
                try:
                    val_float = float(amt_val)
                    if val_float <= 0:
                        errors["upi_amt"] = "Amount must be greater than zero."
                        render_field_error(errors["upi_amt"])
                except ValueError:
                    errors["upi_amt"] = "Amount must be a numeric value."
                    render_field_error(errors["upi_amt"])

        with c_note:
            st.text_input("Payment Note / Reference", key="upi_note", placeholder="Invoice #5021")

        if not errors:
            payload_data = build_upi(
                upi_id=upi_val,
                payee_name=name_val,
                amount=st.session_state["upi_amount"],
                note=st.session_state["upi_note"],
            )

    st.markdown("<hr>", unsafe_allow_html=True)

    # =====================================================================
    # FEATURE 1: LOGO QR SECTION
    # =====================================================================
    with st.expander("🖼️ Feature 1: Add Center Logo", expanded=bool(st.session_state.get("logo_bytes"))):
        st.caption("Upload a PNG or JPG logo (max 2 MB). Verified in memory without disk persistence.")
        logo_file = st.file_uploader(
            "Upload Logo File (PNG or JPG only)",
            type=["png", "jpg", "jpeg"],
            key="logo_uploader",
            label_visibility="collapsed",
            help="Processed completely in memory. Placed at center with white rounded backing.",
        )

        if logo_file is not None:
            is_valid_logo, logo_err, valid_bytes = validate_logo(logo_file)
            if is_valid_logo:
                st.session_state["logo_bytes"] = valid_bytes
                st.session_state["logo_filename"] = logo_file.name
            else:
                render_field_error(logo_err)

        if st.session_state.get("logo_bytes") is not None:
            c_l_prev, c_l_act = st.columns([1, 2])
            with c_l_prev:
                st.image(st.session_state["logo_bytes"], width=80, caption="Active Logo")
            with c_l_act:
                st.markdown(f"**Logo:** `{st.session_state.get('logo_filename', 'uploaded_logo')}`")
                if st.button("🗑️ Remove Logo", use_container_width=True, help="Detach logo from QR code"):
                    st.session_state["logo_bytes"] = None
                    st.session_state["logo_filename"] = ""
                    st.rerun()

            st.markdown(
                """
                <div class="info-note">
                    ℹ️ <strong>Auto-Protection Active:</strong> Error correction Level H (30% recovery) is automatically enforced to keep the QR code 100% readable with the center logo.
                </div>
                """,
                unsafe_allow_html=True,
            )

    # =====================================================================
    # FEATURE 2: STYLED QR (DOT STYLES & CONTRAST CHECK)
    # =====================================================================
    with st.expander("🎨 Feature 2: Dot Styles & Color Customization", expanded=True):
        # 1. Module Style Selector
        style_choice = st.radio(
            "Module Dot Style",
            options=["Square", "Rounded", "Circle"],
            index=["Square", "Rounded", "Circle"].index(st.session_state.get("qr_style", "Rounded")),
            horizontal=True,
            help="Choose between classic Square modules, modern Rounded corners, or elegant Circle dots.",
        )
        st.session_state["qr_style"] = style_choice

        # 2. Foreground & Background Colors
        c_col1, c_col2 = st.columns(2)
        with c_col1:
            fg_color = st.color_picker(
                "Foreground (QR Pattern)",
                value=st.session_state.get("qr_fg_color", "#2C3480"),
                help="Cobalt Blue Deep (#2C3480) or custom color.",
            )
            st.session_state["qr_fg_color"] = fg_color

        with c_col2:
            bg_color = st.color_picker(
                "Background Color",
                value=st.session_state.get("qr_bg_color", "#FFFFFF"),
                help="Background color. Default pure White (#FFFFFF).",
            )
            st.session_state["qr_bg_color"] = bg_color

        # 3. Size Slider
        box_size = st.slider(
            "Module Scale / Resolution",
            min_value=6,
            max_value=16,
            value=st.session_state.get("qr_box_size", 10),
            help="Pixel size of each individual QR matrix block.",
        )
        st.session_state["qr_box_size"] = box_size

        # 4. WCAG Contrast Check
        ratio = contrast_ratio(fg_color, bg_color)
        is_contrast_ok = ratio >= 3.0

        if is_contrast_ok:
            st.markdown(
                f'<div class="contrast-badge contrast-pass">✅ Contrast Ratio: <strong>{ratio:.1f}:1</strong> (Passes WCAG ≥ 3:1)</div>',
                unsafe_allow_html=True,
            )
            st.session_state["allow_low_contrast"] = False
        else:
            st.markdown(
                f'<div class="contrast-badge contrast-fail">⚠️ Low Contrast Ratio: <strong>{ratio:.1f}:1</strong> (&lt; 3:1 minimum)</div>',
                unsafe_allow_html=True,
            )
            st.warning("⚠️ QR may not scan reliably under different camera lenses and lighting conditions. Please choose higher contrasting colors.")
            st.session_state["allow_low_contrast"] = st.checkbox(
                "Proceed with low contrast download anyway",
                value=st.session_state.get("allow_low_contrast", False),
                help="Check to override and allow download buttons even with poor contrast.",
            )


# =========================================================================
# RIGHT COLUMN: LIVE CANVAS, CONTRAST GATING & MULTI-FORMAT EXPORT
# =========================================================================
with col_stage:
    st.markdown(
        """
        <div class="step-heading">
            <span class="step-badge">STEP 3</span> Live QR Canvas & Multi-Export
        </div>
        """,
        unsafe_allow_html=True,
    )

    is_payload_valid = len(errors) == 0 and bool(payload_data)

    if is_payload_valid:
        try:
            # Build Styled QR Image in Memory
            pil_qr_img = build_qr(
                data=payload_data,
                size=st.session_state.get("qr_box_size", 10),
                fg=st.session_state.get("qr_fg_color", "#2C3480"),
                bg=st.session_state.get("qr_bg_color", "#FFFFFF"),
                style=st.session_state.get("qr_style", "Rounded"),
                logo_bytes=st.session_state.get("logo_bytes"),
            )

            # Export PNG bytes for inline rendering
            png_bytes = to_png(pil_qr_img)
            b64_qr = base64.b64encode(png_bytes).decode("utf-8")

            logo_tag = " • 🖼️ Logo" if st.session_state.get("logo_bytes") else ""
            style_label = st.session_state.get("qr_style", "Rounded")

            # Stage Presentation Card
            st.markdown(
                f"""
                <div class="qr-stage">
                    <div class="qr-badge">✨ {selected_type.split()[0]} {style_label} Style{logo_tag}</div>
                    <div style="margin: 1.25rem 0 0.75rem 0;">
                        <div class="qr-canvas-holder">
                            <img src="data:image/png;base64,{b64_qr}" style="width: 250px; height: 250px; display: block; border-radius: 8px;" alt="Generated QR Code" />
                        </div>
                    </div>
                    <div style="font-size: 0.85rem; color: #cbd5e1; margin-bottom: 0.25rem; font-weight: 500;">
                        Scan with any smartphone camera or QR lens
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.write("")

            # Contrast Validation Check for Downloads
            can_download = is_contrast_ok or st.session_state.get("allow_low_contrast", False)

            if not can_download:
                st.info("🔒 Downloads are paused due to low color contrast (< 3:1). Adjust colors or check 'Proceed anyway' in Step 2 to enable exports.")

            # =================================================================
            # FEATURE 8: MULTI-FORMAT EXPORT (PNG, JPG, SVG, PDF)
            # =================================================================
            st.markdown("<p style='font-weight:700; font-size:0.95rem; margin-bottom:0.5rem;'>⬇️ Export Formats</p>", unsafe_allow_html=True)
            
            timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_base = f"qr_{clean_type_name}_{timestamp_str}"

            # Prepare bytes for each format
            jpg_bytes = to_jpg(pil_qr_img)
            pdf_bytes = to_pdf(pil_qr_img)
            svg_bytes = to_svg(
                payload_data,
                fg=st.session_state.get("qr_fg_color", "#2C3480"),
                bg=st.session_state.get("qr_bg_color", "#FFFFFF"),
                scale=st.session_state.get("qr_box_size", 10),
            )

            # 2x2 Download Buttons Grid
            d_col1, d_col2 = st.columns(2)
            with d_col1:
                st.download_button(
                    label="⬇️ Download PNG",
                    data=png_bytes,
                    file_name=f"{file_base}.png",
                    mime="image/png",
                    type="primary",
                    disabled=not can_download,
                    use_container_width=True,
                )
                st.download_button(
                    label="⬇️ Download SVG",
                    data=svg_bytes,
                    file_name=f"{file_base}.svg",
                    mime="image/svg+xml",
                    disabled=not can_download,
                    use_container_width=True,
                )

            with d_col2:
                st.download_button(
                    label="⬇️ Download JPG",
                    data=jpg_bytes,
                    file_name=f"{file_base}.jpg",
                    mime="image/jpeg",
                    disabled=not can_download,
                    use_container_width=True,
                )
                st.download_button(
                    label="⬇️ Download PDF",
                    data=pdf_bytes,
                    file_name=f"{file_base}.pdf",
                    mime="application/pdf",
                    disabled=not can_download,
                    use_container_width=True,
                )

            # Note for SVG export when styling or logo is applied
            if st.session_state.get("logo_bytes") is not None or st.session_state.get("qr_style") != "Square":
                st.markdown(
                    """
                    <div class="info-note" style="font-size: 0.78rem;">
                        ℹ️ <strong>SVG Note:</strong> SVG exports the clean mathematical vector QR matrix (without center logo and custom dot rounding) for optimal vector resolution in CAD/print workflows.
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            st.write("")

            # Feature 8: Copy Image to Clipboard
            render_clipboard_component(png_bytes)

            st.write("")

            # Expandable Raw Payload Inspector
            with st.expander("🔍 Inspect Raw Encoded Payload", expanded=False):
                st.code(payload_data, language="text")

        except Exception as err:
            st.error(f"Error generating styled QR code: {str(err)}")

    else:
        st.markdown(
            """
            <div class="placeholder-box">
                <div style="font-size: 2.8rem; margin-bottom: 0.75rem;">⚡</div>
                <div style="font-weight: 700; color: #FFFFFF; font-size: 1.1rem; margin-bottom: 0.35rem;">
                    Awaiting Valid Input
                </div>
                <div style="font-size: 0.85rem; color: #94a3b8; max-width: 280px; margin: 0 auto;">
                    Fill out all required fields on the left to immediately generate and preview your QR code.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
