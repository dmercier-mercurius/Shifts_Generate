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


# receives starting time of a shift in the range 0 - 23 and returns type of shift
def determine_type_of_shift(shift_start, shift_length):

    if (7 - shift_length / 2) < shift_start <= (7 + shift_length / 2):
        return "DAY"
    elif (15 - shift_length / 2) < shift_start <= (15 + shift_length / 2):
        return "EVE"
    else:
        return "MID"


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


def create_coefficient_matrix_dataframe(daily_average_df, shift_length):

    days = daily_average_df.index.values
    time_windows = daily_average_df.columns

    shifts_mt = []
    columns = {'day_of_week': [], 'time_window': []}
    shifts = {}

    for day in days:
        for time_window in time_windows:
            columns['day_of_week'].append(day)
            columns['time_window'].append(time_window)
            shifts_mt.append(time_window)

    for day in days:
        for shift_mt in shifts_mt:
            shifts[day + " " + shift_mt] = mt_to_int(shift_mt)
            columns[day + " " + shift_mt] = [None] * len(columns['time_window'])

    columns['required'] = [None] * len(columns['day_of_week'])

    coefficient_matrix_df = pd.DataFrame(columns)

    for day_shift_mt, shift in shifts.items():
        for i in range(len(coefficient_matrix_df)):
            shift_day, shift_mt = day_shift_mt.split(" ")
            tw_day = coefficient_matrix_df.loc[i, 'day_of_week']
            time = coefficient_matrix_df.loc[i, 'time_window']
            hours = time[0:2]
            minutes = time[2:4]

            if shift_day == tw_day:
                if time_during_shift(hours, minutes, shift, shift_length) == True:
                    coefficient_matrix_df.loc[i, day_shift_mt] = 1
                elif time_during_shift(hours, minutes, shift, shift_length) == "previous_day":
                    coefficient_matrix_df.loc[i, day_shift_mt] = 0
                    # find the row with the same time on the previous day
                    filt = (coefficient_matrix_df['day_of_week'] == previous(shift_day)) & (coefficient_matrix_df['time_window'] == time)
                    coefficient_matrix_df.loc[filt, day_shift_mt] = 1
                else:
                    coefficient_matrix_df.loc[i, day_shift_mt] = 0
            else:
                if coefficient_matrix_df.loc[i, day_shift_mt] == None:
                    coefficient_matrix_df.loc[i, day_shift_mt] = 0

            coefficient_matrix_df.loc[i, 'required'] = daily_average_df.loc[tw_day, time]

    return coefficient_matrix_df
