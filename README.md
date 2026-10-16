# ⚡ Dynamic Streamlit QR Code Generator

A full-featured Streamlit application to generate, validate, and customize QR codes across 10 standard payload formats with live validation, image embedding, center logo overlays, and instant download.

---

## 🚀 Features

- **10 Standard Payload Formats**:
  1. **URL**: Auto-prefix `https://` if missing.
  2. **Plain Text**: Up to 500 characters with live character counter.
  3. **Image (Upload)**: Embed compact self-contained images (Data URI WebP/PNG) or direct hosted image URLs.
  4. **Wi-Fi**: SSID, password toggle, WPA/WPA2/WEP/None security, hidden network support, and character escaping.
  5. **Contact (vCard 3.0)**: Multi-field contact card (Name, Phone, Email, Company, Job Title, Address).
  6. **Email**: Pre-filled `mailto` action with subject and body encoding.
  7. **Phone**: Direct telephone dialing with country code selector.
  8. **SMS**: Direct SMS messaging with pre-filled message text.
  9. **WhatsApp**: `wa.me` instant chat deep-link with URL-encoded message.
  10. **UPI Payment**: Unified Payments Interface deep-link for instant Indian payments.
- **Design & Customization**:
  - High-end dark theme using **Black (`#000000`)**, **White (`#FFFFFF`)**, and **Cobalt Blue Deep (`#2C3480`)**.
  - Customizable QR fill color (Cobalt Blue Deep `#2C3480` vs. Classic Black `#000000`).
  - Optional **Center Logo / Avatar Overlay** embedding on any generated QR code.
- **Dynamic Live Validation**:
  - Live field format validation (email, phone, UPI VPA, payload size limits).
  - Red field error prompts under invalid inputs.
  - Interactive preview card updates in real time.
- **Session State Persistence**:
  - Retains form inputs across format switches.
  - Dedicated "Clear Form" button per type.

---

## 🛠️ Installation & Setup

```bash
# Clone the repository
git clone https://github.com/palanshujayprakash/QR_code_genrator.git
cd QR_code_genrator

# Install dependencies
pip install -r requirements.txt

# Launch the Streamlit application
streamlit run app.py
```
