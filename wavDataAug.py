# Using Python 3.7.4
# Module for handling read/write of .wav sound files; in Standard Library
import wave
# Module for converting bytes to other types and back; in Standard Library
from struct import pack, unpack

"""
A .wav file (assuming mono not stereo sound) is set up as a sequence of
16-bit/2-byte values, each of which represents the y-value of a sinusoidal
function that represents the sound wave as a signed 16-bit integer (typically
referred to as 'short'), where 0 = silence, and +/-2**15 is loudest.
"""

MAX_SOUND = 2**15

def wavToShort(readBytes):
    """
    Inputs: readBytes = byte stream from .wav file
    Returns: list of (16-bit signed) integers represented by that byte stream
    Purpose: Convert .wav bytes to integers to make it easier to apply
        arithmetic operations to them.
    """
    pass

def shortToWav(intList):
    """
    Inputs: intList = list of (16-bit signed) integers representing a byte stream
    Returns: list of bytes, two per integer, representing that list of integers
    Purpose: Convert list of integers (after it has been modified by an
        augmentation method) back to bytes so it can be written out to a .wav file.
    """
    pass

def changeAmplitude(intList, ampChange):
    """
    Inputs: intList = list of integers representing sound wave
        ampChange = factor by which amplitude should be changed
    Returns: intList = list of integers, modified by a change in amplitude,
        clipped if beyond MAX_SOUND value.
    Purpose: Apply change in amplitude uniformly across the sound wave.
    """
    pass

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
