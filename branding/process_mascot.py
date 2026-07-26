#!/usr/bin/env python3
"""
Turns the user's own original ghost-mascot artwork (branding/source-assets/
ghost-mascot-original.jpeg) into the full set of AetherOS logo assets:
background removed, sized for logo/avatar use, plus an ASCII-art rendition
for the terminal (aether-info).

This replaces the earlier placeholder mascot with the real, user-authored
artwork, as confirmed by the user.

Usage:
    python3 process_mascot.py
"""
import os
from PIL import Image
import numpy as np

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "source-assets", "ghost-mascot-original.jpeg")
ICON_DIR = os.path.join(ROOT, "..", "profile", "airootfs", "usr", "share", "icons", "aetheros")


def cutout_background(src_path):
    """Removes the near-black background, producing a transparent PNG,
    then crops tightly to the mascot's bounding box."""
    src = Image.open(src_path).convert("RGB")
    arr = np.array(src).astype(np.uint8)
    rgba = np.dstack([arr, np.full(arr.shape[:2], 255, dtype=np.uint8)])

    brightness = arr.sum(axis=2).astype(float)
    thresh_low, thresh_high = 30, 90
    alpha = np.clip((brightness - thresh_low) / (thresh_high - thresh_low), 0, 1)
    rgba[:, :, 3] = (alpha * 255).astype(np.uint8)

    out = Image.fromarray(rgba, mode="RGBA")
    bbox = out.getbbox()
    if bbox:
        # small margin around the mascot
        pad = int(0.04 * max(bbox[2] - bbox[0], bbox[3] - bbox[1]))
        l, t, r, b = bbox
        bbox = (max(0, l - pad), max(0, t - pad), min(out.width, r + pad), min(out.height, b + pad))
        out = out.crop(bbox)
    return out


def make_square(img, size, bg=None):
    """Pads/centers the (already-cropped) mascot into a square canvas."""
    ratio = min(size / img.width, size / img.height) * 0.86
    new_w, new_h = int(img.width * ratio), int(img.height * ratio)
    resized = img.resize((new_w, new_h), Image.LANCZOS)
    canvas = Image.new("RGBA", (size, size), bg if bg else (0, 0, 0, 0))
    canvas.paste(resized, ((size - new_w) // 2, (size - new_h) // 2), resized)
    return canvas


def make_ascii(img, cols=42):
    """Downsamples the mascot's alpha/luminance into a small ASCII-art grid
    for terminal display (used by aether-info)."""
    ramp = " .:-=+*#%@"
    w, h = img.size
    rows = max(1, int(cols * (h / w) * 0.5))  # 0.5 to compensate for character aspect ratio
    small = img.resize((cols, rows), Image.LANCZOS)
    arr = np.array(small.convert("RGBA")).astype(float)
    alpha = arr[:, :, 3] / 255.0
    lum = (0.299 * arr[:, :, 0] + 0.587 * arr[:, :, 1] + 0.114 * arr[:, :, 2]) / 255.0
    visible = lum * alpha

    lines = []
    for row in visible:
        line = "".join(ramp[min(len(ramp) - 1, int(v * (len(ramp) - 1)))] if v > 0.04 else " " for v in row)
        lines.append(line.rstrip())
    return "\n".join(lines)


def main():
    if not os.path.exists(SRC):
        raise SystemExit(f"Source artwork not found: {SRC}")

    os.makedirs(ICON_DIR, exist_ok=True)

    mascot = cutout_background(SRC)

    # Primary system logo (transparent PNG, used by Plymouth/GRUB/menus)
    make_square(mascot, 768).save(os.path.join(ICON_DIR, "aetheros-logo.png"))

    # User-avatar version (also transparent; greeters composite it onto a circle)
    make_square(mascot, 512).save(os.path.join(ICON_DIR, "aetheros-avatar.png"))

    # Small taskbar/app-menu size
    make_square(mascot, 128).save(os.path.join(ICON_DIR, "aetheros-logo-128.png"))

    ascii_art = make_ascii(mascot, cols=40)
    with open(os.path.join(ICON_DIR, "aetheros-ghost.txt"), "w") as f:
        f.write(ascii_art + "\n")

    print("Processed the user's original mascot artwork into:")
    print(" -", os.path.join(ICON_DIR, "aetheros-logo.png"))
    print(" -", os.path.join(ICON_DIR, "aetheros-avatar.png"))
    print(" -", os.path.join(ICON_DIR, "aetheros-logo-128.png"))
    print(" -", os.path.join(ICON_DIR, "aetheros-ghost.txt"), "(ASCII rendition)")


if __name__ == "__main__":
    main()
