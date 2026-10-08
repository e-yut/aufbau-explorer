"""
Aufbau Explorer — Web Edition (Physics Engine)
===============================================
Pure-Python electron configuration engine, extracted from the desktop
``aufbau-explorer_v1.1.py`` application so it can run with **no GUI
toolkit dependency**. This module is loaded into the browser by
Pyodide (CPython compiled to WebAssembly) and driven entirely from
``index.html`` / ``static/script.js`` — there is no server-side code at
all, so the whole app can be hosted as static files on GitHub Pages.

Implements:
  * Madelung (n+l) Aufbau filling order
  * Hund's rule / Pauli exclusion placement order
  * Ground-state spectroscopic exceptions (Cr, Cu, Nb, Mo, Pd, Ag, Pt,
    Au, lanthanide/actinide anomalies, etc.)

Every browser-facing function returns a JSON **string** (not a Python
object) so that JavaScript can simply ``JSON.parse()`` the result
without needing ``pyodide.ffi`` conversions.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Tuple

# ═══════════════════════════════════════════════════════════════════════════
# Element data (Z = 1 … 118)
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
84|Po|Polonium|6|16|metalloid|[209]
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
    _z, _symbol, _name, _period, _group, _category, _mass = _line.split("|")
    _el = ElementInfo(int(_z), _symbol, _name, int(_period), int(_group), _category, _mass)
    ELEMENTS.append(_el)
    ELEMENT_BY_Z[_el.z] = _el
    ELEMENT_BY_SYMBOL[_el.symbol.lower()] = _el
    ELEMENT_BY_NAME[_el.name.lower()] = _el

MAX_Z = 118


def get_element(z: int) -> ElementInfo:
    return ELEMENT_BY_Z.get(z, ELEMENTS[0])


def table_cell(el: ElementInfo) -> Tuple[str, int, int]:
    """Return (block, row, col) grid position for the periodic table UI."""
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


def visible_subshells(occ: Dict[str, int], z: int) -> List[Subshell]:
    predicted = aufbau_occupancy(z)
    last = 0
    for i, sub in enumerate(SUBSHELLS):
        if occ.get(sub.label, 0) > 0 or predicted.get(sub.label, 0) > 0:
            last = i
    last = min(len(SUBSHELLS) - 1, last + 1)
    return SUBSHELLS[: last + 1]


def describe_placement(p: Optional[Placement], z: int) -> str:
    if p is None:
        return "An empty atom. Press Play to watch electrons occupy orbitals in energy order."
    ell = L_NAME[p.l]
    ml = f"+{p.ml}" if p.ml > 0 else str(p.ml)
    ms = "+\u00bd" if p.ms == 1 else "\u2212\u00bd"
    qn = f"n={p.n}, \u2113={p.l} ({ell}), m\u2113={ml}, ms={ms}"
    if p.rule == "exception":
        return f"Exception: electron occupies {p.subshell} ({qn}). {exception_reason(z) or ''}"
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


def match_query(q: str) -> Optional[int]:
    """Resolve a free-text search box query to an atomic number."""
    s = (q or "").strip().lower()
    if not s:
        return None
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


# ═══════════════════════════════════════════════════════════════════════════
# Browser-facing API (JSON in / JSON out — called from static/script.js)
# ═══════════════════════════════════════════════════════════════════════════


def elements_json() -> str:
    """Static table of all 118 elements, for building the periodic table UI once."""
    out = []
    for el in ELEMENTS:
        block, row, col = table_cell(el)
        out.append({
            "z": el.z, "symbol": el.symbol, "name": el.name, "period": el.period,
            "group": el.group, "category": el.category, "mass": el.mass,
            "block": block, "row": row, "col": col,
            "exception": is_exception(el.z),
        })
    return json.dumps(out)


def search_json(query: str) -> str:
    """Resolve a search string to an atomic number (or null)."""
    return json.dumps({"z": match_query(query)})


def state_json(z: int, mode: str, placed: int) -> str:
    """
    Full view-model for one UI refresh: element info, partial electron
    configuration (``placed`` electrons out of ``z``), the formatted
    strings, the per-orbital spin-box layout, and a plain-English
    description of the most recently placed electron.
    """
    z = max(1, min(MAX_Z, int(z)))
    mode = mode if mode in ("observed", "aufbau") else "observed"

    full_placements = fill_sequence(z, mode)
    total = len(full_placements)
    placed = max(0, min(total, int(placed)))
    active = full_placements[:placed]

    occ = occupancy_from_placements(active)
    full_occ = occupancy_for(z, mode)
    el = get_element(z)
    last = active[-1] if active else None

    subshells = visible_subshells(full_occ, z)
    orbital_boxes = []
    for sub in subshells:
        orbs = 2 * sub.l + 1
        states = [{"ml": -sub.l + i, "up": False, "down": False} for i in range(orbs)]
        orbital_boxes.append({
            "label": sub.label, "n": sub.n, "l": sub.l, "capacity": sub.capacity,
            "orbitals": states,
        })
    box_by_label = {b["label"]: b for b in orbital_boxes}
    for p in active:
        box = box_by_label.get(p.subshell)
        if box is None:
            continue
        idx = p.ml + p.l
        if p.ms == 1:
            box["orbitals"][idx]["up"] = True
        else:
            box["orbitals"][idx]["down"] = True

    fill_order = []
    for sub in subshells:
        fill_order.append({
            "label": sub.label, "capacity": sub.capacity,
            "count": occ.get(sub.label, 0),
            "is_full_target": full_occ.get(sub.label, 0) == sub.capacity,
        })

    diff = config_diff(z)

    payload = {
        "element": {
            "z": el.z, "symbol": el.symbol, "name": el.name,
            "category": el.category, "period": el.period, "group": el.group,
        },
        "mode": mode,
        "placed": placed,
        "total": total,
        "config": format_config(occ),
        "condensed": format_condensed(occ, z) if placed else "\u2014",
        "unpaired": unpaired_count(occ),
        "shells": shell_occupancy(occ),
        "orbital_boxes": orbital_boxes,
        "fill_order": fill_order,
        "last_placement": (
            {"subshell": last.subshell, "n": last.n, "l": last.l,
             "ml": last.ml, "ms": last.ms, "rule": last.rule}
            if last else None
        ),
        "description": describe_placement(last, z),
        "is_exception": is_exception(z),
        "exception_reason": exception_reason(z),
        "config_diff": [{"label": lb, "predicted": p, "observed": o} for lb, p, o in diff],
    }
    return json.dumps(payload)


def cli_summary_json(query: str) -> str:
    """Text-analyzer-style one-shot summary, equivalent to the desktop CLI mode."""
    z = match_query(query)
    if z is None:
        return json.dumps({"error": f"Element not found: {query!r}"})
    el = get_element(z)
    occ = occupancy_for(z, "observed")
    out = {
        "symbol": el.symbol, "name": el.name, "z": el.z,
        "configuration": format_config(occ),
        "condensed": format_condensed(occ, z),
        "unpaired": unpaired_count(occ),
        "is_exception": is_exception(z),
        "exception_reason": exception_reason(z),
    }
    return json.dumps(out)
