from gurobipy import Model,GRB,quicksum
from fctp_problem import FixedChargeTransportationProblem
from fctp_fsp import FSP
from fctp_osp import OSP

class Master:
	def __init__(self, p:FixedChargeTransportationProblem):
		self.m = Model()
		self.p = p

		# Decision variables
		self.y = self.m.addVars(self.p.n_sources, self.p.n_sinks,vtype=GRB.BINARY, name="x")
		self.phi = self.m.addVar(name="phi")
		# Objective function
		self.m.setObjective(self.y.prod(self.p.fixed_charge)+self.phi,sense=GRB.MINIMIZE)

		# Makes the variables visible in the callback
		self.m._y = self.y
		self.m._phi = self.phi

	def solve(self):
		def callback(model, where):
			# TODO: COMPLETE THE CALLBACK TO ADD CUTS AT INTEGER NODES
			if where == GRB.Callback.MIPSOL:
				y_val = model.cbGetSolution(model._y)
				phi_val = model.cbGetSolution(model._phi)

				# Solve F(x)
				fsp = FSP(self.p, y_val)
				fsp.solve()
				dualsc1, dualsc2, dualsc3 = fsp.get_duals()
				obj = fsp.get_objective()

				# Check feasibility
				if obj > 0:
					# Construct and add cut.

					# Initial version
					#lhs = 0
					#for i in range(self.p.n_sources):
					#	lhs += dualsc1[i] * self.p.supply[i]
					#for j in range(self.p.n_sinks):
					#	lhs += dualsc2[j] * self.p.demand[j]
					#for i in range(self.p.n_sources):
					#	for j in range(self.p.n_sinks):
					#		lhs += dualsc3[i, j] * self.p.get_max_flow(i, j) * model._y[i, j]

					# Quicksum version
					lhs = quicksum([dualsc1[i] * self.p.supply[i] for i in range(self.p.n_sources)]) \
						+ quicksum([dualsc2[j] * self.p.demand[j] for j in range(self.p.n_sinks)]) \
						+ quicksum([dualsc3[i, j] * self.p.get_max_flow(i, j) * model._y[i, j]
									for i in range(self.p.n_sources) for j in range(self.p.n_sinks)])
					model.cbLazy(lhs <= 0)

				else:
					# Solve sub-problem
					osp = OSP(self.p, y_val)
					osp.solve()
					dualsc1, dualsc2, dualsc3 = osp.get_duals()
					obj = osp.get_objective()

					# Check optimality
					if obj <= phi_val:
						print("Optimal!")
					else:
						# Construct and add cut
						lhs = quicksum([dualsc1[i] * self.p.supply[i] for i in range(self.p.n_sources)]) \
							+ quicksum([dualsc2[j] * self.p.demand[j] for j in range(self.p.n_sinks)]) \
							+ quicksum([dualsc3[i, j] * self.p.get_max_flow(i, j) * model._y[i, j]
										for i in range(self.p.n_sources) for j in range(self.p.n_sinks)])
						model.cbLazy(lhs <= model._phi)

		self.m.setParam(GRB.Param.LazyConstraints, 1)
		self.m.optimize(callback)

	# Added getter for comparing results
	def get_objVal(self):
		return self.m.objVal

	def print_solution(self):
		print("Optimal objective value",self.m.objVal)
		print(self.m.getAttr('x', self.y))