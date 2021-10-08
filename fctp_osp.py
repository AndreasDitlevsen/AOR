from gurobipy import Model,GRB
from fctp_problem import FixedChargeTransportationProblem

class OSP:
	def __init__(self, p:FixedChargeTransportationProblem, y:dict):
		self.m = Model()
		self.p = p

		# Decision variables
		self.x = self.m.addVars(self.p.n_sources,self.p.n_sinks,name="x")

		# Objective function
		self.m.setObjective(self.x.prod(self.p.transport_cost),sense=GRB.MINIMIZE)

		# Constraints
		self.c1 = self.m.addConstrs(self.x.sum(i,'*') == self.p.supply[i] for i in range(self.p.n_sources))

		# TODO: CREATE THE REMAINING CONSTRAINTS
		self.c2 = self.m.addConstrs(self.x.sum('*', j) == self.p.demand[j] for j in range(self.p.n_sinks))
		# I wrote this before i saw the exact same line in fsp. I am pretty happy with getting it right on the first try.
		self.c3 = self.m.addConstrs(self.x[i, j] <= self.p.get_max_flow(i, j) * y[i, j] for i in range(self.p.n_sources) for j in range(self.p.n_sinks))

	def solve(self):
		self.m.optimize()

	def print_solution(self):
		print(self.m.getAttr('x', self.x))

	def get_objective(self):
		return self.m.objVal

	def get_duals(self):
		# TODO: RETURN THE OPTIMAL DUAL SOLUTION
		return self.m.getAttr(GRB.Attr.Pi,self.c1), self.m.getAttr(GRB.Attr.Pi,self.c2), self.m.getAttr(GRB.Attr.Pi,self.c3)