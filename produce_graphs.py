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

	df = pd.read_csv(run_times_csv_filename)

	df['model'] = df['model name'].apply(detect_model)
	df.drop(columns=['model number', 'model name'], inplace=True)
	df = pd.pivot_table(df, values='time taken to optimise (in seconds)', index=['number of partitions', 'partition size', 'model'], aggfunc=np.mean)
	df = df.reset_index()
	# print(df)

	width, height = 1200, 800
	G = figure(title = 'Comparison of optimisation run times for the models with individual decision variables and their augmentations via PWL cost profiles.', width = width, 
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
	G.yaxis.axis_label = 'optimisation run time'

	# tune range to be displayed
	# G.x_range.end = 2000
	# G.y_range.end = 4

	show(G)

if __name__ == "__main__":
    main()		