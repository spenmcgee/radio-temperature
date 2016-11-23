import numpy, sys
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
from scipy.signal import decimate
from numpy import zeros

def to_string(symbols):
	st = ''
	for s in symbols:
		if s: st += "1"
		else: st += "0"
	return st

def get_samples(filename):
	f = open(filename, "rb")
	bytestream = numpy.fromfile(f, dtype=numpy.uint8)
	f.close()
	iq = get_iq(bytestream)
	return iq

def get_iq(bytes):
	iq = numpy.empty(len(bytes)//2, 'complex')
	iq.real, iq.imag = bytes[::2], bytes[1::2]
	iq /= (255/2)
	iq -= (1 + 1j)
	return iq

def to_amplitude(iq):
	amp = numpy.sqrt(iq.real*iq.real+iq.imag*iq.imag)
	return amp

def str2num(s):
	total = 0
	for i in range(len(s)):
		total += int(s[i]) * pow(2,len(s)-i-1)
	return total

def bin2str(bits):
	s = ""
	for b in bits:
		if b: s += "1"
		else: s += "0"
	return s

def symbols2bits(s):
	bits = ""
	for i in range(0, len(s), 3):
		sym = s[i:i+3]
		if sym == "110": bits += "1"
		elif sym == "100": bits += "0"
	return bits

def temp(s):
	return (str2num(s[14:24])-500)/10.0

filename = sys.argv[1]
sample_rate = int(sys.argv[2]) #2048000
decimation = int(sys.argv[3]) #10
baud_rate = int(sys.argv[4]) #4096

samples_per_symbol = sample_rate/baud_rate

samples = get_samples(filename)
num_samples = len(samples)
print "NUM SAMPLES", num_samples
print "SAMPLE RATE", sample_rate
print "DECIMATION", decimation
print "BAUD RATE", baud_rate
print "TOTAL TIME", float(num_samples)/float(sample_rate)
print "SAMPLES PER SYMBOL", samples_per_symbol

samples = decimate(samples, decimation)
samples = to_amplitude(samples)

decimation = samples_per_symbol / decimation
convolution_size = decimation

print "NEW DECIMATION", decimation
print "NEW CONVOLUTION SIZE", convolution_size

#convolution_size = 50 #50
samples = numpy.convolve(samples, numpy.ones(convolution_size)/convolution_size, mode='same')
samples = samples > 0.6

offset = 0
while 1:
	if samples[offset] == 1: break
	offset += 1
offset += decimation/4

samples = samples[offset::decimation]

symbols = to_string(samples)
start = symbols.find("111000111000111000111000")
print "FOUND", symbols[start:start+46*3-1]

bits = symbols2bits(symbols)
print "BITS", bits
print "TEMP", temp(bits)
