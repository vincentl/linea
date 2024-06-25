from svgpathtools import Path, Line, QuadraticBezier, CubicBezier

# An Introduction to B-Spline Curves by Thomas W. Sederberg
def bs_to_bz2(p01, p12, p23):
    '''
    Input 3 consecutive B-Spline Control Points
    Return QuadraticBezier
    '''
    p11 = ((2-1)*p01 + (1-0)*p12)/2
    p22 = ((3-2)*p12 + (2-1)*p23)/(3-1)
    return QuadraticBezier(p11, p12, p22)

def bs_to_bz3(p012, p123, p234, p345):
    '''
    Input 4 consecutive B-Spline Control Points
    Return CubicBezier
    '''
    # Pc.. = ((b-c)*Pa.. + (c-a)*Pb..)/(b-a)
    p122 = ((3-2)*p012 + (2-0)*p123)/(3-0)  # a=012 12b=3 -> 12c=2
    p223 = ((4-2)*p123 + (2-1)*p234)/(4-1)  # a=123 23b=4 -> c=223
    p222 = ((3-2)*p122 + (2-1)*p223)/(3-1)  # a=122 22b=3 -> c=222
    p233 = ((4-3)*p123 + (3-1)*p234)/(4-1)  # a=123 23b=4 -> 23c=3
    p334 = ((5-3)*p234 + (3-2)*p345)/(5-2)  # a=234 34b=5 -> c=334
    p333 = ((4-3)*p233 + (3-2)*p334)/(4-2)  # a=233 33b=4 -> c=333 
    return CubicBezier(p222, p223, p233, p333)

def trace_linear(p):
    pieces = [Line(*v) for v in zip(p, p[1:])]
    return Path(*pieces)

def trace_quadratic(p):
    '''
    Input B-Spline Control Points
      p = [p(0,1), p(1,2), p(2,3), p(3,4) ... ]
    compute degree 2 Bezier
      [QuadraticBezier(p(i,i), p(i,i+1), p(i+1,i+1))]
    '''
    pieces = [bs_to_bz2(*v) for v in zip(p, p[1:], p[2:])]
    return Path(*pieces)

def trace_cubic(p):
    '''
    Input B-Spline Control Points
      p = [p(0,1), p(1,2), p(2,3), p(3,4) ... ]
    compute degree 3 Bezier
      [QuadraticBezier(p(i,i,i), p(i,i,i+1), p(i,i+1,i+1), p(i+1,i+1,i+1)]
    '''
    pieces = [bs_to_bz3(*v) for v in zip(p, p[1:], p[2:], p[3:])]
    return Path(*pieces)
