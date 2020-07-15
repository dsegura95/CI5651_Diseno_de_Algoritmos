#  Resolvedor propio de SAT
#  Autores:
#       - David Segura
#       - Amin Arriaga

from sys import argv

class Closure:
  """
  Clase que representara la estructura de datos de las clausuras, donde almacenaremos
  las variables que contiene junto a sus flags y el numero de literales.
  """
  def __init__(self):
    """
    Se inicializan los siguientes parametros:
      self.literales:    Conjunto de literales que aparecen en la clausura.
      self.N:            Numero de literales de la clausura.
      self.satisfied:    Variable booleana que indica si una clausula ya fue satisfecha
      self.cloud:        Diccionario que utilizaremos como nube para guardar la instancia
    """
    self.literales = []
    self.N = 0
    self.satisfied = False
    self.cloud = {}

  def add(self, var: int):
    """
    Agrega un literal a la clausura.
    INPUT:
      - var:  Entero que representa a la variable que aparece en el literal.
    """
    self.literales.append(var)
    self.N += 1

  def delete(self, indexes: [int]) -> bool:
    """
    Elimina el i-esimo literal de la clausura.
    INPUT:  
      i:  Indice del literal.
    OUTPUT:
      bool:  Indica si la clausula quedo vacia.
    """
    p = 0
    for i in indexes:
      self.literales.pop(i-p)
      p += 1
    self.N -= len(indexes)
    return self.N == 0

  def save(self, key: int):
    """
    Metodo que guarda una copia de la instancia.
    INPUT:
      - key: llave donde se guardara la copia de la clausula
    """
    self.cloud[key] = (self.literales.copy(), self.N, self.satisfied)

  def restaure(self, key: int,  pop=False):
    """
    Metodo que restaurara una copia guardada mediante la llave indicada.
    INPUT:
      - key: llave donde se encuentra la copia de la clausula
      - pop: variable que indica si se requiere eliminar la copia o no, por
             defecto es False.
    """
    self.literales, self.N, self.satisfied = self.cloud[key]
    if pop: self.cloud.pop(key)

class Variable:
  """
  Clase que representara la estructura de datos de las variables, donde almacenaremos
  las clausuras a las que pertenece la variable y su signo.
  """
  def __init__(self):
    """
    Se inicializan los siguientes parametros:
      self.sign:         Signo de la variable que comienza sin asignar
      self.closures:     Arreglo con las clausulas a la que pertenece la variable y 
                         el signo que tiene dentro de ella
      self.cloud:        Diccionario que utilizaremos como nube para guardar el signo
                         de la variable
    """
    self.sign = 0
    self.closures = []
    self.cloud = {}
  
  def assign(self, sign: int) -> bool:
    """
    Metodo que asigna el signo a la variable.
    INPUT:
      - sign: signo de la variable.
    OUTPUT:
      - bool: Indica si hubo un conflicto.
    """
    if self.sign == -sign: return True
    self.sign = sign
    return False
  
  def add_closure(self, closure: Closure):
    """
    Metodo que agrega una clausura a la que pertenece la variable.
    INPUT:
      - closure:  clausura a la que pertenece la variable.
    """
    self.closures.append(closure)
  
  def save(self, key: int):
    """
    Metodo que guarda una copia del signo
    INPUT:
      - key: llave donde se guardara la copia del signo
    """
    self.cloud[key] = self.sign

  def restaure(self, key: int, pop=False):
    """
    Metodo que restablecera una copia guardada mediante la llave indicada.
    INPUT:
      - key: llave donde se encuentra la copia del signo
      - pop: variable que indica si se requiere eliminar la copia o no, por
             defecto es False.
    """
    self.sign = self.cloud[key]
    if pop: self.cloud.pop(key)


def read_SAT(text: str) -> ([Variable], [[Closure]]):
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
      C_aux = [Closure() for _ in range(num_C)]
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
          C_aux[i].add(n)
          V[abs(n)-1].add_closure(C_aux[i])
      if last != 0:
        C[C_aux[i].N - 1].append(C_aux[i])
      if i+1 != num_C:
        raise Exception("El numero de clausuras indicadas no coincide con las dadas.")

    else:
      raise Exception("Formato no valido, el metadato debe ser 'c' para comentarios y " + \
                      "'p' para el encabezado.")

  return V, C 

def update_C(V: [Variable], C: [[Closure]], k: int) -> bool:
  """ 
  Actualiza las clausuras de C dada la (k-1)-esima variable de V. Si aparece
  un literal de la variable con valor False, se elimina dicho literal, en caso
  contrario se elimina toda la clausula. En caso de quedar alguna clausura vacia,
  significa que dio False (conflake).
  INPUT:
    - V:  Variables.
    - C:  Clausuras.
    - k:  Variable.
  OUTPUT:
    - bool: Indica si hubo algun conflicto (clausura vacia).
  """
  c = V[k-1].closures
  for i in range(len(c)):
    if c[i].satisfied: continue

    pos = c[i].N - 1
    index = C[pos].index(c[i])

    delete = []
    satisfied = False
    for p, l in enumerate(c[i].literales):
      if k*V[k-1].sign == l:
        c[i].satisfied = True
        C[pos].pop(index)
        satisfied = True
        break

      elif l == -k*V[k-1].sign:
        delete.append(p)

    if delete and not satisfied:
      if c[i].delete(delete): return True
      C[pos].pop(index)
      C[c[i].N - 1].append(c[i])
  
  return False

def restaure(V: [Variable], C: [[Closure]], key: int, pop=False):
  """
    Funcion que restablece los valores guardados en la 'nube' tanto de las  
    clausulas como del signo de las variables
    INPUT:
      - V:   signos de variables a restablecer
      - C:   clausulas a restablecer
      - key: llave donde se encuentran guardados los datos a restablecer
      - pop: variable que indica si se requiere eliminar la copia o no, por
             defecto es False.
    """
  for c in C:
    for c_p in c:
      c_p.restaure(key, pop)
  for v in V: v.restaure(key, pop)

def verify_units(V: [Variable], C: [[Closure]]) -> bool:
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
  while len(C[0]) > 0:
    c = C[0].pop()
    c.satisfied = True
    k = abs(c.literales[0])
    sign = int(abs(c.literales[0])/c.literales[0])
    if V[k-1].assign(sign) or update_C(V, C, k): return True
  return False

def search_amin_zero(V: [Variable]) -> (int):
  """ 
  Dado un arreglo de enteros, retornara la primera posicion donde
  haya un cero.
  INPUT:
    - V:  Arreglo
  OUTPUT:
    - int:  Indice tal que en esa posicion se encuentre un 0.
  """
  for i in range(len(V)):
    if V[i].sign == 0:
      return i
  raise Exception("Todas las variables ya fueron asignadas.")

def laura_SAT(V: [Variable], C: [[Closure]]) -> ([int], bool):
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

  if all(len(c) == 0 for c in C):
    sol = []
    for v in V:
      if v.sign != 0: sol.append(v.sign)
      else: sol.append(-1)
    return sol, False

  key = 0
  while key in V[0].cloud: key += 1

  for c in C:
    for c_p in c: c_p.save(key)
  C_save = [c.copy() for c in C]
  for v in V: v.save(key)

  for i in range(2):
    sign = 1-2*i
    # Hacemos una copia para no modificar los originales.
    # Verificamos cual es la siguiente variable a la que no se le ha
    # asignado un valor.
    k = search_amin_zero(V) + 1
    # Asignamos primero -1 luego 1 a la (k-1)-esima variable.
    V[k-1].sign = sign
    # Actualizamos las clausuras debido a la nueva asignacion.
    if update_C(V, C, k):
      
      # Si dio conflicto con el negativo, no hay solucion en esta rama.
      if sign < 0:
        #restaure(V, C, key, True)
        return [0 for _ in range(len(V))], True

      # Si dio conflicto con el positivo, pasamos al negativo
      C = [c.copy() for c in C_save]
      restaure(V, C, key)
      continue

    # Si no hubo conflictos y no hay mas clausuras, retornamos las variables.
    if all(len(c) == 0 for c in C):
      sol = []
      for v in V:
        if v.sign != 0: sol.append(v.sign)
        else: sol.append(-1)
      return sol, False

    # Si hay mas clausuras, verificamos si hay alguna solucion en futuras ramas
    sol, conflake = laura_SAT(V, C)
    # Si una de las ramas logro retornar el resultado, retornamos dicho resultado
    if not conflake:
      return sol, False

    if sign > 0:
      C = [c.copy() for c in C_save]
      restaure(V, C, key)
    #else: restaure(V, C, key, True) #del_key


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
          V_result, conflake = laura_SAT(V, C)
          print("\n" + output(V_result, int(not conflake)) + "\n")
          sat = input_sat()

    elif len(argv) == 2:
        file_sats = argv[1]
        f = open(file_sats, "r")
        sat = f.read()
        f.close()

        V, C = read_SAT(sat)
        V_result, conflake = laura_SAT(V, C)
        print("\n" + output(V_result, int(not conflake)) + "\n")
    else:
        raise Exception("Numero de argumentos invalidos.")
