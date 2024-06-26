from os.path import dirname, abspath, join
import sys
sys.path.append(dirname(__file__))

import argparse
import geotiff
import math
import numpy as np
import os
import requests
import sys
import yaml
import pint
import svg

from contour import contours
from decimal import Decimal, ROUND_CEILING, ROUND_FLOOR
from pyproj import Transformer
from svg.path.path import Line, Path
from tracing import trace_linear, trace_cubic, trace_quadratic

def bounding_box(pixels):
    '''
    pixels is a list of xy pairs and this function computes a bounded box for the pixels
    '''
    x = [p[0] for p in pixels]
    y = [p[1] for p in pixels]
    return (min(x), min(y)), (max(x), max(y))

def api_bounds(region):
    '''
    add epsilon and round to slightly expand a region and return url fragment
    '''
    (n,s,e,w) = (Decimal(region[i]) for i in ('north', 'south', 'east', 'west'))
    z = Decimal('0.001')
    n = (n+z).quantize(z, rounding=ROUND_CEILING)
    s = (s-z).quantize(z, rounding=ROUND_FLOOR)
    e = (e+z).quantize(z, rounding=ROUND_CEILING)
    w = (w-z).quantize(z, rounding=ROUND_FLOOR)
    return f'&north={n}&south={s}&east={e}&west={w}'

def region_in_bbox(region: dict, data: geotiff.GeoTiff):
    '''
    verify the data bounding box contains the user specified region
    '''
    ((west, north), (east, south)) = data.tif_bBox
    return (south <= region['north'] <= north
            and south <= region['south'] <= north
            and west <= region['east'] <= east
            and west <= region['west'] <= east)

def find_interior(edge):
    '''
    starting from a list of edge vertices defining the boundary, generate all internal (x,y) pairs
    
    (x,y)-(x,y+1) [x,y] (x+1,y)-(x+1,y+1) [x+1,y] (x+2,y)-(x+2,y+1)
    x_min/y_min may be coordinate for interior pixel, but x_max,y_max are not
    '''
    (x_min, y_min), (x_max, y_max) = bounding_box(edge)
    boundary = set([src if src[1] < dst[1] else dst for src, dst in zip(edge, edge[1:] + [edge[-1]]) if src[0] == dst[0]])
    interior = []
    for y in range(y_min, y_max):
        inside = (x_min,y) in boundary
        for x in range(x_min, x_max):
            if inside:
                interior += [(x,y)]
            inside ^= (x+1,y) in boundary
    return interior

def locate_alignment(interior):
    '''
    use the grassfire transform to locate most interior points

    input: interior is the set of pixels forming the interior
    
    2 passes - first top-to-bottom, left-to-right
             - second bottom-to-top, right-to-left
    '''
    # create a bitmap of all zeros
    (x_min, y_min), (x_max, y_max) = bounding_box(interior)
    z = np.zeros((x_max - x_min + 3, y_max - y_min + 3), dtype=int)
    X = lambda x: x - x_min + 1
    Y = lambda y: y - y_min + 1
    for (x, y) in sorted(interior):
        z[X(x)][Y(y)] = 1 + min(z[X(x-1)][Y(y)], z[X(x)][Y(y-1)])
    for (x, y) in sorted(interior, reverse=True): 
        z[X(x)][Y(y)] = min(z[X(x)][Y(y)], 1 + min(z[X(x+1)][Y(y)], z[X(x)][Y(y+1)]))
    m = z.max() - z.std()
    z = list(map(tuple, np.argwhere(z > m)))
    return ((pt[0] + x_min - 1, pt[1] + y_min - 1) for pt in (z[0], z[-1])) 

# Check Version
if not sys.version_info >= (3, 10):
    print('Requires Python3.10 or newer')
    sys.exit(1)

# Load Project Configuration
parser = argparse.ArgumentParser()
parser.add_argument('path', help='path to project.yaml')
options = parser.parse_args()

with open(options.path, 'r') as io:
    config = yaml.safe_load(io)

# Convert units to mm
try:
    for item in [('model','layer','thickness'),
                ('model','bounds','max-edge'),
                ('model','bounds','min-dimension'),
                ('align','radius'),
                ('svg','stroke-width')]:
        match item:
            case [a]:
                config[a] = pint.Quantity(config[a]).to('mm').magnitude
            case [a, b]:
                config[a][b] = pint.Quantity(config[a][b]).to('mm').magnitude
            case [a, b, c]:
                config[a][b][c] = pint.Quantity(config[a][b][c]).to('mm').magnitude
            case _:
                raise Exception('developer error - config value more than 3 levels deep')
except Exception as e:
    print(f'Error while normalizing configuration values to mm: {e}')
    sys.exit(1)

# Make or validate project directory
workspace = config['workspace']
if os.path.exists(workspace):
    if not os.path.isdir(workspace):
        print(f'ERROR: Project workspace "{workspace}" exists but is not a directory')
        sys.exit(1)
else:
    os.makedirs(workspace, exist_ok=True)

# Check data exists or download
data_path = os.path.join(workspace, 'data.tiff')
if not os.path.isfile(data_path):
    print('Downloading data...')
    src = config['data']
    url = f'https://portal.opentopography.org/API/globaldem?demtype={src["demtype"]}&outputFormat=GTiff&API_Key={src["api-key"]}'
    url += api_bounds(config['region'])
    response = requests.get(url)
    if not response.ok:
        print(f'ERROR: Failed to download topographic data - {response.reason}')
        sys.exit(1)
    with open(data_path, 'wb') as io:
        io.write(response.content)
else:
    print('Using cached data...')

# Load topographic data & validate region is inside the data bounding box
data = geotiff.GeoTiff(data_path)

if not region_in_bbox(config['region'], data):
    print(f'The region {config["region"]} is not fully contained in the data bounding box.')
    print(f'Remove the data file {data_path} and rerun {sys.argv[0]}.')
    sys.exit(1)

# Setup extracting the data
max_edge = config['model']['bounds']['max-edge']
min_dimension = config['model']['bounds']['min-dimension']
thickness = config['model']['layer']['thickness']
pt0 = (config['region']['west'], config['region']['north'])
pt1 = (config['region']['east'], config['region']['south'])
ll_box = [pt0, pt1]
elevation = np.array(data.read_box(ll_box)).transpose()

# Project the coordinates
transformer = Transformer.from_crs(data.crs_code, config['data']['projection'], always_xy=True)
bbox = list(transformer.itransform(ll_box))
lon_distance, lat_distance = (abs(bbox[0][0] - bbox[1][0]), abs(bbox[0][1] - bbox[1][1]))
z_distance = elevation.max() - elevation.min()

# base xy scaling on largest lat/lon dimension
xy_scale            = max(lon_distance, lat_distance) / max_edge   # real-m/scale-mm
z_offset            = elevation.min()
layer_count         = config['model']['layer']['count']
layer_count         = int(round((elevation.max() - z_offset) / xy_scale / thickness)) if layer_count == 0 else layer_count
z_step              = z_distance / layer_count
z_scale             = z_distance / (layer_count * thickness)

# compute filter for tiny pieces
xy_pixels           = max(elevation.shape)                         # number of elevation blocks on the longer edge
xy_mm_per_pixel     = max_edge / xy_pixels                         # scale-mm/pixel
xy_filter_pixels    = min_dimension / xy_mm_per_pixel              # pixels

print(f'''Using {xy_scale:f} real-meters/scale-mm for xy
  {z_scale:f} real-meters/layer-mm for z
  {layer_count} layers''')

# Create raw layer bitmaps with 0.0 boarder
frame = np.zeros(tuple(i + 2 for i in elevation.shape), dtype=int)
layers = [frame.copy() for i in range(layer_count + 1)]

print(f'Scanning topology to form layers')
for lon_index, row in enumerate(elevation):
    for lat_index, z in enumerate(row):
        layer = int(math.floor((z - z_offset)/z_step))
        for index in range(layer + 1):
            layers[index][lon_index + 1][lat_index + 1] = 1.0

# In each layer, 0 = not in layer, 1 = in layer
degree = config['contours']['degree']
trace = {1: trace_linear, 2: trace_quadratic, 3: trace_cubic}[degree]
viewbox = svg.ViewBoxSpec(0, 0, *elevation.shape)
dimensions = tuple(f'{i*xy_mm_per_pixel}mm' for i in elevation.shape)
align = set()

# Iterate over each layer and
#   1. find contours in the layer
#   2. eliminate small islands
#   3. trace the contour
#   4. check if existing alignment points intersect island or add new alignment
#   5. Draw all alignment marks
marks = []
composite = []
for index, layer in enumerate(reversed(layers)):
    print(f'Finding contours in layer {index} of {len(layers)}')
    elements = []    
    # contours returns pairs of lists (center-of-edge, corner-of-edge) for each connected set of 'in-layer' pixels
    for (edge, center, pixels) in contours(layer):
        (x_min, y_min), (x_max, y_max) = bounding_box(pixels)
        if (x_max - x_min) < xy_filter_pixels or (y_max - y_min) < xy_filter_pixels:
            continue
        # Choose contour type, convert to complex numbers, pad for contour degree
        contour = {'corner': edge, 'center': center}[config['contours']['point-on-edge']]
        contour = contour[:-1] + contour[0:degree]
        # Trace path and use configuration to set stroke color and wid
        elements += [trace(config, contour)]
        # Draw alignment marks
        interior = set(find_interior(edge))
        if len(align.intersection(interior)) == 0:
            align.update(interior)
            locations = locate_alignment(interior)
            marks += [svg.Circle(
                cx = i[0], cy = i[1], r = config['align']['radius']/xy_mm_per_pixel,
                fill = 'none',
                stroke = config['align']['color'],
                stroke_width = config['svg']['stroke-width'],
            ) for i in locations]

    # provided there is at least one path, write an svg file
    if len(elements) > 0:
        filename = os.path.join(workspace, f'layer-{index:03d}.svg')
        image = svg.SVG(
            viewBox = viewbox,
            width = dimensions[0],
            height = dimensions[1],
            elements = elements + marks,
        )
        with open(filename, 'w') as io:
            io.write(str(image))
        print(f'Wrote SVG: {filename}')
        composite += elements
if len(composite) > 0:
    filename = os.path.join(workspace, f'composite.svg')
    image = svg.SVG(
        viewBox = viewbox,
        width = dimensions[0],
        height = dimensions[1],
        elements = composite + marks,
    )
    with open(filename, 'w') as io:
        io.write(str(image))
    print(f'Wrote SVG: {filename}')

