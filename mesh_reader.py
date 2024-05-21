import struct

import numpy as np

# struct part
messiah = "8s"  # .MESSIAH
unknown0 = "i"  # something is 8
data_size = "I"  # size of data
unknown1 = "H"  # something is 0
sub_mesh_count = "H"
vertex_count = "i"
index_count = "i"

header = ''.join((messiah, unknown0, data_size, unknown1, sub_mesh_count, vertex_count, index_count))
header_size = struct.calcsize(header)

VECTOR2 = np.dtype('2f')
VECTOR2H = np.dtype('2e')
VECTOR3 = np.dtype('3f')  # later better to use slices in favor of struct accessing
VECTOR4SMALL = np.dtype('4b')  # / 128.0
VECTOR4H = np.dtype('4h')  # / 32767.0
VECTOR4B = np.dtype('4B')  # / 255.0 TODO is it packed


data_types = {"P3F": ("position", VECTOR3),
              "N4B": ("normal", VECTOR4SMALL),
              "T2F": ("uv", VECTOR2),
              "T2H": ('uv', VECTOR2H),
              "T4H": ("tangent", VECTOR4H),
              "B4H": ("bitangent", VECTOR4H),
              "W4B": ("bone_weight", VECTOR4B), # / 255
              "I4B": ("bone_index", VECTOR4B),
              "Q4H": ("quaternion", VECTOR4H),
              }

vertex_buf = {"P3F_N4B_T2F": np.dtype([("position", VECTOR3),
                                       ("normal", VECTOR4SMALL),
                                       ("uv", VECTOR2)]),
              "T4H_B4H": np.dtype([("tangent", VECTOR4H), ("bitangent", VECTOR4H)]),
              'W4B_I4B': np.dtype([("bone_weight", '4B'), ("bone_index", '4B')]),
              "P3F": np.dtype([("position", VECTOR3)]),
              "Q4H_T2H": None,
              "None": None}

bounding_box = np.dtype([('min', VECTOR3), ('max', VECTOR3)])
bounding_sphere = np.dtype([('center', VECTOR3), ('radius', 'f4')])


def bounds(file):
    buffer = file.read(bounding_box.itemsize)
    b_box = np.frombuffer(buffer, dtype=bounding_box)

    buffer = file.read(bounding_sphere.itemsize)
    b_sphere = np.frombuffer(buffer, dtype=bounding_sphere)
    return b_box, b_sphere


with open("/mnt/d6b78ffe-71fa-472e-986b-e5a57c7af055/Games/DiabloImmortal/Package/Char/npc/npc_devil_diablo/Mesh_npc_devil_diablo.Mesh", 'rb') as file:
    buffer = file.read(header_size)
    messiah, unknown0, data_size, unknown1, sub_mesh_count, vertex_count, index_count = struct.unpack_from(header, buffer)

    l = "H"
    description = []

    for i in range(4):
        s_len = int.from_bytes(file.read(2), "little")
        section = file.read(s_len).decode('utf-8')
        if section != 'None':
            description.append(section)

    bounds(file)  # bounds per mesh?

    meshes = []
    for i in range(sub_mesh_count):
        mesh = {}
        buffer = file.read(struct.calcsize('4I'))
        idx_start, idx_count, vertex_start, vertex_count = struct.unpack_from('4I', buffer)
        idx_dt = np.dtype('uint16')

        indexes = np.frombuffer(file.read(idx_count * idx_dt.itemsize), dtype=idx_dt)
        indexes = indexes.reshape(-1, 3)
        mesh["indices"] = indexes
        for section in description:
            dtypes = np.dtype(list(map(data_types.get, section.split('_'))))
            buffer = file.read(dtypes.itemsize * vertex_count)
            verts = np.frombuffer(buffer, dtype=dtypes)
            mesh[section] = verts

        bounds(file)  # bounds per submesh?
        meshes.append(mesh)

print()
