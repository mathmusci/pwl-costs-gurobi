# A study of using piece-wise linear cost profiles versus individual variables.
Gurobi allows one to describe piece-wise linear costs per decision variable using `setPWLObj`. This, however, is an interface to a modelling trick which involves describing `n` constraints and one additional auxiliary decision variable. Piece-wise linear cost profile for a decision variable on a partition [x1, ..., xn] can be described as a collection of individual decision variables on each of the sub-intervals of the partition, and the question how does each of these two approaches scale and how they compare. The code in this repo builds models and analyses obtained outputs to study such comparisons.

## Dependencies
* Python 3 (see `requirements.txt`)
* Gurobi 

Use `requirements.txt` in order to be able to run modelling experiments:

```
pip3 install requirements.txt
```

## How to run experiments
```
python3 pwl.py
```
## How to analyse results
```
python3 produce_graphs.py results.csv
```
