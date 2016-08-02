from cothread.catools import caput
from i10controls import PvReferences, PvMonitors, ARRAYS
import numpy as np

import i10buttons


class AbstractWriter(object):

    """
    Abstract writer.

    Takes coordinated magnet moves keys and writes the values to a location.
    """

    def __init__(self):
        self.magnet_coordinator = i10buttons.MagnetCoordinator()

    def write(self, move, factor):
        """
        Applies the requested move.

        Args:
            move (i10buttons.Move): which move to perform.
            factor (float): scale factor to apply to move, usually +/- 1.
        """
        raise NotImplemented()


class PvWriter(AbstractWriter):

    """
    Write coordinated magnets moves to PV's on the machine.
    """

    def __init__(self):

        AbstractWriter.__init__(self)
        self.scale_pvs = [ctrl + ':WFSCA' for ctrl in PvReferences.CTRLS]
        self.set_scale_pvs = [name + ':SETWFSCA' for name in PvReferences.NAMES]
        self.offset_pvs = [ctrl + ':OFFSET' for ctrl in PvReferences.CTRLS]

    def write(self, key, factor, jog_scale):
        if key == 'SCALE':
            scale_jog_values = self.magnet_coordinator.jog(
                PvMonitors.get_instance().get_scales(), key, factor, jog_scale)
            set_scale_jog_values = self.magnet_coordinator.jog(
                PvMonitors.get_instance().get_set_scales(),
                key, factor, jog_scale)
            self.write_to_pvs(self.scale_pvs, scale_jog_values)
            self.write_to_pvs(self.set_scale_pvs, set_scale_jog_values)
        else:
            offset_jog_values = self.magnet_coordinator.jog(
                PvMonitors.get_instance().get_offsets(), key, factor, jog_scale)
            self.write_to_pvs(self.offset_pvs, offset_jog_values)

    def write_to_pvs(self, pvs, jog_values):
            caput(pvs, jog_values)


class SimWriter(AbstractWriter):

    """
    Write coordinated magnets moves to the manual simulation controller.
    """

    def __init__(self, controller):

        AbstractWriter.__init__(self)
        self.controller = controller

    def write(self, key, factor, jog_scale):
        if key == i10buttons.Moves.SCALE:
            jog_values = self.magnet_coordinator.jog(
                self.controller.scales, key, factor, jog_scale)
        else:
            jog_values = self.magnet_coordinator.jog(
                self.controller.offsets, key, factor, jog_scale)

        self.update_sim_values(key, jog_values)

    def update_sim_values(self, key, jog_values):
        if key == i10buttons.Moves.SCALE:
            self.controller.update_sim(ARRAYS.SCALES, jog_values)
        else:
            self.controller.update_sim(ARRAYS.OFFSETS, jog_values)

    def reset(self):
        simulated_scales =  PvMonitors.get_instance().get_scales()
        self.controller.update_sim(ARRAYS.SCALES, simulated_scales)
        simulated_offsets = PvMonitors.get_instance().get_offsets()
        self.controller.update_sim(ARRAYS.OFFSETS, simulated_offsets)



