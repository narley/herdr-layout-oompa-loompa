#!/usr/bin/env python3
"""Reference-inspired Oompa Loompa SVGs for Herdr's eight factory jobs."""
from pathlib import Path

OUT = Path(__file__).parent / "crew"
JOBS = ("stirrer", "taster", "taffy", "bubble", "rower", "ticket", "cracker", "singer")
SKINS = ("#ad6333", "#b96e39", "#a95c31", "#ba7141", "#ae6838", "#bf7643", "#a45b30", "#b66c38")
HAIRS = ("#344b19", "#40571e", "#38501d", "#4b6025", "#364b1b", "#40571c", "#30471a", "#496023")
HAIRLINES = (
    "M43 27Q41 10 56 9q15-8 22 15-11-5-18-4-17 7-17 7z",
    "M43 29Q38 11 59 10q21 0 19 19-8-9-18-8-7 8-17 8z",
    "M42 31Q39 12 55 8q17-5 23 16-13-4-20 1-8-2-16 6z",
    "M43 29Q43 7 59 9q20-3 20 20-10-8-19-8-10 0-17 8z",
    "M43 27Q42 13 56 10q16-5 22 15-9-6-18-4-9 5-17 6z",
    "M43 29Q39 15 53 9q18-7 25 16-13-7-20-3-8 3-15 7z",
    "M43 29Q41 10 59 9q18-1 19 20-6-10-16-10-12 8-19 10z",
    "M43 28Q41 11 58 8q20-3 20 19-10-5-18-5-9-2-17 6z",
)
ACCENTS = ("#d69342", "#80bfb5", "#e497ba", "#ec91ad", "#87aaca", "#d1aa40", "#b78a5c", "#b785b6")
HEADWEAR = (
    '<path d="M45 18q-8-12 3-16 7-7 13 0 11-7 15 4 5 8-3 12z" fill="#f9f9f4" stroke="#cbd1c9"/><path d="M45 18h30v6H45z" fill="#f7f7f2"/>',
    '<path d="M46 17q14-13 28 0" fill="none" stroke="#d8dfd9" stroke-width="5"/><circle cx="76" cy="37" r="6" fill="none" stroke="#d6bb5e" stroke-width="2.5"/>',
    '<path d="M43 19q15-18 34 0v7H43z" fill="#e497ba"/><path d="M47 16l5 5m4-9 5 9m4-9 5 9" stroke="#fff" stroke-width="2"/>',
    '<path d="M41 19q19-17 38 0l-2 7H43z" fill="#ec91ad"/><circle cx="60" cy="16" r="4" fill="#fff7f8"/>',
    '<path d="M42 20q18-14 36 0v7H42z" fill="#eff7f8" stroke="#87aaca" stroke-width="2"/><path d="M76 23l10 5-10 1" fill="#eff7f8"/>',
    '<path d="M45 14q15-9 30 0v12H45z" fill="#57422e"/><rect x="44" y="20" width="32" height="5" fill="#d1aa40"/><path d="M42 26q18 8 36 0" fill="#57422e"/>',
    '<path d="M42 21q4-16 18-16t18 16z" fill="#e9bc57"/><rect x="39" y="19" width="42" height="5" rx="2" fill="#c69236"/>',
    '<path d="M45 19q15-15 30 0v7H45z" fill="#b785b6"/><path d="M43 27q17 5 34 0" fill="none" stroke="#e4c9e1" stroke-width="3"/>',
)
PROPS = (
    '<path d="M92 66l13 69" stroke="#b88852" stroke-width="5" stroke-linecap="round"/><ellipse cx="106" cy="136" rx="8" ry="4" fill="#c1c6bd"/>',
    '<path d="M86 88h21l-4 17H90z" fill="#f8f8f2" stroke="#94aaa2" stroke-width="2"/><path d="M107 91q9 0 3 10h-5" fill="none" stroke="#f8f8f2" stroke-width="3"/>',
    '<path d="M83 100q15-17 29-1" fill="none" stroke="#e497ba" stroke-width="7" stroke-linecap="round"/><path d="M83 100q15-17 29-1" fill="none" stroke="#f9d4e6" stroke-width="2"/>',
    '<circle cx="95" cy="85" r="14" fill="#ee9abc" stroke="#fbdaea" stroke-width="2"/><circle cx="90" cy="80" r="4" fill="#fff" opacity=".6"/>',
    '<path d="M89 65l23 74" stroke="#aa7647" stroke-width="5"/><ellipse cx="113" cy="141" rx="6" ry="12" fill="#aa7647" transform="rotate(-18 113 141)"/>',
    '<path d="M83 90h31v20H83z" fill="#e6bb55" stroke="#946c23" stroke-width="2"/><path d="M89 95h19m-19 5h14" stroke="#946c23" stroke-width="2"/>',
    '<path d="M88 84l16 43" stroke="#a87b50" stroke-width="5"/><rect x="99" y="121" width="17" height="13" rx="2" fill="#888b85" stroke="#4d504e" stroke-width="2"/>',
    '<path d="M94 80v36" stroke="#b785b6" stroke-width="3"/><circle cx="94" cy="74" r="7" fill="#b785b6"/><path d="M104 70v14m0-14q12 1 5 9" fill="none" stroke="#b785b6" stroke-width="3"/><circle cx="101" cy="86" r="4" fill="#b785b6"/>',
)


def svg(body, view="0 0 120 160", size=(120, 160)):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{view}" width="{size[0]}" height="{size[1]}">{body}</svg>\n'


def person(index, state):
    skin, hair = SKINS[index], HAIRS[index]
    raised = state == "work" or state == "blocked"
    left_up = raised and index % 2 == 0
    right_up = raised and index % 2 == 1
    resting_hands = (((29, 92), (91, 92)), ((34, 101), (87, 82)), ((24, 86), (96, 86)),
                     ((34, 103), (86, 103)), ((31, 94), (84, 75)), ((25, 86), (95, 95)),
                     ((31, 105), (88, 91)), ((24, 85), (96, 85)))
    left_hand = (18, 35) if left_up else resting_hands[index][0]
    right_hand = (102, 35) if right_up else resting_hands[index][1]
    if state == "work" and index in (2, 7):
        left_hand, right_hand = (18, 35), (102, 35)
    body = ['<ellipse cx="60" cy="154" rx="30" ry="3" fill="#1d1513" opacity=".25"/>']
    for leg_x in (47, 66):
        body.append(f'<path d="M{leg_x} 120v21" stroke="#eee6dc" stroke-width="11"/>')
        for offset in (2, 7, 12, 17):
            body.append(f'<path d="M{leg_x-5} {121+offset}h10" stroke="#342520" stroke-width="2.7"/>')
        body.append(f'<path d="M{leg_x-6} 140q-5 4-4 10h17q5-4 0-7l-3-3z" fill="#3b2720"/><path d="M{leg_x+2} 143q7 0 5 6-2 4-6 1" fill="none" stroke="#3b2720" stroke-width="3"/>')
    body.append('<path d="M38 84q22-8 44 0l8 26q-5 17-20 17l-10-7-10 7q-15 0-20-17z" fill="#f7f8f4" stroke="#d6dbd8" stroke-width="1.2"/>')
    body.append('<path d="M34 101q3-11 12-7l11 22-8 11q-12-1-16-10z M86 101q-3-11-12-7l-11 22 8 11q12-1 16-10z" fill="#f1f4f1"/>')
    body.append('<path d="M43 61q17-9 34 0l5 30H38z" fill="#70412e" stroke="#4e2b21" stroke-width="1.1"/>')
    for shoulder_x, hand in ((43, left_hand), (77, right_hand)):
        body.append(f'<path d="M{shoulder_x} 65 Q{hand[0]} 62 {hand[0]} {hand[1]-3}" fill="none" stroke="#70412e" stroke-width="11" stroke-linecap="round"/>')
        body.append(f'<path d="M{hand[0]} {hand[1]-10}v8" stroke="#eee" stroke-width="5"/>')
        body.append(f'<ellipse cx="{hand[0]}" cy="{hand[1]}" rx="5.5" ry="7" fill="#f9faf7" stroke="#d8dbd7"/>')
        body.append(f'<path d="M{hand[0]-4} {hand[1]-1}l-5-2" stroke="#f9faf7" stroke-width="3" stroke-linecap="round"/>')
    body.append(f'<rect x="55" y="50" width="10" height="12" rx="3" fill="{skin}"/>')
    body.append('<path d="M46 60l14 23 14-23 M45 63l13 21 M75 63L62 84" fill="none" stroke="#fbfbf9" stroke-width="7"/>')
    body.append('<path d="M41 83q19-5 38 0v29q-19 8-38 0z" fill="#f8faf8"/>')
    body.append('<circle cx="51" cy="85" r="2.3" fill="#34302b"/><circle cx="69" cy="85" r="2.3" fill="#34302b"/>')
    body.append(f'<path d="M43 94h34v6H43z" fill="{ACCENTS[index]}"/>')
    adornments = (
        '<path d="M55 105q5-3 10 0" fill="none" stroke="#d0d3cd"/>',
        '<circle cx="60" cy="103" r="3" fill="#bd8a34"/>',
        '<path d="M50 106h20" stroke="#d0d3cd" stroke-width="2"/>',
        '<path d="M54 102l6 6 6-6" fill="none" stroke="#c9cfc9"/>',
        '<circle cx="51" cy="105" r="2" fill="#b2aa7a"/>',
        '<path d="M57 101h6v7h-6z" fill="#e5e8e2" stroke="#babeb6"/>',
        '<path d="M48 106q12 6 24 0" fill="none" stroke="#cdd0c9"/>',
        '<circle cx="60" cy="104" r="2.5" fill="#c7a14a"/>',
    )
    body.append(adornments[index])
    for neck_x in (52, 57, 63, 68):
        body.append(f'<path d="M{neck_x} 53v7" stroke="#f6f5f0" stroke-width="2.5"/>')
    face_widths = (18, 16, 19, 17, 18, 16, 20, 17)
    body.append(f'<ellipse cx="60" cy="34" rx="{face_widths[index]}" ry="23" fill="{skin}" stroke="#895027" stroke-width=".8"/>')
    body.append(f'<path d="{HAIRLINES[index]}" fill="{hair}"/>')
    side_width = (8, 6, 10, 7, 9, 6, 10, 7)[index]
    body.append(f'<path d="M44 28q-8 1-7 12 0 8 8 8 M76 28q8 1 7 12 0 8-8 8" fill="none" stroke="{hair}" stroke-width="{side_width}" stroke-linecap="round"/>')
    tufts = ("M55 9q3-8 7-4l2 7", "M65 10q4-7 7-3", "M49 14q-5-5-2-8", "M60 10q-1-10 4-7", "M54 11q-2-7-6-7", "M68 11q5-8 7-5", "M60 10q-4-10-8-6", "M63 9q2-8 7-6")
    body.append(f'<path d="{tufts[index]}" fill="none" stroke="{hair}" stroke-width="5" stroke-linecap="round"/>')
    body.append(HEADWEAR[index])
    eye_y = 33 + index % 2
    for eye_x in (53, 67):
        body.append(f'<ellipse cx="{eye_x}" cy="{eye_y}" rx="2.3" ry="2.8" fill="#f4eee5"/><circle cx="{eye_x}" cy="{eye_y}" r="1.3" fill="#35271e"/>')
    body.append('<path d="M60 36l-2 7 3 1" fill="none" stroke="#794627" stroke-width="1"/>')
    brows = ("M49 27q4-2 8 0 M63 27q4-2 8 0", "M49 28h8 M63 28h8", "M48 27q4 1 8 0 M64 27q4 1 8 0", "M49 27q4-3 8-1 M63 26q4-2 8 1")
    body.append(f'<path d="{brows[index % 4]}" fill="none" stroke="#453020" stroke-width="1.5"/>')
    mouth = 'M53 48q7 5 14 0' if index % 3 else 'M54 48q6 2 12 0'
    body.append(f'<path d="{mouth}" fill="none" stroke="#632f23" stroke-width="1.6" stroke-linecap="round"/>')
    body.append(PROPS[index])
    if state == "blocked":
        body.append('<path d="M91 8h16v17H91z" fill="#f3d7a5"/><path d="M99 11v8m0 3v1" stroke="#7c3328" stroke-width="2"/>')
    return "".join(body)


OUT.mkdir(exist_ok=True)
for index, job in enumerate(JOBS):
    for state in ("rest", "work", "blocked"):
        (OUT / f"{job}-{state}-classic-v3.svg").write_text(svg(person(index, state)))
    (OUT / f"{job}-face-classic-v3.svg").write_text(svg(person(index, "rest"), "38 8 44 51", (72, 72)))
