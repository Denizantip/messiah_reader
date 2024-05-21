import struct
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Tuple

from lz4.LZ4 import decompress_file


@dataclass
class File:
    hash: str
    name: str
    type: str
    folder: str
    hashes: Tuple[str]


SKIP = 10

file_hash = '16s'

unknown1 = 'H'
unknown2 = 'H'
unknown3 = 'b'
file_name_size = 'H'

file_name = '{}s'
folder_idx = 'H'
type_idx = 'H'
hash_count = 'H'


def parse_repository(file):
    file.read(SKIP)
    size_filetypes = int.from_bytes(file.read(2), "little")
    list_filetypes = file.read(size_filetypes).decode('utf-8').split(';')
    print("Available file types: " + str(list_filetypes))
    size_folders = int.from_bytes(file.read(2), 'little')
    if size_folders == 0xFFFF:
        size_folders = int.from_bytes(file.read(4), "little")
    folders = file.read(size_folders).decode('utf-8').split(';')
    print("Available folders: " + str(folders[1:]))
    #  first element is @^_^@. Funny. Seems to avoid 0th index )
    total_files = 0
    try:
        while True:
            first = ''.join((unknown1, unknown2, unknown3, file_hash, file_name_size))
            offset = struct.calcsize("<" + first)
            buffer = file.read(offset)
            _, _, _, f_hash, l = struct.unpack("<" + first, buffer)

            second = ''.join((file_name, folder_idx, type_idx)).format(l)
            offset = struct.calcsize("<" + second)
            buffer = file.read(offset)
            name, f_idx, t_idx = struct.unpack("<" + second, buffer)

            offset = struct.calcsize("<" + hash_count)
            buffer = file.read(offset)
            file_hash_count = int.from_bytes(buffer, 'little')
            offset = struct.calcsize("<" + file_hash * file_hash_count)
            buffer = file.read(offset)
            hashes = tuple(h.hex() for h in struct.unpack("<" + file_hash * file_hash_count, buffer))
            total_files += 1
            yield File(f_hash.hex(), name.decode(), list_filetypes[t_idx], folders[f_idx], hashes)
            # print(f"hash: {f_hash},\nname: {name},\ntype: {list_filetypes[t_idx]},\nfolder: {folders[f_idx]},\nhashes: {hashes},\n")

    except struct.error as e:
        return


if __name__ == '__main__':
    if sys.argv[1] == '-p':
        path = Path(sys.argv[2])
    else:
        exit(1)

    with open(path, 'rb') as repository:
        repository.read(8)  # "CCCCZZZ4"

        for file in parse_repository(decompress_file(repository)):

            folder = file.hash[:2]
            f_name = f"{file.hash[:8]}-{file.hash[8:12]}-{file.hash[12:16]}-{file.hash[16:20]}-{file.hash[20:]}"
            source_file = path.parent / folder / f_name

            target_folder = path.parent / Path(file.folder)
            target_folder.mkdir(parents=True, exist_ok=True)
            target_file = target_folder / f"{file.name}.{file.type}"

            if not source_file.exists():  # mostly textures
                for i in range(1, 7):
                    source_file = source_file.with_suffix(f'.{i}')
                    if source_file.exists():
                        break
                else:
                    continue

            with open(source_file, 'rb') as src, open(target_file, 'wb') as target:
                if src.read(4) == b"ZZZ4":
                    src = decompress_file(src)
                else:
                    src.seek(0)
                target.write(src.read())
            source_file.unlink(missing_ok=True)
