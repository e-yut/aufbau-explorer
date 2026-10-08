# Aufbau — Electron Configuration Explorer Version 1.1 By Eylan Yutuc

Interactive desktop application that visualizes how electrons fill atomic orbitals according to the **Aufbau principle** (Madelung *n*+*ℓ* rule), **Hund’s rule**, and the **Pauli exclusion principle**.

> **New: Web Edition.** `index.html` + `app.py` run the same physics engine entirely in the browser via [Pyodide](https://pyodide.org) (Python compiled to WebAssembly) — no server, no build step, free to host on GitHub Pages. See [Web Edition](#web-edition-github-pages) below.

Ground-state spectroscopic exceptions (Cr, Cu, Nb, Mo, Pd, Ag, lanthanides, actinides, and others) are included and can be compared with pure Madelung filling.

![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Dependencies](https://img.shields.io/badge/deps-stdlib%20only-lightgrey)

---

## Features

- **Atom view** — concentric shells (K–Q) with electrons drawn as points; the latest electron is highlighted  
- **Fill-order view** — Madelung (*n*+*ℓ*) groups with occupancy chips  
- **Orbital boxes** — spin arrows (↑↓) per orbital, with *mℓ* labels when active  
- **Periodic table** — full 18-column layout plus f-block; exceptions marked in gold  
- **Playback controls** — play / step / reset, speed settings, electron slider  
- **Modes** — Observed (with exceptions) ↔ Pure Aufbau  
- **Search** — by atomic number, symbol, or name  
- **Keyboard shortcuts** — Space, ←→, `,` `.`, R  
- **CLI one-shot** — print a configuration without opening the GUI  
- **Responsive layout** — scrollable content; table and canvases adapt to window size  

---

## Requirements

- **Python 3.10 or later** (tested on 3.13)
- **tkinter** (included with most Python installs)

| Platform | Notes |
|----------|--------|
| Windows | Comes with the official installer and Microsoft Store builds |
| macOS   | Usually included; if missing, reinstall Python from [python.org](https://www.python.org) |
| Linux   | May need a separate package, e.g. `sudo apt install python3-tk` |

No third-party packages are required.

---

## Quick start

```bash
# Clone
git clone https://github.com/YOUR_USERNAME/aufbau-explorer.git
cd aufbau-explorer

# Run the GUI
python aufbau.py
```

### CLI (no window)

```bash
python aufbau.py Fe
python aufbau.py chromium
python aufbau.py 46
```

Example output:

```text
Fe (Iron, Z=26)
Configuration : 1s² 2s² 2p⁶ 3s² 3p⁶ 4s² 3d⁶
Condensed     : [Ar] 4s² 3d⁶
Unpaired e⁻   : 4
```

---

## Controls

| Input | Action |
|-------|--------|
| Click periodic-table cell | Select element |
| Search + Enter / Go | Jump to element |
| ▶ / Space | Play or pause filling animation |
| ⏭ / `.` | Place next electron |
| ⏮ / `,` | Remove last electron |
| ↺ / R | Reset to empty atom |
| Full | Jump to complete configuration |
| ← → | Previous / next element |
| Observed / Pure Aufbau | Toggle fill mode |
| Atom view / Fill order | Switch main diagram |
| Slow / Med / Fast | Animation speed |
| Electron slider | Scrub number of placed electrons |

---

## Physics notes

- **Madelung order** — subshells fill by increasing *n*+*ℓ*, then increasing *n*.  
- **Hund’s rule** — within a subshell, electrons occupy empty orbitals with parallel spin before pairing.  
- **Pauli exclusion** — each orbital holds at most two electrons of opposite spin.  
- **Exceptions** — gas-phase spectroscopic ground states (e.g. Cr is 4s¹ 3d⁵, not 4s² 3d⁴). Superheavy elements (Z > 103) use the Madelung prediction.

Configuration data follows standard NIST / textbook tables for Z ≤ 103.

---

## Project layout

```text
aufbau-explorer/
├── aufbau.py          # Single-file application (GUI + CLI)
├── README.md
├── LICENSE
├── requirements.txt   # Empty of third-party deps; documents Python version
└── .gitignore
```

---

## Development

The application is a single module with no external dependencies beyond the standard library. To check syntax:

```bash
python -m py_compile aufbau.py
```

To exercise the physics engine without a display:

```bash
python aufbau.py Cr
python aufbau.py Pd
python aufbau.py Lr
```

---

## Web Edition (GitHub Pages)

The repository root also contains a **static, client-side web app**:

```text
index.html        # UI shell + Pyodide CDN script tag
static/style.css   # styling
static/script.js    # DOM ⇄ Python glue (loads app.py into Pyodide)
app.py             # physics engine, extracted from aufbau-explorer_v1.1.py
                   # (no tkinter import — pure standard library, WASM-safe)
```

No Python server is involved: a visitor's browser downloads `pyodide.js`
from a CDN, boots a CPython 3.x WebAssembly runtime, fetches `app.py` as
plain text, and executes it in-browser. All physics (Madelung filling,
Hund's rule, Pauli exclusion, spectroscopic exceptions) runs locally on
the visitor's machine — nothing is sent to a server.

### Run it locally

Any static file server works (the browser must fetch `app.py` over
HTTP, not `file://`):

```bash
python -m http.server 8000
# then open http://localhost:8000/
```

### Publish to GitHub Pages

```bash
# 1. Initialize git (skip if already a repo) and commit the web files
git init
git add index.html app.py static README.md LICENSE requirements.txt .nojekyll
git commit -m "Add Pyodide web edition of Aufbau Explorer"

# 2. Create a new GitHub repository (replace YOUR_USERNAME)
gh repo create YOUR_USERNAME/aufbau-explorer --public --source=. --remote=origin
#    — or manually create the repo on github.com, then:
# git remote add origin https://github.com/YOUR_USERNAME/aufbau-explorer.git

# 3. Push
git branch -M main
git push -u origin main

# 4. Enable GitHub Pages
#    Settings → Pages → "Build and deployment" → Source: "Deploy from a branch"
#    Branch: main, Folder: / (root)  → Save
#    (equivalently via CLI: gh api repos/YOUR_USERNAME/aufbau-explorer/pages \
#       -f source[branch]=main -f source[path]=/)

# 5. Visit the live site a minute or two later:
#    https://YOUR_USERNAME.github.io/aufbau-explorer/
```

The included `.nojekyll` file disables Jekyll processing so GitHub
Pages serves `app.py` and `static/*` as plain static files untouched.

---

## Licence

MIT — see [LICENSE](LICENSE).

---

## Acknowledgements

Educational design inspired by interactive Aufbau demonstrations. Colour palette and interaction patterns follow a dark, high-contrast laboratory aesthetic suitable for teaching.
