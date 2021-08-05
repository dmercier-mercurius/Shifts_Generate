from calc_time_window_requirements import calc_time_window_requirements_from_sector_data
from create_coefficient_matrix import create_coefficient_matrix_dataframe
from pulp import *
import json


# read in data from query_sector excel sheet
path_to_file = '/Users/davismercier/Desktop/sector_count_data.xlsx'
sheet = 'qrySectorCount'

daily_average_df = calc_time_window_requirements_from_sector_data(path_to_file, sheet)
coefficient_matrix_df = create_coefficient_matrix_dataframe(daily_average_df, 8)


shifts = list(coefficient_matrix_df.columns)
shifts.remove('day_of_week')
shifts.remove('time_window')
shifts.remove('required')

# set variables to solve for
num_workers_for_shift = LpVariable.dicts("workers_per_shift", list(range(len(shifts))), lowBound=0, cat="Integer")

# define problem goal (minimize number of workers assigned to shifts)
prob = LpProblem("determine_number_of_each_shift", LpMinimize)

# specify we want to minimize the total number of shifts
prob += lpSum([num_workers_for_shift[i] for i in range(len(shifts))])

# specify that for every row, the shifts assigned must cover the requirement of the time window
# look at every row (i.e. every time window)
for row in range(len(coefficient_matrix_df)):
    # add a constraint that number of shifts assigned must cover requirements for time window
    prob += lpSum([coefficient_matrix_df.loc[row, shifts[j]] * num_workers_for_shift[j] for j in range(len(shifts))]) >= coefficient_matrix_df.loc[row, 'required']

status = prob.solve()
print(LpStatus[status])

dict_to_return = {
    'schedule': None,
    'shift_length': 8,
    'PWP': ['EVE', 'EVE', 'DAY', 'DAY', 'MID'],
    'PSO': ['1500', '1300', '0700', '0600', '2300'],
    'daily_shifts': {}
}

for i in range(len(shifts)):
    day, shift = shifts[i].split(" ")
    quantity = int(num_workers_for_shift[i].value())

    try:
        dict_to_return['daily_shifts'][day][shift] = quantity
    except KeyError:
        dict_to_return['daily_shifts'][day] = {}
        dict_to_return['daily_shifts'][day][shift] = quantity

json_to_return = json.dumps(dict_to_return, indent=4)
print(json_to_return)
