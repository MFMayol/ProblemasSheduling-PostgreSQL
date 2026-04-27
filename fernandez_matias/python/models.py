import math

def haversine(lat1, lon1, lat2, lon2):
    """
    Calcula la distancia en kilómetros entre dos coordenadas. Encontré el código en stackoverflow: https://stackoverflow.com/questions/4913349/haversine-formula-in-python-bearing-and-distance-between-two-gps-points
    """
    
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

class Location:
    """
        Clase que tiene la data relevante del viaje que representa una localización en latitud y longitud. tiene el método para calcular la distancia de este hacia cualquier sitio'
    """
    def __init__(self, lat, lon):
        self.lat = lat # latitud
        self.lon = lon # longitud

    def distance_to(self, other):
        return haversine(self.lat, self.lon, other.lat, other.lon)

class Trip:
    """
    Clase que tiene la data relevante del viaje'
    """
    def __init__(self, id, origin_dict, dest_dict, presentacion, pax):
        self.id = id # el id del viaje
        self.origin = Location(origin_dict['lat'], origin_dict['lon']) # objeto origen del viaje
        self.dest = Location(dest_dict['lat'], dest_dict['lon']) # objeto destino del viaje
        self.hora_presentacion = presentacion # float donde tengo al hora de presentación
        self.num_pasajeros = pax # donde agrego el numero de pasajeros por viaje
        
        self.distance_km = self.origin.distance_to(self.dest) # la distancia entre el origen y el destino del viaje que se hará
        self.travel_time_sec = (self.distance_km / 20.0) * 3600.0 # tomamos la velocidad en segundos

class Vehicle:
    """
    Clase que representa un vehículo de la flota.
    Almacena tanto su configuración inicial (capacidad, horarios de su jornada, ubicación de su base)
    como su estado actual en vivo durante la simulación (dónde está ahora mismo, qué hora marca su reloj y su ruta).
    """
    def __init__(self, id, cap, start_dict, end_dict):
        self.id = id # Identificador único del vehículo (ej. "VEH001")
        self.capacidad = cap # Número máximo de pasajeros que puede llevar al mismo tiempo
        self.base_start = Location(start_dict['lat'], start_dict['lon']) # Ubicación donde inicia su jornada
        self.base_end = Location(end_dict['lat'], end_dict['lon']) # Ubicación a la que debe regresar al terminar
        self.inicio_jornada = start_dict['hora'] # Hora (en segundos) a la que empieza a trabajar
        self.fin_jornada = end_dict['hora'] # Hora límite (en segundos) para estar de vuelta en su base final
        
        # Inicializamos el estado del vehículo preparándolo para empezar a rutear
        self.reset()

    def reset(self): 
        """
        Reinicia el estado del vehículo al comienzo de su jornada.
        Se usa para preparar el vehículo antes de empezar a asignarle viajes.
        """
        self.current_location = self.base_start # Físicamente arranca estacionado en su base de inicio
        self.current_time = self.inicio_jornada # Su reloj interno arranca en la hora de inicio de jornada
        self.route = [] # Aquí iremos guardando el historial cronológico de paradas que hace
        self.assigned_trips = [] # Lista con el resumen de los viajes que se le han asignado exitosamente
        self.deadhead_km = 0.0 # Acumulador de kilómetros recorridos sin pasajeros (en vacío)
        self.idle_time_sec = 0.0 # Acumulador de tiempo ocioso esperando en los orígenes
        self.is_used = False # Bandera para saber si el vehículo salió a trabajar o se quedó en la base todo el día
        
        # Registramos su primera acción en la ruta: empezar su turno en la base
        self.route.append({
            "type": "base_start",
            "lat": self.base_start.lat,
            "lon": self.base_start.lon,
            "time": self.current_time
        })

    def calculate_travel_time(self, distance_km):
        """
        Convierte una distancia en kilómetros a tiempo de viaje en segundos,
        asumiendo la veloccidad del enunciado de 20 km/h.
        """
        return (distance_km / 20.0) * 3600.0 