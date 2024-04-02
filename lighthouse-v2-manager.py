import asyncio
import sys
import re
import os
from bleak import BleakScanner, BleakClient

__PWR_SERVICE = "00001523-1212-efde-1523-785feabcd124"
__PWR_CHARACTERISTIC = "00001525-1212-efde-1523-785feabcd124"
__PWR_ON = bytearray([0x01])
__PWR_STANDBY = bytearray([0x00])

timeout = 4
lh_macs = []

async def discover_devices():
    lh_macs = []
    create_shortcuts = "-cs" in sys.argv or "--create-shortcuts" in sys.argv
    print(">> MODE: discover suitable LightHouse V2")
    if create_shortcuts:
        print("         and create desktop shortcuts")
    print(" ")
    print(">> Discovering BLE devices...")
    devices = await BleakScanner.discover()
    for d in devices:
        if isinstance(d.name, str) and d.name.startswith("LHB-"):
            print(f">> Found potential Valve LightHouse at '{d.address}' with name '{d.name}'...")
            try:
                async with BleakClient(d.address, timeout=timeout) as client:
                    services = await client.get_services()
                    for s in services:
                        if s.uuid == __PWR_SERVICE:
                            print(f"   OK: Service {__PWR_SERVICE} found.")
                            for c in s.characteristics:
                                if c.uuid == __PWR_CHARACTERISTIC:
                                    print(f"   OK: Characteristic {__PWR_CHARACTERISTIC} found.")
                                    print(">> This seems to be a valid LightHouse V2.")
                                    power_state = await client.read_gatt_char(__PWR_CHARACTERISTIC)
                                    print("   Device power state: ", "ON" if power_state == __PWR_ON else "OFF")
                                    lh_macs.append(d.address)
                                    break
                            else:
                                print("   ERROR: Characteristic not found.")
                    else:
                        print("   ERROR: Service not found.")
            except Exception as e:
                print(f">> ERROR: {e}")
            print(" ")
    return lh_macs

async def toggle_mac(mac):
    try:
        async with BleakClient(mac, timeout=timeout) as client:
            power_state = await client.read_gatt_char(__PWR_CHARACTERISTIC)
            print(f"   Getting LightHouse power state...")
            target_state = __PWR_STANDBY if power_state == __PWR_ON else __PWR_ON
            print(f"   Turning LightHouse {'ON' if target_state == __PWR_ON else 'OFF'}...")
            await client.write_gatt_char(__PWR_CHARACTERISTIC, target_state)
            print("   LightHouse toggled.")
    except Exception as e:
        print(f">> ERROR: {e}")

async def process_macs(command, lh_macs):
    tasks = []
    for mac in lh_macs:
        if command.upper() == "TOGGLE":
            tasks.append(toggle_mac(mac))
        elif command.upper() == "ON":
            tasks.append(turn_on_mac(mac))
        else:
            tasks.append(turn_off_mac(mac))
    await asyncio.gather(*tasks)

async def turn_on_mac(mac):
    try:
        async with BleakClient(mac, timeout=timeout) as client:
            print(f"   Powering LightHouse ON...")
            await client.write_gatt_char(__PWR_CHARACTERISTIC, __PWR_ON)
            print("   LightHouse has been turned ON.")
    except Exception as e:
        print(f">> ERROR: {e}")

async def turn_off_mac(mac):
    try:
        async with BleakClient(mac, timeout=timeout) as client:
            print(f"   Putting LightHouse in STANDBY...")
            await client.write_gatt_char(__PWR_CHARACTERISTIC, __PWR_STANDBY)
            print("   LightHouse has been put in STANDBY.")
    except Exception as e:
        print(f">> ERROR: {e}")

async def create_shortcuts(lh_macs):
    if sys.platform == "win32":
        import winshell
        from win32com.client import Dispatch

        desktop = winshell.desktop()

        for state in ["ON", "OFF"]:
            shortcut_name = f"LHv2-{state}.lnk"
            path = os.path.join(desktop, shortcut_name)
            shell = Dispatch("WScript.Shell")
            shortcut = shell.CreateShortcut(path)

            if ".py" in sys.argv[0]:
                target_path = sys.executable
                arguments = f'"{sys.argv[0]}" {state.lower()} ' + " ".join(lh_macs)
            else:
                target_path = '"' + sys.argv[0] + '"'
                arguments = f"{state.lower()} " + " ".join(lh_macs)

            shortcut.TargetPath = target_path
            shortcut.Arguments = arguments
            shortcut.WorkingDirectory = os.path.dirname(os.path.abspath(sys.argv[0]))
            shortcut.IconLocation = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), f"lhv2_{state.lower()}.ico")
            shortcut.Save()

            print(f"   * OK: {shortcut_name} was created successfully.")
    else:
        print(">> WARNING: Creating desktop shortcuts is not supported on this platform.")

async def main():
    global lh_macs
    if len(sys.argv) < 2 or sys.argv[1] not in ["on", "off", "discover", "toggle"]:
        print(" Invalid or no command given. Usage...")
        sys.exit()

    command = sys.argv[1]

    if command == "discover":
        lh_macs = await discover_devices()
        if len(lh_macs) > 0:
            print(">> OK: At least one compatible LightHouse V2 was found.")
            for mac in lh_macs:
                print("   * " + mac)
            print(" ")
            if "-cs" in sys.argv or "--create-shortcuts" in sys.argv:
                await create_shortcuts(lh_macs)
        else:
            print(">> Sorry, no suitable LightHouse V2 found.")
        print(" ")

    elif command in ["on", "off", "toggle"]:
        lh_macs.extend(sys.argv[2:])
        invalid_macs = [mac for mac in lh_macs if not re.match("[0-9a-fA-F]{2}(:[0-9a-fA-F]{2}){5}", mac)]
        if invalid_macs:
            print("   * Invalid MAC address format: ", ", ".join(invalid_macs))
            lh_macs = [mac for mac in lh_macs if mac not in invalid_macs]
        if len(lh_macs) == 0:
            print(" ")
            print(">> ERROR: no (valid) LightHouse MAC addresses given.")
            print(" ")
            sys.exit()

        print(">> MODE: switch LightHouse", command.upper())
        for mac in lh_macs:
            print("   * " + mac)
        print(" ")

        await process_macs(command, lh_macs)

asyncio.run(main())
