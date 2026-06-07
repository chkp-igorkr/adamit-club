"""
gen_corbel_split.py
Corbel template split into 2 parts with a sliding dovetail joint.
Part 1 (top): female socket.   Part 2 (bottom): male tail.
"""
import math, numpy as np
from datetime import datetime
from shapely.geometry import Polygon, box
from trimesh.creation import extrude_polygon as extrude

COR_D=260; COR_H=870; COR_FOOT_X=20; COR_TIP=10; K=16
DENOM=np.exp(K)-1
TEMPLATE_H=400; THK=7.0; BORDER=15; N=500; R_CORNER=6
BASE=f'/Users/igorkr/dev/cp/adamit-club/bar/corbel_template_{datetime.now().strftime("%Y%m%d_%H%M%S")}'

TAIL_BASE = 10
TAIL_D    = 10
ANGLE     = 8
CL        = 0.01
D_SPLIT   = 200
TAIL_TIP  = TAIL_BASE + 2*TAIL_D*math.tan(math.radians(ANGLE))
GAP       = 0.0   # socket opens directly at split face

def xc(d):
    if d<=COR_TIP: return float(COR_D)
    if d>=COR_H:   return float(COR_FOOT_X)
    t=(COR_H-d)/(COR_H-COR_TIP)
    return COR_FOOT_X+(COR_D-COR_FOOT_X)*(np.exp(K*t)-1)/DENOM

ds=np.linspace(COR_TIP,TEMPLATE_H,N)
outer_pts=[(0.,0.),(COR_D,0.),(COR_D,-COR_TIP)]+[(xc(d),-d) for d in ds]+[(0.,-TEMPLATE_H)]
outer_poly=Polygon(outer_pts)
hole_poly =outer_poly.buffer(-BORDER,join_style=2)
hole_poly =hole_poly.buffer(-R_CORNER,join_style=1,resolution=64).buffer(R_CORNER)

x_split=xc(D_SPLIT); cx=x_split/2

# Male tail on Part 2 (protrudes upward into Part 1)
tail=Polygon([
    (cx-TAIL_BASE/2, -D_SPLIT),
    (cx+TAIL_BASE/2, -D_SPLIT),
    (cx+TAIL_TIP/2,  -D_SPLIT+TAIL_D),
    (cx-TAIL_TIP/2,  -D_SPLIT+TAIL_D),
])

# Female socket on Part 1 — closed GAP mm above split face = true interior ring
socket=Polygon([
    (cx-TAIL_BASE/2-CL, -D_SPLIT+GAP),
    (cx+TAIL_BASE/2+CL, -D_SPLIT+GAP),
    (cx+TAIL_TIP/2+CL,  -D_SPLIT+TAIL_D+CL),
    (cx-TAIL_TIP/2-CL,  -D_SPLIT+TAIL_D+CL),
])
top_clip=box(-10,-D_SPLIT,COR_D+10,10)
bot_clip=box(-10,-TEMPLATE_H-10,COR_D+10,-D_SPLIT)
def clip(p,b): return p.intersection(b)

outer_top = clip(outer_poly,top_clip).difference(socket)   # Part 1 with socket notch
outer_bot = clip(outer_poly,bot_clip).union(tail)            # Part 2
hole_top  = clip(hole_poly,top_clip)
hole_bot  = clip(hole_poly,bot_clip)

# ── Second split: Part 1 → 1A (left) + 1B (right curved corner) ──────────────
X_SPLIT = 180   # mm — both halves fit in 255×255

# Find depth where xc(d) == X_SPLIT (below this depth, 1B has no material)
d_xsplit = next(d for d in np.linspace(0, D_SPLIT, 5000) if xc(d) <= X_SPLIT)
cy2 = -d_xsplit / 2   # centre of the x-split face in y

# Part 1B male tail protrudes LEFT (-x) into Part 1A socket
tail2 = Polygon([
    (X_SPLIT,          cy2 - TAIL_BASE/2),
    (X_SPLIT,          cy2 + TAIL_BASE/2),
    (X_SPLIT - TAIL_D, cy2 + TAIL_TIP/2),
    (X_SPLIT - TAIL_D, cy2 - TAIL_TIP/2),
])
socket2 = Polygon([
    (X_SPLIT,                cy2 - TAIL_BASE/2 - CL),
    (X_SPLIT,                cy2 + TAIL_BASE/2 + CL),
    (X_SPLIT - TAIL_D - CL,  cy2 + TAIL_TIP/2 + CL),
    (X_SPLIT - TAIL_D - CL,  cy2 - TAIL_TIP/2 - CL),
])

left_clip  = box(-10, -D_SPLIT, X_SPLIT,      10)
right_clip = box(X_SPLIT, -D_SPLIT, COR_D+10, 10)

outer_1a = clip(outer_top, left_clip).difference(socket2)   # Part 1A: socket
outer_1b = clip(outer_top, right_clip).union(tail2)          # Part 1B: tail
hole_1a  = clip(hole_top,  left_clip)
hole_1b  = clip(hole_top,  right_clip)

def make_mesh(outer_p, hole_p, extra_holes=None):
    extra_holes = extra_holes or []
    solid = outer_p
    if not hole_p.is_empty: solid = solid.difference(hole_p)
    for eh in extra_holes:  solid = solid.difference(eh)
    mesh = extrude(solid, height=THK)
    return mesh.vertices, mesh.faces

def save_obj(verts, faces, path):
    with open(path, 'w') as f:
        f.write(f'# {path}\no part\n')
        for v in verts:  f.write(f'v {v[0]:.4f} {v[1]:.4f} {v[2]:.4f}\n')
        for fc in faces: f.write(f'f {fc[0]+1} {fc[1]+1} {fc[2]+1}\n')
    print(f'Saved {len(faces)} tris → {path}')

save_obj(*make_mesh(outer_1a, hole_1a), BASE+'_part1a.obj')
save_obj(*make_mesh(outer_1b, hole_1b), BASE+'_part1b.obj')
save_obj(*make_mesh(outer_bot, hole_bot), BASE+'_part2.obj')
print(f'Dovetail params: neck {TAIL_BASE}mm → tip {TAIL_TIP:.1f}mm | depth {TAIL_D}mm | angle {ANGLE}°')
print(f'Part 1A: left of x={X_SPLIT}mm | Part 1B: right curved corner (~{int(COR_D-X_SPLIT)}×{int(d_xsplit)}mm)')
print(f'Part 2:  depth {D_SPLIT}–{TEMPLATE_H}mm')

# ── VALIDATION ────────────────────────────────────────────────────────────────
print('\n── VALIDATION ───────────────────────────────────────────────────────')
ok_all = True

def chk(cond, msg):
    global ok_all
    ok_all = ok_all and cond
    print(f'  {"✓" if cond else "✗"} {msg}')

# 1. Bounding boxes ≤ 255×255
BED = 255
for poly, name in [(outer_1a,'Part 1A'),(outer_1b,'Part 1B'),(outer_bot,'Part 2 ')]:
    b = poly.bounds
    w, h = b[2]-b[0], b[3]-b[1]
    chk(w<=BED and h<=BED, f'{name}  bbox {w:.1f}×{h:.1f} mm  (bed {BED}×{BED})')

# 2. Y-split joint: Part 2 tail fits inside Part 1A socket
tail_inflated = tail.buffer(0)            # exact tail
chk(socket.buffer(0.05).contains(tail_inflated),
    f'Y-joint  tail({TAIL_BASE}→{TAIL_TIP:.1f}mm) fits Part1A socket (CL={CL}mm)')

# 3. X-split joint: Part 1B tail2 fits inside Part 1A socket2
chk(socket2.buffer(0.05).contains(tail2.buffer(0)),
    f'X-joint  tail({TAIL_BASE}→{TAIL_TIP:.1f}mm) fits Part1A socket2 (CL={CL}mm)')

# 4. Assembly coverage vs original template
original = clip(outer_poly, top_clip).union(clip(outer_poly, bot_clip))
assembled = outer_1a.union(outer_1b).union(outer_bot)
gap      = original.difference(assembled)
excess   = assembled.difference(original)
gap_pct  = gap.area / original.area * 100
exc_pct  = excess.area / original.area * 100
chk(gap_pct < 1.0,    f'Assembly gap   {gap.area:.1f} mm²  ({gap_pct:.2f}% of template)')
chk(exc_pct < 1.0,    f'Assembly excess {excess.area:.1f} mm²  ({exc_pct:.2f}% of template)')

print(f'\n  {"ALL CHECKS PASSED ✓" if ok_all else "SOME CHECKS FAILED ✗ — review before printing"}')
