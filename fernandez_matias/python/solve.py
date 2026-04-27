import json
import os
import csv
import argparse
from models import Trip, Vehicle
from heuristic import Greedy

def process_instance(ruta_instancia, output_file, metrics_file):
    
    # Forzar que el archivo de salida JSON se guarde en la carpeta 'outputs'
    output_file = os.path.join('outputs', os.path.basename(output_file))
    
    with open(ruta_instancia, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    trips = [Trip(t['id'], t['origen'], t['destino'], t['hora_presentacion'], t['num_pasajeros']) for t in data.get('viajes', [])]
    vehicles = [Vehicle(v['id'], v['capacidad'], v['inicio_jornada'], v['fin_jornada']) for v in data.get('vehiculos', [])]
    
    # Ejecutar heurística
    solver = Greedy(trips, vehicles)
    unassigned_ids = solver.solve() # vemos los vehículos no asignados y la función modificó los vehículos al ejecutar la heurística
    
    # Calcular métricas finales y sumar los kms muertos del regreso a base
    total_trips = len(trips)
    unassigned_trips_count = len(unassigned_ids)
    assigned_trips_count = total_trips - unassigned_trips_count
    
    vehicles_used = 0
    total_deadhead_km = 0.0
    total_idle_time_sec = 0.0
    
    solution_dict = {
        "assigned_trips": [],
        "unassigned_trips": unassigned_ids,
        "routes": {}
    }
    
    for v in vehicles:
        if v.is_used:
            vehicles_used += 1
            total_idle_time_sec += v.idle_time_sec
            # Sumar el retorno a base final
            dist_to_base = v.current_location.distance_to(v.base_end)
            v.deadhead_km += dist_to_base
            total_deadhead_km += v.deadhead_km
            
            # Agregar nodo final a la ruta
            v.route.append({
                "type": "base_end",
                "lat": v.base_end.lat,
                "lon": v.base_end.lon,
                "time": round(v.current_time + v.calculate_travel_time(dist_to_base), 2)
            })
            
            solution_dict['assigned_trips'].extend(v.assigned_trips)
            solution_dict['routes'][v.id] = v.route
            
    # Guardar Output JSON
    output_dir = os.path.dirname(output_file)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(solution_dict, f, indent=4)
        
    # Guardar en CSV
    file_exists = os.path.isfile(metrics_file)
    with open(metrics_file, 'a', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['instance_name', 'total_trips', 'assigned_trips', 'unassigned_trips', 'vehicles_used', 'total_deadhead_km', 'total_idle_time_sec']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow({
            'instance_name': ruta_instancia,
            'total_trips': total_trips,
            'assigned_trips': assigned_trips_count,
            'unassigned_trips': unassigned_trips_count,
            'vehicles_used': vehicles_used,
            'total_deadhead_km': round(total_deadhead_km, 2),
            'total_idle_time_sec': round(total_idle_time_sec, 2)
        })
    print(f"Instancia {ruta_instancia} procesada. Archivo de salida y métricas actualizadas.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Resuelve instancias de ruteo de vehículos.")
    parser.add_argument('--input', required=True, help="Ruta al archivo JSON de la instancia.")
    parser.add_argument('--output', required=True, help="Ruta al archivo JSON de salida (solución).")
    parser.add_argument('--metrics', default='metrics.csv', help="Ruta al archivo CSV de métricas.")
    args = parser.parse_args()
    process_instance(args.input, args.output, args.metrics)
    
    #process_instance(ruta_instancia = "instancias/small.json", output_file='small_solution.json' , metrics_file = 'metrics.csv')
    #process_instance(ruta_instancia = "instancias/medium.json", output_file= 'medium_solution.json', metrics_file = 'metrics.csv')
    #process_instance(ruta_instancia = "instancias/large.json", output_file = 'small_solution.json', metrics_file = 'metrics.csv')
    #process_instance(ruta_instancia = "instancias/muy_large.json", output_file = 'small_solution.json', metrics_file = 'metrics.csv')
