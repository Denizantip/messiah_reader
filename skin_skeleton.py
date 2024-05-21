import struct

import numpy as np

from lz4.LZ4 import decompress_file



with open('/mnt/d6b78ffe-71fa-472e-986b-e5a57c7af055/Games/DiabloImmortal/Package/Char/npc/npc_devil_diablo/Skin_npc_devil_diablo_chuchang.SkinSkeleton', "rb") as skeleton_fd:
    if skeleton_fd.read(4) == b'ZZZ4':
        bio = decompress_file(skeleton_fd)
    else:
        skeleton_fd.seek(0)
        bio = skeleton_fd
    struct_fmt = "<8sIIH"
    struct_size = struct.calcsize(struct_fmt)
    wtf = bio.read(struct_size)
    bone_count = int.from_bytes(bio.read(2), 'little')
    bones = {}
    for _ in range(bone_count):
        name_length = int.from_bytes(bio.read(1), 'little')
        read_size = struct.calcsize('<12f')
        mat = np.eye(4)
        _t = np.frombuffer(bio.read(read_size), dtype=np.float32).reshape(4, -1)
        mat[..., :3] = _t
        name = struct.unpack(f'{name_length}s', bio.read(name_length))
        bones[name] = np.linalg.inv(mat)
    print(bones)
