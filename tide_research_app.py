import requests
from datetime import datetime
from tkinter import *
from tkcalendar import *
from tkinter import messagebox
from geopy.geocoders import Nominatim

def lookup_state_station_ids(state_requested: str)-> list:
    state_requested = state_requested.upper()
    stations = stations_metadata_json()['stations']

    if len(state_requested) != 2 and len(state_requested) != 0:
        return []
    else:
        list_of_stations = []
        k = 0

        for i in range(len(stations)):
            if stations[i]['state'] == state_requested:
                k += 1
                list_of_stations.append(str(k) + ". " + stations[i]['id'] + " - " + state_requested + " - " + stations[i]['name'])

        # print(*list_of_stations, sep = "\n")

        return list_of_stations

def stations_metadata_json():
    return requests.get(url='https://api.tidesandcurrents.noaa.gov/mdapi/prod/webapi/stations.json?type=tidepredictions').json()

def lookup_single_station_coordinates(station_id: str)->tuple:
    stations = stations_metadata_json()['stations']

    for i in range(len(stations)):
        if stations[i]['id'] == station_id:
            return (stations[i]['lat'],stations[i]['lng'])

def convert_coordinates_to_address(lat: str, lng: str) -> str:
    geolocator = Nominatim(user_agent="test")
    return geolocator.reverse(str(lat) + "," + str(lng))

def min_max(time_tide_height: list, start_time: datetime, range_hrs: int)-> list:

    time_list = []
    height_list = []
    rising_list = []

    states = []

    j = 0
    for i in range(len(time_tide_height)):
        temp_date_time = datetime.strptime(time_tide_height[i]['t'], '%Y-%m-%d %H:%M')   # turn string to datetime datatype
        time_tide_height[i]['t'] = temp_date_time                                        # replace string with datetime datatype

        # create lists for time, height, rising/receding
        # current_time plus range_hrs period
        if start_time <= temp_date_time and j < (range_hrs * 10):
            j += 1
            time_list.append(time_tide_height[i]['t'])
            height_list.append(float(time_tide_height[i]['v']))

            if i == 0:
                before_height = 0
            else:
                before_height = float(time_tide_height[i - 1]['v'])
            cur_height = float(time_tide_height[i]['v'])
            after_height = float(time_tide_height[i + 1]['v'])

            if before_height == 0 and cur_height < after_height:
                rising_list.append('rising')
            elif before_height == 0 and cur_height > after_height:
                rising_list.append("receding")
            elif before_height < cur_height and after_height > cur_height:
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

    last_element = len(height_list)-1

    states.append(('lowest_tide', time_list[min_height_index], height_list[min_height_index], rising_list[min_height_index]))
    states.append(('highest_tide', time_list[max_height_index], height_list[max_height_index], rising_list[max_height_index]))
    states.append(('last_tide', time_list[last_element], height_list[last_element], rising_list[last_element]))

    return states

def lookup_state_station_ids(state_requested: str)-> list:
    state_requested = state_requested.upper()
    r = requests.get(url='https://api.tidesandcurrents.noaa.gov/mdapi/prod/webapi/stations.json?type=tidepredictions').json()
    stations = r['stations']

    if len(state_requested) != 2 and len(state_requested) != 0:
        return []

    list_of_stations = []
    k = 0

    for i in range(len(stations)):
        if stations[i]['state'] == state_requested:
            k += 1
            list_of_stations.append(str(k) + ". " + stations[i]['id'] + " - " + stations[i]['name'])

    # print(*list_of_stations, sep = "\n")

    return list_of_stations

def start_time(cal, hour_sb, min_sb):
    date = cal.get_date()
    h = hour_sb.get()
    m = min_sb.get()
    full_str = str(date + " " + h + ":" + m)
    start_time_var = datetime.strptime(full_str, '%m/%d/%y %H:%M')
    return start_time_var

def get_single_station_tide_predictions_json(start_time_var, station_id):

    start_date_formatted = start_time_var.strftime("%Y%m%d")
    r = requests.get(
        url='https://api.tidesandcurrents.noaa.gov/api/prod/datagetter?begin_date=' + start_date_formatted + \
            '&range=48&station=' + station_id + '&product=predictions&datum=MLLW&time_zone=lst_ldt&units=english&format=json')
    return r.json()

def display_msg(cal, hour_sb, min_sb, station, root):

    station_id = station.get()
    start_time_var = start_time(cal, hour_sb, min_sb)
    tide_info = get_single_station_tide_predictions_json(start_time_var, station_id)
    range_hrs = 8  # this variable should come from the form in the future

    coordinates = lookup_single_station_coordinates(station_id)
    print(coordinates)
    print(convert_coordinates_to_address(coordinates[0],coordinates[1]))

    try:
        four_points = min_max(tide_info['predictions'], start_time_var, range_hrs)
    except:
        msg = "No data available for your station. Please check the Station ID and try again."
    else:
        msg = "The following is the tide information for station ID " + station.get() \
            + " for the period between " + four_points[0][1].strftime("%m/%d/%Y %H:%M") + " and " \
            + four_points[3][1].strftime("%m/%d/%Y %H:%M") + ": \n\n" \
            + "1. at " + four_points[0][1].strftime("%H:%M") + " the tide is " + str(four_points[0][2]) + "ft high, and it is " \
            + four_points[0][3] + "\n\n" \
            + "2. at " + four_points[3][1].strftime("%H:%M") + " the tide is " + str(four_points[3][2]) + "ft high, and it is " \
            + four_points[3][3] + "\n\n" \
            + "3. the lowest tide during this period is at " + four_points[1][1].strftime("%H:%M") + "; it is " + str(four_points[1][2]) + "ft high \n\n" \
            + "4. the highest tide during this period is at " + four_points[2][1].strftime("%H:%M") + "; it is " + str(four_points[2][2]) + "ft high\n"


    messagebox.showinfo("Tide Research - Output", msg)
    root.grab_set()

def close_window(window):
    window.destroy()

def write_station(input, station_id_input_field, station_menu_window, station_search_window, root):

    if input =="Choose a station from the list":
        input = "Please enter a valid Station ID"
    elif input == "No Station Available. Try again":
        input = "Please enter a valid Station ID"
    else:
        start = input.find(".") + 2
        input = input[start:start + 7]

    station_id_input_field.delete(0, len(station_id_input_field.get()))
    station_id_input_field.insert(0, input)
    close_window(station_menu_window)
    close_window(station_search_window)

    root.grab_set()

def open_station_menu_window(state_input: str, station_id_input_field, station_search_window, root):
    # Toplevel object which will
    # be treated as a new window

    state_input_list = lookup_state_station_ids(state_input)
    if len(state_input_list) == 0:
        state_input_list.append("No Station Available. Try again")

    station_menu_window = Toplevel(root)
    station_info_string = StringVar()
    f = ('Times', 16)

    station_info_string.set("Choose a station from the list")
    fone = Frame(station_menu_window)
    stationlbl = Label(fone, text="Choose a Station from the list", padx=10)
    station = OptionMenu(fone, station_info_string, *state_input_list)
    instrlbl_1 = Label(fone, text="Click Confirm to choose the selected station", padx=10)

    actionBtn_1 = Button(fone, text="CONFIRM", padx=10, pady=10,
                         command=lambda: write_station(station_info_string.get(), station_id_input_field,
                                                       station_menu_window, station_search_window, root))

    instrlbl_2 = Label(fone, text="Go back", padx=10)
    actionBtn_2 = Button(fone, text="Go Back", padx=10, pady=10, command=lambda: close_window(station_menu_window))

    fone.grid(column=0, row=0, columnspan=2, rowspan=3, padx=10, pady=10, sticky=W)
    stationlbl.grid(column=0,row=0, sticky=W)
    station.grid(column=1, row=0, sticky=W)
    instrlbl_1.grid(column=0, row=1, sticky=W)
    actionBtn_1.grid(column=1, row=1, columnspan=2, pady=30, sticky=W)
    instrlbl_2.grid(column=0, row=2, sticky=W)
    actionBtn_2.grid(column=1, row=2, columnspan=2, pady=30, sticky=W)

    station_menu_window.grab_set()

def open_station_search_window(station_id_input_field, root):
    # Toplevel object which will
    # be treated as a new window

    station_search_window = Toplevel(root)
    state_string = StringVar()
    f = ('Times', 16)

    fone = Frame(station_search_window)
    statelbl = Label(fone, text="Enter State in a two-character format (i.e. CA for California) to find a list of stations in the State:", padx=10)
    state = Entry(fone, textvariable=state_string, bd=5)
    instrlbl_1 = Label(fone, text="Click Find Stations to see a list of stations", padx=10)
    actionBtn_1 = Button(fone, text="Find Stations", padx=10, pady=10,
                         command=lambda: open_station_menu_window(state_string.get(), station_id_input_field,
                                                                  station_search_window, root))

    instrlbl_2 = Label(fone, text="Go back", padx=10)
    actionBtn_2 = Button(fone, text="Go Back", padx=10, pady=10, command=lambda: close_window(station_search_window))


    fone.grid(column=0, row=0, columnspan=2, rowspan=3, padx=10, pady=10, sticky=W)
    statelbl.grid(column=0, row=0, sticky=W)
    state.grid(column=1, row=0, columnspan=2, sticky=EW)
    instrlbl_1.grid(column=0, row=1, sticky=W)
    actionBtn_1.grid(column=1, row=1, columnspan=2, pady=30)
    instrlbl_2.grid(column=0, row=2, sticky=W)
    actionBtn_2.grid(column=1, row=2, columnspan=2, pady=30)

    station_search_window.grab_set()


def open_input_window(root):
    # Toplevel object which will
    # be treated as a new window

    input_window = Toplevel(root)

    hour_string = StringVar()
    min_string = StringVar()
    station_id = StringVar()
    f = ('Times', 16)

    button_size = 20

    fone = Frame(input_window)
    station = Entry(fone, textvariable=station_id, bd=5, width=button_size*2)
    station.insert(0,'9414290')

    stationIDlbl = Label(fone, text="If you know your Station ID, please input it here", padx=10)
    datelbl = Label(fone, text="Pick the start date", padx=10)
    cal = Calendar(fone, selectmode="day")
    timelbl = Label(fone, text="Pick the start time", padx=10)
    hour_sb = Spinbox(fone, from_=0, to=23, wrap=True, textvariable=hour_string, width=2, state="readonly", font=f,
                      justify=CENTER)
    min_sb = Spinbox(fone, from_=0, to=59, wrap=True, textvariable=min_string, font=f, width=2, state="readonly",
                     justify=CENTER)
    hrlbl = Label(fone, text="Hour")
    minlbl = Label(fone, text="Minute")
    instrlbl = Label(fone, text="Press RUN to get the data", padx=10)
    actionBtn = Button(fone, text="RUN", width=button_size, padx=1, pady=10, command=lambda: display_msg(cal, hour_sb, min_sb, station, input_window))
    instrlbl_2 = Label(fone, text="Click My Station button to locate your Station", padx=10)
    actionBtn_2 = Button(fone, text="Find My Station", width=button_size, padx=1, pady=10, command=lambda: open_station_search_window(station, input_window))
    instrlbl_3 = Label(fone, text="Go back", padx=10)
    actionBtn_3 = Button(fone, text="Go Back", width=button_size, padx=1, pady=10,
                         command=lambda: close_window(input_window))

    fone.grid(column=0, row=0, columnspan=3, rowspan=7, padx=10, pady=10, sticky=W)
    stationIDlbl.grid(column=0, row=0, sticky=W)
    station.grid(column=1, row=0, columnspan=2, sticky=W)
    instrlbl_2.grid(column=0, row=1, sticky=W)
    actionBtn_2.grid(column=1, row=1, columnspan=2, pady=30, sticky=EW)
    datelbl.grid(column=0, row=2, sticky=W)
    cal.grid(column=1, row=2, columnspan=2, pady=20, sticky=W)
    timelbl.grid(column=0, row=3, rowspan=2, sticky=W)
    hour_sb.grid(column=1, row=4, sticky=E)
    min_sb.grid(column=2, row=4, sticky=W)
    hrlbl.grid(column=1, row=3, sticky=E)
    minlbl.grid(column=2, row=3, sticky=W)
    instrlbl.grid(column=0, row=5, sticky=W)
    actionBtn.grid(column=1,row=5,columnspan=2, pady=30, sticky=EW)
    instrlbl_3.grid(column=0, row=6, sticky=W)
    actionBtn_3.grid(column=1, row=6, columnspan=2, pady=30, sticky=EW)

    #input_window.mainloop()
    input_window.grab_set()

def open_welcome_window():

    # welcome screen
    root = Tk()
    root.title("Tide Research - Welcome")

    f1 = Frame(root, highlightthickness=0, highlightbackground="red")

    f1.grid(column=0, row=0, columnspan=2, rowspan=7, padx=10, pady=10, sticky=W)


    tx1 = "Welcome to Tide Research App. This App provides tide predictions generated by U.S. NOAA stations."
    tx2 = "While there are many uses for the App, our original client uses it to plan his walks along the shore in \
    and around San Francisco, CA."
    tx3 = "We hope you will find the App useful for planning your walks or any other purposes!"
    tx4 = "The App provides tide predictions for all NOAA stations. If you are near a NOAA station, we got you covered!"
    tx5 = "To launch the App please click START or click END to exit."

    lbl1 = Label(f1, text=tx1, font="Times, 11", highlightbackground="blue", highlightthickness=0)
    lbl2 = Label(f1, text=tx2, font="Times, 11", highlightbackground="blue", highlightthickness=0)
    lbl3 = Label(f1, text=tx3, font="Times, 11", highlightbackground="blue", highlightthickness=0)
    lbl4 = Label(f1, text=tx4, font="Times, 11", highlightbackground="blue", highlightthickness=0)
    lbl5 = Label(f1, text=tx5, font="Times, 11", highlightbackground="blue", highlightthickness=0)

    lbl1.grid(row=0, column=0, columnspan=2, sticky=W, padx=5, pady=5)
    lbl2.grid(row=1, column=0, columnspan=2, sticky=W, padx=5, pady=5)
    lbl3.grid(row=2, column=0, columnspan=2, sticky=W, padx=5, pady=5)
    lbl4.grid(row=3, column=0, columnspan=2, sticky=W, padx=5, pady=5)
    lbl5.grid(row=4, column=0, columnspan=2, padx=5, pady=15)

    start_button = Button(f1, text="START", command=lambda: open_input_window(root))
    exit_button = Button(f1, text="END", command=lambda: close_window(root))
    start_button.grid(row=5, column=0, sticky=E, padx=20, pady=20)
    exit_button.grid(row=5, column=1, sticky=W, padx=20)

    root.mainloop()

if __name__ == '__main__':
    open_welcome_window()