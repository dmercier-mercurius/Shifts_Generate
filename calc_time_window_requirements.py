import pandas as pd
import math


def calc_time_window_requirements_from_sector_data(path_to_file, sheet):
    query_sector_df = pd.read_excel(path_to_file, sheet)

    # create lists of...
    # dates as time stamps
    series_of_dates_time_stamps = query_sector_df['fldDate']
    # dates as strings
    series_of_dates_strings = query_sector_df['fldDate'].dt.strftime('%m-%d-%Y')
    # time windows
    list_of_time_windows = []
    for column in query_sector_df.columns:
        if column[0].isnumeric():
            list_of_time_windows.append(column)

    # set dates as strings
    query_sector_df['fldDate'] = query_sector_df['fldDate'].dt.strftime('%m-%d-%Y')
    # then set date strings as index
    query_sector_df = query_sector_df.set_index('fldDate')

    # add a column with day of the week
    day_of_week = []
    for date in series_of_dates_time_stamps:
        day_of_week.append(date.day_name())
    query_sector_df['day_of_week'] = day_of_week

    # BEGIN TO MAKE REQUIRED_DF

    # create dictionary with...
    # unique dates as keys
    # day of the week as value
    dict_of_unique_dates = {}
    for i in range(len(series_of_dates_strings)):
        date = series_of_dates_strings[i]
        day_of_week = series_of_dates_time_stamps[i].day_name()
        if date not in dict_of_unique_dates.keys():
            dict_of_unique_dates[date] = day_of_week

    # create column dictionary
    # sort dates and create date and day of week columns
    required_df_columns = {'date': [], 'day_of_week': []}
    for date in sorted(dict_of_unique_dates):
        required_df_columns['date'].append(date)
        required_df_columns['day_of_week'].append(dict_of_unique_dates[date])

    # assign time windows from original dataframe to dictionary above
    # fill each time window column with number of sectors open on given day during time window
    for time_window in list_of_time_windows:
        required_df_columns[time_window] = []
        for date in required_df_columns['date']:
            required_df_columns[time_window].append(sum(query_sector_df.loc[date, time_window]))

    # create df to hold number of bodies needed during each time window for each date
    required_df = pd.DataFrame.from_dict(required_df_columns)
    # set unique date as the key
    required_df = required_df.set_index('date')


    # MAKE DAILY AVERAGE DF

    # make daily_average_df_columns
    daily_average_df_columns = {
        'day_of_week': ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    }

    # look at each time window
    for time_window in list_of_time_windows:
        # create list to hold avg number of bodies needed on each day during given time window
        daily_average_df_columns[time_window] = []
        # look at each day
        for day in daily_average_df_columns['day_of_week']:
            # select rows with data about given day
            condition = required_df['day_of_week'] == day
            # calculate and append abg number of bodies needed on day during time window
            daily_avg_for_time_window = math.ceil(sum(required_df.loc[condition, time_window]) / len(required_df.loc[condition, time_window]))
            daily_average_df_columns[time_window].append(daily_avg_for_time_window)

    # create df
    daily_average_df = pd.DataFrame.from_dict(daily_average_df_columns)

    # set unique day of week as the key
    daily_average_df = daily_average_df.set_index('day_of_week')

    return daily_average_df





