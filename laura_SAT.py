#  Resolvedor propio de SAT
#  Autores:
#       - David Segura
#       - Amin Arriaga

from sys import argv

class Variable:
  """
  Clase que representara la estructura de datos de las variables, donde almacenaremos
  las clausuras a las que pertenece la variable y su signo
  INIT:
    - sign:   signo de la variable que comienza sin asignar
    - closures: arreglo con las clausulas a la que pertenece la variable y el signo
                que tiene dentro de ella
  """
  def __init__(self):
    self.sign = None
    self.closures = []
  
  def assign(self, sign):
    """
    Metodo que asigna el signo a la variable
    INPUT:
      - sign: signo de la variable
    """
    self.sign = sign
  
  def get_assign(self):
    """
    Metodo que retorna el signo de la variable
    OUTPUT:
      - sign: signo de la variable
    """
    return self.sign
  
  def add_closure(self, closure, sign):
    """
    Metodo que agrega una clausura a la que pertenece la variable y el signo
    que tiene
    INPUT:
      - closure:  clausura a la que pertenece la variable
      - sign:     signo/s de la variable
    """
    self.closures.append((closure, sign))
  
  def get_closures(self):
    """
    Metodo que obtiene las clausuras a la que pertenece la variable
    OUTPUT:
      - closures:   clasuras a las que pertenece la variable
    """
    return self.closures
  
  def copy(self):
    """
    Metodo que obtiene la copia de la clase
    OUTPUT:
      - v:   copia de la clausula
    """
    v = Variable()
    v.assign(self.sign)
    for x in self.closures:
      v.add_closure(x[0].copy(), x[1].copy())
    return v

class Clousule:
  def __init__(self):
    self.literales = []
    self. flags = []
    self.N = 0

  def add(self, var, flag):
    self.literales.append(var)
    self.flags.append(flag)
    self.N += 1

  def delete(self, i):
    self.literales.pop(i)
    self.flags.pop(i)
    self.N -= 1

  def copy(self):
    C = Clousule
    C.literales = self.literales.copy()
    C.flags = self.flags.copy()
    C.N = self.N
    return C

def read_SAT(text: str) -> ([int], [[int]]):
  """
  Dado un string con un problema SAT en forma cnf, retorna el arreglo con las
  variables y otro arreglo con las clausuras.
  INPUT:
    - text:   String con el problema SAT.
  OUTPUT:
    - [int]:  Variables inicializadas en 0. No confundir con False, que a efectos
              practicos lo consideramos como -1 y True como 1.
    - [[int]]:  Arreglo de clausuras en forma cnf. Cada arreglo dentro del 
                arreglo es una clausura disjuntiva.
  """

  metadata = ""
  while metadata != "p":
    metadata = text[0]

    if metadata == "c":
      # Ignoramos la linea de comentario.
      if text.find("\n") == -1: break
      text = text[text.find("\n")+1:]

    elif metadata == "p":
      # Verificamos el formato
      formato = text[2:5]
      if formato != "cnf":
        raise Exception("El formato del problema SAT debe ser cnf.")

      # Obtenemos el numero de variables.
      text = text[6:] 
      N = int(text[: text.find(" ")])
      V = [Variable() for _ in range(N)]

      # Obtenemos el numero de clausuras.
      text = text[text.find(" ")+1:]
      num_C = int(text[: text.find("\n")])
      if num_C == 0:
        raise Exception("Debe haber por lo menos una clausura.")

      # Obtenemos las clausuras.
      C_aux = [Clousule() for _ in range(num_C)]
      C = [[]]
      text = text[text.find("\n")+1:]
      nums = [int(t) for t in text.split()]
      # Si el ultimo numero es un 0, lo quitamos.
      if nums[len(nums)-1] == 0: nums.pop()
      i = 0
      for n in nums:
        last = n
        if n == 0:
          for k in range(0, C_aux[i].N - len(C)):
            C.append([])
          C[C_aux[i].N - 1].append(C_aux[i])
          i += 1
        elif abs(n) > N: 
          raise Exception("Se indicaron", N, "variables, pero aparece la variable",
                          n, "en la " + str(i) + "-esima clausura.")
        else: 
          sign = int(abs(n)/n)
          C_aux[i].add(abs(n), sign)
          V[abs(n)].add_closure(C_aux[i], sign)
      if last != 0:
        C[C_aux[i].N - 1].append(C_aux[i])
      if i+1 != num_C:
        raise Exception("El numero de clausuras indicadas no coincide con las dadas.")

    else:
      raise Exception("Formato no valido, el metadato debe ser 'c' para comentarios y " + \
                      "'p' para el encabezado.")
  return V, C 

def update_C(V: [int], C: [[int]], k: int) -> bool:
  """ 
  Actualiza las clausuras de C dada la (k-1)-esima variable de V. Si aparece
  un literal de la variable con valor False, se elimina dicho literal, en caso
  contrario se elimina toda la clausula. En caso de quedar alguna clausura vacia,
  significa que dio False (conflict).
  INPUT:
    - V:  Variables.
    - C:  Clausuras.
    - k:  Variable.
  OUTPUT:
    - bool: Indica si hubo algun conflicto (clausura vacia).
  """
  j = 0
  for i in range(len(C)):
    p = i-j
    # Si el literal se encuentra con valor True, eliminamos la clausura.
    if V[k-1]*k in C[p]:
      C.pop(p)
      j += 1
    # Si el literal se encuentra con valor False, se elimina el literal.
    elif -V[k-1]*k in C[p]:
      C[p].pop(C[p].index(-V[k-1]*k))
      # Si la clausura queda vacia, conflicto.
      if not C[p]:
        return True
  return False

def verify_units(V: [int], C: [[int]]) -> bool:
  """ 
  Verifica si hay clausuras unitarias y actualizas las variables en
  consecuencia.
  INPUT:
    - V:  Variables.
    - C:  Clausuras.
  OUPUT:
    - bool: Indica si hubo algun conflicto (variable que deba tener el valor
            True y False, o alguna clausura vacia).
  """
  # Indica si hubo clausuras unitarias.
  units = True
  while units:
    units = False
    # Almacenamos los indices de las clausuras unitarias.
    v_units = []
    for i in range(len(C)):
      if len(C[i]) == 1:
        # Si el valor de la variable de la clausura unitaria es el negado del
        # valor que le ibamos a signar, conflicto.
        if V[abs(C[i][0])-1] == int(-C[i][0]/abs(C[i][0])):
          return True
        v_units.append(abs(C[i][0]))
        V[abs(C[i][0])-1] = int(C[i][0]/abs(C[i][0]))
        units = True
    
    for k in v_units:
      # Si update_C da conflicto, conflicto.
      if update_C(V, C, k):
        return True
  return False

def search_amin_zero(V: [int]) -> (int):
  """ 
  Dado un arreglo de enteros, retornara la primera posicion donde
  haya un cero.
  INPUT:
    - V:  Arreglo
  OUTPUT:
    - int:  Indice tal que en esa posicion se encuentre un 0. Retorna
            -1 si no hay ningun 0 en el arreglo.
  """
  for i in range(len(V)):
    if V[i].sign == 0:
      return i
  return -1

def laura_SAT(V: [int], C: [[int]]) -> ([int], bool):
  """ 
  SAT-Solver
  INPUT:
    - V:  Variables.
    - C:  Clausuras.
  OUTPUT:
    - [int]:  Valores de las variables en caso de haber solucion, [] en caso
              contrario
    - bool:   Indica si hubo conflictos.
  """
  if verify_units(V, C):
    return [0 for _ in range(len(V))], True

  for i in range(2):
    signo = 1-2*i
    # Hacemos una copia para no modificar los originales.
    V_aux = [v.copy() for v in V]
    C_aux = [[clousule.copy() for clousule in c] for c in C]
    # Verificamos cual es la siguiente variable a la que no se le ha
    # asignado un valor.
    k = search_amin_zero(V_aux) + 1
    # Asignamos primero -1 luego 1 a la (k-1)-esima variable.
    V_aux[k-1].sign = signo
    # Actualizamos las clausuras debido a la nueva asignacion.
    if update_C(V_aux, C_aux, k):
      # Si dio conflicto con el negativo, no hay solucion en esta rama.
      if signo < 0:
        return [0 for _ in range(len(V))], True
      # Si dio conflicto con el positivo, pasamos al negativo
      continue

    # Si no hubo conflictos y no hay mas clausuras, retornamos las variables.
    if len(C_aux) == 0:
      sol = []
      for v in V_aux:
        if v.sign != 0: sol.append(v.sign)
        else: sol.append(-1)
      return sol, False

    # Si hay mas clausuras, verificamos si hay alguna solucion en futuras ramas
    sol, conflict = laura_SAT(V_aux, C_aux)
    # Si una de las ramas logro retornar el resultado, retornamos dicho resultado
    if not conflict:
      return sol, False

  # Si no hubo un resultado en futuras ramas, conflicto.
  return [0 for _ in range(len(V))], True

def output(V: [int], result: int) -> str:
  """
  Retorna en un string el resultado del SAT-Solver.
  INPUT:
    - result:   Conclusion del SAT-Solver.
    - V:    Variables.
  OUTPUT:
    - str:   Resultado del SAT-Solver
  """
  text = "s cnf " + str(result) + " " + str(len(V))
  if result == 1:
    for i, v in enumerate(V):
      text += "\nv " + str(int(v*(i+1)))
  return text


if __name__ == "__main__":
    if len(argv) == 1:
        def input_sat():
            sat = "p cnf "
            sat += input("Escriba el numero de variables: ") + " "
            sat += input("Escriba el numero de clausuras: ") + "\n"
            sat += input("Escriba las clausuras: ")
            return sat

        sat = input_sat()
        while sat != "p cnf  \n":
          V, C = read_SAT(sat)
          V_result, conflict = laura_SAT(V, C)
          print("\n" + output(V_result, int(not conflict)) + "\n")
          sat = input_sat()

    elif len(argv) == 2:
        file_sats = argv[1]
        f = open(file_sats, "r")
        sat = f.read()
        f.close()

        V, C = read_SAT(sat)
        V_result, conflict = laura_SAT(V, C)
        print("\n" + output(V_result, int(not conflict)) + "\n")
    else:
        raise Exception("Numero de argumentos invalidos.")
