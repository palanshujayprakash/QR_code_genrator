"""
QR Code Builder Module
Constructs styled QR codes (Square, Rounded, Circle) with custom colors and center logo overlays.
Pure in-memory operations using qrcode[pil] and Pillow.
"""

import io
from typing import Optional, Union, Tuple
from PIL import Image, ImageDraw
import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers.pil import (
    SquareModuleDrawer,
    RoundedModuleDrawer,
    CircleModuleDrawer,
)
from qrcode.image.styles.colormasks import SolidFillColorMask
from utils.validators import hex_to_rgb


def get_module_drawer(style_name: str):
    """
    Map style string to corresponding qrcode module drawer.
    Supported: 'Square', 'Rounded', 'Circle'
    """
    clean = (style_name or "Square").strip().lower()
    if "round" in clean:
        return RoundedModuleDrawer()
    elif "circle" in clean or "dot" in clean:
        return CircleModuleDrawer()
    return SquareModuleDrawer()


def overlay_center_logo(
    qr_img: Image.Image,
    logo_bytes: bytes,
    target_ratio: float = 0.20,
) -> Image.Image:
    """
    Place the logo at the exact center of the QR code:
    - Sized to ~20% of QR code width.
    - Sits inside a protective white rounded-rectangle padding badge.
    - Operates purely in-memory.
    """
    qr_rgba = qr_img.convert("RGBA")
    logo = Image.open(io.BytesIO(logo_bytes)).convert("RGBA")

    qr_w, qr_h = qr_rgba.size
    target_logo_dim = max(16, int(qr_w * target_ratio))

    # Resize logo keeping aspect ratio
    logo.thumbnail((target_logo_dim, target_logo_dim), Image.Resampling.LANCZOS)
    lw, lh = logo.size

    # Protective white rounded padding around logo
    pad = max(6, int(target_logo_dim * 0.12))
    badge_w = lw + pad * 2
    badge_h = lh + pad * 2

    # Draw rounded white background
    badge = Image.new("RGBA", (badge_w, badge_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(badge)
    radius = max(6, int(min(badge_w, badge_h) * 0.25))
    draw.rounded_rectangle(
        [(0, 0), (badge_w - 1, badge_h - 1)],
        radius=radius,
        fill=(255, 255, 255, 255),
    )

    # Paste logo onto badge (using alpha channel mask if present)
    badge.paste(logo, (pad, pad), mask=logo)

    # Paste badge onto QR center
    bx = (qr_w - badge_w) // 2
    by = (qr_h - badge_h) // 2
    qr_rgba.paste(badge, (bx, by), mask=badge)

    return qr_rgba


def build_qr(
    data: str,
    size: int = 10,
    fg: Union[str, Tuple[int, int, int]] = "#2C3480",
    bg: Union[str, Tuple[int, int, int]] = "#FFFFFF",
    style: str = "Square",
    logo_bytes: Optional[bytes] = None,
    error_correction: Optional[int] = None,
) -> Image.Image:
    """
    Generate a styled QR code as a Pillow Image.

    Args:
        data: The encoded text or URI string.
        size: Box size / module size in pixels (default 10).
        fg: Foreground / dot color (hex string or RGB tuple).
        bg: Background color (hex string or RGB tuple).
        style: Module dot style ('Square', 'Rounded', 'Circle').
        logo_bytes: Optional raw bytes of verified center logo.
        error_correction: Optional manual error correction constant (qrcode.constants.ERROR_CORRECT_*).

    Returns:
        PIL.Image.Image: The generated and composited QR image.
    """
    if not data or not str(data).strip():
        raise ValueError("Cannot build QR code: payload data is empty.")

    fg_rgb = hex_to_rgb(fg) if isinstance(fg, str) else fg
    bg_rgb = hex_to_rgb(bg) if isinstance(bg, str) else bg

    # Rule: If a logo is added, automatically enforce Error Correction Level H (30% recovery)
    if logo_bytes is not None:
        ec_level = qrcode.constants.ERROR_CORRECT_H
    elif error_correction is not None:
        ec_level = error_correction
    else:
        ec_level = qrcode.constants.ERROR_CORRECT_M

    qr = qrcode.QRCode(
        version=None,
        error_correction=ec_level,
        box_size=size,
        border=3,
    )
    qr.add_data(data)
    qr.make(fit=True)

    drawer = get_module_drawer(style)
    color_mask = SolidFillColorMask(front_color=fg_rgb, back_color=bg_rgb)

    # Generate styled QR code with StyledPilImage
    styled_img = qr.make_image(
        image_factory=StyledPilImage,
        module_drawer=drawer,
        color_mask=color_mask,
    )

    # Extract underlying Pillow Image instance
    pil_img = styled_img.get_image() if hasattr(styled_img, "get_image") else styled_img

    # Overlay center logo if provided
    if logo_bytes is not None:
        pil_img = overlay_center_logo(pil_img, logo_bytes, target_ratio=0.20)

    return pil_img
