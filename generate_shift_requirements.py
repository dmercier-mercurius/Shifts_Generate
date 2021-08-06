from calc_time_window_requirements import calc_time_window_requirements_from_sector_data
from create_coefficient_matrix import *
from pulp import *
import json


# read in data from query_sector excel sheet
path_to_file = '/Users/davismercier/Desktop/sector_count_data.xlsx'
sheet = 'qrySectorCount'
shift_length = 8

daily_average_df = calc_time_window_requirements_from_sector_data(path_to_file, sheet)
coefficient_matrix_df = create_coefficient_matrix_dataframe(daily_average_df, shift_length)


shifts = list(coefficient_matrix_df.columns)
shifts.remove('day_of_week')
shifts.remove('time_window')
shifts.remove('required')

# set variables to solve for
num_workers_per_shift = LpVariable.dicts("workers_for", shifts, lowBound=0, cat="Integer")
print('number of workers per shift', num_workers_per_shift)

# define problem goal (minimize number of workers assigned to shifts)
prob = LpProblem("determine_number_of_each_shift", LpMinimize)

# specify we want to minimize the total number of shifts
prob += lpSum([num_workers_per_shift[shift] for shift in shifts])

# specify that for every row, the shifts assigned must cover the requirement of the time window
# look at every row (i.e. every time window)
for row in range(len(coefficient_matrix_df)):
    # add a constraint that number of shifts assigned must cover requirements for time window
    prob += lpSum([coefficient_matrix_df.loc[row, shift] * num_workers_per_shift[shift] for shift in shifts]) >= coefficient_matrix_df.loc[row, 'required']

# create binary tracker variables for each distinct shift (i.e. 0600, 0630, etc)
# if one of these shifts is assigned on any day, the value of these binary variables becomes 1
distinct_shifts = {}

for day_shift in shifts:
    day, shift = day_shift.split(' ')
    try:
        distinct_shifts[shift]
    except KeyError:
        distinct_shifts[shift] = LpVariable(shift, 0, 1, cat="Integer")  # shift is only allowed to be 0 or 1
    finally:
        prob += num_workers_per_shift[day_shift] <= 100000 * distinct_shifts[shift]   # if number of shifts is greater than 1, y must equal 1

# sort distinct shifts into categories
mid_shifts = {}
day_shifts = {}
eve_shifts = {}

for mt_shift, lpvar in distinct_shifts.items():
    if determine_type_of_shift(mt_to_int(mt_shift), shift_length) == 'MID':
        mid_shifts[mt_shift] = lpvar
    elif determine_type_of_shift(mt_to_int(mt_shift), shift_length) == 'DAY':
        day_shifts[mt_shift] = lpvar
    else:
        eve_shifts[mt_shift] = lpvar

# restrict number of shifts in each category to 4
prob += lpSum(mid_shifts.values()) <= 4
prob += lpSum(day_shifts.values()) <= 4
prob += lpSum(eve_shifts.values()) <= 4

status = prob.solve()
print(LpStatus[status])

dict_to_return = {
    'schedule': None,
    'shift_length': 8,
    'PWP': ['EVE', 'EVE', 'DAY', 'DAY', 'MID'],
    'PSO': ['1500', '1300', '0700', '0600', '2300'],
    'daily_shifts': {}
}

for day_shift in shifts:
    day, shift = day_shift.split(" ")
    quantity = int(num_workers_per_shift[day_shift].value())

    if quantity > 0:
        try:
            dict_to_return['daily_shifts'][day][shift] = quantity
        except KeyError:
            dict_to_return['daily_shifts'][day] = {}
            dict_to_return['daily_shifts'][day][shift] = quantity

json_to_return = json.dumps(dict_to_return, indent=4)
print(json_to_return)
