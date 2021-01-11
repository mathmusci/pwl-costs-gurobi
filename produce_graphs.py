import sys
import pandas as pd
import numpy as np

from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, FactorRange, Range1d, LabelSet, \
						 LinearAxis, FixedTicker, Label
from bokeh.palettes import Spectral11, Category20b, Colorblind
from bokeh.io import output_file, show, save


def detect_model(m_descr):
	return 'model_with_separate_variables' if 'model_with_separate_variables' in m_descr else 'model_with_pwl_costs'

def main():
	run_times_csv_filename = sys.argv[1]
	x_range = sys.argv[2] # 'shortened' or 'entire'
	X_RANGE_ARGUMENT_VALUES = ['shortened', 'entire']
	if x_range not in X_RANGE_ARGUMENT_VALUES:
		raise ValueError("second argument should be {}".format(' or '.join(X_RANGE_ARGUMENT_VALUES)))

	if len(sys.argv) > 3:
		total_runime = True if sys.argv[3] == 'total_runtime' else False
	else:
		total_runime = False


	print("sys.argv[2].lower() = {}; total_runime = {}".format(sys.argv[2].lower(), total_runime))

	df = pd.read_csv(run_times_csv_filename)

	df['model'] = df['model name'].apply(detect_model)
	df.drop(columns=['model number', 'model name'], inplace=True)

	
	if total_runime:
		df['time taken to optimise (in seconds)'] += df['time taken to build model (in seconds)']
		figure_title = 'Comparison of total optimisation run times (including model building) for the models with individual decision variables and their augmentations via PWL cost profiles.'
	else:
		figure_title = 'Comparison of optimisation run times for the models with individual decision variables and their augmentations via PWL cost profiles.'

	df = pd.pivot_table(df, values='time taken to optimise (in seconds)', index=['number of partitions', 'partition size', 'model'], aggfunc=np.mean)
	df = df.reset_index()
	# print(df)

	width, height = 1200, 800
	
	G = figure(title = figure_title, 
			   width = width, 
			   height = height,
	           tools = 'save')

	line_dash = {'model_with_separate_variables': 'solid', 'model_with_pwl_costs': 'dotdash'}
	palette = list(reversed(list(Colorblind[8])))
	colors = dict()

	for number_of_partitions in df['number of partitions'].unique():
		colors[number_of_partitions] = palette[0]
		palette = palette[1:]


	for (number_of_partitions, model), group in df.groupby(['number of partitions', 'model']):
		CDS = ColumnDataSource(group)
		# try various other glyph methods from http://bokeh.pydata.org/en/0.10.0/docs/reference/plotting.html
		if model == 'model_with_separate_variables':
			G.diamond_cross(x = 'partition size', 
							y = 'time taken to optimise (in seconds)', 
							source = CDS,
							size=10,
							color=colors[number_of_partitions])
		if model == 'model_with_pwl_costs':
			G.asterisk(x = 'partition size', 
							y = 'time taken to optimise (in seconds)', 
							source = CDS,
							size=10,
							color=colors[number_of_partitions])
		G.line(x='partition size', 
			   y='time taken to optimise (in seconds)', 
			   source=CDS, 
			   line_dash=line_dash[model],
			   line_width=1.5,
			   color=colors[number_of_partitions],
			   legend_label = 'number of partitions = {} ({})'.format(number_of_partitions, model.replace('_', ' ')))
	G.legend.location = 'top_left'
	G.xaxis.axis_label = 'partition size'
	G.yaxis.axis_label = 'optimisation run time (in seconds)'

	# tune range to be displayed
	# G.x_range.end, G.y_range.end = 500, 0.6
	if total_runime and x_range == 'shortened':
		G.x_range.end, G.y_range.end = 1000, 10
	elif total_runime and x_range == 'entire':
		G.x_range.end, G.y_range.end = 5100, 60
	elif not total_runime and x_range=='shortened':
		G.x_range.end, G.y_range.end = 1000, 1.5
	elif not total_runime and x_range=='entire':
		G.x_range.end, G.y_range.end = 5100, 40

	show(G)

if __name__ == "__main__":
    main()		