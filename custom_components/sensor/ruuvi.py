import logging
import threading

import voluptuous as vol

from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.helpers.entity import Entity
import homeassistant.helpers.config_validation as cv
from homeassistant.const import (
    CONF_MAC, CONF_NAME, CONF_MONITORED_CONDITIONS, TEMP_CELSIUS, EVENT_HOMEASSISTANT_STOP
)
from ruuvitag_sensor.ruuvitag import RuuviTagSensor

REQUIREMENTS = ['ruuvitag_sensor==0.11.0']

_LOGGER = logging.getLogger(__name__)

CONF_BEACONS = 'beacons'

SENSOR_TYPES = {
    'temperature': ['Temperature', TEMP_CELSIUS],
    'humidity': ['Humidity', '%'],
    'pressure': ['Pressure', 'hPa'],
    'battery': ['Battery', '%']
}

BEACON_SCHEMA = vol.Schema({
    vol.Required(CONF_MAC): cv.string,
    vol.Optional(CONF_MONITORED_CONDITIONS, default=list(SENSOR_TYPES)):
        vol.All(cv.ensure_list, [vol.In(SENSOR_TYPES)]),
    vol.Optional(CONF_NAME): cv.string
})

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_BEACONS): vol.Schema({cv.string: BEACON_SCHEMA})
})

def setup_platform(hass, config, add_devices, discovery_info=None):
    """Setup the sensor platform."""
    ruuvitags = config.get(CONF_BEACONS)
    devices = []

    for dev_name, properties in ruuvitags.items():
        mac = properties.get(CONF_MAC)
        prefix = properties.get(CONF_NAME, dev_name)

        for parameter in properties[CONF_MONITORED_CONDITIONS]:
            sensor_name = SENSOR_TYPES[parameter][0]
            unit = SENSOR_TYPES[parameter][1]
            name = "{} {}".format(prefix, sensor_name)

            devices.append(RuuviSensor(parameter, mac, name, unit))

    mon = Monitor(devices)

    def monitor_stop(_service_or_event):
        """Stop the monitor thread."""
        _LOGGER.info("Stopping scanner for Ruuvitag sensors")
        mon.terminate()

    add_devices(devices)
    hass.bus.listen_once(EVENT_HOMEASSISTANT_STOP, monitor_stop)
    mon.start()

class RuuviSensor(Entity):
    """Representation of a Sensor."""

    def __init__(self, parameter, mac, name, unit):
        """Initialize the sensor."""
        self.parameter = parameter
        self.mac = mac
        self._name = name
        self._unit = unit
        self._state = None

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return self._unit

class Monitor(threading.Thread):
    """Continuously scan for BLE advertisements."""

    def __init__(self, devices):
        """Construct interface object."""
        threading.Thread.__init__(self)
        self.daemon = False
        self.keep_going = threading.Event()

        self.devices = devices

    def run(self):
        """Continuously scan for BLE advertisements."""

        macs = set(map(lambda x : x.mac, self.devices))

        while not self.keep_going.wait(300):
            items = RuuviTagSensor.get_data_for_sensors(macs)
            self.process_packet(items)

    def process_packet(self, items):
        """Assign temperature to device."""
        for dev in self.devices:
            if dev.mac in items:
                data = items[dev.mac]
                dev._state = data[dev.parameter]
                dev.schedule_update_ha_state()

    def terminate(self):
        """Signal runner to stop and join thread."""
        self.keep_going.set()
        self.join()
