import json
import time
from mqtt import MQTTClient
from setup import MQTT_BROKER, MQTT_TOPIC, USER_NAME
from machine import SPI, Pin
import network

message_queue = []
celebration_queue = []


def setup_ethernet():
    """Connect via ethernet"""
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
        print(str(e))
        return False

def setup_mqtt():
    """Setup MQTT client and subscribe"""
    global mqtt_client
    try:
        client_id = f"teacounter_{USER_NAME}"
        mqtt_client = MQTTClient(client_id, MQTT_BROKER)
        mqtt_client.set_callback(mqtt_callback)
        mqtt_client.connect()
        print("Subscribing to:", f"{MQTT_TOPIC}/all", f"{MQTT_TOPIC}/{USER_NAME}")
        mqtt_client.subscribe(f"{MQTT_TOPIC}/all")
        mqtt_client.subscribe(f"{MQTT_TOPIC}/{USER_NAME}")
        print("MQTT connected and subscribed")
        return True
    except Exception as e:
        print(f"MQTT failed: {str(e)}")
        return False

def mqtt_callback(topic, msg):
    """Handle incoming MQTT messages"""
    try:
        data = json.loads(msg.decode())
        print(data)
        if data.get("type") == "message":
            message_queue.append(data["message"])
            print(f"Received message: {data['message']}")
        elif data.get("type") == "celebration":
            celebration_queue.append(data["message"])
            print(f"Received celebration: {data['message']}")
    except Exception as e:
        print(f"MQTT callback error: {e}")

setup_ethernet()
setup_mqtt()
print("setup!")
while True:
    try:
        mqtt_client.check_msg()
    except Exception as e:
        print(f"MQTT error: {e}")
    print(f"messages: {message_queue}")
    if message_queue:
        print(message_queue.pop(0))
    if celebration_queue:
        print(celebration_queue.pop(0))
    time.sleep(1)