import numpy as np, sys
from scipy.signal import decimate

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
    amp = iq.real*iq.real+iq.imag*iq.imag
    return amp
	
def bin2str(bits):
	s = ""
	for b in bits:
		if b: s += "1"
		else: s += "0"
	return s
	
def str2num(s):
	total = 0
	for i in range(len(s)):
		total += int(s[i]) * pow(2,len(s)-i-1)
	return total
	
def temp(s):
	return (str2num(s[22:32])-500)/10.0

sample_rate = int(sys.argv[1])
num_symbols = 23*2*15
convolution_size = 60

buffer_size = int(sample_rate*2)

count = 0
while 1:
	samples = get_samples(buffer_size/100)
	samples = to_amplitude(samples)

	sum = np.sum(samples > 0.01)
	if count % 200 == 0: print "SUM", sum
	count+= 1
	if (sum < 300):
		continue

	print "\nGOT A SIGNAL!", sum
	
	samples = get_samples(buffer_size*5)
	samples = to_amplitude(samples)	
	samples = decimate(samples, 5)
	max = np.max(samples)
	samples /= max
	
	samples = np.convolve(samples, np.ones((convolution_size,))/convolution_size, mode='valid')
	samples = samples > 0.4
	first = np.argmax(samples)
	last = len(samples) - np.argmax(samples[::-1])

#	if last == len(samples): 
#		print "GARBAGE"
#		continue
	print "NUM SAMPLES", len(samples), first, last

	symbols = []
	current = True
	prev = first
	for i in range(first, last):
		if current != samples[i] and current == False:
			current = not current
			prev = i
		if current != samples[i] and current == True:
			current = not current
			width = i-prev
			prev = i
			symbols.append(width)
		if len(symbols) >= 46*2: break
	
	symbols = np.float32(symbols)
	if len(symbols) < 45: 
		print "NO SYMBOLS... NOISEY?"
		continue
		
	print "SYMBOLS", symbols
	symbols /= np.max(symbols)
	print symbols
	sym = ""
	for s in symbols:
		if s > 0.3 and s < 0.7: sym += "1"
		elif s < 0.3: sym += "0"
		elif s > 0.7: sym += "10"
	print "SYMBOLS", sym
	start = sym.find("1010101010001111")
	if start >= 0:
		ans = sym[start:start+45]
		print "TEMP", temp(ans)
	else:
		print "NO PACKED FOUND"