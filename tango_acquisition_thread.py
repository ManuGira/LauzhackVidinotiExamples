import socket
from json import loads as json_loads
from threading import Thread
import os


# TODO: Hey fellow Lauzhacker, you already explored the scene with the TANGO using the app U-TANGO 2.1 right?
# Also, beware that the point where you start the exploration is the origin of the axis system.
# More information here: https://developers.google.com/tango/overview/coordinate-systems

class TangoAcquisition(Thread):
    def __init__(self, local_ip, datawriter=None):
        print("Tango Acquisition Thread init()")
        Thread.__init__(self)
        self.setDaemon(True)  # if the main thread finish, it will finish as well
        self.datawriter = datawriter

        # The mobile phone sends some TCP packet through a socket at on a certain port and IP address.
        self.LOCAL_IP = local_ip  # you can find your own IPv4 address using the command "ifconfig" in linux terminal
        self.SOCKET_PORT = 7585  #7585 for Tango device

    def run(self):
        print("Tango run()")
        toprint = set([])
        measure_list = []

        print("TANGO: Open socket on port ", self.SOCKET_PORT, " with IP ", self.LOCAL_IP)
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.bind((self.LOCAL_IP, self.SOCKET_PORT))
            while True:
                json_str, addr = sock.recvfrom(1024)  # buffer size is 1024 bytes
                # print(json_str.decode())

                json_obj = json_loads(json_str.decode())  # the json format
                timeStamps = json_obj['Time_Stamps']  # time stamp
                device_id = int(json_obj['Tag_ID'], 16)  # convert the id from hexadecimal string to int
                adf_uuid = json_obj['ADF_UUID']
                localPos_x = float(json_obj['POS_X'])
                localPos_y = float(json_obj['POS_Y'])
                localPos_z = float(json_obj['POS_Z'])
                localTheta_x = float(json_obj['THETA_X'])
                localTheta_y = float(json_obj['THETA_Y'])
                localTheta_z = float(json_obj['THETA_Z'])

                timeStamps = int(float(timeStamps))

                # As anchor_id, we use the id of the ADF file (hexadecimal string), translated to a decimal integer
                anchor_id = int(adf_uuid.replace('-', ''), 16)

                dico = {
                    "timestamp": timeStamps,
                    "device_id": device_id,
                    "system_id": self.SOCKET_PORT,  # we use the port as id
                    "anchor_id": anchor_id,
                    "px": localPos_x,
                    "py": localPos_y,
                    "pz": localPos_z,
                    "theta_x": localTheta_x,
                    "theta_y": localTheta_y,
                    "theta_z": localTheta_z
                }

                # Feed datawriter
                if self.datawriter is not None:
                    self.datawriter.writeline(dico)
