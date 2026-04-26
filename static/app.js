const canvas = document.getElementById("canvas");
const statusText = document.getElementById("status");
const saveButton = document.getElementById("saveButton");
const resetButton = document.getElementById("resetButton");
const itemTemplate = document.getElementById("itemTemplate");

const state = {
  layout: null,
  scaleX: 1,
  scaleY: 1,
};

function setStatus(message) {
  statusText.textContent = message;
}

function clamp(value, min, max) {
  return Math.min(Math.max(value, min), max);
}

function updateScale() {
  if (!state.layout) {
    return;
  }

  state.scaleX = canvas.clientWidth / state.layout.canvas.width;
  state.scaleY = canvas.clientHeight / state.layout.canvas.height;
}

function positionElement(element, item) {
  element.style.left = `${item.x * state.scaleX}px`;
  element.style.top = `${item.y * state.scaleY}px`;
}

function drawItems() {
  canvas.replaceChildren();
  updateScale();

  for (const [key, item] of Object.entries(state.layout.items)) {
    const element = itemTemplate.content.firstElementChild.cloneNode(true);
    element.dataset.key = key;
    element.textContent = item.label;
    positionElement(element, item);
    attachDrag(element, key);
    canvas.appendChild(element);
  }
}

function attachDrag(element, key) {
  let startX = 0;
  let startY = 0;
  let pointerId = null;

  element.addEventListener("pointerdown", (event) => {
    pointerId = event.pointerId;
    startX = event.clientX;
    startY = event.clientY;
    element.classList.add("dragging");
    element.setPointerCapture(pointerId);
  });

  element.addEventListener("pointermove", (event) => {
    if (pointerId !== event.pointerId) {
      return;
    }

    const item = state.layout.items[key];
    const deltaX = (event.clientX - startX) / state.scaleX;
    const deltaY = (event.clientY - startY) / state.scaleY;

    startX = event.clientX;
    startY = event.clientY;

    item.x = clamp(Math.round(item.x + deltaX), 0, state.layout.canvas.width - 1);
    item.y = clamp(Math.round(item.y + deltaY), 0, state.layout.canvas.height - 1);
    positionElement(element, item);
    setStatus(`Moved ${item.label} to (${item.x}, ${item.y})`);
  });

  function finishDrag(event) {
    if (pointerId !== event.pointerId) {
      return;
    }

    element.classList.remove("dragging");
    element.releasePointerCapture(pointerId);
    pointerId = null;
  }

  element.addEventListener("pointerup", finishDrag);
  element.addEventListener("pointercancel", finishDrag);
}

async function loadLayout() {
  const response = await fetch("/layout");
  if (!response.ok) {
    throw new Error("Failed to load layout");
  }
  state.layout = await response.json();
  drawItems();
  setStatus("Layout loaded. Drag labels on the preview, then save.");
}

async function saveLayout() {
  saveButton.disabled = true;
  setStatus("Saving layout...");

  const response = await fetch("/layout", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ items: state.layout.items }),
  });

  saveButton.disabled = false;

  if (!response.ok) {
    setStatus("Could not save layout.");
    return;
  }

  state.layout = await response.json();
  drawItems();
  setStatus("Layout saved.");
}

saveButton.addEventListener("click", saveLayout);
resetButton.addEventListener("click", drawItems);
window.addEventListener("resize", drawItems);

loadLayout().catch((error) => {
  console.error(error);
  setStatus("Could not load layout.");
});
