import sys
import numpy as np
import scipy.signal as sig

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

def extract_data(samples, decimation, samples_per_symbol):
	samples = sig.decimate(samples, decimation, ftype='fir')
	samples = to_amplitude(samples)
	samples = sig.convolve(samples, np.ones(samples_per_symbol)/samples_per_symbol, mode='same')
	samples = samples > 0.6

	offset = 0
	while 1:
		if offset >= len(samples) or samples[offset] == 1: break
		offset += 1
	offset += samples_per_symbol/4

	samples = samples[offset::samples_per_symbol]

	symbols = to_string(samples)
	print "SYMBOLS", symbols
	start = symbols.find("111000111000111000111000")
	if start < 0: return False

	bits = symbols2bits(symbols[start:])
	if len(bits) < 37: return False
	t = temp(bits)
	print "BITS", bits
	return {'temperature':t}

def loop(buffer_size):
	while 1:
		samples = get_samples(buffer_size/100)
		samples = to_amplitude(samples)
		if len(samples) == 0: break

		s = np.sum(samples > 0.1)
		if s < 300:
			continue
		print "GOT A SIGNAL!", s

		samples = get_samples(buffer_size)
		data = extract_data(samples, decimation, samples_per_symbol)
		if data:
			print "VALUES", data

buffer_size = sample_rate/8
loop(buffer_size)
print "DONE"
