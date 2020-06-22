# Sudoku-Solver
#  Autores:
#       - David Segura
#       - Amin Arriaga

from sys import argv
from time import time
from sudoku_to_SAT import sudoku_to_SAT, read_sudoku
from laura_SAT import laura_SAT, read_SAT
from SAT_to_sudoku import SAT_to_sudoku

def timer(f, t_max, *args):
    pass