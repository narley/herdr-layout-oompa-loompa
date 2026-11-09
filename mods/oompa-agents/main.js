// Oompa Loompa workers: every agent is a factory worker with an animated sprite.
// A Claude Code card shows its session from the `claude.stats` terminal label
// (~/.config/herdr/claude-desktop.sh writes it on each machine; labels reach this app
// live, remote agents too): name, repo · branch, model · spend, a Cocoa bar (context
// left) and a Sugar bar (5-hour quota left), the prompt cache and running helpers.
// Inspired by herdr-traveler's traveler-agents (Apache-2.0, Frank Lin); reads no files
// but jobs.json, runs nothing, opens no connection.
import { View, div, image, svg } from "gpui-kit";
import { h_flex, v_flex } from "gpui-base";
import { hc, notify, agents, terminals, spaces, panes, openOverlay, appHome, readTextFile, run, setAgentOrder, theme, shared, setShared } from "herdr";
import { ALERT, FX, JOBS, agentKey, allKeys, appLabel, assignJobs, fxPath, jobIn, portraitPath, spritePath } from "./lib.js";

const JOBS_FILE = `${appHome()}/mods/oompa-agents/jobs.json`;
const SPRITE_W = 72;
const SPRITE_H = 96;
const CREW = "oompa.crew";   // { <session>: { job, at } }: workers changed by clicking them
const KEEP_CREW = 60;        // kept for sessions no longer on screen
const MIN = "cards.min";   // { <terminal address>:<created_ms>: true } for minimised cards
const STATUS = { detached: "Detached", working: "Mixing", blocked: "Needs you", done: "Done", idle: "Resting" };
const STALE_S = 12 * 3600;   // older stats are marked "old", never guessed
const SUB_FRESH_S = 90;      // a helper count with no watcher behind it

// address -> parsed claude.stats, for live Claude sessions (the label outlives Claude).
function claudeStats(all, list) {
  const claude = new Set(list.filter((a) => a.app === "claude-code").map((a) => a.address));
  const out = new Map();
  for (const t of all) {
    const raw = t.labels?.["claude.stats"];
    if (!raw || !claude.has(t.address) || t.state !== "live") continue;
    try { out.set(t.address, JSON.parse(raw)); } catch { /* skip a half-written label */ }
  }
  return out;
}

// What the context, usage limit and prompt cache readings mean, with the numbers behind them.
const tipTokens = (n) => (n >= 1e6 ? `${(n / 1e6).toFixed(1)}M` : `${Math.round(n / 1000)}k`);
const tipPad = (n) => String(n).padStart(2, "0");
const tipClock = (at) => { const d = new Date(at * 1000); return `${tipPad(d.getHours())}:${tipPad(d.getMinutes())}`; };
const tipDay = (at) => `${["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"][new Date(at * 1000).getDay()]} ${tipClock(at)}`;
const tipUntil = (d) => (d >= 3600 ? `${Math.floor(d / 3600)}h ${Math.floor((d % 3600) / 60)}m` : `${Math.max(1, Math.floor(d / 60))}m`);
function contextTip(label, s) {
  const pct = s.ctx?.pct ?? 0;
  const size = s.ctx?.size ?? 200000;
  const estimated = s.parent ? "\nThe window size is an estimate for background sessions." : "";
  return `${label}: context left in this session.\n${pct}% used, about ${tipTokens((size * pct) / 100)} of ${tipTokens(size)} tokens.\nWhen it runs low, Claude compacts the conversation.${estimated}`;
}
function limitTip(label, s, now) {
  const who = s.profile && s.profile !== "default" ? ` (${s.profile} account)` : "";
  const five = s.rl?.five_hour;
  const week = s.rl?.seven_day;
  const current = five && five.resets_at > now
    ? `${Math.round(five.used_percentage ?? 0)}% used, resets at ${tipClock(five.resets_at)} (in ${tipUntil(five.resets_at - now)}).`
    : "No current reading: Claude reports it with its next reply.";
  const weekly = week && week.resets_at > now ? `\n7-day limit: ${Math.round(week.used_percentage ?? 0)}% used, resets ${tipDay(week.resets_at)}.` : "";
  return `${label}: your 5-hour usage limit left${who}.\n${current}${weekly}`;
}
function cacheTip(label, s, now) {
  const warm = s.cache?.warm === true && s.cache.exp > now;
  return warm
    ? `${label}: this session's prompt cache.\nWarm for ${tipUntil(s.cache.exp - now)} more, until ${tipClock(s.cache.exp)}.\nA reply before then reuses it, which costs less.`
    : `${label}: this session's prompt cache.\nIt has expired.\nThe next reply rebuilds it, which costs more.`;
}

// Close and Delete worktree, shown on hover. session-actions asks before doing anything.
const actionInfo = (a, s) => ({ address: a.address, name: s?.name || a.address, bg: a.bg ?? null, sid: s?.sid ?? null, profile: s?.profile ?? null, dir: s?.dir ?? null });
function actionButtons(a, s, kids, t) {
  const chip = (id, label, tip, action) => div().id(`${id}-${a.address}`).size(18).flex().items_center().justify_center().rounded(4).border(1).border_color(t.dim).bg(t.popover)
    .cursor_pointer().hover((x) => x.bg(t.hover)).tooltip(tip)
    .on_click((_e, cx) => {
      cx.stop_propagation();
      openOverlay({ mod: "session-actions", kind: "dialog", modal: true, width: 480, height: 300, props: { action, session: actionInfo(a, s), kids: kids.map((k) => actionInfo(k, k.stats)) } });
    })
    .child(label);
  return h_flex().gap(4).child(chip("act-close", svg("mods/pane/close.svg").size(12).text_color(t.accent), "Close this session", "close"))
    .when(s?.loc === "wt" && Boolean(s?.dir), (el) => el.child(chip("act-wt", svg("mods/oompa-agents/bin.svg").size(12).text_color(t.accent), "Close this session and delete its worktree", "worktree")));
}

// An attached session's pane can lose Claude (a restart, a crash) and fall back to a shell, while
// its old labels stay. Such a card is DETACHED, and clicking it reattaches: it only types when the
// pane is at a shell prompt, so anything else running there just gets focus.
const detachedFrom = (t) => {
  const fg = t.foreground;
  return Boolean(fg) && !(fg.argv ?? []).join(" ").includes("claude") && !/^\d+\.\d+\.\d+/.test(fg.name ?? "");
};
const atShell = (t) => /^-?(zsh|bash|fish|sh|dash)$/.test(String(t.foreground?.name ?? "").split("/").pop());
async function reattach(k) {
  run("pane.focus", { terminal: k.address });
  if (!k.shell || !/^[A-Za-z0-9_-]+$/.test(k.bg ?? "")) return;
  const profile = k.stats?.profile;
  const config = profile && profile !== "default" && /^[A-Za-z0-9_-]+$/.test(profile) ? `CLAUDE_CONFIG_DIR="$HOME/.claude-${profile}" ` : "";
  await hc(["keys", k.address, "ctrl+u"]);   // anything half-typed at the prompt
  const r = await hc(["send", k.address, `${config}claude attach ${k.bg}`]);
  if (r.code !== 0) notify({ title: "Couldn't reattach", body: (r.stderr || r.stdout || "").trim(), level: "error" });
}

// Attached background sessions (`claude --bg` in a child terminal labelled claude.bg), by
// their parent's address, as agent-shaped rows. Their stats label names the parent.
function bgChildren(all) {
  const out = new Map();
  for (const t of all) {
    const raw = t.labels?.["claude.stats"];
    if (!raw || !t.labels?.["claude.bg"] || t.state !== "live") continue;
    let s;
    try { s = JSON.parse(raw); } catch { continue; }
    if (!s.parent) continue;
    const machine = t.address.includes("/") ? `${t.address.split("/")[0]}/` : "";
    const key = `${machine}${s.parent}`;
    const status = detachedFrom(t) ? "detached" : s.state === "working" || s.state === "busy" ? "working" : /input|wait|block/.test(s.state ?? "") ? "blocked" : "idle";
    out.set(key, [...(out.get(key) ?? []), { address: t.address, app: "claude-code", status, shell: atShell(t), focused: false, bg: t.labels["claude.bg"], tab_name: s.name ?? t.address, stats: s }]);
  }
  for (const kids of out.values()) kids.sort((x, y) => String(x.stats.name ?? x.address).localeCompare(String(y.stats.name ?? y.address)));
  return out;
}

const cacheText = (s, now) => {
  if (s.cache?.warm === true && s.cache.exp > now) {
    const d = s.cache.exp - now;
    return { text: d >= 3600 ? `${Math.floor(d / 3600)}h ${Math.floor((d % 3600) / 60)}m warm` : d >= 60 ? `${Math.floor(d / 60)}m warm` : "<1m warm", hot: d < 60 };
  }
  return s.cache?.warm != null ? { text: "cache cold", hot: true } : null;
};

// Everything a minimised card is hiding, for its tooltip.
function foldedTip(a, s, name, who, word, machine, now, kids) {
  if (a.status === "detached") return `${name}\nDetached. Click to reattach.`;
  const where = machine ? ` @${machine}` : "";
  const lines = [name, [who, word].filter(Boolean).join(" · ")];
  if (s) {
    lines.push(`${s.repo || "~"}${where}`);
    if (s.branch) lines.push(`${s.loc === "wt" ? "wt" : "br"}: ${s.branch}`);
    const spend = s.tokens != null && s.cost == null ? `${Math.floor(s.tokens / 1000)}k tok` : `$${(s.cost ?? 0).toFixed(2)}`;
    lines.push(`${s.model ?? "claude"}${s.effort ? ` ${s.effort}` : ""} · ${spend}`);
    const stale = now - (s.at ?? 0) > STALE_S ? " (old)" : "";
    const five = s.rl?.five_hour;
    lines.push(`COCOA: ${100 - (s.ctx?.pct ?? 0)}% left${stale}`);
    lines.push(`SUGAR: ${five && five.resets_at > now ? `${Math.round(100 - (five.used_percentage ?? 0))}% left${stale}` : "—"}`);
    const fresh = s.subs && now - (s.subs.at ?? 0) <= SUB_FRESH_S;
    const total = (fresh ? s.subs.n ?? 0 : 0) + (a.status === "working" ? 1 : 0);
    const d = s.cache?.warm === true ? s.cache.exp - now : 0;
    const link = [
      s.cache?.warm == null ? null : d > 0 ? `cache ${d >= 3600 ? `${Math.floor(d / 3600)}h${Math.floor((d % 3600) / 60)}m` : d >= 60 ? `${Math.floor(d / 60)}m` : "<1m"}` : "cache lost",
      total > 0 ? `${total} running` : null,
      s.rc ? "rc" : null,
    ].filter(Boolean);
    if (link.length) lines.push(link.join(" · "));
    if (fresh) for (const n of s.subs.helpers ?? s.subs.names ?? []) lines.push(`  ${n}`);
  } else {
    lines.push(`${a.app ?? a.program?.name ?? "program"}${where}`);
    lines.push(a.app === "claude-code" ? "stats after its next reply" : "no telemetry");
  }
  if (kids.length) lines.push("Attached:", ...kids.map((k) => `  ${k.stats?.name || k.address}: ${STATUS[k.status] ?? k.status}`));
  return lines.join("\n");
}

export default class Workers extends View {
  init(_props, cx) {
    this.jobs = {};
    cx.spawn(async (cx) => {
      const text = await readTextFile(JOBS_FILE).catch(() => null);
      try { const j = JSON.parse(text); if (j && typeof j === "object" && !Array.isArray(j)) this.jobs = j; } catch {}
      cx.notify();
    });
    // The cache timer and stale marks move with the clock.
    cx.timer.every(30000, (cx) => cx.notify());
  }

  // Who this session is, for a worker changed by clicking: a Claude session by its id, anything
  // else by its terminal's life.
  crewKey(a, s) {
    return s?.sid ? `sid:${s.sid}` : `term:${a.address}:${this.terms?.get(a.address)?.created_ms ?? ""}`;
  }

  // The worker someone clicked to, else the one its tab or jobs.json gives it.
  jobOf(a, s) {
    return shared(CREW)?.[this.crewKey(a, s)]?.job ?? jobIn(agentKey(a, this.sp), this.assigned);
  }

  // Another worker, preferring one nobody on screen is.
  changeJob(a, s) {
    const crew = { ...(shared(CREW) ?? {}) };
    const current = this.jobOf(a, s);
    const free = JOBS.filter((j) => j !== current && !this.crewTaken?.has(j));
    const pool = free.length ? free : JOBS.filter((j) => j !== current);
    crew[this.crewKey(a, s)] = { job: pool[Math.floor(Math.random() * pool.length)], at: Date.now() };
    const old = Object.keys(crew).sort((x, y) => (crew[y].at ?? 0) - (crew[x].at ?? 0)).slice(KEEP_CREW);
    for (const k of old) delete crew[k];
    setShared(CREW, crew);
  }

  sprite(a, t, job) {
    const src = spritePath(job, a.status);
    if (src) {
      // the worker breathes; the working effect plays; a pink "!" bubble pulses when they need you
      const layer = (p) => image(p).absolute().top(0).left(0).w(SPRITE_W).h(SPRITE_H);
      const [prop, policy] = FX[job] ?? ["opacity", { from: 0.4, to: 1, period: 1000 }];
      return div().relative().w(SPRITE_W).h(SPRITE_H).flex_none().overflow_hidden()
        .child(layer(src).when(a.status !== "blocked", (el) => el.loop("top", { from: 0, to: 1.5, period: 3200 })))
        .when(a.status === "working", (el) => el.child(layer(fxPath(job)).loop(prop, policy)))
        .when(a.status === "blocked", (el) => el.child(layer(ALERT).loop("opacity", { from: 0.3, to: 1, period: 700 })));
    }
    const pic = portraitPath(job);
    if (pic) return image(pic).w(SPRITE_W).h(SPRITE_W).flex_none();
    const p = a.program;
    if (!p?.icon) return div().w(SPRITE_W).h(SPRITE_W).flex_none();
    return p.tint ? svg(p.icon).size(SPRITE_W).flex_none().text_color(t.foreground) : image(p.icon).w(SPRITE_W).h(SPRITE_W).flex_none();
  }

  // A labelled bar; null value: an empty track and "—".
  bar(label, value, color, old, t) {
    const v = value == null ? null : Math.max(0, Math.min(100, Math.round(value)));
    return h_flex().w_full().min_w(0).h(13).gap(6).items_center()
      .child(div().w(38).flex_none().text_size(9.5).font_semibold().text_color(t.dim).child(label))
      .child(h_flex().flex_1().min_w(0).h(6).bg(t.raised).rounded(3).overflow_hidden()
        .when(v !== null, (el) => el.child(div().h_full().w(`${v}%`).bg(color).rounded(3))))
      .child(div().w(34).flex_none().text_right().text_size(10.5).text_color(old ? t.dim : t.foreground)
        .child(v === null ? "—" : old ? `${v}% old` : `${v}%`));
  }

  // A minimised card belongs to its terminal's life: a reused terminal id starts expanded.
  minKey(address) {
    return `${address}:${this.terms?.get(address)?.created_ms ?? ""}`;
  }

  toggleMin(address) {
    const min = { ...(shared(MIN) ?? {}) };
    const key = this.minKey(address);
    if (min[key]) delete min[key];
    else min[key] = true;
    // a parent takes its attached sessions with it; each can still be opened on its own
    for (const k of this.allKids?.get(address) ?? []) { if (min[key]) min[this.minKey(k.address)] = true; else delete min[this.minKey(k.address)]; }
    const live = new Set([...(this.terms?.keys() ?? [])].map((k) => this.minKey(k)));
    for (const k of Object.keys(min)) if (!live.has(k)) delete min[k];
    setShared(MIN, min);
  }

  // Every card, attached sessions included. Expanding clears the lot, which also drops ended terminals.
  setAllMin(everyone, folded) {
    setShared(MIN, folded ? Object.fromEntries(everyone.map((a) => [this.minKey(a.address), true])) : {});
  }

  // In the header: expands when every card is minimised, otherwise minimises them all.
  minAllButton(everyone, t) {
    const min = shared(MIN) ?? {};
    const allFolded = everyone.every((a) => min[this.minKey(a.address)]);
    return div().id("card-min-all").size(16).flex_none().flex().items_center().justify_center().border(1).border_color(t.dim).rounded(5)
      .text_size(12).font_semibold().text_color(t.muted).cursor_pointer().hover((x) => x.bg(t.hover).text_color(t.accent))
      .tooltip(allFolded ? "Expand all sessions" : "Minimise all sessions")
      .on_click((_e, cx) => { cx.stop_propagation(); this.setAllMin(everyone, !allFolded); })
      .child(allFolded ? "+" : "\u2013");
  }

  // Shown while the pointer is over the card.
  minButton(a, folded, t) {
    return div().id(`card-min-${a.address}`).size(16).flex_none().flex().items_center().justify_center().border(1).border_color(t.dim).rounded(5)
      .text_size(12).font_semibold().text_color(t.muted).cursor_pointer().hover((x) => x.bg(t.hover).text_color(t.accent))
      .tooltip(folded ? "Expand this session" : "Minimise this session")
      .on_click((_e, cx) => { cx.stop_propagation(); this.toggleMin(a.address); })
      .child(folded ? "+" : "\u2013");
  }

  // A minimised card's one line: avatar, name, attached sessions folded inside, status.
  // The tooltip is on the text, not the whole row, so the button keeps its own.
  foldedRow(a, name, who, status, tip, kids, t) {
    return [
      h_flex().id(`card-info-${a.address}`).flex_1().min_w(0).h_full().gap(7).items_center().tooltip(tip)
        .when(Boolean(who), (el) => el.child(div().flex_none().min_w(46).text_size(9.5).font_semibold().text_color(t.muted).child(who)))
        .child(div().flex_1().min_w(0).truncate().font_semibold().text_size(12).text_color(t.foreground).child(name))
        .child(status),
      this.hoveredCard === a.address && this.minButton(a, true, t),
    ].filter(Boolean);
  }

  // One worker's row; a parent's box also holds its attached sessions, nested below it.
  card(a, s, now, t, stats, kids = [], nested = false) {
    const blocked = a.status === "blocked";
    const statusColor = t[a.status] ?? t.dim;
    const label = appLabel(a.app);
    const old = s && now - (s.at ?? 0) > STALE_S;
    const name = s?.name || agentKey(a, this.sp) || a.address;
    const machine = a.address.includes("/") ? a.address.split("/")[0] : null;
    const line = (key, kids) => h_flex().id(`ol-${key}-${a.address}`).w_full().min_w(0).h(15).items_center().gap(0).overflow_hidden().whitespace_nowrap().text_size(11).children(kids.filter(Boolean));
    const span = (text, color, bold) => div().flex_none().text_color(color).when(Boolean(bold), (el) => el.font_semibold()).child(text);
    const flex = (text, color) => div().min_w(0).truncate().text_color(color).child(text);
    const dot = () => span(" · ", t.dim);

    const folded = Boolean(shared(MIN)?.[this.minKey(a.address)]);
    const status = () => div().flex_none().text_size(10.5).font_semibold().text_color(statusColor).child(STATUS[a.status] ?? a.status);
    const job = this.jobOf(a, s);
    const rows = [h_flex().w_full().min_w(0).gap(6).items_center()
      .child(div().flex_1().min_w(0).truncate().font_semibold().text_color(t.foreground).child(name))
      .child(status())
      .when(this.hoveredCard === a.address, (el) => el.child(this.minButton(a, false, t)))];
    const body = { child: (el) => rows.push(el) };

    if (a.status === "detached") {
      body.child(line("detached", [flex("Click to reattach", t.accent)]));
    } else if (s) {
      // repo and the machine when it isn't this one, then the branch (wt: a linked worktree)
      if (s.repo || machine) body.child(line("where", [s.repo && flex(s.repo, t.muted), machine && span(s.repo ? `  ${machine}` : machine, t.dim)]));
      if (s.branch) body.child(line("branch", [flex(`${s.loc === "wt" ? "wt" : "br"}: ${s.branch}`, t.muted)]));
      // [Claude] model effort ............ $spend
      const spend = s.tokens != null && s.cost == null ? `${Math.floor(s.tokens / 1000)}k tok` : `$${(s.cost ?? 0).toFixed(2)}`;
      body.child(h_flex().w_full().min_w(0).h(16).gap(6).items_center()
        .child(div().flex_none().px(5).rounded(4).border(1).border_color(t.accent).text_size(9.5).font_semibold().text_color(t.accent).child("Claude"))
        .child(div().flex_1().min_w(0).truncate().text_size(11).text_color(t.muted).child(`${s.model ?? ""}${s.effort ? ` ${s.effort}` : ""}`))
        .child(div().flex_none().text_size(11).font_semibold().text_color(t.ansi2).child(spend)));
      // Cocoa: context left (red under 10%, orange under 25%); Sugar: 5-hour quota left
      const cocoa = 100 - (s.ctx?.pct ?? 0);
      const five = s.rl?.five_hour;
      const sugar = five && five.resets_at > now ? 100 - (five.used_percentage ?? 0) : null;
      body.child(div().id(`ol-cocoa-${a.address}`).w_full().tooltip(contextTip("COCOA", s)).child(this.bar("COCOA", cocoa, cocoa < 10 ? t.blocked : cocoa < 25 ? t.ansi3 : t.solid, old, t)));
      body.child(div().id(`ol-sugar-${a.address}`).w_full().tooltip(limitTip("SUGAR", s, now)).child(this.bar("SUGAR", sugar, sugar != null && sugar < 10 ? t.blocked : t.ansi5, old, t)));
      // cache · helpers: the main session counts while it works, as in the herdr TUI card
      const cache = cacheText(s, now);
      const fresh = s.subs && now - (s.subs.at ?? 0) <= SUB_FRESH_S;
      const helpers = fresh ? s.subs.n ?? 0 : 0;
      const total = helpers + (a.status === "working" ? 1 : 0);
      if (cache || total) {
        body.child(line("cache", [
          cache && span(cache.text, cache.hot ? t.blocked : t.dim).id(`ol-cachetip-${a.address}`).tooltip(cacheTip("CACHE", s, now)),
          cache && total && dot(),
          total && span(`${total} running`, t.muted),
          s.rc && dot(), s.rc && span("rc", t.ansi5),
        ]));
      }
      // helpers only: attached sessions get their own nested cards
      if (fresh) (s.subs.helpers ?? s.subs.names ?? []).slice(0, 3).forEach((n, i, arr) => {
        const last = i === arr.length - 1 && (s.subs.hn ?? helpers) <= arr.length;
        body.child(line(`sub${i}`, [flex(`${last ? "└" : "├"} ${n}`, t.dim)]));
      });
    } else if (label) {
      body.child(h_flex().w_full().min_w(0).h(16).gap(6).items_center()
        .child(div().flex_none().px(5).rounded(4).border(1).border_color(label.builder ? t.unknown : t.accent).text_size(9.5).text_color(label.builder ? t.unknown : t.accent).child(label.text))
        .when(Boolean(machine), (el) => el.child(div().text_size(11).text_color(t.dim).child(machine))));
      if (!label.builder) body.child(line("wait", [span("stats after its next reply", t.dim)]));
    }

    const head = h_flex()
      .id(`worker-head-${a.address}`)
      .relative()
      .w_full()
      .flex_none()
      .when(folded, (el) => el.h(28).px(8).gap(7))
      .when(!folded, (el) => el.p(8).gap(10))
      .items_center()
      .rounded(10)
      .when(nested && blocked, (el) => el.bg(`${t.blocked}22`))
      // inside a group, a lighter border marks the selected session
      .when(nested || kids.length > 0, (el) => el.border(1).border_color(this.focusedTerm === a.address ? t.foreground : "#00000000"))
      .cursor_pointer()
      .hover((st) => st.bg(t.hover))
      .on_click(() => a.status === "detached" ? reattach(a) : run(nested ? "pane.focus" : "agent.focus", { terminal: a.address }))
      .on_hover((on, cx) => {
        if (on) this.hoveredCard = a.address;
        else if (this.hoveredCard === a.address) this.hoveredCard = null;
        cx.notify();
      })
      .when(folded, (el) => {
        const who = job && `${job[0].toUpperCase()}${job.slice(1)}`;
        return el.children(this.foldedRow(a, name, who, status(), foldedTip(a, s, name, who, STATUS[a.status] ?? a.status, machine, now, kids), kids, t));
      })
      .when(!folded, (el) => el.child(job
          ? div().id(`worker-sprite-${a.address}`).flex_none().cursor_pointer()
              .tooltip(`${job[0].toUpperCase()}${job.slice(1)} · click to change`)
              .on_click((_e, cx) => { cx.stop_propagation(); this.changeJob(a, s); })
              .child(this.sprite(a, t, job))
          : this.sprite(a, t, job))
        .child(v_flex().flex_1().min_w(0).gap(3).children(rows))
        .when(this.hoveredCard === a.address, (e) => e.child(actionButtons(a, s, kids, t).absolute().right(6).bottom(6))));
    if (nested) return head;

    const alarm = blocked || kids.some((k) => k.status === "blocked");
    // the group stays highlighted while the parent or any of its sessions is selected
    const active = a.focused || this.focusedTerm === a.address || kids.some((k) => k.address === this.focusedTerm);
    return v_flex()
      .id(`worker-${a.address}`)
      .w_full()
      .flex_none()
      .bg(blocked ? `${t.blocked}22` : `${t.surface}d8`)
      .border(1)
      .border_color(alarm ? t.blocked : active ? t.accent : t.border)
      .rounded(10)
      .child(head)
      .children(kids.map((k, i) => h_flex().id(`worker-kid-${k.address}`).w_full().min_w(0).items_start().border_t(1).border_color(t.border)
        .child(div().flex_none().w(14).pt(6).text_center().text_size(11).text_color(t.dim).child(i === kids.length - 1 ? "└" : "├"))
        .child(div().flex_1().min_w(0).child(this.card(k, stats.get(k.address), now, t, stats, [], true)))));
  }

  render() {
    const t = theme();
    const all = terminals();
    const kids = bgChildren(all);
    this.allKids = kids;
    const flatKids = [...kids.values()].flat();
    const nestedAt = new Set(flatKids.map((k) => k.address));
    const list = agents().filter((a) => !nestedAt.has(a.address));
    this.sp = spaces();
    // sessions after tabs, so a nested session never changes a tab's worker
    this.assigned = assignJobs([...allKeys(this.sp), ...flatKids.map((k) => k.tab_name)], this.jobs);
    setAgentOrder(list.map((a) => a.address));
    this.focusedTerm = panes().find((p) => p.focused)?.terminal ?? null;
    this.terms = new Map(all.map((x) => [x.address, x]));
    const stats = claudeStats(all, list);
    for (const k of flatKids) stats.set(k.address, k.stats);
    this.crewTaken = new Set([...list, ...flatKids].map((a) => this.jobOf(a, stats.get(a.address))).filter(Boolean));
    const now = Math.floor(Date.now() / 1000);
    const busy = [...list, ...flatKids].filter((a) => a.status === "working").length;
    return v_flex().id("workers").size_full().min_h(0).text_color(t.foreground).text_size(13)
      .child(h_flex().h(30).flex_none().px(14).gap(6).items_center().bg(`${t.chrome}d8`).border_t(1).border_color(t.border)
        .child(div().text_size(11.5).font_semibold().text_color(t.accent).child("Workers"))
        .child(div().text_size(11).text_color(t.dim).child(`${list.length}`))
        .child(div().flex_1())
        .when(busy > 0, (el) => el.child(div().text_size(11).text_color(t.working).child(`${busy} mixing`)))
        .when(list.length + flatKids.length > 0, (el) => el.child(this.minAllButton([...list, ...flatKids], t))))
      .child(v_flex().id("worker-list").flex_1().min_h(0).gap(6).p(6).overflow_y_scrollbar()
        .children(list.map((a) => this.card(a, stats.get(a.address), now, t, stats, kids.get(a.address) ?? [])))
        .when(list.length === 0, (el) => el.child(div().p(8).text_size(12).text_color(t.dim).child("No workers yet. Agents show up here when they report their status."))));
  }
}
