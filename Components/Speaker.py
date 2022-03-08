import pygame
import math
import numpy
import threading
import time

from Components.Component import Component


class Speaker(Component):

    def __init__(self, source, component_id, component_address):
        self.state = False
        super().__init__(source, component_id, component_address)

    def play_sound(self, frequency, volume, duration):
        th = threading.Thread(target=self._play_sound, args=(frequency, volume, duration))
        th.start()

    def _play_sound(self, frequency, volume, duration):
        sample_rate = 22050  # 44100 #Hz or data points per sec
        bits = 16

        pygame.mixer.pre_init(sample_rate, -bits, 2)

        # n_samples = int(round(float(duration)*sample_rate)) # Number of sample to generate
        n_samples = int(sample_rate)  # Number of sample to generate

        # set up our numpy array to handle 16 bit ints, which is what we set our mixer to expect with "bits" up above
        buf = numpy.zeros((n_samples, 2), dtype=numpy.int16)
        # max_sample = 2**(bits - 1) - 1   # at 16 bits, max_sample = 16384
        max_sample = 128.0
        for s in range(n_samples):
            t = float(s) / sample_rate  # time in seconds
            # grab the x-coordinate of the sine wave at a given time, while constraining the sample to what our mixer is set to with "bits"
            buf[s][0] = int(round(max_sample * math.sin(2 * math.pi * float(frequency) * t)))  # left
            buf[s][1] = int(round(max_sample * math.sin(2 * math.pi * float(frequency) * t)))  # right

        sound = pygame.sndarray.make_sound(buf)
        # play once, then loop until duration time has passed
        sound.set_volume(float(volume))  # volume value 0.0 to 1.0
        play_time = int(duration * 1000)  # Duration in sec, need ms
        self.state = True
        sound.play(loops=-1, maxtime=play_time)  # - 1 = loops forever, max time in ms
        time.sleep(duration)
        self.state = False

    def play_sound_file(self, music_file, volume=0.8):
        th = threading.Thread(target=self._play_sound_file, args=(music_file, volume))
        th.start()
        th.join()
        self.state = False

    def _play_sound_file(self, music_file, volume):
        # set up the mixer
        freq = 44100  # audio CD quality
        bitsize = -16  # unsigned 16 bit
        channels = 2  # 1 is mono, 2 is stereo
        buffer = 2048  # number of samples (experiment to get best sound)
        pygame.mixer.init(freq, bitsize, channels, buffer)

        # volume value 0.0 to 1.0
        pygame.mixer.music.set_volume(volume)
        try:
            pygame.mixer.music.load(music_file)
        except pygame.error:
            return
        self.state = True
        pygame.mixer.music.play()

    def get_state(self):
        return self.state

    def get_type(self):
        return Component.Type.OUTPUT
