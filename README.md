# OSGB 10km Grid Map

This project generates an interactive Leaflet map displaying OSGB 10km grid squares with color-coded data based on point counts.

## Files

- **map.html** - Interactive Leaflet map viewer
- **generate_grid_map.py** - Python script to convert lat/long points to OSGB grid squares
- **grid_data.js** - Generated browser-ready data file with grid square data (automatically created)
- **data/** - Folder of habitat JSON files used as input
- **.github/workflows/generate-map.yml** - GitHub Actions workflow to auto-generate map data

## How to Use

### Option 1: Run Locally

1. Install dependencies:
   ```bash
   pip install pyproj
   ```

2. Run the script (reads all habitat JSON files in `data/`):
   ```bash
   python generate_grid_map.py
   ```

3. Open `map.html` in your web browser

### Option 2: Use GitHub Actions

1. Put habitat JSON files into `data/` using this format:
   ```json
    {
       "image_file": "habitat_20260415T152601Z.jpg",
       "datetime": "2026-04-15T15:26:00+00:00",
       "lat": 53.41278246985077,
       "long": -1.5131156888662485,
       "selected_habitat_code": "g4",
       "selected_habitat_name": "Modified grassland"
    }
   ```

2. Push files under `data/` to GitHub
3. The workflow automatically:
    - Converts all habitat records to OSGB grid squares
    - Counts distinct selected habitat codes in each 10km square
   - Generates `grid_data.js`
   - Commits the updated map data back to the repo

4. Open `map.html` to view the updated map

## Input Data Format

Each file in `data/` should contain a single JSON object with:
- `lat`: WGS84 latitude (required)
- `long`: WGS84 longitude (required)
- `selected_habitat_code`: Selected habitat code used for distinct counting (required)
- `selected_habitat_name`: Human-readable habitat name (optional)

## Example Data

The repository includes a sample habitat record in `data/` to demonstrate the input format.

## Map Features

- **Interactive visualization**: Click any grid square to see the distinct habitat codes in that cell
- **Color coding**: Red (low values) → Yellow → Green (high values)
- **Zoom and pan**: Full Leaflet map controls
- **Legend**: Shows value ranges in bottom-right corner
- **Responsive**: Works on desktop and mobile browsers

## Coordinate System

- **Input**: WGS84 latitude/longitude
- **Processing**: Converted to OSGB36 (UK national grid)
- **Grid**: 10km × 10km squares aligned to the OSGB system
- **Output**: Grid data as JSON with easting/northing coordinates

## Customization

### Change color scheme
Edit the `getColor()` function in `map.html` to adjust the gradient

### Change grid size
Modify the `grid_size` parameter in `generate_grid_map.py` (default: 10000m = 10km)

### Adjust map center
Edit the initial view in `map.html`: `map.setView([54.5, -3.5], 6)`

## Workflow Triggers

The GitHub Actions workflow runs when:
- Files under `data/` are pushed or modified
- `generate_grid_map.py` is updated
- The workflow file itself changes
- Manual trigger via GitHub Actions UI

## Requirements

- Python 3.7+
- `pyproj` library (auto-installed by GitHub Actions)
- Modern web browser with JavaScript enabled
