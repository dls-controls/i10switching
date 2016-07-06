import dls_packages

import numpy as np
from cothread.catools import caget, camonitor
import matplotlib.pyplot as plt
import matplotlib.animation as animation

def plot(x_pv, y1_pv):

    s = x_pv
    betax = caget(y1_pv)

    lines = []
    fig, ax = plt.subplots()
    lines.append(ax.plot(s, betax)[0])

    def plot_nans():
        lines.set_ydata([np.nan] * len(s))

    def update(_):
        try:
            # Check the data is the right length, as it won't be while
            # virtac starts
            y1_data = caget(y1_pv)
            if len(y1_data) != len(s):
                raise Exception
            lines[0].set_ydata(caget(y1_pv))

        except:  # Remove trace when we don't have signal
            plot_nans()

    _ = animation.FuncAnimation(fig, update)
    plt.show()


#camonitor('BL10I-EA-USER-01:WAI1', plot)

plot(range(10000), 'BL10I-EA-USER-01:WAI1')

# successfully worked out how to plot it using the data!

#### I GIVE UP!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!