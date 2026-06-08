"""
gen_corbel_split.py
Corbel template split into 2 parts with a sliding dovetail joint.
Part 1 (top): female socket.   Part 2 (bottom): male tail.
"""
import numpy as np
from datetime import datetime
from shapely.geometry import Polygon, box, LineString
from trimesh.creation import extrude_polygon as extrude
from dovetail import dovetail_poly

COR_D=260; COR_H=870; COR_FOOT_X=20; COR_TIP=10; K=16
DENOM=np.exp(K)-1
TEMPLATE_H=400; THK=8.0; BORDER=20; N=200; R_CORNER=3
BASE=f'/Users/igorkr/dev/cp/adamit-club/bar/corbel_template_{datetime.now().strftime("%H%M%S")}'

TAIL_BASE = 7; TAIL_D = 7; TAIL_TIP = 9; CL = 0.01
TAIL_SPACING = 14   # centre-to-centre spacing between the two tails on each split face
D_SPLIT      = 180  # depth of the y-split between Part 1 (top) and Part 2 (bottom)

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

# Two male tails on Part 2 (protrude upward into Part 1), spaced along x
cx_a, cx_b = cx - TAIL_SPACING/2, cx + TAIL_SPACING/2
tail   = (dovetail_poly(cx_a, -D_SPLIT, TAIL_BASE, TAIL_TIP, TAIL_D, direction='up')
          .union(dovetail_poly(cx_b, -D_SPLIT, TAIL_BASE, TAIL_TIP, TAIL_D, direction='up')))
socket = (dovetail_poly(cx_a, -D_SPLIT, TAIL_BASE, TAIL_TIP, TAIL_D, direction='up', cl=CL)
          .union(dovetail_poly(cx_b, -D_SPLIT, TAIL_BASE, TAIL_TIP, TAIL_D, direction='up', cl=CL)))
top_clip=box(-10,-D_SPLIT,COR_D+10,10)
bot_clip=box(-10,-TEMPLATE_H-10,COR_D+10,-D_SPLIT)
def clip(p,b): return p.intersection(b)

outer_top = clip(outer_poly,top_clip).difference(socket)   # Part 1 with socket notch
outer_bot = clip(outer_poly,bot_clip).union(tail)            # Part 2
hole_top  = clip(hole_poly,top_clip)
hole_bot  = clip(hole_poly,bot_clip)

# ── Second split: Part 1 → 1 (left) + 3 (right curved corner) ───────────────
X_SPLIT = 180   # mm — both halves fit in 255×255

# Find depth where xc(d) == X_SPLIT (below this depth, 1B has no material)
d_xsplit = next(d for d in np.linspace(0, D_SPLIT, 5000) if xc(d) <= X_SPLIT)
cy2 = -d_xsplit / 2   # centre of the x-split face in y

# Two tails on Part 3 protrude LEFT into Part 1, spaced along y
cy2_a, cy2_b = cy2 - TAIL_SPACING/2, cy2 + TAIL_SPACING/2
tail2   = (dovetail_poly(X_SPLIT, cy2_a, TAIL_BASE, TAIL_TIP, TAIL_D, direction='left')
           .union(dovetail_poly(X_SPLIT, cy2_b, TAIL_BASE, TAIL_TIP, TAIL_D, direction='left')))
socket2 = (dovetail_poly(X_SPLIT, cy2_a, TAIL_BASE, TAIL_TIP, TAIL_D, direction='left', cl=CL)
           .union(dovetail_poly(X_SPLIT, cy2_b, TAIL_BASE, TAIL_TIP, TAIL_D, direction='left', cl=CL)))

left_clip  = box(-10, -D_SPLIT, X_SPLIT,      10)
right_clip = box(X_SPLIT, -D_SPLIT, COR_D+10, 10)

outer_1 = clip(outer_top, left_clip).difference(socket2)   # Part 1: socket
outer_3 = clip(outer_top, right_clip).union(tail2)          # Part 3: tail
hole_1  = clip(hole_top,  left_clip)
hole_3  = clip(hole_top,  right_clip)

# Diagonal support through Part 1 hole (bottom-left → top-right)
_hb = hole_1.bounds
diag_strip = LineString([(_hb[0], _hb[3]), ((_hb[0]+_hb[2])/2, (_hb[1]+_hb[3])/2)]).buffer(BORDER/2, cap_style=2)
hole_1 = hole_1.difference(diag_strip)

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

save_obj(*make_mesh(outer_1, hole_1), BASE+'_part1.obj')
save_obj(*make_mesh(outer_3, hole_3), BASE+'_part3.obj')
save_obj(*make_mesh(outer_bot, hole_bot), BASE+'_part2.obj')
print(f'Dovetail params: neck {TAIL_BASE}mm → tip {TAIL_TIP:.1f}mm | depth {TAIL_D}mm')
print(f'Part 1: left of x={X_SPLIT}mm | Part 3: right curved corner (~{int(COR_D-X_SPLIT)}×{int(d_xsplit)}mm)')
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
for poly, name in [(outer_1,'Part 1'),(outer_3,'Part 3'),(outer_bot,'Part 2 ')]:
    b = poly.bounds
    w, h = b[2]-b[0], b[3]-b[1]
    chk(w<=BED and h<=BED, f'{name}  bbox {w:.1f}×{h:.1f} mm  (bed {BED}×{BED})')

# 2. Y-split joint: Part 2 tail fits inside Part 1 socket
tail_inflated = tail.buffer(0)            # exact tail
chk(socket.buffer(0.05).contains(tail_inflated),
    f'Y-joint  tail({TAIL_BASE}→{TAIL_TIP:.1f}mm) fits Part1 socket (CL={CL}mm)')

# 3. X-split joint: Part 3 tail2 fits inside Part 1 socket2
chk(socket2.buffer(0.05).contains(tail2.buffer(0)),
    f'X-joint  tail({TAIL_BASE}→{TAIL_TIP:.1f}mm) fits Part1 socket2 (CL={CL}mm)')

# 4. Assembly coverage vs original template
original = clip(outer_poly, top_clip).union(clip(outer_poly, bot_clip))
assembled = outer_1.union(outer_3).union(outer_bot)
gap      = original.difference(assembled)
excess   = assembled.difference(original)
gap_pct  = gap.area / original.area * 100
exc_pct  = excess.area / original.area * 100
chk(gap_pct < 1.0,    f'Assembly gap   {gap.area:.1f} mm²  ({gap_pct:.2f}% of template)')
chk(exc_pct < 1.0,    f'Assembly excess {excess.area:.1f} mm²  ({exc_pct:.2f}% of template)')

print(f'\n  {"ALL CHECKS PASSED ✓" if ok_all else "SOME CHECKS FAILED ✗ — review before printing"}')
