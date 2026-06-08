from shapely.geometry import Polygon

def dovetail_poly(x, y, tail_base, tail_tip, tail_d, direction='down', cl=0):
    """
    Trapezoid for a dovetail tail or socket.
    x, y      : neck centre (point on the joint face at the centre of the tail)
    tail_base : neck width (mm)
    tail_tip  : tip width (mm)
    tail_d    : depth (mm)
    direction : 'up' | 'down' | 'left' | 'right' — which way the tail grows
    cl        : clearance per side — 0 for male tail, CL for socket
    """
    b = tail_base/2 + cl
    t = tail_tip/2  + cl
    d = tail_d      + cl
    if direction == 'down':
        return Polygon([(x-b, y), (x+b, y), (x+t, y-d), (x-t, y-d)])
    if direction == 'up':
        return Polygon([(x-b, y), (x+b, y), (x+t, y+d), (x-t, y+d)])
    if direction == 'left':
        return Polygon([(x, y-b), (x, y+b), (x-d, y+t), (x-d, y-t)])
    if direction == 'right':
        return Polygon([(x, y-b), (x, y+b), (x+d, y+t), (x+d, y-t)])
    raise ValueError(f"direction must be 'up'|'down'|'left'|'right', got {direction!r}")
