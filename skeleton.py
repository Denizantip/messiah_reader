import struct
from collections import deque
import numpy as np


def dictionary(dict_entry_count):
    d = []
    for i in range(dict_entry_count):
        entry = []
        while True:
            ch = file.read(1)
            if ch == b'\x00':
                break
            else:
                entry.append(ch.decode('utf-8'))
        d.append(''.join(entry))
    file.read(1)
    return d


def cValue():
    """VLQ """
    first = int.from_bytes(file.read(1), 'little', signed=True)
    second = int.from_bytes(file.read(1), 'little', signed=True)
    if not (first & 128):
        val = first
    else:
        val = first & 127 | ((second & 127) << 7)
    return val


class Descriptor:
    def __init__(self, name, children_count):
        self.name = name
        self.value = None
        self.children_count = children_count
        if children_count != 0:
            self.children = []

    def __repr__(self):
        return f"{self.name}: {self.value}"


def read_string():
    buf = bytearray()
    while True:
        c = file.read(1)
        if c == b'\x00':
            break
        buf.append(ord(c))
    return buf.decode('utf-8')



with open('/mnt/d6b78ffe-71fa-472e-986b-e5a57c7af055/Games/DiabloImmortal/Package/Char/npc/npc_devil_diablo/Skin_npc_devil_diablo.SkinSkeleton', "rb") as skeleton_fd:
    bio = skeleton_fd
    struct_fmt = "<8sIIH"
    struct_size = struct.calcsize(struct_fmt)
    bio.read(struct_size)
    bone_count = int.from_bytes(bio.read(2), 'little')
    bone_names = list()
    bones_matrices = list()
    for _ in range(bone_count):
        name_length = int.from_bytes(bio.read(1), 'little')
        read_size = struct.calcsize('<12f')
        mat = np.eye(4)
        _t = np.frombuffer(bio.read(read_size), dtype=np.float32).reshape(4, -1)
        mat[..., :3] = _t
        name = struct.unpack(f'{name_length}s', bio.read(name_length))[0]
        bone_names.append(name.decode())
        bones_matrices.append(np.linalg.inv(mat))


with open("/mnt/d6b78ffe-71fa-472e-986b-e5a57c7af055/Games/DiabloImmortal/Package/Char/npc/npc_devil_diablo/npc_devil_diablo.skeleton.unpacked", "rb") as file:
    file.read(4)  # magic
    file_size = int.from_bytes(file.read(4), 'little')
    file.read(4)  # zero0
    dict_entry_count = struct.unpack('<B', file.read(1))[0]
    dicts = dictionary(dict_entry_count)
    data_start_offset = struct.unpack('<I', file.read(4))[0]

    file.read(4)  # uint zero
    element_count = cValue()
    descriptors = []
    elements = []
    for i in range(element_count):
        name, children_count = file.read(2)
        descriptor = Descriptor(dicts[name], children_count)
        descriptors.append(descriptor)

    for i in range(element_count):
        file.read(1)
        type_ = ord(file.read(1))
        match type_:
            case 1:
                element = read_string()
            case 2 | 4:
                element = int.from_bytes(file.read(2), 'little')
                file.read(2)
            case 3:  # boolean
                element = bool.from_bytes(file.read(1), 'little', signed=True)
            case 5:
                element = struct.unpack('<f', file.read(4))[0]
            case _:
                element = read_string()
        descriptors[i].value = element
        elements.append(element)


def parse_rows(children):
    return np.array([np.fromstring(row.value, sep=' ', dtype=np.float32) for row in children])


class Bone:
    def __init__(self, node, descr):
        self.parent = node
        self.children = []
        for child in descr.children:
            match child.name:
                case 'identifier':
                    self.name = child.value
                    if self.name in bone_names:
                        mat_idx = bone_names.index(self.name)
                        self.mat = bones_matrices[mat_idx]
                case 'transform':
                    self.transform = parse_rows(child.children)
                case 'node':
                    # if list(filter(lambda c: c.name == 'identifier' and c.value in bone_names, child.children)):
                    self.children.append(Bone(self, child))

    def __repr__(self):
        return self.name


root_element = descriptors[0]
parent_queue = deque()
parent_queue.append(root_element)
offset = 1



while parent_queue:
    parent = parent_queue.popleft()
    if parent.children_count != 0:
        children = descriptors[offset: offset + parent.children_count]

        parent.children = children

        parent_queue.extend(parent.children)
        offset += parent.children_count

skeleton = Bone(None, descriptors[0])

queue = deque()
queue.extend(skeleton.children)

while queue:
    bone_data = queue.popleft()
    if bone_data.name not in bone_names:
        queue.extend(bone_data.children)
        continue
    print(f"{bone_data} -> {bone_data.parent}")

    queue.extend(bone_data.children)

print(bone_names)
