/* Aufbau Explorer — Web Edition
 * DOM / Pyodide integration layer. Loads app.py (pure-Python physics
 * engine) into a Pyodide (CPython-on-WebAssembly) runtime and drives
 * all rendering from the JSON view-models it returns. No server code.
 */

const state = {
  z: 26,          // current element (defaults to Iron)
  mode: "observed",
  placed: 0,
  total: 0,
  view: "atom",
  playing: false,
  speedMs: 280,
  timer: null,
  elements: [],   // static periodic-table metadata from app.py
};

let pyodide = null;

async function boot() {
  pyodide = await loadPyodide();
  const src = await (await fetch("app.py")).text();
  pyodide.FS.writeFile("app.py", src);
  await pyodide.runPythonAsync(`
import app
`);
  state.elements = JSON.parse(pyodide.runPython("app.elements_json()"));

  document.getElementById("loading").hidden = true;
  document.getElementById("app").hidden = false;

  buildPeriodicTable();
  wireControls();
  selectElement(state.z);
}

// ─── Python bridge helpers ──────────────────────────────────────────────

function getState() {
  const json = pyodide.runPython(
    `app.state_json(${state.z}, ${JSON.stringify(state.mode)}, ${state.placed})`
  );
  return JSON.parse(json);
}

function searchQuery(q) {
  const json = pyodide.runPython(`app.search_json(${JSON.stringify(q)})`);
  return JSON.parse(json).z;
}

// ─── State transitions ──────────────────────────────────────────────────

function selectElement(z) {
  stopPlaying();
  state.z = Math.max(1, Math.min(118, z));
  state.placed = 0;
  render();
}

function setPlaced(n) {
  const model = getState();
  state.placed = Math.max(0, Math.min(model.total, n));
  render();
}

function stepForward() {
  const model = getState();
  if (state.placed >= model.total) { stopPlaying(); return; }
  state.placed += 1;
  render();
}

function stepBack() {
  stopPlaying();
  state.placed = Math.max(0, state.placed - 1);
  render();
}

function reset() {
  stopPlaying();
  state.placed = 0;
  render();
}

function fillAll() {
  stopPlaying();
  const model = getState();
  state.placed = model.total;
  render();
}

function togglePlay() {
  if (state.playing) { stopPlaying(); return; }
  const model = getState();
  if (state.placed >= model.total) state.placed = 0;
  state.playing = true;
  document.getElementById("playBtn").textContent = "⏸ Pause";
  state.timer = setInterval(() => {
    const m = getState();
    if (state.placed >= m.total) { stopPlaying(); return; }
    state.placed += 1;
    render();
  }, state.speedMs);
}

function stopPlaying() {
  state.playing = false;
  document.getElementById("playBtn").textContent = "▶ Play";
  if (state.timer) { clearInterval(state.timer); state.timer = null; }
}

function setMode(mode) {
  state.mode = mode;
  document.querySelectorAll("#modeObserved, #modeAufbau").forEach((b) =>
    b.classList.toggle("active", b.dataset.mode === mode)
  );
  render();
}

function setView(view) {
  state.view = view;
  document.querySelectorAll(".view-btn").forEach((b) =>
    b.classList.toggle("active", b.dataset.view === view)
  );
  document.querySelectorAll(".view-panel").forEach((p) =>
    p.classList.toggle("active", p.id === `view-${view}`)
  );
  render();
}

// ─── Rendering ───────────────────────────────────────────────────────────

function render() {
  const model = getState();
  state.total = model.total;
  renderInfo(model);
  document.getElementById("slider").max = model.total;
  document.getElementById("slider").value = model.placed;
  document.getElementById("sliderLabel").textContent = `${model.placed} / ${model.total} e⁻`;

  if (state.view === "atom") drawAtom(model);
  if (state.view === "fill") renderFillOrder(model);
  if (state.view === "orbitals") renderOrbitalBoxes(model);
  if (state.view === "table") highlightPeriodicTable(model);
}

function renderInfo(model) {
  const el = model.element;
  document.getElementById("infoSymbol").textContent = el.symbol;
  document.getElementById("infoName").textContent = el.name;
  document.getElementById("infoZ").textContent = `Z = ${el.z}`;
  document.getElementById("infoCategory").textContent = el.category;
  document.getElementById("infoConfig").textContent = model.config;
  document.getElementById("infoCondensed").textContent = model.condensed;
  document.getElementById("infoUnpaired").textContent = `${model.unpaired} unpaired e⁻`;
  document.getElementById("infoDescription").textContent = model.description;

  const badge = document.getElementById("infoException");
  badge.hidden = !model.is_exception;

  const diffEl = document.getElementById("infoDiff");
  if (model.is_exception && model.placed === model.total && model.config_diff.length) {
    const parts = model.config_diff.map(
      (d) => `${d.label}: predicted ${d.predicted} → observed ${d.observed}`
    );
    diffEl.textContent = `${model.exception_reason} (${parts.join(", ")})`;
    diffEl.hidden = false;
  } else {
    diffEl.hidden = true;
  }
}

function drawAtom(model) {
  const canvas = document.getElementById("atomCanvas");
  const ctx = canvas.getContext("2d");
  const w = canvas.width, h = canvas.height;
  ctx.clearRect(0, 0, w, h);
  const cx = w / 2, cy = h / 2;

  ctx.fillStyle = "#181b22";
  ctx.beginPath();
  ctx.arc(cx, cy, 18, 0, Math.PI * 2);
  ctx.fill();
  ctx.fillStyle = "#e8e6e1";
  ctx.font = "bold 13px sans-serif";
  ctx.textAlign = "center";
  ctx.textBaseline = "middle";
  ctx.fillText(model.element.symbol, cx, cy);

  const shells = model.shells;
  const maxShell = shells.reduce((last, n, i) => (n > 0 ? i : last), 0);
  const maxRadius = Math.min(w, h) / 2 - 20;
  const step = maxRadius / Math.max(1, maxShell + 1);

  let lastPoint = null;
  for (let i = 0; i <= maxShell; i++) {
    const n = shells[i];
    if (n <= 0) continue;
    const r = step * (i + 1);
    ctx.strokeStyle = "#2a2d36";
    ctx.beginPath();
    ctx.arc(cx, cy, r, 0, Math.PI * 2);
    ctx.stroke();
    for (let k = 0; k < n; k++) {
      const angle = (2 * Math.PI * k) / n - Math.PI / 2;
      const x = cx + r * Math.cos(angle);
      const y = cy + r * Math.sin(angle);
      const isLast = i === maxShell && k === n - 1 && model.placed > 0;
      ctx.fillStyle = isLast ? "#c4a574" : "#7eb8da";
      ctx.beginPath();
      ctx.arc(x, y, isLast ? 6 : 4.5, 0, Math.PI * 2);
      ctx.fill();
      if (isLast) lastPoint = [x, y];
    }
  }
  if (lastPoint) {
    ctx.strokeStyle = "#c4a574";
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    ctx.arc(lastPoint[0], lastPoint[1], 10, 0, Math.PI * 2);
    ctx.stroke();
  }
}

function renderFillOrder(model) {
  const container = document.getElementById("fillOrderList");
  container.innerHTML = "";
  for (const sub of model.fill_order) {
    const row = document.createElement("div");
    row.className = "fill-row";
    const pct = (sub.count / sub.capacity) * 100;
    row.innerHTML = `
      <span class="fill-label">${sub.label}</span>
      <span class="fill-bar-track"><span class="fill-bar-fill" style="width:${pct}%"></span></span>
      <span class="fill-count">${sub.count} / ${sub.capacity}</span>
    `;
    container.appendChild(row);
  }
}

function renderOrbitalBoxes(model) {
  const container = document.getElementById("orbitalBoxes");
  container.innerHTML = "";
  for (const sub of model.orbital_boxes) {
    const row = document.createElement("div");
    row.className = "orbital-row";
    const label = document.createElement("span");
    label.className = "fill-label";
    label.textContent = sub.label;
    row.appendChild(label);
    for (const orb of sub.orbitals) {
      const box = document.createElement("div");
      box.className = "orbital-box" + (orb.up || orb.down ? " active" : "");
      let arrows = "";
      if (orb.up) arrows += "<span>↑</span>";
      if (orb.down) arrows += "<span>↓</span>";
      box.innerHTML = arrows;
      box.title = `mℓ = ${orb.ml}`;
      row.appendChild(box);
    }
    container.appendChild(row);
  }
}

function buildPeriodicTable() {
  const container = document.getElementById("periodicTable");
  container.innerHTML = "";
  // Rows 0-6: periods 1-7. Row 7: blank spacer. Rows 8-9: lanthanides/actinides.
  const F_OFFSET = 8;
  const grid = [];
  for (let r = 0; r < 10; r++) grid.push(new Array(18).fill(null));

  for (const el of state.elements) {
    if (el.block === "f") {
      grid[F_OFFSET + el.row][el.col] = el;
    } else {
      grid[el.row][el.col] = el;
    }
  }

  for (let r = 0; r < grid.length; r++) {
    for (let c = 0; c < 18; c++) {
      const el = grid[r][c];
      const cell = document.createElement("div");
      if (!el) {
        cell.className = "pt-cell pt-blank";
      } else {
        cell.className = "pt-cell" + (el.exception ? " exception" : "");
        cell.dataset.z = el.z;
        cell.innerHTML = `<span class="pt-z">${el.z}</span><strong>${el.symbol}</strong>`;
        cell.title = `${el.name} (Z=${el.z})`;
        cell.addEventListener("click", () => selectElement(el.z));
      }
      container.appendChild(cell);
    }
  }
}

function highlightPeriodicTable(model) {
  document.querySelectorAll(".pt-cell").forEach((cell) => {
    cell.classList.toggle("selected", Number(cell.dataset.z) === model.element.z);
  });
}

// ─── Wiring ──────────────────────────────────────────────────────────────

function wireControls() {
  document.getElementById("searchBtn").addEventListener("click", runSearch);
  document.getElementById("search").addEventListener("keydown", (e) => {
    if (e.key === "Enter") runSearch();
  });
  document.getElementById("prevBtn").addEventListener("click", () => selectElement(state.z - 1));
  document.getElementById("nextBtn").addEventListener("click", () => selectElement(state.z + 1));

  document.getElementById("resetBtn").addEventListener("click", reset);
  document.getElementById("stepBackBtn").addEventListener("click", stepBack);
  document.getElementById("stepFwdBtn").addEventListener("click", stepForward);
  document.getElementById("fillAllBtn").addEventListener("click", fillAll);
  document.getElementById("playBtn").addEventListener("click", togglePlay);
  document.getElementById("slider").addEventListener("input", (e) => {
    stopPlaying();
    setPlaced(Number(e.target.value));
  });

  document.getElementById("modeObserved").addEventListener("click", () => setMode("observed"));
  document.getElementById("modeAufbau").addEventListener("click", () => setMode("aufbau"));

  document.querySelectorAll(".speed-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".speed-btn").forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
      state.speedMs = Number(btn.dataset.ms);
      if (state.playing) { stopPlaying(); togglePlay(); }
    });
  });

  document.querySelectorAll(".view-btn").forEach((btn) => {
    btn.addEventListener("click", () => setView(btn.dataset.view));
  });

  document.addEventListener("keydown", (e) => {
    if (document.activeElement && document.activeElement.id === "search") return;
    switch (e.key) {
      case " ": e.preventDefault(); togglePlay(); break;
      case "ArrowRight": selectElement(state.z + 1); break;
      case "ArrowLeft": selectElement(state.z - 1); break;
      case ".": stepForward(); break;
      case ",": stepBack(); break;
      case "r": case "R": reset(); break;
    }
  });
}

function runSearch() {
  const q = document.getElementById("search").value;
  const z = searchQuery(q);
  if (z !== null) {
    selectElement(z);
    document.getElementById("search").value = "";
  } else {
    document.getElementById("infoDescription").textContent = `Element not found: "${q}"`;
  }
}

boot();
