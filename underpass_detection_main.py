import argparse
import sys
import json
import underpass_detection_ocs

def main():
    parser = argparse.ArgumentParser(description="Detect buildings with underpasses")

    parser.add_argument("inputfile", help="Input cityjson file (required)")

    args = parser.parse_args()

    try:
        with open(args.inputfile) as f:
            data = json.load(f)
    except Exception as e:
        print(e)
        sys.exit()

    # 1) Create lists of outer ceiling surfaces per city object
    obj_ocs, ocs_bounds = underpass_detection_ocs.ocs_boundaries(data)

    # 2) Translate vertex coordinates from indices
    v_coords = underpass_detection_ocs.vertex_idx_to_coords(data)

    # 3) Get boundary coordinates
    ocs_bounds_coords = underpass_detection_ocs.boundary_idx_to_coords(ocs_bounds, v_coords)

    # 4) Generate a shp file of underpass surfaces and area
    underpass_detection_ocs.output_shp(obj_ocs, ocs_bounds_coords, 'data/underpass')


if __name__ == "__main__":
    main()
