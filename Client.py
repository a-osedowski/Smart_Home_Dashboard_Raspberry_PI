import asyncio
from bleak import BleakClient
import pyrebase
import binascii
from datetime import datetime

address = ""
MODEL_NBR_UUID = "46749D0D-28DA-B4BA-E9EE-60C2456EB34D"


temp_uuid = f"0000{0x2A6E:x}-0000-1000-8000-00805f9b34fb"
humid_uuid = f"0000{0x2A6F:x}-0000-1000-8000-00805f9b34fb"
light_uuid = f"0000{0x2a6d:x}-0000-1000-8000-00805f9b34fb"


firebaseConfig = {
    "apiKey": "",
    "authDomain": "project-dashboarding.firebaseapp.com",
    "projectId": "project-dashboarding",
    "storageBucket": "project-dashboarding.appspot.com",
    "messagingSenderId": "714624220340",
    "appId": "1:714624220340:web:190f09043509f098572be1",
    "measurementId": "G-RF95WJ0G6W",
    "databaseURL": "https://project-dashboarding-default-rtdb.europe-west1.firebasedatabase.app"
};


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


if __name__ == '__main__':
    asyncio.run(main(address))