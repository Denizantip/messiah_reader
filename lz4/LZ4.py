import ctypes
from io import BytesIO

lz4_lib = ctypes.CDLL("lz4/lz4.o")
lz4_lib.LZ4_decompress_fast.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int]
lz4_lib.LZ4_decompress_fast.restype = ctypes.c_int


def decompress_file(file):
    decompressed_size = int.from_bytes(file.read(4), 'little')
    compressed_data = file.read()
    decompressed_buffer = bytes(decompressed_size)

    lz4_lib.LZ4_decompress_fast(compressed_data, decompressed_buffer, decompressed_size)
    return BytesIO(decompressed_buffer)


def decompress_bytes(data: bytes, size: int) -> bytes:
    decompressed_buffer = bytes(size)
    lz4_lib.LZ4_decompress_fast(data, decompressed_buffer, size)
    return decompressed_buffer
