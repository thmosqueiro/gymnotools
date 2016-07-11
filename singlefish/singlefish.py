#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import svm
import pickle
import pygymnext
import windowfile
import numpy as np
import argparse

class MyParser(argparse.ArgumentParser):
    def error(self, message):
        self.print_help()
        sys.stderr.write('\nerror: %s\n'%message)
        sys.exit(2)

description = 'Apply SVM model on spikes window file with 2 fishes'
parser = MyParser(description=description, formatter_class=argparse.RawTextHelpFormatter)

parser.add_argument('timeseries_file', type=argparse.FileType('r'), help='Timeseries (I32) file')
parser.add_argument('spikes_file', type=argparse.FileType('r'), help='Spikes window file')
parser.add_argument('scale_file', type=argparse.FileType('r'), help='Traning generated feature scale file')
parser.add_argument('filter_file', type=argparse.FileType('r'), help='Traning generated feature filter file')
parser.add_argument('svm_file', type=argparse.FileType('r'), help='Traning generated SVM model file')
#parser.add_argument('overlap_file', type=argparse.FileType('r'), help='Traning generated overlap classifier file')
parser.add_argument('singlefish_file', type=argparse.FileType('w'), help='Output timestamps of the SVM classfied pairs')
parser.add_argument('probs_file', type=argparse.FileType('w'), help='Output SVM probabilities for all spikes')

args = parser.parse_args()

maxSize = 160
maxDist = sys.maxint
onlyAbove = 0.005
saturationLow = -9.9
saturationHigh = 9.9
minWins = 1
numFeatures = 20
minprob = 0.80
minOverlapChan = 5


nChan = 11
winSize = 256
numFeatures = winSize/2+9*winSize
bytesPerSample = nChan * 4

def readScaleFile(scaleFile):
    minval = np.zeros(numFeatures)
    maxval = np.zeros(numFeatures)

    f = scaleFile.read()
    t = len(f)
    minval = np.fromstring(f[:t/2], dtype=np.float32)
    maxval = np.fromstring(f[t/2:], dtype=np.float32)

    return minval, maxval

def rescaleFeatureWin(featureData, mincal, maxval):
    return 2.*( (featureData - minval) / (maxval-minval) ) - 1

def applyFilter(featureData, selectedFeatures):
    return np.array([ featureData[f] for f in selectedFeatures ], dtype=np.float32)

inI32 = np.memmap(args.timeseries_file, mode='r', dtype=np.float32)
inSpkFile = args.spikes_file.name

inSpk = windowfile.readwinsExAllCh(open(inSpkFile, 'r'))
offs = np.array(list( windowfile.readwinsEx2(open(inSpkFile, 'r')) ))

minval, maxval = readScaleFile( args.scale_file )
selectedFeatures = np.loadtxt( args.filter_file, dtype=np.int32 )

inSVM = svm.libsvm.svm_load_model(args.svm_file.name)
#inRF = pickle.load( open(args.overlap_file.name, 'r') )

outSinglefish = args.singlefish_file
outProbs = args.probs_file

invec = np.zeros(winSize, dtype=np.float32)
outvec = np.zeros(numFeatures, dtype=np.float32)

worker = pygymnext.FeatureProcessor(invec, outvec)

prevOff = -sys.maxint
prevSamples = 0
prevWasSingle = False
prevWasA = False

tam = offs.size
for n, (curOff, winSamples, sigs) in enumerate(inSpk):
    #print('%d\t%d\t%d'%(n, curOff, winSamples))
    if n % 300 == 0:
        sys.stdout.write('\r%.03f%%'%( (100.*n) / tam ) )
        sys.stdout.flush()

    cause = 's'


    # Check in event is below maxsize
    '''if winSamples > maxSize:
        prevWasSingle = False
        prevSamples = winSamples
        prevOff = curOff

        cause = 'a'''

    ############### Novo
    if winSamples != winSize:
        prevSamples = winSamples
        prevOff = curOff

        cause = 'o'
    """else:
        nPred = inRF.predict(sigs.values()).sum()
        if nPred > minOverlapChan:
            #print('%d\t%d'%(curOff, nPred))
            cause = 'r'
            #outProbs.write('%s %d %f %f\n'%(cause, curOff, 0., 0.))
            '''import matplotlib.pyplot as plt
            for s in sigs.values():
                plt.plot(s)
            plt.show()'''
            #continue"""

    # Calculate and check distance to next and previous events
    nextOff = sys.maxint
    if n+1 < offs.size:
        nextOff = offs[n+1]

    distPrev = curOff - prevOff / bytesPerSample
    distNext = nextOff - curOff / bytesPerSample
    prevEndOff = prevOff + prevSamples * bytesPerSample

    prevSamples = winSamples
    prevOffBck = prevOff
    prevOff = curOff

    if (distPrev > maxDist) and (distNext > maxDist):
        cause = 'd'

    # Verify which channels can be used to feed the SVM
    assert(len(sigs) <= nChan)

    numWinOk = 0
    if winSamples == winSize:
        winOk = np.zeros(nChan, dtype=np.bool)
        maxAmp = np.zeros(nChan, dtype=np.float32)

        for m, (ch, sig) in enumerate(sigs.items()):
            abssig = np.abs(sig)

            chOk = False
            idxOnlyAbove = ( abssig >= onlyAbove ).sum()
            if idxOnlyAbove > 0:
                chOk = True
            satLowIdx = ( sig < saturationLow ).sum()
            satHighIdx = ( sig > saturationHigh ).sum()
            if (satLowIdx > 0) or (satHighIdx > 0):
                chOk = False
            maxAmp[ch] = abssig.max()

            if chOk == True:
                winOk[ch] = True
                numWinOk += 1
    else:
        cause = 'o'
        numWinOk = minWins

    # Check if there are sufficient windows to trust SVM
    if numWinOk < minWins:
        cause = 'i'

    ########### Pulei a parte do overlap, acho que nao faz mais sentido

    # Feed SVM and calculate joint probability

    probA = 0.
    probB = 0.
    if winSamples == winSize: #### Novo
        probA = 1.
        probB = 1.
        totalMaxAmp = 0.
        for m, (ch, sig) in enumerate(sigs.items()):
            if winOk[ch] == False:
                continue

            # Compute features
            invec[:] = sig[:]
            worker.process()

            # Rescale features
            rescvec = rescaleFeatureWin(outvec, minval, maxval)

            # Filter features
            filtvec = applyFilter(rescvec, selectedFeatures)

            # Apply SVM
            probs = (svm.c_double*2)(0.,0.)
            x0, max_idx = svm.gen_svm_nodearray(filtvec.tolist())
            c = svm.libsvm.svm_predict_probability(inSVM, x0, probs)

            M = np.abs(sig).max()

            probA *= probs[0] ** M
            probB *= probs[1] ** M
            totalMaxAmp += M

        if totalMaxAmp > 0:
            probA  = probA ** (1./totalMaxAmp)
            probB  = probB ** (1./totalMaxAmp)
        else:
            probA = 0.
            probB = 0.

        #print('%f\t%f'%(probA, probB))

        # Check if joint probability is above minimum
        if probA < minprob and probB < minprob:
            cause = 'p'

        # Everything Ok, write event pair offsets to outfile
    if cause == 's':
        if (probB > probA):
            outSinglefish.write('-1 %d\n'%(curOff))
            outProbs.write('%s %d %f %f\n'%(cause, curOff, probA, probB) )
        else:
            outSinglefish.write('1 %d\n'%(curOff))
            outProbs.write('%s %d %f %f\n'%(cause, curOff, probA, probB) )

    else:
        outProbs.write('%s %d %f %f\n'%(cause, curOff, probA, probB))

print('')
