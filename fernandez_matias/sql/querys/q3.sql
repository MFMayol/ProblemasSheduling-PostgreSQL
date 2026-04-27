SELECT 
    v.viaje_id,
    v.fecha,
    v.inicio_programado,
    v.fin_programado,
    v.origen_comuna,
    v.destino_comuna,
    v.num_pasajeros
FROM 
    viajes v
LEFT JOIN 
    asignaciones a ON v.viaje_id = a.viaje_id
WHERE 
    a.viaje_id IS NULL --para encontrar los que no se asignaron
ORDER BY 
    v.fecha ASC, 
    v.inicio_programado ASC;
