# Using piece-wise linear cost profiles versus individual variables: a study.
Gurobi allows one to describe piece-wise linear costs per decision variable using `setPWLObj`. This, however, is an interface to a modelling trick which involves describing `n` constraints and one additional auxiliary decision variable. Piece-wise linear cost profile for a decision variable on a partition [x1, ..., xn] can be described as a collection of individual decision variables on each of the sub-intervals of the partition, and the question of interest is how each of these two approaches scales and how they compare. The code in this repo builds models and analyses obtained outputs to study such comparisons.

## Dependencies
* Python 3 (see `requirements.txt`)
* Gurobi 

Use `requirements.txt` in order to be able to run modelling experiments:

```
pip install requirements.txt
```

## How to run experiments
```
python pwl.py
```
## Known bugs
1. Upon producing `results.csv` some table cell labels have suffix `_copy` - this needs to be removed; this is probably due to the need to repeatedly generate experiments until solvable model instances are obtained.

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

## Observations
TBA...