import json
import argparse
import os
from models import Trip, Vehicle, haversine

def validate_solution(instance_path, solution_path):
    
    # Forzar que el validador busque el archivo de solución en la carpeta 'outputs'
    solution_path = os.path.join('outputs', os.path.basename(solution_path))
    
    with open(instance_path, 'r', encoding='utf-8') as f:
        inst_data = json.load(f)
    with open(solution_path, 'r', encoding='utf-8') as f:
        sol_data = json.load(f)
        
    # Mapear diccionarios
    trips_map = {t['id']: t for t in inst_data['viajes']}
    vehicles_map = {v['id']: v for v in inst_data['vehiculos']}
    
    errors = []
    
    # Validar viajes asignados
    assigned_trip_ids = set()
    for trip_record in sol_data.get('assigned_trips', []):
        tid = trip_record['trip_id']
        assigned_trip_ids.add(tid)
        
        if tid not in trips_map:
            errors.append(f"Viaje asignado {tid} no existe en la instancia.")
            continue
            
        inst_trip = trips_map[tid]
        if trip_record['pickup_time'] < inst_trip['hora_presentacion']:
            errors.append(f"Viaje {tid} recogido en {trip_record['pickup_time']} antes de su presentación {inst_trip['hora_presentacion']}.")
            
        # Verificar tiempo de viaje físico congruente
        dist_km = haversine(inst_trip['origen']['lat'], inst_trip['origen']['lon'], inst_trip['destino']['lat'], inst_trip['destino']['lon'])
        expected_time_sec = (dist_km / 20.0) * 3600
        actual_time_sec = trip_record['dropoff_time'] - trip_record['pickup_time']
        if abs(actual_time_sec - expected_time_sec) > 5.0: # tolerancia de 5 seg por redondeos
            errors.append(f"Viaje {tid} tiempo de traslado inconsistente. Se esperaban {expected_time_sec}s, tomó {actual_time_sec}s.")

    # Comprobar estado final del vehículo y capacidades
    for vid, route in sol_data.get('routes', {}).items():
        veh_inst = vehicles_map[vid]
        current_capacity = veh_inst['capacidad']
        current_pax = 0
        
        if not route:
            continue
            
        prev_step = route[0]
        if prev_step['time'] < veh_inst['inicio_jornada']['hora']:
            errors.append(f"Vehículo {vid} inició su recorrido antes de su inicio_jornada.")

        for step in route:
            time_stamp = step['time']
            
            # Validar que los tiempos de viaje entre CUALQUIER par de paradas (con o sin pasajeros) sean físicamente posibles
            if step != prev_step:
                dist_from_prev = haversine(prev_step['lat'], prev_step['lon'], step['lat'], step['lon'])
                min_expected_time = prev_step['time'] + (dist_from_prev / 20.0) * 3600
                if time_stamp < min_expected_time - 5.0: # 5 seg de tolerancia por redondeos
                    errors.append(f"Vehículo {vid} viajó de forma imposible hacia {step['type']} (Teletransportación detectada).")
                    
            if step['type'] == 'pickup':
                pax = trips_map[step['trip_id']]['num_pasajeros']
                current_pax += pax
                if current_pax > current_capacity:
                    errors.append(f"Vehículo {vid} superó capacidad en viaje {step['trip_id']}.")
            elif step['type'] == 'dropoff':
                pax = trips_map[step['trip_id']]['num_pasajeros']
                current_pax -= pax
                
            prev_step = step
                
        # Validar final de jornada
        last_step = route[-1]
        if last_step['type'] == 'base_end':
            if last_step['time'] > veh_inst['fin_jornada']['hora']:
                errors.append(f"Vehículo {vid} regresa a base ({last_step['time']}) excediendo fin_jornada ({veh_inst['fin_jornada']['hora']}).")

    if errors:
        print("Validación fallida. Se encontraron los siguientes errores:")
        for e in errors:
            print(f"- {e}")
        return False
    else:
        print("Validación exitosa. La solución es factible.")
        return True

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Verifica factibilidad de un ruteo.")
    parser.add_argument('--instance', required=True, help="JSON de la instancia.")
    parser.add_argument('--solution', required=True, help="JSON con la solución.")
    args = parser.parse_args()
    
    validate_solution(args.instance, args.solution)