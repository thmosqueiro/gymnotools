#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division

import scipy.signal
import numpy as np
import sys
import matplotlib.pyplot as plt
import argparse

from windowfile import writewin

if sys.version_info.major == 3:
    xrange = range
    mode = 'b'
else:
    mode = ''

freq = 45454.545454
winSize = 256
chirpGain = 0.5
satH = 9.9
satL = -9.9
onlyAbove = 0.005

class MyParser(argparse.ArgumentParser):
    def error(self, message):
        self.print_help()
        sys.stderr.write('\nerror: %s\n'%message)
        sys.exit(2)

description = 'Detect spikes on memmapf32 (DasyLab I32) format series'
parser = MyParser(description=description, formatter_class=argparse.RawTextHelpFormatter)

parser.add_argument('timeseries_file', type=argparse.FileType('r'), help='Timeseries (I32) file')
parser.add_argument('hilbert_file', help='Output Absolute sum of Hilbert Transform of the signal on I32 format')
parser.add_argument('outfile', type=argparse.FileType('w'), help='Output spike window file')
parser.add_argument('--chirps_file', type=argparse.FileType('r'), help='Chirp regions file')
parser.add_argument('-d', '--detection', type=float, default=1.00, help='Theshold for detecting a spike')
parser.add_argument('-r', '--refractory', type=float, default=0.001, help='Refractory period for spike detection')
parser.add_argument('-m', '--max_size', type=float, default=0.0035, help='Maximum size for a single spike')
parser.add_argument('-n', '--numtaps', type=int, default=301, help='Number of taps for high pass filter on Hilbert Transform')
parser.add_argument('-c', '--cutoff', type=float, default=1., help='Cutoff frequency of high pass filter')
parser.add_argument('-f', '--fixedwin', help='Fixed window(use for single-fish data files)', action='store_true')
parser.add_argument('-u', '--useHilbert', help='use already generated Hilbert file', action='store_true')


args = parser.parse_args()

threshold = args.detection
refrac = int(args.refractory * freq)
maxSize = int(args.max_size * freq)
single = args.fixedwin

debug = False

num = [-0.127838238013738, -0.122122430298337, -0.207240989159078, -0.741109041690890,  1.329553577868309]
den = [ 1.000000000000000, -0.445897866413142, -0.101209607292324, -0.047938888781208, -0.037189007185997]

def myabshilbert(x):
    return np.sqrt(scipy.signal.lfilter(num, den, x)[4:]**2 + x[:-4]**2)

nchan = 11

inarr = np.memmap(args.timeseries_file, dtype=np.float32, mode='r')
sizein, = inarr.shape

if args.useHilbert == True:
    h = np.memmap(args.hilbert_file, np.float32, 'r')
else:
    print('Generating new Hilbert file')
    h = np.memmap(args.hilbert_file, np.float32, 'w+', shape=(sizein//11 - 4))
    for i in xrange(nchan):
        print(i)
        h += myabshilbert(inarr[i::nchan])

    n = args.numtaps
    a = scipy.signal.firwin(n, cutoff=(args.cutoff/freq), window='hanning')
    a = -a
    a[n//2] += 1

    h = scipy.signal.lfilter(a, [1], h)[(n-1)//2:]

if args.chirps_file is not None:
    chirps = np.loadtxt(args.chirps_file, unpack=True, dtype=np.int)
    nChirps = chirps.shape[1]
outputFile = args.outfile
#plt.plot(h[:10000])
#plt.show()

idxAbove = np.array([], dtype=np.int)
thresholds = []
last = 0
print('Applying threshold...')
if args.chirps_file is not None:
    for n in range(nChirps):
        beg, end = chirps[:, n]
        idxAbovelow, = np.where( h[last:beg] > threshold )
        idxAbovelow += last
        th = h[beg:end].max() * chirpGain
        idxAbovehigh, = np.where( h[beg:end] > th ) #############
        thresholds.append(th)
        idxAbovehigh += beg
        idxAbove = np.concatenate( (idxAbove, idxAbovelow, idxAbovehigh))
        last = end
    idxAbovelow, = np.where( h[last:] > threshold )
    idxAbovelow += last
    idxAbove = np.concatenate( (idxAbove, idxAbovelow) )
else:
    idxAbove, = np.where( h > threshold )

locs, = np.where( np.diff(idxAbove) > refrac )

onChirp = False
chirpIdx = 0
tamlocs = len(locs)
offsets = np.zeros(tamlocs, dtype=np.int)
M = np.zeros(tamlocs)
l = np.zeros(tamlocs, dtype=np.int)
lastLen = 0
#possiveisSpikes = [None for i in range(tamlocs)]
beg = idxAbove[0]
n = 0
for num,i in enumerate(locs):
    if num % 300 == 0:
        sys.stdout.write('\rWindowing: %.03f%%'%( 100.*num / (1.*tamlocs) ))
        sys.stdout.flush()

    if beg - winSize//2 > 0:
        offset = beg-winSize//2
    else:
        offset = 0



    offsetend = idxAbove[i]+winSize//2

    begChirp = np.inf
    endChirp = np.inf
    if args.chirps_file is not None:
        if chirpIdx < nChirps:
            begChirp, endChirp = chirps[:, chirpIdx]

    if offsetend > begChirp:
        onChirp = True
    if offset > endChirp:
        chirpIdx += 1
        onChirp = False

    if onChirp == True:
        th = thresholds[chirpIdx]
    else:
        th = threshold

    PS = h[offset : offsetend]
    if PS.size < 20:
        print('Window too small %ld'%offset)
        continue
    possiveisSpikesSig =  [ np.array(inarr[c+11*offset: c + 11*offsetend: 11]) for c in range(11) ] 
        
    #possiveisSpikes[num] = PS 
    #l[num] = len(PS) 
    beg = idxAbove[i+1]

    if PS[winSize//2:-winSize//2] != []:
        #M[num] = PS[winSize//2:-winSize//2].max() 
        Mi = winSize//2 + PS[winSize//2:-winSize//2].argmax()
    else:
        #M[num] = PS.max()
        Mi = PS.argmax()
    Midx = offset + Mi


    flagOverlapBegin = True
    begin = 0
    counter = 0
    for n,s in enumerate(PS[:Mi][::-1]):
        if s < th:
            counter += 1
        else:
            counter = 0
        if counter == refrac :
            begin = Mi - n + refrac//2
            flagOverlapBegin = False
            break


    flagOverlapEnd = True
    fim = PS.size-1
    counter = 0
    for n,s in enumerate(PS[Mi:]):
        if s < th:
            counter += 1
        else:
            counter = 0
        if counter == refrac:
            fim = Mi + n - refrac//2
            flagOverlapEnd = False
            break

    flagOverlapSize = False
    if fim - begin > maxSize:
        flagOverlapSize = True
        

    # Fill borders with DC sample
    if flagOverlapBegin == False:
        for c in range(nchan):
            possiveisSpikesSig[c][:begin] = possiveisSpikesSig[c][begin]
            #possiveisSpikesSig[c][:begin] = 0
    if flagOverlapEnd == False:
        for c in range(nchan):
            possiveisSpikesSig[c][fim:] = possiveisSpikesSig[c][fim]
            #possiveisSpikesSig[c][fim:] = 0

    #print('%d\t%d\t%d'%(flagOverlapEnd, flagOverlapBegin, flagOverlapSize))
    if (flagOverlapEnd == False and flagOverlapBegin == False) or single == True:
        b = Mi-winSize//2
        e = min((Mi+winSize//2), possiveisSpikesSig[0].size)
        size = e - (Mi-winSize//2)
        center = Mi - b
        janelas = [possiveisSpikesSig[c][b:e] for c in range(nchan)]
    elif flagOverlapEnd == True and flagOverlapBegin == False:
        b = Mi-winSize//2
        e = fim
        size = fim - (Mi-winSize//2)
        center = Mi - b
        janelas = [possiveisSpikesSig[c][b:e] for c in range(nchan)]
    elif flagOverlapEnd == False and flagOverlapBegin == True:
        b = begin
        e = min((Mi+winSize//2), possiveisSpikesSig[0].size)
        size = e - begin
        center = Mi - b
        janelas = [possiveisSpikesSig[c][b:e] for c in range(nchan)]
    #elif flagOverlapEnd == True and flagOverlapBegin == True:
    else:
        b = begin
        e = fim
        size = fim - begin
        center = Mi - b
        janelas = [possiveisSpikesSig[c][b:e] for c in range(nchan)]
    #print("%d\t%d\t%d\t%d\t%d\t%.03f"%(flagOverlapBegin, flagOverlapEnd, begin, fim, janelas[0].size, 100.*num / (1.*tamlocs)))
   
    if flagOverlapSize == True and single == False:
        b = begin
        e = fim
        size = fim - begin
        center = Mi - b
        janelas = [possiveisSpikesSig[c][begin:fim] for c in range(nchan)]

    '''if b - e < winSize and single == False:
        b = max(0, Mi-winSize//2)
        e = min(Mi+winSize//2, possiveisSpikesSig[0].size)
        size = e - b
        center = Mi - b
        janelas = [possiveisSpikesSig[c][b:e] for c in range(nchan)]'''

    if single == True:
        njanelas = 0
        listjanelas = []
        for n,s in enumerate(janelas):
            if s.size > 0:
                m = s.min()
                M = s.max()
                if M > satH or m < satL:
                    continue
                if abs(M) < onlyAbove and abs(m) < onlyAbove:
                    continue
                else:
                    listjanelas.append( (n, s) )
                    njanelas += 1
            else:
                continue
    else:
        njanelas = 11
        listjanelas = [(n,s) for n,s in enumerate(janelas)]
    
    if njanelas == 0:
        continue

    if single == True:
        if size != winSize:
            print('--')
            print(size)
            print('--')
            continue
    if offset+b not in offsets:
        writewin(outputFile, (lastLen, offset+b, size, njanelas, center, listjanelas) )
        offsets[num] = offset+b
        lastLen = 6*4 + njanelas*4*(1 + size)
        if lastLen > 400*njanelas*4:
            print(' Too large window: %d samples'%(lastLen/njanelas/4))
            plt.plot(PS)
            plt.show()
    #else:
    #    print('Will not print same offset twice')

    if debug == True:
        for c in xrange(nchan):
            plt.plot(janelas[c], 'k-', alpha=0.1)

        '''print("%d\t%d\t%d\t%d"%(flagOverlapBegin, flagOverlapEnd, begin, fim))
        plt.plot(np.arange(-b, PS.size-b, 1), PS)
        plt.plot([Mi-b, Mi-b], [0, 10], 'k-')
        plt.plot([0-b,winSize], [threshold, threshold], 'k-')
        plt.plot([begin-b, begin-b], [0, 10], 'c-')
        plt.plot([fim-b, fim-b], [0, 10], 'm-')
        plt.show()'''

        if (num+1) % 500 == 0:
            plt.show()

print('')