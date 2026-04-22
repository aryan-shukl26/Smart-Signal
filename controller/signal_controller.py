import traci

INCOMING_EDGES = {
    "north": "north_in",
    "south": "south_in",
    "east":  "east_in",
    "west":  "west_in"
}

MIN_GREEN = 10
MAX_GREEN = 60
TRAFFIC_LIGHT_ID = "center"

# Phase indices in our traffic light program
PHASE_NS_GREEN = 0   # North/South green
PHASE_NS_YELLOW = 1  # North/South yellow
PHASE_EW_GREEN = 2   # East/West green
PHASE_EW_YELLOW = 3  # East/West yellow

def get_vehicle_counts():
    counts = {}
    for direction, edge in INCOMING_EDGES.items():
        counts[direction] = traci.edge.getLastStepVehicleNumber(edge)
    return counts

def calculate_green_duration(vehicle_count):
    duration = MIN_GREEN + (vehicle_count * 2)
    return min(duration, MAX_GREEN)

def get_busiest_direction(counts):
    return max(counts, key=counts.get)

def control_signals(counts):
    ns_count = counts["north"] + counts["south"]
    ew_count = counts["east"] + counts["west"]

    current_phase = traci.trafficlight.getPhase(TRAFFIC_LIGHT_ID)

    if ns_count >= ew_count:
        if current_phase != PHASE_NS_GREEN:
            traci.trafficlight.setPhase(TRAFFIC_LIGHT_ID, PHASE_NS_YELLOW)
        duration = calculate_green_duration(ns_count)
        traci.trafficlight.setPhaseDuration(TRAFFIC_LIGHT_ID, duration)
    else:
        if current_phase != PHASE_EW_GREEN:
            traci.trafficlight.setPhase(TRAFFIC_LIGHT_ID, PHASE_EW_YELLOW)
        duration = calculate_green_duration(ew_count)
        traci.trafficlight.setPhaseDuration(TRAFFIC_LIGHT_ID, duration)

    return ns_count, ew_count, duration

EMERGENCY_VEHICLE_TYPES = ["emergency"]

DIRECTION_TO_PHASE = {
    "north": PHASE_NS_GREEN,
    "south": PHASE_NS_GREEN,
    "east":  PHASE_EW_GREEN,
    "west":  PHASE_EW_GREEN,
}

def detect_emergency_vehicles():
    emergency_vehicles = []
    for veh_id in traci.vehicle.getIDList():
        veh_type = traci.vehicle.getTypeID(veh_id)
        if veh_type in EMERGENCY_VEHICLE_TYPES:
            edge = traci.vehicle.getRoadID(veh_id)
            speed = traci.vehicle.getSpeed(veh_id)
            emergency_vehicles.append({
                "id": veh_id,
                "edge": edge,
                "speed": speed
            })
    return emergency_vehicles

def handle_emergency(emergency_vehicles):
    for vehicle in emergency_vehicles:
        edge = vehicle["edge"]
        for direction, incoming_edge in INCOMING_EDGES.items():
            if edge == incoming_edge:
                required_phase = DIRECTION_TO_PHASE[direction]
                current_phase = traci.trafficlight.getPhase(TRAFFIC_LIGHT_ID)
                if current_phase != required_phase:
                    traci.trafficlight.setPhase(TRAFFIC_LIGHT_ID, required_phase)
                    traci.trafficlight.setPhaseDuration(TRAFFIC_LIGHT_ID, 60)
                    print(f"  🚨 EMERGENCY OVERRIDE: {vehicle['id']} on {edge} → forcing {direction} GREEN")
                return True
    return False
