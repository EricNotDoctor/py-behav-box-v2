from types import MethodType
from typing import List

from Elements.Element import Element
from GUIs.SequenceGUI import SequenceGUI

from Elements.InfoBoxElement import InfoBoxElement


class ClosedLoopSequenceGUI(SequenceGUI):

    def __init__(self, task_gui, task):
        super().__init__(task_gui, task)
        self.info_boxes = []

        def event_countup(self):
            return [str(round(task.time_elapsed() / 60, 2))]

        ec = InfoBoxElement(self.task_gui, self.SF * 372, self.SF * 500, self.SF * 50, self.SF * 15, "SESSION TIME", 'BOTTOM',
                            ['0'], int(self.SF * 14), self.SF)
        ec.get_text = MethodType(event_countup, ec)
        self.info_boxes.append(ec)

    def draw(self):
        super(ClosedLoopSequenceGUI, self).draw()
        for el in self.get_elements():
            el.draw()

    def get_elements(self) -> List[Element]:
        return [*self.info_boxes]
