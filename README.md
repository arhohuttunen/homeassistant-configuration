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

# Installing Home Assistant on Raspberry Pi Zero W

These instructions are provided as-is and are gathered from various sources to make the installation process smoother.

Please note that I don’t reply to questions about installation and do not provide support. There are far more capable people to do that in other forums.

## Installing Rasbian

You will need to download the official [Raspbian Stretch Lite](https://www.raspberrypi.org/downloads/raspbian/) image and flash it to an SD card. Just follow the [Installing operating system images](https://www.raspberrypi.org/documentation/installation/installing-images/README.md) instructions.

Please note that you will need to format your SD card first. If you don’t do this you may end up with some really random errors.

### Wireless network

After flashing the image to your SD Card open the partition `boot` and create a new file `wpa_supplicant.conf`:

```
country=FI
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1

network={
    ssid="YOUR_SSID"
    psk="YOUR_PASSWORD"
}
```

During the Raspberry boot the file will automatically be copied in the right folder and the network connection will be established.

If you run into any trouble check the [Setting WiFi up via the command line](https://www.raspberrypi.org/documentation/configuration/wireless/wireless-cli.md) instructions.

## Installing Home Assistant

Installation on Raspbian is pretty straightforward if you follow the  [Manual installation on a Raspberry Pi](https://www.home-assistant.io/docs/installation/raspberry-pi/) guide.

I have noticed that sometimes some of steps may fail because of download errors. This can be resolved by executing the command again.

### Autostart

To control Home Assistant with `systemd` a service file is needed:

```bash
$ sudo nano -w /etc/systemd/system/home-assistant@homeassistant.service
```

Paste the following as the contents of the file:

```
[Unit]
Description=Home Assistant
After=network-online.target

[Service]
Type=simple
User=%i
ExecStart=/srv/homeassistant/bin/hass -c "/home/homeassistant/.homeassistant"

[Install]
WantedBy=multi-user.target
```

Now you need to reload `systemd` to make the daemon aware of the new configuration and then start the service:

```bash
$ sudo systemctl --system daemon-reload
$ sudo systemctl start home-assistant@homeassistant
```

To get the log output of Home Assistan you can now use:

```bash
$ sudo journalctl -f -u home-assistant@homeassistant
```

If everything starts up ok, you can make Home Assistant start automatically at boot:

```bash
$ sudo systemctl enable home-assistant@homeassistant
```

## Backup to Github

The process of backing up to Github is pretty well documented in [Configuration Backup to GitHub](https://www.home-assistant.io/docs/ecosystem/backup/backup_github/) instructions.

It’s quite important that you do not push any sensitive information to Github.

### Setting up SSH keys

To make it easier to push your configuration to Github I recommend setting up SSH keys. As the `homeassistant` user first make sure the SSH key directory exists:

```bash
$ mkdir -p $HOME/.ssh
$ chmod 0700 $HOME/.ssh
```

Now you can generate a key:

```bash
$ ssh-keygen -t rsa -C "homeassistant@raspberrypi.local"
```

Once the keys have been generated you have to login into your Github account, go to your account `Settings`, navigate to `SSH and GPG Keys` and add a new SSH key. 

Paste the contents of file in the `~/.ssh/id_rsa.pub` into your public key and you are all set.
