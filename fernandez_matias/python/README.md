# Prueba Matías Fernández

Implementación de heurística simple que elige los vehículos más cercanos factibles para cada trip. Para problema de recoger pasajeros en The Optimal

## Lógica de la Heurística

El algoritmo busca asignar iterativamente un conjunto de viajes a una flota de vehículos minimizando principalmente los kilómetros recorridos a buscar pasajeros y cumpliendo estrictamente con todas las restricciones del problema, en caso de que no se pueda, simplemente dejo a los trips sin asignar y los reporto en los outputs

### Pasos del algoritmo:

1. **Ordenamiento Inicial:** 
   Se ordenan todos los viajes cronológicamente de forma ascendente según su `hora_presentacion`. Esto prioriza la atención de los pasajeros que deben viajar más temprano.

2. **Evaluación de Inserción (Greedy):**
   Iteramos viaje por viaje. Para cada viaje, evaluamos todos los vehículos disponibles y simulamos su inserción al final de la ruta actual del vehículo. Durante la simulación verificamos:
   - **Capacidad:** Que el número de pasajeros no exceda la capacidad máxima del vehículo.
   - **Tiempos y distancias:** Calculamos el tiempo de viaje desde la ubicación actual del vehículo hasta el origen del viaje utilizando la Fórmula de Haversine y asumiendo una velocidad constante de 20 km/h.
   - **Ventanas de tiempo (Espera):** Si el vehículo llega al origen antes de la `hora_presentacion`, debe esperar. El tiempo de "pickup" real es el máximo entre la hora de llegada del vehículo y la hora de presentación exigida.
   - **Fin de Jornada:** Simulamos el traslado completo (desde el origen hasta el destino del viaje) y el retorno a la base final del vehículo (`fin_jornada`). Si el tiempo calculado de retorno a la base excede la hora de término de la jornada del vehículo, la inserción se rechaza.

3. **Función de Costo:**
   Para los vehículos factibles, se calcula un "costo" de asignación:
   `Costo = Distancia' Se prioriza estrictamente la minimización de kilómetros muertos para asignar el viaje al vehículo más cercano en términos de distancia.*

4. **Asignación y Actualización:**
   El viaje se asigna al vehículo con el **menor costo factible**. Acto seguido, se actualiza el estado del vehículo (nueva ubicación actual, tiempo actual, acumulación de kilómetros muertos) y se registran los nodos de `pickup` y `dropoff` en su ruta. Los viajes que no logran cumplir las restricciones con ningún vehículo se marcan como `unassigned`.

## Estructura del Proyecto

El código está desarrollado aplicando Programación Orientada a Objetos (POO) y su estructura principal consta de los siguientes archivos y directorios:

- `models.py`: Define las entidades del dominio.
  - Función `haversine` para cálculo de distancias.
  - Clase `Location` para representar coordenadas.
  - Clase `Trip` para los viajes y sus cálculos de tiempo de traslado.
  - Clase `Vehicle` que mantiene el estado actual (ubicación, tiempo, capacidad, ruta trazada).

- `heuristic.py`: Contiene la clase `GreedyInsertionHeuristic`, responsable de ejecutar la lógica principal detallada anteriormente.

- `solve.py`: Es el script principal. Lee la instancia JSON, construye los objetos, llama al solver, formatea el JSON de salida y agrega un registro al archivo `metrics.csv`.

- `validator.py`: Script secundario para auditar una solución generada. Verifica la congruencia de los tiempos de viaje (distancias a 20 km/h), que las capacidades no sean superadas, y que se respete el fin de jornada y las horas de presentación.

- `metrics.csv`: Archivo generado automáticamente donde se van acumulando los KPIs de cada ejecución de `solve.py`.
- Directorio `outputs/`: Carpeta generada automáticamente donde se guardan todas las soluciones JSON (para mantener el repositorio ordenado).


## Instrucciones de Uso

### 1. Generar una solución
Ejecutar `solve.py` proporcionando el archivo de entrada, el nombre del archivo de salida deseado, y el archivo de métricas.

Usaré de ejemplo la small, pero simplemente después hay que cambiar el nombre de la instancia por la que se desea revisar

```bash
python solve.py --input instancias/small.json --output small_solution.json --metrics metrics.csv
```
*Este comando procesará la instancia, creará/actualizará el archivo `metrics.csv` añadiendo una fila con los KPIs de la solución, y guardará la estructura del ruteo en `outputs`.*

### 2. Validar una solución
Para correr el auditor de reglas de negocio sobre el JSON generado:
Usaré de ejemplo la small, pero simplemente después hay que cambiar el nombre de la instancia por la que se desea revisar

```bash
python validator.py --instance instancias/small.json --solution small_solution.json
```

## Métricas Registradas (`metrics.csv`)
El archivo CSV generado contiene las siguientes columnas:
- `instance_name`: Nombre del archivo procesado.
- `total_trips`: Total de viajes en la instancia.
- `assigned_trips`: Cantidad de viajes exitosamente ruteados.
- `unassigned_trips`: Viajes rechazados por violar las restricciones (capacidad, tiempo o fin de turno).
- `vehicles_used`: Cantidad de vehículos de la flota utilizados.
- `total_deadhead_km`: Sumatoria de todos los kilómetros recorridos por la flota en reposicionamientos sin pasajeros a bordo.
- `total_idle_time_sec`: Tiempo ocioso total (en segundos) que los vehículos pasaron esperando entre el fin de un reposicionamiento y el inicio de un viaje.
