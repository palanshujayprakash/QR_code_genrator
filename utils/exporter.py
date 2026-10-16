"""
Multi-Format QR Exporter Module
Exports QR codes into PNG, JPG, PDF, and SVG formats as in-memory byte streams.
"""

import io
from typing import Union, Tuple
from PIL import Image
import segno
from utils.validators import hex_to_rgb


def _ensure_rgb(pil_image: Image.Image, bg_color: Tuple[int, int, int] = (255, 255, 255)) -> Image.Image:
    """
    Ensure a Pillow image is in RGB mode (required for JPEG and PDF formats).
    If the image has an alpha channel (RGBA), composites it onto a solid background.
    """
    if pil_image.mode == "RGB":
        return pil_image

    rgba = pil_image.convert("RGBA")
    solid_bg = Image.new("RGB", rgba.size, bg_color)
    solid_bg.paste(rgba, mask=rgba.split()[3])
    return solid_bg


def to_png(pil_image: Image.Image) -> bytes:
    """Export Pillow QR image as PNG byte stream."""
    buffer = io.BytesIO()
    pil_image.save(buffer, format="PNG")
    return buffer.getvalue()


def to_jpg(pil_image: Image.Image, quality: int = 95) -> bytes:
    """Export Pillow QR image as JPEG byte stream (auto-converts RGBA to RGB)."""
    rgb_img = _ensure_rgb(pil_image)
    buffer = io.BytesIO()
    rgb_img.save(buffer, format="JPEG", quality=quality)
    return buffer.getvalue()


def to_pdf(pil_image: Image.Image) -> bytes:
    """Export Pillow QR image as PDF document byte stream (auto-converts RGBA to RGB)."""
    rgb_img = _ensure_rgb(pil_image)
    buffer = io.BytesIO()
    rgb_img.save(buffer, format="PDF")
    return buffer.getvalue()


def to_svg(
    data: str,
    fg: Union[str, Tuple[int, int, int]] = "#2C3480",
    bg: Union[str, Tuple[int, int, int]] = "#FFFFFF",
    scale: int = 10,
) -> bytes:
    """
    Export plain vector QR code as SVG byte stream using segno.
    Note: Vector SVG exports the mathematical QR grid; custom center logos
    and dot rounding are raster features rendered via PNG/JPG/PDF.
    """
    if not data or not str(data).strip():
        raise ValueError("Cannot export SVG: payload data is empty.")

    # Convert RGB tuple to hex string if needed
    if isinstance(fg, tuple):
        fg_hex = f"#{fg[0]:02x}{fg[1]:02x}{fg[2]:02x}"
    else:
        fg_hex = fg if fg.startswith("#") else f"#{fg}"

    if isinstance(bg, tuple):
        bg_hex = f"#{bg[0]:02x}{bg[1]:02x}{bg[2]:02x}"
    else:
        bg_hex = bg if bg.startswith("#") else f"#{bg}"

    qr = segno.make(data, error="h")
    buffer = io.BytesIO()
    qr.save(buffer, kind="svg", dark=fg_hex, light=bg_hex, scale=scale)
    return buffer.getvalue()
