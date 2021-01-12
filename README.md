# Using piece-wise linear cost profiles versus individual variables: a study.
Gurobi allows one to describe piece-wise linear costs per decision variable using `setPWLObj`. This, however, is an interface to a modelling trick which involves describing `n` constraints and one additional auxiliary decision variable. Piece-wise linear cost profile for a decision variable on a partition of an interval can be described as a collection of individual decision variables on each of the sub-intervals of the partition, and the question of interest is how each of these two approaches scales and how they compare. The code in this repo describes and implements simple models designed to study the effect of model size and complexity on performance.

## Dependencies
* Python 3 (see `requirements.txt`)
* Gurobi 

Use `requirements.txt` in order to be able to run modelling experiments:

```
pip install requirements.txt
```
## Model(s) implemented
### Model A (individual variables)
Fix <img src="https://latex.codecogs.com/svg.latex?X" title="X" /> and a partition <img src="https://latex.codecogs.com/svg.latex?\inline&space;\Pi" title="\Pi" /> of reals between 0 and <img src="https://latex.codecogs.com/svg.latex?X" title="X" />: 

<img src="https://latex.codecogs.com/svg.latex?\Pi:&space;\,&space;\pi_0=0\leq\pi_1\leq\ldots...\leq\pi_{n-1}\leq\pi_n=&space;X" title="\Pi: \, \pi_0=0\leq\pi_1\leq\ldots...\leq\pi_{n-1}\leq\pi_n= X" />

Fix <img src="https://latex.codecogs.com/svg.latex?\inline&space;S\in\mathbb{N}" title="S\in\mathbb{N}" /> and <img src="https://latex.codecogs.com/svg.latex?\inline&space;\gamma_0,\gamma_1,\ldots,\gamma_S&space;\in&space;(0,X)" title="\gamma_0,\gamma_1,\ldots,\gamma_S \in (0,X)" />. Let <img src="https://latex.codecogs.com/svg.latex?P" title="P" /> be a finite set of consecutive integers <img src="https://latex.codecogs.com/svg.latex?\inline&space;\{1,2,\ldots\}" title="\{1,2,\ldots\}" /> and let <img src="https://latex.codecogs.com/svg.latex?\inline&space;P_1,\ldots,P_S" title="P_1,\ldots,P_S" /> be its subsets, so that no two such subsets are the same.

Introduce continuous decision variables as follows: 

<img src="https://latex.codecogs.com/svg.latex?\inline&space;x_{i,p}\in[\pi_i,\pi_{i&plus;1}]" title="x_{i,p}\in[\pi_i,\pi_{i+1}]" />, <img src="https://latex.codecogs.com/svg.latex?\inline&space;i=1,\ldots,n" title="i=1,\ldots,n" />, <img src="https://latex.codecogs.com/svg.latex?\inline&space;p\in&space;P" title="p\in P" />. 

Consider the following set of constraints:

<img src="https://latex.codecogs.com/svg.latex?\begin{align}&space;\sum\limits_{p\in&space;P_0}\sum\limits_{i}x_{i,p}&=\gamma|P_0|,\nonumber\\&space;\sum\limits_{p\in&space;P_s}\sum\limits_{i}x_{i,p}&\leq\gamma_s&space;P_s,\,&space;s\in&space;1,2,\ldots,S.\nonumber&space;\end{}" title="\begin{align} \sum\limits_{p\in P_0}\sum\limits_{i}x_{i,p}&=\gamma|P_0|,\nonumber\\ \sum\limits_{p\in P_s}\sum\limits_{i}x_{i,p}&\leq\gamma_s P_s,\, s\in 1,2,\ldots,S.\nonumber \end{}" />

Model A minimises function 

<img src="https://latex.codecogs.com/svg.latex?\inline&space;\sum\limits_{i,p}&space;c_{i,p}x_{i,p}" title="\sum\limits_{i,p} c_{i,p}x_{i,p}" /> 

for some choice of weights <img src="https://latex.codecogs.com/svg.latex?\inline&space;c_{i,p}" title="c_{i,p}" />, where sequence <img src="https://latex.codecogs.com/svg.latex?\inline&space;\{c_{i,p}\}" title="\{c_{i,p}\}" /> is non-decreasing for each fixed <img src="https://latex.codecogs.com/svg.latex?\inline&space;p" title="p" />.

### Model B (augmented variables with piece-wise linear costs)
Model B is equivalent to Model A and is obtained by augmenting decision variables as follows:

<img src="https://latex.codecogs.com/svg.latex?\inline&space;y_p&space;=&space;\sum\limits_{i}x_{i,p}" title="y_p = \sum\limits_{i}x_{i,p}" />.

Same constraints apply as in model A and the objective function is as follows:

<img src="https://latex.codecogs.com/svg.latex?\inline&space;\sum\limits_{p}d_py_p" title="\sum\limits_{p}d_py_p" />,

where costs <img src="https://latex.codecogs.com/svg.latex?\inline&space;d_p" title="d_p" /> are calculated implicitly by the solver after passing PWL cost profiles for each variable <img src="https://latex.codecogs.com/svg.latex?\inline&space;y_p" title="y_p" /> (as sequence <img src="https://latex.codecogs.com/svg.latex?\inline&space;\{c_{i,p}\}" title="\{c_{i,p}\}" /> is non-decreasing for each fixed <img src="https://latex.codecogs.com/svg.latex?\inline&space;p" title="p" />, it is guaranteed that the resulting cost profiles are convex).

## Multiple model instances
We generate multiple Model A and Model B instances by varying <img src="https://latex.codecogs.com/svg.latex?\inline&space;\{\gamma_s\}" title="\{\gamma_s\}" /> and <img src="https://latex.codecogs.com/svg.latex?\inline&space;\{P_s\}" title="\{P_s\}" />. The size of the problem is controlled by the set <img src="https://latex.codecogs.com/svg.latex?\inline&space;P" title="P" /> and partition <img src="https://latex.codecogs.com/svg.latex?\inline&space;\Pi" title="\Pi" />. Cost profiles are fixed for a given partition <img src="https://latex.codecogs.com/svg.latex?\inline&space;\Pi" title="\Pi" /> and the number of its replications (size of set <img src="https://latex.codecogs.com/svg.latex?\inline&space;P" title="P" />).

## How to run experiments
```
python pwl.py
```
## Known bugs
1. Upon producing `results.csv` some table cell labels have suffix `_copy` - this needs to be removed prior to running `produce_graphs.py`; theis suffix is probably due to the need to repeatedly generate experiments until solvable model instances are obtained.

## How to analyse results
```
# the following will produce total run times (i.e. model building plus optimisation times)
python produce_graphs.py results.csv entire total_runtime
python produce_graphs.py results.csv shortened total_runtime

# the following will produce pure optimisation run times (i.e. model building times are left out)
python produce_graphs.py results.csv entire
python produce_graphs.py results.csv shortened
```

## Results
![alt text](figures/optimisation-only-entire-range-of-partition-size.png)
![alt text](figures/optimisation-only-small-partition-size.png)
![alt text](figures/total_runtimes-entire-range-of-partition-size.png)
![alt text](figures/total-runtimes-only-small-partition-size.png)

## Observations and preliminary conclusions
1. Pure optimisation run times depend both on the complexity (number of partition replications) and size of the model (main partition size). Pure optimisation run times for the models with augmented variables and PWL cost profiles outperform the model with individual variables for smaller values of the partition size, whereas larger problem sizes show the opposite effect.
2. Model building times, especially in the model instances with individual variables, have a dramatic effect on the total runtimes and show that augmentation with PWL cost profiles can be significantly faster. To emphasise, this effect is due to the time spent on building model instances with individual variables.
3. Note that model instances with individual variables are produced for arbitrary partitions. Model building times can be significantly improved by taking uniform partitions, so that each individual decision variable has the same domain. Albeit this is only a speculation, I suspect that will make total runtime comparable again.
4. Augmentation is not always possible. It is impossible to both have individual variables and their augmentations with PWL costs in Gurobi. Even when augmentation is possible, one should weigh up giving up the convenience of dealing with individual decision variables (e.g. in terms of dealing with the input data or interpreting the results). However, whenever augmentation is possible and the resulting cost profiles are ensured to be convex/concave, the transition is reasonably straightforward.
