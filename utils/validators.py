"""
Validation utilities for QR Code Studio:
1. Logo validation (in-memory Pillow verification, size constraint <= 2 MB, format check).
2. WCAG contrast ratio calculation for Foreground vs Background colors.
"""

import io
from typing import Tuple, Union
from PIL import Image, UnidentifiedImageError

# Maximum allowed logo file size (2 MB)
MAX_LOGO_SIZE_BYTES = 2 * 1024 * 1024


def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    """
    Convert a hex color string (e.g. '#2C3480' or '2C3480') to an RGB tuple (R, G, B).
    Supports 3-character and 6-character hex formats.
    """
    clean_hex = hex_color.strip().lstrip("#")
    if len(clean_hex) == 3:
        clean_hex = "".join([c * 2 for c in clean_hex])
    if len(clean_hex) != 6:
        raise ValueError(f"Invalid hex color: '{hex_color}'. Expected format like '#2C3480'.")
    try:
        r = int(clean_hex[0:2], 16)
        g = int(clean_hex[2:4], 16)
        b = int(clean_hex[4:6], 16)
        return (r, g, b)
    except ValueError as e:
        raise ValueError(f"Invalid hex color characters in '{hex_color}': {str(e)}")


def relative_luminance(rgb: Tuple[int, int, int]) -> float:
    """
    Calculate relative luminance (Y) of an sRGB color per WCAG 2.1 specifications.
    Luminance is normalized to [0.0, 1.0].
    """
    def channel_linear(val: int) -> float:
        c = val / 255.0
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

    r_lin = channel_linear(rgb[0])
    g_lin = channel_linear(rgb[1])
    b_lin = channel_linear(rgb[2])
    return 0.2126 * r_lin + 0.7152 * g_lin + 0.0722 * b_lin


def contrast_ratio(
    fg: Union[str, Tuple[int, int, int]],
    bg: Union[str, Tuple[int, int, int]],
) -> float:
    """
    Calculate the WCAG contrast ratio between foreground (QR code) and background.
    Formula: (L1 + 0.05) / (L2 + 0.05), where L1 is lighter and L2 is darker.
    Returns:
        float: Contrast ratio value between 1.0 and 21.0.
    """
    fg_rgb = hex_to_rgb(fg) if isinstance(fg, str) else fg
    bg_rgb = hex_to_rgb(bg) if isinstance(bg, str) else bg

    l1 = relative_luminance(fg_rgb)
    l2 = relative_luminance(bg_rgb)

    lighter = max(l1, l2)
    darker = min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)


def validate_logo(file_obj_or_bytes) -> Tuple[bool, str, bytes]:
    """
    Validate an uploaded logo file in-memory using Pillow without touching the disk:
    1. Checks if file is present and not empty.
    2. Checks if file size is <= 2 MB.
    3. Verifies file integrity with Pillow (Image.open + verify).
    4. Ensures file format is PNG or JPEG/JPG.

    Args:
        file_obj_or_bytes: Streamlit UploadedFile, BytesIO stream, or raw bytes.

    Returns:
        Tuple[bool, str, bytes]: (is_valid, error_message, file_bytes)
    """
    if file_obj_or_bytes is None:
        return False, "No file uploaded.", b""

    # Extract raw bytes strictly in memory
    if hasattr(file_obj_or_bytes, "getvalue"):
        raw_bytes = file_obj_or_bytes.getvalue()
    elif hasattr(file_obj_or_bytes, "read"):
        raw_bytes = file_obj_or_bytes.read()
    elif isinstance(file_obj_or_bytes, bytes):
        raw_bytes = file_obj_or_bytes
    else:
        return False, "Unsupported file input format.", b""

    # Check for empty file
    if len(raw_bytes) == 0:
        return False, "Uploaded logo file is empty.", b""

    # Check size constraint (max 2 MB)
    if len(raw_bytes) > MAX_LOGO_SIZE_BYTES:
        size_mb = len(raw_bytes) / (1024 * 1024)
        return False, f"Logo size ({size_mb:.2f} MB) exceeds maximum allowed limit of 2 MB.", b""

    # In-memory verification with Pillow
    try:
        mem_stream = io.BytesIO(raw_bytes)
        img = Image.open(mem_stream)
        img.verify()  # Validates image header and stream integrity
        fmt = (img.format or "").upper()
        if fmt not in ("PNG", "JPEG", "JPG"):
            return False, f"Unsupported format: {fmt}. Only PNG and JPG/JPEG files are accepted.", b""
        return True, "", raw_bytes
    except (UnidentifiedImageError, OSError, SyntaxError) as err:
        return False, f"Corrupted or invalid image file: {str(err)}", b""
