# Osama Hussein — Portfolio

A single-page, static personal portfolio for **Osama Hussein** — Cybersecurity
Specialist, Penetration Tester, and Information Security Officer. Built on
**Material Design 3** (color roles, type scale, elevation, shape, state layers,
and motion) with light/dark themes. No backend, no build step to deploy.

---

## Run it

It's plain static files — open `index.html`, or serve the folder:

```powershell
# From the project root (F:\ME\Portfolio)
python -m http.server 8080
# then visit http://127.0.0.1:8080/
```

Any static host works (GitHub Pages, Netlify, Cloudflare Pages, S3): just upload
the folder. The only external runtime request is to Google Fonts (Roboto +
Roboto Mono); if that's blocked, the site falls back to system fonts.

---

## Publish to GitHub Pages → https://endline01.github.io

This repo is already initialized and committed on `main`, with the remote set to
`https://github.com/endline01/endline01.github.io.git`.

1. **Create the repo on GitHub** (must be **public** for Pages on a free plan):
   go to <https://github.com/new>, set **Repository name** to exactly
   `endline01.github.io`, leave it **empty** (no README / .gitignore / license),
   and click *Create repository*.

2. **Push** from the project root:

   ```powershell
   git push -u origin main
   ```

   On first push, Git Credential Manager opens a browser to sign in to GitHub.

3. **Confirm Pages is on:** in the repo, **Settings → Pages** → *Build and
   deployment* → **Source: Deploy from a branch**, **Branch: `main` / `(root)`**,
   then *Save*. For a `username.github.io` repo this is usually auto-enabled.

4. Wait ~1 minute, then visit **https://endline01.github.io**.

**Updating later:** edit files, then

```powershell
git add -A
git commit -m "Update content"
git push
```

Pages redeploys automatically within a minute or so.

---

## Project structure

```
Portfolio/
├─ index.html              # All content + markup (the 12 sections)
├─ css/
│  ├─ theme.css            # GENERATED M3 color tokens (light + dark)
│  └─ styles.css           # System layer: type scale, shape, elevation,
│                          #   state layers, motion, layout, components
├─ js/
│  └─ main.js              # Theme toggle, mobile nav, scroll-spy, reveal motion
├─ assets/
│  └─ bg.webm              # Background dust-particle loop (dark theme only)
├─ tools/
│  └─ generate_theme.py    # Re-generates css/theme.css from one seed color
└─ README.md
```

### Background video

`assets/bg.webm` is a subtle dust-particle loop shown in **both themes**, tinted
toward the theme's cyan and disabled under `prefers-reduced-motion`:
- **Dark:** a `screen` blend drops the footage's black background so the
  particles glow as light motes.
- **Light:** the clip is inverted and `multiply`-blended, so the particles read
  as soft dark motes drifting over the page.

- **Credit (required):** "Dust Particles 5" by *VFX FOOTAGE*, licensed
  [CC BY 3.0](https://creativecommons.org/licenses/by/3.0/), via
  [Wikimedia Commons](https://commons.wikimedia.org/wiki/File:Dust_Particles_5_--FREE_FOOTAGE--.webm).
  The attribution line is in the page footer; keep it while you use the clip.
- **To replace it:** drop your own `bg.webm` (or add a `bg.mp4` `<source>` in
  `index.html`) into `assets/`, and update the footer credit to match the new
  clip's license.

---

## Changing the color scheme (one place)

The entire palette is derived from a **single seed color**. To re-theme the whole
site:

1. Open `tools/generate_theme.py` and edit the `SEED` value near the top:

   ```python
   SEED = "#1F5E66"   # deep teal/slate — change to any hex color
   ```

2. Regenerate the tokens:

   ```powershell
   python tools/generate_theme.py
   ```

   This overwrites `css/theme.css` with a fresh, full M3 scheme (all color roles,
   light and dark).

> **How it works:** In Material Design 3 a *tone* is CIELAB lightness (L\*). The
> generator builds each tonal palette by fixing a hue + target chroma and
> sweeping the tone 0→100, clipping chroma to the sRGB gamut — the M3 model,
> implemented in pure Python (no dependencies). Primary/secondary/tertiary/
> neutral/neutral-variant come from the seed using M3's standard chroma targets;
> the error palette uses M3's canonical constant tones.

### Light / dark behavior
- **Dark is the default** (`<html data-theme="dark">`). First-time visitors see
  the dark theme regardless of their OS setting.
- The header toggle switches to light/dark and persists the choice in
  `localStorage` (re-applied before first paint to avoid a flash), so a returning
  visitor keeps whatever they last selected.
- To make **light** the default instead, just remove `data-theme="dark"` from the
  `<html>` tag in `index.html`.

---

## Editing content

All content lives in **`index.html`**, organized by section with clear comment
banners (`<!-- ===== EXPERIENCE ===== -->`, etc.). Every claim comes from the
résumé and the curated context — there are no placeholder/lorem values.

- **Skills / Tools / Project tags** are `<span class="chip">…</span>` items —
  add or remove `<span>`s inside the relevant `.chip-set`.
- **Experience bullets** are `.xp__item` blocks (a `<h4>` + `<p>`).
- **Phone number** is intentionally omitted for privacy. To enable it, uncomment
  the commented block at the bottom of the Contact section in `index.html`.

---

## Accessibility & performance

- Semantic landmarks (`header`/`main`/`footer`/`nav`/`section`), a skip link,
  visible focus rings, `aria-current` on the active nav item, and a keyboard-
  and Escape-dismissible mobile navigation drawer.
- All key text/background pairs meet **WCAG AA** (≥ 4.5:1) in both themes.
- Respects `prefers-reduced-motion` (reveal animations and smooth scroll are
  disabled).
- No frameworks, no bundler, ~1 small JS file; inline SVG icons (no icon font).
```
