#!/usr/bin/env python3
"""The candy crew for the Oompa Loompa Herdr layout: eight original full-body factory
workers as SVG (viewBox 0 0 120 160, shown at 72x96).
Writes mods/oompa-agents/crew/:
  <job>-rest.svg  <job>-work.svg  <job>-blocked.svg   full-body poses
  <job>-fx.svg                                       the working effect (animated by the mod)
  <job>-face.svg                                     a round badge for the tab bar
  alert.svg                                          the needs-you bubble
"""
import os, sys

OUT = os.path.join(sys.argv[1], "mods/oompa-agents/crew")


def mix(c, k):
    c = c.lstrip("#")
    r, g, b = (int(c[i:i + 2], 16) for i in (0, 2, 4))
    f = (lambda v: int(v + (255 - v) * (k - 1))) if k > 1 else (lambda v: int(v * k))
    return "#%02x%02x%02x" % tuple(max(0, min(255, f(v))) for v in (r, g, b))


def lin(id, c1, c2, x1=0, y1=0, x2=0, y2=1):
    return (f'<linearGradient id="{id}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"><stop offset="0" stop-color="{c1}"/>'
            f'<stop offset="1" stop-color="{c2}"/></linearGradient>')


def wrap(body, defs="", vb="0 0 120 160", w=120, h=160):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}" width="{w}" height="{h}"><defs>{defs}</defs>{body}</svg>\n'


# ── the crew ─────────────────────────────────────────────────────────────────
CREW = {   # the palette: raspberry velvet, cotton-candy pink, teal, cream, gilded gold, chocolate
    "stirrer": dict(skin="#f1c9a5", hair="#5a3a24", hat="toque",     outfit="#c8366a", trim="#f2c463", pants="#5a3524", tile="#f6a8c8"),
    "taster":  dict(skin="#a86f4c", hair="#1d1412", hat="stripes",   outfit="#f6a8c8", trim="#c8366a", pants="#4a2a3a", tile="#6fd0c0"),
    "taffy":   dict(skin="#e8b896", hair="#b8452a", hat="bandana",   outfit="#6fc8b8", trim="#2f7f78", pants="#3a2a40", tile="#f6a8c8"),
    "bubble":  dict(skin="#7a4a32", hair="#120c0a", hat="beret",     outfit="#f6e7c8", trim="#c8366a", pants="#5a3524", tile="#e0457b"),
    "rower":   dict(skin="#d9a27c", hair="#e3c06a", hat="sailor",    outfit="#3f9a94", trim="#f6e7c8", pants="#2a3a44", tile="#6fd0c0"),
    "ticket":  dict(skin="#f3d2b8", hair="#2a1a14", hat="conductor", outfit="#f2c463", trim="#8c1f4a", pants="#5a3524", tile="#f2c463"),
    "cracker": dict(skin="#8d5a3b", hair="#3a2418", hat="hardhat",   outfit="#8a5638", trim="#f2c463", pants="#3a2216", tile="#c8366a"),
    "singer":  dict(skin="#c68863", hair="#6e2d6a", hat="bowler",    outfit="#8c1f4a", trim="#f6a8c8", pants="#2e1a26", tile="#f6e7c8"),
}

SH_L, SH_R = (47, 70), (73, 70)   # shoulders


def arm(shoulder, hand, sleeve, skin, bend=1):
    (sx, sy), (hx, hy) = shoulder, hand
    mx, my = (sx + hx) / 2, (sy + hy) / 2
    ex, ey = mx + bend * (hy - sy) * 0.18, my - bend * (hx - sx) * 0.18   # an elbow off the straight line
    return (f'<path d="M{sx},{sy} Q{ex:.1f},{ey:.1f} {hx},{hy}" fill="none" stroke="{sleeve}" stroke-width="8.5" stroke-linecap="round"/>'
            f'<circle cx="{hx}" cy="{hy}" r="4.6" fill="{skin}" stroke="{mix(skin, 0.75)}" stroke-width="0.8"/>')


def hat(kind, c):
    t, o = c["trim"], c["outfit"]
    if kind == "toque":       # a tall chef's hat
        return ('<path d="M44,30 C36,26 38,12 48,13 C50,4 70,4 72,13 C82,12 84,26 76,30 Z" fill="#fffaf2" stroke="#e2d8c8" stroke-width="1"/>'
                '<rect x="43" y="27" width="34" height="7" rx="2" fill="#fffaf2" stroke="#e2d8c8" stroke-width="1"/>'
                f'<path d="M52,14 L52,26 M60,10 L60,26 M68,14 L68,26" stroke="#ece2d2" stroke-width="1.4"/>')
    if kind == "stripes":     # a candy-striped cap with a pom
        stripes = "".join(f'<path d="M{40 + i * 6},33 C{44 + i * 6},20 {48 + i * 6},16 {50 + i * 6},15" stroke="{t}" stroke-width="2.6" fill="none"/>' for i in range(5))
        return (f'<path d="M40,34 C38,14 82,14 80,34 Z" fill="#fff6f0"/>{stripes}'
                f'<rect x="38" y="31" width="44" height="5" rx="2.5" fill="{t}"/><circle cx="60" cy="13" r="4.5" fill="#fff6f0" stroke="{t}" stroke-width="1.6"/>')
    if kind == "bandana":     # a polka-dot bandana knotted at the side
        dots = "".join(f'<circle cx="{x}" cy="{y}" r="1.6" fill="#fff"/>' for x, y in ((48, 24), (56, 20), (64, 20), (72, 24), (52, 30), (68, 30), (60, 26)))
        return (f'<path d="M40,34 C38,16 82,16 80,34 Z" fill="{t}"/>{dots}'
                f'<path d="M80,30 L90,26 L88,34 Z M80,32 L90,38 L84,40 Z" fill="{mix(t, 0.85)}"/>')
    if kind == "beret":       # a soft beret, tilted
        return (f'<ellipse cx="62" cy="24" rx="25" ry="10" fill="{t}" transform="rotate(-8 62 24)"/>'
                f'<rect x="58" y="12" width="3" height="6" rx="1.5" fill="{mix(t, 0.7)}"/>'
                f'<path d="M40,30 C50,34 70,34 82,26" fill="none" stroke="{mix(t, 0.75)}" stroke-width="2"/>')
    if kind == "sailor":      # a white sailor cap with a blue band
        return ('<path d="M40,32 C40,18 80,18 80,32 Z" fill="#fbfdff" stroke="#d4dbe6" stroke-width="1"/>'
                f'<rect x="39" y="27" width="42" height="6" rx="3" fill="{t}"/><path d="M78,30 L88,36 L86,40 Z" fill="{t}"/>')
    if kind == "conductor":   # a peaked cap with a gold band and badge
        return (f'<path d="M41,30 C41,16 79,16 79,30 Z" fill="#3b2f4a"/><rect x="40" y="25" width="40" height="6" rx="2" fill="#d6a630"/>'
                '<path d="M40,31 C50,38 72,38 82,31 Z" fill="#241b30"/><circle cx="60" cy="21" r="3.2" fill="#ffd76a" stroke="#b0841c"/>')
    if kind == "hardhat":     # a yellow hard hat, it's a nut-cracking job
        return ('<path d="M40,32 C40,12 80,12 80,32 Z" fill="#ffcf3a"/><rect x="36" y="29" width="48" height="5" rx="2.5" fill="#e3ad16"/>'
                '<path d="M60,14 L60,30" stroke="#e3ad16" stroke-width="3"/><path d="M48,20 C52,16 56,15 58,15" stroke="#fff3b0" stroke-width="2" fill="none"/>')
    if kind == "bowler":      # a round bowler with a candy flower
        return ('<ellipse cx="60" cy="31" rx="25" ry="4" fill="#2c2430"/><path d="M45,31 C45,12 75,12 75,31 Z" fill="#3a3040"/>'
                f'<rect x="45" y="25" width="30" height="4" fill="{t}"/><circle cx="72" cy="24" r="3.2" fill="#ffd76a"/><circle cx="72" cy="24" r="1.2" fill="#ff7ac8"/>')
    return ""


def face(c, mouth="smile", eyes="open"):
    s, hcol = c["skin"], c["hair"]
    out = [f'<ellipse cx="41" cy="44" rx="3.5" ry="5" fill="{mix(s, 0.88)}"/><ellipse cx="79" cy="44" rx="3.5" ry="5" fill="{mix(s, 0.88)}"/>',
           '<circle cx="60" cy="42" r="19" fill="url(#skin)"/>',
           f'<path d="M41,38 C42,28 52,24 60,24 C68,24 78,28 79,38 C72,32 66,31 60,31 C54,31 48,32 41,38 Z" fill="{hcol}"/>',
           '<ellipse cx="49" cy="49" rx="4.5" ry="3" fill="#ff7a7a" opacity="0.35"/><ellipse cx="71" cy="49" rx="4.5" ry="3" fill="#ff7a7a" opacity="0.35"/>']
    for x in (52, 68):
        if eyes == "open":
            out.append(f'<ellipse cx="{x}" cy="43" rx="3" ry="3.6" fill="#2a1a14"/><circle cx="{x + 1}" cy="41.8" r="1.1" fill="#fff"/>')
        elif eyes == "happy":
            out.append(f'<path d="M{x - 3},44 Q{x},40 {x + 3},44" fill="none" stroke="#2a1a14" stroke-width="1.8" stroke-linecap="round"/>')
        out.append(f'<path d="M{x - 3.5},37.5 Q{x},36 {x + 3.5},37.5" fill="none" stroke="{mix(hcol, 0.9)}" stroke-width="1.6" stroke-linecap="round"/>')
    out.append(f'<path d="M60,45 Q58.5,48.5 61,49" fill="none" stroke="{mix(s, 0.7)}" stroke-width="1.3" stroke-linecap="round"/>')
    if mouth == "smile":
        out.append('<path d="M54,52 Q60,57 66,52" fill="none" stroke="#7a3226" stroke-width="2" stroke-linecap="round"/>')
    elif mouth == "open":
        out.append('<path d="M54,51 Q60,59 66,51 Z" fill="#7a3226"/><path d="M57,55 Q60,57 63,55" fill="#ff8a8a"/>')
    elif mouth == "o":
        out.append('<ellipse cx="60" cy="53" rx="3" ry="3.5" fill="#7a3226"/>')
    elif mouth == "blow":
        out.append('<circle cx="61" cy="53" r="2" fill="#7a3226"/>')
    return "".join(out)


def figure(job, pose, behind="", front=""):
    """A whole worker: legs, boots, overalls, arms, head, hat, plus props behind and in front."""
    c = CREW[job]
    d = (lin("skin", mix(c["skin"], 1.1), mix(c["skin"], 0.86), 0.2, 0, 0.8, 1)
         + lin("outfit", mix(c["outfit"], 1.1), mix(c["outfit"], 0.85))
         + lin("pants", mix(c["pants"], 1.15), mix(c["pants"], 0.8)))
    sleeve = mix(c["outfit"], 0.92)
    b = ['<ellipse cx="60" cy="152" rx="26" ry="4.5" fill="#000" opacity="0.28"/>', behind]
    # legs and boots
    b.append('<rect x="47" y="98" width="12" height="44" rx="5" fill="url(#pants)"/><rect x="61" y="98" width="12" height="44" rx="5" fill="url(#pants)"/>')
    b.append('<path d="M44,140 C44,135 58,135 59,140 L59,148 L42,148 C40,148 40,142 44,140 Z" fill="#3d2618"/>'
             '<path d="M76,140 C76,135 62,135 61,140 L61,148 L78,148 C80,148 80,142 76,140 Z" fill="#3d2618"/>'
             '<rect x="42" y="146" width="17" height="3" rx="1.5" fill="#24160e"/><rect x="61" y="146" width="17" height="3" rx="1.5" fill="#24160e"/>')
    # body: overalls with a bib, straps, a pocket and a candy patch
    b.append('<path d="M45,66 C45,60 75,60 75,66 L77,102 C77,106 43,106 43,102 Z" fill="url(#outfit)"/>')
    b.append(f'<path d="M48,64 C52,62 68,62 72,64 L70,74 L50,74 Z" fill="{mix(c["outfit"], 1.2)}"/>')
    b.append(f'<rect x="50" y="74" width="20" height="18" rx="3" fill="{mix(c["outfit"], 1.28)}" stroke="{c["trim"]}" stroke-width="1.2"/>')
    b.append(f'<path d="M50,74 L47,63 M70,74 L73,63" stroke="{c["trim"]}" stroke-width="2.4" stroke-linecap="round"/>'
             f'<circle cx="51" cy="76" r="1.7" fill="{c["trim"]}"/><circle cx="69" cy="76" r="1.7" fill="{c["trim"]}"/>')
    b.append(f'<path d="M54,80 C54,77 66,77 66,80 L66,86 L54,86 Z" fill="none" stroke="{c["trim"]}" stroke-width="1"/>')
    b.append(f'<circle cx="60" cy="83" r="2.6" fill="#fff"/><path d="M57.4,83 L62.6,83 M60,80.4 L60,85.6" stroke="{c["trim"]}" stroke-width="1.1"/>')
    b.append(f'<rect x="43" y="96" width="34" height="5" rx="2" fill="{mix(c["pants"], 0.9)}"/><rect x="58" y="96" width="5" height="5" rx="1" fill="#e8c46a"/>')
    # arms
    b.append(arm(SH_L, pose.get("l", (40, 98)), sleeve, c["skin"], pose.get("lb", 1)))
    b.append(arm(SH_R, pose.get("r", (80, 98)), sleeve, c["skin"], pose.get("rb", -1)))
    # neck, head, hat
    b.append(f'<rect x="55" y="56" width="10" height="8" rx="3" fill="{mix(c["skin"], 0.84)}"/>')
    b.append(face(c, pose.get("mouth", "smile"), pose.get("eyes", "open")))
    b.append(hat(c["hat"], c))
    b.append(front)
    return d, "".join(b)


# ── props and poses per job ───────────────────────────────────────────────────
def pot(x=92, y=118):
    return (f'<path d="M{x - 18},{y} L{x + 18},{y} L{x + 15},{y + 26} C{x + 14},{y + 30} {x - 14},{y + 30} {x - 15},{y + 26} Z" fill="#b8763e"/>'
            f'<ellipse cx="{x}" cy="{y}" rx="18" ry="4.5" fill="#5a3218"/><ellipse cx="{x}" cy="{y}" rx="15" ry="3" fill="#7a4626"/>'
            f'<path d="M{x - 16},{y + 8} L{x + 16},{y + 8}" stroke="#d8955a" stroke-width="1.5"/>')


def poses(job):
    """{rest|work|blocked: (pose, behind, front)} and the fx layer."""
    gold = "#ffd76a"
    up = dict(r=(84, 24), rb=1, mouth="open")   # a raised hand: needs you
    if job == "stirrer":
        rest = (dict(r=(84, 104)), pot(), '<path d="M86,72 L98,118" stroke="#a8743a" stroke-width="4" stroke-linecap="round"/>')
        work = (dict(l=(78, 92), r=(86, 86), lb=-1, eyes="happy"), pot(), '<path d="M80,80 L96,120" stroke="#a8743a" stroke-width="4.5" stroke-linecap="round"/>')
        fx = ("top", '<circle cx="86" cy="112" r="3" fill="#8a5230"/><circle cx="96" cy="108" r="2.2" fill="#8a5230"/><circle cx="92" cy="104" r="1.6" fill="#a8683e"/>'
                     '<path d="M84,100 C80,92 88,88 84,80 M98,98 C94,90 102,86 98,78" fill="none" stroke="#fff" stroke-width="1.8" opacity="0.55" stroke-linecap="round"/>')
        return dict(rest=rest, work=work, blocked=(up, pot(), "")), fx
    if job == "taster":
        bowl = '<path d="M24,96 C24,108 44,108 44,96 Z" fill="#fff8ee" stroke="#e0d2bc"/><ellipse cx="34" cy="96" rx="10" ry="2.6" fill="#6a3a1e"/>'
        rest = (dict(l=(34, 98)), "", bowl + '<path d="M80,98 L90,90" stroke="#c8cdd4" stroke-width="2.4" stroke-linecap="round"/><ellipse cx="91" cy="89" rx="3" ry="2" fill="#c8cdd4"/>')
        work = (dict(l=(34, 98), r=(68, 56), rb=-1, mouth="open", eyes="happy"), "", bowl + '<path d="M70,58 L64,52" stroke="#c8cdd4" stroke-width="2.4" stroke-linecap="round"/><ellipse cx="62" cy="51" rx="3.2" ry="2.2" fill="#6a3a1e"/>')
        fx = ("opacity", '<path d="M86,22 C86,18 92,18 92,22 C92,18 98,18 98,22 C98,27 92,30 92,32 C92,30 86,27 86,22 Z" fill="#ff6fa8"/>'
                         '<path d="M100,36 L102,40 L106,41 L102,43 L100,47 L98,43 L94,41 L98,40 Z" fill="#ffd76a"/>')
        return dict(rest=rest, work=work, blocked=(dict(up, l=(34, 98)), "", bowl)), fx
    if job == "taffy":
        rest = (dict(r=(82, 100)), "", '<circle cx="86" cy="100" r="6" fill="#ff8fc6"/><path d="M82,98 C86,94 90,98 88,102" stroke="#ffd0e6" stroke-width="1.6" fill="none"/>')
        work = (dict(l=(22, 84), r=(98, 84), lb=-1, rb=1, eyes="happy"), "",
                '<path d="M22,84 C40,100 80,100 98,84" fill="none" stroke="#ff8fc6" stroke-width="6" stroke-linecap="round"/>'
                '<path d="M24,82 C42,96 78,96 96,82" fill="none" stroke="#ffd0e6" stroke-width="2" stroke-linecap="round"/>')
        fx = ("opacity", '<path d="M60,104 L62,108 L66,109 L62,111 L60,115 L58,111 L54,109 L58,108 Z" fill="#fff"/><circle cx="40" cy="104" r="1.6" fill="#ffd76a"/><circle cx="82" cy="106" r="1.6" fill="#ffd76a"/>')
        return dict(rest=rest, work=work, blocked=(up, "", "")), fx
    if job == "bubble":
        rest = (dict(r=(82, 98)), "", '<rect x="78" y="94" width="10" height="6" rx="1.5" fill="#ff8fc6"/><rect x="78" y="96" width="10" height="2" fill="#fff"/>')
        work = (dict(mouth="blow", r=(80, 96)), "", "")
        fx = ("top", '<circle cx="72" cy="50" r="15" fill="#ff8fc6" opacity="0.92"/><circle cx="66" cy="44" r="4" fill="#fff" opacity="0.7"/>'
                     '<circle cx="72" cy="50" r="15" fill="none" stroke="#e05a9e" stroke-width="1.2"/>')
        return dict(rest=rest, work=work, blocked=(up, "", "")), fx
    if job == "rower":
        waves = '<path d="M0,146 C10,140 20,152 30,146 C40,140 50,152 60,146 C70,140 80,152 90,146 C100,140 110,152 120,146 L120,160 L0,160 Z" fill="#6a3a1e" opacity="0.9"/>'
        oar = '<path d="M30,70 L96,140" stroke="#b07a3e" stroke-width="3.5" stroke-linecap="round"/><ellipse cx="98" cy="142" rx="5" ry="9" fill="#9a6430" transform="rotate(-42 98 142)"/>'
        rest = (dict(l=(48, 86), r=(64, 92)), waves, oar)
        work = (dict(l=(40, 80), r=(58, 90), lb=-1), waves, oar.replace("M30,70", "M22,62"))
        fx = ("left", '<path d="M-20,150 C-10,144 0,156 10,150 C20,144 30,156 40,150 C50,144 60,156 70,150 C80,144 90,156 100,150 C110,144 120,156 130,150 C140,144 150,156 160,150" fill="none" stroke="#c48a5a" stroke-width="2" opacity="0.8"/>')
        return dict(rest=rest, work=work, blocked=(up, waves, "")), fx
    if job == "ticket":
        tk = lambda x, y, r=0: (f'<g transform="rotate({r} {x} {y})"><rect x="{x - 14}" y="{y - 8}" width="28" height="16" rx="2" fill="{gold}" stroke="#c99520" stroke-width="1.2"/>'
                                f'<rect x="{x - 10}" y="{y - 4}" width="20" height="8" rx="1" fill="none" stroke="#c99520"/><path d="M{x - 7},{y} L{x + 7},{y}" stroke="#8a5a10" stroke-width="1.4"/></g>')
        rest = (dict(r=(82, 98)), "", tk(88, 100, -10))
        work = (dict(r=(86, 30), rb=1, mouth="open", eyes="happy"), "", tk(90, 22, 12))
        fx = ("opacity", "".join(f'<path d="M{x},{y - 4} L{x + 1.2},{y - 1.2} L{x + 4},{y} L{x + 1.2},{y + 1.2} L{x},{y + 4} L{x - 1.2},{y + 1.2} L{x - 4},{y} L{x - 1.2},{y - 1.2} Z" fill="#fff6c8"/>'
                                 for x, y in ((72, 12), (108, 18), (104, 38), (76, 34))))
        return dict(rest=rest, work=work, blocked=(dict(up, r=(84, 24)), "", "")), fx
    if job == "cracker":
        block = '<rect x="80" y="126" width="30" height="20" rx="2" fill="#8a5a34"/><rect x="80" y="124" width="30" height="4" rx="1" fill="#a8743e"/>'
        nut = '<ellipse cx="95" cy="119" rx="6" ry="5" fill="#b8844a" stroke="#7a5228"/><path d="M95,115 C93,118 97,120 95,123" stroke="#7a5228" fill="none"/>'
        mallet = lambda x, y: f'<path d="M78,86 L{x},{y}" stroke="#a8743a" stroke-width="3.5" stroke-linecap="round"/><rect x="{x - 7}" y="{y - 5}" width="14" height="10" rx="2" fill="#8c939c" stroke="#5c636c"/>'
        rest = (dict(r=(80, 98)), block + nut, '<path d="M82,98 L84,124" stroke="#a8743a" stroke-width="3.5" stroke-linecap="round"/><rect x="78" y="120" width="12" height="9" rx="2" fill="#8c939c"/>')
        work = (dict(r=(80, 70), rb=1, eyes="happy"), block + nut, mallet(98, 52))
        fx = ("opacity", '<path d="M88,112 L84,106 M102,112 L106,106 M95,108 L95,102" stroke="#ffd76a" stroke-width="2" stroke-linecap="round"/>'
                         '<path d="M86,118 L82,116 M104,118 L108,116" stroke="#c48a52" stroke-width="2.4" stroke-linecap="round"/>')
        return dict(rest=rest, work=work, blocked=(up, block + nut, "")), fx
    if job == "singer":
        rest = (dict(), "", "")
        work = (dict(l=(28, 70), r=(92, 70), lb=-1, rb=1, mouth="open", eyes="happy"), "", "")
        note = lambda x, y, col: (f'<g fill="{col}"><ellipse cx="{x}" cy="{y + 12}" rx="4.4" ry="3.2"/><rect x="{x + 3}" y="{y}" width="1.8" height="12"/>'
                                  f'<path d="M{x + 4.8},{y} Q{x + 11},{y + 3} {x + 8},{y + 8}" fill="none" stroke="{col}" stroke-width="1.8"/></g>')
        fx = ("top", note(88, 18, gold) + note(100, 40, "#ff8fc6") + note(18, 28, "#5fd4c4"))
        return dict(rest=rest, work=work, blocked=(up, "", "")), fx
    raise ValueError(job)


def alert():
    return wrap('<g><path d="M86,6 C76,6 72,12 72,20 C72,28 78,33 86,33 L88,33 L92,40 L94,33 C102,32 106,27 106,20 C106,12 100,6 90,6 Z" fill="#ff5a8a" stroke="#fff" stroke-width="2"/>'
                '<rect x="87.3" y="11" width="4" height="12" rx="2" fill="#fff"/><circle cx="89.3" cy="27.5" r="2.3" fill="#fff"/></g>')


def badge(job):
    """The tab bar's round face: the head and hat on a candy-coloured disc."""
    c = CREW[job]
    d, body = figure(job, dict())
    disc = f'<circle cx="60" cy="40" r="31" fill="{c["tile"]}"/><circle cx="60" cy="40" r="27" fill="{mix(c["tile"], 0.62)}"/>'
    clip = '<clipPath id="disc"><circle cx="60" cy="40" r="31"/></clipPath>'
    return wrap(f'{disc}<g clip-path="url(#disc)">{body}</g><circle cx="60" cy="40" r="31" fill="none" stroke="#2a1910" stroke-width="2"/>',
                d + clip, vb="29 9 62 62", w=72, h=72)


os.makedirs(OUT, exist_ok=True)
for job in CREW:
    ps, (prop, fxsvg) = poses(job)
    for name, (pose, behind, front) in ps.items():
        d, body = figure(job, pose, behind, front)
        open(f"{OUT}/{job}-{name}.svg", "w").write(wrap(body, d))
    open(f"{OUT}/{job}-fx.svg", "w").write(wrap(fxsvg))
    open(f"{OUT}/{job}-face.svg", "w").write(badge(job))
open(f"{OUT}/alert.svg", "w").write(alert())
FXPROP = {job: poses(job)[1][0] for job in CREW}
print(FXPROP)
