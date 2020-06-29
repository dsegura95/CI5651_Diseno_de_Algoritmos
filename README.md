# Resolvedor de Sudoku
Proyecto de CI-5651 "Diseño de Algoritmos I". 

_Implementación de un resolvedor de Sudoku, el cual traduce la instancia de Sudoku a un problema SAT (Boolean SATisfiability Problem) y resuelve dicho problema. Los detalles de los objetivos del programa se encuentran en el archivo [proyecto1.pdf](https://github.com/dsegura95/CI5651_Diseno_de_Algoritmos/blob/master/proyecto1.pdf)_



## Comenzando
Este proyecto es privado, por lo que necesitará permisos para obtener una copia de este. Una vez obtenido los permisos ejecute:

```$ git clone https://github.com/dsegura95/CI5651_Diseno_de_Algoritmos ```

### Pre-requisitos
* Python3
* pip install matplotlib


## Ejecución
Cada módulo del resolvedor de sudoku se pueden usar de manera independiente, asi que explicaremos cada uno de ellos por separado. Los formatos de las instancias de sudoku y los problemas SAT se detallan en [proyecto1.pdf](https://github.com/dsegura95/CI5651_Diseno_de_Algoritmos/blob/master/proyecto1.pdf). 

### sudoku_to_SAT
Dada una instancia de sudoku el programa retorna una representación en SAT de la instancia del sudoku. La sintaxis del programa es

```$ python3 sudoku_to_SAT.py [FILE_IN FILE_OUT]```

Donde ```FILE_IN``` y ```FILE_OUT``` son parámetros opcionales e indican el nombre de un archivo con instancias de sudoku (uno por línea) y otro donde guardar las representaciones de SAT respectivamente. Si hay más de una instancia de sudoku, guardará cada representación en un archivo distinto con nombre ```FILE_OUT``` para la primera instancia y ```FILE_OUT(k-1)``` para la k-ésima instancia (k > 1). En caso de ejecutar el programa sin parámetros, se iniciará una versión interactiva donde se podrá escribir instancias de sudokus y el programa imprimirá su versión en SAT. Para finalizar el programa, basta con dejar vacío el input.

### laura_SAT
Este es el módulo principal del proyecto, el cual, dado un problema SAT, retorna su solución. La sintaxis del programa es

```$ python3 laura_SAT.py [FILE]```

Donde ```FILE``` es un parámetro opcional e indica el nombre de un con archivo con un problema SAT e imprime su resultado. En caso de no indicar ```FILE``` se iniciará una version interactiva donde se podrán escribir problemas SAT y el programa imprimirá sus soluciones. Para finalizar el programa, basta con dejar vacío todos los inputs.

### SAT_to_sudoku
Dado el resultado de un problema SAT que representa una instancia de sudoku, el programa retorna la representación de dicha instancia. La sintaxis del programa es

```$ python3 SAT_to_sudoku.py FILE```

Donde ```FILE``` indica un archivo con la solución al SAT.

### sudoku_solver
Programa principal del proyecto que llama a los módulos anteriores. Dada una instancia de sudoku y un tiempo máximo, el programa lo resuelve y retorna la solución en caso de conseguirla antes del tiempo indicado. La sintaxis del programa es

```$ python3 sudoku_solver.py [FILE_IN FILE_OUT TIME_MAX]```

Donde ```FILE_IN```, ```FILE_OUT``` y ```TIME_MAX``` son parámetros opcionales e indican el nombre de un archivo con instancias de sudoku (uno por línea), otro donde guardar las soluciones y el tiempo máximo para resolver cada sudoku respectivamente. Si hay más de una instancia de sudoku, cada solución se almacenará en una linea de ```FILE_OUT```. En caso de ejecutar el programa sin parámetros, se iniciará una versión interactiva donde se podrán escribir instancias de sudokus y el tiempo maximo, luego el programa imprimirá su solución en caso de haberla conseguida. Para finalizar el programa, basta con dejar vacío alguno de los inputs.

También se puede ejecutar de la siguiente forma:

- ```$ python3 sudoku_solver.py FILE_IN TIME_MAX```
- ```$ python3 sudoku_solver.py FILE_IN FILE_OUT```
- ```$ python3 sudoku_solver.py FILE_IN```

Tomando como valores predeterminados ```TIME_MAX = 15``` y ```FILE_OUT = Soluciones.txt``` en caso de no ser indicados.

## Wiki

### Implementación
Para obtener los detalles de la implementación final, por favor lea el [informe.pdf](https://github.com/dsegura95/CI5651_Diseno_de_Algoritmos/blob/master/informe.pdf)


### Excepciones con ZCHAFF
El programa ZCHAFF no nos compiló bien, pero sin embargo por magia de la computación pudimos realizar las pruebas
corriendo el programa sin problema. Si por alguna razón el programa llegase a tener errores en la ejecución probablemente sea por el ZCHAFF. En tal caso de que hayan problemas, nos lo hacen saber y podemos modificar el programa para quitar el ZCHAFF y al menos puedan ver la corrida de nuestra solución. Las funciones que se encargan
de esto en nuestro programa ```sudoku_solver.py``` son: ```compile_zchaff``` y ```zchaff_run```, donde el primero recibe la ubicacion en el que se encuentra el Makefile del programa y el segundo recibe la ubicacion donde se se encuentra el ejecutable y el problema a resolver, que por defecto la ubicación que nosotros definimos por defecto es ```./zchaff```.

### Autores
* *David Segura*.
* *Amin Arriaga*.
* *Ricardo Monascal*.
