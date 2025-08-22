Hardware: [WIZnet W5500-EVB-Pico](https://thepihut.com/products/wiznet-w5100s-evb-pico-rp2040-board-with-ethernet?srsltid=AfmBOooQ7SRgiXSiHIm8nm7YFBl2_ydEktIVkSzv2TyWrW6W12kUSfSE), [WIZnet WIZPoE](https://thepihut.com/products/wiznet-wizpoe-p1-poe-module) & [Waveshare 1.28 inch LCD](https://thepihut.com/products/round-1-28-lcd-display-module-240x240-ips-65k-rgb).

## Hardware steps
1. Add the POE component.
   >**Note:** the VC1 and VC2 labels are the wrong way round - ignore them.
2. Connect the switch into **Ground** and **GP27** on the Pico.
3. Connect the screen with the following cabling:

   | Screen Pin | Pico Connection |
   |------------|-----------------|
   | VCC        | 3V3 (Power)     |
   | GND        | Ground          |
   | DIN        | GP11            |
   | CLK        | GP14            |
   | CS         | GP13            |
   | DC         | GP4             |
   | RST        | GP6             |
   | BL         | GP0             |

   ---


## Installing firmware on Pico

1. **Download the latest MicroPython `.uf2` file** from:  
   [https://micropython.org/download/W5500_EVB_PICO/](https://micropython.org/download/W5500_EVB_PICO/), or use the [file provided here](pico_stuff/W5500_EVB_PICO-20250809-v1.26.0.uf2).

2. **Flash the Pico**:
   - Hold the **BOOTSEL** button while plugging it into your computer.
   - Copy the `.uf2` file onto the Pico.

3. **Reconnect** the Pico after flashing.


## Edit username, add IP address and upload:
1. Install the raspbery pi pico extension in VSCode.  Follow this [guide](https://www.hackster.io/Shilleh/how-to-use-vscode-with-raspberry-pi-pico-w-and-micropython-de88d6
) if necessary.
2. Connect to the Pico by pressing `Ctrl + Shift + P`, and executing **MicroPico: Connect**
3. Change the **username** in `setup.py` to your own name.
4. Add the **IP** and **port** in `setup.py` being used for the server.
5. Copy the files inside `pico_stuff`(./pico_stuff) to the pico, by first running `Initialize MicroPico Projecet` and then running `Upload Projec to Pico`.  Both these commands can be accessed by pressing `Ctrl + Shift + P`.
6. In the REPL, test `import urequests`.  If you get an error, then you need to install it manually.  See the note at the bottom.
7. If you want to create new icons, you can use the [`convert_images.py`](pico_stuff/original_images/convert_images.py) to do so.

## MQTT instructions
1. On the pi / API server device, install moquitto.  Then edit the config file found at `/etc/mosquitto/mosquitto.conf` by adding the lines:

```
listener 1883 0.0.0.0
allow_anonymouse true
```

2. Run `systemctl start moquitto`, then `systemctl enable mosquitto`.

## Installing `urequests` (Only if Needed)

> **Note:** Most newer firmware versions already include `urequests`. If you get an error saying `urequests` not found, follow these steps, otherwise you can ignore this.  Info from [here](https://github.com/thonny/thonny/issues/2947).

1. Create a new Python virtual environment:
2. Install pipkin: `pip install pipkin`
3. Use pipkin to install urequests on the pico:
    In a fresh terminal (make sure nothing else is connecting to the pico), run: `pipkin install urequests`


