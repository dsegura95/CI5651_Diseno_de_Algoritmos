# Sudoku-Solver
#  Autores:
#       - David Segura
#       - Amin Arriaga

import multiprocessing, queue
from sys import argv
from time import time, sleep
from sudoku_to_SAT import sudoku_to_SAT, read_sudoku
from laura_SAT import laura_SAT, read_SAT
from SAT_to_sudoku import SAT_to_sudoku


def timer(f, t_max: float, *args) -> float:
    """ 
    Ejecuta una funcion, cancelando el proceso si se alcanza un tiempo maximo. 
    INPUT:
        - f: function   Funcion a ejecutar.
        - t_max:    Tiempo maximo.
        - *args:    Argumentos de la funcion.
    OUTPUT:
        - float:    Tiempo que tardo en ejecutarse la funcion. 0 en caso de
                    que alcance el tiempo maximo.
    """

    def wait(t_max = t_max):
        """ Funcion que finaliza al pasar un tiempo maximo. """
        initial_t = time()
        while time() - initial_t < t_max:
            pass
        # El return es necesario para el metodo put de multiprocessing.Queue().
        return
    
    # Creamos los hilos de ambas funciones.
    h1 = multiprocessing.Process(target=f, args=args)
    h2 = multiprocessing.Process(target=wait)

    t = time()
    h1.start()
    h2.start()
    while h2.is_alive() and h1.is_alive():
        pass
    t = time() - t

    # Verificamos cual se ejecuto primero y cancelamos el otro.
    if h1.is_alive(): h1.terminate(); return 0
    else: h2.terminate(); return t

def get_solution(V: [int], C: [[int]], result: multiprocessing.Queue):
    """ Funcion que ejecuta laura_SAT y guarda se resultado en una cola
    de multiprocessing. """
    result.put(laura_SAT(V, C, 1))
  
def sudoku_solver(sudoku: str, t_max: float) -> str:
    """ 
    Funcion que toma el string de una instancia de sudoku y
    lo resuelve.
    INPUT:
        - sudoku:   String que representa la instancia del sudoku.
        - t_max:    Tiempo maximo para la resolucion del sudoku.
    OUTPUT:
        - str:  Solucion del sudoku (en caso de no expirar el tiempo maximo).
    """
    # Obtenemos la representacion matricial del sudoku.
    sudoku_matrix = read_sudoku(sudoku)
    # Obtenemos la representacion en SAT del sudoku.
    sat = sudoku_to_SAT(sudoku_matrix)
    V, C = read_SAT(sat)
    # Creamos la cola para el multiprocessing.
    result = multiprocessing.Queue()
    # Obtenemos el tiempo y la solucion del sudoku.
    t = timer(get_solution, t_max, V, C, result)
    
    # Si el tiempo es distinto de 0
    if t:
        V_sol, conflict = result.get()
        string_solution, m = SAT_to_sudoku(V_sol)
        return string_solution + " Time: " + str(t)
    else:
        return "Time expired."


if __name__ == "__main__":
    if len(argv) == 1:
        sudoku = input("Escriba la instancia del sudoku (enter para cancelar): ")
        t = float("0" + input("Indique el tiempo maximo de ejecucion (enter para cancelar): "))
        while sudoku and t:
            print(sudoku_solver(sudoku, t) + "\n")
            sudoku = input("Escriba la instancia del sudoku (enter para cancelar): ")
            t = float("0" + input("Indique el tiempo maximo de ejecucion (enter para cancelar): ")

    elif len(argv) == 4:
        f = open(argv[1], "r")
        sudokus = f.readlines()
        f.close()
        f = open(argv[2], "w")
        t = float(argv[3])
        instancia = 1
        for s in sudokus:
            # Verificamos que no sean un salto de linea.
            if len(s) > 2:
                f.write(sudoku_solver(s[:-1], t) + "\n")
                print("Resuelta Instancia "+ str(instancia))
                instancia += 1
        f.close()

    else:
        raise Exception("Numero de argumentos invalidos.")
