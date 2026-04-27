CREATE TABLE vehiculos (
    vehiculo_id VARCHAR(50) PRIMARY KEY,
    capacidad INT NOT NULL,
    base_id VARCHAR(50),
    hora_inicio_jornada TIME,
    hora_fin_jornada TIME
);

CREATE TABLE viajes (
    viaje_id VARCHAR(50) PRIMARY KEY,
    fecha DATE NOT NULL,
    inicio_programado TIMESTAMP,
    fin_programado TIMESTAMP,
    origen_comuna VARCHAR(50),
    destino_comuna VARCHAR(50),
    num_pasajeros INT NOT NULL
);

CREATE TABLE asignaciones (
    asignacion_id VARCHAR(50) PRIMARY KEY,
    vehiculo_id VARCHAR(50),
    viaje_id VARCHAR(50),
    orden_en_ruta INT,
    FOREIGN KEY (vehiculo_id) REFERENCES vehiculos(vehiculo_id),
    FOREIGN KEY (viaje_id) REFERENCES viajes(viaje_id)
);

CREATE TABLE eventos_operaciones (
    evento_id VARCHAR(50) PRIMARY KEY,
    vehiculo_id VARCHAR(50),
    viaje_id VARCHAR(50),
    timestamp_evento TIMESTAMP,
    tipo_evento VARCHAR(50),
    detalle TEXT,
    FOREIGN KEY (vehiculo_id) REFERENCES vehiculos(vehiculo_id),
    FOREIGN KEY (viaje_id) REFERENCES viajes(viaje_id)
);

