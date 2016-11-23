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

filename = "temp_recording_8" #sys.argv[1]
#sample_rate = int(sys.argv[2]) #2048000

samples = get_samples(filename)
num_samples = len(samples)
samples = to_amplitude(samples)

#samples = decimate(samples, 10)

convolution_size = 200 #50
samples = numpy.convolve(samples, numpy.ones(convolution_size)/convolution_size, mode='same')
#samples = samples > 0.6

frame_size = 4000

totaltime = num_samples #float(num_samples) / float(sample_rate)
num_frames = num_samples / frame_size
t = numpy.arange(0.0, totaltime, totaltime/len(samples))
xdata = t
ydata = samples

fig = plt.figure()
ax = fig.add_subplot(111)
ax.autoscale(True)
plt.subplots_adjust(left=0.2, bottom=0.2)
ax.set_title(filename + "; total frames: " + str(num_frames))

# plot first data set
frame = 0
ln, = ax.plot(xdata[frame:frame_size],ydata[frame:frame_size])

axframe = plt.axes([0.25, 0.1, 0.65, 0.03])
sframe = Slider(axframe, 'Frame', 0, num_frames, valinit=0, valfmt='%d')

def update(val):
    frame = numpy.floor(sframe.val)
    start, end = int(frame*frame_size), int((frame+1)*frame_size)
    print "FRAME", start, end
    ln.set_xdata(xdata[start:end])
    ln.set_ydata(ydata[start:end])
    ax.relim()
    ax.autoscale_view()
    plt.draw()

sframe.on_changed(update)
plt.show()

sys.exit()

samples = samples.tolist()

widths = []
current = samples.index(1)
while current < len(samples):
	print "START", current
	try:
		n = samples.index(0, current)
		n = samples.index(1, n)
		print "FOUND", current, n
	except:
		break
	widths.append(n-current-1)
	current = n

#rng = numpy.random.RandomState(10)
#a = numpy.hstack((rng.normal(size=1000), rng.normal(loc=5, scale=2, size=1000)))

plt.hist(widths, 10, normed=1, facecolor='green', alpha=0.75)

#plt.hist(a, bins='auto')  # plt.hist passes it's arguments to np.histogram
plt.title("Histogram with 'auto' bins")
plt.show()


#NOTE: THE RESULTS OF RUNNING THIS INDICATE 3 PULSE WIDTHS: 437, 980, 1410
