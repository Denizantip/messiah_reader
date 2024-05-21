import struct
import os.path as op
from enum import Enum

from lz4.LZ4 import decompress_file
from resource_repository import parse_repository


class EShaderGraphType(Enum):
    PBR = 0
    Unlit = 1
    Particle = 2
    Effect = 3
    Decal = 4
    PostProcess = 5
    UI = 6
    Function = 7


fmt = "<8sIH"
buf_size = struct.calcsize(fmt)

with open("../Package/resource.repository", "rb") as file:
    file.read(4)
    for f in parse_repository(decompress_file(file)):
        if f.type == 'Material':
            material_name = f.name
            material_path = f.hash
            folder = material_path[:2]
            path = f"{material_path[:8]}-{material_path[8:12]}-{material_path[12:16]}-{material_path[16:20]}-{material_path[20:]}"
            with open(op.join('..', 'Package', folder, path), "rb") as material_fd:
                buffer = decompress_file(material_fd)
# mat_path = "/mnt/d6b78ffe-71fa-472e-986b-e5a57c7af055/Games/DiabloImmortal/messiah_reader/m_necromancer_yifu_s03_001_aw3_mat_cn.bin"
# with open(mat_path, 'rb') as mat_fd:
                header, one, string_size = struct.unpack(fmt, buffer.read(buf_size))
                if string_size == 0:
                    num_of_materials = buffer.read(1)
                    continue
                else:
                    s = buffer.read(string_size).decode('utf-8')
                    sub_materials_count = struct.unpack('B', buffer.read(1))
