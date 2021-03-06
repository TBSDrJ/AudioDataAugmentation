# Using Python 3.7.4
# Module for handling read/write of .wav sound files; in Standard Library
import wave
# Module for converting bytes to other types and back; in Standard Library
from struct import pack, unpack
# Module to generate random values for data augmentation; in Standard Library
from random import randrange
# Module to run system commands, use to get directory listing; in Standard Library
from subprocess import run

"""
Assumption: A .wav file (assuming mono not stereo sound) is set up as a sequence of
16-bit/2-byte values, each of which represents the y-value of a sinusoidal
function that represents the sound wave as a signed 16-bit integer (typically
referred to as 'short'), where 0 = silence, and +/-2**15 is loudest.
"""

DEBUG = True
MAX_SOUND = 2**15
REPS = 2 # Number of times each augmentation is run

def wavToShort(readBytes):
    """
    Inputs: readBytes = byte stream from .wav file
    Returns: list of (16-bit signed) integers represented by that byte stream
    Purpose: Convert .wav bytes to integers to make it easier to apply
        arithmetic operations to them.
    """
    intList = []
    for i, b in enumerate(readBytes):
        if i % 2 == 1:
            # This will never get index out of range because of if statement
            inBytes = readBytes[i-1:i+1]
            # Outputs 1-tuple, so use [0] to get only integer
            inShort = unpack('h', inBytes)
            intList.append(inShort[0])
    return intList

def shortToWav(intList):
    """
    Inputs: intList = list of (16-bit signed) integers representing a byte stream
    Returns: list of bytes, two per integer, representing that list of integers
    Purpose: Convert list of integers (after it has been modified by an
        augmentation method) back to bytes so it can be written out to a .wav file.
    """
    bitStr = b''
    for index, i in enumerate(intList):
        try:
            bitStr += pack('h', i)
        except:
            print("BYTE TO SHORT FAILED!")
            print("Value:", i, "at Index:", index)
            break
    return bitStr

def changeAmplitude(intList, ampChange):
    """
    Inputs: intList = list of integers representing sound wave
        ampChange = factor by which amplitude should be changed
    Returns: intList = list of integers, modified by a change in amplitude,
        clipped if beyond MAX_SOUND value.
    Purpose: Apply change in amplitude uniformly across the sound wave.
    """
    newList = []
    for index, value in enumerate(intList):
        newValue =  int(value * ampChange)
        if newValue >= MAX_SOUND:
            newValue = MAX_SOUND - 1
        if newValue <= -MAX_SOUND:
            newValue = -MAX_SOUND + 1
        newList.append(newValue)
    return newList

def wobbleAmplitude(intList, ampChanges):
    """
    Inputs: intList = list of integers representing sound wave
        ampChange = 2-tuples, first is factor by which amplitude should be
            changed, second is duration (proportion) over which change is applied
            Sum of second coords should be 1.0; if not, all amounts past 1.0 will
            be truncated.
    Returns: intList = list of integers, modified by a change in amplitude,
        clipped if beyond MAX_SOUND value.
    Purpose: Apply change in amplitude uniformly across the each section of
        the sound wave.
    """
    pass


# Get a listing of input .wav files, convert stdout to string
fileList = run(['ls', 'inputWavs'], capture_output=True).stdout.decode()
fileList = fileList.split('\n')
for inFileName in fileList:
    if DEBUG: print('File List Entry:', inFileName)
    if '.wav' in inFileName or '.WAV' in inFileName:
        if DEBUG: print('File is wav.')
        strippedFileName = inFileName.split('.wav')[0]
        if DEBUG: print('Stripped File Name:', strippedFileName)
        fileCounter = 0
        inWavFile = wave.open(inFileName, 'rb')
        if DEBUG:
            # Check input .wav file parameters.
            # Expecting:
            #   nchannels = 1
            #   sampwidth = 2
            #   framerate = 44100
            #   nframes = variable
            #   compType = 'NONE' or equivalent
            #   compname = 'NONE' or equivalent
            print(inWavFile.getparams())
        # Capture parameters for setting up output file.
        chn, swd, frt, nfr, cmt, cmn = inWavFile.getparams()
        # Read entire .wav file as bytes
        wavBytes = inWavFile.readframes(inWavFile.getnframes())
        inWavFile.close()
        intWav = wavToShort(wavBytes)
        if DEBUG:
            # Make sure integer list length matches .wav number of frames
            print("This should match nframes:", len(intWav))
        # Find maximum amplitude of wave as a percentage of maximum.
        maxAmp = max(abs(max(intWav)), abs(min(intWav))) / MAX_SOUND
        if DEBUG: print("Max amplitude (as int):", max(abs(max(intWav)),
            abs(min(intWav))), "Proportion of MAX:", maxAmp)

        # Start data augmentation process with uniform amplitude change
        # Amount and direction of change depends on maxAmp.
        ampFactors = []
        while len(ampFactors) < REPS:
            if maxAmp < 0.33:
                # If maxAmp is less than 0.33, multiply by a factor between 1 and 3
                # Using powers of 2 to ensure exact decimal matching
                factor = randrange(257, 769) / 256
            elif maxAmp < 0.66:
                # If maxAmp is between 0.33 and 0.66, multiply by 0.5 to 1.5
                factor =  randrange(256, 769) / 512
            else:
                # If maxAmp is bigger than 0.66, multiply by 0.33 and 1
                factor = randrange(257, 768) / 768
            # Don't use the same factor twice
            if factor not in ampFactors:
                ampFactors.append(factor)
        if DEBUG: print("Uniform Amplitude Factors:", ampFactors)
        for factor in ampFactors:
            newIntWav = changeAmplitude(intWav, factor)
            newFileName = 'outputWavs/' + strippedFileName + str(fileCounter) + '.wav'
            if DEBUG: print('Writing file:', newFileName)
            outWavFile = wave.open(newFileName, 'wb')
            outWavFile.setparams((chn, swd, frt, nfr, cmt, cmn))
            outWavFile.writeframes(shortToWav(newIntWav))
            if DEBUG: print('Done.')
            fileCounter += 1


        # Next, augment by speeding up/slowing down the original by a factor up to 0.20
        spFactors = []
        while len(spFactors) < REPS:
            factor = randrange(410, 615) / 512
            if factor not in spFactors:
                spFactors.append(factor)
        if DEBUG: print("Speed Change Factors:", spFactors)
        for factor in spFactors:
            newFileName = 'outputWavs/' + strippedFileName + str(fileCounter) + '.wav'
            if DEBUG: print('Writing file:', newFileName)
            outWavFile = wave.open(newFileName, 'wb')
            # Use captured paramters for setting up output file.
            # Notice that we carry out the speed change by changing sample rate.
            outWavFile.setparams((chn, swd, int(frt * factor), nfr, cmt, cmn))
            outWavFile.writeframes(shortToWav(intWav))
            if DEBUG: print('Done.')
            fileCounter += 1
