import pandas as pd

pd.set_option("display.max_rows", None, "display.max_columns", None)


# converts a value in military time to an equivalent integer/float
def mt_to_int(military_time):

    hours = military_time[0:2]
    minutes = military_time[2:]

    if hours[0] == 0:
        hours = hours[1]
    hours = int(hours)

    minutes = round(int(minutes)/60, 2)

    if minutes == 0:
        time = hours
    else:
        time = hours + minutes
    return time


# returns the previous day
def previous(day):
    if day == "SUN":
        return "SAT"
    elif day == "MON":
        return "SUN"
    elif day == "TUE":
        return "MON"
    elif day == "WED":
        return "TUE"
    elif day == "THU":
        return "WED"
    elif day == "FRI":
        return "THU"
    elif day == "SAT":
        return "FRI"
    else:
        return "invalid entry"


def time_during_shift(hours, minutes, shift, shift_length):

    time_window = float(hours) + float(minutes)/60

    start_time = shift
    end_time = (start_time + shift_length) % 24

    time_window_during_shift = False

    if start_time < end_time:
        if start_time <= time_window < end_time:
            time_window_during_shift = True
    else:
        if (23 - shift_length/2) < start_time < 24:
            if start_time <= time_window < 24:
                return "previous_day"
            elif 0 <= time_window < end_time:
                return True
        else:
            if start_time <= time_window < 24 or 0 <= time_window < end_time:
                time_window_during_shift = True

    return time_window_during_shift


def create_dataframe():
    # days for one week
    days = ['SUN', 'MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT']
    # # days for two weeks
    # days = ['SUN1', 'MON1', 'TUE1', 'WED1', 'THU1', 'FRI1', 'SAT1', 'SUN2', 'MON2', 'TUE2', 'WED2', 'THU2', 'FRI2', 'SAT2']
    time_window_length = 15
    shift_length = 8

    shifts_mt = ["2300", "0000", "0600", "0700", "0800", "1300", "1500", "1600"]
    columns = {'day': [], 'time': []}
    shifts = {}

    for day in days:
        hours = 0
        minutes = 0
        while hours < 24:
            if hours < 10:
                hour_string = "0" + str(hours)
            else:
                hour_string = hours
            if minutes < 10:
                minute_string = "0" + str(minutes)
            else:
                minute_string = minutes
            columns['time'].append('{}:{}'.format(hour_string, minute_string))
            columns['day'].append(day)

            minutes += time_window_length
            if minutes % 60 == 0:
                hours += 1
                minutes = 0

    for day in days:
        for shift_mt in shifts_mt:
            shifts[day + " " + shift_mt] = mt_to_int(shift_mt)
            columns[day + " " + shift_mt] = [None] * len(columns['day'])

    path_to_file = '/Users/davismercier/Desktop/Shift_Generate_Data.xlsx'
    sheet = 'Sheet1'
    required_df = pd.read_excel(path_to_file, sheet)
    required_list = required_df['Required'].to_list()

    columns['required'] = required_list

    df = pd.DataFrame(columns)

    for day_shift_mt, shift in shifts.items():
        for i in range(len(df)):
            shift_day, shift_mt = day_shift_mt.split(" ")
            tw_day = df.loc[i, 'day']
            time = df.loc[i, 'time']
            hours, minutes = time.split(":")

            if shift_day == tw_day:
                if time_during_shift(hours, minutes, shift, shift_length) == True:
                    df.loc[i, day_shift_mt] = 1
                elif time_during_shift(hours, minutes, shift, shift_length) == "previous_day":
                    df.loc[i, day_shift_mt] = 0
                    # find the row with the same time on the previous day
                    filt = (df['day'] == previous(shift_day)) & (df['time'] == time)
                    df.loc[filt, day_shift_mt] = 1
                else:
                    df.loc[i, day_shift_mt] = 0
            else:
                if df.loc[i, day_shift_mt] == None:
                    df.loc[i, day_shift_mt] = 0
    return df

