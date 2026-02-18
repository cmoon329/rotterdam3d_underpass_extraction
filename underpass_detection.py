import shapely
from shapely import wkt as shapely_wkt
import pandas as pd
import geopandas as gpd
import csv
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
        measuredHeights: A dictionary mapping City Object IDs to their measured heights
        elevations: A dictionary mapping City Object IDs to their elevation information
                          {city_object_id: min_z}
    """
    cityobjs = list(input_data['CityObjects'].keys())


    elevation_per_building = {}  # {city_object_id: min_z}

    # first extract elevations of all buildings
    for i in cityobjs:
        if input_data['CityObjects'][i]['type'] == "Building":
            # Extract geographic extent values (min_x, min_y, min_z, max_x, max_y, max_z)
            geographicalExtent = input_data['CityObjects'][i].get('geographicalExtent')
            min_z = None
            if geographicalExtent and len(geographicalExtent) >= 6:
                min_z = geographicalExtent[2]  # 3rd value - minimum Z coordinate
            elevation_per_building[i] = min_z

    obj_ocs = {}    # {city_object_id: [outer_ceiling_surface_id, ...]}
    ocs_bounds = {}  # {outer_ceiling_surface_id: [[[vertex_index_1, vertex_index_2, ...]]]}
    measuredHeights = {}  # {city_object_id: measuredHeight}
    elevations = {}  # {city_object_id: elevation}

    # then extract outer ceiling surfaces and their boundaries, and measured heights of all city objects
    for i in cityobjs:
        if len(input_data['CityObjects'][i]['geometry']) == 0:
            continue
        else:
            type = input_data['CityObjects'][i]['geometry'][0]['type']
            boundaries = input_data['CityObjects'][i]['geometry'][0]['boundaries']
            smt_values = input_data['CityObjects'][i]['geometry'][0]['semantics']['values']
            smt_surfaces = input_data['CityObjects'][i]['geometry'][0]['semantics']['surfaces']

            highest_floor = input_data['CityObjects'][i]['attributes'].get('HOOGSTE_BOUWLAAG')
            lowest_floor = input_data['CityObjects'][i]['attributes'].get('LAAGSTE_BOUWLAAG')
            measuredHeight = input_data['CityObjects'][i]['attributes'].get('measuredHeight')
            parent = input_data['CityObjects'][i].get('parents')[0] if input_data['CityObjects'][i].get('parents') else None
            if parent:
                elevation = elevation_per_building[parent] if parent and elevation_per_building.get(parent) else None
            else:
                geographicalExtent = input_data['CityObjects'][i].get('geographicalExtent')
                elevation = None
                if geographicalExtent and len(geographicalExtent) >= 6:
                    elevation = geographicalExtent[2]  # 3rd value - minimum Z coordinate
            measuredHeights[i] = measuredHeight
            elevations[i] = elevation
            
            if highest_floor != None:
                highest_floor = float(highest_floor)
            if lowest_floor != None:
                lowest_floor = float(lowest_floor)

            ocs_num = {}  # {outer_ceiling_surface_num: outer_ceiling_surface_id}

            is_metro = ((highest_floor != None and highest_floor <= 0) \
                        and (lowest_floor != None and lowest_floor < 0) \
                        and (measuredHeight == None))
            
            for num, surf in enumerate(smt_surfaces):
                if surf['type'] == 'OuterCeilingSurface':
                    if not is_metro:
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

    #print(elevations)
    return obj_ocs, ocs_bounds, measuredHeights, elevations


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

    v_coords = {}  # {vertex_idx: [x_coord, y_coord, z_coord]}
    for i in range(0, len(vertices)):
        v_xyz = []
        v_x = (vertices[i][0] * scale[0]) + translate[0]
        v_y = (vertices[i][1] * scale[1]) + translate[1]
        v_z = (vertices[i][2] * scale[2]) + translate[2] if len(vertices[i]) > 2 else 0.0

        v_xyz.append(v_x)
        v_xyz.append(v_y)
        v_xyz.append(v_z)

        v_coords[i] = v_xyz

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

# 4) Calculate average height of outer ceiling surfaces
def average_outer_ceiling_surface_height(surface_coords):
    """
    Calculate the average height (Z value) of an outer ceiling surface from its vertices.
    Input:
        surface_coords: list of faces, each face is a list of rings, each ring is a list of [x, y, z] vertices
    Output:
        Average Z value (float) or None if no vertices
    """
    all_z = []
    for face in surface_coords:
        for ring in face:
            for vertex in ring:
                if len(vertex) == 3:
                    all_z.append(vertex[2])
    if all_z:
        return sum(all_z) / len(all_z)
    else:
        print("No vertices with Z value found.")
        return None
    
def all_outer_ceiling_surface_heights(ocs_bounds_coords):
    """
    Calculate the average height for all outer ceiling surfaces.
    Input:
        ocs_bounds_coords: dict {surface_id: surface_coords}
    Output:
        Dict {surface_id: average_height}
    """
    heights = {}
    for surface_id, surface_coords in ocs_bounds_coords.items():
        height = average_outer_ceiling_surface_height(surface_coords)
        heights[surface_id] = height
    return heights


# 5) Output a shp file of outer ceiling surfaces for visualization
def output_shp(obj_ocs, ocs_bounds_coords, surface_heights, measuredHeights, elevations, output_file_nm):
    """
    Function that outputs a shp file of outer ceiling surfaces for visualization

    Input:
        obj_ocs: A dictionary of City Objects and their outer ceiling surface IDs
        ocs_bounds_coords: A dictionary of outer ceiling surface IDs and their boundary cooridnates
        surface_heights: A dictionary of outer ceiling surface IDs and their average heights
        measuredHeights: A dictionary of City Objects and their measured heights
        elevations: A dictionary of City Objects and their elevation information
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
        writer.writerow(['surface_id', 'cityobj_id', 'area', 'upass_h', 'building_h', 'elevation', 'geom'])

        for uuid, surfs in obj_ocs.items():
            # if City Object has no outer ceiling surfaces, skip
            if len(surfs) == 0:
                continue

            geom = None
            for surf in surfs:
                geom = shapely_wkt.loads(ocs_bounds_wkts[surf])
                surf_ele = surface_heights.get(surf) if surface_heights is not None else None
                area = shapely.area(geom)
                building_h = measuredHeights.get(uuid)
                elevation = elevations.get(uuid)
                writer.writerow([surf, uuid, area, surf_ele - elevation if surf_ele is not None and elevation is not None else None, building_h, elevation, geom])

    # write to shp and remove the created csv file
    df = pd.read_csv(output_file_path)
    df['geom'] = df['geom'].apply(shapely_wkt.loads)
    gdf = gpd.GeoDataFrame(df, geometry=df['geom'], crs='epsg:28992')
    gdf = gdf.drop(columns=['geom'])
    gdf.to_file(f'data/{output_file_nm}.shp')

    if os.path.exists(output_file_path):
        os.remove(output_file_path)

    print('shp file created')
