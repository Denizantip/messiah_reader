import ctypes

lib = ctypes.CDLL('BCn/bcdec')

lib.bcdec_bc7.restype = ctypes.c_int
lib.bcdec_bc7.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int, ctypes.c_int]


def decompress_bc7(compressed_block, width, height):
    dest = bytes(width * height * 4)
    if lib.bcn_decode(compressed_block, dest, width, height):
        return dest
    else:
        raise ValueError("Could not decompress")
