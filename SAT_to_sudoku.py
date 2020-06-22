#  Traductor de instancias de SAT a instancias de Sudoku.
#  Autores:
#       - David Segura
#       - Amin Arriaga

from sys import argv

def F_inv(n: int, N: int) -> (int, int, int):
  """ 
  Funcion biyectiva que va de la posicion de una variable en el arreglo a
  los indices del literal que representa en la version SAT de la instancia del sudoku. 
  INPUT:
    - n:  Posicion de la variable en el arreglo.
    - N:  Grado del tablero de sudoku.
  OUTPUT:
    - int:  Fila i.
    - int:  Columna j.
    - int:  Valor de la casilla (i, j)."""
  return int(n/N**4), int((n%N**4)/N**2), int(n%N**2)+1

def SAT_to_sudoku(V: [int]) -> (str, [[int]]):
  """
  Traduce el conjunto de variables a una instancia resuelta de sudoku.
  INPUT:
    - V:  Variables
  OUTPUT: 
    - str:  Representacion de string de la instancia resuelta del sudoku.
    - [[int]]:    Representacion matricial de la instancia resuelta del sudoku.
  """
  N = int(len(V)**(1/6))
  result = str(N) + " "

  # Traducimos las variables a una matriz.
  sudoku = [[0 for _ in range(N**2)] for _ in range(N**2)]
  for i in range(len(V)):
    if V[i] == 1:
      i, j, d = F_inv(i, N)
      sudoku[i][j] = d

  # Traducimos la matriz a un string
  for row in sudoku:
    for column in row:
      result += str(column)   

  return result, sudoku


if __name__ == "__main__":
    if len(argv) == 2:
        file_vars = argv[1]
        f = open(file_vars, "r")
        V = f.readlines()
        f.close()

        sol, sudoku = SAT_to_sudoku(V)
        print("Solucion: ")
        for s in sudoku:
            print(s)
    else:
        raise Exception("Numero de argumentos invalidos.")