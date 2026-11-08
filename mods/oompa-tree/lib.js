// Oompa Loompa layout: pure helpers shared by oompa-agents and oompa-tabs (a mod can't
// import from another mod's folder, so oompa-tabs/lib.js is a copy: change both).
// Adapted from herdr-traveler's traveler-agents/lib.js (Apache-2.0, Frank Lin).

// The factory jobs; each is an original candy-crew worker drawn as SVG by crew_svg.py:
// three full-body poses, a working effect, and a round face badge.
export const JOBS = ["stirrer", "taster", "taffy", "bubble", "rower", "ticket", "cracker", "singer"];
const JOB_SET = new Set(JOBS);
const CREW = "mods/oompa-agents/crew";

// What a tab is called for job matching: its own name when someone named it,
// else its space's name, so unnamed "1" tabs in different spaces get different workers.
export function tabKey(space, tab) {
  const name = tab?.named ? tab.name : space?.name ?? tab?.name;
  return typeof name === "string" ? name : "";
}
export function allKeys(spaces) {
  return (spaces ?? []).flatMap((s) => (s.tabs ?? []).map((t) => tabKey(s, t)));
}
// The key of the tab an agent sits in.
export function agentKey(agent, spaces) {
  for (const s of spaces ?? []) for (const t of s.tabs ?? []) if (t.id === agent.tab) return tabKey(s, t);
  return agent.tab_name ?? agent.space_name ?? "";
}

const norm = (n) => n.trim().toLowerCase();

// jobs.json: { "<tab or space name>": "<job>" }, matched whole, ignoring case.
export function jobFor(name, jobs) {
  if (typeof name !== "string" || !name.trim() || !jobs || typeof jobs !== "object" || Array.isArray(jobs)) return null;
  for (const key of Object.keys(jobs)) {
    if (norm(key) !== norm(name)) continue;
    const job = typeof jobs[key] === "string" ? jobs[key].trim() : null;
    return JOB_SET.has(job) ? job : null;
  }
  return null;
}

// Listed names first; the rest get a free job picked from the name, repeating only past eight.
export function assignJobs(names, jobs) {
  const list = [...new Set((names ?? []).filter((n) => typeof n === "string" && n.trim()).map(norm))];
  const out = new Map();
  const used = new Set();
  for (const key of list) {
    const job = jobFor(key, jobs);
    if (job) { out.set(key, job); used.add(job); }
  }
  for (const key of list) {
    if (out.has(key)) continue;
    if (used.size >= JOBS.length) used.clear();
    const start = [...key].reduce((n, c) => n + c.codePointAt(0), 0);
    const job = Array.from({ length: JOBS.length }, (_, i) => JOBS[(start + i) % JOBS.length]).find((j) => !used.has(j));
    out.set(key, job);
    used.add(job);
  }
  return out;
}
export const jobIn = (name, assigned) => (typeof name === "string" ? assigned.get(norm(name)) ?? null : null);

export const portraitPath = (job) => (JOB_SET.has(job) ? `${CREW}/${job}-face-classic-v3.svg` : null);
// The full-body pose: working, blocked (a raised hand), or resting for anything else.
export function spritePath(job, status) {
  if (!JOB_SET.has(job)) return null;
  return `${CREW}/${job}-${status === "working" ? "work" : status === "blocked" ? "blocked" : "rest"}-classic-v3.svg`;
}
export const fxPath = (job) => (JOB_SET.has(job) ? `${CREW}/${job}-fx.svg` : null);
export const ALERT = `${CREW}/alert.svg`;
// How each job's working effect moves (native loops): steam and bubbles rise, sparkles
// twinkle, the bubblegum bubble bobs, the river flows, notes drift up.
export const FX = {
  stirrer: ["top", { from: 3, to: -7, period: 1500 }],
  taster: ["opacity", { from: 0, to: 1, period: 900 }],
  taffy: ["opacity", { from: 0.15, to: 1, period: 520 }],
  bubble: ["top", { from: 2, to: -3, period: 1600 }],
  rower: ["left", { from: -14, to: 0, period: 1800 }],
  ticket: ["opacity", { from: 0, to: 1, period: 620 }],
  cracker: ["opacity", { from: 0, to: 1, period: 380 }],
  singer: ["top", { from: 4, to: -9, period: 1500 }],
};

// The program tag, from the agent's own report (OSC 7501).
const APPS = new Map([
  ["claude-code", { text: "Claude", builder: false }],
  ["codex", { text: "Codex", builder: true }],
  ["opencode", { text: "OpenCode", builder: true }],
  ["pi", { text: "Pi", builder: true }],
]);
export const appLabel = (app) => (APPS.has(app) ? { ...APPS.get(app) } : null);
