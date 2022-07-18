from enum import Enum

import numpy as np
from Tasks.Task import Task
from Components.BinaryInput import BinaryInput
from Events.InputEvent import InputEvent

from source.Events.OEEvent import OEEvent


class ClosedLoop(Task):
    class States(Enum):
        START_RECORD = 0
        CLOSED_LOOP = 1
        STOP_RECORD = 2

    class Inputs(Enum):
        STIM = 0
        SHAM = 1

    def __init__(self, *args):
        super().__init__(*args)
        self.last_pulse_time = 0
        self.pulse_count = 0
        self.stim_last = False
        self.complete = False

    def start(self):
        self.state = self.States.START_RECORD
        self.stim.parametrize(0, [1, 3], 180, 1800, np.array([300, -300], [0, 0]), [90, 90])
        self.events.append(OEEvent("startRecording", self.cur_time - self.start_time, {"pre": "ClosedLoop"}))
        super(ClosedLoop, self).start()

    def main_loop(self):
        super().main_loop()
        thr = self.threshold.check()
        if self.state == self.States.START_RECORD:
            if self.cur_time - self.entry_time > self.record_lockout:
                self.change_state(self.States.CLOSED_LOOP)
        if self.cur_time - self.last_pulse_time > self.min_pulse_separation and self.cur_time - self.entry_time > self.closed_loop_duration * 60:
            self.change_state(self.States.STOP_RECORD)
            self.events.append(OEEvent("stopRecording", self.cur_time - self.start_time))
        else:
            if self.cur_time - self.last_pulse_time > self.min_pulse_separation:
                if thr == BinaryInput.ENTERED:
                    if not self.stim_last:
                        self.events.append(InputEvent(self.Inputs.STIM, self.cur_time - self.start_time))
                        self.stim.start(0)
                    else:
                        self.events.append(InputEvent(self.Inputs.SHAM, self.cur_time - self.start_time))
                    self.stim_last = not self.stim_last

    def get_variables(self):
        return {
            'record_lockout': 4,
            'closed_loop_duration': 30,
            'min_pulse_separation': 2
        }

    def is_complete(self):
        return self.state == self.States.STOP_RECORD and self.cur_time - self.entry_time > self.record_lockout
