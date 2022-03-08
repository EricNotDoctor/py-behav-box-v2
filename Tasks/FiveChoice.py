import random
from enum import Enum

from Components.NosePoke import NosePoke
from Events.InputEvent import InputEvent
from Tasks.Task import Task


class FiveChoice(Task):
    """
        Class defining the Five Choice Serial Reaction Time Task.

        Attributes
        ---------
        state : Enum
            An enumerated variable indicating the state the task is currently in
        entry_time : float
            The time in seconds when the current state began
        cur_time : float
            The current time in seconds for the task loop
        events : List<Event>
            List of events related to the current loop of the task

        Methods
        -------
        change_state(new_state)
            Updates the task state
        start()
            Begins the task
        pause()
            Pauses the task
        stop()
            Ends the task
        main_loop()
            Repeatedly called throughout the lifetime of the task. State transitions are executed within.
        get_variables()
            Abstract method defining all variables necessary for the task as a dictionary relating variable names to
            default values.
        is_complete()
            Abstract method that returns True if the task is complete
        """

    class States(Enum):
        INITIATION = 0
        INTER_TRIAL_INTERVAL = 1
        STIMULUS_ON = 2
        LIMITED_HOLD = 3
        POST_RESPONSE_INTERVAL = 4

    class Inputs(Enum):
        TROUGH_ENTERED = 0
        TROUGH_EXIT = 1
        NP1_ENTERED = 2
        NP1_EXIT = 3
        NP2_ENTERED = 4
        NP2_EXIT = 5
        NP3_ENTERED = 6
        NP3_EXIT = 7
        NP4_ENTERED = 8
        NP4_EXIT = 9
        NP5_ENTERED = 10
        NP5_EXIT = 11

    def __init__(self, ws, source, address_file, protocol=None):
        super().__init__(ws, source, address_file, protocol)
        self.cur_trial = 0
        self.state = self.States.INITIATION
        self.food_light.toggle(True)

    def main_loop(self):
        super().main_loop()
        self.events = []
        pokes = []
        # Output events for pokes that were entered/exited
        for i in range(5):
            pokes.append(self.nose_pokes[i].check())
            if pokes[i] == NosePoke.POKE_ENTERED:
                if i == 0:
                    self.events.append(InputEvent(self.Inputs.NP1_ENTERED, self.cur_time - self.start_time))
                elif i == 1:
                    self.events.append(InputEvent(self.Inputs.NP2_ENTERED, self.cur_time - self.start_time))
                elif i == 2:
                    self.events.append(InputEvent(self.Inputs.NP3_ENTERED, self.cur_time - self.start_time))
                elif i == 3:
                    self.events.append(InputEvent(self.Inputs.NP4_ENTERED, self.cur_time - self.start_time))
                elif i == 4:
                    self.events.append(InputEvent(self.Inputs.NP5_ENTERED, self.cur_time - self.start_time))
            elif pokes[i] == NosePoke.POKE_EXIT:
                if i == 0:
                    self.events.append(InputEvent(self.Inputs.NP1_EXIT, self.cur_time - self.start_time))
                elif i == 1:
                    self.events.append(InputEvent(self.Inputs.NP2_EXIT, self.cur_time - self.start_time))
                elif i == 2:
                    self.events.append(InputEvent(self.Inputs.NP3_EXIT, self.cur_time - self.start_time))
                elif i == 3:
                    self.events.append(InputEvent(self.Inputs.NP4_EXIT, self.cur_time - self.start_time))
                elif i == 4:
                    self.events.append(InputEvent(self.Inputs.NP5_EXIT, self.cur_time - self.start_time))
        # Output if the food trough was entered/exited
        trough_entered = self.food_trough.check()
        if trough_entered == NosePoke.POKE_ENTERED:
            self.events.append(InputEvent(self.Inputs.TROUGH_ENTERED, self.cur_time - self.start_time))
        elif trough_entered == NosePoke.POKE_EXIT:
            self.events.append(InputEvent(self.Inputs.TROUGH_EXIT, self.cur_time - self.start_time))
            if self.state == self.States.INITIATION:  # The rat has not initiated the trial yet
                if trough_entered == NosePoke.POKE_ENTERED:  # Trial is initiated when the rat nosepokes the trough
                    self.food_light.toggle(False)  # Turn the food light off
                    self.change_state(self.States.INTER_TRIAL_INTERVAL)
            elif self.state == self.States.INTER_TRIAL_INTERVAL:  # The rat has initiated a trial and must wait before nose poking
                if any(map(lambda x: x == NosePoke.POKE_ENTERED, pokes)):  # The rat failed to withold a response
                    self.change_state(self.States.POST_RESPONSE_INTERVAL, {"response": "premature"})
                elif self.cur_time - self.entry_time > self.inter_trial_interval:  # The rat waited the necessary time
                    self.nose_poke_lights[self.sequence[self.cur_trial]].toggle(True)  # Turn the stimulus light on
                    self.change_state(self.States.STIMULUS_ON)
            elif self.state == self.States.STIMULUS_ON:  # The correct stimulus lights up
                if any(map(lambda x: x == NosePoke.POKE_ENTERED, pokes)):  # The rat made a selection
                    selection = next(i for i in range(5) if pokes[i] == NosePoke.POKE_ENTERED)
                    if selection == self.sequence[self.cur_trial]:  # If the selection was correct, provide a reward
                        self.food.dispense()
                        metadata = {"response": "correct"}
                    else:
                        metadata = {"response": "incorrect"}
                    self.nose_poke_lights[self.sequence[self.cur_trial]].toggle(False)  # Turn the stimulus light off
                    self.change_state(self.States.POST_RESPONSE_INTERVAL, metadata)
                elif self.cur_time - self.entry_time > self.stimulus_duration:  # The stimulus was shown for the allotted time
                    self.nose_poke_lights[self.sequence[self.cur_trial]].toggle(False)  # Turn the stimulus light off
                    self.change_state(self.States.LIMITED_HOLD)
            elif self.state == self.States.LIMITED_HOLD:  # The correct stimulus is turned off and the rat has time to decide
                if any(map(lambda x: x == NosePoke.POKE_ENTERED, pokes)):  # The rat made a selection
                    selection = next(i for i in range(5) if pokes[i] == NosePoke.POKE_ENTERED)
                    if selection == self.sequence[self.cur_trial]:  # If the selection was correct, provide a reward
                        self.food.dispense()
                        metadata = {"response": "correct"}
                    else:
                        metadata = {"response": "incorrect"}
                    self.change_state(self.States.POST_RESPONSE_INTERVAL, metadata)
                elif self.cur_time - self.entry_time > self.limited_hold_duration:  # The rat failed to respond
                    self.change_state(self.States.POST_RESPONSE_INTERVAL, {"response", "none"})
            elif self.state == self.States.POST_RESPONSE_INTERVAL:  # The rat has responded and an initiation lockout begins
                if self.cur_time - self.entry_time > self.post_response_interval:  # The post response period has ended
                    self.change_state(self.States.INITIATION)
                    self.food_light.toggle(True)  # Turn the food light on
                    self.cur_trial += 1
        return self.events

    def get_variables(self):
        return {
            'max_duration': 30,  # The max time the task can take in seconds
            'max_trials': 100,  # The maximum number of trials the rat can do
            'inter_trial_interval': 5,  # Time between initiation and stimulus presentation
            'stimulus_duration': 0.5,  # Time the stimulus is presented for
            'limited_hold_duration': 5,  # Time after stimulus presentation during which the rat can decide
            'post_response_interval': 5,  # Time after response before the rat can initiate again
            'sequence': [random.randint(0, 4) for _ in range(100)]  # Sequence of stimulus presentations
        }

    def is_complete(self):
        return self.cur_trial == self.max_trials or self.cur_time - self.start_time > self.max_duration * 60
