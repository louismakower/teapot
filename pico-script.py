from machine import Pin, SPI
import time
import network
import urequests

# CHANGE THIS FOR EACH DEVICE
USER_NAME = "doug"
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

def send_click(drink_type: str):
    """Send a click to the server"""
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
        return False
    


if __name__ == "__main__":
    print(f"Starting click counter for user: {USER_NAME}")

    # Connect to internet
    if not setup_ethernet():
        print("Cannot start without internet")
        while True:
            time.sleep(1)

    # Setup button
    switch_pin = Pin(27, Pin.IN, Pin.PULL_UP)
    switch_pin.irq(trigger=Pin.IRQ_FALLING, handler=switch_handler)

    print("Ready! Press the button to send clicks")

    # Main loop
    while True:
        if switch_pressed:
            switch_pressed = False
            double_count_timer = time.ticks_ms()
            double_click = False
            while time.ticks_ms() < double_count_timer + 500:
                if switch_pressed:
                    double_click = True
                    switch_pressed = False
                    break
            
            if double_click:
                if send_click("coffee"):
                    time.sleep(0.2)
                else:
                    print("failed")
                    time.sleep(0.2)
            else:
                if send_click("tea"):
                    time.sleep(0.2)
                else:
                    print("failed")
                    time.sleep(0.2)
        
        time.sleep(0.1)