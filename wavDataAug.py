# Using Python 3.7.4
# Module for handling read/write of .wav sound files; in Standard Library
import wave
# Module for converting bytes to other types and back; in Standard Library
from struct import pack, unpack
# Module to generate random values for data augmentation; in Standard Library
from random import randrange

"""
Assumption: A .wav file (assuming mono not stereo sound) is set up as a sequence of
16-bit/2-byte values, each of which represents the y-value of a sinusoidal
function that represents the sound wave as a signed 16-bit integer (typically
referred to as 'short'), where 0 = silence, and +/-2**15 is loudest.
"""

DEBUG = True
MAX_SOUND = 2**15
REPS = 1 # Number of times each augmentation is run

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
    for i in intList:
        bitStr += pack('h', i)
    return bitStr

def changeAmplitude(intList, ampChange):
    """
    Inputs: intList = list of integers representing sound wave
        ampChange = factor by which amplitude should be changed
    Returns: intList = list of integers, modified by a change in amplitude,
        clipped if beyond MAX_SOUND value.
    Purpose: Apply change in amplitude uniformly across the sound wave.
    """
    for index, value in enumerate(intList):
        newValue =  int(value * ampChange)
        if newValue > MAX_SOUND:
            newValue = MAX_SOUND
        if newValue < -MAX_SOUND:
            newValue = -MAX_SOUND
        intList[index] = newValue
    return intList

def changeSpeed(intList, spChange):
    """
    Inputs: intList = list of integers representing sound wave
        spChange = factor by which speed should be changed
    Returns: intList = list of integers, stretched to be longer/slower, or
        compressed to be shorter/faster.
    Purpose: Apply change in speed uniformly across the sound wave.
    """
    pass

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

inWavFile = wave.open('coke.wav', 'rb')
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
if DEBUG:
    print("Max amplitude (as int):", max(abs(max(intWav)), abs(min(intWav))),
        "Proportion of MAX:", maxAmp)

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
if DEBUG:
    print("Uniform Amplitude Factors:", ampFactors)
for factor in ampFactors:
    newIntWav = changeAmplitude(intWav, factor)

# Next, augment by speeding up/slowing down the original by a factor up to 0.20
spFactors = []
while len(spFactors) < REPS:
    factor = randrange(590, 615) / 512
    if factor not in spFactors:
        spFactors.append(factor)
if DEBUG:
    print("Speed Change Factors:", spFactors)
for factor in spFactors:
    outWavFile = wave.open('newCoke.wav', 'wb')
    # Use captured paramters for setting up output file.
    # Notice number of frames is set to match length of new byte stream, in case
    #    that has changed.
    outWavFile.setparams((chn, swd, int(frt * factor), len(newIntWav), cmt, cmn))
    outWavFile.writeframes(shortToWav(newIntWav))
