from random import random 
from numpy import cumsum
import pandas as pd
import time
import gurobipy as grb

class PWLTest(object):
	"""Compare run times for models with individual decision variables (and their sums) 
	and augmented variables.
	
	This class follows the following scheme:
	Prepare data subsequently used in the models.
	Use synthesised data and prepare multiple instances of two model types:
		- with multiple independent decision variables;
		- with variable augmentation and PWL objective.
	"""
	def __init__(self, x_range):
		"""Define partition and model placeholders.
		"""
		self.x_range = x_range
		if any(a-b < 0 for a,b in zip(self.x_range[1:], self.x_range[:-1])):
			raise ValueError("x_range is a non-increasing sequence.")		
		self.model_with_separate_variables = dict()
		self.model_with_pwl_costs = dict()
		self.runtimes = list()
		
		self.costs = dict()
		self.number_of_partitions = None
		self.interval_ends = None
		self.partitions = None
		
		self.model_with_separate_variables_runtime = dict()
		self.model_with_pwl_costs_runtime = dict()
		self.run_times = list()

		self.model_with_separate_variables_build_times = dict()
		self.model_with_pwl_costs_build_times = dict()
		self.model_build_times = list()

	def generate_models(self, number_of_models, number_of_partitions, group_size=2, overlap_size=0, cost_increase_coeff=2, output_models=False):
		"""Generate models, variables and constraints.
		"""
		# instantiate Gurobi models		
		t = time.time()
		self.model_with_separate_variables = {str(k): grb.Model(f'model_with_separate_variables_{k}') for k in range(number_of_models)}
		self.model_with_pwl_costs = {str(k): grb.Model(f'model_with_pwl_costs_{k}') for k in range(number_of_models)}

		# prepare placeholders for decision variables (use tupledict for easy summation later)
		self.model_with_separate_variables_vars = grb.tupledict()
		self.model_with_pwl_costs_vars = grb.tupledict()
		
		# prepare some auxiliary data		
		interval_ends = list(zip(self.x_range[:-1], self.x_range[1:]))
		self.interval_ends = interval_ends
		x_diffs = [a-b for a,b in zip(self.x_range[1:], self.x_range[:-1])]

		partitions = list(range(number_of_partitions))
		self.partitions = partitions
		K = random() * self.x_range[-1]
		index_tuples = [tuple(partitions[i:i+group_size]) for i in range(0, len(partitions), group_size-overlap_size)]
		M = {index_tuple: random() * self.x_range[-1] for index_tuple in index_tuples}
		constant_part_of_model_build_times = time.time() - t

		## describe models with separate variables
		for m_str, m in self.model_with_separate_variables.items():
			print("building model {} (separate variables)".format(m_str))
			t = time.time()
			# generate costs for this model
			m.setObjective(0.0, grb.GRB.MINIMIZE)
			self.costs[m_str] = {p: list(cumsum([cost_increase_coeff*random() for x in self.x_range])) for p in range(number_of_partitions)}
			# define variables			
			for partition in partitions:
				for c, (interval_start, interval_end) in enumerate(interval_ends): 
					self.model_with_separate_variables_vars[m_str, partition, interval_start, interval_end] = m.addVar(lb=0, 
																	ub=interval_end - interval_start, 
																	obj=self.costs[m_str][partition][c], 
																	vtype=grb.GRB.CONTINUOUS,
																	name="X_{},{},{},{}".format(m_str, partition, interval_start, interval_end)
																	)
			# describe constraints			
			m.addConstr(self.model_with_separate_variables_vars.sum(m_str, '*', '*', '*') == number_of_partitions * K)
			m.addConstrs(grb.quicksum(self.model_with_separate_variables_vars.sum(m_str, p, '*', '*') for p in ps) <= len(ps) * M[ps] for ps in M)

			self.model_with_separate_variables_build_times[m_str] = constant_part_of_model_build_times + time.time() - t
			self.model_build_times.append({'model number': m_str,
								 		   'model name': m.ModelName,
								  		   'time taken to build model (in seconds)': self.model_with_separate_variables_build_times[m_str]
								  		   })

			# output model description if output_models flag is True
			if output_models:
				m.write('{}.lp'.format(m.ModelName))

		## describe models with augmented variables		
		for m_str, m in self.model_with_pwl_costs.items():
			print("building model {} (augmented variables)".format(m_str))
			t = time.time()
			m.setObjective(0.0, grb.GRB.MINIMIZE)
			# define variables
			for partition in partitions:
				total_costs = list(cumsum([u_c*x_diff for u_c, x_diff in zip([0] + self.costs[m_str][partition][:-1], [0] + x_diffs)]))
				self.model_with_pwl_costs_vars[m_str, partition] = m.addVar(lb=self.x_range[0], 
																			ub=self.x_range[-1], 
																			vtype=grb.GRB.CONTINUOUS,
																			name="X_{},{}".format(m_str, partition, interval_start, interval_end)
																			)
				m.setPWLObj(self.model_with_pwl_costs_vars[m_str, partition], self.x_range, total_costs)

			# describe constraints			
			m.addConstr(self.model_with_pwl_costs_vars.sum(m_str, '*') == number_of_partitions * K)
			m.addConstrs(grb.quicksum(self.model_with_pwl_costs_vars[m_str, p] for p in ps) <= len(ps) * M[ps] for ps in M)

			self.model_with_pwl_costs_build_times[m_str] = constant_part_of_model_build_times + time.time() - t
			self.model_build_times.append({'model number': m_str,
								 		   'model name': m.ModelName,
								  		   'time taken to build model (in seconds)': self.model_with_pwl_costs_build_times[m_str]
								  		   })

			# output model description if output_models flag is True
			if output_models:
				m.write('{}.lp'.format(m.ModelName))

	def optimise(self, log_to_console=True, output_flag=True):
		"""Optimise all generated models.
		"""
		for m_str, m in self.model_with_separate_variables.items():
			if not log_to_console:
				m.setParam("LogToConsole", 0)
			if not output_flag:
				m.setParam("OutputFlag", 0)        			
			
			t = time.time()
						
			m.optimize()
			
			if m.Status == grb.GRB.INFEASIBLE:
				raise ValueError("Model infeasible. I will stop here as the setup will lead to a bunch of infeasible models. Please, review the setup or change input parameters before continuing.")
			self.model_with_separate_variables_runtime[m_str] = time.time() - t			
			self.runtimes.append({'model number': m_str,
								  'model name': m.ModelName,
								  'time taken to optimise (in seconds)': self.model_with_separate_variables_runtime[m_str],
								  'number of partitions': len(self.partitions),
								  'partition size': len(self.x_range)})

		for m_str, m in self.model_with_pwl_costs.items():
			if not log_to_console:
				m.setParam("LogToConsole", 0)
			if not output_flag:
				m.setParam("OutputFlag", 0)        			

			t = time.time()
			m.optimize()
			if m.Status == grb.GRB.INFEASIBLE:
				raise ValueError("Model infeasible. I will stop here as the setup will lead to a bunch to infeasible models. Please, review the setup or change input parameters before continuing.")			
			self.model_with_pwl_costs_runtime[m_str] = time.time() - t
			self.runtimes.append({'model number': m_str,
								  'model name': m.ModelName,
								  'time taken to optimise (in seconds)': self.model_with_pwl_costs_runtime[m_str],
								  'number of partitions': len(self.partitions),
								  'partition size': len(self.x_range)})

	def save_runtimes_as_csv(self, output_filename='run_times.csv'):
		"""Export run time statistics for all optimised models into a csv file.
		"""
		df = pd.DataFrame(self.runtimes)
		df.to_csv(output_filename, index=False) 

	def print_results(self):
		"""Output the solution and the value of the objective function for each of the considered models.
		"""
		# for m_str, m in self.model_with_separate_variables.items():			
		# 	try: 
		# 		print("\nModel {}".format(m.ModelName))
		# 		print("The value of the objective function after optimisation is {}".format(m.objVal))
		# 		print("Variables are as follows:")
		# 		for partition in self.partitions:
		# 			# for c, (interval_start, interval_end) in enumerate(self.interval_ends):
		# 			# 	# x = round(self.model_with_separate_variables_vars[m_str, partition, interval_start, interval_end].X, 2)
		# 			# 	# x = self.model_with_separate_variables_vars[m_str, partition, interval_start, interval_end].X
		# 			# 	# print("X_{}_{}_{} = {}".format(partition, interval_start, interval_end, x))
		# 			# 	x = self.model_with_separate_variables_vars.sum(m_str, partition, '*', '*').getValue()
		# 			# 	print("X_{} = {}".format(partition, x))
		# 			x = self.model_with_separate_variables_vars.sum(m_str, partition, '*', '*').getValue()
		# 			print("X_{} = {}".format(partition, x))
		# 	except AttributeError:
		# 		print("\nModel {} is infeasible!".format(m_str))

		# for m_str, m in self.model_with_pwl_costs.items():			
		# 	try: 
		# 		print("\nModel {}".format(m.ModelName))
		# 		print("The value of the objective function after optimisation is {}".format(m.objVal))
		# 		print("Variables are as follows:")
		# 		for partition in self.partitions:
		# 			x = self.model_with_pwl_costs_vars[m_str, partition].X
		# 			print("X_{} = {}".format(partition, x))
		# 	except AttributeError:
		# 		print("\nModel {} is infeasible!".format(m_str))

		print("\n MODEL COMPARISON")
		for m_str in self.model_with_separate_variables:
			print("\n{} (objective {}) | {} (objective {})".format(self.model_with_separate_variables[m_str].ModelName, self.model_with_separate_variables[m_str].objVal,\
																 	self.model_with_pwl_costs[m_str].ModelName, self.model_with_pwl_costs[m_str].objVal))
			print("runtimes (in seconds): {} | {}".format(self.model_with_separate_variables_runtime[m_str], self.model_with_pwl_costs_runtime[m_str]))
			for partition in self.partitions:
				x_model_with_separate_variables = self.model_with_separate_variables_vars.sum(m_str, partition, '*', '*').getValue()
				x_model_with_pwl_costs = self.model_with_pwl_costs_vars[m_str, partition].X
				print("X_{}: {} | {}".format(partition, x_model_with_separate_variables, x_model_with_pwl_costs))


def main():
	PARTITION_SIZES = [5, 10, 50, 100, 250, 500, 750, 1000, 2000, 3000, 4000, 5000]
	NUMBERS_OF_PARTITIONS = [5, 20, 50, 100, 250, 500]

	# PARTITION_SIZES = [5, 10, 50]
	# NUMBERS_OF_PARTITIONS = [5, 20, 50]

	NUMBER_OF_MODEL_INSTANCES = 25
	COST_INCREASE_COEFFICIENTS = 1
	OUTPUT_MODELS = False
	RESULTS_OUTPUT_CSV = 'results.csv'
	LOG_TO_CONSOLE = False
	OUTPUT_FLAG = False

	runtimes = list()
	model_build_times = list()

	for partition_size in PARTITION_SIZES:
		for number_of_partitions in NUMBERS_OF_PARTITIONS:
			_pass = True
			while _pass:		
				try:
					print("partition_size = {}, number_of_partitions = {}".format(partition_size, number_of_partitions))
					pwl_test = PWLTest(x_range=list(range(partition_size)))
					pwl_test.generate_models(number_of_models=NUMBER_OF_MODEL_INSTANCES, 
											 number_of_partitions=number_of_partitions, 
											 cost_increase_coeff=COST_INCREASE_COEFFICIENTS, 
											 output_models=OUTPUT_MODELS)
					pwl_test.optimise(log_to_console=LOG_TO_CONSOLE, output_flag=OUTPUT_FLAG)
					runtimes += pwl_test.runtimes
					model_build_times += pwl_test.model_build_times
					# pwl_test.print_results()
					# pwl_test.save_runtimes_as_csv()
					_pass = False
				except ValueError:
					pass

	runtimes_df = pd.DataFrame(runtimes)	
	model_build_times_df = pd.DataFrame(model_build_times)

	output_df = runtimes_df.merge(model_build_times_df, on=['model number', 'model name'], left_index=True, right_index=True)
	output_df.to_csv(RESULTS_OUTPUT_CSV, index=False)

if __name__ == "__main__":
    main()