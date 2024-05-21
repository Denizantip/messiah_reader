#define BCDEC_IMPLEMENTATION 1
#include <stdlib.h>
#include "bcdec.h"

/* Header file contains next implementation of BC decodings.
    bcdec_bc1
    bcdec_bc2
    bcdec_bc3
    bcdec_bc4
    bcdec_bc5
    bcdec_bc6h_float
    bcdec_bc6h_half
    bcdec_bc7         <-- I was needed only this
*/

int bcn_decode(char* compData, char* uncompData, int w, int h){
    char *src, *dst;
    src = compData;
    for (int i = 0; i < h; i += 4) {
        for (int j = 0; j < w; j += 4) {
            dst = uncompData + (i * w + j) * 4;
            bcdec_bc7(src, dst, w * 4);
            src += BCDEC_BC7_BLOCK_SIZE;
        }
    }
    return 1;
}