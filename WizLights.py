import asyncio
import time
from flags import FLAGS
from pywizlight.bulb import PilotBuilder, wizlight
import re

from helpers import console_logger

LOGGER = console_logger(__name__, "DEBUG")


class WizLight:

    def __init__(self, ip: str, loop):
        self.light = wizlight(ip)
        self.loop = loop

        self.initial_state = self.get_state()

    def set_brightness(self, brightness=None):
        if brightness is None:
            state = self.get_state()
            brightness = state.get_brightness()
        brightness = int(brightness)
        brightness = max(brightness, 0)  # lower bound
        brightness = min(brightness, 255)  # upper bound
        self.loop.run_until_complete(self.light.turn_on(PilotBuilder(brightness=brightness)))

    def set_color(self, rgb=(0, 0, 0)):
        rgb = tuple([max(min(int(c), 255), 0) for c in rgb])
        self.loop.run_until_complete(self.light.turn_on(PilotBuilder(rgb=rgb)))

    def set_colortemp(self, colortemp=None):
        if colortemp is None:
            state = self.get_state()
            colortemp = state.get_colortemp()
        colortemp = max(min(int(colortemp), 6500), 2200)
        self.loop.run_until_complete(self.light.turn_on(PilotBuilder(colortemp=colortemp)))

    def turn_off(self):
        self.loop.run_until_complete(self.light.turn_off())

    def get_state(self):
        return asyncio.run(self.light.updateState())

    def get_state_dict(self):
        state = self.get_state()
        return {"state": state.get_state(),
                "scene": state.get_scene(),
                "brightness": state.get_brightness(),
                "rgb": state.get_rgb(),
                "colortemp": state.get_colortemp()}


def light_commands(lights, locations, command):
    if "everyroom" in locations:
        locations = lights.keys()
    for loc in locations:
        light = lights[loc]
        if "rgb" in command:
            sequence = re.findall(r"\brgb\s(\d{0,3}\s*\d{0,3}\s*\d{0,3})", command, flags=re.I)
            LOGGER.debug(f"rgb sequence: {sequence}")
            colors = [int(s) for s in sequence[0].split(" ")]
            for i in range(3 - len(colors)):
                colors.append(0)  # pad to have to 3 values
            LOGGER.debug(f"colors: {colors}")
            light.set_color(colors)
        if "brightness" in command:
            sequence = re.findall(r"\bbrightness\s(\b\d{1,3}\b)", command, flags=re.I)
            LOGGER.debug(f"brightness sequence: {sequence}")
            brightness = int(sequence[0])
            light.set_brightness(brightness)
        if "colortemp" in command:
            sequence = re.findall(r"\bcolortemp\s(\b\d{4}\b)", command, flags=re.I)
            LOGGER.debug(f"colortemp sequence: {sequence}")
            colortemp = int(sequence[0])
            light.set_colortemp(colortemp)
        if "turnon" in command:
            light.set_brightness()
        elif "turnoff" in command:
            light.turn_off()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    lights = {k: WizLight(v, loop) for k, v in FLAGS.lights.items()}
    light1 = lights["bedroom"]
    state_dict = light1.get_state_dict()

#    light1.set_color((255, 255, 0))  # setting color
#    time.sleep(0.5)
#    light1.set_brightness(255)  # setting brightness
#    time.sleep(0.5)
#    light1.set_colortemp(3000)  # setting color temperature (switches color to white)
#    time.sleep(1.)
#    light1.turn_off()  # turn off light

    time.sleep(1.)
    light_commands(lights, ["all"], "turnon rgb 255 0 brightness 255")
    time.sleep(2.)
    light_commands(lights, lights.keys(), "turnoff")
