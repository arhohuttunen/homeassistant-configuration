# My Home Assistant configuration

Here is my configuration for Home Assistant running on Raspberry Pi Zero W.

Currently the setup has:
* Some Philips HUE lights
* Ruuvitag sensor beacons for measuring temperature and humidity

There is also a simple custom sensor component for Ruuvi.

The custom component uses the `ruuvitag_sensor` library and needs some superuser rights for `homeassistant` user to work correctly:

```
$ sudo visudo
```

Add the following line:

```
homeassistant   ALL = (ALL) NOPASSWD: /bin/hciconfig, /usr/bin/hcitool, /usr/bin/hciattach, /usr/bin/hcidump, /usr/bin/hcitool, /bin/kill
```

I am not super happy about this solution and am thinking of creating a more secure implementation.
