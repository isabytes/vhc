# simulation.py

class Simulation:
    def __init__(self):
        self.running = False
        self.vehicles = []

    def add_vehicle(self, vehicle):
        self.vehicles.append(vehicle)

    def start(self):
        self.running = True
        print("Simulation started")

    def update(self, delta_time):
        if not self.running:
            return
        for vehicle in self.vehicles:
            vehicle.update(delta_time)
        print("Simulation updated")
