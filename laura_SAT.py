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
      self.satisfied:    Variable booleana que indica si una clausula ya fue satisfecha.
      self.backup:       Diccionario que utilizaremos como nube para guardar la informacion actual.
    """
    self.literales = []
    self.N = 0
    self.satisfied = False
    self.backup = {}

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
    self.backup[key] = (self.literales.copy(), self.N, self.satisfied)

  def restaure(self, key: int):
    """
    Metodo que restaurara una copia guardada mediante la llave indicada.
    INPUT:
      - key: llave donde se encuentra la copia de la clausula
      - pop: variable que indica si se requiere eliminar la copia o no, por
             defecto es False.
    """
    self.literales, self.N, self.satisfied = self.backup.pop(key)

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
                         el signo que tiene dentro de ella.
      self.backup:       Diccionario que utilizaremos para guardar el signo actual
                         de la variable.
    """
    self.sign = 0
    self.closures = []
    self.backup = {}
  
  def assign(self, sign: int) -> bool:
    """
    Metodo que asigna el signo a la variable.
    INPUT:
      - sign: Signo de la variable.
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
      - closure:  Clausura a la que pertenece la variable.
    """
    self.closures.append(closure)
  
  def save(self, key: int):
    """
    Metodo que guarda una copia del signo.
    INPUT:
      - key: Llave donde se guardara la copia del signo.
    """
    self.backup[key] = self.sign

  def restaure(self, key: int):
    """
    Metodo que restablecera una copia guardada mediante la llave indicada.
    INPUT:
      - key: llave donde se encuentra la copia del signo
    """
    self.sign = self.backup.pop(key)

class CNF:
  """
  Clase que contendra todas las clausulas del problema CNF.
  """
  def __init__(self, closures):
    """
    Se inicializan los siguientes parametros:
      self.closures:     Clausulas en el problema
      self.N:     Numero de clausulas sin satisfacer.
      self.backup:       Diccionario que utilizaremos para guardar el numero de clausulas actual.
    """
    self.closures = closures
    self.N = sum(sum(1 for c_p in c) for c in closures)
    self.backup = {}

  def save(self, key: int):
    """
    Metodo que guarda una copia del numero de clausulas actual.
    INPUT:
      - key:  Llave donde se guardara la copia de N.
    """
    self.backup[key] = self.N

  def restaure(self, key: int):
    """
    Metodo que restablecera una copia guardada mediante la llave indicada.
    INPUT:
      - key: Llave donde se encuentra la copia de N.
    """
    self.N = self.backup.pop(key)


def read_SAT(text: str) -> ([Variable], CNF):
  """
  Dado un string con un problema SAT en forma cnf, retorna el arreglo con las
  variables y otro arreglo con las clausuras.
  INPUT:
    - text:   String con el problema SAT.
  OUTPUT:
    - [Variable]:  Variables inicializadas en 0. No confundir con False, que a efectos
                  practicos lo consideramos como -1 y True como 1.
    - CNF:   Instancia de la clase CNF con las clausulas del problema.
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

  return V, CNF(C) 

def update_C(V: [Variable], C: CNF, k: int) -> bool:
  """ 
  Actualiza las clausuras de C dada la (k-1)-esima variable de V. Si aparece
  un literal de la variable con valor False, se elimina dicho literal, en caso
  contrario se elimina toda la clausula. En caso de quedar alguna clausura vacia,
  significa que dio False (conflicto).
  INPUT:
    - V:  Variables.
    - C:  Clausulas.
    - k:  Variable.
  OUTPUT:
    - bool: Indica si hubo algun conflicto (clausura vacia).
  """
  # Obtenemos todas las clausulas en las que aparece la variable.
  c = V[k-1].closures
  for i in range(len(c)):
    if c[i].satisfied: continue

    pos = c[i].N - 1
    index = C.closures[pos].index(c[i])

    # Verificamos los literales de la clausula.
    delete = []
    satisfied = False
    for p, l in enumerate(c[i].literales):
      # Si el literal aparece con valor True, la clausula queda satisfecha.
      if k*V[k-1].sign == l:
        c[i].satisfied = True
        C.closures[pos].pop(index)
        C.N -= 1
        satisfied = True
        break

      # Si el literal aparece con valor False, se elimina de la clausula.
      elif l == -k*V[k-1].sign:
        delete.append(p)

    # Eliminamos los literales falsos de la clausula.
    if delete and not satisfied:
      if c[i].delete(delete): return True
      C.closures[pos].pop(index)
      C.closures[c[i].N - 1].append(c[i])
  # No hubo conflicto.
  return False

def verify_units(V: [Variable], C: CNF) -> bool:
  """ 
  Verifica si hay clausuras unitarias y actualizas las variables en
  consecuencia.
  INPUT:
    - V:  Variables.
    - C:  Clausulas.
  OUPUT:
    - bool: Indica si hubo algun conflicto (variable que deba tener el valor
            True y False, o alguna clausura vacia).
  """
  # Mientras hayan clausulas unitarias.
  while len(C.closures[0]) > 0:
    # Obtenemos una clausula unitaria y hacemos True su literal.
    c = C.closures[0].pop()
    C.N -= 1
    c.satisfied = True

    k = abs(c.literales[0])
    sign = int(abs(c.literales[0])/c.literales[0])
    # Verificamos que no haya conflicto al asignar un valor a la variable o
    # al actualizar las demas clausulas en consecuencia.
    if V[k-1].assign(sign) or update_C(V, C, k): return True
  return False

def search_amin_zero(V: [Variable]) -> (int):
  """ 
  Dado un arreglo de enteros, retornara la primera posicion donde
  haya un cero.
  INPUT:
    - V:  Arreglo con las variables.
  OUTPUT:
    - int:  Menor indice tal que se encuentre una variable con valor 0.
  """
  for i in range(len(V)):
    if V[i].sign == 0:
      return i
  return -1

def restaure(V: [Variable], C: CNF, key: int):
  """
    Funcion que restablece los valores guardados en el 'backup' tanto de las  
    clausulas como del signo de las variables.
    INPUT:
      - V:   signos de variables a restablecer
      - C:   clausulas a restablecer
      - key: llave donde se encuentran guardados los datos a restablecer.
    """
  C.restaure(key)
  for c in C.closures:
    for c_p in c:
      c_p.restaure(key)
  for v in V: v.restaure(key)

def laura_SAT(V: [Variable], C: CNF) -> ([int], bool):
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
  # Propagacion unitaria.
  if verify_units(V, C):
    return [0 for _ in range(len(V))], True

  # Si no quedan clausulas, terminamos.
  if C.N == 0:
    sol = []
    for v in V:
      if v.sign != 0: sol.append(v.sign)
      else: sol.append(-1)
    return sol, False

  # Obtenemos una llave.
  key = 0
  while key in V[0].backup: key += 1

  # Hacemos un backup del estado actual.
  C.save(key)
  for c in C.closures:
    for c_p in c: c_p.save(key)
  C_save = [c.copy() for c in C.closures]
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
        return [0 for _ in range(len(V))], True

      # Si dio conflicto con el positivo, restauramos lo valores de las
      # clausulas y las variables y pasamos al negativo.
      C.closures = [c.copy() for c in C_save]
      restaure(V, C, key)
      continue

    # Si no hubo conflictos y no hay mas clausuras, retornamos las variables.
    if C.N == 0:
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
      # Restauramos los valores de las clausulas y las variables.
      C.closures = [c.copy() for c in C_save]
      restaure(V, C, key)

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
