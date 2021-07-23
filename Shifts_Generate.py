from Dataframe import *
from pulp import *
import json
import pandas as pd

df = create_dataframe()

shifts = list(df.columns)
shifts.remove('day')
shifts.remove('time')
shifts.remove('required')

# set variables to solve for
num_workers_for_shift = LpVariable.dicts("workers_per_shift", list(range(len(shifts))), lowBound=0, cat="Integer")

# define problem goal (minimize number of workers assigned to shifts)
prob = LpProblem("determine_number_of_each_shift", LpMinimize)

# specify we want to minimize the total number of shifts
prob += lpSum([num_workers_for_shift[i] for i in range(len(shifts))])

# specify that for every row, the shifts assigned must cover the requirement of the time window
# look at every row (i.e. every time window)
for row in range(len(df)):
    # add a constraint that number of shifts assigned must cover requirements for time window
    prob += lpSum([df.loc[row, shifts[j]] * num_workers_for_shift[j] for j in range(len(shifts))]) >= df.loc[row, 'required']

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
