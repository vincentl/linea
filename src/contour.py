from collections import defaultdict

def mid(src, dst):
   '''
   Compute the midpoint of the line segment from `src` to `dst`
   '''
   return tuple((i+j)/2.0 for i,j in zip(src, dst))

def contours(z):
    '''
    Input : z a numpy array representing a bitmap image with a 1-pixel
    wide gutter of while pixels surrounding the bitmap.
    
    Return: A list of tuples where each tuple represents a connected
    region in z. The tuple entries are (l, c, p) where
      l = boundary points determine by edge intersections
      c = boundary points determine by mid-points on each edge
      p = boundary pixels

    Coordinates in each tuple component trace the boundary.
    '''
    # Step 1 - Scan the input bitmap and identify all edges between white and
    # black pixels. Account for the 1-pixel wide gutter around z when recording
    # coordinates.
    # edge = Set{(src, dst, pixel)} where src and dst are the end points of 
    # the edge and pixel is the black boundary pixel.
    # points = Dict[point] -> List{edges} is used to connect edge segments to
    # form a connected boundary.
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
    # Step 2 - Form contours
    # Start with an arbitrary edge and use points dictionary to find connecting edge.
    # Remote an edge from edges once it is used.
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
