import asyncio
from bleak import BleakClient
import pyrebase
import binascii
import logging
import sys
import time
# import platformcd
from bluepy import btle
import gatt
from datetime import datetime

address = "e5:06:27:d7:a6:a9"
MODEL_NBR_UUID = "46749D0D-28DA-B4BA-E9EE-60C2456EB34D"

# logger = logging.getLogger(__name__)

temp_uuid = f"0000{0x2A6E:x}-0000-1000-8000-00805f9b34fb"
humid_uuid = f"0000{0x2A6F:x}-0000-1000-8000-00805f9b34fb"
light_uuid = f"0000{0x2a6d:x}-0000-1000-8000-00805f9b34fb"


firebaseConfig = {
    "apiKey": "AIzaSyCakKQr-Z1J3oRJG76UK3l8RAQTCKz4Kxc",
    "authDomain": "project-dashboarding.firebaseapp.com",
    "projectId": "project-dashboarding",
    "storageBucket": "project-dashboarding.appspot.com",
    "messagingSenderId": "714624220340",
    "appId": "1:714624220340:web:190f09043509f098572be1",
    "measurementId": "G-RF95WJ0G6W",
    "databaseURL": "https://project-dashboarding-default-rtdb.europe-west1.firebasedatabase.app"
};

manager = gatt.DeviceManager(adapter_name='hci0')


# class AnyDevice(gatt.Device):
#     def connect_succeeded(self):
#         super().connect_succeeded()
#         print("[%s] Connected" % (self.mac_address))
#
#     def connect_failed(self, error):
#         super().connect_failed(error)
#         print("[%s] Connection failed: %s" % (self.mac_address, str(error)))
#
#     def disconnect_succeeded(self):
#         super().disconnect_succeeded()
#         print("[%s] Disconnected" % (self.mac_address))
#
#     def services_resolved(self):
#         super().services_resolved()
#
#         print("[%s] Resolved services" % (self.mac_address))
#         for service in self.services:
#             print("[%s]  Service [%s]" % (self.mac_address, service.uuid))
#             for characteristic in service.characteristics:
#                 print("[%s]    Characteristic [%s]" % (self.mac_address, characteristic.uuid))
#
#     def services_resolved(self):
#         super().services_resolved()
#
#         device_information_service = next(
#             s for s in self.services
#             if s.uuid == '0000181a-0000-1000-8000-00805f9b34fb')
#
#         temp_characteristic = next(
#             c for c in device_information_service.characteristics
#             if c.uuid == '00002a6e-0000-1000-8000-00805f9b34fb')
#
#         humid_characteristic = next(
#             c for c in device_information_service.characteristics
#             if c.uuid == '00002a6f-0000-1000-8000-00805f9b34fb')
#
#         light_characteristic = next(
#             c for c in device_information_service.characteristics
#             if c.uuid == '00002a6d-0000-1000-8000-00805f9b34fb')
#
#         temp_characteristic.read_value()
#         humid_characteristic.read_value()
#         light_characteristic.read_value()
#
#     def characteristic_value_updated(self, characteristic, value):
#         print("Characteristic", characteristic)
#         print("Value:", binascii.hexlify(value))



# def read_humidity(service):
#     humidity_char = service.getCharacteristics("2A6F")[0]
#     humidity = humidity_char.read()
#     # humidity = byte_array_to_int(humidity)
#     # humidity = decimal_exponent_two(humidity)
#     # print(f"Humidity: {round(humidity, 2)}%")
#
#
# async def read_temperature(service):
#     temperature_char = await service.getCharacteristics("2A6E")[0]
#     temperature = temperature_char.read()
#     temperature = int.from_bytes(temperature/100, "little")
#     print(f"Temperature: {temperature}°C")
#
# async def main():
#     print("Connecting…")
#     nano_sense = await btle.Peripheral(address)
#     print("Discovering Services…")
#     _ = await nano_sense.services
#     environmental_sensing_service = await nano_sense.getServiceByUUID("181A")
#     print("Discovering Characteristics…")
#     _ = environmental_sensing_service.getCharacteristics()
#     while True:
#         print("\n")
#     read_temperature(environmental_sensing_service)
#     # read_humidity(environmental_sensing_service)



async def main(address):
    firebase = pyrebase.initialize_app(firebaseConfig)
    database = firebase.database()

    now = datetime.now()
    current_time = now.strftime("%H:%M")
    print(current_time)
    # async with BleakClient(address) as client:
    client = BleakClient(address)
    try:
        await client.connect()

        if client.is_connected:
            print("Connected")
        else:
            print("Unable to connect")
        services = await client.get_services()
        print("Characteristics:")
        for s in services:
            print(s)

        data_temp = await client.read_gatt_char(temp_uuid)
        print(data_temp)
        print(binascii.hexlify(data_temp))
        int_data_temp = int.from_bytes(data_temp, "little")
        print("Temperature:")
        print(int_data_temp/10)
        upload_temp = database.child("temperature").push({"Temperature": int_data_temp/10, "Time": current_time})

        data_humid = await client.read_gatt_char(humid_uuid)
        int_data_humid = int.from_bytes(data_humid, "little")
        print("Humidity:")
        print(int_data_humid/100)
        upload_humidity = database.child("humidity").push({"Humidity": int_data_humid/100, "Time": current_time})


        data_light = await client.read_gatt_char(light_uuid)
        int_data_light = int.from_bytes(data_light, "little")
        print("Light:")
        print(int_data_light)
        upload_humidity = database.child("light").push({"Light": int_data_light, "Time": current_time})

    except Exception as e:
        print(e)
        await client.disconnect()
        asyncio.run(main(address))
    finally:
        await client.disconnect()

def callback(sender: int, data: bytearray):
    data_int = int.from_bytes(data, "little")
    print(f"{sender}: {data_int}")

async def connection(client):
    try:
        await client.connect()
        if client.is_connected:
            print("Connected")
        else:
            print("Unable to connect")
    except Exception as e:
        print(e)

async def notify(client):

    loop = asyncio.get_event_loop()
    await loop.run_forever(None, client.start_notify(temp_uuid, callback))


if __name__ == '__main__':
    # device = AnyDevice(mac_address='e5:06:27:d7:a6:a9', manager=manager)
    # device.connect()
    #
    # manager.run()
    # # main()

    # upload = database.child("measurements").push({"Humidity": 450})
    # client = BleakClient(address)
    # logging.basicConfig(level=logging.INFO)
    # asyncio.run(
    #     notifyClient(address, temp_uuid)
    # )
    asyncio.run(main(address))
    # loop = asyncio.new_event_loop()
    # asyncio.set_event_loop(loop)
    # loop.run_until_complete(connection(client))
    # loop.run(client.start_notify(temp_uuid, callback))
    # loop.run_forever(notify(client))
    # asyncio.create_task(notify(client))