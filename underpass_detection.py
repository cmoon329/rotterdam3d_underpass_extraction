import shapely
from shapely import wkt


# 1) Create lists of roofs and grounds per city object
def roof_boundaries(input_data):
    """
    Function that returns dictionaries of roof surfaces and their boundaries from CityJSON data

    Input:
        Loaded CityJSON data
    Output:
        obj_roofs: A dictionary mapping City Object IDs to their associated Roof Surface ID lists
                   {city_object_id: [roof_surface_id, ...]}
        roof_bounds: A dictionary mapping Roof Surface IDs to their boundaries
                     {roof_surface_id: [[[vertex_index_1, vertex_index_2, ...]]]}
                     The depth of the boundaries array depends on its geometry type
                     - Solid -> 4
                     - MultiSurface --> 3
    """
    cityobjs = list(input_data['CityObjects'].keys())

    obj_roofs = {}    # {city_object_id: [roof_surface_id, ...]}
    roof_bounds = {}  # {roof_surface_id: [[[vertex_index_1, vertex_index_2, ...]]]}

    for i in cityobjs:
        if len(input_data['CityObjects'][i]['geometry']) == 0:
            continue
        else:
            type = input_data['CityObjects'][i]['geometry'][0]['type']
            boundaries = input_data['CityObjects'][i]['geometry'][0]['boundaries']
            smt_values = input_data['CityObjects'][i]['geometry'][0]['semantics']['values']
            smt_surfaces = input_data['CityObjects'][i]['geometry'][0]['semantics']['surfaces']

            roof_num = {}  # {roof_surface_num: roof_surface_id}
            for num, surf in enumerate(smt_surfaces):
                # Consider 'RoofSurface' and 'OuterFloorSurface' as roof surface
                if (surf['type'] == 'RoofSurface') or (surf['type'] == 'OuterFloorSurface'):
                    roof_num[num] = surf['id']

            obj_roofs[i] = list(roof_num.values())

            roof_val = {}  # {roof_surface_id: [value_1, value_2, ...] }
            for num in list(roof_num.keys()):
                vals = []
                if type == 'Solid':
                    for id, val in enumerate(smt_values[0]):
                        if val == num:
                            vals.append(id)
                elif type == 'MultiSurface':
                    for id, val in enumerate(smt_values):
                        if val == num:
                            vals.append(id)
                roof_val[roof_num[num]] = vals

            for id in list(roof_val.keys()):
                bounds = []
                for val in roof_val[id]:
                    if type == 'Solid':  # Array depth == 4
                        bounds.append(boundaries[0][val])
                    elif (type == 'MultiSurface'):  # Array depth == 3
                        bounds.append(boundaries[val])
                    else:
                        print(f'geometry type error : {type}')  # Returns an error massage if a geometry type is something else
                roof_bounds[id] = bounds

    return obj_roofs, roof_bounds


def ground_boundaries(input_data):
    """
    Function that returns dictionaries of ground surfaces and their boundaries from CityJSON data

    Input:
        Loaded CityJSON data
    Output:
        obj_grounds: A dictionary mapping City Object IDs to their associated Ground Surface ID lists
                     {city_object_id: [ground_surface_id, ...]}
        ground_bounds: A dictionary mapping Ground Surface IDs to their boundaries
                       {ground_surface_id: [[[vertex_index_1, vertex_index_2, ...]]]}
                       The depth of the boundaries array depends on its geometry type
                       - Solid -> 4
                       - MultiSurface --> 3
    """
    cityobjs = list(input_data['CityObjects'].keys())

    obj_grounds = {}    # {city_object_id: [ground_surface_id, ...]}
    ground_bounds = {}  # {ground_surface_id: [[[vertex_index_1, vertex_index_2, ...]]]}

    for i in cityobjs:
        if len(input_data['CityObjects'][i]['geometry']) == 0:
            continue
        else:
            type = input_data['CityObjects'][i]['geometry'][0]['type']
            boundaries = input_data['CityObjects'][i]['geometry'][0]['boundaries']
            smt_values = input_data['CityObjects'][i]['geometry'][0]['semantics']['values']
            smt_surfaces = input_data['CityObjects'][i]['geometry'][0]['semantics']['surfaces']

            ground_num = {}  # {ground_surface_num: ground_surface_id}
            for num, surf in enumerate(smt_surfaces):
                # Consider 'GroundSurface' as ground surface
                if surf['type'] == 'GroundSurface':
                    ground_num[num] = surf['id']

            obj_grounds[i] = list(ground_num.values())

            ground_val = {}  # {ground_surface_id: [value_1, value_2, ...] }
            for num in list(ground_num.keys()):
                vals = []
                if type == 'Solid':
                    for id, val in enumerate(smt_values[0]):
                        if val == num:
                            vals.append(id)
                elif type == 'MultiSurface':
                    for id, val in enumerate(smt_values):
                        if val == num:
                            vals.append(id)
                ground_val[ground_num[num]] = vals

            for id in list(ground_val.keys()):
                bounds = []
                for val in ground_val[id]:
                    if type == 'Solid':   # Array depth == 4
                        bounds.append(boundaries[0][val])
                    elif type == 'MultiSurface':  # Array depth == 3
                        bounds.append(boundaries[val])
                    else:
                        print(f'geometry type error : {type}')  # Returns an error massage if a geometry type is something else
                ground_bounds[id] = bounds

    return obj_grounds, ground_bounds


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
def boundary_idx_to_coords(surf_bounds, v_coords):
    """
    Function that returns a dictionary of surface IDs and their boundary coordinates

    Input:
        surf_bounds: A dictionary of roof/ground surface IDs and their boundary vertex indices
        v_coords: A dictionary of vertex indices and their x, y coordinates
    Output:
        surf_bounds_coords: A dictionary of roof/ground surface IDs and their boundary coordinates
                       {surface_id: [[[(v1_x, v1_y), (v2_x, v2_y), ...]]]}
    """
    surf_bounds_coords = {}  # {surface_id: [[[(v1_x, v1_y), (v2_x, v2_y), ...]]]}

    for uuid, bound in surf_bounds.items():
        bound_coords =[]
        for face in bound:
            face_coords = []
            for ring in face:
                ring_coords =[]
                for v in ring:
                    ring_coords.append(tuple(v_coords[v]))
                face_coords.append(ring_coords)
            bound_coords.append(face_coords)
        surf_bounds_coords[uuid] = bound_coords

    return surf_bounds_coords


# 4) Generate wkt strings of roof/ground surfaces and output a wkt file for visualization
def write_wkt_polygon(surf_bounds_coords, output_file_nm):
    """
    Function that returns wkt strings of roof/groundsurfaces and outputs a wkt file for visualization

    Input:
        surf_bounds_coords: A dictionary of roof/ground surface IDs and their boundary cooridnates
        output_file_nm: Output wkt file name
    Output:
        surf_bounds_wkts: A dictionary mapping roof/ground surface IDs and their WKT strings
                          {surface_id: '(MULTI)POLYGON((v1_x v1_y, v2_x v2_y, ...))}
        output_wkt: A WKT file to visualize each roof/ground surfaces
    """
    surf_bounds_wkts = {}  # {surface_id: '(MULTI)POLYGON((v1_x v1_y, v2_x v2_y, ...))}

    with open(output_file_nm, 'w') as output_wkt:
        output_wkt.write('uuid; geom\n')

        for uuid, bound in surf_bounds_coords.items():
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

            output_wkt.write(f'{uuid}; {wkt}\n')

            surf_bounds_wkts[uuid] = wkt

    return surf_bounds_wkts


# 5) Merge roof/ground surfaces and calculate area for each City Object
def cal_area(obj_surfs, surf_bounds_wkts, output_file_nm):
    """
    Function that merges roof/ground surfaces and calculates area for each City Object,
    returns dictionaries of City Object IDs and surface area and of City Object IDs and surface WKTs,
    and output a WKT file of merged roof/ground surfaces for each City Objects

    Input:
        obj_surfs: A dictionary of City Objects and their roof/ground surface IDs
        surf_bounds_wkts: A dictionary of roof/ground surface IDs and their WKT strings
        output_file_nm: Output wkt file name
    Output:
        obj_surf_union_wkts: A dictionary mapping City Object IDs and their merged roof/ground surface's WKT
                             {city_object_id: (MULTI)POLYGON((v1_x v1_y, v2_x v2_y, ...))}
        obj_surf_area: A dictionary mapping City Object IDs and their roof/ground surface area
                       {city_object_id: area(np.float64)}
        output_wkt: A WKT file to visualize merged roof/ground surfaces for each City Objects
    """
    obj_surf_union_wkts = {}  # {city_object_id: (MULTI)POLYGON ((v1_x v1y, v2_x v2_y, ...))}
    obj_surf_area = {}   # {city_object_id: area(np.float64)}

    with open(output_file_nm, 'w') as output_wkt:
        output_wkt.write('uuid; geom\n')

        for uuid, surfs in obj_surfs.items():
            # Case 1) A single roof/ground surface city object
            if len(surfs) == 1:
                poly = wkt.loads(surf_bounds_wkts[surfs[0]])
                area = shapely.area(poly)

                obj_surf_union_wkts[uuid] = poly
                obj_surf_area[uuid] = area

                output_wkt.write(f'{uuid}; {poly}\n')

            # Case 2) Multiple roof/ground surfaces city object
            elif len(surfs) > 1:
                polys = []
                for i in range(0, len(surfs)):
                    poly = wkt.loads(surf_bounds_wkts[surfs[i]])
                    polys.append(poly)

                union_polys = shapely.unary_union(polys)  # merge surfaces
                union_area = shapely.area(union_polys)

                obj_surf_union_wkts[uuid] = union_polys
                obj_surf_area[uuid] = union_area

                output_wkt.write(f'{uuid}; {union_polys}\n')

    return obj_surf_union_wkts, obj_surf_area


# 6) Calculate the difference between roof and ground area and identify City Objects with underpasses
def diff_area(eps, obj_roof_area, obj_ground_area, obj_roof_union_wkts, obj_ground_union_wkts, output_file_nm):
    """
    Function that calculates the difference between roof and ground area for each City Object
    and returns City Object IDs with underpasses.
    For testing purpose, it also returns City Object IDs that have only roof surfaces with no ground surfaces)

    Input:
        eps: Minimum difference between roof and ground areas to consider an underpass
             -> default: 1e-8
        obj_roof_area: A dictionary of City Object IDs and their roof area
        obj_ground_area: A dictionary of City Object IDs and their ground area
        obj_roof_union_wkts: A dictionary of City Object IDs and their merged roof surface's WKT
        obj_ground_union_wkts: A dictionary of City Object IDs and their merged ground surface's WKT
        output_file_nm: Output WKT file name
                        -> format: city_obj_id; roof_wkt; ground_wkt; area_diff
    Output:
        list(underpass_obj_id_diff.keys()): A list of City Object IDs with underpasses
        only_roof_obj_ids: A list of City Object IDs that have roof surfaces but no ground surfaces (for testing)
    """
    underpass_obj_id_diff = {}
    only_roof_obj_ids = []

    for id, area in obj_roof_area.items():
        roof_area = area
        if id in obj_ground_area.keys():
            ground_area = obj_ground_area[id]
            diff = roof_area - ground_area  # roof - ground

            if diff > eps:
                underpass_obj_id_diff[id] = diff
        else:
            only_roof_obj_ids.append(id)

    with open(output_file_nm, 'w') as output_wkt:
        output_wkt.write('uuid; diff; roof_geom; ground_geom\n')

        for id, diff in underpass_obj_id_diff.items():
            output_wkt.write(f'{id}; {diff}; {str(obj_roof_union_wkts[id])}; {str(obj_ground_union_wkts[id])}\n')

    return list(underpass_obj_id_diff.keys()), only_roof_obj_ids
