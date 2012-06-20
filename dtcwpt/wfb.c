/* Wavelet filtering routines */

/*
 * Copyright (c) 2010-2012 Paulo Matias
 *
 * Permission to use, copy, modify, and distribute this software for any
 * purpose with or without fee is hereby granted, provided that the above
 * copyright notice and this permission notice appear in all copies.
 *
 * THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
 * WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
 * MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
 * ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
 * WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
 * ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
 * OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
 */

/* Based on the public domain code from Numerical Recipes at:
 * http://www.nr.com/pubdom/pwt.c.txt
 */

#include "wfb.h"

/* Analysis Filter Bank
 * filt: wavelet filter
 * in: input vector
 * n: size of the input vector
 * hout: low-pass filter output  (size: n/2)
 * gout: high-pass filter output (size: n/2)
 */
void afb(wavelet_filt *filt, float *in, unsigned int n, float *hout, float *gout) {
    unsigned int i,ii,j,k,n1,ni,nmod,ncoef;
    float ai,*h,*g;
    
    ncoef = filt->n;
    h = filt->h;
    g = filt->g;
    
    nmod = ncoef * n - filt->off;
    n1 = n - 1;  /* as n is a power of 2, n1 will always have all bits 1 */

    for(j = 0; j < (n >> 1); j++) {
        hout[j] = 0.;
        gout[j] = 0.;
    }
    
    for(ii=0,i=0; i<n; i+=2,ii++) {
        ni = nmod+i;
        for(k = 0; k < ncoef; k++) {
            ai = in[(ni + k) & n1];
            hout[ii] += h[k]*ai;
            gout[ii] += g[k]*ai;
        }
    }
}

/* Synthesis Filter Bank
 * filt: wavelet filter
 * hin: low-frequency input vector
 * gin: high-frequency input vector
 * n: size of the output vector
 * out: output vector
 */
void sfb(wavelet_filt *filt, float *hin, float *gin, unsigned int n, float *out) {
    unsigned int i,ii,j,k,jf,n1,ni,nmod,ncoef;
    float ai,ai1,*h,*g;
    
    ncoef = filt->n;
    h = filt->h;
    g = filt->g;
    
    nmod = ncoef * n - filt->off;
    n1 = n - 1;  /* as n is a power of 2, n1 will always have all bits 1 */

    for(j = 0; j < n; j++)
        out[j] = 0.;
    
    for(ii=0,i=0; i<n; i+=2,ii++) {
        ni = nmod+i;
        ai  = hin[ii];
        ai1 = gin[ii];
        for(k = 0; k < ncoef; k++) {
            jf = (ni + k) & n1;
            out[jf] += h[k]*ai ;
            out[jf] += g[k]*ai1;
        }
    }
}
