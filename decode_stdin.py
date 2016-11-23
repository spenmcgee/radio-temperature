import numpy as np, sys, time
import matplotlib.pyplot as plt
from scipy.signal import decimate
from numpy import zeros

def to_string(symbols):
	st = ''
	for s in symbols:
		if s: st += "1"
		else: st += "0"
	return st

def get_samples(size):
	stdin = sys.stdin.read(int(size))
	data = np.frombuffer(stdin, dtype='uint8')
	samples = get_iq(data)
	return samples

def get_iq(bytes):
	iq = np.empty(len(bytes)//2, 'complex')
	iq.real, iq.imag = bytes[::2], bytes[1::2]
	iq /= (255/2)
	iq -= (1 + 1j)
	return iq

def to_amplitude(iq):
	amp = np.sqrt(iq.real*iq.real+iq.imag*iq.imag)
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

sample_rate = int(sys.argv[1]) #2048000
decimation = int(sys.argv[2]) #10
baud_rate = int(sys.argv[3]) #4096
samples_per_symbol = sample_rate/baud_rate

print "SAMPLE RATE", sample_rate
print "DECIMATION", decimation
print "BAUD RATE", baud_rate
print "SAMPLES PER SYMBOL", samples_per_symbol

samples_per_symbol = samples_per_symbol / decimation

def extract_temp(samples, decimation, samples_per_symbol):
	samples = decimate(samples, decimation)
	samples = to_amplitude(samples)
	samples = np.convolve(samples, np.ones(samples_per_symbol)/samples_per_symbol, mode='same')
	samples = samples > 0.6

	offset = 0
	while 1:
		if offset >= len(samples) or samples[offset] == 1: break
		offset += 1
	offset += samples_per_symbol/4

	samples = samples[offset::samples_per_symbol]

	symbols = to_string(samples)
	print "SYMBOLS", symbols
	sys.stdout.flush()
	start = symbols.find("111000111000111000111000")
	if start < 0: return False

	bits = symbols2bits(symbols[start:])
	if len(bits) < 37: return False
	t = temp(bits)
	print "BITS", bits
	return {'temp':t}

def loop(buffer_size):
	while 1:
		samples = get_samples(buffer_size/100)
		samples = to_amplitude(samples)
		if len(samples) == 0: break

		sum = np.sum(samples > 0.1)
		if sum < 300:
			continue
		print "GOT A SIGNAL!", sum

		samples = get_samples(buffer_size)
		t = extract_temp(samples, decimation, samples_per_symbol)
		if t:
			print "VALUES", t
			#time.sleep(25) #next signal comes in 30s

buffer_size = sample_rate/8
loop(buffer_size)
print "DONE"
