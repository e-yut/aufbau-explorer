#!/usr/bin/env python3
"""
Aufbau Principle — Electron Configuration Explorer (GUI)
================================================
Interactive desktop application that visualizes how electrons fill atomic
orbitals according to the Aufbau principle (Madelung n+ℓ rule), Hund's rule,
and the Pauli exclusion principle.

Includes spectroscopic ground-state exceptions for transition metals,
lanthanides, and actinides.

Single-file application. Requires only the Python standard library
(tkinter). Compatible with Python 3.10–3.13.
"""

from __future__ import annotations

import math
import sys
from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Tuple

try:
    import tkinter as tk
    from tkinter import font as tkfont
    _HAS_TK = True
except ImportError:
    tk = None  # type: ignore
    tkfont = None  # type: ignore
    _HAS_TK = False

# ═══════════════════════════════════════════════════════════════════════════
# Colour palette (matches original web app)
# ═══════════════════════════════════════════════════════════════════════════

BG          = "#0b0c0e"
BG_ELEVATED = "#12141a"
SURFACE     = "#181b22"
SURFACE_H   = "#22262f"
FG          = "#e8e6e1"
MUTED       = "#8b8d93"
SUBTLE      = "#5c5e66"
ACCENT      = "#c5d0de"
ACCENT_FG   = "#0b0c0e"
BORDER      = "#2a2d36"
BORDER_S    = "#3d424e"
EXCEPTION   = "#c4a574"
HIGHLIGHT   = "#7eb8da"

# ═══════════════════════════════════════════════════════════════════════════
# Elements data (Z = 1 … 118)
# ═══════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class ElementInfo:
    z: int
    symbol: str
    name: str
    period: int
    group: int
    category: str
    mass: str


_RAW = """
1|H|Hydrogen|1|1|nonmetal|1.008
2|He|Helium|1|18|noble|4.003
3|Li|Lithium|2|1|alkali|6.94
4|Be|Beryllium|2|2|alkaline|9.012
5|B|Boron|2|13|metalloid|10.81
6|C|Carbon|2|14|nonmetal|12.011
7|N|Nitrogen|2|15|nonmetal|14.007
8|O|Oxygen|2|16|nonmetal|15.999
9|F|Fluorine|2|17|halogen|18.998
10|Ne|Neon|2|18|noble|20.180
11|Na|Sodium|3|1|alkali|22.990
12|Mg|Magnesium|3|2|alkaline|24.305
13|Al|Aluminium|3|13|post-transition|26.982
14|Si|Silicon|3|14|metalloid|28.085
15|P|Phosphorus|3|15|nonmetal|30.974
16|S|Sulfur|3|16|nonmetal|32.06
17|Cl|Chlorine|3|17|halogen|35.45
18|Ar|Argon|3|18|noble|39.948
19|K|Potassium|4|1|alkali|39.098
20|Ca|Calcium|4|2|alkaline|40.078
21|Sc|Scandium|4|3|transition|44.956
22|Ti|Titanium|4|4|transition|47.867
23|V|Vanadium|4|5|transition|50.942
24|Cr|Chromium|4|6|transition|51.996
25|Mn|Manganese|4|7|transition|54.938
26|Fe|Iron|4|8|transition|55.845
27|Co|Cobalt|4|9|transition|58.933
28|Ni|Nickel|4|10|transition|58.693
29|Cu|Copper|4|11|transition|63.546
30|Zn|Zinc|4|12|transition|65.38
31|Ga|Gallium|4|13|post-transition|69.723
32|Ge|Germanium|4|14|metalloid|72.630
33|As|Arsenic|4|15|metalloid|74.922
34|Se|Selenium|4|16|nonmetal|78.971
35|Br|Bromine|4|17|halogen|79.904
36|Kr|Krypton|4|18|noble|83.798
37|Rb|Rubidium|5|1|alkali|85.468
38|Sr|Strontium|5|2|alkaline|87.62
39|Y|Yttrium|5|3|transition|88.906
40|Zr|Zirconium|5|4|transition|91.224
41|Nb|Niobium|5|5|transition|92.906
42|Mo|Molybdenum|5|6|transition|95.95
43|Tc|Technetium|5|7|transition|[98]
44|Ru|Ruthenium|5|8|transition|101.07
45|Rh|Rhodium|5|9|transition|102.91
46|Pd|Palladium|5|10|transition|106.42
47|Ag|Silver|5|11|transition|107.87
48|Cd|Cadmium|5|12|transition|112.41
49|In|Indium|5|13|post-transition|114.82
50|Sn|Tin|5|14|post-transition|118.71
51|Sb|Antimony|5|15|metalloid|121.76
52|Te|Tellurium|5|16|metalloid|127.60
53|I|Iodine|5|17|halogen|126.90
54|Xe|Xenon|5|18|noble|131.29
55|Cs|Caesium|6|1|alkali|132.91
56|Ba|Barium|6|2|alkaline|137.33
57|La|Lanthanum|6|3|lanthanide|138.91
58|Ce|Cerium|6|3|lanthanide|140.12
59|Pr|Praseodymium|6|3|lanthanide|140.91
60|Nd|Neodymium|6|3|lanthanide|144.24
61|Pm|Promethium|6|3|lanthanide|[145]
62|Sm|Samarium|6|3|lanthanide|150.36
63|Eu|Europium|6|3|lanthanide|151.96
64|Gd|Gadolinium|6|3|lanthanide|157.25
65|Tb|Terbium|6|3|lanthanide|158.93
66|Dy|Dysprosium|6|3|lanthanide|162.50
67|Ho|Holmium|6|3|lanthanide|164.93
68|Er|Erbium|6|3|lanthanide|167.26
69|Tm|Thulium|6|3|lanthanide|168.93
70|Yb|Ytterbium|6|3|lanthanide|173.05
71|Lu|Lutetium|6|3|lanthanide|174.97
72|Hf|Hafnium|6|4|transition|178.49
73|Ta|Tantalum|6|5|transition|180.95
74|W|Tungsten|6|6|transition|183.84
75|Re|Rhenium|6|7|transition|186.21
76|Os|Osmium|6|8|transition|190.23
77|Ir|Iridium|6|9|transition|192.22
78|Pt|Platinum|6|10|transition|195.08
79|Au|Gold|6|11|transition|196.97
80|Hg|Mercury|6|12|transition|200.59
81|Tl|Thallium|6|13|post-transition|204.38
82|Pb|Lead|6|14|post-transition|207.2
83|Bi|Bismuth|6|15|post-transition|208.98
84|Po|Polonium|6|16|post-transition|[209]
85|At|Astatine|6|17|halogen|[210]
86|Rn|Radon|6|18|noble|[222]
87|Fr|Francium|7|1|alkali|[223]
88|Ra|Radium|7|2|alkaline|[226]
89|Ac|Actinium|7|3|actinide|[227]
90|Th|Thorium|7|3|actinide|232.04
91|Pa|Protactinium|7|3|actinide|231.04
92|U|Uranium|7|3|actinide|238.03
93|Np|Neptunium|7|3|actinide|[237]
94|Pu|Plutonium|7|3|actinide|[244]
95|Am|Americium|7|3|actinide|[243]
96|Cm|Curium|7|3|actinide|[247]
97|Bk|Berkelium|7|3|actinide|[247]
98|Cf|Californium|7|3|actinide|[251]
99|Es|Einsteinium|7|3|actinide|[252]
100|Fm|Fermium|7|3|actinide|[257]
101|Md|Mendelevium|7|3|actinide|[258]
102|No|Nobelium|7|3|actinide|[259]
103|Lr|Lawrencium|7|3|actinide|[266]
104|Rf|Rutherfordium|7|4|transition|[267]
105|Db|Dubnium|7|5|transition|[268]
106|Sg|Seaborgium|7|6|transition|[269]
107|Bh|Bohrium|7|7|transition|[270]
108|Hs|Hassium|7|8|transition|[277]
109|Mt|Meitnerium|7|9|unknown|[278]
110|Ds|Darmstadtium|7|10|unknown|[281]
111|Rg|Roentgenium|7|11|unknown|[282]
112|Cn|Copernicium|7|12|unknown|[285]
113|Nh|Nihonium|7|13|unknown|[286]
114|Fl|Flerovium|7|14|unknown|[289]
115|Mc|Moscovium|7|15|unknown|[290]
116|Lv|Livermorium|7|16|unknown|[293]
117|Ts|Tennessine|7|17|unknown|[294]
118|Og|Oganesson|7|18|unknown|[294]
""".strip()

ELEMENTS: List[ElementInfo] = []
ELEMENT_BY_Z: Dict[int, ElementInfo] = {}
ELEMENT_BY_SYMBOL: Dict[str, ElementInfo] = {}
ELEMENT_BY_NAME: Dict[str, ElementInfo] = {}

for _line in _RAW.splitlines():
    z_s, symbol, name, period, group, category, mass = _line.split("|")
    el = ElementInfo(int(z_s), symbol, name, int(period), int(group), category, mass)
    ELEMENTS.append(el)
    ELEMENT_BY_Z[el.z] = el
    ELEMENT_BY_SYMBOL[el.symbol.lower()] = el
    ELEMENT_BY_NAME[el.name.lower()] = el

MAX_Z = 118

CATEGORY_LABEL = {
    "alkali": "Alkali metal",
    "alkaline": "Alkaline earth",
    "transition": "Transition metal",
    "post-transition": "Post-transition metal",
    "metalloid": "Metalloid",
    "nonmetal": "Reactive nonmetal",
    "halogen": "Halogen",
    "noble": "Noble gas",
    "lanthanide": "Lanthanide",
    "actinide": "Actinide",
    "unknown": "Unknown properties",
}

CATEGORY_COLOUR = {
    "alkali": "#3d2a2a",
    "alkaline": "#3d352a",
    "transition": "#2a2d3d",
    "post-transition": "#2a3d35",
    "metalloid": "#353d2a",
    "nonmetal": "#2a3d3d",
    "halogen": "#2a353d",
    "noble": "#352a3d",
    "lanthanide": "#3d2a35",
    "actinide": "#3d2a2f",
    "unknown": "#2a2a2a",
}


def get_element(z: int) -> ElementInfo:
    return ELEMENT_BY_Z.get(z, ELEMENTS[0])


def table_cell(el: ElementInfo) -> Tuple[str, int, int]:
    if 57 <= el.z <= 71:
        return ("f", 0, el.z - 57 + 2)
    if 89 <= el.z <= 103:
        return ("f", 1, el.z - 89 + 2)
    if el.z == 2:
        return ("main", 0, 17)
    return ("main", el.period - 1, el.group - 1)


# ═══════════════════════════════════════════════════════════════════════════
# Physics
# ═══════════════════════════════════════════════════════════════════════════

LETTER = {0: "s", 1: "p", 2: "d", 3: "f"}
L_NAME = ("s", "p", "d", "f")
SHELL_NAME = ("K", "L", "M", "N", "O", "P", "Q")
NOBLE_Z = (0, 2, 10, 18, 36, 54, 86, 118)
NOBLE_SYMBOL = {2: "He", 10: "Ne", 18: "Ar", 36: "Kr", 54: "Xe", 86: "Rn", 118: "Og"}


@dataclass(frozen=True)
class Subshell:
    n: int
    l: int
    letter: str
    label: str
    capacity: int
    n_plus_l: int


def _make(n: int, l: int) -> Subshell:
    return Subshell(n, l, LETTER[l], f"{n}{LETTER[l]}", 2 * (2 * l + 1), n + l)


SUBSHELLS: List[Subshell] = [
    _make(1, 0), _make(2, 0), _make(2, 1), _make(3, 0), _make(3, 1),
    _make(4, 0), _make(3, 2), _make(4, 1), _make(5, 0), _make(4, 2),
    _make(5, 1), _make(6, 0), _make(4, 3), _make(5, 2), _make(6, 1),
    _make(7, 0), _make(5, 3), _make(6, 2), _make(7, 1),
]

EXCEPTIONS: Dict[int, Dict] = {
    24:  {"valence": {"3d": 5, "4s": 1}, "reason": "Exchange energy: a half-filled 3d\u2075 subshell plus 4s\u00b9 is lower than 4s\u00b2 3d\u2074."},
    29:  {"valence": {"3d": 10, "4s": 1}, "reason": "A filled 3d\u00b9\u2070 subshell plus 4s\u00b9 is lower than 4s\u00b2 3d\u2079."},
    41:  {"valence": {"4d": 4, "5s": 1}, "reason": "Niobium promotes a 5s electron into 4d, giving 5s\u00b9 4d\u2074."},
    42:  {"valence": {"4d": 5, "5s": 1}, "reason": "Like chromium: half-filled 4d\u2075 plus 5s\u00b9 is preferred over 5s\u00b2 4d\u2074."},
    44:  {"valence": {"4d": 7, "5s": 1}, "reason": "Ruthenium\u2019s 4d\u20135s gap favours 5s\u00b9 4d\u2077 over 5s\u00b2 4d\u2076."},
    45:  {"valence": {"4d": 8, "5s": 1}, "reason": "Rhodium\u2019s ground state is 5s\u00b9 4d\u2078 rather than 5s\u00b2 4d\u2077."},
    46:  {"valence": {"4d": 10, "5s": 0}, "reason": "Palladium uniquely empties 5s entirely, leaving a closed 4d\u00b9\u2070 shell."},
    47:  {"valence": {"4d": 10, "5s": 1}, "reason": "Silver follows copper: filled 4d\u00b9\u2070 plus 5s\u00b9."},
    57:  {"valence": {"4f": 0, "5d": 1, "6s": 2}, "reason": "At the start of the f-block, 5d lies below 4f, so lanthanum is 6s\u00b2 5d\u00b9."},
    58:  {"valence": {"4f": 1, "5d": 1, "6s": 2}, "reason": "Cerium keeps one 5d electron; 4f and 5d are nearly degenerate."},
    64:  {"valence": {"4f": 7, "5d": 1, "6s": 2}, "reason": "Gadolinium prefers a half-filled 4f\u2077 plus 5d\u00b9 over 4f\u2078."},
    78:  {"valence": {"4f": 14, "5d": 9, "6s": 1}, "reason": "Platinum is 5d\u2079 6s\u00b9 \u2014 the 5d\u20136s gap is small enough to unpair 6s."},
    79:  {"valence": {"4f": 14, "5d": 10, "6s": 1}, "reason": "Gold follows copper and silver: filled 5d\u00b9\u2070 plus 6s\u00b9."},
    89:  {"valence": {"5f": 0, "6d": 1, "7s": 2}, "reason": "Actinium mirrors lanthanum: 6d is occupied before 5f."},
    90:  {"valence": {"5f": 0, "6d": 2, "7s": 2}, "reason": "Thorium occupies 6d\u00b2 rather than beginning the 5f series."},
    91:  {"valence": {"5f": 2, "6d": 1, "7s": 2}, "reason": "Protactinium\u2019s ground state is 5f\u00b2 6d\u00b9 7s\u00b2."},
    92:  {"valence": {"5f": 3, "6d": 1, "7s": 2}, "reason": "Uranium keeps a 6d electron: 5f\u00b3 6d\u00b9 7s\u00b2."},
    93:  {"valence": {"5f": 4, "6d": 1, "7s": 2}, "reason": "Neptunium is 5f\u2074 6d\u00b9 7s\u00b2 rather than 5f\u2075 7s\u00b2."},
    96:  {"valence": {"5f": 7, "6d": 1, "7s": 2}, "reason": "Curium, like gadolinium, keeps a half-filled f\u2077 plus a d electron."},
    103: {"valence": {"5f": 14, "6d": 0, "7s": 2, "7p": 1}, "reason": "Relativistic effects put lawrencium\u2019s extra electron in 7p, not 6d."},
}


def noble_gas_before(z: int) -> int:
    core = 0
    for n in NOBLE_Z:
        if n < z:
            core = n
    return core


def is_exception(z: int) -> bool:
    return z in EXCEPTIONS


def exception_reason(z: int) -> Optional[str]:
    info = EXCEPTIONS.get(z)
    return info["reason"] if info else None


def occupancy_sum(occ: Dict[str, int]) -> int:
    return sum(occ.values())


def aufbau_occupancy(z: int) -> Dict[str, int]:
    occ: Dict[str, int] = {}
    left = max(0, z)
    for sub in SUBSHELLS:
        if left <= 0:
            break
        take = min(left, sub.capacity)
        occ[sub.label] = take
        left -= take
    return occ


def observed_occupancy(z: int) -> Dict[str, int]:
    exception = EXCEPTIONS.get(z)
    if not exception:
        return aufbau_occupancy(z)
    occ = aufbau_occupancy(noble_gas_before(z))
    for label, count in exception["valence"].items():
        if count <= 0:
            occ.pop(label, None)
        else:
            occ[label] = count
    return occ


def occupancy_for(z: int, mode: str) -> Dict[str, int]:
    return aufbau_occupancy(z) if mode == "aufbau" else observed_occupancy(z)


@dataclass
class Placement:
    index: int
    subshell: str
    n: int
    l: int
    ml: int
    ms: int
    rule: str


def _rule(already: int, orbs: int, using_exc: bool, exc_subs: Set[str], label: str) -> str:
    if using_exc and label in exc_subs:
        return "exception"
    if already == 0:
        return "aufbau"
    if already < orbs:
        return "hund"
    return "pauli"


def fill_sequence(z: int, mode: str) -> List[Placement]:
    occ = occupancy_for(z, mode)
    predicted = aufbau_occupancy(z)
    using_exc = mode == "observed" and is_exception(z)
    exc_subs: Set[str] = set()
    if using_exc:
        for sub in SUBSHELLS:
            if occ.get(sub.label, 0) != predicted.get(sub.label, 0):
                exc_subs.add(sub.label)
    placements: List[Placement] = []
    index = 0
    for sub in SUBSHELLS:
        count = occ.get(sub.label, 0)
        if count <= 0:
            continue
        orbs = 2 * sub.l + 1
        ups = min(count, orbs)
        downs = max(0, count - orbs)
        for i in range(ups):
            placements.append(Placement(index, sub.label, sub.n, sub.l, -sub.l + i, 1,
                                        _rule(i, orbs, using_exc, exc_subs, sub.label)))
            index += 1
        for i in range(downs):
            placements.append(Placement(index, sub.label, sub.n, sub.l, -sub.l + i, -1,
                                        _rule(ups + i, orbs, using_exc, exc_subs, sub.label)))
            index += 1
    return placements


def occupancy_from_placements(placements: List[Placement]) -> Dict[str, int]:
    occ: Dict[str, int] = {}
    for p in placements:
        occ[p.subshell] = occ.get(p.subshell, 0) + 1
    return occ


_SUPER = str.maketrans("0123456789", "\u2070\u00b9\u00b2\u00b3\u2074\u2075\u2076\u2077\u2078\u2079")


def to_sup(n: int) -> str:
    return str(n).translate(_SUPER)


def format_config(occ: Dict[str, int]) -> str:
    parts = [f"{sub.label}{to_sup(occ[sub.label])}" for sub in SUBSHELLS if occ.get(sub.label, 0) > 0]
    return " ".join(parts) or "\u2014"


def format_condensed(occ: Dict[str, int], z: int) -> str:
    filled = occupancy_sum(occ)
    core = 0
    for n in NOBLE_Z:
        if n == 0 or n > filled or n > z:
            continue
        core_occ = aufbau_occupancy(n)
        if all(occ.get(s.label, 0) >= core_occ.get(s.label, 0) for s in SUBSHELLS):
            core = n
    if core == 0:
        return format_config(occ)
    if filled == core:
        return f"[{NOBLE_SYMBOL[core]}]"
    core_occ = aufbau_occupancy(core)
    valence = {s.label: occ.get(s.label, 0) - core_occ.get(s.label, 0)
               for s in SUBSHELLS if occ.get(s.label, 0) - core_occ.get(s.label, 0) > 0}
    rest = format_config(valence)
    return f"[{NOBLE_SYMBOL[core]}] {rest}" if rest else f"[{NOBLE_SYMBOL[core]}]"


def unpaired_count(occ: Dict[str, int]) -> int:
    n = 0
    for sub in SUBSHELLS:
        c = occ.get(sub.label, 0)
        if c <= 0:
            continue
        orbs = 2 * sub.l + 1
        n += c if c <= orbs else 2 * orbs - c
    return n


def shell_occupancy(occ: Dict[str, int]) -> List[int]:
    shells = [0] * 7
    for sub in SUBSHELLS:
        shells[sub.n - 1] += occ.get(sub.label, 0)
    return shells


def highest_occupied_n(occ: Dict[str, int]) -> int:
    n = 1
    for sub in SUBSHELLS:
        if occ.get(sub.label, 0) > 0:
            n = sub.n
    return n


def expand_subshell(count: int, l: int) -> List[Tuple[int, bool, bool]]:
    orbs = 2 * l + 1
    states = [(-l + i, False, False) for i in range(orbs)]
    left = max(0, min(count, 2 * orbs))
    for i in range(orbs):
        if left <= 0:
            break
        states[i] = (states[i][0], True, False)
        left -= 1
    for i in range(orbs):
        if left <= 0:
            break
        ml, up, _ = states[i]
        states[i] = (ml, up, True)
        left -= 1
    return states


def describe_placement(p: Optional[Placement], z: int) -> str:
    if p is None:
        return "An empty atom. Press Play to watch electrons occupy orbitals in energy order."
    ell = L_NAME[p.l]
    ml = f"+{p.ml}" if p.ml > 0 else str(p.ml)
    ms = "+\u00bd" if p.ms == 1 else "\u2212\u00bd"
    qn = f"n={p.n}, \u2113={p.l} ({ell}), m\u2113={ml}, ms={ms}"
    el = get_element(z)
    if p.rule == "exception":
        return f"Exception in {el.name}: electron occupies {p.subshell} ({qn}). {exception_reason(z) or ''}"
    if p.rule == "hund":
        return f"Hund\u2019s rule \u2014 {p.subshell} still has an empty orbital, so this electron stays unpaired ({qn})."
    if p.rule == "pauli":
        return f"Pauli exclusion \u2014 {p.subshell} (m\u2113={ml}) already holds an electron; opposite spin ({qn})."
    return f"Aufbau principle \u2014 {p.subshell} is next by the n+\u2113 (Madelung) rule ({qn})."


def config_diff(z: int) -> List[Tuple[str, int, int]]:
    if not is_exception(z):
        return []
    a, o = aufbau_occupancy(z), observed_occupancy(z)
    return [(s.label, a.get(s.label, 0), o.get(s.label, 0))
            for s in SUBSHELLS if a.get(s.label, 0) != o.get(s.label, 0)]


def visible_subshells(occ: Dict[str, int], z: int) -> List[Subshell]:
    predicted = aufbau_occupancy(z)
    last = 0
    for i, sub in enumerate(SUBSHELLS):
        if occ.get(sub.label, 0) > 0 or predicted.get(sub.label, 0) > 0:
            last = i
    last = min(len(SUBSHELLS) - 1, last + 1)
    return SUBSHELLS[: last + 1]


# ═══════════════════════════════════════════════════════════════════════════
# GUI
# ═══════════════════════════════════════════════════════════════════════════

SPEEDS = [("Slow", 700), ("Med", 280), ("Fast", 90)]


class AufbauApp(tk.Tk if _HAS_TK else object):  # type: ignore[misc]
    def __init__(self) -> None:
        if not _HAS_TK:
            raise RuntimeError(
                "tkinter is required for the GUI. "
                "On Debian/Ubuntu: sudo apt install python3-tk"
            )
        super().__init__()
        self.title("Aufbau Principle \u2014 Electron Configuration Explorer version 1.1 by Eylan Yutuc")
        self.configure(bg=BG)
        self.geometry("1100x780")
        self.minsize(900, 640)
        self._resize_after = None

        self.z = 26
        self.electrons = 26
        self.mode = "observed"
        self.view = "atom"
        self.playing = False
        self.speed_ms = 280
        self._play_after: Optional[str] = None
        self._cell_buttons: Dict[int, tk.Button] = {}

        self._build_fonts()
        self._build_ui()
        self._bind_keys()
        self.refresh()

    def _build_fonts(self) -> None:
        self.font_title   = tkfont.Font(family="Georgia", size=22, slant="italic")
        self.font_heading = tkfont.Font(family="Helvetica", size=13, weight="bold")
        self.font_body    = tkfont.Font(family="Helvetica", size=11)
        self.font_small   = tkfont.Font(family="Helvetica", size=9)
        self.font_mono    = tkfont.Font(family="Courier", size=11)
        self.font_mono_sm = tkfont.Font(family="Courier", size=9)
        self.font_micro   = tkfont.Font(family="Courier", size=7)

    def _build_ui(self) -> None:
        # Scrollable outer shell so content stays reachable at any window size
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        outer = tk.Frame(self, bg=BG)
        outer.grid(row=0, column=0, sticky="nsew")
        outer.columnconfigure(0, weight=1)
        outer.rowconfigure(0, weight=1)

        self._scroll_canvas = tk.Canvas(outer, bg=BG, highlightthickness=0)
        self._scroll_canvas.grid(row=0, column=0, sticky="nsew")
        vbar = tk.Scrollbar(outer, orient="vertical", command=self._scroll_canvas.yview,
                            bg=BG_ELEVATED, troughcolor=BG, activebackground=BORDER_S)
        vbar.grid(row=0, column=1, sticky="ns")
        self._scroll_canvas.configure(yscrollcommand=vbar.set)

        self._content = tk.Frame(self._scroll_canvas, bg=BG)
        self._content_win = self._scroll_canvas.create_window((0, 0), window=self._content, anchor="nw")

        def _on_content_configure(_event=None):
            self._scroll_canvas.configure(scrollregion=self._scroll_canvas.bbox("all"))

        def _on_canvas_configure(event):
            self._scroll_canvas.itemconfigure(self._content_win, width=event.width)

        self._content.bind("<Configure>", _on_content_configure)
        self._scroll_canvas.bind("<Configure>", _on_canvas_configure)

        # Mouse-wheel scrolling (Windows / macOS / Linux)
        def _wheel(event):
            delta = 0
            if getattr(event, "num", None) == 5 or event.delta < 0:
                delta = 1
            elif getattr(event, "num", None) == 4 or event.delta > 0:
                delta = -1
            if delta:
                self._scroll_canvas.yview_scroll(delta, "units")

        self.bind_all("<MouseWheel>", _wheel)
        self.bind_all("<Button-4>", _wheel)
        self.bind_all("<Button-5>", _wheel)

        root = self._content
        root.columnconfigure(0, weight=1)

        # ── Header ────────────────────────────────────────────────────────
        header = tk.Frame(root, bg=BG, padx=16, pady=10)
        header.grid(row=0, column=0, sticky="ew")
        header.columnconfigure(1, weight=1)

        tk.Label(header, text="Aufbau Principle Explorer v1.1", font=self.font_title, fg=FG, bg=BG).grid(
            row=0, column=0, sticky="w")

        search_fr = tk.Frame(header, bg=BG)
        search_fr.grid(row=0, column=1, sticky="e")
        tk.Label(search_fr, text="Search", font=self.font_small, fg=MUTED, bg=BG).pack(
            side="left", padx=(0, 6))
        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(
            search_fr, textvariable=self.search_var, width=16,
            bg=SURFACE, fg=FG, insertbackground=FG, relief="flat",
            font=self.font_body, highlightthickness=1,
            highlightbackground=BORDER, highlightcolor=ACCENT,
        )
        self.search_entry.pack(side="left")
        self.search_entry.bind("<Return>", self._on_search)
        tk.Button(
            search_fr, text="Go", command=self._on_search,
            bg=SURFACE, fg=FG, activebackground=SURFACE_H, activeforeground=FG,
            relief="flat", font=self.font_small, padx=8, cursor="hand2",
        ).pack(side="left", padx=(4, 0))

        # ── Main two-column area ──────────────────────────────────────────
        main = tk.Frame(root, bg=BG, padx=12, pady=4)
        main.grid(row=1, column=0, sticky="nsew")
        main.columnconfigure(0, weight=3, minsize=320)
        main.columnconfigure(1, weight=2, minsize=280)
        main.rowconfigure(0, weight=1)
        root.rowconfigure(1, weight=1)

        left = tk.Frame(main, bg=BG)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        left.columnconfigure(0, weight=1)
        left.rowconfigure(2, weight=1, minsize=220)

        right = tk.Frame(main, bg=BG)
        right.grid(row=0, column=1, sticky="nsew")
        right.columnconfigure(0, weight=1)

        # Element info card
        self.info_card = tk.Frame(left, bg=BG_ELEVATED, padx=12, pady=10)
        self.info_card.grid(row=0, column=0, sticky="ew", pady=(0, 6))
        self.info_card.columnconfigure(1, weight=1)

        self.lbl_symbol = tk.Label(
            self.info_card, text="Fe",
            font=tkfont.Font(family="Helvetica", size=32, weight="bold"),
            fg=FG, bg=BG_ELEVATED,
        )
        self.lbl_symbol.grid(row=0, column=0, rowspan=3, sticky="w", padx=(0, 12))

        self.lbl_name = tk.Label(
            self.info_card, text="Iron", font=self.font_heading, fg=FG, bg=BG_ELEVATED, anchor="w")
        self.lbl_name.grid(row=0, column=1, sticky="w")
        self.lbl_meta = tk.Label(
            self.info_card, text="", font=self.font_small, fg=MUTED, bg=BG_ELEVATED, anchor="w")
        self.lbl_meta.grid(row=1, column=1, sticky="w")
        self.lbl_config = tk.Label(
            self.info_card, text="", font=self.font_mono, fg=ACCENT, bg=BG_ELEVATED, anchor="w")
        self.lbl_config.grid(row=2, column=1, sticky="w")
        self.lbl_condensed = tk.Label(
            self.info_card, text="", font=self.font_mono_sm, fg=MUTED, bg=BG_ELEVATED, anchor="w")
        self.lbl_condensed.grid(row=3, column=1, sticky="w")
        self.lbl_exception = tk.Label(
            self.info_card, text="", font=self.font_small, fg=EXCEPTION, bg=BG_ELEVATED,
            anchor="w", justify="left", wraplength=400,
        )
        self.lbl_exception.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(4, 0))

        # View toggle
        view_bar = tk.Frame(left, bg=BG)
        view_bar.grid(row=1, column=0, sticky="ew")
        self.btn_view_atom = self._toggle_btn(view_bar, "Atom view", lambda: self._set_view("atom"))
        self.btn_view_atom.pack(side="left", padx=(0, 4))
        self.btn_view_order = self._toggle_btn(view_bar, "Fill order", lambda: self._set_view("order"))
        self.btn_view_order.pack(side="left")

        # Atom / orbital canvas — expands with left column
        canvas_fr = tk.Frame(left, bg=BG_ELEVATED)
        canvas_fr.grid(row=2, column=0, sticky="nsew", pady=(4, 0))
        canvas_fr.columnconfigure(0, weight=1)
        canvas_fr.rowconfigure(0, weight=1)

        self.atom_canvas = tk.Canvas(
            canvas_fr, bg=BG_ELEVATED, highlightthickness=0, height=320)
        self.atom_canvas.grid(row=0, column=0, sticky="nsew", padx=6, pady=6)
        # Keep a minimum height for the atom diagram area
        canvas_fr.rowconfigure(0, weight=1, minsize=220)
        self.atom_canvas.bind("<Configure>", self._on_atom_resize)

        self.lbl_placement = tk.Label(
            left, text="", font=self.font_small, fg=MUTED, bg=BG,
            justify="left", anchor="w", wraplength=400,
        )
        self.lbl_placement.grid(row=3, column=0, sticky="ew", pady=(6, 0))

        # ── Right: orbital boxes ──────────────────────────────────────────
        orb_card = tk.Frame(right, bg=BG_ELEVATED, padx=10, pady=8)
        orb_card.grid(row=0, column=0, sticky="ew", pady=(0, 6))
        orb_card.columnconfigure(0, weight=1)
        tk.Label(orb_card, text="Orbital boxes", font=self.font_heading, fg=FG, bg=BG_ELEVATED).grid(
            row=0, column=0, sticky="w")
        self.orb_canvas = tk.Canvas(orb_card, bg=BG_ELEVATED, highlightthickness=0, height=200)
        self.orb_canvas.grid(row=1, column=0, sticky="ew", pady=(4, 0))
        self.orb_canvas.bind("<Configure>", self._on_orb_resize)

        # Controls
        ctrl = tk.Frame(right, bg=BG_ELEVATED, padx=10, pady=8)
        ctrl.grid(row=1, column=0, sticky="ew", pady=(0, 6))
        ctrl.columnconfigure(0, weight=1)

        tk.Label(ctrl, text="Electrons", font=self.font_small, fg=MUTED, bg=BG_ELEVATED).grid(
            row=0, column=0, sticky="w")
        slider_fr = tk.Frame(ctrl, bg=BG_ELEVATED)
        slider_fr.grid(row=1, column=0, sticky="ew", pady=(2, 6))
        slider_fr.columnconfigure(0, weight=1)
        self.electron_var = tk.IntVar(value=26)
        self.slider = tk.Scale(
            slider_fr, from_=0, to=26, orient="horizontal", variable=self.electron_var,
            command=self._on_slider, bg=BG_ELEVATED, fg=FG, troughcolor=SURFACE,
            highlightthickness=0, activebackground=ACCENT,
            showvalue=0, borderwidth=0,
        )
        self.slider.grid(row=0, column=0, sticky="ew")
        self.lbl_e_count = tk.Label(
            slider_fr, text="26 / 26", font=self.font_mono_sm, fg=FG, bg=BG_ELEVATED, width=8)
        self.lbl_e_count.grid(row=0, column=1, padx=(6, 0))

        btn_row = tk.Frame(ctrl, bg=BG_ELEVATED)
        btn_row.grid(row=2, column=0, sticky="w", pady=(0, 6))
        self._ctrl_btn(btn_row, "\u23ee", self.step_back).pack(side="left", padx=2)
        self.btn_play = self._ctrl_btn(btn_row, "\u25b6", self.toggle_play)
        self.btn_play.pack(side="left", padx=2)
        self._ctrl_btn(btn_row, "\u23ed", self.step_forward).pack(side="left", padx=2)
        self._ctrl_btn(btn_row, "\u21ba", self.reset).pack(side="left", padx=2)
        self._ctrl_btn(btn_row, "Full", self.fill_all).pack(side="left", padx=2)

        speed_fr = tk.Frame(ctrl, bg=BG_ELEVATED)
        speed_fr.grid(row=3, column=0, sticky="w", pady=(0, 6))
        tk.Label(speed_fr, text="Speed", font=self.font_small, fg=MUTED, bg=BG_ELEVATED).pack(
            side="left", padx=(0, 8))
        self.speed_btns = {}
        for label, ms in SPEEDS:
            b = self._toggle_btn(speed_fr, label, lambda m=ms, l=label: self._set_speed(m, l))
            b.pack(side="left", padx=2)
            self.speed_btns[label] = b

        mode_fr = tk.Frame(ctrl, bg=BG_ELEVATED)
        mode_fr.grid(row=4, column=0, sticky="w")
        tk.Label(mode_fr, text="Mode", font=self.font_small, fg=MUTED, bg=BG_ELEVATED).pack(
            side="left", padx=(0, 8))
        self.btn_mode_obs = self._toggle_btn(mode_fr, "Observed", lambda: self._set_mode("observed"))
        self.btn_mode_obs.pack(side="left", padx=2)
        self.btn_mode_auf = self._toggle_btn(mode_fr, "Pure Aufbau", lambda: self._set_mode("aufbau"))
        self.btn_mode_auf.pack(side="left", padx=2)

        # Educational cards (compact)
        edu = tk.Frame(right, bg=BG)
        edu.grid(row=2, column=0, sticky="ew")
        for title, body in [
            ("Aufbau", "Electrons enter the vacant orbital of lowest energy (Madelung n+\u2113 rule)."),
            ("Hund", "Degenerate orbitals fill singly with parallel spins before pairing."),
            ("Pauli", "No two electrons share the same four quantum numbers."),
        ]:
            card = tk.Frame(edu, bg=BG_ELEVATED, padx=8, pady=6)
            card.pack(fill="x", pady=2)
            tk.Label(card, text=title,
                     font=tkfont.Font(family="Georgia", size=11, slant="italic"),
                     fg=FG, bg=BG_ELEVATED).pack(anchor="w")
            tk.Label(card, text=body, font=self.font_small, fg=MUTED, bg=BG_ELEVATED,
                     wraplength=300, justify="left").pack(anchor="w")

        # ── Periodic table (scales with width) ────────────────────────────
        pt_outer = tk.Frame(root, bg=BG, padx=12, pady=6)
        pt_outer.grid(row=2, column=0, sticky="ew")
        pt_outer.columnconfigure(0, weight=1)

        pt_header = tk.Frame(pt_outer, bg=BG)
        pt_header.grid(row=0, column=0, sticky="ew")
        tk.Label(pt_header, text="Periodic table", font=self.font_heading, fg=FG, bg=BG).pack(
            side="left")
        tk.Label(pt_header, text="  \u25cf Ground-state exception", font=self.font_small,
                 fg=EXCEPTION, bg=BG).pack(side="left", padx=(8, 0))

        self.pt_frame = tk.Frame(pt_outer, bg=BG)
        self.pt_frame.grid(row=1, column=0, sticky="ew", pady=(4, 0))
        self.pt_frame.bind("<Configure>", self._on_pt_resize)
        self._pt_cell_w = 36
        self._build_periodic_table()

        # Status
        self.status = tk.Label(
            root,
            text="Space: play/pause  \u00b7  \u2190\u2192: element  \u00b7  , . : step  \u00b7  scroll if needed",
            font=self.font_small, fg=SUBTLE, bg=BG, anchor="w", padx=12, pady=4,
        )
        self.status.grid(row=3, column=0, sticky="ew")

        # Redraw once widgets have real sizes
        self.after(50, self._force_redraw)

    def _force_redraw(self) -> None:
        self.refresh()
        self._scroll_canvas.configure(scrollregion=self._scroll_canvas.bbox("all"))

    def _on_atom_resize(self, event) -> None:
        if event.width < 40 or event.height < 40:
            return
        self._schedule_redraw()

    def _on_orb_resize(self, event) -> None:
        if event.width < 40:
            return
        self._schedule_redraw()

    def _on_pt_resize(self, event) -> None:
        if event.width < 100:
            return
        # Target ~18 columns with small gaps
        new_w = max(22, min(42, (event.width - 40) // 18))
        if abs(new_w - self._pt_cell_w) >= 2:
            self._pt_cell_w = new_w
            self._build_periodic_table()
            self.refresh()

    def _schedule_redraw(self) -> None:
        if self._resize_after is not None:
            self.after_cancel(self._resize_after)
        self._resize_after = self.after(40, self._do_redraw)

    def _do_redraw(self) -> None:
        self._resize_after = None
        el = get_element(self.z)
        placements = fill_sequence(self.z, self.mode)[: self.electrons]
        occ = occupancy_from_placements(placements)
        last = placements[-1] if placements else None
        if self.view == "atom":
            self._draw_atom(occ, el.symbol, last)
        else:
            self._draw_madelung(occ, last)
        self._draw_orbital_boxes(occ, last)
        # Keep placement text wrap in sync with width
        w = max(self.atom_canvas.winfo_width(), 200)
        self.lbl_placement.configure(wraplength=max(w - 20, 200))
        self.lbl_exception.configure(wraplength=max(w - 40, 200))

    def _toggle_btn(self, parent, text, cmd) -> tk.Button:
        return tk.Button(
            parent, text=text, command=cmd,
            bg=SURFACE, fg=MUTED, activebackground=SURFACE_H, activeforeground=FG,
            relief="flat", font=self.font_small, padx=8, pady=3, cursor="hand2",
            highlightthickness=0, bd=0,
        )

    def _ctrl_btn(self, parent, text, cmd) -> tk.Button:
        return tk.Button(
            parent, text=text, command=cmd,
            bg=SURFACE, fg=FG, activebackground=SURFACE_H, activeforeground=FG,
            relief="flat", font=self.font_body, padx=10, pady=4, cursor="hand2",
            highlightthickness=0, bd=0, width=4,
        )

    def _build_periodic_table(self) -> None:
        for w in self.pt_frame.winfo_children():
            w.destroy()
        self._cell_buttons.clear()
        main: List[List[Optional[ElementInfo]]] = [[None] * 18 for _ in range(7)]
        fblock: List[List[Optional[ElementInfo]]] = [[None] * 18 for _ in range(2)]
        for el in ELEMENTS:
            sec, row, col = table_cell(el)
            if sec == "main":
                main[row][col] = el
            else:
                fblock[row][col] = el

        cw = getattr(self, "_pt_cell_w", 36)
        # Scale font slightly with cell size
        pt_font = tkfont.Font(family="Courier", size=max(6, min(9, cw // 4)))

        for r, row in enumerate(main):
            for c, el in enumerate(row):
                if r == 5 and c == 2:
                    self._pt_marker(r, c, "57\u201371", cw, pt_font)
                    continue
                if r == 6 and c == 2:
                    self._pt_marker(r, c, "89\u2013103", cw, pt_font)
                    continue
                if el is None:
                    tk.Frame(self.pt_frame, width=cw, height=int(cw * 0.9), bg=BG).grid(
                        row=r, column=c, padx=1, pady=1)
                else:
                    self._pt_cell(el, r, c, cw, pt_font)

        tk.Frame(self.pt_frame, height=4, bg=BG).grid(row=7, column=0, columnspan=18)

        for r, row in enumerate(fblock):
            grid_r = 8 + r
            for c, el in enumerate(row):
                if c == 0:
                    lbl = "Ln" if r == 0 else "An"
                    tk.Label(self.pt_frame, text=lbl, font=pt_font, fg=SUBTLE, bg=BG,
                             width=3).grid(row=grid_r, column=0, columnspan=2, sticky="e", padx=1)
                    continue
                if c == 1:
                    continue
                if el is None:
                    tk.Frame(self.pt_frame, width=cw, height=int(cw * 0.9), bg=BG).grid(
                        row=grid_r, column=c, padx=1, pady=1)
                else:
                    self._pt_cell(el, grid_r, c, cw, pt_font)

        # Let columns expand evenly
        for c in range(18):
            self.pt_frame.columnconfigure(c, weight=1, minsize=max(cw - 4, 16))

    def _pt_marker(self, r, c, text, cw=36, pt_font=None) -> None:
        if pt_font is None:
            pt_font = self.font_micro
        tk.Label(
            self.pt_frame, text=text, font=pt_font, fg=MUTED, bg=BG_ELEVATED,
            width=max(3, cw // 8), height=2,
        ).grid(row=r, column=c, padx=1, pady=1, sticky="nsew")

    def _pt_cell(self, el, r, c, cw=36, pt_font=None) -> None:
        if pt_font is None:
            pt_font = self.font_micro
        bg = CATEGORY_COLOUR.get(el.category, SURFACE)
        btn = tk.Button(
            self.pt_frame, text=f"{el.z}\n{el.symbol}", font=pt_font,
            fg=EXCEPTION if is_exception(el.z) else FG, bg=bg,
            activebackground=ACCENT, activeforeground=ACCENT_FG,
            relief="flat", cursor="hand2",
            highlightthickness=0, bd=0,
            command=lambda z=el.z: self.select_element(z),
        )
        btn.grid(row=r, column=c, padx=1, pady=1, sticky="nsew")
        # Prefer pixel size over character width for consistent scaling
        btn.configure(width=max(3, cw // 8), height=2)
        self._cell_buttons[el.z] = btn

    def select_element(self, z: int) -> None:
        self.z = max(1, min(MAX_Z, z))
        self.electrons = self.z
        self.playing = False
        self._cancel_play()
        self.electron_var.set(self.electrons)
        self.slider.configure(to=self.z)
        self.refresh()

    def set_electrons(self, n: int) -> None:
        self.electrons = max(0, min(self.z, n))
        self.electron_var.set(self.electrons)
        self.refresh()

    def step_forward(self) -> None:
        if self.electrons < self.z:
            self.set_electrons(self.electrons + 1)

    def step_back(self) -> None:
        if self.electrons > 0:
            self.set_electrons(self.electrons - 1)

    def reset(self) -> None:
        self.playing = False
        self._cancel_play()
        self.set_electrons(0)

    def fill_all(self) -> None:
        self.playing = False
        self._cancel_play()
        self.set_electrons(self.z)

    def toggle_play(self) -> None:
        if self.playing:
            self.playing = False
            self._cancel_play()
            self.btn_play.configure(text="\u25b6")
        else:
            if self.electrons >= self.z:
                self.set_electrons(0)
            self.playing = True
            self.btn_play.configure(text="\u23f8")
            self._play_tick()

    def _play_tick(self) -> None:
        if not self.playing:
            return
        if self.electrons < self.z:
            self.set_electrons(self.electrons + 1)
            self._play_after = self.after(self.speed_ms, self._play_tick)
        else:
            self.playing = False
            self.btn_play.configure(text="\u25b6")

    def _cancel_play(self) -> None:
        if self._play_after is not None:
            self.after_cancel(self._play_after)
            self._play_after = None
        self.btn_play.configure(text="\u25b6")

    def _set_speed(self, ms: int, label: str) -> None:
        self.speed_ms = ms
        for l, b in self.speed_btns.items():
            b.configure(bg=ACCENT if l == label else SURFACE, fg=ACCENT_FG if l == label else MUTED)

    def _set_mode(self, mode: str) -> None:
        self.mode = mode
        self.electrons = self.z
        self.electron_var.set(self.electrons)
        self.refresh()

    def _set_view(self, view: str) -> None:
        self.view = view
        self.refresh()

    def _on_slider(self, val: str) -> None:
        self.playing = False
        self._cancel_play()
        self.electrons = int(float(val))
        self.refresh()

    def _on_search(self, event=None) -> None:
        q = self.search_var.get().strip()
        if not q:
            return
        matched = self._match_query(q)
        if matched is not None:
            self.select_element(matched)
            self.search_var.set("")
        else:
            self.status.configure(text=f"Element not found: {q!r}")

    def _match_query(self, q: str) -> Optional[int]:
        s = q.strip().lower()
        if s.isdigit():
            n = int(s)
            return n if 1 <= n <= MAX_Z else None
        if s in ELEMENT_BY_SYMBOL:
            return ELEMENT_BY_SYMBOL[s].z
        if s in ELEMENT_BY_NAME:
            return ELEMENT_BY_NAME[s].z
        for el in ELEMENTS:
            if el.name.lower().startswith(s) or el.symbol.lower().startswith(s):
                return el.z
        return None

    def _bind_keys(self) -> None:
        self.bind("<space>", lambda e: self.toggle_play())
        self.bind("<Left>", lambda e: self.select_element(self.z - 1))
        self.bind("<Right>", lambda e: self.select_element(self.z + 1))
        self.bind("<comma>", lambda e: self.step_back())
        self.bind("<period>", lambda e: self.step_forward())
        self.bind("<r>", lambda e: self.reset())
        self.focus_set()

    def refresh(self) -> None:
        el = get_element(self.z)
        placements = fill_sequence(self.z, self.mode)[: self.electrons]
        occ = occupancy_from_placements(placements)
        full_occ = occupancy_for(self.z, self.mode)
        last = placements[-1] if placements else None

        self.lbl_symbol.configure(text=el.symbol)
        self.lbl_name.configure(text=el.name)
        self.lbl_meta.configure(
            text=f"Z = {el.z}  \u00b7  {CATEGORY_LABEL.get(el.category, el.category)}  \u00b7  "
                 f"Period {el.period}, Group {el.group}  \u00b7  {el.mass} u"
        )
        self.lbl_config.configure(text=format_config(full_occ))
        self.lbl_condensed.configure(
            text=f"{format_condensed(full_occ, self.z)}   \u00b7   unpaired: {unpaired_count(full_occ)}"
        )
        if is_exception(self.z) and self.mode == "observed":
            reason = exception_reason(self.z) or ""
            diffs = config_diff(self.z)
            diff_s = "  ".join(f"{lb}: {p}\u2192{o}" for lb, p, o in diffs)
            self.lbl_exception.configure(
                text=f"\u2605 Exception \u2014 {reason}  ({diff_s})" if diff_s else f"\u2605 Exception \u2014 {reason}"
            )
        else:
            self.lbl_exception.configure(text="")

        self.lbl_e_count.configure(text=f"{self.electrons} / {self.z}")
        self.lbl_placement.configure(text=describe_placement(last, self.z))

        if self.mode == "observed":
            self.btn_mode_obs.configure(bg=ACCENT, fg=ACCENT_FG)
            self.btn_mode_auf.configure(bg=SURFACE, fg=MUTED)
        else:
            self.btn_mode_auf.configure(bg=ACCENT, fg=ACCENT_FG)
            self.btn_mode_obs.configure(bg=SURFACE, fg=MUTED)

        if self.view == "atom":
            self.btn_view_atom.configure(bg=ACCENT, fg=ACCENT_FG)
            self.btn_view_order.configure(bg=SURFACE, fg=MUTED)
        else:
            self.btn_view_order.configure(bg=ACCENT, fg=ACCENT_FG)
            self.btn_view_atom.configure(bg=SURFACE, fg=MUTED)

        for l, b in self.speed_btns.items():
            ms = next(m for lab, m in SPEEDS if lab == l)
            b.configure(bg=ACCENT if ms == self.speed_ms else SURFACE,
                        fg=ACCENT_FG if ms == self.speed_ms else MUTED)

        for z, btn in self._cell_buttons.items():
            el2 = get_element(z)
            bg = CATEGORY_COLOUR.get(el2.category, SURFACE)
            if z == self.z:
                btn.configure(bg=ACCENT, fg=ACCENT_FG)
            else:
                btn.configure(bg=bg, fg=EXCEPTION if is_exception(z) else FG)

        if self.view == "atom":
            self._draw_atom(occ, el.symbol, last)
        else:
            self._draw_madelung(occ, last)
        self._draw_orbital_boxes(occ, last)

    def _draw_atom(self, occ, symbol, last) -> None:
        c = self.atom_canvas
        c.delete("all")
        w = max(c.winfo_width(), 200)
        h = max(c.winfo_height(), 180)
        cx, cy = w / 2, h / 2
        max_r = min(w, h) / 2 - 30
        shells = shell_occupancy(occ)
        max_n = max(2, highest_occupied_n(occ))
        c.create_oval(cx - max_r - 10, cy - max_r - 10, cx + max_r + 10, cy + max_r + 10,
                      outline="", fill="#121820")
        for i in range(max_n):
            n = i + 1
            r = 28 + (n / max_n) * (max_r - 28)
            c.create_oval(cx - r, cy - r, cx + r, cy + r, outline=BORDER, width=1)
            c.create_text(cx + r + 12, cy, text=SHELL_NAME[i], fill=SUBTLE, font=self.font_micro, anchor="w")
            count = shells[i] if i < len(shells) else 0
            for k in range(count):
                angle = (k / max(count, 1)) * math.pi * 2 - math.pi / 2
                ex = cx + r * math.cos(angle)
                ey = cy + r * math.sin(angle)
                is_last = last is not None and last.n == n and k == count - 1
                rad = 5 if is_last else 3.5
                colour = HIGHLIGHT if is_last else FG
                c.create_oval(ex - rad, ey - rad, ex + rad, ey + rad, fill=colour, outline="")
        c.create_oval(cx - 20, cy - 20, cx + 20, cy + 20, fill=SURFACE, outline=BORDER_S, width=1)
        c.create_text(cx, cy, text=symbol, fill=FG, font=self.font_heading)

    def _draw_madelung(self, occ, last) -> None:
        c = self.atom_canvas
        c.delete("all")
        w = max(c.winfo_width(), 200)
        h = max(c.winfo_height(), 180)
        c.create_text(12, 14, text="Madelung (n+\u2113) fill order", fill=MUTED, font=self.font_small, anchor="w")
        groups: Dict[int, List[Subshell]] = {}
        for sub in SUBSHELLS:
            groups.setdefault(sub.n_plus_l, []).append(sub)
        y = 40
        for npl in sorted(groups):
            subs = sorted(groups[npl], key=lambda s: s.n)
            x = 20
            c.create_text(x, y + 10, text=f"n+\u2113={npl}", fill=SUBTLE, font=self.font_micro, anchor="w")
            x += 50
            for sub in subs:
                count = occ.get(sub.label, 0)
                filled = count >= sub.capacity
                partial = 0 < count < sub.capacity
                is_hl = last is not None and last.subshell == sub.label
                if is_hl:
                    bg, fg = ACCENT, ACCENT_FG
                elif filled:
                    bg, fg = "#2a3d35", FG
                elif partial:
                    bg, fg = "#2a2d3d", FG
                else:
                    bg, fg = SURFACE, SUBTLE
                bw, bh = 48, 28
                c.create_rectangle(x, y, x + bw, y + bh, fill=bg, outline=BORDER if not is_hl else ACCENT)
                c.create_text(x + bw / 2, y + 10, text=sub.label, fill=fg, font=self.font_mono_sm)
                c.create_text(x + bw / 2, y + 22, text=f"{count}/{sub.capacity}",
                              fill=MUTED if not is_hl else ACCENT_FG, font=self.font_micro)
                x += bw + 6
            y += 38
            if y > h - 20:
                break

    def _draw_orbital_boxes(self, occ, last) -> None:
        c = self.orb_canvas
        c.delete("all")
        subs = visible_subshells(occ, self.z)
        y = 4
        box_w, box_h = 22, 28
        for sub in subs:
            count = occ.get(sub.label, 0)
            states = expand_subshell(count, sub.l)
            is_hl = last is not None and last.subshell == sub.label
            label_colour = HIGHLIGHT if is_hl else (MUTED if count == 0 else FG)
            c.create_text(6, y + box_h / 2, text=sub.label, fill=label_colour, font=self.font_mono_sm, anchor="w")
            x = 42
            for ml, up, down in states:
                outline = ACCENT if (is_hl and last and last.ml == ml) else BORDER
                c.create_rectangle(x, y, x + box_w, y + box_h, fill=SURFACE, outline=outline)
                if up:
                    c.create_line(x + 7, y + 20, x + 7, y + 6, fill=FG, width=1.5,
                                  arrow=tk.LAST, arrowshape=(5, 5, 2))
                if down:
                    c.create_line(x + 15, y + 6, x + 15, y + 20, fill=FG, width=1.5,
                                  arrow=tk.LAST, arrowshape=(5, 5, 2))
                if is_hl and sub.l > 0:
                    ml_s = f"+{ml}" if ml > 0 else str(ml)
                    c.create_text(x + box_w / 2, y + box_h + 8, text=ml_s, fill=SUBTLE, font=self.font_micro)
                x += box_w + 3
            c.create_text(x + 4, y + box_h / 2, text=f"{count}/{sub.capacity}",
                          fill=SUBTLE, font=self.font_micro, anchor="w")
            y += box_h + (14 if is_hl and sub.l > 0 else 6)
        c.configure(height=max(y + 8, 80))


def main() -> None:
    if len(sys.argv) > 1 and sys.argv[1] in ("-h", "--help"):
        print("Usage: python3 aufbau.py [element]")
        print("  No arguments: launches the interactive GUI.")
        print("  With element (symbol/name/Z): prints configuration and exits.")
        return

    if len(sys.argv) > 1:
        q = " ".join(sys.argv[1:]).strip().lower()
        z = None
        if q.isdigit() and 1 <= int(q) <= MAX_Z:
            z = int(q)
        elif q in ELEMENT_BY_SYMBOL:
            z = ELEMENT_BY_SYMBOL[q].z
        elif q in ELEMENT_BY_NAME:
            z = ELEMENT_BY_NAME[q].z
        else:
            for el in ELEMENTS:
                if el.name.lower().startswith(q) or el.symbol.lower().startswith(q):
                    z = el.z
                    break
        if z is None:
            print(f"Element not found: {sys.argv[1]}", file=sys.stderr)
            sys.exit(1)
        el = get_element(z)
        occ = occupancy_for(z, "observed")
        print(f"{el.symbol} ({el.name}, Z={el.z})")
        print(f"Configuration : {format_config(occ)}")
        print(f"Condensed     : {format_condensed(occ, z)}")
        print(f"Unpaired e\u207b   : {unpaired_count(occ)}")
        if is_exception(z):
            print(f"Exception     : {exception_reason(z)}")
            for lb, p, o in config_diff(z):
                print(f"  {lb}: predicted {p} \u2192 observed {o}")
        return

    if not _HAS_TK:
        print("tkinter is required for the GUI.", file=sys.stderr)
        print("On Debian/Ubuntu: sudo apt install python3-tk", file=sys.stderr)
        print("Or use CLI mode:  python3 aufbau.py Fe", file=sys.stderr)
        sys.exit(1)

    app = AufbauApp()
    app._set_speed(280, "Med")
    app.mainloop()


if __name__ == "__main__":
    main()
