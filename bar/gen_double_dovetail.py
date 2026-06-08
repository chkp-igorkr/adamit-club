"""
gen_double_dovetail.py
Double dovetail test connector — male + female — two tails side by side on the same face.
Parameters match gen_dovetail_test2.py.
"""
import math
from datetime import datetime
from shapely.geometry import box
from shapely.affinity import translate
from trimesh.creation import extrude_polygon as extrude
from dovetail import dovetail_poly as _dt

TAIL_BASE = 7      # neck width at joint face (mm)
TAIL_D    = 7      # tail depth (mm)
TAIL_TIP  = 9     # tail tip width (mm)
CL        = 0.005   # clearance per side (mm)
THK       = 8.0     # extrusion thickness (mm)

TAIL_SPACING = 14   # center-to-center spacing between the two tails (mm)
W  = 30             # block width (must fit 2 tails + walls)
H  = 15             # body height on each side of joint

cx1 = W/2 - TAIL_SPACING/2   # left tail centre-x
cx2 = W/2 + TAIL_SPACING/2   # right tail centre-x

BASE = f'/Users/igorkr/dev/cp/adamit-club/bar/dovetail2_{datetime.now().strftime("%H%M%S")}'

def dt(x, y, direction='down', cl=0):
    return _dt(x, y, TAIL_BASE, TAIL_TIP, TAIL_D, direction=direction, cl=cl)

# Male: body + two tails protruding downward (neck at y=0)
male = box(0, 0, W, H - 10).union(dt(cx1, 0)).union(dt(cx2, 0))

# Female: body with two sockets cut in from bottom edge (neck at y=0)
female = box(0, -H, W, 0).difference(dt(cx1, 0, cl=CL)).difference(dt(cx2, 0, cl=CL))

parts = {
    'male':   extrude(male, height=THK),
    'female': extrude(female, height=THK),
}

for name, mesh in parts.items():
    path = f'{BASE}_{name}.obj'
    with open(path, 'w') as f:
        f.write(f'# {path}\n')
        f.write(f'o {name}\n')
        for v in mesh.vertices: f.write(f'v {v[0]:.4f} {v[1]:.4f} {v[2]:.4f}\n')
        for fc in mesh.faces:   f.write(f'f {fc[0]+1} {fc[1]+1} {fc[2]+1}\n')
    print(f'Saved {len(mesh.faces)} tris → {path}')

print(f'2× tails at x={cx1:.1f}, x={cx2:.1f} | neck={TAIL_BASE}mm → tip={TAIL_TIP:.2f}mm | depth={TAIL_D}mm | CL={CL}mm')
