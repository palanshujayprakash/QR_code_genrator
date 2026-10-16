"""
Streamlit QR Code Generator - Dynamic Form, Live Validation & Database History
"""

import io
import re
import streamlit as st
import qrcode
from PIL import Image

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
)
import database

# Initialize Database
database.init_db()

# Page Configuration
st.set_page_config(
    page_title="QR Code Generator with History",
    page_icon="⚡",
    layout="centered",
)

# Custom Styling for error badges, counters, and cards
st.markdown(
    """
    <style>
    .field-error {
        color: #ef4444;
        font-size: 0.85rem;
        margin-top: -0.6rem;
        margin-bottom: 0.5rem;
        font-weight: 500;
        display: flex;
        align-items: center;
        gap: 4px;
    }
    .char-counter {
        font-size: 0.82rem;
        color: #64748b;
        text-align: right;
        margin-top: -0.6rem;
        margin-bottom: 0.5rem;
    }
    .char-counter-warn {
        color: #ef4444 !important;
        font-weight: 600;
    }
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
    }
    .section-title {
        font-size: 1.25rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    .history-card {
        padding: 1rem;
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        background: rgba(255, 255, 255, 0.03);
        margin-bottom: 0.8rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Types available
QR_TYPES = [
    "🌐 URL",
    "📝 Text",
    "📶 Wi-Fi",
    "👤 Contact (vCard)",
    "✉️ Email",
    "📞 Phone",
    "💬 SMS",
    "🟢 WhatsApp",
    "💳 UPI Payment",
]

# Validation Helpers
EMAIL_REGEX = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
UPI_REGEX = r"^[\w.-]+@[\w.-]+$"

def render_field_error(msg: str):
    st.markdown(f'<div class="field-error">⚠️ {msg}</div>', unsafe_allow_html=True)


# Initialize Session State Keys
DEFAULT_STATES = {
    "qr_type": QR_TYPES[0],
    # URL
    "url_input": "https://example.com",
    # Text
    "text_input": "",
    # Wi-Fi
    "wifi_ssid": "",
    "wifi_password": "",
    "wifi_security": "WPA/WPA2",
    "wifi_show_password": False,
    "wifi_hidden": False,
    # vCard
    "vcard_first_name": "",
    "vcard_last_name": "",
    "vcard_phone": "",
    "vcard_email": "",
    "vcard_company": "",
    "vcard_job_title": "",
    "vcard_website": "",
    "vcard_address": "",
    # Email
    "email_to": "",
    "email_subject": "",
    "email_body": "",
    # Phone
    "phone_cc": "+91",
    "phone_number": "",
    # SMS
    "sms_number": "",
    "sms_message": "",
    # WhatsApp
    "wa_cc": "+91",
    "wa_phone": "",
    "wa_message": "",
    # UPI
    "upi_id": "",
    "upi_name": "",
    "upi_amount": "",
    "upi_note": "",
    # Active viewed QR from history
    "active_history_id": None,
}

for key, val in DEFAULT_STATES.items():
    if key not in st.session_state:
        st.session_state[key] = val


def clear_current_form(selected_type: str):
    """Reset form fields for the currently selected type."""
    if "URL" in selected_type:
        st.session_state["url_input"] = ""
    elif "Text" in selected_type:
        st.session_state["text_input"] = ""
    elif "Wi-Fi" in selected_type:
        st.session_state["wifi_ssid"] = ""
        st.session_state["wifi_password"] = ""
        st.session_state["wifi_security"] = "WPA/WPA2"
        st.session_state["wifi_hidden"] = False
        st.session_state["wifi_show_password"] = False
    elif "vCard" in selected_type:
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


# Header
st.title("⚡ QR Code Generator")
st.caption("Generate dynamic QR codes & track all generated QR codes in database history.")

# Main Navigation Tabs
tab_create, tab_history = st.tabs(["✨ Generate New QR", "📚 Saved Database History & Stats"])

with tab_create:
    st.subheader("1. Choose QR Code Type")
    selected_type = st.selectbox(
        "Select QR Type",
        options=QR_TYPES,
        key="qr_type",
        help="Choose the type of data to encode into the QR code.",
        label_visibility="collapsed",
    )

    # Clear Form Action
    col_type_hdr, col_clear = st.columns([3, 1])
    with col_clear:
        if st.button("🧹 Clear Form", use_container_width=True, help="Clear inputs for current type"):
            clear_current_form(selected_type)
            st.rerun()

    st.markdown("---")
    st.markdown('<div class="section-title">2. Enter Payload Details</div>', unsafe_allow_html=True)

    # Dynamic Field Rendering & Validation State
    errors = {}
    payload_data = ""
    entry_label = ""

    # ========================== 1. URL ==========================
    if "URL" in selected_type:
        st.text_input(
            "Website Link (Required)",
            key="url_input",
            placeholder="https://example.com or example.com",
            help="Full web link. Auto-prefixes https:// if missing.",
        )
        url_val = st.session_state["url_input"].strip()
        if not url_val:
            errors["url"] = "Website link is required."
        else:
            payload_data = build_url(url_val)
            entry_label = payload_data

        if "url" in errors:
            render_field_error(errors["url"])

    # ========================== 2. Text ==========================
    elif "Text" in selected_type:
        st.text_area(
            "Message (Required)",
            key="text_input",
            max_chars=500,
            placeholder="Enter plain text message up to 500 characters...",
            help="Plain text encoded directly into the QR code.",
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
            errors["text"] = "Message text is required."
        else:
            payload_data = build_text(text_val)
            entry_label = text_val[:40] + ("..." if len(text_val) > 40 else "")

        if "text" in errors:
            render_field_error(errors["text"])

    # ========================== 3. Wi-Fi ==========================
    elif "Wi-Fi" in selected_type:
        st.text_input(
            "Network Name / SSID (Required)",
            key="wifi_ssid",
            placeholder="e.g. Office_WiFi_5G",
            help="SSID of the wireless network.",
        )
        ssid_val = st.session_state["wifi_ssid"].strip()
        if not ssid_val:
            errors["ssid"] = "Network SSID is required."
            render_field_error(errors["ssid"])

        c_sec, c_hid = st.columns([1, 1])
        with c_sec:
            st.selectbox(
                "Security Type",
                options=["WPA/WPA2", "WEP", "None"],
                key="wifi_security",
                help="Encryption standard used by the router.",
            )
        with c_hid:
            st.checkbox(
                "Hidden Network",
                key="wifi_hidden",
                help="Check if this SSID does not broadcast publicly.",
            )

        sec_val = st.session_state["wifi_security"]
        if sec_val != "None":
            st.checkbox("Show Password", key="wifi_show_password")
            pass_type = "default" if st.session_state["wifi_show_password"] else "password"
            st.text_input(
                "Network Password (Required)",
                type=pass_type,
                key="wifi_password",
                placeholder="Enter Wi-Fi password",
                help="Password is required unless security is set to None.",
            )
            pass_val = st.session_state["wifi_password"]
            if not pass_val:
                errors["wifi_pass"] = "Password is required for secured networks."
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
            entry_label = f"SSID: {ssid_val} ({sec_val})"

    # ========================== 4. Contact (vCard) ==========================
    elif "Contact (vCard)" in selected_type:
        c1, c2 = st.columns(2)
        with c1:
            st.text_input("First Name (Required)", key="vcard_first_name", placeholder="Ravi")
            if not st.session_state["vcard_first_name"].strip():
                errors["vcard_first_name"] = "First name is required."
                render_field_error(errors["vcard_first_name"])
        with c2:
            st.text_input("Last Name", key="vcard_last_name", placeholder="Kumar")

        c3, c4 = st.columns(2)
        with c3:
            st.text_input("Phone Number (Required)", key="vcard_phone", placeholder="+919876543210")
            phone_val = st.session_state["vcard_phone"].strip()
            digits = re.sub(r"\D", "", phone_val)
            if not phone_val:
                errors["vcard_phone"] = "Phone number is required."
                render_field_error(errors["vcard_phone"])
            elif len(digits) < 10:
                errors["vcard_phone"] = "Phone number must have at least 10 digits."
                render_field_error(errors["vcard_phone"])

        with c4:
            st.text_input("Email Address", key="vcard_email", placeholder="ravi@example.com")
            email_val = st.session_state["vcard_email"].strip()
            if email_val and not re.match(EMAIL_REGEX, email_val):
                errors["vcard_email"] = "Invalid email format."
                render_field_error(errors["vcard_email"])

        c5, c6 = st.columns(2)
        with c5:
            st.text_input("Company / Organization", key="vcard_company", placeholder="Acme Corp")
        with c6:
            st.text_input("Job Title", key="vcard_job_title", placeholder="Product Manager")

        st.text_input("Website", key="vcard_website", placeholder="https://myportfolio.io")
        st.text_input("Address", key="vcard_address", placeholder="Suite 400, MG Road, Bengaluru")

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
            full_n = f"{st.session_state['vcard_first_name']} {st.session_state['vcard_last_name']}".strip()
            entry_label = f"Contact: {full_n} ({phone_val})"

    # ========================== 5. Email ==========================
    elif "Email" in selected_type:
        st.text_input(
            "To Email (Required)",
            key="email_to",
            placeholder="recipient@example.com",
            help="Recipient email address.",
        )
        to_val = st.session_state["email_to"].strip()
        if not to_val:
            errors["email_to"] = "Recipient email is required."
            render_field_error(errors["email_to"])
        elif not re.match(EMAIL_REGEX, to_val):
            errors["email_to"] = "Please enter a valid email address (e.g. user@domain.com)."
            render_field_error(errors["email_to"])

        st.text_input("Subject", key="email_subject", placeholder="Meeting Agenda & Details")
        st.text_area("Body", key="email_body", placeholder="Write message body here...", height=100)

        if not errors:
            payload_data = build_email(
                to=to_val,
                subject=st.session_state["email_subject"],
                body=st.session_state["email_body"],
            )
            entry_label = f"Email to: {to_val}"

    # ========================== 6. Phone ==========================
    elif "Phone" in selected_type:
        c_cc, c_num = st.columns([1, 2])
        with c_cc:
            st.selectbox("Country Code", options=["+91", "+1", "+44", "+61", "+81", "+49", "+33"], key="phone_cc")
        with c_num:
            st.text_input("Phone Number (Required)", key="phone_number", placeholder="9876543210")

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
            entry_label = f"Call: {st.session_state['phone_cc']} {num_val}"

    # ========================== 7. SMS ==========================
    elif "SMS" in selected_type:
        st.text_input("Phone Number (Required)", key="sms_number", placeholder="+919876543210 or 9876543210")
        num_val = st.session_state["sms_number"].strip()
        digits = re.sub(r"\D", "", num_val)
        if not num_val:
            errors["sms_num"] = "Phone number is required."
            render_field_error(errors["sms_num"])
        elif len(digits) < 10:
            errors["sms_num"] = "Enter a valid phone number (at least 10 digits)."
            render_field_error(errors["sms_num"])

        st.text_area("Pre-filled Message", key="sms_message", placeholder="Hello, see you at 5 PM!", height=90)

        if not errors:
            payload_data = build_sms(num_val, message=st.session_state["sms_message"])
            entry_label = f"SMS to: {num_val}"

    # ========================== 8. WhatsApp ==========================
    elif "WhatsApp" in selected_type:
        c_cc, c_num = st.columns([1, 2])
        with c_cc:
            st.selectbox("Country Code", options=["+91", "+1", "+44", "+61", "+81", "+49"], key="wa_cc")
        with c_num:
            st.text_input("Phone Number (Required)", key="wa_phone", placeholder="9876543210")

        num_val = st.session_state["wa_phone"].strip()
        digits = re.sub(r"\D", "", num_val)
        if not num_val:
            errors["wa_phone"] = "WhatsApp phone number is required."
            render_field_error(errors["wa_phone"])
        elif len(digits) < 10:
            errors["wa_phone"] = "Phone number must have at least 10 digits."
            render_field_error(errors["wa_phone"])

        st.text_area("Pre-filled Message", key="wa_message", placeholder="Hi! I would like to know more about...", height=90)

        if not errors:
            full_number = f"{st.session_state['wa_cc']}{num_val}"
            payload_data = build_whatsapp(full_number, message=st.session_state["wa_message"])
            entry_label = f"WA: {full_number}"

    # ========================== 9. UPI Payment ==========================
    elif "UPI Payment" in selected_type:
        st.text_input(
            "UPI ID (Required)",
            key="upi_id",
            placeholder="merchant@okhdfcbank or john@upi",
            help="VPA in format name@bank",
        )
        upi_val = st.session_state["upi_id"].strip()
        if not upi_val:
            errors["upi_id"] = "UPI ID is required."
            render_field_error(errors["upi_id"])
        elif not re.match(UPI_REGEX, upi_val):
            errors["upi_id"] = "Invalid UPI format. Must match pattern like username@bank."
            render_field_error(errors["upi_id"])

        st.text_input("Payee Name (Required)", key="upi_name", placeholder="Acme Store")
        name_val = st.session_state["upi_name"].strip()
        if not name_val:
            errors["upi_name"] = "Payee name is required."
            render_field_error(errors["upi_name"])

        c_amt, c_note = st.columns(2)
        with c_amt:
            st.text_input("Amount (Optional)", key="upi_amount", placeholder="e.g. 499.00")
            amt_val = st.session_state["upi_amount"].strip()
            if amt_val:
                try:
                    val_float = float(amt_val)
                    if val_float <= 0:
                        errors["upi_amt"] = "Amount must be positive."
                        render_field_error(errors["upi_amt"])
                except ValueError:
                    errors["upi_amt"] = "Amount must be a valid number."
                    render_field_error(errors["upi_amt"])

        with c_note:
            st.text_input("Note / Description (Optional)", key="upi_note", placeholder="Order #1042")

        if not errors:
            payload_data = build_upi(
                upi_id=upi_val,
                payee_name=name_val,
                amount=st.session_state["upi_amount"],
                note=st.session_state["upi_note"],
            )
            amt_disp = f" ₹{amt_val}" if amt_val else ""
            entry_label = f"UPI: {name_val} ({upi_val}){amt_disp}"

    # Generate Button
    is_valid = len(errors) == 0 and bool(payload_data)

    st.write("")
    gen_btn = st.button(
        "⚡ Generate & Save QR Code",
        type="primary",
        disabled=not is_valid,
        use_container_width=True,
    )

    if not is_valid:
        st.caption("🔒 Complete all required fields above without errors to generate.")

    # 3. Live Output & QR Preview
    st.markdown("---")
    st.subheader("3. Live Output & QR Preview")

    # Expander for Debugging Preview
    with st.expander("🔍 View QR Data (Raw Payload)", expanded=True):
        if payload_data:
            st.code(payload_data, language="text")
        else:
            st.info("Fill out the required fields above to inspect raw QR payload.")

    if payload_data and is_valid:
        # Generate QR Image
        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=10,
            border=4,
        )
        qr.add_data(payload_data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="#1e293b", back_color="#ffffff")

        buf = io.BytesIO()
        img.save(buf, format="PNG")
        byte_im = buf.getvalue()

        # Handle Save to DB when Generate button clicked
        if gen_btn:
            new_id = database.save_qr(
                qr_type=selected_type,
                label=entry_label,
                payload=payload_data,
                image_blob=byte_im,
            )
            st.success(f"✅ QR Code saved to database successfully! (ID: #{new_id})")

        c_img, _ = st.columns([1, 1])
        with c_img:
            st.image(byte_im, caption="Generated QR Code", width=300)

            st.download_button(
                label="⬇️ Download QR Code (PNG)",
                data=byte_im,
                file_name=f"qr_{selected_type.split()[1].lower()}.png",
                mime="image/png",
                use_container_width=True,
            )
    else:
        st.warning("Awaiting valid input to generate QR code.")


# =========================================================================
# TAB 2: DATABASE HISTORY & ANALYTICS
# =========================================================================
with tab_history:
    st.subheader("📊 Database Analytics")
    stats = database.get_qr_stats()
    total_qrs = stats["total"]

    # Metrics
    m1, m2 = st.columns([1, 2])
    with m1:
        st.metric(label="Total QR Codes Generated", value=total_qrs)
    with m2:
        if stats["by_type"]:
            # Display breakdown by type as small chips
            chips_text = " • ".join([f"**{k}**: {v}" for k, v in stats["by_type"].items()])
            st.write("**Breakdown by Type:**")
            st.markdown(chips_text)
        else:
            st.info("No QR codes saved yet.")

    st.markdown("---")

    # Filter & Actions Row
    all_qrs = database.get_all_qrs()
    if all_qrs:
        c_filter, c_clear_all = st.columns([3, 1])
        with c_filter:
            filter_type = st.selectbox(
                "Filter by Type",
                options=["All Types"] + QR_TYPES,
                index=0,
            )
        with c_clear_all:
            st.write("")
            st.write("")
            if st.button("🗑️ Clear Entire History", help="Delete all records"):
                database.clear_all_history()
                st.session_state["active_history_id"] = None
                st.rerun()

        # Filtered results
        filtered_qrs = (
            all_qrs if filter_type == "All Types"
            else [r for r in all_qrs if r["qr_type"] == filter_type]
        )

        st.caption(f"Showing {len(filtered_qrs)} record(s)")

        # Modal/Viewer if an item is selected to open
        if st.session_state.get("active_history_id"):
            active_qr = database.get_qr_by_id(st.session_state["active_history_id"])
            if active_qr:
                st.markdown("---")
                st.markdown(f"### 🔍 Opened QR: #{active_qr['id']} — {active_qr['label']}")
                c_act_img, c_act_meta = st.columns([1, 1.2])
                with c_act_img:
                    st.image(active_qr["image_blob"], caption=f"Created: {active_qr['created_at']}", width=250)
                    st.download_button(
                        label="⬇️ Download This QR",
                        data=active_qr["image_blob"],
                        file_name=f"qr_history_{active_qr['id']}.png",
                        mime="image/png",
                        use_container_width=True,
                    )
                with c_act_meta:
                    st.write(f"**Type:** {active_qr['qr_type']}")
                    st.write(f"**Created At:** {active_qr['created_at']}")
                    st.write("**Encoded Raw Payload:**")
                    st.code(active_qr["payload"], language="text")
                    if st.button("❌ Close Preview"):
                        st.session_state["active_history_id"] = None
                        st.rerun()
                st.markdown("---")

        # History Records List
        for row in filtered_qrs:
            with st.container():
                st.markdown('<div class="history-card">', unsafe_allow_html=True)
                col_info, col_open, col_del = st.columns([4, 1.2, 0.8])

                with col_info:
                    st.markdown(f"**{row['qr_type']}** | `{row['label']}`")
                    st.caption(f"🕒 Created: {row['created_at']} • ID: #{row['id']}")

                with col_open:
                    if st.button("👁️ Open", key=f"open_{row['id']}", use_container_width=True):
                        st.session_state["active_history_id"] = row["id"]
                        st.rerun()

                with col_del:
                    if st.button("🗑️", key=f"del_{row['id']}", help="Delete this entry", use_container_width=True):
                        database.delete_qr(row["id"])
                        if st.session_state.get("active_history_id") == row["id"]:
                            st.session_state["active_history_id"] = None
                        st.rerun()

                st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("No generated QR codes in database yet. Generate a QR code in the first tab to see it here!")
