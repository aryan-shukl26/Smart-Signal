import traci
from controller.signal_controller import (
    get_vehicle_counts,
    get_busiest_direction,
    control_signals,
    detect_emergency_vehicles,
    handle_emergency
)

SUMO_CFG = "simulation/intersection.sumocfg"

def run_simulation():
    traci.start(["sumo-gui", "-c", SUMO_CFG])
    
    try:
        step = 0
        while step < 3600:
            traci.simulationStep()
            
            emergency_vehicles = detect_emergency_vehicles()
            emergency_active = handle_emergency(emergency_vehicles)
            
            if step % 30 == 0:
                counts = get_vehicle_counts()
                busiest = get_busiest_direction(counts)
                
                if not emergency_active:
                    ns_count, ew_count, duration = control_signals(counts)
                    print(f"Step {step}:")
                    print(f"  Vehicle counts: {counts}")
                    print(f"  NS total: {ns_count} | EW total: {ew_count}")
                    print(f"  Busiest direction: {busiest}")
                    print(f"  Green duration set to: {duration}s")
                    print()
                else:
                    print(f"Step {step}:")
                    print(f"  🚨 Emergency mode active — adaptive control paused")
                    print()
            
            step += 1

    except Exception as e:
        print(f"Simulation stopped: {e}")
    finally:
        traci.close()

if __name__ == "__main__":
    run_simulation()