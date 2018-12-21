import logging

import voluptuous as vol

from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.helpers.entity import Entity
import homeassistant.helpers.config_validation as cv
from homeassistant.const import (
    CONF_MAC, CONF_NAME, CONF_MONITORED_CONDITIONS, TEMP_CELSIUS
)
from ruuvitag_sensor.ruuvitag import RuuviTag

REQUIREMENTS = ['ruuvitag_sensor==0.11.0']

_LOGGER = logging.getLogger(__name__)

DEFAULT_NAME = "Ruuvi"

SENSOR_TYPES = {
    'temperature': ['Temperature', TEMP_CELSIUS],
    'humidity': ['Humidity', '%'],
    'pressure': ['Pressure', 'hPa'],
    'battery': ['Battery', '%']
}

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_MAC): cv.string,
    vol.Optional(CONF_MONITORED_CONDITIONS, default=list(SENSOR_TYPES)):
        vol.All(cv.ensure_list, [vol.In(SENSOR_TYPES)]),
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string
})

def setup_platform(hass, config, add_devices, discovery_info=None):
    """Setup the sensor platform."""
    devs = []
    for parameter in config[CONF_MONITORED_CONDITIONS]:
        name = SENSOR_TYPES[parameter][0]
        unit = SENSOR_TYPES[parameter][1]

        prefix = config.get(CONF_NAME)
        if prefix:
            name = "{} {}".format(prefix, name)

        devs.append(RuuviSensor(parameter, config.get(CONF_MAC), name, unit))

    add_devices(devs)

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

    def update(self):
        """Fetch new state data for the sensor.

        This is the only method that should fetch new data for Home Assistant.
        """
        sensor = RuuviTag(self.mac)
        state = sensor.update()
        _LOGGER.info(state)
        self._state = state[self.parameter]
