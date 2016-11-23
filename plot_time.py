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

filename = sys.argv[1]
sample_rate = int(sys.argv[2]) #2048000
decimation = int(sys.argv[3]) #50
frame_size = int(sys.argv[4]) #1024

samples = get_samples(filename)
num_samples = len(samples)
print "NUM SAMPLES", num_samples
totaltime = float(num_samples) / float(sample_rate)
num_frames = num_samples / decimation / frame_size

print "DECIMATION", decimation
print "SAMPLE RATE", sample_rate
print "FRAME SIZE", frame_size
print "NUM SAMPLES", num_samples
print "TOTAL TIME", totaltime
print "NUM FRAMES", num_frames

#samples = samples[::decimation]
samples = decimate(samples, decimation)
print "AFTER DECIMATION", len(samples)
samples = to_amplitude(samples)
print "AFTER AMP", len(samples)

convolution_size = 50 #50
samples2 = numpy.convolve(samples, numpy.ones(convolution_size)/convolution_size, mode='same')
samples2 = samples2 > 0.6

final_decimation = 50
dec = samples2[::final_decimation]
samples3 = zeros(len(samples2))
count = 0
for d in dec:
	samples3[count*final_decimation] = d
	count += 1

s = to_string(dec)
print s[s.find("1"):s.find("1")+3000]

#samples = samples > 0.9

t = numpy.arange(0.0, totaltime, totaltime/len(samples))
xdata = t
ydata = samples

fig = plt.figure()
ax = fig.add_subplot(111)
ax.autoscale(True)
plt.subplots_adjust(left=0.2, bottom=0.2)
ax.set_title(filename + "; total frames: " + str(num_frames))

ax2 = fig.add_subplot(111)
ax2.autoscale(True)

ax3 = fig.add_subplot(111)
ax3.autoscale(True)

# plot first data set
frame = 0
ln, = ax.plot(xdata[frame:frame_size],ydata[frame:frame_size])
ln2, = ax2.plot(xdata[frame:frame_size],samples2[frame:frame_size])
ln3, = ax3.plot(xdata[frame:frame_size],samples3[frame:frame_size], 'ro')

axframe = plt.axes([0.25, 0.1, 0.65, 0.03])
sframe = Slider(axframe, 'Frame', 0, num_frames, valinit=0, valfmt='%d')

def update(val):
	frame = numpy.floor(sframe.val)
	start, end = int(frame*frame_size), int((frame+1)*frame_size)
	#print to_string(samples2[start:end])
	print "FRAME", start, end
	ln.set_xdata(xdata[start:end])
	ln.set_ydata(ydata[start:end])
	ln2.set_xdata(xdata[start:end])
	ln2.set_ydata(samples2[start:end])
	ln3.set_xdata(xdata[start:end])
	ln3.set_ydata(samples3[start:end])
	ax.relim()
	ax.autoscale_view()
	ax2.relim()
	ax2.autoscale_view()
	ax3.relim()
	ax3.autoscale_view()
	plt.draw()

sframe.on_changed(update)
plt.show()
