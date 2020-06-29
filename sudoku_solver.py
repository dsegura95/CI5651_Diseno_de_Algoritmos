# Sudoku-Solver
#  Autores:
#       - David Segura
#       - Amin Arriaga

import multiprocessing, queue, os, subprocess, re
import matplotlib.pyplot as plt
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
    result.put(laura_SAT(V, C))

def print_sudoku(sudoku) -> str:
    """ 
    Metodo para imprimir un sudoku
    INPUT:
        - sudoku: recibe el sudoku en forma de Matriz
    OUTPUT:
        - str:    sudoku ya en formato de juego
    """
    N = abs(len(sudoku)**(1/2))
    bar = ' '
    row = ' '
    final = ''
    for i in range(len(sudoku)):
        bar += '--'
        if (i+1)%N == 0 and (i+1) != N**2:
            if (i+1) / N > 1:
                bar += '-+'
            else:
                bar += '+'

    for i in range(len(sudoku)):
        for j in range(len(sudoku)):
            if sudoku[i][j] == 0:
                row += '_ '
            else:
                row += str(sudoku[i][j]) + ' '
            if (j+1)%N == 0 and (j+1) != N**2:
                row += '| '
        final += row + "\n"
        row = ' '
        if (i+1) % N == 0 and (i+1) != N**2:
            final += bar + "\n"
    return final

def sudoku_solver(sat: str, t_max: float) -> (float, str,[[int]]):
    """ 
    Funcion que toma el string de una instancia de sudoku y
    lo resuelve.
    INPUT:
        - sat:      String que representa la instancia del sudoku en CNF.
        - t_max:    Tiempo maximo para la resolucion del sudoku.
    OUTPUT:
        - float:  Valor del tiempo
        - str:  Solucion del sudoku (en caso de no expirar el tiempo maximo).
    """
    V, C = read_SAT(sat)
    # Creamos la cola para el multiprocessing.
    result = multiprocessing.Queue()
    # Obtenemos el tiempo y la solucion del sudoku.
    t = timer(get_solution, t_max, V, C, result)
    
    # Si el tiempo es distinto de 0
    if t:
        V_sol, conflict = result.get()
        string_solution, m = SAT_to_sudoku(V_sol)
        return (t, string_solution + " Time: " + str(t),m)
    else:
        return (0,"Time expired.",[[0]])

def zchaff_run(path,problem) -> str:
    """ 
    Funcion que toma el string en formato CNF de una instancia de sudoku y
    lo resuelve con ZCHAFF.
    INPUT:
        - path:      Ubicacion del programa
        - problem:   String que representa la instancia del sudoku en CNF.
    """
    # Cambiamos de directorio al de zchaff
    os.chdir('./'+path)
    # Ejecutamos el programa
    subprocess.run(["./zchaff", problem],capture_output=True)
    os.chdir('../')

def compile_zchaff(path):
    """ 
    Funcion que recibe el directorio donde se encuentra el ZCHAFF y compila
    el programa en cuestion.
    """
    os.chdir('./' + path)
    subprocess.run(["make", "all"],capture_output=True)
    os.chdir('../')

if __name__ == "__main__":
    if len(argv) == 1:
        sudoku = input("Escriba la instancia del sudoku (enter para cancelar): ")
        t = float("0" + input("Indique el tiempo maximo de ejecucion (enter para cancelar): "))
        while sudoku and t:
            # Obtenemos la representacion matricial del sudoku.
            sudoku_matrix = read_sudoku(sudoku)
            # Obtenemos la representacion en SAT del sudoku.
            sat = sudoku_to_SAT(sudoku_matrix)
            time, string_solution, solve_matrix = sudoku_solver(sat, t)
            print(string_solution + "\n")
            sudoku = input("Escriba la instancia del sudoku (enter para cancelar): ")
            t = float("0" + input("Indique el tiempo maximo de ejecucion (enter para cancelar): "))

    elif len(argv) >= 2 and len(argv) <= 4:
        path = "zchaff"
        compile_zchaff(path)
        f = open(argv[1], "r")
        sudokus = f.readlines()
        f.close()
        if len(argv) == 4:
            f = open(argv[2], "w")
            t = float(argv[3])
        elif len(argv) == 3:
            try:
                t = float(argv[2])
                f = open("Soluciones.txt", "w")
            except:
                f = open(argv[2], "w")
                t = 15
        elif len(argv) == 2:
            f = open("Soluciones.txt", "w")
            t = 15
        g = open("Soluciones_Matrices.txt","w")
        instancia = 1
        laura_times = [[],[]]
        laura_fails = [[],[]]
        zchaff_times = [[],[]]
        for s in sudokus:
            # Verificamos que no sean un salto de linea.
            if len(s) > 2:
                # Obtenemos la representacion matricial del sudoku.
                sudoku_matrix = read_sudoku(s[:-1])
                # Obtenemos la representacion en SAT del sudoku.
                sat = sudoku_to_SAT(sudoku_matrix)
                time_laura, to_file, solve_matrix = sudoku_solver(sat, t)
                time_zchaff = timer(zchaff_run, t, path,sat)
                f.write(to_file + "\n")
                print(">>> INSTANCIA ["+ str(instancia)+"]")
                sudoku_instance = ">>> SUDOKU [" + str(instancia)+"]\n" + print_sudoku(sudoku_matrix)
                g.write(sudoku_instance)
                if time_laura != 0:
                    print("\tlaura_SAT time: " + str(time_laura))
                    g.write("Solucion: \n" + print_sudoku(solve_matrix) + "\n")
                    laura_times[0].append(instancia)
                    laura_times[1].append(time_laura)
                else:
                    print("\tlaura_SAT time: " + to_file)
                    g.write("Solucion: " + to_file + "\n")
                    laura_fails[0].append(instancia)
                    laura_fails[1].append(t)
                print("\tZCHAFF time: " + str(time_zchaff))
                zchaff_times[0].append(instancia)
                zchaff_times[1].append(time_zchaff)
                instancia += 1
        # Plotting
        plt.ylabel("Segundos")
        plt.xlabel("Instancias")
        plt.suptitle('ZCHAFF vs LAURA_SAT')
        plt.plot(laura_times[0], laura_times[1], 'bo' ,label='laura_SAT')
        plt.plot(laura_fails[0],laura_fails[1] , 'ro', label='laura_SAT expired' )
        plt.plot(zchaff_times[0], zchaff_times[1], 'go',label='ZCHAFF')
        plt.legend()
        plt.yscale('log')
        plt.show()
        g.close()
        f.close()
    else:
        raise Exception("Numero de argumentos invalidos.")