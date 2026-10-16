"""
QR Code Builders
Pure Python functions to construct standardized QR data strings for various payload types.
"""

import re
import urllib.parse
from typing import Optional


# 1. URL Format: Direct web link (starts with http:// or https://)
def build_url(url: str) -> str:
    """Build standard URL string, auto-prefixing https:// if missing."""
    clean_url = url.strip()
    if not clean_url:
        return ""
    if not re.match(r"^https?://", clean_url, re.IGNORECASE):
        clean_url = f"https://{clean_url}"
    return clean_url


# 2. Text Format: Plain text message
def build_text(message: str) -> str:
    """Build plain text payload."""
    return message


# 3. Wi-Fi Format: WIFI:T:<security>;S:<ssid>;P:<password>;H:<hidden>;;
def build_wifi(
    ssid: str,
    password: str = "",
    security: str = "WPA/WPA2",
    hidden: bool = False,
) -> str:
    """Build Wi-Fi configuration string escaping special characters (; , : " \\)."""
    def escape_wifi(val: str) -> str:
        # Escape order: backslash first, then others
        val = val.replace("\\", "\\\\")
        for ch in [";", ",", ":", '"']:
            val = val.replace(ch, f"\\{ch}")
        return val

    # Map security type to standard spec
    sec_map = {
        "WPA/WPA2": "WPA",
        "WPA": "WPA",
        "WEP": "WEP",
        "None": "nopass",
        "nopass": "nopass",
    }
    sec_type = sec_map.get(security, "WPA")
    escaped_ssid = escape_wifi(ssid.strip())
    escaped_pass = escape_wifi(password) if sec_type != "nopass" else ""
    hidden_str = "true" if hidden else "false"

    return f"WIFI:T:{sec_type};S:{escaped_ssid};P:{escaped_pass};H:{hidden_str};;"


# 4. Contact (vCard 3.0) Format: Standard multi-line vCard
def build_vcard(
    first_name: str,
    last_name: str = "",
    phone: str = "",
    email: str = "",
    company: str = "",
    job_title: str = "",
    website: str = "",
    address: str = "",
) -> str:
    """Build vCard 3.0 string with personal and professional details."""
    fn_parts = [p for p in [first_name.strip(), last_name.strip()] if p]
    full_name = " ".join(fn_parts)
    
    lines = [
        "BEGIN:VCARD",
        "VERSION:3.0",
        f"N:{last_name.strip()};{first_name.strip()};;;",
        f"FN:{full_name}",
    ]
    if company.strip():
        lines.append(f"ORG:{company.strip()}")
    if job_title.strip():
        lines.append(f"TITLE:{job_title.strip()}")
    if phone.strip():
        lines.append(f"TEL;TYPE=CELL:{phone.strip()}")
    if email.strip():
        lines.append(f"EMAIL:{email.strip()}")
    if website.strip():
        clean_site = build_url(website)
        lines.append(f"URL:{clean_site}")
    if address.strip():
        # ADR format: ;;street;city;state;zip;country
        clean_adr = address.strip().replace(";", " ")
        lines.append(f"ADR:;;{clean_adr};;;;")
    lines.append("END:VCARD")
    return "\n".join(lines)


# 5. Email Format: mailto:<to>?subject=<encoded>&body=<encoded>
def build_email(to: str, subject: str = "", body: str = "") -> str:
    """Build mailto link with URL-encoded query parameters."""
    clean_to = to.strip()
    params = {}
    if subject.strip():
        params["subject"] = subject.strip()
    if body.strip():
        params["body"] = body.strip()
    
    if params:
        query_string = urllib.parse.urlencode(params, quote_via=urllib.parse.quote)
        return f"mailto:{clean_to}?{query_string}"
    return f"mailto:{clean_to}"


# 6. Phone Format: tel:<number>
def build_phone(number: str, country_code: str = "+91") -> str:
    """Build telephone URI with country code."""
    num = re.sub(r"[^\d+]", "", number)
    if country_code and not num.startswith("+"):
        cc = country_code if country_code.startswith("+") else f"+{country_code}"
        num = f"{cc}{num}"
    return f"tel:{num}"


# 7. SMS Format: SMSTO:<number>:<message>
def build_sms(number: str, message: str = "") -> str:
    """Build SMS URI for direct messaging."""
    clean_num = re.sub(r"[^\d+]", "", number)
    return f"SMSTO:{clean_num}:{message.strip()}"


# 8. WhatsApp Format: https://wa.me/<number>?text=<encoded>
def build_whatsapp(phone: str, message: str = "") -> str:
    """Build WhatsApp click-to-chat URL with digits-only phone and encoded text."""
    # wa.me requires phone number without '+', spaces, or dashes
    clean_num = re.sub(r"\D", "", phone)
    encoded_msg = urllib.parse.quote(message.strip()) if message.strip() else ""
    if encoded_msg:
        return f"https://wa.me/{clean_num}?text={encoded_msg}"
    return f"https://wa.me/{clean_num}"


# 9. UPI Format: upi://pay?pa=<id>&pn=<name>&am=<amount>&cu=INR&tn=<note>
def build_upi(
    upi_id: str,
    payee_name: str,
    amount: Optional[str] = "",
    note: Optional[str] = "",
) -> str:
    """Build standard Unified Payments Interface (UPI) deep-link URI."""
    params = [
        ("pa", upi_id.strip()),
        ("pn", payee_name.strip()),
    ]
    if amount and str(amount).strip():
        try:
            amt_float = float(str(amount).strip())
            params.append(("am", f"{amt_float:.2f}"))
        except ValueError:
            params.append(("am", str(amount).strip()))
    
    params.append(("cu", "INR"))
    
    if note and str(note).strip():
        params.append(("tn", str(note).strip()))
    
    query_string = urllib.parse.urlencode(params, quote_via=urllib.parse.quote)
    return f"upi://pay?{query_string}"
