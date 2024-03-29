from gurobipy import Model,GRB,quicksum
from fctp_problem import FixedChargeTransportationProblem

class FSP:
	def __init__(self, p:FixedChargeTransportationProblem, y:dict):
		self.m = Model()
		self.p = p
		self.m.setParam("OutputFlag", 0)

		# Decision variables
		self.x = self.m.addVars(self.p.n_sources,self.p.n_sinks,name="x")
		self.vA1 = self.m.addVars(self.p.n_sources,name="vA+")
		self.vA2 = self.m.addVars(self.p.n_sources, name="vA-")
		self.vB1 = self.m.addVars(self.p.n_sinks, name="vB+")
		self.vB2 = self.m.addVars(self.p.n_sinks, name="vB-")
		self.vC = self.m.addVars(self.p.n_sources,self.p.n_sinks,name="vC")
		# Objective function
		# TODO: Create the objective function

		# Initial version
		#for i in range(self.p.n_sources):
		#	expr += self.vA1[i] + self.vA2[i]
		#for j in range(self.p.n_sinks):
		#	expr += self.vB1[j] + self.vB2[j]
		#for i in range(self.p.n_sources):
		#	for j in range(self.p.n_sinks):
		#		expr += self.vC[i, j]

		# Quicksum version
		expr = quicksum([self.vA1[i] + self.vA2[i] for i in range(self.p.n_sources)])\
			+ quicksum([self.vB1[j] + self.vB2[j] for j in range(self.p.n_sinks)])\
			+ quicksum([self.vC[i, j] for i in range(self.p.n_sources) for j in range(self.p.n_sinks)])

		self.m.setObjective(expr, GRB.MINIMIZE)

		# Constraints
		self.c1 = self.m.addConstrs(self.x.sum(i,'*') + self.vA1[i] - self.vA2[i] == self.p.supply[i] for i in range(self.p.n_sources))
		self.c2 = self.m.addConstrs(self.x.sum('*',j) + self.vB1[j] - self.vB2[j] == self.p.demand[j] for j in range(self.p.n_sinks))
		self.c3 = self.m.addConstrs(self.x[i,j] - self.vC[i,j] <= self.p.get_max_flow(i,j)*y[i,j] for i in range(self.p.n_sources) for j in range(self.p.n_sinks))

	def solve(self):
		self.m.optimize()

	def print_solution(self):
		print(self.m.getAttr('x',self.x))

	def get_objective(self):
		# TODO: Return the optimal objective value
		return self.m.objVal

	def get_duals(self):
		return self.m.getAttr(GRB.Attr.Pi,self.c1), self.m.getAttr(GRB.Attr.Pi,self.c2), self.m.getAttr(GRB.Attr.Pi,self.c3)
