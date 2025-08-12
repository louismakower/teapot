Hardware: [WIZnet W5500-EVB-Pico](https://thepihut.com/products/wiznet-w5100s-evb-pico-rp2040-board-with-ethernet?srsltid=AfmBOooQ7SRgiXSiHIm8nm7YFBl2_ydEktIVkSzv2TyWrW6W12kUSfSE) & [WIZnet WIZPoE](https://thepihut.com/products/wiznet-wizpoe-p1-poe-module).

## Hardware steps
1. Add the POE component.
>**Note:** the VC1 and VC2 labels are the wrong way round - ignore them.)
2. Connect the switch into **Ground** and **Port 27** on the Pico.

## Setup Steps

1. **Download the latest MicroPython `.uf2` file** from:  
   [https://micropython.org/download/W5500_EVB_PICO/](https://micropython.org/download/W5500_EVB_PICO/)

2. **Flash the Pico**:
   - Hold the **BOOTSEL** button while plugging it into your computer.
   - Copy the `.uf2` file onto the Pico.

3. **Reconnect** the Pico after flashing.


## Edit username, add IP address and upload:
1. Install the raspbery pi pico extension in VSCode.  Follow this [guide](https://www.hackster.io/Shilleh/how-to-use-vscode-with-raspberry-pi-pico-w-and-micropython-de88d6
) if necessary.
2. Copy the file `pico-script.py` to a workspace.
2. Change the **username** to your own name.
3. Add the **IP** and **port** being used for the server.
4. In the REPL, test `import urequests`.  If you get an error, then you need to install it manually.  See the note at the bottom.
5. Save the script on the pico, renaming it `main.py.`  In VSCode, this is done by right-clicking the file and select **Upload File to Pico**.

## Installing `urequests` (Only if Needed)

> **Note:** Most newer firmware versions already include `urequests`. If you get an error saying `urequests` not found, follow these steps, otherwise you can ignore this.  Info from [here](https://github.com/thonny/thonny/issues/2947).

1. Create a new Python virtual environment:
2. Install pipkin: `pip install pipkin`
3. Use pipkin to install urequests on the pico:
    In a fresh terminal (make sure nothing else is connecting to the pico), run: `pipkin install urequests`