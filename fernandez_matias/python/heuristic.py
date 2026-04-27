from models import Location, Trip, Vehicle

class Greedy:
    """
    Heurística de Inserción greedy.
    Asigna cada viaje al vehículo que esté más cerca físicamente,
    priorizando minimizar los kilómetros recorridos en vacío (sin pasajeros).
    """
    def __init__(self, trips: list[Trip], vehicles: list[Vehicle]):
        # Ordenamos cronológicamente: los viajes más tempranos se asignan primero.
        # Esto imita la realidad donde damos prioridad a quien debe viajar antes.
        self.trips = sorted(trips, key=lambda t: t.hora_presentacion) # guardamos los viajes ordenados 
        
        # Flota de vehículos disponibles.
        self.vehicles = vehicles # almacenamos los vehpiculos para tenerlo en la clase directamente
        
        # Lista para almacenar los viajes que rompan reglas y no puedan asignarse.
        self.unassigned_trips = [] # en caso de que alguno no sirva, pero Christian dijo que todas las instancias son factibles

    def solve(self):
        # Iteramos uno por uno sobre la lista de viajes (ya ordenada por hora)
        for trip in self.trips: # iteramos sobre cada viaje
            best_vehicle = None  # Almacenará el mejor vehículo encontrado para este viaje
            best_cost = float('inf')  # Costo inicial infinito. de ahí vamos agregando el vehículo más cercano con la menor distancia
            best_insertion = None      # Almacenará los tiempos simulados (recogida y entrega)

            # Evaluamos todos los vehículos para ver cuál es el elegido por la heurística
            for v in self.vehicles:
                
                # Capacidad.
                # Si el viaje tiene más pasajeros de los que el vehículo soporta, lo ignoramos.
                if trip.num_pasajeros > v.capacidad:
                    continue

                # El vehículo viaja vacío a recoger al pasajero.
                # Distancia desde donde está el vehículo hasta el origen del pasajero.
                dist_to_origin = v.current_location.distance_to(trip.origin)
                # Tiempo que tarda en recorrer esa distancia vacío.
                time_to_origin = v.calculate_travel_time(dist_to_origin)
                # Hora a la que el vehículo llega físicamente al origen del viaje.
                arrival_at_origin = v.current_time + time_to_origin
                
                # Ventana de presentación.
                # Si el vehículo llega antes de tiempo, debe esperar. Se sube al pasajero en la hora mayor. 
                # Pensandolo bien, nunca ocurrirá que llegue después por motivos de la heurística
                pickup_time = max(arrival_at_origin, trip.hora_presentacion)
                
                # El traslado del pasajero.
                # La hora a la que termina el viaje es la hora de recogida + lo que tarda el traslado.
                dropoff_time = pickup_time + trip.travel_time_sec
                
                # Retorno a la base.
                # Simulamos que después de este viaje el vehículo vuelve a casa para ver si el tiempo le alcanza.
                dist_to_base = trip.dest.distance_to(v.base_end)
                time_to_base = v.calculate_travel_time(dist_to_base)
                arrival_at_base = dropoff_time + time_to_base
                
                # Fin de jornada.
                # El vehículo solo es válido si logra volver a la base antes o justo a su hora límite de fin_jornada. 
                if arrival_at_base <= v.fin_jornada:
                    
                    # FUNCIÓN DE COSTO:
                    # Queremos el algoritmo lo más simple posible. El "costo" es solo la 
                    # distancia en vacío. Ganará el vehículo que tenga que viajar menos para recogerlo.
                    cost = dist_to_origin
                    
                    # Si este costo es menor que el mejor encontrado hasta ahora, actualizamos al ganador.
                    if cost < best_cost:
                        best_cost = cost
                        best_vehicle = v
                        best_insertion = {
                            'pickup_time': pickup_time,
                            'dropoff_time': dropoff_time,
                            'deadhead': dist_to_origin,
                            'idle_time': pickup_time - arrival_at_origin
                        }

            # Si encontramos un vehículo que cumplió todo y tiene el menor costo:
            if best_vehicle:
                ins = best_insertion
                
                # Actualizamos el estado del vehículo para prepararlo para su siguiente destino:
                best_vehicle.is_used = True                           # Marcamos que el vehículo salió a trabajar
                best_vehicle.deadhead_km += ins['deadhead']           # Acumulamos los kilómetros que recorrió vacío
                best_vehicle.idle_time_sec += ins['idle_time']        # Acumulamos el tiempo ocioso
                best_vehicle.current_location = trip.dest             # Ahora se encuentra estacionado en el destino
                best_vehicle.current_time = ins['dropoff_time']       # El reloj del vehículo avanza hasta el fin del viaje
                
                # Guardamos un resumen para el output final
                best_vehicle.assigned_trips.append({
                    'trip_id': trip.id,
                    'pickup_time': round(ins['pickup_time'], 2),
                    'dropoff_time': round(ins['dropoff_time'], 2)
                })
                
                # Agregamos la parada de recogida al registro de su ruta
                best_vehicle.route.append({"type": "pickup", "trip_id": trip.id, "lat": trip.origin.lat, "lon": trip.origin.lon, "time": round(ins['pickup_time'], 2)})
                
                # Agregamos la parada de entrega al registro de su ruta
                best_vehicle.route.append({"type": "dropoff", "trip_id": trip.id, "lat": trip.dest.lat, "lon": trip.dest.lon, "time": round(ins['dropoff_time'], 2)})
            else:
                # Si ningún vehículo pudo atender este viaje (por falta de capacidad o falta de tiempo en sus jornadas).
                self.unassigned_trips.append(trip.id)
                
        # Retornamos la lista final con los IDs de los viajes que tristemente no pudieron rutease.
        return self.unassigned_trips