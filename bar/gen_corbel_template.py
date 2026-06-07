"""
gen_corbel_template.py
Generates corbel_template.stl — upper 400 mm of the corbel outer profile,
extruded to 4 mm for FDM 3-D printing.

Router offset guidance:
  Flush-trim bit (bearing ø = cutter ø)  → NO offset, use as-is.
  Pattern bit    (top bearing, same ø)   → NO offset, use as-is.
  Guide bushing + straight bit           → offset = (bushing OD − bit ø) / 2
     e.g. 12.7 mm bushing + 6.35 mm bit → 3.2 mm offset (rerun with OFFSET > 0).

Note: template bounding box is 260 × 400 mm — may need a large-format printer
or print in two halves along the mid-depth seam and glue.
"""
import numpy as np
import struct

# ── Parameters (mm) ──────────────────────────────────────────────────────────
COR_D      = 260
COR_H      = 870
COR_FOOT_X = 20
COR_TIP    = 10
K          = 16
DENOM      = np.exp(K) - 1

TEMPLATE_H = 400    # depth from countertop bottom to template bottom
THICKNESS  = 4.0    # extrusion thickness for printing
OFFSET     = 0.0    # router offset (0 = flush-trim, set >0 for guide bushing)

# ── Curve formula (t=0 at foot, t=1 at top) ──────────────────────────────────
def x_at_depth(d):
    if d <= COR_TIP: return float(COR_D) + OFFSET
    if d >= COR_H:   return float(COR_FOOT_X) + OFFSET
    t = (COR_H - d) / (COR_H - COR_TIP)
    x = COR_FOOT_X + (COR_D - COR_FOOT_X) * (np.exp(K * t) - 1) / DENOM
    return x + OFFSET

# ── Sample curve ──────────────────────────────────────────────────────────────
N = 500
depths = np.linspace(COR_TIP, TEMPLATE_H, N)
cx = np.array([x_at_depth(d) for d in depths])
cy = -depths   # y-up, downward = negative

T = THICKNESS
triangles = []

def tri(a, b, c):
    a, b, c = np.asarray(a, float), np.asarray(b, float), np.asarray(c, float)
    n = np.cross(b - a, c - a)
    ln = np.linalg.norm(n)
    if ln < 1e-12:
        return
    triangles.append((n / ln, a, b, c))

# ── Top face  (z = T, outward normal +z, CCW winding viewed from +z) ─────────
# Top flat rectangle: y=0 → y=-COR_TIP, x=0 → x=COR_D
tri((0, 0, T), (0, -COR_TIP, T), (COR_D, -COR_TIP, T))
tri((0, 0, T), (COR_D, -COR_TIP, T), (COR_D, 0, T))
# Curved strips: left wall at x=0, right wall follows cx
for i in range(N - 1):
    y0, y1, x0, x1 = cy[i], cy[i+1], cx[i], cx[i+1]
    tri((0, y0, T), (0, y1, T), (x1, y1, T))
    tri((0, y0, T), (x1, y1, T), (x0, y0, T))

# ── Bottom face  (z = 0, outward normal −z, reversed winding) ────────────────
tri((0, 0, 0), (COR_D, -COR_TIP, 0), (0, -COR_TIP, 0))
tri((0, 0, 0), (COR_D, 0, 0), (COR_D, -COR_TIP, 0))
for i in range(N - 1):
    y0, y1, x0, x1 = cy[i], cy[i+1], cx[i], cx[i+1]
    tri((0, y0, 0), (x1, y1, 0), (0, y1, 0))
    tri((0, y0, 0), (x0, y0, 0), (x1, y1, 0))

# ── Side walls  (outward normals point away from interior) ───────────────────
# Build outline polygon — clockwise when viewed from +z
outline = np.array(
    [(0., 0.), (COR_D + OFFSET, 0.), (COR_D + OFFSET, -COR_TIP)]
    + list(zip(cx, cy))
    + [(0., -TEMPLATE_H)]
)
for i in range(len(outline)):
    p0 = outline[i]
    p1 = outline[(i + 1) % len(outline)]
    tri((p0[0], p0[1], 0), (p0[0], p0[1], T), (p1[0], p1[1], T))
    tri((p0[0], p0[1], 0), (p1[0], p1[1], T), (p1[0], p1[1], 0))

# ── Write binary STL ──────────────────────────────────────────────────────────
out = '/Users/igorkr/dev/cp/adamit-club/bar/corbel_template.stl'
header = b'Corbel router template 400mm, flush-trim bit, no offset' + b'\x00' * 80
with open(out, 'wb') as f:
    f.write(header[:80])
    f.write(struct.pack('<I', len(triangles)))
    for n, a, b, c in triangles:
        f.write(struct.pack('<3f', *n))
        f.write(struct.pack('<3f', *a))
        f.write(struct.pack('<3f', *b))
        f.write(struct.pack('<3f', *c))
        f.write(struct.pack('<H', 0))

print(f'Saved  → {out}')
print(f'Size     {TEMPLATE_H} × {COR_D} × {T:.0f} mm  (depth × width × thick)')
print(f'Offset   {OFFSET} mm  (0 = flush-trim / pattern bit)')
print(f'Tris     {len(triangles)}')
print()
print('Router offset guide:')
print('  Flush-trim / pattern bit  → OFFSET = 0  (this file)')
print('  Guide bushing             → OFFSET = (bushing OD − bit ø) / 2')
print('  To apply offset: set OFFSET in this script and rerun.')
