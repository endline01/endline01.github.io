#!/usr/bin/env python3
"""
Material Design 3 theme generator.

Derives a full M3 color scheme (light + dark) from a single seed color and
writes the result as CSS custom properties to ../css/theme.css.

M3 defines a tone as CIELAB lightness (L*). A "tonal palette" fixes a hue and a
target chroma, then sweeps the tone (L*) from 0 to 100, clipping chroma to the
sRGB gamut at each tone. That is exactly what this script does, so the output is
faithful to the M3 model while requiring no third-party dependencies.

Usage:
    python tools/generate_theme.py

To re-theme the whole site, change SEED below and re-run. Every token in
css/theme.css is regenerated; nothing else needs to change.
"""

import math

# ─────────────────────────────────────────────────────────────────────────────
# CONFIG — change the seed color here to re-theme the entire site.
# A deep teal/slate: technical, credible, not corporate-generic.
SEED = "#1F5E66"
OUTPUT = "css/theme.css"
# ─────────────────────────────────────────────────────────────────────────────


# ── sRGB ⇄ linear ────────────────────────────────────────────────────────────
def _srgb_to_linear(c: float) -> float:
    c = c / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def _linear_to_srgb(c: float) -> float:
    v = 12.92 * c if c <= 0.0031308 else 1.055 * (c ** (1 / 2.4)) - 0.055
    return v * 255.0


# ── sRGB ⇄ XYZ (D65) ─────────────────────────────────────────────────────────
def _rgb_to_xyz(r, g, b):
    r, g, b = _srgb_to_linear(r), _srgb_to_linear(g), _srgb_to_linear(b)
    x = r * 0.4124564 + g * 0.3575761 + b * 0.1804375
    y = r * 0.2126729 + g * 0.7151522 + b * 0.0721750
    z = r * 0.0193339 + g * 0.1191920 + b * 0.9503041
    return x, y, z


def _xyz_to_linrgb(x, y, z):
    r = x * 3.2404542 + y * -1.5371385 + z * -0.4985314
    g = x * -0.9692660 + y * 1.8760108 + z * 0.0415560
    b = x * 0.0556434 + y * -0.2040259 + z * 1.0572252
    return r, g, b


# ── XYZ ⇄ CIELAB (D65 white point) ───────────────────────────────────────────
_XN, _YN, _ZN = 0.95047, 1.0, 1.08883
_EPS = 216 / 24389
_KAPPA = 24389 / 27


def _f(t):
    return t ** (1 / 3) if t > _EPS else (_KAPPA * t + 16) / 116


def _f_inv(t):
    t3 = t ** 3
    return t3 if t3 > _EPS else (116 * t - 16) / _KAPPA


def _xyz_to_lab(x, y, z):
    fx, fy, fz = _f(x / _XN), _f(y / _YN), _f(z / _ZN)
    return (116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz))


def _lab_to_xyz(l, a, b):
    fy = (l + 16) / 116
    fx = fy + a / 500
    fz = fy - b / 200
    return _f_inv(fx) * _XN, _f_inv(fy) * _YN, _f_inv(fz) * _ZN


# ── Lab ⇄ LCh ────────────────────────────────────────────────────────────────
def _rgb_to_lch(r, g, b):
    l, a, bb = _xyz_to_lab(*_rgb_to_xyz(r, g, b))
    c = math.hypot(a, bb)
    h = math.degrees(math.atan2(bb, a)) % 360
    return l, c, h


def _lch_to_linrgb(l, c, h):
    a = c * math.cos(math.radians(h))
    b = c * math.sin(math.radians(h))
    return _xyz_to_linrgb(*_lab_to_xyz(l, a, b))


def _in_gamut(linrgb, eps=1e-4):
    return all(-eps <= v <= 1 + eps for v in linrgb)


def _hex_from_linrgb(linrgb):
    out = []
    for v in linrgb:
        out.append(max(0, min(255, round(_linear_to_srgb(max(0.0, min(1.0, v)))))))
    return "#{:02X}{:02X}{:02X}".format(*out)


# ── Tonal palette: tone (L*) → hex, with chroma clipped to the sRGB gamut ─────
def tone_to_hex(hue: float, chroma_target: float, tone: float) -> str:
    tone = max(0.0, min(100.0, tone))
    # Binary-search the largest in-gamut chroma up to the target at this tone.
    lo, hi = 0.0, chroma_target
    if _in_gamut(_lch_to_linrgb(tone, hi, hue)):
        c = hi
    else:
        for _ in range(40):
            mid = (lo + hi) / 2
            if _in_gamut(_lch_to_linrgb(tone, mid, hue)):
                lo = mid
            else:
                hi = mid
        c = lo
    return _hex_from_linrgb(_lch_to_linrgb(tone, c, hue))


# ── Seed → key palettes (M3 standard chroma targets) ─────────────────────────
def _hex_to_rgb(h):
    h = h.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


seed_l, seed_c, seed_h = _rgb_to_lch(*_hex_to_rgb(SEED))

PALETTES = {
    "P":  (seed_h,            max(48.0, seed_c)),  # primary
    "S":  (seed_h,            16.0),               # secondary
    "T":  ((seed_h + 60) % 360, 24.0),             # tertiary
    "N":  (seed_h,            4.0),                # neutral
    "NV": (seed_h,            8.0),                # neutral-variant
}

# M3's error palette is a constant across all themes — use the canonical tones.
ERROR = {
    0: "#000000", 4: "#280001", 6: "#310001", 10: "#410002", 12: "#490002",
    17: "#5C0004", 20: "#690005", 22: "#710005", 24: "#790005", 30: "#93000A",
    40: "#BA1A1A", 50: "#DE3730", 60: "#FF5449", 70: "#FF897D", 80: "#FFB4AB",
    87: "#FFCFC9", 90: "#FFDAD6", 92: "#FFE2DE", 94: "#FFE9E6", 95: "#FFEDEA",
    96: "#FFF0EE", 98: "#FFF8F7", 99: "#FFFBFF", 100: "#FFFFFF",
}


def resolve(token):
    """token = ('E', 40) for error, or ('P', 40) etc. for derived palettes."""
    pal, tone = token
    if pal == "E":
        return ERROR[tone]
    hue, chroma = PALETTES[pal]
    return tone_to_hex(hue, chroma, tone)


# ── Role → (palette, tone) maps per the M3 specification ─────────────────────
LIGHT = {
    "primary": ("P", 40), "on-primary": ("P", 100),
    "primary-container": ("P", 90), "on-primary-container": ("P", 10),
    "secondary": ("S", 40), "on-secondary": ("S", 100),
    "secondary-container": ("S", 90), "on-secondary-container": ("S", 10),
    "tertiary": ("T", 40), "on-tertiary": ("T", 100),
    "tertiary-container": ("T", 90), "on-tertiary-container": ("T", 10),
    "error": ("E", 40), "on-error": ("E", 100),
    "error-container": ("E", 90), "on-error-container": ("E", 10),
    "background": ("N", 99), "on-background": ("N", 10),
    "surface": ("N", 99), "on-surface": ("N", 10),
    "surface-variant": ("NV", 90), "on-surface-variant": ("NV", 30),
    "outline": ("NV", 50), "outline-variant": ("NV", 80),
    "shadow": ("N", 0), "scrim": ("N", 0),
    "inverse-surface": ("N", 20), "inverse-on-surface": ("N", 95),
    "inverse-primary": ("P", 80),
    "surface-dim": ("N", 87), "surface-bright": ("N", 98),
    "surface-container-lowest": ("N", 100), "surface-container-low": ("N", 96),
    "surface-container": ("N", 94), "surface-container-high": ("N", 92),
    "surface-container-highest": ("N", 90),
}

DARK = {
    "primary": ("P", 80), "on-primary": ("P", 20),
    "primary-container": ("P", 30), "on-primary-container": ("P", 90),
    "secondary": ("S", 80), "on-secondary": ("S", 20),
    "secondary-container": ("S", 30), "on-secondary-container": ("S", 90),
    "tertiary": ("T", 80), "on-tertiary": ("T", 20),
    "tertiary-container": ("T", 30), "on-tertiary-container": ("T", 90),
    "error": ("E", 80), "on-error": ("E", 20),
    "error-container": ("E", 30), "on-error-container": ("E", 90),
    "background": ("N", 10), "on-background": ("N", 90),
    "surface": ("N", 10), "on-surface": ("N", 90),
    "surface-variant": ("NV", 30), "on-surface-variant": ("NV", 80),
    "outline": ("NV", 60), "outline-variant": ("NV", 30),
    "shadow": ("N", 0), "scrim": ("N", 0),
    "inverse-surface": ("N", 90), "inverse-on-surface": ("N", 20),
    "inverse-primary": ("P", 40),
    "surface-dim": ("N", 6), "surface-bright": ("N", 24),
    "surface-container-lowest": ("N", 4), "surface-container-low": ("N", 10),
    "surface-container": ("N", 12), "surface-container-high": ("N", 17),
    "surface-container-highest": ("N", 22),
}


def _emit_block(scheme):
    lines = []
    for role, token in scheme.items():
        lines.append(f"  --md-sys-color-{role}: {resolve(token)};")
    return "\n".join(lines)


def main():
    header = (
        "/* ===========================================================================\n"
        "   Material Design 3 — color tokens (GENERATED)\n"
        f"   Seed color: {SEED}  (L*={seed_l:.1f}  C={seed_c:.1f}  h={seed_h:.1f}°)\n"
        "   Do not edit by hand. Regenerate with:  python tools/generate_theme.py\n"
        "   =========================================================================== */\n\n"
    )
    light = _emit_block(LIGHT)
    dark = _emit_block(DARK)

    css = (
        header
        + "/* Light is the default. With no [data-theme] attribute the site follows the\n"
        "   OS via prefers-color-scheme; an explicit [data-theme] forces a choice. */\n"
        + ":root {\n" + light + "\n  color-scheme: light;\n}\n\n"
        + '@media (prefers-color-scheme: dark) {\n  :root:not([data-theme="light"]) {\n'
        + "\n".join("  " + l for l in dark.splitlines())
        + "\n    color-scheme: dark;\n  }\n}\n\n"
        + '[data-theme="dark"] {\n' + dark + "\n  color-scheme: dark;\n}\n\n"
        + '[data-theme="light"] {\n' + light + "\n  color-scheme: light;\n}\n"
    )

    import os
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out_path = os.path.join(here, OUTPUT)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write(css)
    print(f"Wrote {out_path}")
    # Print a few key roles for a sanity check.
    for r in ("primary", "primary-container", "tertiary", "surface", "error"):
        print(f"  light {r:18} {resolve(LIGHT[r])}   dark {resolve(DARK[r])}")


if __name__ == "__main__":
    main()
