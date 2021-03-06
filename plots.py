#!/usr/bin/env dls-python2.7
"""Selection of Qt plots that show information about the I10 chicane.

Plots are available for use in eithier the beamline or accelerator GUIs.
"""


import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.backends.backend_qt4agg import (
    FigureCanvasQTAgg as FigureCanvas)
import scipy.integrate as integ
import controls
import cothread


class BaseFigureCanvas(FigureCanvas):

    """Initialise the figures for plotting."""

    def __init__(self):
        """
        Set up plot.

        Initialise figure canvas, set plot background to be blue and
        transparent (goes blue for simulation mode), get instance of PvMonitors
        to receive updated PV values.
        """
        self.figure = plt.figure()
        FigureCanvas.__init__(self, self.figure)
        self.figure.patch.set_facecolor('blue')
        self.figure.patch.set_alpha(0.0)
        self.pv_monitor = controls.PvMonitors.get_instance()


class Simulation(BaseFigureCanvas):

    """Plot the simulation of the I10 fast chicane."""

    def __init__(self, straight):
        """Initialise the straight, axes, animation and graph shading."""
        BaseFigureCanvas.__init__(self)
        self.straight = straight
        self.fill1 = None
        self.fill2 = None
        self.ax = self.fig_setup()
        self.beams = self.data_setup()
        self.anim = animation.FuncAnimation(self.figure, self.animate,
                    init_func=self.init_data, frames=1000, interval=20)

    def fig_setup(self):
        """Set up axes."""
        ax1 = self.figure.add_subplot(1, 1, 1)
        ax1.set_xlim(self.straight.data.path[0].s,
                     self.straight.data.path[-1].s)
        ax1.set_ylim(-0.01, 0.01)
        ax1.set_xlabel('Distance along the straight/m')
        ax1.set_ylabel('Deflection off axis/m') # Is it in m or other size??

        # Plot positions of kickers and IDs.
        for i in self.straight.data.kickers:
            ax1.axvline(x=i.s, color='k', linestyle='dashed')
        for i in self.straight.data.ids:
            ax1.axvline(x=i.s, color='b', linestyle='dashed')

        plt.tight_layout()

        return ax1

    def data_setup(self):
        """Set up data for the animation."""
        beams = [
                self.ax.plot([], [], 'b')[0],
                self.ax.plot([], [], 'r')[0],
                self.ax.plot([], [], 'r')[0]
                ]

        return beams

    def init_data(self):

        for line in self.beams:
            line.set_data([], [])

        return self.beams

    def beam_plot(self, t):
        """
        Extract electron and photon beam positions from data for plotting.

        Args:
            t (int): time counter for the animation
        Returns:
            e_positions (numpy array): electron beam data without duplicated
            values for plotting
            p_positions (numpy array): photon position data (remove velocity
            data as not needed for plotting)
        """
        e_positions = np.array(self.straight.step(t)[0])[:, 0].tolist()
        # Remove duplicates in data.
        for i in range(len(self.straight.data.get_elements('drift'))):
            if e_positions[i] == e_positions[i+1]:
                e_positions.pop(i+1)

        p_positions = np.array(self.straight.step(t)[1])[:, [0, 2]]

        return e_positions, p_positions

    def animate(self, t):
        """
        Animation function.

        Set data for animation frame at time t.

        Args:
            t (int): time counter for the animation
        Returns:
            beams (list): list of lines to be plotted
        """
        data = self.beam_plot(t)
        e_data = data[0]
        p_data = data[1]

        beams = self.init_data()
        beams[0].set_data(self.straight.data.xaxis, e_data)
        for line, x, y in zip(beams[1:],
                              self.straight.data.photon_coordinates, p_data):
            line.set_data(x, y)

        return beams

    def update_colourin(self):
        """Shade in the range over which each photon beam sweeps."""
        if self.fill1:
            self.ax.collections.remove(self.fill1)
        if self.fill2:
            self.ax.collections.remove(self.fill2)

        strengths = [np.array([1, 1, 1, 0, 0]), np.array([0, 0, 1, 1, 1])]
        edges = [[], []]
        for s in range(2):
            edges[s] = np.array(
                self.straight.p_beam_range(strengths[s]))[:, [0, 2]]

        beam1max = edges[0][0]
        beam1min = edges[1][0]
        beam2max = edges[1][1]
        beam2min = edges[0][1]

        self.fill1 = self.ax.fill_between(
                               self.straight.data.photon_coordinates[0],
                               beam1min, beam1max, facecolor='blue', alpha=0.2)
        self.fill2 = self.ax.fill_between(
                               self.straight.data.photon_coordinates[1],
                               beam2min, beam2max, facecolor='green', alpha=0.2)

    def magnet_limits(self):
        """Show maximum currents that can be passed through the magnets."""
        max_currents = self.pv_monitor.get_max_currents()

        strengths = [np.array([max_currents[0],
                              -max_currents[1],
                               max_currents[2], 0, 0]),
                     np.array([0, 0, max_currents[2],
                              -max_currents[3],
                               max_currents[4]])]

        edges = [[], []]
        for s in range(2):
            edges[s] = np.array(self.straight.p_beam_lim(strengths[s])
                               )[:, [0, 2]]

        beam1max = edges[0][0]
        beam2max = edges[1][1]

        self.ax.plot(self.straight.data.photon_coordinates[0],
                                   beam1max, 'r--')
        self.ax.plot(self.straight.data.photon_coordinates[1],
                                   beam2max, 'r--')


class OverlaidWaveforms(BaseFigureCanvas):

    """
    Overlay the two intensity peaks of the x-ray beams.

    'Cuts out' two peaks from X-ray intensity trace corresponding to the two
    X-ray beams and displays them overlaid. Calculates areas under peaks and
    displays as a legend, plots Gaussian for visual comparison of peak shapes.
    """

    def __init__(self, ctrls):
        BaseFigureCanvas.__init__(self)

        self.ax = self.figure.add_subplot(2, 1, 1)
        self.controls = ctrls
        self.pv_monitor = self.controls.PvMonitors.get_instance()
        self.pv_monitor.register_trace_listener(self.update_waveforms)
        self.pv_monitor.register_trace_listener(self.update_overlaid_plot)

        trigger = self.pv_monitor.arrays[self.controls.Arrays.WAVEFORMS][0]
        trace = self.pv_monitor.arrays[self.controls.Arrays.WAVEFORMS][1]

        traces_x_axis = range(len(trace))
        self.trace_lines = [
                     self.ax.plot(traces_x_axis, trigger, 'b')[0],
                     self.ax.plot(traces_x_axis, trace, 'g')[0]
                     ]
        self.ax.set_xlabel('Time samples')
        self.ax.set_ylabel('Voltage/V')
        self.ax.set_title('Square wave trigger signal and beam intensity trace')

        self.ax2 = self.figure.add_subplot(2, 1, 2)
        first_peak, second_peak = self.get_windowed_data(trigger, trace)
        self.overlaid_x_axis = range(len(first_peak))
        self.overlaid_lines = [
                     self.ax2.plot(self.overlaid_x_axis, first_peak, 'b')[0],
                     self.ax2.plot(self.overlaid_x_axis, second_peak, 'g')[0]
                     ]
        self.ax2.set_xlabel('Time samples')
        self.ax2.set_ylabel('Voltage/V')
        self.ax2.set_title('Beam intensity peaks overlaid')
        plt.tight_layout()

    def update_waveforms(self, key, _):
        """Update plot data whenever it changes."""
        if key == self.controls.Arrays.WAVEFORMS:
            self.trace_lines[0].set_ydata(self.pv_monitor.arrays[key][0])
            self.trace_lines[1].set_ydata(self.pv_monitor.arrays[key][1])
            self.draw()

    def update_overlaid_plot(self, key, _):
        """Update overlaid plot data whenever it changes, calculate areas."""
        if key == self.controls.Arrays.WAVEFORMS:

            trigger = self.pv_monitor.arrays[self.controls.Arrays.WAVEFORMS][0]
            trace = self.pv_monitor.arrays[self.controls.Arrays.WAVEFORMS][1]
            waveforms = [trigger, trace]

            first_peak, second_peak = self.get_windowed_data(waveforms[0], waveforms[1])
            self.overlaid_lines[0].set_ydata(first_peak)
            self.overlaid_lines[0].set_xdata(range(len(first_peak)))
            self.overlaid_lines[1].set_ydata(second_peak)
            self.overlaid_lines[1].set_xdata(range(len(second_peak)))

            areas = [integ.simps(first_peak), integ.simps(second_peak)]
            labels = ['%.1f' % areas[0], '%.1f' % areas[1]]

#            for area in areas:
#                if area < 0.1:
#                    raise RangeError # calculation warning error for example
            self.ax2.legend([self.overlaid_lines[0], self.overlaid_lines[1]],
                           labels)

        self.draw()

    def get_windowed_data(self, trigger, trace):
        """Overlay the two peaks."""
        try:
            diff = np.diff(trigger)

            length = len(trace)
            # TODO: this parameter probably shouldn't be hard coded
            stepvalue = 0.5

            if min(diff) > -1 * stepvalue or max(diff) < stepvalue:
                raise RangeError

            maxtrig = next(x for x in diff if x > stepvalue)
            mintrig = next(x for x in diff if x < -1 * stepvalue)
            edges = [np.where(diff == maxtrig)[0][0],
                     np.where(diff == mintrig)[0][0]]


            cothread.Yield()
            trigger_length = (edges[1]-edges[0])*2

            if length < trigger_length:
                raise RangeError
            if edges[1] > edges[0]:  # So that colours don't swap around
                first_peak = np.roll(trace[:trigger_length], - edges[0]
                                - trigger_length/4)[:trigger_length/2]
                second_peak = np.roll(trace[:trigger_length], - edges[1]
                                - trigger_length/4)[:trigger_length/2]
            else:
                first_peak = np.roll(trace[:trigger_length], - edges[1]
                                - trigger_length/4)[:trigger_length/2]
                second_peak = np.roll(trace[:trigger_length], - edges[0]
                                - trigger_length/4)[:trigger_length/2]

            return first_peak, second_peak

        except RangeError:
            print 'Trace is partially cut off' # status bar? callback?
            first_peak = [float('nan'), float('nan')]
            second_peak = [float('nan'), float('nan')]
            return first_peak, second_peak

    def gaussian(self, amp_step, sigma_step):
        """
        Plot a theoretical Gaussian for comparison with the x-ray peaks.

        Initialise the amplitude and standard deviation from a caget of the
        trigger and trace. Amplitude is the maximum value of the trace plus
        amp_step; sigma is 1/8th of the length of a full trigger cycle plus
        sigma_step.
    
        Args:
            amp_step (int): amount by which the amplitude is increased or
            decreased from the default value
            sigma_step (int): as above but for sigma, the standard deviation
        """
        l = len(self.overlaid_x_axis)
        x = np.linspace(0, l, l) - l/2 # centre of data

        # This is new code to 'guess' the size of the Gaussian from the
        # existing data rather than from hard-coded numbers.
        # TODO: test this! Possibly link up to the get_windowed_data function
        # as it uses a lot of the same functionality
        trigger = self.pv_monitor.arrays[self.controls.Arrays.WAVEFORMS][0]
        trace = self.pv_monitor.arrays[self.controls.Arrays.WAVEFORMS][1]
        amplitude = max(trace) + amp_step
        diff = np.diff(trigger)
        stepvalue = 0.5
        if min(diff) > -1 * stepvalue or max(diff) < stepvalue:
            raise RangeError
        else:
            maxtrig = next(x for x in diff if x > stepvalue)
            mintrig = next(x for x in diff if x < -1 * stepvalue)
            edges = [np.where(diff == maxtrig)[0][0],
                     np.where(diff == mintrig)[0][0]]
            half_trigger_length = (edges[1]-edges[0])
            sigma = half_trigger_length/4 + sigma_step

        gauss = self.ax2.plot(amplitude * np.exp(-x**2 / (2 * sigma**2)), 'r')
        self.overlaid_lines.append(gauss)
        self.draw()

    def clear_gaussian(self):
        """Remove the Gaussian."""
        self.ax2.lines.pop(-1)
        self.ax2.relim()
        self.ax2.autoscale_view()
        self.draw()


class RangeError(Exception):

    """Raised when the trace data is partially cut off."""

    pass
