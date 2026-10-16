"""
Pytest suite for QR Code Studio Phase 1 features:
1. Contrast ratio calculations (standard high contrast, low contrast warnings).
2. Logo validation (valid PNG/JPG, oversized > 2MB, fake/corrupted images, empty files).
3. Exporter functions (to_png, to_jpg, to_pdf, to_svg return valid non-empty byte streams).
4. QR Builder styling (Square, Rounded, Circle module drawers and logo compositing).
"""

import io
import pytest
from PIL import Image

from utils.validators import (
    contrast_ratio,
    validate_logo,
    hex_to_rgb,
    MAX_LOGO_SIZE_BYTES,
)
from utils.qr_builder import build_qr
from utils.exporter import to_png, to_jpg, to_pdf, to_svg


# =========================================================================
# 1. CONTRAST RATIO TESTS
# =========================================================================
class TestContrastRatio:
    def test_standard_high_contrast(self):
        """Black vs White should yield the maximum WCAG contrast ratio of 21.0:1."""
        ratio_bw = contrast_ratio("#000000", "#FFFFFF")
        assert pytest.approx(ratio_bw, 0.1) == 21.0

        # Cobalt Blue Deep (#2C3480) on White (#FFFFFF) is well above the 3:1 threshold
        ratio_cobalt_white = contrast_ratio("#2C3480", "#FFFFFF")
        assert ratio_cobalt_white >= 10.0
        assert ratio_cobalt_white > 3.0

    def test_low_contrast_warning_range(self):
        """Low contrast combinations (below 3:1) should be accurately identified."""
        # Cobalt Blue Deep on pure Black has very low contrast (~1.9:1)
        ratio_cobalt_black = contrast_ratio("#2C3480", "#000000")
        assert ratio_cobalt_black < 3.0

        # Similar grays
        ratio_similar_gray = contrast_ratio("#777777", "#888888")
        assert ratio_similar_gray < 3.0

    def test_hex_conversion(self):
        """Verify hex to RGB parsing."""
        assert hex_to_rgb("#2C3480") == (44, 52, 128)
        assert hex_to_rgb("#FFFFFF") == (255, 255, 255)
        assert hex_to_rgb("#000") == (0, 0, 0)

        with pytest.raises(ValueError):
            hex_to_rgb("invalid_hex")


# =========================================================================
# 2. LOGO VALIDATION TESTS
# =========================================================================
class TestLogoValidation:
    def _create_sample_image_bytes(self, fmt="PNG", size=(50, 50), color="blue") -> bytes:
        img = Image.new("RGB", size, color=color)
        buf = io.BytesIO()
        img.save(buf, format=fmt)
        return buf.getvalue()

    def test_valid_png_logo(self):
        """Valid PNG image bytes should pass validation."""
        valid_bytes = self._create_sample_image_bytes("PNG")
        is_valid, msg, out_bytes = validate_logo(valid_bytes)
        assert is_valid is True
        assert msg == ""
        assert len(out_bytes) > 0

    def test_valid_jpeg_logo(self):
        """Valid JPEG image bytes should pass validation."""
        valid_bytes = self._create_sample_image_bytes("JPEG")
        is_valid, msg, out_bytes = validate_logo(valid_bytes)
        assert is_valid is True
        assert msg == ""
        assert len(out_bytes) > 0

    def test_oversized_logo(self):
        """Files exceeding 2 MB must fail validation with a friendly error message."""
        # Create dummy buffer exceeding 2 MB limit
        oversized_data = b"x" * (MAX_LOGO_SIZE_BYTES + 1024)
        is_valid, msg, out_bytes = validate_logo(oversized_data)
        assert is_valid is False
        assert "exceeds maximum allowed limit of 2 MB" in msg
        assert len(out_bytes) == 0

    def test_fake_or_corrupted_image(self):
        """Corrupted or non-image files must fail verification in memory."""
        fake_bytes = b"This is a text file renamed to logo.png"
        is_valid, msg, out_bytes = validate_logo(fake_bytes)
        assert is_valid is False
        assert "Corrupted or invalid image file" in msg

    def test_empty_file(self):
        """Empty uploads should fail with a friendly prompt."""
        is_valid, msg, out_bytes = validate_logo(b"")
        assert is_valid is False
        assert "empty" in msg

    def test_none_input(self):
        """None input should be handled gracefully."""
        is_valid, msg, out_bytes = validate_logo(None)
        assert is_valid is False
        assert "No file" in msg


# =========================================================================
# 3. EXPORTER TESTS
# =========================================================================
class TestExporters:
    @pytest.fixture
    def sample_qr_image(self) -> Image.Image:
        return build_qr("https://github.com", size=8, fg="#2C3480", bg="#FFFFFF", style="Square")

    def test_to_png_returns_non_empty_bytes(self, sample_qr_image):
        """to_png must return valid PNG bytes starting with the PNG magic header."""
        png_bytes = to_png(sample_qr_image)
        assert isinstance(png_bytes, bytes)
        assert len(png_bytes) > 0
        assert png_bytes.startswith(b"\x89PNG")

    def test_to_jpg_returns_non_empty_bytes(self, sample_qr_image):
        """to_jpg must return valid JPEG bytes starting with the JPEG magic marker."""
        jpg_bytes = to_jpg(sample_qr_image)
        assert isinstance(jpg_bytes, bytes)
        assert len(jpg_bytes) > 0
        assert jpg_bytes.startswith(b"\xff\xd8")

    def test_to_pdf_returns_non_empty_bytes(self, sample_qr_image):
        """to_pdf must return valid PDF bytes starting with the %PDF header."""
        pdf_bytes = to_pdf(sample_qr_image)
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
        assert pdf_bytes.startswith(b"%PDF")

    def test_to_svg_returns_non_empty_bytes(self):
        """to_svg must return valid SVG bytes containing svg markup."""
        svg_bytes = to_svg("https://example.com", fg="#2C3480", bg="#FFFFFF", scale=10)
        assert isinstance(svg_bytes, bytes)
        assert len(svg_bytes) > 0
        assert b"<svg" in svg_bytes


# =========================================================================
# 4. QR BUILDER STYLES & LOGO TESTS
# =========================================================================
class TestQRBuilder:
    def test_build_qr_square_style(self):
        """Build standard square module QR code."""
        img = build_qr("Test Square", style="Square", fg="#2C3480", bg="#FFFFFF")
        assert isinstance(img, Image.Image)
        assert img.size[0] > 100

    def test_build_qr_rounded_style(self):
        """Build rounded module QR code."""
        img = build_qr("Test Rounded", style="Rounded", fg="#2C3480", bg="#FFFFFF")
        assert isinstance(img, Image.Image)
        assert img.size[0] > 100

    def test_build_qr_circle_style(self):
        """Build circle module QR code."""
        img = build_qr("Test Circle", style="Circle", fg="#2C3480", bg="#FFFFFF")
        assert isinstance(img, Image.Image)
        assert img.size[0] > 100

    def test_build_qr_with_logo_overlay(self):
        """Build QR code with center logo overlay."""
        logo_img = Image.new("RGB", (60, 60), color="red")
        buf = io.BytesIO()
        logo_img.save(buf, format="PNG")
        logo_bytes = buf.getvalue()

        img = build_qr(
            "https://antigravity.ai",
            style="Rounded",
            fg="#2C3480",
            bg="#FFFFFF",
            logo_bytes=logo_bytes,
        )
        assert isinstance(img, Image.Image)
        assert img.mode in ("RGBA", "RGB")
        assert img.size[0] > 100

    def test_empty_payload_raises_error(self):
        """Empty data should raise a ValueError."""
        with pytest.raises(ValueError):
            build_qr("")
