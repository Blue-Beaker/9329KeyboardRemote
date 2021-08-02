# 9329KeyboardRemote
A tool that uses CH9329 to control another device.  
Currently work in progress but usable.  

Can be used to control a device from remote through some remote desktop tools. 


TCP Support added, Connect the ch9329 chip with an ESP8266 module and Use this: https://github.com/jeelabs/esp-link  
Then select "Serial over TCP", input Host IP, and connect.

For remote control, run this tool on a linux device is suggested as you can use ssh X11 port forwarding for the GUI.
