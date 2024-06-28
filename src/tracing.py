import svg

def cartesian_to_complex(pt):
    return pt[0] + 1j*pt[1]

def complex_to_cartensian(c):
    return (c.real, c.imag)

# An Introduction to B-Spline Curves by Thomas W. Sederberg
def bs_to_bz2(p01, p12, p23):
    '''
    Input 3 consecutive B-Spline Control Points
    Return QuadraticBezier
    '''
    p01, p12, p23 = (cartesian_to_complex(pt) for pt in (p01, p12, p23))
    p11 = ((2-1)*p01 + (1-0)*p12)/2
    p22 = ((3-2)*p12 + (2-1)*p23)/(3-1)
    p11, p12, p22 = (complex_to_cartensian(c) for c in (p11, p12, p22))
    return [svg.MoveTo(*p11), svg.QuadraticBezier(*p12, *p22)]

def bs_to_bz3(p012, p123, p234, p345):
    '''
    Input 4 consecutive B-Spline Control Points
    Return CubicBezier
    '''
    p012, p123, p234, p345 = (cartesian_to_complex(pt) for pt in (p012, p123, p234, p345))
    # Pc.. = ((b-c)*Pa.. + (c-a)*Pb..)/(b-a)
    p122 = ((3-2)*p012 + (2-0)*p123)/(3-0)  # a=012 12b=3 -> 12c=2
    p223 = ((4-2)*p123 + (2-1)*p234)/(4-1)  # a=123 23b=4 -> c=223
    p222 = ((3-2)*p122 + (2-1)*p223)/(3-1)  # a=122 22b=3 -> c=222
    p233 = ((4-3)*p123 + (3-1)*p234)/(4-1)  # a=123 23b=4 -> 23c=3
    p334 = ((5-3)*p234 + (3-2)*p345)/(5-2)  # a=234 34b=5 -> c=334
    p333 = ((4-3)*p233 + (3-2)*p334)/(4-2)  # a=233 33b=4 -> c=333 
    p222, p223, p233, p333 = (complex_to_cartensian(c) for c in (p222, p223, p233, p333))
    return [svg.MoveTo(*p222), svg.CubicBezier(*p223, *p233, *p333)]

def trace_linear(config, p):
    '''
    Input Points
      p = [p(0,1), p(1,2), p(2,3), p(3,4) ... ]
    form lines between the points
      Path(...Line(p[i], p[i+1])...)
    '''
    d = [svg.MoveTo(*p[-1])]
    d += [svg.LineTo(*v) for v in p]
    return svg.Path(
        d=d,
        fill='none',
        stroke=config['svg']['color'],
        stroke_width=config['svg']['stroke-width'],
    )

def trace_quadratic(config, p):
    '''
    Input B-Spline Control Points
      p = [p(0,1), p(1,2), p(2,3), p(3,4) ... ]
    compute degree 2 Bezier curves
      Path(...QuadraticBezier(p(i,i), p(i,i+1), p(i+1,i+1))...)
    '''
    d = [cmd for v in zip(p, p[1:], p[2:]) for cmd in bs_to_bz2(*v)]
    d = d[:2] + d[3::2]
    return svg.Path(
        d=d,
        fill='none',
        stroke=config['svg']['color'],
        stroke_width=config['svg']['stroke-width'],
    )

def trace_cubic(config, p):
    '''
    Input B-Spline Control Points
      p = [p(0,1), p(1,2), p(2,3), p(3,4) ... ]
    compute degree 3 Bezier curves
      Path(...QuadraticBezier(p(i,i,i), p(i,i,i+1), p(i,i+1,i+1), p(i+1,i+1,i+1)...)
    '''
    d = [cmd for v in zip(p, p[1:], p[2:], p[3:]) for cmd in bs_to_bz3(*v)]
    d = d[:2] + d[3::2]
    return svg.Path(
        d=d,
        fill='none',
        stroke=config['svg']['color'],
        stroke_width=config['svg']['stroke-width'],
    )
