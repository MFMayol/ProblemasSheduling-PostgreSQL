COPY vehiculos
FROM 'C:\Users\Public\vehiculos.csv'
DELIMITER ','
CSV HEADER;

COPY viajes
FROM 'C:\Users\Public\viajes.csv'
DELIMITER ','
CSV HEADER;

COPY asignaciones
FROM 'C:\Users\Public\asignaciones.csv'
DELIMITER ','
CSV HEADER;

COPY eventos_operaciones
FROM 'C:\Users\Public\eventos_operacion.csv'
DELIMITER ','
CSV HEADER;