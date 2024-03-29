import math
import random as rd
rd.seed(1)
from fctp_problem import FixedChargeTransportationProblem
from fctp_fullmodel import FullModel
from fctp_master import Master

# 1. We generate a random instance of the problem
n_sources = 3
n_sinks = 9

# We need to ensure that total supply equals total demand
supply = [rd.randint(20,40) for i in range(n_sources)]
total_supply = sum(supply)
# Now we assign demand such that they sum to the total supply
# We first randomly assign demand to n_sink-1 and the the remaining to the last sink
demand = [rd.randint(math.floor(total_supply/n_sinks)-5,math.floor(total_supply/n_sinks)+5) for j in range(n_sinks-1)]
demand.append(total_supply-sum(demand))
transport_cost = {(i,j) : rd.randint(2,8) for i in range(n_sources) for j in range(n_sinks)}
fixed_charge = {(i,j) : rd.randint(15,28) for i in range(n_sources) for j in range(n_sinks)}

# TODO: CREATE AN INSTANCE OF THE FIXED CHARGE TRANSPORTATION PROBLEM
p = FixedChargeTransportationProblem(n_sources, n_sinks, supply, demand, transport_cost, fixed_charge)

# TODO: SOLVE THE PROBLEM VIA BENDERS

mp = Master(p)
mp.solve()

# TODO: SOLVE THE FULL MODEL (I.E., WITHOUT DECOMPOSITION)
fm = FullModel(p)
fm.solve()

# TODO: PRINT THE SOLUTION TO THE FULL PROBLEM AND TO BD
print()
fm.print_solution()
print()
mp.print_solution()
print()
# Using added getters
print("Difference: ", abs(mp.get_objVal() - fm.get_obj()))