from collections import defaultdict

def mid(src, dst):
   return tuple((i+j)/2.0 for i,j in zip(src, dst))

def contours(z):
    # Create edge set - all edges between white and black pixels
    # Points maps point -> edge 
    # edge = (src, dst, pixel)
    x_count, y_count = z.shape
    edges = set()
    points = defaultdict(list)
    for x in range(1,x_count-1):
        for y in range(1,y_count-1):
            if z[x][y] == 0:
                continue
            pixel = (x,y)
            # check pixel, src, dst
            for check, src, dst in [[(x-1,y), (x  -1,y  -1), (x  -1,y+1-1)],
                                    [(x,y+1), (x  -1,y+1-1), (x+1-1,y+1-1)],
                                    [(x+1,y), (x+1-1,y+1-1), (x+1-1,y  -1)],
                                    [(x,y-1), (x+1-1,y  -1), (x  -1,y  -1)]]:
                if z[*pixel] != z[*check]:
                    edge = (src, dst, (x-1,y-1))
                    points[src] += [edge]
                    points[dst] += [edge]
                    edges.add(edge)
    # Form contours
    contour = []
    while len(edges):
        src, dst, pixel = edges.pop()
        start = src
        p = [pixel]
        l = [src]
        c = [mid(src,dst)]
        while dst != start:
            option = [e for e in points[dst] if e in edges]
            if len(option) > 1:
                option = [e for e in option if e[-1] == pixel]
            if len(option) != 1:
                print("ERROR")
                return
            edge = option[0]
            edges.remove(edge)
            src, dst, pixel = edge
            p += [pixel]
            l += [src]
            c += [mid(src, dst)]
        p += [p[0]]
        l += [l[0]]
        c += [c[0]]
        contour += [(l, c, p)]
    return contour
