#!/usr/bin/env python3
"""
Prep a photo for ASCII conversion. Run this locally, once, whenever you
change your source photo:

    python scripts/prep_photo.py path/to/your-photo.jpg

Writes source-prepped.png (grayscale, background removed, contrast
boosted, composited onto white so the background maps to blank space
in the ASCII ramp instead of printing as noise).

Uses rembg + opencv if they're installed (best quality). If they're
not, falls back to a plain PIL auto-contrast pass so the script still
works with just `pip install pillow`.
"""

import os
import sys
from PIL import Image, ImageOps

OUT_PATH = "source-prepped.png"

# Default photo location — edit this if you move the file, or just pass
# a different path on the command line: python scripts/prep_photo.py path\to\photo.jpg
DEFAULT_PHOTO_PATH = r"D:\GitProfile\SatyaPrakash252\IMAGES\PHOTO.jpg"


def prep_with_rembg_cv2(img_bytes: bytes) -> Image.Image:
    import io
    import numpy as np
    import cv2
    from rembg import remove

    no_bg = remove(img_bytes)  # RGBA, background made transparent
    rgba = Image.open(io.BytesIO(no_bg)).convert("RGBA")

    # composite onto white
    white_bg = Image.new("RGBA", rgba.size, (255, 255, 255, 255))
    flattened = Image.alpha_composite(white_bg, rgba).convert("RGB")

    # CLAHE for local contrast on the luminance channel
    arr = np.array(flattened)
    lab = cv2.cvtColor(arr, cv2.COLOR_RGB2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    l = clahe.apply(l)
    lab = cv2.merge((l, a, b))
    boosted = cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)

    return Image.fromarray(boosted).convert("L")


def prep_with_pillow_only(path: str) -> Image.Image:
    img = Image.open(path).convert("L")
    img = ImageOps.autocontrast(img, cutoff=1)
    return img


def main():
    path = sys.argv[1] if len(sys.argv) >= 2 else DEFAULT_PHOTO_PATH

    if not os.path.exists(path):
        print(f"Photo not found at: {path}")
        print("Usage: python scripts/prep_photo.py path\\to\\photo.jpg")
        sys.exit(1)

    try:
        with open(path, "rb") as f:
            raw = f.read()
        img = prep_with_rembg_cv2(raw)
        print("Prepped with rembg + OpenCV (background removed, CLAHE contrast).")
    except ImportError:
        print("rembg/opencv not installed — falling back to a plain contrast boost.")
        print("For best results: pip install rembg opencv-python numpy")
        img = prep_with_pillow_only(path)

    img.save(OUT_PATH)
    print(f"Wrote {OUT_PATH}")


if __name__ == "__main__":
    main()