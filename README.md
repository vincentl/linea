![Image of a laser cut topographic map of Yosemite Valley, USA](https://github.com/vincentl/linea/blob/main/resources/yosemite.png)

# linea - Geographic Contour Line Generator

**linea** is a prototype Python3 program for generating contour line SVG files suitable for laser cutting layers that stack to create an 3D topographic map. Topographic data is downloaded from [OpenTopography](https://opentopography.org/) and processed to sort the data into layers, identify connected areas in each layer, and form smooth SVG tracing paths.

*Important*: `linea` is a free and open source prototype with limited testing. Using `linea` requires some familiarity with running Python3 programs. Using the resulting SVG files to create 3D topographic maps requires experience with safely operating a laser cutter. If you experience any issues with `linea` or have feature suggestions, please open a [Github Issue](https://github.com/vincentl/linea/issues/new).

# Contributing

Open a [Github Pull Request](https://github.com/vincentl/linea/pulls) to add a new example configuration file, propose improvements or new features, or correct an issue. All contributions will be licensed according to the [LICENSE](LICENSE) file in this repository.

# Setup

Running `linea` requires:
- An OpenTopography API key
  - [Register](https://portal.opentopography.org/newUser) for an account
  - Log into your account and make note of your API key
- Python3, version 3.10 or newer
  - Use your preferred operating system package manager or direct [download](https://www.python.org/downloads/) to get the latest version of Python3
- Several Python3 modules
  - The [requirements.txt](requirements.txt) file lists the needed modules. To use a virtual environment with these modules
  ```bash
  python3 -m venv /path/to/environment
  . /path/to/environment/bin/activate
  pip install -r requirements.txt
  ```
  - **Note**: If you see an error similar to `AttributeError: module 'svg' has no attribute 'Rect'` when running `linea`, force a reinstall of svg.py with
  ```bash
  pip install -I svg.py
  ```

# Tutorial

The steps for creating a 3D topographic map with `linea` are:
1. Identify the latitude and longitude boundaries for the desired region
2. Create a configuration file
3. Run `linea`
4. Review the resulting SVG files and modify as needed
5. Cut
6. Assembly

This tutorial will demonstrate how to use `linea` to create a 3D map of Yosemite Valley in California.

## Region Boundaries

Use a map service such as [Google Maps](https://www.google.com/maps) to locate boundaries for the map region. `linea` requires a rectangular bounding box of four values: east and west longitude boundaries and north and south latitude boundaries. Consult the map service documentation to learn how to determine the latitude and longitude of points on the map.
For Yosemite Valley, this tutorial will use the bounding box
```yaml
  north: 37.769248
  west: -119.664105
  south: 37.705105
  east: -119.519888
```
Some map services do not provide a method to draw a bounding box, but [bboxfinder.com](http://bboxfinder.com) can be used to visualize a bounding box on [OpenStreetMap.org](https://openstreetmap.org) maps. To see the Yosemite Valley bounding box, go to 
* http://bboxfinder.com/#37.705105,-119.664105,37.769248,-119.519888

`linea` prints a similar URL during execution to enable users to verify the bounding box is correct.

## Configuration File

All the parameters for a `linea` project are contained in a [YAML](https://yaml.org) configuration file. This example file shows the parameters for the Yosemite example with brief YAML comments describing each entry. See the next section for more detailed descriptions of the parameters.

```yaml
project: Yosemite Valley, CA, USA  # Descriptive project name
workspace: yosemite                # directory path for intermediate and output files
region:                            # bounds define the region of interest
  north: 37.769248                 #   northern latitude
  west: -119.664105                #   western longitude
  south: 37.705105                 #   southern latitude
  east: -119.519888                #   easter longitude
data:                              # parameters for fetching data
  api-key: API_KEY                 #   API key from opentopography.org (32 hex characters or environment variable)
  demtype: SRTMGL1                 #   global data set - see https://opentopography.org/developers
  projection: EPSG:3857            #   map projection - see https://epsg.io - EPSG:3857
  downsample: 1                    #   [optional] - for integer n, use every nth elevation sample to reduce data
model:                             # parameters for the final model
  layer:                           #   layer parameters
    thickness: 3.175mm             #     thickness of material with units (such as mm or in)
    count: 12                      #     [optional] number of layers, otherwise computed using xy scale
  bounds:                          #   restrictions on part sizes
    max-edge: 7in                  #     maximum edge length of final model with units
    min-dimension: 2mm             #     eliminate parts with an x or y dimension less than min-dimension
contour:                           # parameters for converting elevation data into SVG cut paths
  point-on-edge: center            #   place Path control points at 'end' or 'center' of layer edge segments
  degree: 3                        #   degree of SVG curves (1 = lines, 2 = smooth, 3 = smoother)
  color: rgb(0,0,255)              #   color code for cut lines
align:                             # [optional] draw alignment holes
  color: rgb(0,224,244)            #   color code for alignment marks
  radius: 0.75mm                   #   radius for alignment holes
frame:                             # [optional] add a rounded corner frame around each layer
  color: rgb(0,224,0)              #   color code for the frame
  round:                           #   [optional] corner rounding parameters
    x: 4mm                         #     rounding radius in the x direction
    y: 4mm                         #     rounding radius in the y direction
shadow:                            # [optional] add outline of the layer above to help with alignment 
  color: rgb(255,0,0)              #   color for the above-layer outline
svg:                               # parameters for the SVG file
  stroke-width: 0.03125mm          #   set the stroke width for the layer outlines
```

### SVG Paths & Color Codes

`linea` creates an SVG file with following kinds of paths
* ___contour___: the cut lines 
* ___align___: optional circular holes to assist in aligning layers with an aid, such as a toothpick or skewer
* ___frame___: optional frames used to round the corners of layers extend to the boundary of the model 
* ___shadow___: optional feature to repeat the contour lines from the next higher level that can be engraved to help with alignment

To distinguish each SVG path type, the configuration file has a color field for each path type. Laser control software such as [LightBurn](https://docs.lightburnsoftware.com/LayerColors.html) uses color to assign an operation to paths. `linea` embeds the specified color string directly into the SVG, so any valid [SVG color](https://developer.mozilla.org/en-US/docs/Web/CSS/color_value) can be used.

### Detailed Configuration Parameter Documentations

* ___project___: an information field for describing the geographic region captured by the configuration file.
* ___workspace___: the path to a directory where `linea` will store download data, intermediate files, and the final output. The path will be created if it does not exist.
* ___region___: the key for a mapping of the four bounding box boundaries.
  * ___north___: northern latitude expressed in decimal form.
  * ___west___: western longitude expressed in decimal form.
  * ___south___: southern latitude expressed in decimal form.
  * ___east___: eastern longitude expressed in decimal form.
* ___data___: contains parameters for fetching and interpreting the elevation data.
  * ___api-key___: OpenTopography requires a per-user API key that is free to registered users. Register at 
[opentopography.org](https://opentopography.org). The API key may be stored directly in the configuration file for convenience, but API keys should not be shared. If the value does not look like an API key, `linea` assumes it is the name of environment variable that contains the API key.
  * ___demtype___: names the OpenTopography dataset to query. See the [developers](https://opentopography.org/developers) documentation for more details.
  * ___projection___: mapping the spherical earth to a flat surface is called projection and there are many options for projection. See [epsq.io](https://epsg.io) for a list of projections and what areas of the global each projection is best suited.
  * ___downsample___: optional integer value that reduces the number of elevation samples. Useful for large geographic areas or to create smoother contours.
* ___model___: parameters that determine the size of the final model
  * ___layer___: the layer parameters govern the vertical dimension of the model
    * ___thickness___: specify the thickness of the model material with units
    * ___count___: optional parameter. Set this parameter to an integer value to exaggerate the height of the model.
  * ___bounds___: specifies the size of the model.
    * ___max-edge___: determines the scale of the model. The longer of the North-South or East-West dimension is scaled to this size.
    * ___min-dimension___: is used to filter out tiny layer fragments. 
* ___contour___: required parameters for the cut paths.
  * ___point-on-edge___: either 'end' or 'center'. A smooth, continuous contour is created from short, discrete edges and this parameter determines if the end points or center of each segment is used in constructing contours.
  * ___degree___: the mathematical degree of the SVG Path segments. Straight lines are degree 1, smooth curves are degree 2, and the smoothest curves are degree 3.
  * ___color__: specify the cut path color
* ___align___: optional. Parameters for align holes.
  * ___color__: specify the align path color
  * ___radius___: radius of the alignment holes. Consider setting it the radius of a wooden toothpick or skewer that can be threaded through the alignment holes.
* ___frame___: optional. Parameters for the frame path.
  * ___color__: specify the frame path color
  * ___round___: optional. Parameters that control the amount of rounding on the frame corners.
    * ___x___: radius in the x direction.
    * ___y___: radius in the y direction.
* ___shadow___: optional. Parameters for shadow paths.
  * ___color__: specify the shadow path color
* ___svg___: parameters for SVG attributes
  * ___stroke-width___: set the width of paths in the SVG file. This typically does not affect cutting, but is important for visual inspection of the SVG before cutting.

## Run `linea`

After completing the steps in the **Setup** section and creating a configuration file, run `linea` with
```bash
 API_KEY=0123456789abcdef... python3 src/linea.py examples/yosemite.yaml
```
where `API_KEY` is the string value for the `api-key` field in the configuration file and the key `0123...` is a placeholder that must be replaced with the API key obtained during setup. If the API key is directly recorded in the configuration file, then the run line can simply begin with `python3`.

`linea` reports several items as output
```txt
Region: http://bboxfinder.com/#37.705105,-119.664105,37.769248,-119.519888
Downloading data...
Using 90.293380 real-meters/scale-mm for xy
  38.346457 real-meters/layer-mm for z
  12 layers
Data grid has shape (518, 230)
Scanning topology to form layers
Finding contours in layer 0 of 13
Finding contours in layer 1 of 13
Wrote SVG: yosemite/layer-001.svg
Finding contours in layer 2 of 13
Wrote SVG: yosemite/layer-002.svg
...
Wrote SVG: yosemite/layer-011.svg
Finding contours in layer 12 of 13
Wrote SVG: yosemite/layer-012.svg
Wrote SVG: yosemite/composite.svg
```
* Follow the bboxfinder URL to see the region `linea` is processing
* Scale parameters are reported for the horizontal xy-plane and the vertical z dimension
  * If the configuration file specifies the number of layers, the xy and z scales will most likely be different
* Some times the first layer or layers will not produce an output file. This is because all the elements in the layer are smaller than the `min-dimensions` parameter.
* The `layer-###.svg` files contain the paths for a single layer of the final model. Optional frame and alignment holes are included.
* The `composite.svg` file contains all the layers as individual SVG groups plus the optional frame and alignment holes. It may be easier to edit alignment holes using this file and then exporting separate cut layers.

## Review Layers

There are many options for viewing SVG files, including most modern web browsers. To make any changes, an SVG editor is needed. [Inkscape](https://inkscape.org) is a powerful Free and Open Source Software project that is an excellent choice for editing SVG files. Open the `composite.svg` files to get a sense of the overall model. 

This image is a portion of the `yosemite/composite.svg` created in the sample project.
![Image showing contours and alignment holes](https://github.com/vincentl/linea/blob/main/resources/yosemite-composite-zoom.png)
One alignment hole in cyan is visible near the top and the dense set of contour lines suggest rapid elevation changes.

### Items to consider when reviewing layers

Depending on which optional features are used for a project, consider the following when reviewing the model layers.

- Check for alignment holes that touch or cut through contour lines. `linea` attempts to put alignment holes in the center of the topmost layer in a stack, but if the layers are long and narrow or oddly shaped, the automatic placement might fail. You can choose to manually adjust the position of the hole in every layer or remove it from the upper layers. Alignment holes are not drawn for the top most part surrounding an alignment hole in the individual layer files so when assembly is compete, all the alignment holes are hidden.
- Check the radius of the rounded frame corners and how the frame corners intersect with each layer.
- Check for empty layers. `linea` starts with the designated layer count, but if the top layers contain only tiny parts that fall below the minimum part dimension, a layer could be empty. Either adjust the layer count or minimum dimensions to achieve the desired number of layers before finalizing a configuration.

## Cutting the Layers

The exact details for cutting layers will depending on the laser cutter and control software. This section of the tutorial covers the general steps that must be adapted for a specific laser cutter setup.

1. Configure the laser control software to use the appropriate settings for each feature. Alignment shadows should be lightly engraved and the other features configured for clean cuts for the model material. 

2. **⁘ Test Cut ⁘** Browse through the layer files and look for examples of the four main types of features in a model. Isolate small samples and complete a test cut.
  - Contour line - check for clean cuts with minimal burn marks
  - Alignment hole - check that the alignment aid (tooth pick, skewer, etc) fits in the hole
  - Layer alignment shadow line - check the line is visible with minimal burn marks
  - Rounded frame corner - check that the dimension are aesthetically pleasing

3. Work through each layer and cut all the parts
  - `linea` makes no attempt to efficiently layout parts, instead the parts are positioned according to the geography of the region. Manually positioning the parts on each layer can significantly reduce material waste. Be careful to move all the features (contour, alignment holes and shadows, and frame corners) together.
  - Keep track of parts! Some models will produce many individual parts per layer and final assembly can turn into a gigantic puzzle.

## Final Assembly

Start with the bottom layer, which is the layer with the largest numeric suffix, and glue the parts from the layer above into position. Aligning parts
- ***Alignment Holes*** - If the `align` option is configured, simply match up the holes either visually or using a aid such as a toothpick or skewer. Some layers will have two or more holes and will be automatically oriented with all the holes are aligned. When a part has a single hole, use the `composite.svg` file to help visually orient the part.
- ***Alignment Shadows*** - If the `shadow` options is configured, each part should sit exactly on the shadow line.
- ***Paper templates*** - Another option for alignment is to configure alignment shadows and cut both the contours and shadow lines from a layer file on scrap paper. Then the outer edge of each paper cutout will align with a part on one layer and the inner hole on the paper cutout will align with the edges of a part from the layer above.

# Algorithms

This section describes the algorithms `linea` uses for each major step in producing layer files from topological data. 

## XYZ Scales

The latitude and longitude boundaries are used to fetch the model data and then it is transformed according to the model projection. A model XY-scaling factor is computed by taking the largest bounding box dimension of the transformed region divided by the maximum model scale. This gives the ratio between geographic meters and model millimeters.

For the vertical or Z dimension, either the layer count is specified in the configuration file or the XY-scale is used with the difference between the minimum and maximum elevation to compute a layer count. Given the layer count, the total elevation represented in the model (the maximum minus minimum elevation) is divided by the number of layers to compute the geographic elevation meters represented by one layer, which is called the Z-step.

## Layer Slice

Elevation data records the elevation at regularly spaced points in a grid. Layers start out as grids of the same shape with all white pixels. Using the Z-step and the minimum elevation, `linea` simply computes which layer each elevation point maps into using 
```math
\text{layer} = \left\lfloor\frac{\text{elevation} - \text{minimum elevation}}{\text{Z-step}}\right\rfloor
```
The corresponding pixel in the computed layer is colored blacked and the same pixel in every layer below the computed layer is colored black.

The end result is that each layer is like a black-white bitmap image with a white background and each black region describes one part to cut for the model.

## Find Contours

`linea` must take the layer bitmaps and convert each black region into an SVG path appropriate for laser cutting. The following algorithm is based on ideas presented in [_A Parallel Algorithm for Dilated Contour Extraction from Bilevel Images_](https://arxiv.org/pdf/cs/0001024).
- Scan the input bitmap and identify all edges between white and black pixels
- Start with an arbitrary edge and follow connected edges
- Remove each visited edge from future consideration
- When a path visits the starting edge, emit a contour and start again

The sequence of edges around a contour are represented with one point per edge.
The `point-on-edge` configuration parameter selects either the end or center of the edges.

## Continuous Contour

An SVG path is not a sequence of points, but a collection of mathematical curves between points. Given a sequence of contour points, `linea` links the points together using lines (degree 1), quadratic curves (degree 2), or cubic curves (degree 3), depending on the configuration `contour:degree` value.

There are many descriptions of this process from different viewpoints and for a wide range of applications. The paper [_An Introduction to B-Spline Curves_](https://github.com/vincentl/linea/blob/main/resources/An_Introduction_to_B-Spline_Curves.pdf) describes an approach developed by Dr. Lyle Ramshaw at DEC Systems Research Center using polar forms. Following this approach, `tracing.py` contains functions `bs_to_bz2` and `bs_to_bz3` to compute the appropriate SVG Bezier curves from a sequence of points. Some care is required to patch together the start and end of the path to form one continuous part boundary.

## Alignment Holes

The bottom layer of a model is solid wood and the surface of the model consists of isolated shapes. `linea` places alignment holes below each of this top-most isolated shapes.

A grassfire transform is used to identify a point that is most distant from all boundary points and an alignment hole is centered at this point. If the top-most shape is oddly shaped for very thin, it might not fully cover the alignment hole.