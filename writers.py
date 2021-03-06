#!/usr/bin/env dls-python2.7
"""Write coordinated magnet moves to different outputs.

A PvWriter and a Simulation writer are available to take magnet_jogs.Moves
and apply them to their respective interfaces.
"""


from cothread.catools import caput
from controls import PvReferences, PvMonitors, Arrays

import magnet_jogs


class AbstractWriter(object):

    """
    Abstract writer.

    Takes coordinated magnet moves keys and writes the values to a location.
    """

    def __init__(self):
        self.magnet_coordinator = magnet_jogs.MagnetCoordinator()

    def write(self, move, factor):
        """
        Apply the requested move.

        Args:
            move (magnet_jogs.Move): which move to perform.
            factor (float): scale factor to apply to move.
        """
        raise NotImplementedError()


class PvWriter(AbstractWriter):

    """Write coordinated magnets moves to PV's on the machine."""

    def __init__(self):

        AbstractWriter.__init__(self)
        self.scale_pvs = [ctrl + ':WFSCA' for ctrl in PvReferences.CTRLS]
        self.set_scale_pvs = [name + ':SETWFSCA' for name in PvReferences.NAMES]
        self.offset_pvs = [ctrl + ':OFFSET' for ctrl in PvReferences.CTRLS]

    def write(self, move, factor):
        if move == 'SCALE':
            scale_jog_values = self.magnet_coordinator.jog(
                PvMonitors.get_instance().get_scales(), move, factor)
            set_scale_jog_values = self.magnet_coordinator.jog(
                PvMonitors.get_instance().get_set_scales(), move, factor)
            self.write_to_pvs(self.scale_pvs, scale_jog_values)
            self.write_to_pvs(self.set_scale_pvs, set_scale_jog_values)
        else:
            offset_jog_values = self.magnet_coordinator.jog(
                PvMonitors.get_instance().get_offsets(), move, factor)
            self.write_to_pvs(self.offset_pvs, offset_jog_values)

    def write_to_pvs(self, pvs, jog_values):
        caput(pvs, jog_values)


class SimWriter(AbstractWriter):

    """Write coordinated magnets moves to the manual simulation controller."""

    def __init__(self, controller):
        """
        Class initialised with instance of the simulation controller.

        Args:

        controller (straight.SimModeController): write to the controller's
        stored /scales and offsets
        """
        AbstractWriter.__init__(self)
        self.controller = controller

    def write(self, move, factor):
        if move == magnet_jogs.Moves.SCALE:
            jog_values = self.magnet_coordinator.jog(
                self.controller.scales, move, factor)
        else:
            jog_values = self.magnet_coordinator.jog(
                self.controller.offsets, move, factor)
        self.check_bounds(move, jog_values)
        self.update_sim_values(move, jog_values)

    def update_sim_values(self, key, jog_values):
        """Pass jog values to the controller."""
        if key == magnet_jogs.Moves.SCALE:
            self.controller.update_sim(Arrays.SCALES, jog_values)
        else:
            self.controller.update_sim(Arrays.OFFSETS, jog_values)

    def reset(self):
        """Reset simulation with the PVs to reflect the real chicane."""
        simulated_scales = PvMonitors.get_instance().get_scales()
        self.controller.update_sim(Arrays.SCALES, simulated_scales)
        simulated_offsets = PvMonitors.get_instance().get_offsets()
        self.controller.update_sim(Arrays.OFFSETS, simulated_offsets)

    def check_bounds(self, key, jog_values):
        """Raise exception if new value exceeds magnet current limit."""
        pvm = PvMonitors.get_instance()
        scales = self.controller.scales
        offsets = self.controller.offsets
        imaxs = pvm.get_max_currents()
        imins = pvm.get_min_currents()

        # Check errors on limits.
        for idx, (max_val, min_val, offset, scale, new_val) in enumerate(
                zip(imaxs, imins, offsets, scales, jog_values)):
            if key == magnet_jogs.Moves.SCALE:
                high = offset + new_val
                low = offset - new_val
            else:
                high = new_val + scale
                low = new_val - scale
            if high > max_val or low < min_val:
                raise magnet_jogs.OverCurrentException(idx)
