# OPERION OS — Style Guide
**Version:** 1.0 · **Date:** April 21, 2026  
**Owner:** Felix Andres Rios Blanco — Founder & CEO  
**Classification:** Internal · Source of Truth for all visual outputs

This document is the single authority for every visual decision made under the OPERION brand. Any agent, contractor, or collaborator producing visual output reads this first.

---

## 1. Color System

### Core palette

| Token | Hex | Name | Usage |
|-------|-----|------|-------|
| `--cobalt` | `#1A2B72` | Deep cobalt | Primary accent — CTAs, active states, accents on light surfaces |
| `--cobalt-pop` | `#5870CC` | Bright cobalt | Accent on dark surfaces — stat numbers, featured labels |
| `--chrome` | `#B8BCC8` | Chrome silver | Metallic secondary — borders on dark, decorative lines |
| `--ink` | `#0D1420` | Ink | Dark section backgrounds, near-black |
| `--blanc` | `#F5F5F7` | Blanc technique | Body background, alternating section fills |
| `--black` | `#000000` | Absolute black | Military-grade document backgrounds (Register B) |
| `--white` | `#FFFFFF` | Absolute white | Card surfaces, text on dark |
| `--dim` | `#72727E` | Dim | Secondary text, labels, captions |
| `--border` | `#E0E0E8` | Light border | 1px borders on light surfaces |
| `--border-dark` | `rgba(255,255,255,0.10)` | Dark border | 1px borders on dark surfaces |

### Color rules
- `--cobalt` is reserved for data, CTAs, and critical highlights on **light surfaces**. Never use it for decoration.
- `--cobalt-pop` is used on **dark surfaces** where `--cobalt` would be invisible against the dark background.
- Never put `--cobalt` text on a `--cobalt` background.
- Dark backgrounds use `--ink` (branded) or `--black` (military documents).
- No gradients in Register A. No color fills beyond the palette above.
- Cobalt glow is permitted only on live-data elements: `box-shadow: 0 0 40px rgba(26,43,114,0.08)`.
- Chrome silver (`--chrome`) is used as a subtle secondary accent, especially on dark surfaces.

### Legacy tokens (deprecated — do not use in new work)
The amber `#E8A33D` ("Sol naciente") and `#0F1729` ("Noche andina") tokens are retired as of v2 identity. Any file still using these must be migrated to the cobalt/ink system.

---

## 2. Typography

### Typefaces

| Role | Family | Weight | Transform |
|------|--------|--------|-----------|
| Display / Headlines | Space Grotesk | 700, 800 | UPPERCASE |
| Body copy | Inter | 300, 400, 500 | sentence case |
| Data / Terminal | JetBrains Mono | 400 | as-is |

### Import (Google Fonts)
```html
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;700;800&family=Inter:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap" />
```

### Type scale

| Name | Size | Weight | Font | Notes |
|------|------|--------|------|-------|
| `display-xl` | 72–96px | 800 | Space Grotesk | Hero headlines only |
| `display-lg` | 48–64px | 800 | Space Grotesk | Section headlines |
| `display-md` | 32–40px | 700 | Space Grotesk | Sub-section, card titles |
| `label` | 11–12px | 500 | Inter | Uppercase + letter-spacing 0.18em |
| `body-lg` | 17–18px | 300 | Inter | Lead paragraphs |
| `body` | 15–16px | 400 | Inter | Standard body |
| `body-sm` | 13px | 400 | Inter | Captions, footnotes |
| `mono` | 13–14px | 400 | JetBrains Mono | Terminal, code, coordinates |

### Typography rules
- All Space Grotesk headlines: uppercase, no exceptions.
- Body copy uses sentence case. Never title-case marketing copy.
- Line height: 1.15 for headlines, 1.65 for body.
- Max line width: 680px for body text. Do not let paragraphs run wider.

---

## 3. Spacing

Base unit: **8px**. All spacing values are multiples of 8.

| Token | Value | Usage |
|-------|-------|-------|
| `--space-1` | 8px | Tight internal gaps |
| `--space-2` | 16px | Component internal padding |
| `--space-3` | 24px | Card padding, small gaps |
| `--space-4` | 32px | Medium gaps between elements |
| `--space-6` | 48px | Large gaps |
| `--space-8` | 64px | Section sub-divisions |
| `--space-12` | 96px | Section padding (min) |
| `--space-16` | 128px | Section padding (preferred) |

**Law:** Sections must breathe. Min 80px vertical padding per section. White space is not empty space — it signals precision and confidence. Never add decorative elements to fill whitespace.

---

## 4. Layout

- Max content width: **1080px**
- Standard content width: **900px**
- Narrow (text-only) width: **680px**
- Grid: 12-column, 24px gutter
- Breakpoints: mobile 375px / tablet 768px / desktop 1200px

---

## 5. Components

### Buttons

```
Primary (filled):
  background: --cobalt (#1A2B72)
  color: --white
  border: none
  border-radius: 2px
  padding: 12px 28px
  font: Inter 500, 13px, letter-spacing 0.08em, UPPERCASE
  hover: opacity 0.88

Ghost:
  background: transparent
  color: --cobalt
  border: 1px solid rgba(26,43,114,0.30)
  border-radius: 2px
  padding: 11px 27px  (1px less to account for border)
  font: same as primary
  hover: background rgba(26,43,114,0.05)

Tactical (dark surfaces):
  background: transparent
  color: --white
  border: 1px solid rgba(255,255,255,0.25)
  border-radius: 2px
  hover: border-color rgba(255,255,255,0.60)
```

### Cards (light surface)
```
background: #FFFFFF
border: 1px solid --border-light
border-radius: 2px
padding: 24px
hover: border-color #AAAAAA
transition: border-color 0.2s
No box-shadow.
```

### Cards (dark surface)
```
background: rgba(255,255,255,0.03)
border: 1px solid --border-dark
border-radius: 2px
padding: 24px
hover: border-color rgba(255,255,255,0.25)
No box-shadow. 
Amber glow on live-data cards only.
```

### Labels / Eyebrows
```
font: Inter 500
size: 11px
transform: UPPERCASE
letter-spacing: 0.20em
color: --dim (light) or rgba(255,255,255,0.40) (dark)
No background pills unless deliberately marking a status.
```

### Status pills
```
LIVE:     background rgba(34,197,94,0.12),  color #22C55E, border 1px solid rgba(34,197,94,0.30)
PENDING:  background rgba(255,255,255,0.05), color --dim,   border 1px solid --border-dark
PHASE N:  background rgba(232,163,61,0.10),  color --sol,   border 1px solid rgba(232,163,61,0.30)
```

### Dividers
```
1px solid --border-light (light)
1px solid --border-dark  (dark)
No decorative dividers. No gradient fades. No double lines.
```

---

## 6. Iconography

- No decorative icons. Icons serve function only.
- SVG inline when possible.
- Size: 16px or 20px. Never mix sizes within a component.
- Color: inherits from parent text color. Never --sol for icons unless interactive.

---

## 7. Logos and Brand Assets

| File | Background | Usage |
|------|-----------|-------|
| `brand_assets/OPERION_REDUCED.png` | Light gray | **Primary mark** — hero sections, print, presentations |
| `brand_assets/operion_emblem_light.svg` | Transparent | **Digital light** — nav, hero, footer ghost; use on white or `--blanc` |
| `brand_assets/OPERION_Sovereign_Emblem_FINAL.svg` | Obsidian `#0D0D0D` | **Digital dark (Register B)** — investor docs, classified assets |
| `operion_lockup_horizontal.svg` | Transparent | Full lockup for document headers |
| `operion_sigil.svg` | Transparent | Watermark — 10% opacity, bottom-right on video |

### Logo rules
- Minimum clear space: equal to the cap-height of the wordmark on all sides.
- **Never recolor** the emblem — the cobalt sphere and chrome frame are identity elements.
- `operion_emblem_light.svg` — for all Register A (light) surfaces. Transparent background; the metallic geometry reads against white or `--blanc`.
- `OPERION_Sovereign_Emblem_FINAL.svg` — for Register B (military) documents only. Has obsidian background baked in; functions as a seal.
- `OPERION_REDUCED.png` — use for hero-scale display (≥80px height). Place the file in `brand_assets/` after download.
- In nav: preferred height 32–40px. In hero: preferred height 64–96px.
- Wordmark "OPERION" in Space Grotesk 800 when no SVG/PNG is available.

---

## 8. Photography and Media

- Real photos only. No stock photography.
- Real screenshots, real data, real metrics.
- If client data appears in media: written consent required before any public use (see CLAUDE.md §2.5 and §1.9).
- Video watermark: `operion_sigil.svg`, bottom-right, 10% opacity.
- No AI-generated images in client-facing materials without disclosure.

---

## 9. Document Registers

OPERION produces two visual registers depending on audience:

### Register A — Technical Landing (operion.ai, client proposals)
- Background: `--blanc` (#F5F5F7)
- Text: `--ink` (#0D1420)
- Accent: `--cobalt` (#1A2B72)
- Secondary: `--chrome` (#B8BCC8)
- Tone: precise, clean, technical authority

### Register B — Military-Grade (investor briefs, internal ops, classified docs)
- Background: `--black` (#000000)
- Text: `#FFFFFF`
- Accent: `--cobalt-pop` (#5870CC) for data highlights
- Borders: 1px `rgba(255,255,255,0.10)`
- Tone: tactical, compressed, authoritative

Never mix registers within a single document.

---

## 10. Writing Style (Visual Copy Rules)

- Headlines: UPPERCASE, no punctuation except full stops and dashes.
- No exclamation marks. Ever.
- Numbers are always written numerically (not spelled out) in visual contexts.
- Currency: € prefix, period for thousands separator (German convention): €1.737
- Data claims must be sourced from CLAUDE.md, CORE_VISION.md, or verified client metrics.
- Never write "revolutionary," "game-changing," "disrupting," or any synonym.

---

## 11. Anti-patterns

The following are strictly prohibited:

- Gradients (except amber glow §5 and Register B depth gradient §12)
- Drop shadows (except amber glow §5 and glassmorphism §12)
- Border-radius > 4px
- Rounded buttons
- Color fills outside the defined palette
- Decorative illustrations or abstract graphics
- Stock photography
- Animated backgrounds, particles, or canvas effects
- More than 2 typefaces on a single page
- Former brand identities or legacy naming in any active file, comment, or metadata

---

## 12. Depth Effects — Register B Exceptions

The following are permitted **only in Register B (Military-Grade)** documents. Never apply in Register A (Technical Landing).

### Background depth gradient
```
radial-gradient(ellipse at 50% 0%, #0A0E1F 0%, #000000 55%)
```
- Maximum 2 color stops
- Maximum 4% lightness shift from black
- Radial direction only — no linear gradients
- Purpose: spatial depth perception, not decoration

### Glassmorphism (dark surfaces)
```
backdrop-filter: blur(8px–16px)
background: rgba(0, 0, 12, 0.60–0.88)     ← terminal/deep surfaces
         or rgba(15, 23, 41, 0.30–0.50)   ← card surfaces
```
- 1px border rule still applies (rgba(255,255,255,0.09) or rgba(232,163,61,0.28) for live elements)
- Permitted on: sticky nav, terminal block, featured pricing cards, live-data stat cells
- Never on: text paragraphs, footnotes, body containers

**Prohibited regardless of register:**
- Scroll-based parallax
- Canvas effects
- Animated backgrounds
- CSS `filter: blur()` on text content

---

*STYLE_GUIDE.md — OPERION v2.0 · April 26, 2026*  
*v2.0 — Identity refresh: cobalt/chrome system replaces amber/noche. New logo OPERION REDUCED introduced.*  
*This document is the source of truth. Changes require founder approval.*  
*Next review: July 2026*

---

## Relaciones
- [[CLAUDE]] — Master OS: origen de los tokens de marca y reglas de consentimiento de clientes (§1.9, §2.5)
- [[MASTER_BUSINESS_PLAN]] — Contexto de negocio para Register A (landing) y Register B (investor brief)
