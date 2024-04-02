# Manager for V2 Lighthouses by Valve/HTC

This python script helps you switch your Valve Lighthouses V2 on and into stand-by.

## Installation & Prerequisites

Make sure that you have the following:
* BLE / Bluetooth 4.0 dongle installed and connected (*not* a BGAPI one!)
* Python 3
* Run `pip3 install -r requirements.txt`

## Usage with Command Line Arguments

The script provides three usage options: discovery, turning on, and switching to standby of a lighthouse V2.

**Note:** If you installed the binary version, simply call the program by executing it. Instead of `python3 .\lighthouse-v2-manager.py`, type `lighthouse-v2-manager.exe` in the command prompt window for the commands below.

### Display Instructions

If you call the executable/script with no command line arguments or with an invalid command, the usage instructions are returned. Choose one of the commands `discover`, `on`, `off`, or `toggle` to interact with your Lighthouses V2.

**Usage:** `python3 .\lighthouse-v2-manager.py`

### Discovery

If you call the program with the `discover` command, it tries to open your BLE device and scans for BLE servers in range. Once found, it looks for the service and characteristic which allow for the power-up and power-down of a lighthouse V2. Look for the MAC addresses and the results on the console output.

Optionally, since version 1.1, you can specify the command line option `-cs` or `--create-shortcuts` with the discovery command. The program then tries to create suitable shortcuts for your installation and your Lighthouses' MAC addresses. This works with both the script version and the binary stand-alone version.

**Usage:** `python3 .\lighthouse-v2-manager.py discover [-cs,--create-shortcuts]`

### Switch Lighthouses into Standby

If you want to switch a lighthouse off ("stand-by"), specify either "off" as the first argument and then each MAC address consecutively as further arguments like so:

**Usage:** `python3 .\lighthouse-v2-manager.py off aa:aa:aa:aa:aa:aa bb:bb:bb:bb:bb:bb ...`

The lighthouses LED will now start a blue breathing animation, that is, it will fade-in and fade-out to indicate its standby operation state.

### Turning Lighthouses Back On

If you want to switch a lighthouse back on, specify either "on" as the first argument and then each MAC address consecutively as further arguments like so:

**Usage:** `python3 .\lighthouse-v2-manager.py on aa:aa:aa:aa:aa:aa bb:bb:bb:bb:bb:bb ...`

The lighthouses LED will power up. As soon as it's stabilized, the LED turns solid green.

### Toggle Lighthouse States

If you want to toggle the state of the basestation(s), specify "toggle" as the first argument then each MAC address consecutively as further arguments like so:

**Usage:** `python3 .\lighthouse-v2-manager.py toggle aa:aa:aa:aa:aa:aa bb:bb:bb:bb:bb:bb ...`

The script connects to each basestation specified, then gets if they are active or in standby mode. Then based on the state it will send a command to swap it to the opposite state. So if it is on, it will be toggled to standby, and vice versa. The point of this argument is to reduce the amount of scripts you would need to just one to turn the basestations on or off.

### Hard-Coding Your Lighthouses' MAC Addresses

Inside the script, you can edit the list `lh_macs` to contain the MAC addresses of your lighthouses as strings. Doing so allows a shorter command-line interaction:
* `python3 .\lighthouse-v2-manager.py on`
* `python3 .\lighthouse-v2-manager.py off`

Still, you can add other MAC addresses dynamically even after you put some in the file itself:
* `python3 .\lighthouse-v2-manager.py off cc:cc:cc:cc:cc:cc`

## Credits

* [Enzo Geant](https://github.com/egeant94) for the new on/off icons. Thanks for your contribution.
