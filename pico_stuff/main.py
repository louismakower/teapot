from machine import Pin, SPI
import time
import network
import urequests
from display import Display

spi = SPI(1, baudrate=10000000, sck=Pin(14), mosi=Pin(11))
screen = Display(
    spi=spi,
    dc=Pin(4, Pin.OUT),
    cs=Pin(13, Pin.OUT), 
    reset=Pin(6, Pin.OUT),
    backlight=Pin(0, Pin.OUT)
)

# CHANGE THIS FOR EACH DEVICE
USER_NAME = "doug"

# api access
SERVER_IP = "192.168.101.197"
PORT = "8000"
API_URL = f"http://{SERVER_IP}:{PORT}"

# Simple switch setup
switch_pressed = False
debounce_time = 200 # 200 ms
last_interrupt_time = 0

def switch_handler(pin):
    """Interrupt handler with debouncing"""
    global switch_pressed, last_interrupt_time
    
    current_time = time.ticks_ms()
    
    # Check if enough time has passed since last interrupt
    if time.ticks_diff(current_time, last_interrupt_time) > debounce_time:
        # Only trigger if pin is actually LOW (pressed)
        if pin.value() == 0:
            switch_pressed = True
            last_interrupt_time = current_time

def setup_ethernet():
    """Connect to internet via ethernet"""
    try:
        print("Connecting to ethernet...")
        
        # Setup W5500 ethernet chip
        spi = SPI(0, baudrate=2000000, sck=Pin(18), mosi=Pin(19), miso=Pin(16))
        nic = network.WIZNET5K(spi, Pin(17), Pin(20))
        nic.active(True)
        nic.ifconfig('dhcp')  # Get IP address automatically
        
        # Wait for connection
        for i in range(10):
            if nic.isconnected():
                print("Connected! IP address:", nic.ifconfig()[0])
                return True
            print(f"Waiting... ({i+1}/10)")
            time.sleep(1)
        
        print("Failed to connect")
        return False
    except Exception as e:
        print(e)
        screen.error_message(str(e))
        return False

def send_click(drink_type: str):
    """Send a click to the server"""
    screen.status(f"Sending {drink_type}...")
    try:
        url = f"{API_URL}/{USER_NAME}/{drink_type}"
        print(f"Sending drink to: {url}")
        
        response = urequests.post(url)
        result = response.json()
        
        print(f"Success! {result['message']}")
        response.close()
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        screen.error_message(f"Error: {str(e)}")
        return False

def send_undo():
    """Send an undo to the server"""
    screen.status("Sending undo...")
    try:
        url = f"{API_URL}/{USER_NAME}/undo"
        print(f"Sending undo to: {url}")
        
        response = urequests.post(url)
        result = response.json()
        if result["success"]:
            print(f"Success! {result['message']}")
            response.close()
            return True
        else:
            print(f"failed: {result['message']}")
            screen.error_message(f"Failed: {result['message']}")
            return False
        
    except Exception as e:
        print(f"Error: {e}")
        screen.error_message(f"Error: {str(e)}")
        return False

def get_user_data():
    try:
        url = f"{API_URL}/stats/{USER_NAME}"
        response = urequests.get(url)
        result = response.json()
        return True, {
            "tea": result["tea"],
            "coffee": result["coffee"]
        }
    except Exception as e:
        print(f"error: {e}")
        return False, {}

def update_home_screen():
    success, user_data = get_user_data()
    if success:
        screen.home_screen(USER_NAME, user_data["tea"], user_data["coffee"])


if __name__ == "__main__":
    print(f"Starting click counter for user: {USER_NAME}")

    # Connect to internet
    while not setup_ethernet():
        screen.error_message("Cannot start without internet")
        while True:
            time.sleep(1)

    # Setup button
    switch_pin = Pin(27, Pin.IN, Pin.PULL_UP)
    switch_pin.irq(trigger=Pin.IRQ_FALLING, handler=switch_handler)

    print("Ready! Press the button to send clicks")
    screen.welcome(USER_NAME)
    update_home_screen()

    # Main loop
    while True:
        if switch_pressed:
            switch_pressed = False
            press_start_time = time.ticks_ms()
            
            # Wait for button release or timeout for long press detection
            while switch_pin.value() == 0:  # Button still pressed
                if time.ticks_diff(time.ticks_ms(), press_start_time) >= 1000:
                    # Long press detected (1 second)
                    if send_undo():
                        screen.draw_undo()
                        time.sleep(0.2)
                        update_home_screen()
                        switch_pressed = False
                    else:
                        print("undo failed")
                        screen.undo_failed()
                        time.sleep(0.2)
                        update_home_screen()
                        switch_pressed = False
                    
                    # Wait for button release
                    while switch_pin.value() == 0:
                        time.sleep(0.01)
                    break
                time.sleep(0.01)
            else:
                # Button was released - check for double click
                double_count_timer = time.ticks_ms()
                double_click = False
                while time.ticks_ms() < double_count_timer + 500:
                    if switch_pressed:
                        double_click = True
                        switch_pressed = False
                        break
                
                if double_click:
                    if send_click("coffee"):
                        screen.draw_coffee_registered()
                        time.sleep(0.2)
                        update_home_screen()
                        switch_pressed = False
                    else:
                        print("failed")
                        time.sleep(0.2)
                else:
                    if send_click("tea"):
                        screen.draw_tea_registered()
                        time.sleep(0.2)
                        update_home_screen()
                        switch_pressed = False
                    else:
                        print("failed")
                        time.sleep(0.2)
        
        time.sleep(0.1)
        
