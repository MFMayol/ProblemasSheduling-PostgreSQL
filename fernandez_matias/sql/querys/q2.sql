    SELECT 
        ve.vehiculo_id,
        COUNT(a.viaje_id) AS viajes_asignados,
        COALESCE(SUM(v.num_pasajeros), 0) AS pasajeros_transportados,
        MIN(v.inicio_programado) AS primera_salida_programada,
        MAX(v.fin_programado) AS ultima_llegada_programada
    FROM 
        vehiculos ve
    LEFT JOIN 
        asignaciones a ON ve.vehiculo_id = a.vehiculo_id
    LEFT JOIN 
        viajes v ON a.viaje_id = v.viaje_id
    GROUP BY 
        ve.vehiculo_id
    ORDER BY 
        ve.vehiculo_id;
