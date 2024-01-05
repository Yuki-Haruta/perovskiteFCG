import sys
import cv2
import serial.tools.list_ports
import numpy as np

'''
System Information
'''

def get_pump_port(serial_number):
    '''
    Use a serial number of the usb cable
    '''
    port_number = None
    ports = serial.tools.list_ports.comports()
    for p in ports:
        Number = p.serial_number
        if Number == serial_number:
            port_number = p.device
    if port_number == None:
        print("Port was not detected. Check connection.")
    return port_number

def get_system_info(SYSTEM_ID):
    if SYSTEM_ID == 'A':
        # Scale factor
        camera_scale = 69.62
        # Crop radius
        radius = 430
        # Pump type
        pumpName = "PHD"
        # Pump Port (depends on the USB cable)
        pump_port = get_pump_port(port_number) # use a port number
        # RGB threshold to detect MAPbBr3
        lower = np.array([0, 0, 50])  # B,G,R threshold to find orange regions
        upper = np.array([255, 60, 255])
        RGB_threshold = [lower,upper]

    elif SYSTEM_ID == 'AY1':
        # Scale factor
        camera_scale = 87.65
        # Crop radius
        radius = 450
        # Pump type
        pumpName = "NE"
        # Pump Port (depends on the USB cable)
        pump_port = get_pump_port(port_number) # use a port number
        # RGB threshold to detect MAPbBr3
        lower = np.array([0, 0, 100])  # B,G,R threshold to find orange regions
        upper = np.array([50, 50, 255])
        RGB_threshold = [lower,upper]

    else:
        print('SYSTEM_ID is wrong. It should be A, AY1.')
        sys.exit(0)
    
    # Camera settings
    camera_settings = {
        cv2.CAP_PROP_FRAME_WIDTH: 1920.0,
        cv2.CAP_PROP_FRAME_HEIGHT: 1080.0,
        cv2.CAP_PROP_MODE: -1.0,
        cv2.CAP_PROP_BRIGHTNESS: 0.0,
        cv2.CAP_PROP_CONTRAST: 0.0,
        cv2.CAP_PROP_SATURATION: 64.0,
        cv2.CAP_PROP_HUE: 0.0,
        cv2.CAP_PROP_GAIN: -1.0,
        cv2.CAP_PROP_EXPOSURE: -6.0,
        cv2.CAP_PROP_WB_TEMPERATURE: -1.0,
        cv2.CAP_PROP_GAMMA: 100.0,
        cv2.CAP_PROP_FOCUS: 5.0,
        cv2.CAP_PROP_TEMPERATURE: -1.0,
        cv2.CAP_PROP_AUTO_EXPOSURE: -1.0,
        cv2.CAP_PROP_AUTOFOCUS: 1.0,
        cv2.CAP_PROP_AUTO_WB: -1.0
    }
    
    systeminfo = [camera_scale, radius, camera_settings, RGB_threshold, pumpName, pump_port]
    
    print(f"Grabbed system information for SYSTEM {SYSTEM_ID}")
    return systeminfo