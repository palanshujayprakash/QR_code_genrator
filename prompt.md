Build the "Fill Details" step of my Streamlit QR Code Generator.

The form must change dynamically based on the selected QR type. Use st.selectbox or selectable cards for type, and st.form for details. Show a red error under any invalid field, and disable Generate until required fields are valid.

1. URL
- Fields: Website link (required)
- Validation: must start with http:// or https:// (auto-add https:// if missing)
- QR data: the link itself

2. Text
- Fields: Message (required, max 500 characters, show live counter)
- QR data: plain text

3. Wi-Fi
- Fields: Network name/SSID (required), Password (hidden input with show toggle), Security type (WPA/WPA2, WEP, None), Hidden network (checkbox)
- Validation: password required unless security is None
- QR data: WIFI:T:WPA;S:<ssid>;P:<password>;H:<true/false>;;
- Escape special characters ; , : " \ in SSID and password

4. Contact (vCard)
- Fields: First name (required), Last name, Phone (required), Email, Company, Job title, Website, Address
- Validation: valid email format, phone 10 digits (allow +country code)
- QR data: BEGIN:VCARD / VERSION:3.0 / N / FN / TEL / EMAIL / ORG / TITLE / URL / ADR / END:VCARD

5. Email
- Fields: To (required), Subject, Body
- QR data: mailto:<to>?subject=<encoded>&body=<encoded> (URL-encode subject and body)

6. Phone
- Fields: Phone number (required, with country code dropdown, default +91)
- QR data: tel:<number>

7. SMS
- Fields: Phone number (required), Message
- QR data: SMSTO:<number>:<message>

8. WhatsApp
- Fields: Phone number with country code (required), Pre-filled message
- QR data: https://wa.me/<number without + or spaces>?text=<encoded message>

9. UPI Payment
- Fields: UPI ID (required, format name@bank), Payee name (required), Amount (optional), Note (optional)
- Validation: UPI ID must match pattern like abc@okbank
- QR data: upi://pay?pa=<id>&pn=<name>&am=<amount>&cu=INR&tn=<note>

General rules:
- Use placeholders and small help text in every field (example: "9876543210")
- Keep entered values when user switches type and comes back (st.session_state)
- Add a "Clear form" button
- Show a small preview of the final encoded data in an expander ("View QR data") for debugging
- Write each type as a separate function: build_url(), build_wifi(), build_vcard() etc., returning the final string
- Add a short comment above each function explaining the format
- Test with sample inputs and show me the output of each function