import os.path
import struct
from enum import Enum, Flag

import matplotlib.pyplot as plt
import matplotlib.image
import numpy as np

from BCn import decompress_bc7
from lz4.LZ4 import decompress_bytes, decompress_file
from resource_repository import parse_repository


class ESamplerFilter(Enum):
    FNone = 0
    Point = 1
    Linear = 2
    Anisotropic = 3


class ESampleAddress(Enum):
    ANone = 0
    Wrap = 1
    Mirror = 2
    Clamp = 3
    FromTexture = 4


class EPixelFormat(Enum):
    R32G32B32A32 = 3
    A16B16G16R16 = 4
    R8G8B8A8 = 5
    B5G6R5 = 6
    A8L8 = 7
    G16R16 = 8
    G16R16F = 9
    G32R32F = 10
    R16F = 11
    L8 = 12
    L16 = 13
    A8 = 14
    FloatRGB = 15
    FloatRGBA = 255
    D24 = 16
    D32 = 17
    BC1 = 18
    BC2 = 19
    BC3 = 20
    BC4 = 21
    BC5 = 22
    BC6S = 23
    BC6U = 24
    BC7 = 25
    PVRTC2_RGB = 27
    PVRTC2_RGBA = 28
    PVRTC4_RGB = 29
    PVRTC4_RGBA = 30
    ETC1 = 31
    ETC2RGB = 32
    ETC2RGBA = 33
    ATC_RGBA_E = 34
    ATC_RGBA_I = 35
    ASTC_4x4_LDR = 36
    ASTC_5x4_LDR = 37
    ASTC_5x5_LDR = 38
    ASTC_6x5_LDR = 39
    ASTC_6x6_LDR = 40
    ASTC_8x5_LDR = 41
    ASTC_8x6_LDR = 42
    ASTC_8x8_LDR = 43
    ASTC_10x5_LDR = 44
    ASTC_10x6_LDR = 45
    ASTC_10x8_LDR = 46
    ASTC_10x10_LDR = 47
    ASTC_12x10_LDR = 48
    ASTC_12x12_LDR = 49
    ShadowDepth = 50
    ShadowDepth32 = 51
    R10G10B10A2 = 52
    R32U = 53
    R11G11B10 = 54
    ASTC_4x4_HDR = 55
    ASTC_5x4_HDR = 56
    ASTC_5x5_HDR = 57
    ASTC_6x5_HDR = 58
    ASTC_6x6_HDR = 59
    ASTC_8x5_HDR = 60
    ASTC_8x6_HDR = 61
    ASTC_8x8_HDR = 62
    ASTC_10x5_HDR = 63
    ASTC_10x6_HDR = 64
    ASTC_10x8_HDR = 65
    ASTC_10x10_HDR = 66
    ASTC_12x10_HDR = 67
    ASTC_12x12_HDR = 68
    R32G32B32A32UI = 69


class ESampleQuality(Enum):
    QNone = 0
    sample2x = 1
    sample4x = 2
    sample8x = 3


class ETextureType(Enum):
    Texture1D = 0
    Texture2D = 1
    Texture3D = 2
    Cube = 3
    Texture2DArray = 4
    CubeArray = 5
    Array = 6


class ETextureCompression(Enum):
    Default = 0
    NormalMap = 1
    DisplacementMap = 2
    Grayscale = 3
    HDR = 4
    NormalMapUncompress = 5
    NormalMapBC5 = 6
    VectorMap = 7
    Uncompressed = 8
    LightMap = 9
    EnvMap = 10
    MixMap = 11
    UI = 12
    TerrainBlock = 13
    TerrainIndex = 14
    NormalMapCompact = 15
    cBC6H = 16
    cBC7 = 17
    LightProfile = 18
    LUTHDR = 19
    LUTLOG = 20
    TerrainNormalMap = 21


class ETextureLODGroup(Enum):
    World = 0
    WorldNormalMap = 1
    WorldSpecular = 2
    Character = 3
    CharacterNormalMap = 4
    CharacterSpecular = 5
    Weapon = 6
    WeaponNormalMap = 7
    WeaponSpecular = 8
    Cinematic = 9
    Effect = 10
    EffectUnfiltered = 11
    Sky = 12
    gUI = 13
    RenderTarget = 14
    ShadowMap = 15
    LUT = 16
    TerrainBlockMap = 17
    TerrainIndexMap = 18
    TerrainLightMap = 19
    ImageBaseReflection = 20


class ETextureMipGen(Enum):
    FromTextureGroup = 0
    Simple = 1
    Sharpen = 2
    NoMip = 3
    Blur = 4
    AlphaDistribution = 5


class Flags(Flag):
    NONE = 0
    IsSRGB = 1
    IsDynamicRange = 2
    NoneCompression = 4
    CompressionNoAlpha = 8
    NoneMipDowngrading = 16


class Color:
    def __init__(self, r, g, b, a):
        self.r = r
        self.g = g
        self.b = b
        self.a = a


class Texture2DInfo:
    def __init__(self,
                 mag_filter,
                 min_filter,
                 mip_filter,
                 addressU,
                 addressV,
                 pixel_format,
                 mipLevel,
                 flags,
                 compression_preset,
                 lod_group,
                 mip_gen_preset,
                 texture_type,
                 width,
                 height,
                 r, g, b, a,
                 size,
                 unknown,
                 slice_count
                 ):
        self.mag_filter = ESamplerFilter(mag_filter)
        self.min_filter = ESamplerFilter(min_filter)
        self.mip_filter = ESamplerFilter(mip_filter)
        self.addressU = ESampleAddress(addressU)
        self.addressV = ESampleAddress(addressV)
        self.pixel_format = EPixelFormat(pixel_format)
        self.mipLevel = mipLevel
        self.flags = Flags(flags)
        self.compression_preset = ETextureCompression(compression_preset)
        self.lod_group = ETextureLODGroup(lod_group)
        self.mip_gen_preset = ETextureMipGen(mip_gen_preset)
        self.texture_type = ETextureType(texture_type)
        self.width = width
        self.height = height
        self.default_color = Color(r, g, b, a)
        self.size = size
        self.unknown = unknown
        self.slice_count = slice_count


class SliceInfo:
    def __init__(self,
                 size,
                 width,
                 height,
                 depth,
                 pitch_in_byte,
                 slice_in_byte):
        self.size = size
        self.width = width
        self.height = height
        self.depth = depth
        self.pitch_in_byte = pitch_in_byte
        self.slice_in_byte = slice_in_byte
        self.data = None


class Texture2D:
    def __init__(self, texture_info, slices):
        self.texture_info = texture_info
        self.slices = slices

texture_path = "/mnt/d6b78ffe-71fa-472e-986b-e5a57c7af055/Games/DiabloImmortal/Package/fe/feea889e-cafc-426d-b01c-7c15702ef063.6"

texture_info_fmt = "BBB BB B B B B B B B H H 4f I H H"
texture_info_size = struct.calcsize(texture_info_fmt)

texture_slice_fmt = "IHHHHI"
texture_slice_size = struct.calcsize(texture_slice_fmt)


with open("/mnt/d6b78ffe-71fa-472e-986b-e5a57c7af055/Games/DiabloImmortal/Patch/fa/fa5f513c-6bb8-4260-a6b8-67ca44b3cf37.6", "rb") as f:
    data = f.read(texture_info_size)
    texture_info = Texture2DInfo(*struct.unpack(texture_info_fmt, data))

    slices = list()
    for _ in range(texture_info.slice_count):
        slice_data = f.read(texture_slice_size)
        slice_info = SliceInfo(*struct.unpack(texture_slice_fmt, slice_data))
        texture_data_type = f.read(4)

        if texture_data_type == b"NNNN":
            size = slice_info.slice_in_byte or (slice_info.width * slice_info.height * 4)
            slice_info.data = f.read(size)

        elif texture_data_type == b"ZZZ4":
            decompressed_size = int.from_bytes(f.read(4), "little")
            slice_info.data = decompress_bytes(f.read(slice_info.size-24), decompressed_size)
        if texture_info.pixel_format == EPixelFormat.BC7:
            slice_info.data = decompress_bc7(slice_info.data,
                                             slice_info.width,
                                             slice_info.height)
        slices.append(slice_info)

    import matplotlib.image
    matplotlib.image.imsave('normals.png', np.frombuffer(slice_info.data, 'uint8').reshape(slice_info.height, slice_info.width, 4))

    texture = Texture2D(texture_info, slices)
