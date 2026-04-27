SELECT 
    v.fecha,
    COUNT(v.viaje_id) AS viajes_totales,
    SUM(v.num_pasajeros) AS pasajeros_totales,
    COUNT(a.viaje_id) AS viajes_asignados,
    SUM(CASE WHEN a.viaje_id IS NULL THEN 1 ELSE 0 END) AS viajes_no_asignados
FROM 
    viajes v
LEFT JOIN 
    asignaciones a ON v.viaje_id = a.viaje_id
GROUP BY 
    v.fecha
ORDER BY 
    v.fecha;
