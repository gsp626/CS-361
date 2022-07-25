# CS 361
# Date: 7/24/2022
# Student: Vadim Krifuks
# Microservice Implementation - Client Side

import zmq
import time

context = zmq.Context()

#  Socket to talk to server
print("1. The client is connecting to a microservice server")
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5555")
time.sleep(1)
print("2. The client established a connection with the server")
time.sleep(1)

# INPUT VALUES
# https://tidesandcurrents.noaa.gov/stations.html?type=Harmonic+Constituents - URL to find Station IDs
station_id_var = 8537121
month = 50                       # from 1 to 12
day = 1                        # from 1 to 31
year = 22                       # 2 digit format
hour = -1                       # from 0 to 23
minute = 30                     # from 0 to 59

request = str(str(station_id_var) + "," + str(month) + "," + str(day) + "," + str(year) + "," + str(hour) + "," + str(minute))


print(f"3. The client is sending a request: {request}")
socket.send(request.encode())
#  Get the reply.
message = socket.recv().decode()
time.sleep(1)
print(f"4. The client received a reply: {message}")
time.sleep(1)