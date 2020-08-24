import asyncio
from flags import FLAGS
from pywizlight.bulb import PilotBuilder, wizlight


class WizLightWhite:

    def __init__(self, ip: str):
        self.light = wizlight(ip)
        self.loop = asyncio.get_event_loop()

    def turn_on(self, brightness: int):
        self.loop.run_until_complete(self.light.turn_on(PilotBuilder(brightness=brightness)))

    def turn_off(self):
        self.loop.run_until_complete(self.light.turn_off())


def main():
    light1 = WizLightWhite(FLAGS.lights[0])
    light1.turn_on(0)


if __name__ == '__main__':
    main()