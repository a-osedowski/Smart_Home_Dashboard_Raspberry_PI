import asyncio
from bleak import BleakClient

address = "e5:06:27:d7:a6:a9"
MODEL_NBR_UUID = "46749D0D-28DA-B4BA-E9EE-60C2456EB34D"

temp_uuid = f"0000{0x2A6E:x}-0000-1000-8000-00805f9b34fb"
press_uuid = f"0000{0x2A6D:x}-0000-1000-8000-00805f9b34fb"

async def main(address):
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
        int_data_temp = int.from_bytes(data_temp, "little")
        print("Temperature:")
        print(int_data_temp/100)

        data_press = await client.read_gatt_char(press_uuid)
        int_data_press = int.from_bytes(data_press, "little")
        print("Pressure:")
        print(int_data_press/10)

    except Exception as e:
        print(e)
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
    client = BleakClient(address)
    asyncio.run(main(address))
    # loop = asyncio.new_event_loop()
    # asyncio.set_event_loop(loop)
    # loop.run_until_complete(connection(client))
    # loop.run(client.start_notify(temp_uuid, callback))
    # loop.run_forever(notify(client))
    # asyncio.create_task(notify(client))