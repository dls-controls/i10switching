import dls_packages

import numpy as np
from cothread.catools import caget
import matplotlib.pyplot as plt
import matplotlib.animation as animation

def plot(y1_pv):

    betax = caget(y1_pv)


    lines = []
    fig, ax = plt.subplots()
    lines = ax.plot(betax)[0]

    def plot_nans():
        lines.set_ydata([np.nan] * 10000)

    def update(_):
        try:
            # Check the data is the right length, as it won't be while
            # virtac starts
            y1_data = caget(y1_pv)
            if len(y1_data) != 10000 :
                raise Exception
            lines.set_ydata(caget(y1_pv))
        except:  # Remove trace when we don't have signal
            plot_nans()

    _ = animation.FuncAnimation(fig, update)
    plt.show()

plot('BL10I-EA-USER-01:WAI1')
