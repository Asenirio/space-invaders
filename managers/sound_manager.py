import pygame
import array
import math
import random

class SoundManager:
    def __init__(self, settings_manager=None):
        self.settings_manager = settings_manager
        
        if not pygame.mixer.get_init():
            pygame.mixer.init(frequency=22050, size=-16, channels=2)

        self.laser_sound = self._generate_laser_sound()
        self.explosion_sound = self._generate_explosion_sound()
        self.update_volume()

    def is_enabled(self):
        if self.settings_manager:
            return self.settings_manager.get("sound_enabled", True)
        return True

    def update_volume(self):
        volume = 1.0
        if self.settings_manager:
            volume = self.settings_manager.get("volume", 100) / 100.0
        
        if self.laser_sound:
            self.laser_sound.set_volume(volume)
        if self.explosion_sound:
            self.explosion_sound.set_volume(volume)

    def _generate_laser_sound(self):
        """Generates a procedural 8-bit retro synth laser tone."""
        try:
            sample_rate = 22050
            duration = 0.12
            n_samples = int(sample_rate * duration)
            buf = array.array('h')

            for i in range(n_samples):
                t = i / sample_rate
                freq = 900 - (700 * (i / n_samples))
                value = int(32767 * 0.3 * math.sin(2 * math.pi * freq * t))
                buf.append(value)
                buf.append(value)

            return pygame.mixer.Sound(buffer=buf)
        except Exception as e:
            print(f"Error generating laser sound: {e}")
            return None

    def _generate_explosion_sound(self):
        """Generates a procedural 8-bit retro explosion noise."""
        try:
            sample_rate = 22050
            duration = 0.25
            n_samples = int(sample_rate * duration)
            buf = array.array('h')

            for i in range(n_samples):
                envelope = 1.0 - (i / n_samples)
                value = int(32767 * 0.4 * (random.random() * 2 - 1) * envelope)
                buf.append(value)
                buf.append(value)

            return pygame.mixer.Sound(buffer=buf)
        except Exception as e:
            print(f"Error generating explosion sound: {e}")
            return None

    def play_laser(self):
        if self.is_enabled() and self.laser_sound:
            self.laser_sound.play()

    def play_explosion(self):
        if self.is_enabled() and self.explosion_sound:
            self.explosion_sound.play()