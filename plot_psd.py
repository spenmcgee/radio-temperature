from pylab import *
from rtlsdr import *
import numpy
import sys
from scipy.signal import decimate

def get_samples(file):
	bytestream = numpy.fromfile(file, dtype=numpy.uint8)
	#num_bytes = 2*num_samples
	iq = get_iq(bytestream)
	return iq

def get_iq(bytes):
	iq = numpy.empty(len(bytes)//2, 'complex')
	iq.real, iq.imag = bytes[::2], bytes[1::2]
	iq /= (255/2)
	iq -= (1 + 1j)
	return iq

filename = sys.argv[1]
decimation = int(sys.argv[2])

f = open(filename, "rb")
samples = get_samples(f)
f.close()
if (decimation > 1):
	samples = decimate(samples, decimation)
#psd(samples, NFFT=1024, Fs=2.048, Fc=433.92)
psd(samples, NFFT=1024, Fs=2.048000, Fc=433.920000)
xlabel('Frequency (MHz)')
ylabel('Relative power (dB)')
show()
