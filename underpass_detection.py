import shapely
from shapely import wkt as shapely_wkt
import pandas as pd
import geopandas as gpd
import csv
import json
import os


# 1) Create lists of outer ceiling surfaces per city object
def ocs_boundaries(input_data):
    """
    Function that returns dictionaries of outer ceiling surfaces and their boundaries from CityJSON data

    Input:
        Loaded CityJSON data
    Output:
        obj_ocs: A dictionary mapping City Object IDs to their associated OuterCeilingSurface ID lists
                   {city_object_id: [outer_ceiling_surface_id, ...]}
        ocs_bounds: A dictionary mapping OuterCeilingSurface IDs to their boundaries
                     {outer_ceiling_surface_id: [[[vertex_index_1, vertex_index_2, ...]]]}
                     The depth of the boundaries array depends on its geometry type
                     - Solid -> 4
                     - MultiSurface --> 3
    """
    cityobjs = list(input_data['CityObjects'].keys())

    obj_ocs = {}    # {city_object_id: [outer_ceiling_surface_id, ...]}
    ocs_bounds = {}  # {outer_ceiling_surface_id: [[[vertex_index_1, vertex_index_2, ...]]]}

    for i in cityobjs:
        if len(input_data['CityObjects'][i]['geometry']) == 0:
            continue
        else:
            type = input_data['CityObjects'][i]['geometry'][0]['type']
            boundaries = input_data['CityObjects'][i]['geometry'][0]['boundaries']
            smt_values = input_data['CityObjects'][i]['geometry'][0]['semantics']['values']
            smt_surfaces = input_data['CityObjects'][i]['geometry'][0]['semantics']['surfaces']

            ocs_num = {}  # {outer_ceiling_surface_num: outer_ceiling_surface_id}
            for num, surf in enumerate(smt_surfaces):
                if surf['type'] == 'OuterCeilingSurface':
                    ocs_num[num] = surf['id']

            obj_ocs[i] = list(ocs_num.values())

            ocs_val = {}  # {outer_ceiling_surface_id: [value_1, value_2, ...] }
            for num in list(ocs_num.keys()):
                vals = []
                if type == 'Solid':
                    for id, val in enumerate(smt_values[0]):
                        if val == num:
                            vals.append(id)
                elif type == 'MultiSurface':
                    for id, val in enumerate(smt_values):
                        if val == num:
                            vals.append(id)
                ocs_val[ocs_num[num]] = vals

            for id in list(ocs_val.keys()):
                bounds = []
                for val in ocs_val[id]:
                    if type == 'Solid':  # Array depth == 4
                        bounds.append(boundaries[0][val])
                    elif (type == 'MultiSurface'):  # Array depth == 3
                        bounds.append(boundaries[val])
                    else:
                        print(f'geometry type error : {type}')  # Returns an error massage if a geometry type is something else
                ocs_bounds[id] = bounds

    return obj_ocs, ocs_bounds


# 2) Translate vertex coordinates from indices
def vertex_idx_to_coords(input_data):
    """
    Function that returns a dictionary of vertex indices and their x, y coordinates from CityJSON data

    Input:
        Loaded CityJSON data
    Output:
        v_coords: A dictionary mapping vertex indices to their x, y coordinates
                  (Coordinate translating formula: https://www.cityjson.org/specs/1.0.0/#transform-object)
    """
    scale = input_data['transform']['scale']
    translate = input_data['transform']['translate']
    vertices = input_data['vertices']

    v_coords = {}  # {vertex_idx: [x_coord, y_coord]}
    for i in range(0, len(vertices)):
        v_xy = []
        v_x = (vertices[i][0] * scale[0]) + translate[0]
        v_y = (vertices[i][1] * scale[1]) + translate[1]

        v_xy.append(v_x)
        v_xy.append(v_y)

        v_coords[i] = v_xy

    return v_coords


# 3) Get boundary coordinates
def boundary_idx_to_coords(ocs_bounds, v_coords):
    """
    Function that returns a dictionary of outer ceiling surface IDs and their boundary coordinates

    Input:
        ocs_bounds: A dictionary of outer ceiling surface IDs and their boundary vertex indices
        v_coords: A dictionary of vertex indices and their x, y coordinates
    Output:
        ocs_bounds_coords: A dictionary of outer ceiling surface IDs and their boundary coordinates
                           {surface_id: [[[(v1_x, v1_y), (v2_x, v2_y), ...]]]}
    """
    ocs_bounds_coords = {}  # {surface_id: [[[(v1_x, v1_y), (v2_x, v2_y), ...]]]}

    for uuid, bound in ocs_bounds.items():
        bound_coords =[]
        for face in bound:
            face_coords = []
            for ring in face:
                ring_coords =[]
                for v in ring:
                    ring_coords.append(tuple(v_coords[v]))
                face_coords.append(ring_coords)
            bound_coords.append(face_coords)
        ocs_bounds_coords[uuid] = bound_coords

    return ocs_bounds_coords


# 4) Output a shp file of outer ceiling surfaces for visualization
def output_shp(obj_ocs, ocs_bounds_coords, output_file_nm):
    """
    Function that outputs a shph file of outer ceiling surfce a for visualization

    Input:
        obj_ocs: A dictionary of City Objects and their outer ceiling surface IDs
        ocs_bounds_coords: A dictionary of outer ceiling surface IDs and their boundary cooridnates
        output_file_nm: Output shp file name
    Output:
        output_shp: A SHP file to visualize each outer ceiling surface
    """
    ocs_bounds_wkts = {}  # {surface_id: '(MULTI)POLYGON((v1_x v1_y, v2_x v2_y, ...))}

    for uuid, bound in ocs_bounds_coords.items():
        polygon_strs = []
        for face in bound:
            ring_strs = []
            for ring in face:
                if ring[0] != ring[-1]:  # Close polygon
                    ring.append(ring[0])
                coords_list = []
                for coord in ring:
                    coords_list.append(f'{coord[0]} {coord[1]}')
                coords = ', '.join(coords_list)
                ring_strs.append(f'({coords})')
            face_str = f"({', '.join(ring_strs)})"
            polygon_strs.append(face_str)

        if len(polygon_strs) == 1:
            wkt = f'POLYGON{polygon_strs[0]}'
        else:
            all_faces = ', '.join(polygon_strs)
            wkt = f'MULTIPOLYGON({all_faces})'

        ocs_bounds_wkts[uuid] = wkt

    # write to csv first
    output_file_path = f'{output_file_nm}.csv'
    folder_path = os.path.dirname(output_file_path)
    if folder_path and not os.path.exists(folder_path):
        os.makedirs(folder_path)

    with open(output_file_path, 'w', newline='') as output_csv:
        writer = csv.writer(output_csv)
        writer.writerow(['uuid', 'area', 'geom'])

        for uuid, surfs in obj_ocs.items():
            # if City Object has no outer ceiling surfaces, skip
            if len(surfs) == 0:
                continue

            geom = None
            # Case 1) A single outer ceiling surface city object
            if len(surfs) == 1:
                geom = shapely_wkt.loads(ocs_bounds_wkts[surfs[0]])

            # Case 2) Multiple outer ceiling surfaces city object
            elif len(surfs) > 1:
                polys = []
                for i in range(0, len(surfs)):
                    poly = shapely_wkt.loads(ocs_bounds_wkts[surfs[i]])
                    polys.append(poly)

                geom = shapely.unary_union(polys)  # merge surfaces

            area = shapely.area(geom)

            writer.writerow([uuid, area, geom])

    # write to shp and remove the created csv file
    df = pd.read_csv(output_file_path)
    df['geom'] = df['geom'].apply(shapely_wkt.loads)
    gdf = gpd.GeoDataFrame(df, geometry=df['geom'], crs='epsg:28992')
    gdf = gdf.drop(columns=['geom'])
    gdf.to_file(f'{output_file_nm}.shp')

    if os.path.exists(output_file_path):
        os.remove(output_file_path)

    print('shp file created')

