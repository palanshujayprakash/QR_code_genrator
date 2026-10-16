# ⚡ Dynamic Streamlit QR Code Generator

A full-featured Streamlit application to generate, validate, customize, and store QR codes across 9 standard payload formats with SQLite history tracking and analytics.

---

## 🚀 Features

- **9 Standard Payload Formats**:
  1. **URL**: Auto-prefix `https://` if missing.
  2. **Plain Text**: Up to 500 characters with live character counter.
  3. **Wi-Fi**: SSID, password toggle, WPA/WPA2/WEP/None security, hidden network support, and character escaping.
  4. **Contact (vCard 3.0)**: Multi-field contact card (Name, Phone, Email, Company, Job Title, Address).
  5. **Email**: Pre-filled `mailto` action with subject and body encoding.
  6. **Phone**: Direct telephone dialing with country code selector.
  7. **SMS**: Direct SMS messaging with pre-filled message text.
  8. **WhatsApp**: `wa.me` instant chat deep-link with URL-encoded message.
  9. **UPI Payment**: Unified Payments Interface deep-link for instant Indian payments.
- **Dynamic Live Validation**:
  - Live field format validation (email, phone, UPI VPA).
  - Red field error prompts under invalid inputs.
  - Generate button stays disabled until all required inputs are valid.
- **Session State Persistence**:
  - Retains all form inputs across type switches.
  - Dedicated "Clear Form" button per type.
- **SQLite Database History & Analytics**:
  - Automatically records generated QR codes (ID, Type, Label, Payload, Image, Timestamp).
  - Total count and category breakdown metrics.
  - Open and inspect past QR codes anytime with one-click download or deletion.

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
