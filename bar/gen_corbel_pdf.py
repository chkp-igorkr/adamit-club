import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Polygon

# ── Parameters (mm) ──────────────────────────────────────────────────────────
COR_D      = 260   # horizontal projection at top
COR_H      = 870   # total height (countertop bottom to foot)
COR_FOOT_X = 20    # protrusion at foot
COR_TIP    = 10    # flat face thickness at outer tip
COR_W      = 40    # depth into page
K          = 16    # exponential steepness

# ── Curve points (internal: t=0 → top, t=1 → foot, traces top→foot for polygon) ─
N = 400
t  = np.linspace(0, 1, N)
DENOM = np.exp(K) - 1
xc = COR_FOOT_X + (COR_D - COR_FOOT_X) * (np.exp(K * (1 - t)) - 1) / DENOM
yc = -(COR_TIP + (COR_H - COR_TIP) * t)   # downward = negative

# ── Profile outline ───────────────────────────────────────────────────────────
px = np.concatenate([[0, COR_D, COR_D], xc, [0, 0]])
py = np.concatenate([[0, 0, -COR_TIP],  yc, [-COR_H, 0]])

# ── Figure (A4 portrait) ──────────────────────────────────────────────────────
fig = plt.figure(figsize=(8.27, 11.69), facecolor='white')
ax  = fig.add_axes([0.18, 0.18, 0.64, 0.72])
ax.set_aspect('equal')
ax.set_xlim(-100, 380)
ax.set_ylim(-960, 90)
ax.axis('off')

# ── Corbel fill ───────────────────────────────────────────────────────────────
poly = Polygon(list(zip(px, py)), closed=True,
               facecolor='#C8A068', edgecolor='#2a2a2a', linewidth=1.5, zorder=3)
ax.add_patch(poly)

for yi in range(-50, -int(COR_H), -80):
    ax.plot([2, 30], [yi, yi - 8], color='#b08040', lw=0.4, alpha=0.5, zorder=4)

# ── Reference lines ───────────────────────────────────────────────────────────
ax.plot([0,  0], [65, -COR_H - 20], color='#aaa', lw=0.7, ls='--', zorder=1)
ax.plot([-90, COR_D + 35], [0, 0],  color='#aaa', lw=0.7, ls='--', zorder=1)

# ── Overall dimensions ────────────────────────────────────────────────────────
ASPEC = dict(arrowstyle='<->', color='black', lw=0.9, mutation_scale=9)

def hdim(x1, x2, y, label, laby=None, fs=9, bold=False):
    ax.plot([x1, x1], [y - 5, y + 5], 'k-', lw=0.9)
    ax.plot([x2, x2], [y - 5, y + 5], 'k-', lw=0.9)
    ax.annotate('', xy=(x2, y), xytext=(x1, y), arrowprops=ASPEC)
    ax.text((x1 + x2) / 2, (laby if laby is not None else y + 6), label,
            ha='center', va='bottom', fontsize=fs,
            fontweight='bold' if bold else 'normal',
            bbox=dict(facecolor='white', edgecolor='none', pad=1))

def vdim(x, y1, y2, label, labx=None, fs=9, bold=False):
    ax.plot([x - 5, x + 5], [y1, y1], 'k-', lw=0.9)
    ax.plot([x - 5, x + 5], [y2, y2], 'k-', lw=0.9)
    ax.annotate('', xy=(x, y2), xytext=(x, y1), arrowprops=ASPEC)
    ax.text((labx if labx is not None else x - 10), (y1 + y2) / 2, label,
            ha='center', va='center', fontsize=fs, rotation=90,
            fontweight='bold' if bold else 'normal',
            bbox=dict(facecolor='white', edgecolor='none', pad=1))

# Overall width (above)
hdim(0, COR_D, 55, f'{COR_D} mm', laby=62, bold=True)

# Foot protrusion (below)
hdim(0, COR_FOOT_X, -COR_H - 40, f'{COR_FOOT_X} mm', laby=-COR_H - 54, bold=True)

# Overall height (right)
vdim(330, -COR_H, 0, f'{COR_H} mm', labx=344, bold=True)

# Tip thickness (right)
ax.plot([COR_D + 12, COR_D + 20], [0, 0], 'k-', lw=0.9)
ax.plot([COR_D + 12, COR_D + 20], [-COR_TIP, -COR_TIP], 'k-', lw=0.9)
ax.annotate('', xy=(COR_D + 16, -COR_TIP), xytext=(COR_D + 16, 0),
            arrowprops=dict(arrowstyle='<->', color='black', lw=0.8, mutation_scale=7))
ax.text(COR_D + 50, -COR_TIP / 2, f'{COR_TIP} mm tip', ha='left', va='center', fontsize=7.5)

# Depth note
ax.text(COR_D / 2, -COR_H / 2 + 30, f'Depth: {COR_W} mm\n(into page)',
        ha='center', va='center', fontsize=7.5, color='#444', style='italic',
        bbox=dict(facecolor='#f0e8d8', edgecolor='#b08040', pad=4, lw=0.7))

# ── Curve x-dimensions at every 50 mm of depth ───────────────────────────────
# Formula with t=0 at foot: x(t) = 20 + 240*(exp(16t)-1)/(exp(16)-1)
# For depth d: t = (COR_H - d) / (COR_H - COR_TIP)  [maps foot→0, top→1]
depths = list(range(0, 351, 25)) + list(range(400, COR_H, 50)) + [COR_H]
for i, d in enumerate(depths):
    if d <= COR_TIP:
        x_val = float(COR_D)                             # flat top face
    elif d >= COR_H:
        x_val = float(COR_FOOT_X)                        # foot
    else:
        t_val = (COR_H - d) / (COR_H - COR_TIP)         # t=0 at foot, t=1 at top
        x_val = COR_FOOT_X + (COR_D - COR_FOOT_X) * (np.exp(K * t_val) - 1) / DENOM
    x_val  = round(x_val, 1)
    y_plot = -d

    # Thin horizontal reference tick from cabinet face to curve
    ax.plot([0, x_val], [y_plot, y_plot], color='#bbb', lw=0.5, zorder=2)
    ax.plot([0,     0    ], [y_plot - 2, y_plot + 2], color='#555', lw=0.7, zorder=5)
    ax.plot([x_val, x_val], [y_plot - 2, y_plot + 2], color='#555', lw=0.7, zorder=5)

    # Both labels to the left of cabinet face, aligned columns
    ax.text(-5, y_plot, f'y={d:3d}, x={x_val:5.1f}',
            ha='right', va='center', fontsize=6.5, color='#222', family='monospace')

# ── Formula box (no table) ────────────────────────────────────────────────────
formula = '\n'.join([
    'OUTER PROFILE CURVE',
    '',
    '  x(t) = 20 + 240 · (exp(16·t) − 1) / (exp(16) − 1)',
    '  depth(t) = 870 − 860 · t          t ∈ [0, 1]',
    '',
    '  t = 0  →  foot:   x =  20 mm,  depth = 870 mm',
    '  t = 1  →  top:    x = 260 mm,  depth =  10 mm',
    '',
    '  Dimensions on drawing show x at every 50 mm of depth.',
])

fig.text(0.07, 0.155, formula,
         fontsize=7.5, family='monospace', va='top', ha='left',
         bbox=dict(boxstyle='round,pad=0.5', facecolor='#f9f9f9',
                   edgecolor='#999', lw=0.8))

# ── Title block ───────────────────────────────────────────────────────────────
fig.text(0.5, 0.962, 'OAK CORBEL  —  SIDE PROFILE',
         ha='center', va='top', fontsize=15, fontweight='bold')
fig.text(0.5, 0.944,
         'Bar Island  ·  Material: Solid Oak  ·  Piece depth: 40 mm  ·  All dimensions in mm',
         ha='center', va='top', fontsize=8.5, color='#444')
fig.add_artist(plt.Line2D([0.04, 0.96], [0.935, 0.935],
               transform=fig.transFigure, color='black', lw=0.8))

# ── Border ────────────────────────────────────────────────────────────────────
for inset, lw in [(0.025, 1.8), (0.032, 0.5)]:
    rect = mpatches.FancyBboxPatch(
        (inset, inset), 1 - 2 * inset, 1 - 2 * inset,
        boxstyle='square,pad=0', transform=fig.transFigure,
        fill=False, linewidth=lw, color='black', clip_on=False)
    fig.add_artist(rect)

# ── Save ──────────────────────────────────────────────────────────────────────
out = '/Users/igorkr/dev/cp/adamit-club/bar/corbel_profile.pdf'
plt.savefig(out, format='pdf', dpi=300, bbox_inches='tight', facecolor='white')
print(f'Saved → {out}')
