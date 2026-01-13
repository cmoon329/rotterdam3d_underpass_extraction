import argparse
import sys
import json
import underpass_detection

def main():
    parser = argparse.ArgumentParser(description="Detect buildings with underpasses")

    parser.add_argument("inputfile", help="Input cityjson file (required)")
    parser.add_argument("--eps", type=float, default=1e-8, help="Minimum difference between roof and ground areas to consider an underpass")

    args = parser.parse_args()

    try:
        with open(args.inputfile) as f:
            data = json.load(f)
    except Exception as e:
        print(e)
        sys.exit()

    # 1) Create lists of roofs and grounds per city object
    obj_roofs, roof_bounds = underpass_detection.roof_boundaries(data)
    obj_grounds, ground_bounds = underpass_detection.ground_boundaries(data)

    # 2) Translate vertex coordinates from indices
    v_coords = underpass_detection.vertex_idx_to_coords(data)

    # 3) Get boundary coordinates
    roof_coords = underpass_detection.boundary_idx_to_coords(roof_bounds, v_coords)
    ground_coords = underpass_detection.boundary_idx_to_coords(ground_bounds, v_coords)

    # 4) Generate wkt strings of roof/ground surfaces and output a wkt file for visualization
    ground_wkts = underpass_detection.write_wkt_polygon(ground_coords, 'ground_pre_union.wkt')
    roof_wkts = underpass_detection.write_wkt_polygon(roof_coords, 'roof_pre_union.wkt')

    # 5) Merge roof/ground surfaces and calculate area for each City Object
    obj_roof_union_wkts, obj_roof_area = underpass_detection.cal_area(obj_roofs, roof_wkts, 'roof_union.wkt')
    obj_ground_union_wkts, obj_ground_area = underpass_detection.cal_area(obj_grounds, ground_wkts, 'ground_union.wkt')

    # 6) Calculate the difference between roof and ground area and identify City Objects with underpasses
    eps = args.eps
    underpass_obj_ids, only_roof_obj_ids = underpass_detection.diff_area(eps, obj_roof_area, obj_ground_area, obj_roof_union_wkts, obj_ground_union_wkts, f'underpass_obj_eps_{eps}.wkt')

    print('<City Object IDs with Underpass>')
    for obj in underpass_obj_ids:
        print(obj)

    # print(f'\nonly_roof_obj_ids\n{only_roof_obj_ids}')

if __name__ == "__main__":
    main()
