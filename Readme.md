# linea - Geographic Contour Line Generator

**linea** is a prototype Python3 program for generating contour line SVG files suitable for laser cutting layers that stack to create an 3D topographic map. Topographic data is downloaded from [OpenTopography](https://opentopography.org/) and processed to sort the data into layers, identify connected areas in each layer, and form smooth SVG tracing paths.

*Important*: `linea` is a free and open source prototype with limited testing. Using `linea` requires some familiarity with Python3 and using the resulting SVG files to create 3D topographic maps requires experience with safely operating a laser cutter. If you experience any issues with `linea` or have feature suggestions, please open a (Github Issue)[https://github.com/vincentl/linea/issues/new].

# Setup

Getting ready to run `linea` requires:
- An OpenTopography API key
  - (Register)[https://portal.opentopography.org/newUser] for an account
  - Log into your account and make note of your API key
- Python3, version 3.10 or newer
  - Use your preferred operating system package manager or direct (download)[https://www.python.org/downloads/] to get the latest version of Python3
- Several Python3 modules
  - The `requirements.txt` file lists the needed modules. Install these modules. For example, to use a virtual environment with these modules
  ```bash
  python3 -m venv /path/to/environment
  . /path/to/environment/bin/activate
  pip install -r requirements.txt
  ```

# Tutorial

Creating a 3D topographic map with `linea` follows several steps:
1. Identify the latitude and longitude boundaries for the desired region
2. Create a configuration file
3. Run `linea`
4. Review the resulting SVG files and modify if needed
5. Cut & assemble

## Region Boundaries

## Configuration File

## Running `linea`

## Review the Layers

## Cut & Final Assembly
