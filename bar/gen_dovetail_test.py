"""
gen_dovetail_test.py
Small dovetail test connector — male + female — to calibrate clearance.
Tail parameters match gen_corbel_split.py.
"""
import math
from datetime import datetime
from shapely.geometry import Polygon, box
from trimesh.creation import extrude_polygon as extrude

TAIL_BASE = 10
TAIL_D    = 10
ANGLE     = 8
CL        = 0.005   # tweak this to calibrate fit
THK       = 7.0

TAIL_TIP = TAIL_BASE + 2*TAIL_D*math.tan(math.radians(ANGLE))

BASE = f'/Users/igorkr/dev/cp/adamit-club/bar/dovetail_test_{datetime.now().strftime("%Y%m%d_%H%M%S")}'

W  = 25   # block width
H  = 15   # body height on each side of joint
cx = W / 2

# Male: body + tail protruding downward
male = box(0, 0, W, H-10).union(Polygon([
    (cx - TAIL_BASE/2,  0),
    (cx + TAIL_BASE/2,  0),
    (cx + TAIL_TIP/2,  -TAIL_D),
    (cx - TAIL_TIP/2,  -TAIL_D),
]))

# Female: body with socket cut in from bottom edge
female = box(0, -H, W, 0).difference(Polygon([
    (cx - TAIL_BASE/2 - CL,  0),
    (cx + TAIL_BASE/2 + CL,  0),
    (cx + TAIL_TIP/2  + CL, -TAIL_D - CL),
    (cx - TAIL_TIP/2  - CL, -TAIL_D - CL),
]))

from shapely.affinity import translate
GAP = 5   # mm between pieces when laid side by side
meshes = [extrude(male, height=THK), extrude(translate(female, xoff=W + GAP), height=THK)]

path = BASE + '_test.obj'
with open(path, 'w') as f:
    f.write(f'# {path}\n')
    offset = 0
    for i, mesh in enumerate(meshes):
        f.write(f'o part{i+1}\n')
        for v in mesh.vertices: f.write(f'v {v[0]:.4f} {v[1]:.4f} {v[2]:.4f}\n')
        for fc in mesh.faces:   f.write(f'f {fc[0]+1+offset} {fc[1]+1+offset} {fc[2]+1+offset}\n')
        offset += len(mesh.vertices)
total = sum(len(m.faces) for m in meshes)
print(f'Saved {total} tris → {path}')
print(f'Tail: neck={TAIL_BASE}mm → tip={TAIL_TIP:.2f}mm | depth={TAIL_D}mm | angle={ANGLE}° | CL={CL}mm')
