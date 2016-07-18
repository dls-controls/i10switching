#i10buttons
# Contains Knobs

import cothread
from cothread.catools import caget, caput, camonitor, FORMAT_TIME
import numpy
import scipy.io
import os
import traceback


class OverCurrentException(Exception):
    def __init__(self, magnet_index):
        self.magnet_index = magnet_index


class Knobs(object):

    """
    Provides an interface to control the I10 Fast Chicane.
    Values stored in the mat file are obtained through a matlab
    middle layer simulation. The values are calculated to enable
    steering of the photon and electron beams.
    """

    # Path for matfile loading
    I10_PATH = '/dls_sw/work/common/matlab/i10'

    # PV names
    TRIMNAMES = [
        'SR10I-MO-VSTR-21',
        'SR10I-MO-VSTR-22',
        'SR10I-MO-VSTR-11',
        'SR10I-MO-VSTR-12']
    NAMES = [
        'SR09A-PC-FCHIC-01',
        'SR09A-PC-FCHIC-02',
        'SR10S-PC-FCHIC-03',
        'SR10S-PC-FCHIC-04',
        'SR10S-PC-FCHIC-05']
    CTRLS = [
        'SR09A-PC-CTRL-01',
        'SR09A-PC-CTRL-02',
        'SR10S-PC-CTRL-03',
        'SR10S-PC-CTRL-04',
        'SR10S-PC-CTRL-05']

    def __init__(self):
        """Setup physics values from matlab files."""
        S = scipy.io.loadmat(os.path.join(self.I10_PATH, 'knobsi10.mat'))

        # knob deltas
        dbpm = 1e-4  # 1e-4 mm = 100 nm
        dscale = numpy.array([1e-2, 1e-2, 0, 1e-2, 1e-2])
        dk3 = numpy.array([0, 0, 1e-2, 0, 0])

        self.dscale = dscale * 1
        self.dbpm = dbpm * 1
        self.dk3 = dk3 * 1

        # 600 Clicks to move through entire range
        self.b1 = numpy.array([23.2610, 23.2145, 10.1888, 0, 0]) / 600
        self.b2 = numpy.array([0, 0, 10.1888, 23.1068, 23.0378]) / 600

        self.jog_scale = 1.0

    def get_imin(self):
        return caget([name + ':IMIN' for name in self.NAMES])

    def get_imax(self):
        return caget([name + ':IMAX' for name in self.NAMES])

    def get_offset(self):
        return caget([ctrl + ':OFFSET' for ctrl in self.CTRLS])

    def get_scale(self):
        return caget([name + ':SETWFSCA' for name in self.NAMES])

    def get_error(self):
        return caget([name + ':ERRG' for name in self.NAMES])

    def jog(self, pvs, ofs):
        """
        Increments the list of PVs by the offset.
        Errors are created when a user is likley to exceed magnet tolerances.
        """
        ofs = ofs * self.jog_scale

        old_values = caget(pvs)
        values = old_values + ofs #;

        print
        for name, old, new in zip(pvs, old_values, values):
            print '%s:\t%f->%f' % (name, old, new) #;

        scales = [abs(scale) for scale in self.get_scale()]
        offsets = self.get_offset()
        imaxs = self.get_imax()
        imins = self.get_imin()

        # Check errors on limits.
        for n in range(len(pvs)):
            max = imaxs[n]
            min = imins[n]
            offset = offsets[n]
            scale = scales[n]
            new_val = ofs[n]
            high = offset + new_val + scale
            low = offset + new_val - scale
            if high > max or low < min:
                print 'Warning: Setting current value above limits:'
                print ('%s: High: %f\tLow: %f\tMin: %f\tMax: %f\n'
                        % (pvs[n], high, low, max, min))
                raise OverCurrentException(n)
        caput(pvs, values)

