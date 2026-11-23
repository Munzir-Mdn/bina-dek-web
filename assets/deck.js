"use strict";

const slides = [...document.querySelectorAll(".slide")];
const byId = id => document.getElementById(id);
const notes = JSON.parse(byId("deck-data").textContent);
const panel = byId("presenter");
let index = 0;
let elapsed = 0;
let startedAt = null;

function formatTime(seconds) {
  const minutes = Math.floor(seconds / 60);
  return [minutes, seconds % 60].map(value => String(value).padStart(2, "0")).join(":");
}

function updateClock() {
  const running = startedAt === null ? 0 : performance.now() - startedAt;
  const current = Math.floor((elapsed + running) / 1000);
  byId("clock").textContent = formatTime(current);
}

function show(nextIndex, focus = false) {
  if (nextIndex < 0 || nextIndex >= slides.length) return;
  slides[index].hidden = true;
  index = nextIndex;
  const slide = slides[index];
  slide.hidden = false;
  byId("count").textContent = `${index + 1} / ${slides.length}`;
  byId("prev").disabled = index === 0;
  byId("next").disabled = index === slides.length - 1;
  byId("notes").textContent = notes[index].notes || "Tiada nota.";
  byId("planned").textContent = notes[index].seconds ? formatTime(notes[index].seconds) : "—";
  byId("upcoming").textContent = slides[index + 1]?.querySelector("h1").textContent || "Tamat";
  if (focus) slide.querySelector("h1").focus();
}

byId("prev").onclick = () => show(index - 1, true);
byId("next").onclick = () => show(index + 1, true);
byId("toggle").onclick = () => {
  panel.hidden = !panel.hidden;
  byId("toggle").setAttribute("aria-expanded", String(!panel.hidden));
};
byId("timer").onclick = () => {
  if (startedAt === null) {
    startedAt = performance.now();
    byId("timer").textContent = "Jeda";
  } else {
    elapsed += performance.now() - startedAt;
    startedAt = null;
    byId("timer").textContent = "Sambung";
  }
  updateClock();
};
byId("reset").onclick = () => {
  elapsed = 0;
  startedAt = null;
  byId("timer").textContent = "Mula";
  updateClock();
};

const keys = { ArrowLeft: () => index - 1, ArrowRight: () => index + 1,
  Home: () => 0, End: () => slides.length - 1 };
document.addEventListener("keydown", event => {
  if (event.altKey || event.ctrlKey || event.metaKey || event.shiftKey ||
      event.target.closest("input, textarea, select, [contenteditable]")) return;
  if (!Object.hasOwn(keys, event.key)) return;
  event.preventDefault();
  show(keys[event.key](), true);
});

show(0);
updateClock();
setInterval(updateClock, 250);
