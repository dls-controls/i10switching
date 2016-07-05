# overlays gaussians

import dls_packages
import numpy as np
import matplotlib.pyplot as plt
import scipy.integrate as integ



# Number of data points
GRAPHRANGE = 10000
WINDOW = GRAPHRANGE/2
# Shift between edge of square wave and peak of Gaussian
CENTRESHIFT = 100


x = np.linspace(0, GRAPHRANGE, GRAPHRANGE)
#########################################################
# Let's create a function to model and create data
def gaussian(x, a, x0, sigma):
    return a*np.exp(-(x-x0)**2/(2*sigma**2))


# Key points of square wave
SQUARE1 = 2000 # how to find edge of trace...
SQUARE2 = 7000
# Generate square wave trigger
ysq = np.zeros(GRAPHRANGE)
ysq[SQUARE1:SQUARE2] = 1
# Add noise
ysq = ysq + 0.01 * np.random.normal(size=len(x))

# Generating clean data
y1 = gaussian(x[:WINDOW], 1, SQUARE1+CENTRESHIFT, 200)
y2 = gaussian(x[WINDOW:], 0.5, SQUARE2+CENTRESHIFT, 400)
y = np.concatenate([y1,y2])

# Adding noise to the data
yn = y + 0.01 * np.random.normal(size=len(x))

#########################################################

# Import data...


# Finds edges of square wave
edges = []
ysqdiff = np.diff(ysq).tolist()
edges = [ysqdiff.index(max(ysqdiff)), ysqdiff.index(min(ysqdiff))]

# Plot out the current state of the data and model
fig = plt.figure()
ax1 = fig.add_subplot(211)
ax1.plot(x,ysq)
ax1.plot(x,yn)

# Overlay the two gaussians
ax2 = fig.add_subplot(212)
peak1 = np.array(yn[:WINDOW])
peak2 = np.array(yn[WINDOW:])
xwindow = np.linspace(-WINDOW/2, WINDOW/2, WINDOW)
peak1shift = WINDOW/2 - edges[0] - CENTRESHIFT
peak2shift = 3*WINDOW/2 - edges[1] - CENTRESHIFT
ax2.plot(xwindow + peak1shift,peak1, label=integ.simps(peak1))
ax2.plot(xwindow + peak2shift,peak2, label=integ.simps(peak2))
ax2.legend()

plt.show()
