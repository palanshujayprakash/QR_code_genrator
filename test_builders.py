"""
Test script for all QR code builder functions with sample inputs.
"""

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


def run_tests():
    print("=" * 60)
    print("QR CODE GENERATOR - FUNCTION TEST OUTPUTS")
    print("=" * 60)

    # 1. URL
    url_res = build_url("github.com/streamlit/streamlit")
    print(f"\n[1. URL]\nInput: 'github.com/streamlit/streamlit'\nOutput:\n{url_res}")

    # 2. Text
    text_res = build_text("Hello World! Antigravity QR Code test.")
    print(f"\n[2. Text]\nInput: 'Hello World! Antigravity QR Code test.'\nOutput:\n{text_res}")

    # 3. Wi-Fi
    wifi_res = build_wifi(
        ssid='MyHome"WiFi;5G',
        password="p@ss:word;123\\",
        security="WPA/WPA2",
        hidden=False,
    )
    print(f"\n[3. Wi-Fi]\nInput: SSID='MyHome\"WiFi;5G', pass='p@ss:word;123\\', sec='WPA/WPA2', hidden=False\nOutput:\n{wifi_res}")

    # 4. Contact (vCard)
    vcard_res = build_vcard(
        first_name="Ravi",
        last_name="Kumar",
        phone="+919876543210",
        email="ravi.kumar@example.com",
        company="Tech Innovations",
        job_title="Lead Architect",
        website="techinnovations.io",
        address="123 Tech Park, Bengaluru, India",
    )
    print(f"\n[4. Contact (vCard)]\nOutput:\n{vcard_res}")

    # 5. Email
    email_res = build_email(
        to="support@example.com",
        subject="Inquiry & Support",
        body="Hello team,\nI would like more info.",
    )
    print(f"\n[5. Email]\nOutput:\n{email_res}")

    # 6. Phone
    phone_res = build_phone("9876543210", country_code="+91")
    print(f"\n[6. Phone]\nInput: '9876543210', CC='+91'\nOutput:\n{phone_res}")

    # 7. SMS
    sms_res = build_sms("9876543210", message="Hey, meeting at 5 PM!")
    print(f"\n[7. SMS]\nOutput:\n{sms_res}")

    # 8. WhatsApp
    wa_res = build_whatsapp("+91 98765 43210", message="Hi! Interested in your services.")
    print(f"\n[8. WhatsApp]\nOutput:\n{wa_res}")

    # 9. UPI Payment
    upi_res = build_upi(
        upi_id="merchant@okhdfcbank",
        payee_name="Acme Store",
        amount="499.50",
        note="Order #1042",
    )
    print(f"\n[9. UPI Payment]\nOutput:\n{upi_res}")
    print("\n" + "=" * 60)
    print("ALL BUILDER TESTS COMPLETED SUCCESSFULLY!")
    print("=" * 60)


if __name__ == "__main__":
    run_tests()
