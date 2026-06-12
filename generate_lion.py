#!/usr/bin/env python3
"""
generate_lion.py
Generates an animated lion SVG that walks across the GitHub contribution grid.
The lion leaves a glowing trail of gold as it walks over the cells.
"""

import os, json, math, random
from datetime import datetime, timedelta

# ── CONFIG ──────────────────────────────────────────────────────────────────
COLS       = 53   # weeks in a year
ROWS       = 7    # days per week
CELL       = 12   # px per cell
GAP        = 3    # px between cells
PAD_X      = 64   # left padding (for day labels)
PAD_Y      = 32   # top padding (for month labels)
W = PAD_X + COLS * (CELL + GAP) + 40
H = PAD_Y + ROWS * (CELL + GAP) + 120   # extra for lion

BG         = "#0d1117"
CELL_EMPTY = "#161b22"
GOLD_DARK  = "#b45309"
GOLD_MID   = "#d97706"
GOLD_LIGHT = "#fbbf24"
GOLD_GLOW  = "#fef08a"
LION_COLOR = "#f59e0b"
MANE_COLOR = "#92400e"
WHITE      = "#ffffff"
GRAY       = "#8b949e"

DAYS   = ["Mon","","Wed","","Fri","",""]
MONTHS = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

TOTAL_STEPS = COLS   # one step per column
STEP_MS     = 80     # ms between steps → total animation ~4.2 seconds

def level_color(level):
    return [CELL_EMPTY, GOLD_DARK, GOLD_MID, GOLD_LIGHT, GOLD_GLOW][level]

def make_grid():
    """Generate a realistic-looking contribution grid."""
    random.seed(42)
    grid = []
    for col in range(COLS):
        col_data = []
        # Higher activity in recent months
        base = 0.25 + 0.3 * (col / COLS)
        for row in range(ROWS):
            if row in [5, 6]:  # weekends less active
                base_r = base * 0.4
            else:
                base_r = base
            # activity bursts
            if 38 <= col <= 45:
                base_r *= 2.2
            r = random.random()
            if r < base_r * 0.1:
                lvl = 4
            elif r < base_r * 0.3:
                lvl = 3
            elif r < base_r * 0.6:
                lvl = 2
            elif r < base_r:
                lvl = 1
            else:
                lvl = 0
            col_data.append(lvl)
        grid.append(col_data)
    return grid

def cell_x(col): return PAD_X + col * (CELL + GAP)
def cell_y(row): return PAD_Y + row * (CELL + GAP)

def lion_svg(cx, cy, step, total):
    """Returns SVG for a walking lion at position (cx, cy)."""
    progress = step / total
    # Walking cycle — body bob
    bob = math.sin(step * 1.2) * 2
    leg_swing = math.sin(step * 1.2)

    # Body
    parts = []

    # Shadow
    parts.append(f'<ellipse cx="{cx}" cy="{cy+22+bob:.1f}" rx="22" ry="5" fill="#000" opacity="0.3"/>')

    # Tail
    tail_wave = math.sin(step * 0.8) * 12
    tail_path = (f'M {cx-20} {cy+8+bob:.1f} '
                 f'Q {cx-36} {cy+tail_wave:.1f} '
                 f'{cx-40} {cy-10+tail_wave*0.5:.1f}')
    parts.append(f'<path d="{tail_path}" stroke="{LION_COLOR}" stroke-width="3.5" fill="none" stroke-linecap="round"/>')
    # Tail tuft
    parts.append(f'<ellipse cx="{cx-40}" cy="{cy-12+tail_wave*0.5:.1f}" rx="5" ry="6" fill="{MANE_COLOR}"/>')

    # Legs (back)
    for dx, dy, phase in [(-10,16,0.0), (-4,16,math.pi)]:
        swing = leg_swing * 6 * math.cos(phase)
        parts.append(
            f'<line x1="{cx+dx}" y1="{cy+bob:.1f}" '
            f'x2="{cx+dx+swing:.1f}" y2="{cy+dy+bob:.1f}" '
            f'stroke="{LION_COLOR}" stroke-width="5" stroke-linecap="round"/>'
        )
    # Legs (front)
    for dx, dy, phase in [(6,16,math.pi*0.5), (12,16,math.pi*1.5)]:
        swing = leg_swing * 6 * math.cos(phase)
        parts.append(
            f'<line x1="{cx+dx}" y1="{cy+bob:.1f}" '
            f'x2="{cx+dx+swing:.1f}" y2="{cy+dy+bob:.1f}" '
            f'stroke="{LION_COLOR}" stroke-width="5" stroke-linecap="round"/>'
        )

    # Body
    parts.append(
        f'<ellipse cx="{cx}" cy="{cy+bob:.1f}" rx="20" ry="12" fill="{LION_COLOR}"/>'
    )

    # Mane (back of circle)
    mane_r = 13 + math.sin(step * 0.5) * 0.8
    parts.append(
        f'<circle cx="{cx+16}" cy="{cy-4+bob:.1f}" r="{mane_r:.1f}" fill="{MANE_COLOR}" opacity="0.9"/>'
    )

    # Head
    parts.append(
        f'<circle cx="{cx+18}" cy="{cy-4+bob:.1f}" r="10" fill="{LION_COLOR}"/>'
    )

    # Ear left
    parts.append(
        f'<polygon points="{cx+12},{cy-12+bob:.1f} {cx+9},{cy-20+bob:.1f} {cx+16},{cy-14+bob:.1f}" fill="{LION_COLOR}"/>'
    )
    # Ear right
    parts.append(
        f'<polygon points="{cx+22},{cy-12+bob:.1f} {cx+25},{cy-20+bob:.1f} {cx+20},{cy-14+bob:.1f}" fill="{LION_COLOR}"/>'
    )

    # Eye
    blink = "" if step % 18 != 0 else f'transform="scale(1,0.1) translate(0,{(cy-5+bob)*9:.1f})"'
    parts.append(
        f'<circle cx="{cx+22}" cy="{cy-5+bob:.1f}" r="2" fill="{MANE_COLOR}" {blink}/>'
    )
    parts.append(
        f'<circle cx="{cx+23}" cy="{cy-6+bob:.1f}" r="0.7" fill="{WHITE}"/>'
    )

    # Nose
    parts.append(
        f'<ellipse cx="{cx+27}" cy="{cy-2+bob:.1f}" rx="2" ry="1.5" fill="{MANE_COLOR}"/>'
    )

    # Mouth
    parts.append(
        f'<path d="M{cx+25} {cy+0+bob:.1f} Q{cx+27} {cy+3+bob:.1f} {cx+29} {cy+0+bob:.1f}" '
        f'stroke="{MANE_COLOR}" stroke-width="1" fill="none"/>'
    )

    # Whiskers
    for wy, angle in [(-3, -0.3), (-1, 0.0), (1, 0.3)]:
        parts.append(
            f'<line x1="{cx+27}" y1="{cy+wy+bob:.1f}" '
            f'x2="{cx+38}" y2="{cy+wy+math.sin(angle)*3+bob:.1f}" '
            f'stroke="{GOLD_GLOW}" stroke-width="0.8" opacity="0.7"/>'
        )
        parts.append(
            f'<line x1="{cx+27}" y1="{cy+wy+bob:.1f}" '
            f'x2="{cx+16}" y2="{cy+wy+math.sin(angle)*3+bob:.1f}" '
            f'stroke="{GOLD_GLOW}" stroke-width="0.8" opacity="0.7"/>'
        )

    return "\n".join(parts)


def build_svg():
    grid = make_grid()

    lines = []
    lines.append(f'<svg xmlns="http://www.w3.org/2000/svg" '
                 f'viewBox="0 0 {W} {H}" width="{W}" height="{H}">')

    # Background
    lines.append(f'<rect width="{W}" height="{H}" rx="10" fill="{BG}"/>')

    # Title
    lines.append(f'<text x="{PAD_X}" y="18" font-family="monospace" font-size="11" fill="{GRAY}">contributions in the last year</text>')

    # Month labels
    for i, m in enumerate(MONTHS):
        x = PAD_X + int(i * COLS/12) * (CELL+GAP)
        lines.append(f'<text x="{x}" y="{PAD_Y-6}" font-family="monospace" font-size="9" fill="{GRAY}">{m}</text>')

    # Day labels
    for row, label in enumerate(DAYS):
        if label:
            y = PAD_Y + row * (CELL + GAP) + CELL - 2
            lines.append(f'<text x="{PAD_X-4}" y="{y}" text-anchor="end" font-family="monospace" font-size="9" fill="{GRAY}">{label}</text>')

    # ── GRID CELLS with per-column animation ─────────────────────────
    # Each column lights up gold when the lion walks over it, then dims to normal
    for col in range(COLS):
        for row in range(ROWS):
            x = cell_x(col)
            y = cell_y(row)
            base_fill = level_color(grid[col][row])

            # timing: lion reaches this column at step=col
            t_arrive  = col * STEP_MS
            t_peak    = t_arrive + STEP_MS * 0.5
            t_fade    = t_arrive + STEP_MS * 3
            total_ms  = TOTAL_STEPS * STEP_MS + 400
            begin     = f"{t_arrive}ms"

            cell_id = f"c{col}_{row}"
            if grid[col][row] == 0:
                glow_fill = GOLD_DARK
            else:
                glow_fill = GOLD_GLOW

            lines.append(
                f'<rect id="{cell_id}" x="{x}" y="{y}" width="{CELL}" height="{CELL}" '
                f'rx="2" fill="{base_fill}">'
                f'<animate attributeName="fill" '
                f'values="{base_fill};{glow_fill};{GOLD_MID};{base_fill}" '
                f'keyTimes="0;0.15;0.45;1" '
                f'dur="{total_ms}ms" begin="{begin}" '
                f'repeatCount="indefinite"/>'
                f'</rect>'
            )

    # ── LION ANIMATION ───────────────────────────────────────────────
    # Generate lion frames as separate <g> elements with visibility animation
    total_ms = TOTAL_STEPS * STEP_MS + 400
    lion_y   = PAD_Y + (ROWS * (CELL + GAP)) // 2 + 4  # vertically centred on grid

    for step in range(TOTAL_STEPS + 1):
        lx = cell_x(step) + 4
        t_start = step * STEP_MS
        t_end   = (step + 1) * STEP_MS

        # visibility keyTimes (hidden → visible → hidden)
        frac_start = t_start / total_ms
        frac_end   = min(t_end / total_ms, 1.0)

        kv = f"0;0;{frac_start:.4f};{frac_start:.4f};{frac_end:.4f};{frac_end:.4f};1"
        ka = "hidden;hidden;visible;visible;hidden;hidden;hidden"

        svg_lion = lion_svg(lx, lion_y, step, TOTAL_STEPS)

        lines.append(
            f'<g opacity="1">'
            f'<animate attributeName="visibility" '
            f'values="{ka}" keyTimes="{kv}" '
            f'dur="{total_ms}ms" repeatCount="indefinite"/>'
            f'{svg_lion}'
            f'</g>'
        )

    # ── GLOW TRAIL ───────────────────────────────────────────────────
    # Horizontal glow line that sweeps with the lion
    for step in range(0, TOTAL_STEPS, 2):
        lx = cell_x(step)
        t_start = step * STEP_MS
        t_end   = t_start + STEP_MS * 4
        frac_s  = t_start / total_ms
        frac_e  = min(t_end / total_ms, 1.0)

        kv = f"0;{frac_s:.4f};{frac_s:.4f};{frac_e:.4f};1"
        ka = "0;0;0.6;0;0"

        lines.append(
            f'<rect x="{lx-4}" y="{PAD_Y-2}" '
            f'width="{CELL+GAP+8}" height="{ROWS*(CELL+GAP)+4}" '
            f'rx="3" fill="{GOLD_MID}" opacity="0">'
            f'<animate attributeName="opacity" '
            f'values="{ka}" keyTimes="{kv}" '
            f'dur="{total_ms}ms" repeatCount="indefinite"/>'
            f'</rect>'
        )

    # ── LEGEND ───────────────────────────────────────────────────────
    legend_y = H - 22
    lines.append(f'<text x="{PAD_X}" y="{legend_y}" font-family="monospace" font-size="9" fill="{GRAY}">Less</text>')
    for i, c in enumerate([CELL_EMPTY, GOLD_DARK, GOLD_MID, GOLD_LIGHT, GOLD_GLOW]):
        lx = PAD_X + 32 + i * (CELL + 3)
        lines.append(f'<rect x="{lx}" y="{legend_y-9}" width="{CELL}" height="{CELL}" rx="2" fill="{c}"/>')
    lines.append(f'<text x="{PAD_X + 32 + 5*(CELL+3) + 4}" y="{legend_y}" font-family="monospace" font-size="9" fill="{GRAY}">More</text>')

    lines.append('</svg>')
    return "\n".join(lines)


if __name__ == "__main__":
    os.makedirs("dist", exist_ok=True)
    svg = build_svg()

    with open("dist/github-contribution-grid-lion.svg", "w") as f:
        f.write(svg)
    print("✓ dist/github-contribution-grid-lion.svg generated")

    # Also write dark variant (same content — already dark-themed)
    with open("dist/github-contribution-grid-lion-dark.svg", "w") as f:
        f.write(svg)
    print("✓ dist/github-contribution-grid-lion-dark.svg generated")
