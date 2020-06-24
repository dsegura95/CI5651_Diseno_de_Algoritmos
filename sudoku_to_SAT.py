#  Traductor de instancias de Sudoku a instancias de SAT
#  Autores:
#       - David Segura
#       - Amin Arriaga

from sys import argv

def read_sudoku(string: str) -> [[int]]:
  """ 
  Dado un string con una codificacion de un sudoku, retorna una matriz que
  representa dicho sudoku. 
  INPUT:
    - string:   Instancia del sudoku codificado en un string.
  OUTPUT:
    - [[int]]:  Matriz que representa la instancia del sudoku.
  """
  space = string.index(" ")
  dim = int(string[:space])
  sudoku = [[0 for _ in range(dim**2)] for _ in range(dim**2)]
  i, j = 0, 0
  for x in string[space+1:]:
    # Verificamos que caracter es usando ASCII.
    if 64 < ord(x) < 91: x = ord(x) - 55
    elif x == ".": x = 36
    else: x = int(x)
    if x > dim**2:
      raise Exception("Los numeros del tablero deben estar entre 1 y " + str(dim**2))
    
    # Asignamos el valor numerico del caracter a la casilla correspondiente.
    sudoku[i][j] = x
    i += int((j+1)/dim**2)
    j = (j+1)%dim**2
  return sudoku

def F(i: int, j: int, d: int, N: int) -> int:
  """ 
  Funcion biyectiva que va de los indices de cada literal de la version SAT 
  de la instancia del sudoku a la posicion de dicha variable en el arreglo. 
  INPUT:
    - i:  Fila.
    - j:  Columna.
    - d:  Valor de la casilla (i, j).
    - N:  Grado del trablero de sudoku.
  OUTPUT:
    i*N^4 + j*N^2 + d.
  """
  return i*N**4 + j*N**2 + d

def plus(i: int, j: int, N: int, k: int) -> (int, int):
  """ 
  Dada la posicion de una casilla en el tablero de sudoku, retorna la posicion
  de la siguiente casilla dentro de la misma seccion. 
  INPUT:
    - i:  Fila.
    - j:  Columna.
    - N:  Grado del trablero de sudoku.
    - k:  Seccion.
  OUTPUT:
    - int:  Primera coordenada de la siguiente casilla.
    - int:  Segunda coordenada de la siguiente casilla.
  """
  # Esta dificil explicarlo a_a, pero funciona. Solo gozalo.
  return i+int((j+1)/((k%N+1)*N)), (j+1)%((k%N+1)*N) + (k%N)*N*int((j+1)/((k%N+1)*N))

def sudoku_to_SAT(sudoku: [[int]]) -> str:
  """ 
  Dada una instancia de sudoku representado en una matriz, retorna su representacion
  en SAT. 
  INPUT:
    - sudoku:   Matriz que representa la instancia de sudoku.
  OUTPUT:
    - str:  Representacion en SAT de la instancia de sudoku.
  """
  N = int(len(sudoku)**(1/2))
  commentary = "c \n"
  preamble = "p cnf " + str(N**6) + " "
  C = ""
  num_C = 0

  # CLAUSULAS:
  for i in range(N**2):
    for j in range(N**2):
      # Instancia del Sudoku.
      if sudoku[i][j] != 0:
        C += str(F(i, j, sudoku[i][j], N)) + " 0\n"
        num_C += 1

      # Completitud.
      for d in range(1, N**2+1):
        C += str(F(i, j, d, N)) + " "
      C += "0\n"
      num_C += 1

      # Unicidad.
      for d in range(1, N**2+1):
        for dp in range(d+1, N**2+1):
          C += str(-F(i,j,d,N)) + " " + str(-F(i,j,dp,N)) + " 0\n"
          num_C += 1


  # Validez (filas y columnas).
  for i in range(N**2):
    for j in range(N**2):
      for jp in range(j+1, N**2):
        for d in range(1, N**2+1):
          C += str(-F(i, j, d, N)) + " " + str(-F(i, jp, d, N)) + " 0\n"
          C += str(-F(j, i, d, N)) + " " + str(-F(jp, i, d, N)) + " 0\n"
          num_C += 2

  # Validez (secciones).
  for k in range(N**2):
    i, j = N*int(k/N), N*(k%N)
    ip, jp = i, j+1
    while i != N*(int(k/N) + 1)-1 or j != N*(k%N + 1)-1:
      for d in range(1, N**2+1):
        C += str(-F(i, j, d, N)) + " " + str(-F(ip, jp, d, N)) + " 0\n"
        num_C += 1

      if ip == N*(int(k/N) + 1)-1 and jp == N*(k%N + 1)-1:
        i, j = plus(i, j, N, k)
        ip, jp = i, j
      
      ip, jp = plus(ip, jp, N, k)

  preamble += str(num_C) + "\n"
  return commentary + preamble + C


if __name__ == "__main__":
    if len(argv) == 1:
        sudoku = input("Escriba la instancia del sudoku (enter para cancelar): ")
        while sudoku:
            print(sudoku_to_SAT(read_sudoku(sudoku)))
            sudoku = input("Escriba la instancia del sudoku (enter para cancelar): ")
    elif len(argv) == 3:
        f = open(argv[1], "r")
        sudokus = f.readlines()
        f.close()

        i = 0
        for s in sudokus:
            if len(s) > 2:
                if i == 0: f = open(argv[2], "w")
                else: f = open(argv[2] + "(" + str(i) + ")", "w")
                f.write(sudoku_to_SAT(read_sudoku(s[:-1])))
                i += 1
                f.close()
    else:
        raise Exception("Numero de argumentos invalidos.")
