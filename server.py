# CS 361
# Date: 7/24/2022
# Student: Vadim Krifuks
# Microservice Implementation - Server Side

import zmq
import requests
from datetime import datetime

def min_max(time_tide_height: list, start_time: datetime, range_hrs: int) -> list:

    time_list = []
    height_list = []
    rising_list = []

    states = []

    j = 0
    for i in range(len(time_tide_height)):
        temp_date_time = datetime.strptime(time_tide_height[i]['t'],
                                           '%Y-%m-%d %H:%M')  # turn string to datetime datatype
        time_tide_height[i]['t'] = temp_date_time  # replace string with datetime datatype

        # create lists for time, height, rising/receding
        # current_time plus range_hrs period
        if start_time < temp_date_time and j < ((range_hrs * 10) + 1):
            j += 1
            time_list.append(time_tide_height[i]['t'])
            height_list.append(float(time_tide_height[i]['v']))

            before_height = float(time_tide_height[i - 1]['v'])
            cur_height = float(time_tide_height[i]['v'])
            after_height = float(time_tide_height[i + 1]['v'])

            if before_height < cur_height and after_height > cur_height:
                rising_list.append('rising')
            elif before_height < cur_height and after_height < cur_height:
                rising_list.append('high tide')
            elif before_height > cur_height and after_height < cur_height:
                rising_list.append('receding')
            else:
                rising_list.append('low tide')

    states.append(('start_time_tide', time_list[0], height_list[0], rising_list[0]))

    min_height = height_list[0]
    max_height = height_list[0]

    for i in range(j):
        if height_list[i] > max_height:
            max_height = height_list[i]
        elif height_list[i] < min_height:
            min_height = height_list[i]

    min_height_index = height_list.index(min_height)

    max_height_index = height_list.index(max_height)

    last_element = len(height_list) - 1

    states.append(
        ('lowest_tide', time_list[min_height_index], height_list[min_height_index], rising_list[min_height_index]))
    states.append(
        ('highest_tide', time_list[max_height_index], height_list[max_height_index], rising_list[max_height_index]))
    states.append(('last_tide', time_list[last_element], height_list[last_element], rising_list[last_element]))

    return states

def provide_cur_time() -> list:
    x = datetime.now()

    year = int(str(x.year)[2:])
    month = x.month
    day = x.day
    hour = x.hour
    minute = x.minute

    return [month,day,year,hour,minute]

def tide_info(station_id: int, month: int, day: int, year: int, h: int, m: int) -> list:

    full_str = str(str(month) + "/" + str(day) + "/" + str(year) + " " + str(h) + ":" + str(m))

    start_time = datetime.strptime(full_str, '%m/%d/%y %H:%M')

    range_hrs = 5  # this variable should come from the form

    start_date_formatted = start_time.strftime("%Y%m%d")

    r = requests.get(
        url='https://api.tidesandcurrents.noaa.gov/api/prod/datagetter?begin_date=' + start_date_formatted + '&range=48&station=' + str(station_id) + '&product=predictions&datum=MLLW&time_zone=lst&units=english&format=json')
    temp = r.json()

    four_points = min_max(temp['predictions'], start_time, range_hrs)
    return four_points

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")

print(f"The microservice server is online and waiting for requests. \n")

while True:
    #  Wait for next request from client
    message = socket.recv().decode()

    print(f"A. The server received the following request from a client: {message}")

    #  Do some 'work'
    message_list = message.split(",")

    message_list = [int(i) for i in message_list]

    try:
        if (message_list[1] == -1 or message_list[2] == -1 or message_list[3] == -1 or message_list[4] == -1 or message_list[5] == -1):
            cur_time_list = provide_cur_time()
            four_points = tide_info(message_list[0], cur_time_list[0], cur_time_list[1], cur_time_list[2], cur_time_list[3], cur_time_list[4])
        else:
            four_points = tide_info(message_list[0], message_list[1], message_list[2], message_list[3], message_list[4], message_list[5])
    except:
        microservice_output = "Bad request. Please check the Station ID, date, and time (month 1-12, day 1-31, year - two digits, \n" \
        + "   hour 0-23, min 0-59, and send another request.\n" \
        + "   If you'd like to receive the tide information for the current time (specific to the microservice server's clock), set month, day, year, hour or min to -1."
        print(f"B. The server is sending back the following reply: {microservice_output} \n")
        socket.send(microservice_output.encode())
        continue

    one_point = four_points[0]
    one_point = [str(i) for i in one_point]

    microservice_output = ",".join(one_point)

    #  Send reply back to client
    print(f"B. The server is sending back the following reply: {microservice_output} \n")
    socket.send(microservice_output.encode())