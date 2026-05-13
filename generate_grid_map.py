#!/usr/bin/env python3
"""
Convert habitat JSON records to OSGB 10km grid squares and count unique selected habitat codes.
Generates JSON file for the Leaflet map visualization.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from collections import defaultdict

try:
    from pyproj import Proj, transform
except ImportError:
    print("Installing pyproj...")
    import subprocess
    import sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyproj"])
    from pyproj import Proj, transform


def latlong_to_osgb(lat: float, lon: float) -> Tuple[int, int]:
    """
    Convert WGS84 latitude/longitude to OSGB36 easting/northing coordinates.
    
    Args:
        lat: Latitude in WGS84
        lon: Longitude in WGS84
        
    Returns:
        Tuple of (easting, northing) in OSGB36 coordinates
    """
    from pyproj import CRS, Transformer
    
    # Define coordinate systems
    wgs84 = CRS.from_epsg(4326)  # WGS84
    osgb36 = CRS.from_epsg(27700)  # OSGB36
    
    # Create transformer
    transformer = Transformer.from_crs(wgs84, osgb36, always_xy=True)
    
    # Transform coordinates
    easting, northing = transformer.transform(lon, lat)
    
    return int(easting), int(northing)


def get_grid_square(easting: int, northing: int, grid_size: int = 10000) -> Tuple[int, int]:
    """
    Get the 10km grid square coordinates for a given easting/northing.
    
    Args:
        easting: OSGB easting coordinate
        northing: OSGB northing coordinate
        grid_size: Grid size in meters (default 10000 for 10km)
        
    Returns:
        Tuple of (grid_easting, grid_northing) representing the lower-left corner
    """
    grid_easting = (easting // grid_size) * grid_size
    grid_northing = (northing // grid_size) * grid_size
    return grid_easting, grid_northing


def load_habitat_records(data_dir: str = "data") -> List[Dict]:
    """
    Load all habitat JSON records from a folder.

    Args:
        data_dir: Folder containing habitat JSON files

    Returns:
        List of habitat record dictionaries
    """
    data_path = Path(data_dir)
    if not data_path.exists():
        print(f"Data folder {data_dir} not found.")
        return []

    records = []
    json_files = sorted(data_path.glob("**/*.json"))
    print(f"Loading habitat files from {data_dir}...")
    print(f"Found {len(json_files)} JSON file(s)")

    for file_path in json_files:
        try:
            with file_path.open("r", encoding="utf-8") as file_handle:
                record = json.load(file_handle)
            if isinstance(record, dict):
                record["_source_file"] = str(file_path)
                records.append(record)
            else:
                print(f"  Skipping {file_path.name}: expected an object at top level")
        except Exception as error:
            print(f"  Error loading {file_path.name}: {error}")

    return records


def habitat_records_to_grid_data(records: List[Dict]) -> Dict:
    """
    Convert habitat records to OSGB grid squares with unique selected habitat code counts.
    
    Args:
        records: List of habitat record dictionaries
        
    Returns:
        Dictionary containing grid squares with unique selected habitat code counts
    """
    grid_codes = defaultdict(set)
    grid_code_names = defaultdict(dict)  # Maps grid_key -> {code: name}

    print(f"Converting {len(records)} habitat record(s) to OSGB grid...")

    for record in records:
        try:
            lat = record["lat"]
            lon = record["long"]
            selected_code = record.get("selected_habitat_code")
            selected_name = record.get("selected_habitat_name", "")
            source_file = record.get("_source_file", "unknown")

            if not selected_code:
                print(f"  Skipping {source_file}: missing selected_habitat_code")
                continue

            easting, northing = latlong_to_osgb(lat, lon)
            grid_e, grid_n = get_grid_square(easting, northing)
            grid_key = (grid_e, grid_n)

            grid_codes[grid_key].add(selected_code)
            grid_code_names[grid_key][selected_code] = selected_name

            print(
                f"  {Path(source_file).name}: ({lat:.4f}, {lon:.4f}) → OSGB ({easting}, {northing}) → Grid ({grid_e}, {grid_n}) → Code {selected_code}"
            )
        except Exception as e:
            source_file = record.get("_source_file", "unknown")
            print(f"  Error converting {source_file}: {e}")
    
    # Convert to list format for JSON
    grid_data = []
    for (easting, northing), codes in grid_codes.items():
        code_objects = [
            {"code": code, "name": grid_code_names[(easting, northing)].get(code, "")}
            for code in sorted(codes)
        ]
        grid_data.append({
            "gridRef": f"{easting}_{northing}",
            "easting": easting,
            "northing": northing,
            "value": len(codes),
            "selected_habitat_codes": code_objects
        })
    
    # Sort by easting then northing for consistent ordering
    grid_data.sort(key=lambda x: (x["easting"], x["northing"]))
    
    return grid_data


def main():
    """Main function for habitat data."""

    records = load_habitat_records('data')
    if not records:
        print("No habitat JSON records found in data/")
        return None
    
    print()
    print("=" * 60)
    print("OSGB 10km Habitat Grid Map Generator")
    print("=" * 60)
    print()
    
    # Convert habitat records to grid data
    grid_data = habitat_records_to_grid_data(records)
    
    print()
    print(f"Generated {len(grid_data)} grid squares")
    print(f"Total unique selected habitat codes: {sum(item['value'] for item in grid_data)}")
    print()
    
    # Save to JavaScript file so map.html can load the data directly
    js_output_file = "grid_data.js"
    with open(js_output_file, 'w', encoding='utf-8') as f:
        f.write("window.GRID_DATA = ")
        json.dump(grid_data, f, indent=2)
        f.write(";\n")

    print(f"✓ Saved to {js_output_file}")
    
    # Print summary
    print()
    print("Grid Summary:")
    print("-" * 60)
    for item in sorted(grid_data, key=lambda x: x['value'], reverse=True)[:10]:
        print(f"  Grid ({item['easting']}, {item['northing']}): {item['value']} unique habitat code(s)")
        codes = [entry.get('code', '') for entry in item['selected_habitat_codes']]
        print(f"    Codes: {', '.join(codes)}")
    
    return grid_data


if __name__ == "__main__":
    main()
