#!/usr/bin/env python3
"""
Generates AetherOS branding assets (wallpapers + logo) programmatically,
so the project has real, working image files without depending on any
external downloads.

Usage:
    python3 generate_assets.py

Outputs into ../profile/airootfs/usr/share/backgrounds/aetheros/
and ../profile/airootfs/usr/share/icons/aetheros/
"""
import math
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = os.path.dirname(os.path.abspath(__file__))
WALLPAPER_DIR = os.path.join(ROOT, "..", "profile", "airootfs", "usr", "share", "backgrounds", "aetheros")
ICON_DIR = os.path.join(ROOT, "..", "profile", "airootfs", "usr", "share", "icons", "aetheros")

# AetherOS palette
NAVY      = (13, 20, 38)
DEEP_BLUE = (20, 40, 80)
ACCENT    = (90, 170, 255)     # primary brand blue
ACCENT_2  = (140, 110, 255)    # violet accent
WHITE     = (240, 245, 255)


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def make_gradient(size, top, bottom):
    w, h = size
    img = Image.new("RGB", size, top)
    px = img.load()
    for y in range(h):
        t = y / (h - 1)
        color = lerp(top, bottom, t)
        for x in range(w):
            px[x, y] = color
    return img


def add_glow_orb(img, center, radius, color, alpha=90):
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    draw.ellipse(
        [center[0] - radius, center[1] - radius, center[0] + radius, center[1] + radius],
        fill=color + (alpha,),
    )
    overlay = overlay.filter(ImageFilter.GaussianBlur(radius // 2))
    img.paste(Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB"), (0, 0))
    return img


def draw_wordmark(draw, xy, text, size, color):
    font = None
    for candidate in (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ):
        if os.path.exists(candidate):
            font = ImageFont.truetype(candidate, size)
            break
    if font is None:
        font = ImageFont.load_default()
    draw.text(xy, text, font=font, fill=color)


def make_wallpaper(path, size=(3840, 2160)):
    img = make_gradient(size, NAVY, DEEP_BLUE)
    img = add_glow_orb(img, (int(size[0] * 0.78), int(size[1] * 0.28)), int(size[1] * 0.45), ACCENT, alpha=70)
    img = add_glow_orb(img, (int(size[0] * 0.15), int(size[1] * 0.85)), int(size[1] * 0.35), ACCENT_2, alpha=55)

    draw = ImageDraw.Draw(img)
    # subtle concentric "aether ring" motif, bottom-left
    cx, cy = int(size[0] * 0.15), int(size[1] * 0.85)
    for r in range(80, 640, 80):
        bbox = [cx - r, cy - r, cx + r, cy + r]
        draw.ellipse(bbox, outline=WHITE, width=1)

    draw_wordmark(draw, (int(size[0] * 0.05), int(size[1] * 0.08)), "AetherOS", int(size[1] * 0.07), WHITE)
    img.save(path, quality=95)


def make_logo_mark(path, size=512):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    cx, cy = size // 2, size // 2
    # layered rings forming an abstract "A" / aether motif
    draw.ellipse([cx - size * 0.42, cy - size * 0.42, cx + size * 0.42, cy + size * 0.42],
                 outline=ACCENT, width=int(size * 0.045))
    draw.ellipse([cx - size * 0.30, cy - size * 0.30, cx + size * 0.30, cy + size * 0.30],
                 outline=ACCENT_2, width=int(size * 0.035))
    # inner triangle nodding to "A"
    pts = [
        (cx, cy - size * 0.20),
        (cx - size * 0.17, cy + size * 0.14),
        (cx + size * 0.17, cy + size * 0.14),
    ]
    draw.line(pts + [pts[0]], fill=WHITE, width=int(size * 0.03), joint="curve")
    img.save(path)


def make_streak_wallpaper(path, size=(3840, 2160), bg_top=(8, 11, 18), bg_bottom=(14, 20, 32),
                           streak_color=(90, 235, 220), streak_y=0.66, core_alpha=200, line_alpha=235,
                           brightness=1.0):
    """Dark background with a single glowing horizontal streak, like a beam
    of light entering from the left — matches the AetherOS reference mood.
    Parameterized so the same generator can produce the "Aether Cycle"
    time-of-day variants (dawn/day/dusk/night) just by changing the palette."""
    import random
    w, h = size
    base = make_gradient(size, bg_top, bg_bottom).convert("RGBA")

    # subtle grain so the background isn't a flat gradient
    grain = Image.new("L", size, 0)
    gpx = grain.load()
    random.seed(42)
    for _ in range(w * h // 400):
        x, y = random.randint(0, w - 1), random.randint(0, h - 1)
        gpx[x, y] = random.randint(0, 30)
    grain = grain.filter(ImageFilter.GaussianBlur(1))
    base = Image.alpha_composite(base, Image.merge("RGBA", (grain, grain, grain, grain.point(lambda p: p // 3))))

    streak_layer = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(streak_layer)
    cy = int(h * streak_y)
    x_start = int(w * 0.40)
    teal = streak_color

    # wide soft glow
    d.rectangle([x_start, cy - int(h * 0.10), w, cy + int(h * 0.10)], fill=teal + (int(55 * brightness),))
    streak_layer = streak_layer.filter(ImageFilter.GaussianBlur(int(h * 0.045)))

    # tighter, brighter core glow
    core_layer = Image.new("RGBA", size, (0, 0, 0, 0))
    dc = ImageDraw.Draw(core_layer)
    dc.rectangle([x_start, cy - int(h * 0.02), w, cy + int(h * 0.02)], fill=teal + (int(core_alpha * brightness),))
    core_layer = core_layer.filter(ImageFilter.GaussianBlur(int(h * 0.010)))

    # thin bright line at the very center of the streak
    line_layer = Image.new("RGBA", size, (0, 0, 0, 0))
    dl = ImageDraw.Draw(line_layer)
    dl.line([(x_start, cy), (w, cy)], fill=(220, 255, 250, int(line_alpha * brightness)),
             width=max(1, int(h * 0.0016)))
    line_layer = line_layer.filter(ImageFilter.GaussianBlur(1))

    out = Image.alpha_composite(base, streak_layer)
    out = Image.alpha_composite(out, core_layer)
    out = Image.alpha_composite(out, line_layer)
    out.convert("RGB").save(path, quality=95)


def make_cycle_wallpapers(wallpaper_dir):
    """Generates the 4 'Aether Cycle' time-of-day wallpaper variants."""
    variants = {
        "dawn":  dict(bg_top=(20, 14, 24), bg_bottom=(48, 26, 34), streak_color=(255, 170, 120), brightness=0.9),
        "day":   dict(bg_top=(8, 11, 18),  bg_bottom=(14, 20, 32), streak_color=(90, 235, 220), brightness=1.0),
        "dusk":  dict(bg_top=(14, 10, 26), bg_bottom=(30, 16, 46), streak_color=(190, 130, 255), brightness=0.85),
        "night": dict(bg_top=(4, 5, 9),    bg_bottom=(7, 9, 15),   streak_color=(70, 110, 170), brightness=0.5),
    }
    for name, params in variants.items():
        make_streak_wallpaper(os.path.join(wallpaper_dir, f"aetheros-cycle-{name}.png"), **params)


def make_wordmark_logo(path, size=768):
    """AetherOS mark: a stylised letter 'A' in dark green with one leg drawn
    out into a long streak — echoes the wallpaper's light-beam motif."""
    dark_green = (18, 92, 58)
    dark_green_soft = (18, 92, 58, 130)

    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    apex = (size * 0.40, size * 0.18)
    left_foot = (size * 0.16, size * 0.82)
    right_foot = (size * 0.52, size * 0.82)
    crossbar_y = size * 0.60
    stroke = max(4, int(size * 0.045))

    # soft glow behind the strokes
    glow = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.line([apex, left_foot], fill=dark_green_soft, width=stroke * 3)
    gd.line([apex, right_foot], fill=dark_green_soft, width=stroke * 3)
    glow = glow.filter(ImageFilter.GaussianBlur(size * 0.02))
    img = Image.alpha_composite(img, glow)
    draw = ImageDraw.Draw(img)

    # the two legs of the 'A'
    draw.line([apex, left_foot], fill=dark_green + (255,), width=stroke, joint="curve")
    draw.line([apex, right_foot], fill=dark_green + (255,), width=stroke, joint="curve")
    # crossbar
    cb_left = (size * 0.235, crossbar_y)
    cb_right = (size * 0.445, crossbar_y)
    draw.line([cb_left, cb_right], fill=dark_green + (255,), width=int(stroke * 0.8))

    # the elongated streak extending the crossbar out to the right —
    # tapering line with a soft glow, echoing the wallpaper
    streak_layer = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    sd = ImageDraw.Draw(streak_layer)
    streak_y = crossbar_y
    sd.line([(cb_right[0], streak_y), (size * 0.97, streak_y)], fill=dark_green + (230,), width=int(stroke * 0.55))
    glow2 = streak_layer.filter(ImageFilter.GaussianBlur(size * 0.012))
    img = Image.alpha_composite(img, glow2)
    img = Image.alpha_composite(img, streak_layer)

    img.save(path)

def make_ghost_logo(path, size=768, color=(70, 220, 190)):
    """AetherOS mascot: an original friendly ghost mark (our own design,
    not a copy of any reference image) — used as the primary system logo
    at boot, in the greeter, and as the default user avatar."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))

    # soft glow halo behind the mascot
    glow = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse([size * 0.12, size * 0.08, size * 0.88, size * 0.86], fill=color + (90,))
    glow = glow.filter(ImageFilter.GaussianBlur(size * 0.05))
    img = Image.alpha_composite(img, glow)

    body = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    bd = ImageDraw.Draw(body)

    top, bottom = size * 0.16, size * 0.80
    left, right = size * 0.22, size * 0.78
    mid_x = size / 2

    # rounded head/dome
    bd.pieslice([left, top, right, top + (right - left)], 180, 360, fill=color + (255,))
    body_top = top + (right - left) / 2
    bd.rectangle([left, body_top, right, bottom], fill=color + (255,))

    # scalloped bottom hem (the classic "ghost" silhouette)
    scallops = 5
    seg = (right - left) / scallops
    hem = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    hd = ImageDraw.Draw(hem)
    for i in range(scallops):
        cx = left + seg * i + seg / 2
        hd.ellipse([cx - seg * 0.55, bottom - seg * 0.55, cx + seg * 0.55, bottom + seg * 0.55],
                   fill=(0, 0, 0, 255))
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).rectangle([0, bottom, size, size], fill=255)
    body.paste(Image.new("RGBA", (size, size), (0, 0, 0, 0)), (0, 0), mask)
    img = Image.alpha_composite(img, body)

    # cut scalloped notches out using the hem ellipses as an eraser mask
    eraser = Image.new("L", (size, size), 0)
    ed = ImageDraw.Draw(eraser)
    for i in range(scallops):
        cx = left + seg * i + seg / 2
        ed.ellipse([cx - seg * 0.55, bottom - seg * 0.28, cx + seg * 0.55, bottom + seg * 0.55], fill=255)
    r, g, b, a = img.split()
    a = Image.composite(Image.new("L", (size, size), 0), a, eraser)
    img = Image.merge("RGBA", (r, g, b, a))

    # face: two soft eyes + tiny smile, dark navy so it reads on teal
    face = ImageDraw.Draw(img)
    eye_y = top + (right - left) * 0.42
    eye_w, eye_h = size * 0.055, size * 0.075
    face.ellipse([mid_x - size * 0.15 - eye_w, eye_y, mid_x - size * 0.15 + eye_w, eye_y + eye_h], fill=(10, 20, 25, 255))
    face.ellipse([mid_x + size * 0.15 - eye_w, eye_y, mid_x + size * 0.15 + eye_w, eye_y + eye_h], fill=(10, 20, 25, 255))
    smile_y = eye_y + eye_h * 1.7
    face.arc([mid_x - size * 0.07, smile_y, mid_x + size * 0.07, smile_y + size * 0.08], 10, 170,
             fill=(10, 20, 25, 255), width=max(2, int(size * 0.012)))

    img.save(path)


def make_ghost_ascii():
    """A small ASCII-art rendition of the ghost mascot for terminal branding
    (used by aether-info / boot messages). Original, hand-drawn ASCII."""
    lines = [
        "     .--~~~~--.",
        "    /  o    o  \\",
        "   |     ..     |",
        "   |   \\____/   |",
        "    \\/\\/\\/\\/\\/\\/",
    ]
    return "\n".join(lines)


def main():
    os.makedirs(WALLPAPER_DIR, exist_ok=True)
    os.makedirs(ICON_DIR, exist_ok=True)

    # New default: dark streak-of-light wallpaper (reference-matched)
    make_streak_wallpaper(os.path.join(WALLPAPER_DIR, "aetheros-default.png"))
    # Keep the original wordmark gradient as a selectable alternative
    make_wallpaper(os.path.join(WALLPAPER_DIR, "aetheros-wordmark.png"))

    # "Aether Cycle" — 4 time-of-day wallpaper variants (dawn/day/dusk/night)
    make_cycle_wallpapers(WALLPAPER_DIR)

    # Light variant for the "Aether Light" theme
    light = make_gradient((3840, 2160), (225, 235, 250), (190, 210, 240))
    d = ImageDraw.Draw(light)
    draw_wordmark(d, (3840 * 0.05, 2160 * 0.08), "AetherOS", int(2160 * 0.07), (30, 40, 60))
    light.save(os.path.join(WALLPAPER_DIR, "aetheros-light.png"), quality=95)

    # Secondary mark: dark-green "A" with elongated streak (used for the
    # Aether Info app and other internal branding)
    make_wordmark_logo(os.path.join(ICON_DIR, "aetheros-wordmark-logo.png"))

    # PRIMARY system logo: original ghost mascot (boot splash, greeter,
    # default user avatar, GRUB)
    make_ghost_logo(os.path.join(ICON_DIR, "aetheros-logo.png"))
    # A version with transparent background sized for a user-avatar circle
    make_ghost_logo(os.path.join(ICON_DIR, "aetheros-avatar.png"), size=512)

    with open(os.path.join(ICON_DIR, "aetheros-ghost.txt"), "w") as f:
        f.write(make_ghost_ascii() + "\n")

    print("Generated:")
    print(" -", os.path.join(WALLPAPER_DIR, "aetheros-default.png"), "(streak wallpaper)")
    print(" -", os.path.join(WALLPAPER_DIR, "aetheros-wordmark.png"))
    print(" -", os.path.join(WALLPAPER_DIR, "aetheros-light.png"))
    print(" -", os.path.join(ICON_DIR, "aetheros-logo.png"), "(ghost mascot — primary logo)")
    print(" -", os.path.join(ICON_DIR, "aetheros-avatar.png"))
    print(" -", os.path.join(ICON_DIR, "aetheros-wordmark-logo.png"))
    print(" -", os.path.join(ICON_DIR, "aetheros-ghost.txt"), "(ASCII art)")


if __name__ == "__main__":
    main()
