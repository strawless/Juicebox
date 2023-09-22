import asyncio
from senselink import SenseLink
from juicebox import Juicebox
import socket
import json
import logging
import sys

root = logging.getLogger()
root.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)

watts = 0

def update_watts(w):
    global watts
    logging.info("Updating wattage %f" %(w))
    watts = w

async def change_mutable_plug_power(plug):
    global watts
    while True:
        plug.data_source.power = float(watts)
        await asyncio.sleep(1)
            

async def main():
    # Get config
    config = open('juicelink.yml', 'r')
    
    # Create controller, with config
    controller = SenseLink(config, 9999)
    # Create instances
    controller.create_instances()

    j = Juicebox("192.168.50.202", update_watts)

    # Get Mutable controller object, and create task to update it
    mutable_plug = controller.plug_for_mac("70:AC:00:00:00:00")
    plug_update = change_mutable_plug_power(mutable_plug)

    # Get base SenseLink tasks (for other controllers in the config, perhaps), and
    # add our new top level plug task, as well as the main SenseLink controller itself
    tasks = controller.tasks
    tasks.add(plug_update)
    tasks.add(controller.server_start())
    tasks.add(j.readForever())
    print("Starting SenseLink controller")
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Interrupt received, stopping SenseLink")
