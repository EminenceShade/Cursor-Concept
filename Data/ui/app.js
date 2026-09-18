// Cursor Concept - UI Application Logic

const PRESETS = [
  { name: "Moga Purple", mode: "solid", a: "#a6a3ff", b: "#00f0ff", angle: 45, outline: "#ffffff", base: "dark" },
  { name: "Cyber Neon", mode: "gradient", a: "#00f0ff", b: "#d946ef", angle: 45, outline: "#ffffff", base: "dark" },
  { name: "Sunset Vapor", mode: "gradient", a: "#ff007f", b: "#7928ca", angle: 45, outline: "#ffffff", base: "dark" },
  { name: "Emerald Aurora", mode: "gradient", a: "#10b981", b: "#06b6d4", angle: 90, outline: "#ffffff", base: "dark" },
  { name: "Toxic Wave", mode: "gradient", a: "#00ff66", b: "#0099ff", angle: 0, outline: "#000000", base: "dark" },
  { name: "RGB Wave", mode: "rgb", a: "#ec4899", b: "#8b5cf6", angle: 45, outline: "#ffffff", base: "dark" },
  { name: "Solar Gold", mode: "gradient", a: "#f59e0b", b: "#eab308", angle: 45, outline: "#ffffff", base: "dark" },
  { name: "Obsidian", mode: "solid", a: "#27272a", b: "#09090b", angle: 45, outline: "#ffffff", base: "dark" },
  { name: "Pure Light", mode: "solid", a: "#ffffff", b: "#e2e8f0", angle: 45, outline: "#000000", base: "white" }
];

const state = {
  schemeName: "Cursor Concept",
  mode: "solid",
  colorA: "#a6a3ff",
  colorB: "#00f0ff",
  angle: 45,
  rgbSpeed: 2,
  rgbDirection: "clockwise",
  outlineColor: "#ffffff",
  baseType: "dark",
  activeCategory: "all",
  searchQuery: "",
  cursors: [],
  debounceTimer: null
};

// DOM Elements
const schemeNameInput = document.getElementById("schemeNameInput");
const presetsGrid = document.getElementById("presetsGrid");
const modeButtons = document.querySelectorAll("#modeSelector .seg-btn");

// Swatch Trigger Buttons
const rowColorA = document.getElementById("rowColorA");
const labelColorA = document.getElementById("labelColorA");
const btnOpenPickerA = document.getElementById("btnOpenPickerA");
const swatchBubbleA = document.getElementById("swatchBubbleA");
const swatchHexA = document.getElementById("swatchHexA");

const rowColorB = document.getElementById("rowColorB");
const btnOpenPickerB = document.getElementById("btnOpenPickerB");
const swatchBubbleB = document.getElementById("swatchBubbleB");
const swatchHexB = document.getElementById("swatchHexB");

const gradientAngleGroup = document.getElementById("gradientAngleGroup");
const angleSlider = document.getElementById("angleSlider");
const angleDisplay = document.getElementById("angleDisplay");
const gradientPreviewStrip = document.getElementById("gradientPreviewStrip");

// Evofox RGB Dynamics Elements
const rgbDynamicsPanel = document.getElementById("rgbDynamicsPanel");
const rgbSpeedSlider = document.getElementById("rgbSpeedSlider");
const rgbSpeedBadge = document.getElementById("rgbSpeedBadge");
const rgbDirectionSelector = document.getElementById("rgbDirectionSelector");

// Floating Color Popover Elements
const colorPickerBackdrop = document.getElementById("colorPickerBackdrop");
const colorPickerCard = document.getElementById("colorPickerCard");
const popoverTitle = document.getElementById("popoverTitle");
const popoverCloseBtn = document.getElementById("popoverCloseBtn");
const popoverDoneBtn = document.getElementById("popoverDoneBtn");
const popoverSvCanvas = document.getElementById("popoverSvCanvas");
const popoverPuck = document.getElementById("popoverPuck");
const popoverHueSlider = document.getElementById("popoverHueSlider");
const popoverSwatches = document.getElementById("popoverSwatches");
const popoverHexInput = document.getElementById("popoverHexInput");
const popoverEyedropperBtn = document.getElementById("popoverEyedropperBtn");

// App Theme DOM Elements
const appThemeSwitcher = document.getElementById("appThemeSwitcher");
const themeToggleBtns = document.querySelectorAll(".theme-toggle-btn");

const outlineOptions = document.querySelectorAll(".outline-opt");
const customOutlineRow = document.getElementById("customOutlineRow");
const pickerOutline = document.getElementById("pickerOutline");
const hexInputOutline = document.getElementById("hexInputOutline");
const customOutlineSwatch = document.getElementById("customOutlineSwatch");
const baseTypeSelect = document.getElementById("baseTypeSelect");

const sandboxPad = document.getElementById("sandboxPad");
const testTargets = document.querySelectorAll(".test-target");
const activeCursorSimName = document.getElementById("activeCursorSimName");

const cursorCardsGrid = document.getElementById("cursorCardsGrid");
const filterChips = document.querySelectorAll(".filter-chip");
const shelfCount = document.getElementById("shelfCount");

const btnApply = document.getElementById("btnApply");
const btnRevert = document.getElementById("btnRevert");
const btnExport = document.getElementById("btnExport");

const toastPill = document.getElementById("toastPill");
const toastMsg = document.getElementById("toastMsg");
const toastIcon = document.getElementById("toastIcon");

function showToast(message, isError = false, duration = 3500) {
  toastMsg.textContent = message;
  toastIcon.textContent = isError ? "✕" : "✓";
  toastPill.classList.toggle("error", isError);
  toastPill.classList.add("show");
  setTimeout(() => {
    toastPill.classList.remove("show");
  }, duration);
}

// ----------------------------------------------------
// App Theming (System Default / Dark / Light)
// ----------------------------------------------------
let currentAppTheme = localStorage.getItem("cursor_concept_app_theme") || "system";
let systemThemeMql = window.matchMedia("(prefers-color-scheme: dark)");

function applyAppTheme(theme) {
  currentAppTheme = theme;
  localStorage.setItem("cursor_concept_app_theme", theme);
  
  themeToggleBtns.forEach(btn => {
    btn.classList.toggle("active", btn.dataset.theme === theme);
  });
  
  if (theme === "system") {
    const isDark = systemThemeMql.matches;
    document.documentElement.setAttribute("data-app-theme", isDark ? "dark" : "light");
  } else {
    document.documentElement.setAttribute("data-app-theme", theme);
  }
}

function initAppTheming() {
  themeToggleBtns.forEach(btn => {
    btn.addEventListener("click", () => {
      applyAppTheme(btn.dataset.theme);
    });
  });
  
  systemThemeMql.addEventListener("change", (e) => {
    if (currentAppTheme === "system") {
      document.documentElement.setAttribute("data-app-theme", e.matches ? "dark" : "light");
    }
  });
  
  applyAppTheme(currentAppTheme);
}

// ----------------------------------------------------
// Color Math
// ----------------------------------------------------
function hsvToRgb(h, s, v) {
  const c = v * s;
  const x = c * (1 - Math.abs(((h / 60) % 2) - 1));
  const m = v - c;
  let r = 0, g = 0, b = 0;
  if (0 <= h && h < 60) { r = c; g = x; b = 0; }
  else if (60 <= h && h < 120) { r = x; g = c; b = 0; }
  else if (120 <= h && h < 180) { r = 0; g = c; b = x; }
  else if (180 <= h && h < 240) { r = 0; g = x; b = c; }
  else if (240 <= h && h < 300) { r = x; g = 0; b = c; }
  else { r = c; g = 0; b = x; }
  return [
    Math.round((r + m) * 255),
    Math.round((g + m) * 255),
    Math.round((b + m) * 255)
  ];
}

function rgbToHsv(r, g, b) {
  r /= 255; g /= 255; b /= 255;
  const max = Math.max(r, g, b), min = Math.min(r, g, b);
  const d = max - min;
  let h = 0;
  const s = max === 0 ? 0 : d / max;
  const v = max;
  if (max !== min) {
    switch (max) {
      case r: h = (g - b) / d + (g < b ? 6 : 0); break;
      case g: h = (b - r) / d + 2; break;
      case b: h = (r - g) / d + 4; break;
    }
    h *= 60;
  }
  return [h, s, v];
}

function rgbToHex(r, g, b) {
  return "#" + [r, g, b].map(x => x.toString(16).padStart(2, "0")).join("");
}

function hexToRgb(hex) {
  hex = hex.replace("#", "");
  if (hex.length === 3) hex = hex.split("").map(c => c + c).join("");
  const num = parseInt(hex, 16);
  return [(num >> 16) & 255, (num >> 8) & 255, num & 255];
}

// ----------------------------------------------------
// Floating Popover Color Picker
// ----------------------------------------------------
let activeColorTarget = "colorA"; // 'colorA' or 'colorB'
let popoverH = 240, popoverS = 0.36, popoverV = 1.0;
let isDraggingSv = false;

const QUICK_SWATCHES = [
  "#A6A3FF", "#00F0FF", "#EC4899", "#10B981", 
  "#F59E0B", "#3B82F6", "#EF4444", "#FFFFFF", "#18181B", "#8B5CF6"
];

function drawSvCanvas() {
  if (!popoverSvCanvas) return;
  const ctx = popoverSvCanvas.getContext("2d");
  const w = popoverSvCanvas.width;
  const h = popoverSvCanvas.height;

  // Base hue
  ctx.fillStyle = `hsl(${popoverH}, 100%, 50%)`;
  ctx.fillRect(0, 0, w, h);

  // Horizontal white gradient
  const gradWhite = ctx.createLinearGradient(0, 0, w, 0);
  gradWhite.addColorStop(0, "rgba(255, 255, 255, 1)");
  gradWhite.addColorStop(1, "rgba(255, 255, 255, 0)");
  ctx.fillStyle = gradWhite;
  ctx.fillRect(0, 0, w, h);

  // Vertical black gradient
  const gradBlack = ctx.createLinearGradient(0, 0, 0, h);
  gradBlack.addColorStop(0, "rgba(0, 0, 0, 0)");
  gradBlack.addColorStop(1, "rgba(0, 0, 0, 1)");
  ctx.fillStyle = gradBlack;
  ctx.fillRect(0, 0, w, h);
}

function updatePuckPosition() {
  if (!popoverPuck || !popoverSvCanvas) return;
  const w = popoverSvCanvas.width;
  const h = popoverSvCanvas.height;
  const px = popoverS * w;
  const py = (1 - popoverV) * h;
  popoverPuck.style.left = `${px}px`;
  popoverPuck.style.top = `${py}px`;
  
  const [r, g, b] = hsvToRgb(popoverH, popoverS, popoverV);
  popoverPuck.style.background = rgbToHex(r, g, b);
}

function updateColorFromPopover() {
  const [r, g, b] = hsvToRgb(popoverH, popoverS, popoverV);
  const hex = rgbToHex(r, g, b);
  state[activeColorTarget] = hex;
  
  if (popoverHexInput) {
    popoverHexInput.value = hex.replace("#", "").toUpperCase();
  }
  
  syncUIFromState();
  schedulePreviewRefresh();
}

function openColorPicker(target, title) {
  activeColorTarget = target;
  popoverTitle.textContent = title;
  
  const currentHex = state[target] || "#a6a3ff";
  const [r, g, b] = hexToRgb(currentHex);
  const [h, s, v] = rgbToHsv(r, g, b);
  popoverH = h;
  popoverS = s;
  popoverV = v;
  
  if (popoverHueSlider) popoverHueSlider.value = Math.round(h);
  if (popoverHexInput) popoverHexInput.value = currentHex.replace("#", "").toUpperCase();
  
  drawSvCanvas();
  updatePuckPosition();
  colorPickerBackdrop.classList.remove("hidden");
}

function closeColorPicker() {
  colorPickerBackdrop.classList.add("hidden");
}

function initColorPickerPopover() {
  if (!popoverSvCanvas) return;
  
  // Quick Swatches
  popoverSwatches.innerHTML = "";
  QUICK_SWATCHES.forEach(hex => {
    const dot = document.createElement("div");
    dot.className = "popover-swatch-dot";
    dot.style.background = hex;
    dot.title = hex;
    dot.addEventListener("click", () => {
      const [r, g, b] = hexToRgb(hex);
      const [h, s, v] = rgbToHsv(r, g, b);
      popoverH = h;
      popoverS = s;
      popoverV = v;
      if (popoverHueSlider) popoverHueSlider.value = Math.round(h);
      drawSvCanvas();
      updatePuckPosition();
      updateColorFromPopover();
    });
    popoverSwatches.appendChild(dot);
  });

  // SV Canvas interaction
  function handleSvPick(e) {
    const rect = popoverSvCanvas.getBoundingClientRect();
    const x = Math.max(0, Math.min(rect.width, e.clientX - rect.left));
    const y = Math.max(0, Math.min(rect.height, e.clientY - rect.top));
    popoverS = x / rect.width;
    popoverV = 1 - (y / rect.height);
    updatePuckPosition();
    updateColorFromPopover();
  }

  popoverSvCanvas.addEventListener("mousedown", (e) => {
    isDraggingSv = true;
    handleSvPick(e);
  });

  window.addEventListener("mousemove", (e) => {
    if (isDraggingSv) {
      handleSvPick(e);
    }
  });

  window.addEventListener("mouseup", () => {
    isDraggingSv = false;
  });

  // Hue Slider
  if (popoverHueSlider) {
    popoverHueSlider.addEventListener("input", (e) => {
      popoverH = parseFloat(e.target.value);
      drawSvCanvas();
      updatePuckPosition();
      updateColorFromPopover();
    });
  }

  // Hex Input
  if (popoverHexInput) {
    popoverHexInput.addEventListener("input", (e) => {
      let val = e.target.value.trim().replace("#", "");
      if (val.length === 6 && /^[0-9A-Fa-f]{6}$/.test(val)) {
        const hex = "#" + val;
        const [r, g, b] = hexToRgb(hex);
        const [h, s, v] = rgbToHsv(r, g, b);
        popoverH = h;
        popoverS = s;
        popoverV = v;
        if (popoverHueSlider) popoverHueSlider.value = Math.round(h);
        drawSvCanvas();
        updatePuckPosition();
        updateColorFromPopover();
      }
    });
  }

  // Eyedropper in popover
  if (popoverEyedropperBtn) {
    popoverEyedropperBtn.addEventListener("click", async () => {
      if (window.EyeDropper) {
        try {
          const eye = new window.EyeDropper();
          const res = await eye.open();
          const hex = res.sRGBHex;
          const [r, g, b] = hexToRgb(hex);
          const [h, s, v] = rgbToHsv(r, g, b);
          popoverH = h;
          popoverS = s;
          popoverV = v;
          if (popoverHueSlider) popoverHueSlider.value = Math.round(h);
          drawSvCanvas();
          updatePuckPosition();
          updateColorFromPopover();
        } catch (err) {}
      }
    });
  }

  // Close & Done buttons
  if (popoverCloseBtn) popoverCloseBtn.addEventListener("click", closeColorPicker);
  if (popoverDoneBtn) popoverDoneBtn.addEventListener("click", closeColorPicker);

  // Click outside dismiss
  colorPickerBackdrop.addEventListener("click", (e) => {
    if (e.target === colorPickerBackdrop) {
      closeColorPicker();
    }
  });

  // Swatch Trigger Buttons
  btnOpenPickerA.addEventListener("click", () => {
    const title = state.mode === "solid" ? "Fill Color" : "Primary Gradient Stop";
    openColorPicker("colorA", title);
  });

  btnOpenPickerB.addEventListener("click", () => {
    openColorPicker("colorB", "Secondary Gradient Stop");
  });
}

function initPresets() {
  presetsGrid.innerHTML = "";
  PRESETS.forEach((preset, idx) => {
    const chip = document.createElement("div");
    chip.className = `preset-chip ${idx === 0 ? "active" : ""}`;
    
    let bgStyle;
    if (preset.mode === "solid") {
      bgStyle = preset.a;
    } else if (preset.mode === "gradient") {
      bgStyle = `linear-gradient(${preset.angle}deg, ${preset.a}, ${preset.b})`;
    } else {
      bgStyle = `conic-gradient(red, yellow, lime, aqua, blue, magenta, red)`;
    }
    
    chip.innerHTML = `
      <div class="preset-thumb" style="background: ${bgStyle};"></div>
      <span class="preset-name">${preset.name}</span>
    `;
    
    chip.addEventListener("click", () => {
      document.querySelectorAll(".preset-chip").forEach(c => c.classList.remove("active"));
      chip.classList.add("active");
      applyPreset(preset);
    });
    
    presetsGrid.appendChild(chip);
  });
}

function applyPreset(preset) {
  state.mode = preset.mode;
  state.colorA = preset.a;
  state.colorB = preset.b;
  state.angle = preset.angle;
  state.outlineColor = preset.outline;
  state.baseType = preset.base;
  state.schemeName = `Cursor Concept: ${preset.name}`;
  if (schemeNameInput) schemeNameInput.value = state.schemeName;
  
  syncUIFromState();
  schedulePreviewRefresh();
}

function syncUIFromState() {
  // Mode tabs
  modeButtons.forEach(btn => {
    btn.classList.toggle("active", btn.dataset.mode === state.mode);
  });
  
  // Visibility based on mode
  if (state.mode === "solid") {
    rowColorA.style.display = "flex";
    labelColorA.textContent = "Fill Color";
    rowColorB.style.display = "none";
    gradientAngleGroup.style.display = "none";
    rgbDynamicsPanel.style.display = "none";
  } else if (state.mode === "gradient") {
    rowColorA.style.display = "flex";
    labelColorA.textContent = "Primary Stop";
    rowColorB.style.display = "flex";
    gradientAngleGroup.style.display = "flex";
    rgbDynamicsPanel.style.display = "none";
  } else if (state.mode === "rgb" || state.mode === "chroma") {
    rowColorA.style.display = "none";
    rowColorB.style.display = "none";
    gradientAngleGroup.style.display = "none";
    rgbDynamicsPanel.style.display = "flex";
  }
  
  // Update Swatch Triggers
  swatchBubbleA.style.backgroundColor = state.colorA;
  swatchHexA.textContent = state.colorA.toUpperCase();
  swatchBubbleB.style.backgroundColor = state.colorB;
  swatchHexB.textContent = state.colorB.toUpperCase();
  
  angleSlider.value = state.angle;
  angleDisplay.textContent = `${state.angle}°`;
  gradientPreviewStrip.style.background = `linear-gradient(${state.angle}deg, ${state.colorA}, ${state.colorB})`;
  
  // RGB Dynamics
  if (rgbSpeedSlider) rgbSpeedSlider.value = state.rgbSpeed;
  const speedNames = {
    1: "1x Ambient (15 FPS)",
    2: "2x Smooth (30 FPS)",
    3: "3x Fast (45 FPS)",
    4: "4x Blaze (60 FPS)"
  };
  if (rgbSpeedBadge) rgbSpeedBadge.textContent = speedNames[state.rgbSpeed] || "2x Smooth (30 FPS)";

  const speedDurations = { 1: "2.4s", 2: "1.2s", 3: "0.8s", 4: "0.5s" };
  document.documentElement.style.setProperty("--chroma-speed", speedDurations[state.rgbSpeed] || "1.2s");
  document.documentElement.style.setProperty("--chroma-dir", state.rgbDirection === "clockwise" ? "normal" : "reverse");

  if (rgbDirectionSelector) {
    rgbDirectionSelector.querySelectorAll(".seg-btn").forEach(btn => {
      btn.classList.toggle("active", btn.dataset.dir === state.rgbDirection);
    });
  }

  // Outline
  let matchedOutline = false;
  outlineOptions.forEach(opt => {
    const val = opt.dataset.outline;
    if (val.toLowerCase() === state.outlineColor.toLowerCase()) {
      opt.classList.add("active");
      matchedOutline = true;
    } else {
      opt.classList.remove("active");
    }
  });
  
  if (!matchedOutline) {
    document.querySelector('.outline-opt[data-outline="custom"]').classList.add("active");
    customOutlineRow.style.display = "flex";
    pickerOutline.value = state.outlineColor;
    hexInputOutline.value = state.outlineColor;
    customOutlineSwatch.style.background = state.outlineColor;
  } else {
    customOutlineRow.style.display = "none";
  }
  
  baseTypeSelect.value = state.baseType;
}

function getConfig() {
  return {
    scheme_name: (schemeNameInput ? schemeNameInput.value.trim() : "Cursor Concept") || "Cursor Concept",
    mode: state.mode === "rgb" ? "chroma" : state.mode,
    color_a: state.colorA,
    color_b: state.colorB,
    angle: state.angle,
    rgb_speed: state.rgbSpeed,
    rgb_direction: state.rgbDirection,
    outline_color: state.outlineColor,
    base_type: state.baseType
  };
}

function schedulePreviewRefresh() {
  clearTimeout(state.debounceTimer);
  state.debounceTimer = setTimeout(() => {
    fetchPreviews();
  }, 120);
}

async function fetchPreviews() {
  const config = getConfig();
  if (window.pywebview && window.pywebview.api && window.pywebview.api.get_previews) {
    try {
      const data = await window.pywebview.api.get_previews(config);
      state.cursors = data;
      renderCursorCards();
      updateSandboxCursors();
    } catch (e) {
      console.error("Error fetching previews from backend:", e);
    }
  } else {
    // Standalone fallback mockup previews if testing directly in browser
    console.log("Running in standalone preview mode (pywebview not attached yet)");
  }
}

function renderCursorCards() {
  cursorCardsGrid.innerHTML = "";
  const query = (state.searchQuery || "").trim().toLowerCase();
  
  const filtered = state.cursors.filter(c => {
    const matchCat = (state.activeCategory === "all") || (c.category.toLowerCase() === state.activeCategory.toLowerCase());
    if (!matchCat) return false;
    if (!query) return true;
    return (
      c.name.toLowerCase().includes(query) ||
      (c.css_name && c.css_name.toLowerCase().includes(query)) ||
      (c.os_key && c.os_key.toLowerCase().includes(query)) ||
      c.category.toLowerCase().includes(query)
    );
  });
  
  shelfCount.textContent = `${filtered.length} Transformations`;
  
  filtered.forEach(item => {
    const card = document.createElement("div");
    card.className = "cursor-card";
    card.dataset.cursorId = item.id;
    
    card.innerHTML = `
      <div class="card-preview-stage">
        <img src="${item.data_url}" alt="${item.name}" loading="lazy">
      </div>
      <div class="card-details">
        <span class="card-name" title="${item.name}">${item.name}</span>
        <div class="card-meta">
          <span class="card-cat-tag">${item.category}</span>
          <span class="card-hotspot">(${item.hotspot[0]}, ${item.hotspot[1]})</span>
        </div>
      </div>
    `;
    
    card.addEventListener("click", () => {
      document.querySelectorAll(".cursor-card").forEach(c => c.classList.remove("focused"));
      card.classList.add("focused");
      activeCursorSimName.textContent = item.name;
      // Set the sandbox default pointer to this chosen cursor
      const [hx, hy] = item.hotspot;
      sandboxPad.style.cursor = `url('${item.data_url}') ${hx} ${hy}, auto`;
    });
    
    cursorCardsGrid.appendChild(card);
  });
}

function updateSandboxCursors() {
  if (!state.cursors || state.cursors.length === 0) return;
  
  const cursorMap = {};
  state.cursors.forEach(c => { cursorMap[c.id] = c; });
  
  // Set default sandbox canvas cursor to Normal Select
  const normalCur = cursorMap["normal"];
  if (normalCur) {
    const [hx, hy] = normalCur.hotspot;
    sandboxPad.style.cursor = `url('${normalCur.data_url}') ${hx} ${hy}, auto`;
  }
  
  // Update targets
  testTargets.forEach(target => {
    const cid = target.dataset.cursorId;
    const cur = cursorMap[cid];
    if (cur) {
      const [hx, hy] = cur.hotspot;
      target.style.cursor = `url('${cur.data_url}') ${hx} ${hy}, auto`;
      
      const iconEl = target.querySelector(".target-icon");
      if (iconEl && cur.data_url) {
        iconEl.innerHTML = `<img src="${cur.data_url}" alt="${cur.name}" style="width: 24px; height: 24px; image-rendering: pixelated; filter: drop-shadow(0 2px 4px rgba(0,0,0,0.35)); pointer-events: none;">`;
      }
      
      target.onmouseenter = () => {
        activeCursorSimName.textContent = `${cur.name} (${cur.category})`;
      };
      target.onmouseleave = () => {
        const currentActive = document.querySelector(".test-target.active");
        const actCid = currentActive ? currentActive.dataset.cursorId : "normal";
        const actCur = cursorMap[actCid] || normalCur;
        activeCursorSimName.textContent = actCur ? actCur.name : "Normal Select";
      };

      target.onclick = () => {
        testTargets.forEach(t => t.classList.remove("active"));
        target.classList.add("active");
        sandboxPad.style.cursor = `url('${cur.data_url}') ${hx} ${hy}, auto`;
        activeCursorSimName.textContent = `${cur.name} (${cur.category})`;
      };
    }
  });
}

// Event Listeners
function setupEvents() {
  // Mode selection
  modeButtons.forEach(btn => {
    btn.addEventListener("click", () => {
      state.mode = btn.dataset.mode;
      syncUIFromState();
      schedulePreviewRefresh();
    });
  });

  // RGB Wave Dynamics (Evofox style)
  if (rgbSpeedSlider) {
    rgbSpeedSlider.addEventListener("input", (e) => {
      state.rgbSpeed = parseInt(e.target.value, 10);
      syncUIFromState();
      schedulePreviewRefresh();
    });
  }

  if (rgbDirectionSelector) {
    rgbDirectionSelector.querySelectorAll(".seg-btn").forEach(btn => {
      btn.addEventListener("click", () => {
        state.rgbDirection = btn.dataset.dir;
        syncUIFromState();
        schedulePreviewRefresh();
      });
    });
  }
  
  // Angle slider
  angleSlider.addEventListener("input", (e) => {
    state.angle = parseInt(e.target.value, 10);
    angleDisplay.textContent = `${state.angle}°`;
    gradientPreviewStrip.style.background = `linear-gradient(${state.angle}deg, ${state.colorA}, ${state.colorB})`;
    schedulePreviewRefresh();
  });
  
  // Outline options
  outlineOptions.forEach(opt => {
    opt.addEventListener("click", () => {
      outlineOptions.forEach(o => o.classList.remove("active"));
      opt.classList.add("active");
      const val = opt.dataset.outline;
      if (val === "custom") {
        customOutlineRow.style.display = "flex";
        state.outlineColor = pickerOutline.value;
      } else {
        customOutlineRow.style.display = "none";
        state.outlineColor = val;
      }
      schedulePreviewRefresh();
    });
  });
  
  pickerOutline.addEventListener("input", (e) => {
    state.outlineColor = e.target.value;
    hexInputOutline.value = state.outlineColor;
    customOutlineSwatch.style.background = state.outlineColor;
    schedulePreviewRefresh();
  });
  
  hexInputOutline.addEventListener("change", (e) => {
    let val = e.target.value.trim();
    if (!val.startsWith("#")) val = "#" + val;
    if (/^#[0-9A-Fa-f]{6}$/.test(val)) {
      state.outlineColor = val;
      pickerOutline.value = val;
      customOutlineSwatch.style.background = val;
      schedulePreviewRefresh();
    }
  });
  
  baseTypeSelect.addEventListener("change", (e) => {
    state.baseType = e.target.value;
    schedulePreviewRefresh();
  });
  
  // Category Filter chips
  filterChips.forEach(chip => {
    chip.addEventListener("click", () => {
      filterChips.forEach(c => c.classList.remove("active"));
      chip.classList.add("active");
      state.activeCategory = chip.dataset.cat;
      renderCursorCards();
    });
  });
  
  // Search input
  const searchInput = document.getElementById("cursorSearchInput");
  if (searchInput) {
    searchInput.addEventListener("input", (e) => {
      state.searchQuery = e.target.value;
      renderCursorCards();
    });
  }

  // Sandbox Contrast Switcher
  const sandboxBgBtns = document.querySelectorAll("#sandboxBgSwitcher .bg-switch-btn");
  sandboxBgBtns.forEach(btn => {
    btn.addEventListener("click", () => {
      sandboxBgBtns.forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      const bg = btn.dataset.bg;
      sandboxPad.classList.remove("mode-light", "mode-wallpaper");
      if (bg === "light") {
        sandboxPad.classList.add("mode-light");
      } else if (bg === "wallpaper") {
        sandboxPad.classList.add("mode-wallpaper");
      }
    });
  });

  // DPI Scale Selector
  const dpiBtns = document.querySelectorAll("#dpiScaleSwitcher .dpi-btn");
  dpiBtns.forEach(btn => {
    btn.addEventListener("click", () => {
      dpiBtns.forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      const scale = parseFloat(btn.dataset.scale) || 1;
      testTargets.forEach(t => {
        t.style.transform = scale === 1 ? "" : `scale(${scale})`;
        t.style.transformOrigin = "center center";
      });
    });
  });
  
  // Apply Button
  btnApply.addEventListener("click", async () => {
    btnApply.disabled = true;
    btnApply.style.opacity = "0.7";
    showToast("Applying customized cursors to Windows...", false, 2000);
    
    try {
      if (window.pywebview && window.pywebview.api && window.pywebview.api.apply_theme) {
        const res = await window.pywebview.api.apply_theme(getConfig());
        if (res.success) {
          showToast(res.message, false, 4000);
        } else {
          showToast(res.message, true, 4000);
        }
      }
    } catch (err) {
      showToast(`Error applying theme: ${err.message}`, true, 4000);
    } finally {
      btnApply.disabled = false;
      btnApply.style.opacity = "1";
    }
  });
  
  // Revert Button
  btnRevert.addEventListener("click", async () => {
    btnRevert.disabled = true;
    showToast("Restoring standard Windows Aero default...", false, 2000);
    
    try {
      if (window.pywebview && window.pywebview.api && window.pywebview.api.revert_default) {
        const res = await window.pywebview.api.revert_default();
        if (res.success) {
          showToast(res.message, false, 4000);
        } else {
          showToast(res.message, true, 4000);
        }
      }
    } catch (err) {
      showToast(`Error reverting: ${err.message}`, true, 4000);
    } finally {
      btnRevert.disabled = false;
    }
  });
  
  // Export Button
  btnExport.addEventListener("click", async () => {
    try {
      if (window.pywebview && window.pywebview.api && window.pywebview.api.export_theme) {
        const res = await window.pywebview.api.export_theme(getConfig());
        if (res.success) {
          showToast(res.message, false, 5000);
        } else {
          showToast(res.message, true, 4000);
        }
      }
    } catch (err) {
      showToast(`Error exporting: ${err.message}`, true, 4000);
    }
  });
}

// Dynamic Display Metrics Discovery
async function updateDisplayMetrics() {
  const displayElem = document.getElementById("sysDisplayMetrics");
  const refreshElem = document.getElementById("sysRefreshRate");
  const sepElem = document.getElementById("sysMetricsSep");
  if (!displayElem || !refreshElem) return;

  // 1. Initial immediate estimation via browser screen API
  try {
    const dpr = window.devicePixelRatio || 1;
    const w = Math.round((window.screen.width || 1920) * dpr);
    const h = Math.round((window.screen.height || 1080) * dpr);
    const dpi = Math.round(dpr * 100);
    displayElem.textContent = `${w}×${h} @ ${dpi}% DPI`;
  } catch (_) {}

  // 2. Exact physical query via Win32 API bridge
  try {
    if (window.pywebview && window.pywebview.api && window.pywebview.api.get_display_info) {
      const info = await window.pywebview.api.get_display_info();
      if (info && info.display_str) {
        displayElem.textContent = info.display_str;
        if (info.hz_str) {
          refreshElem.textContent = info.hz_str;
          refreshElem.style.display = "inline-block";
          if (sepElem) sepElem.style.display = "inline-block";
        }
      }
    }
  } catch (err) {
    console.warn("Display info query error:", err);
  }
}

// Window init
window.addEventListener("pywebviewready", () => {
  console.log("pywebview API ready!");
  updateDisplayMetrics();
  fetchPreviews();
});

document.addEventListener("DOMContentLoaded", () => {
  initAppTheming();
  initColorPickerPopover();
  initPresets();
  syncUIFromState();
  setupEvents();
  updateDisplayMetrics();
  
  // In case pywebviewready already fired
  setTimeout(() => {
    updateDisplayMetrics();
    fetchPreviews();
  }, 100);
});

