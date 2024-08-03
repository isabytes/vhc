"""
This is the main file. To run the simulation, you need to execute this file.
It is responsible of the game window, handles the main menu, creates vehicles and trailers,
and manages the simulation loop. The file coordinates all aspects of the vehicle
simulator, from user interface to physics calculations.
"""

import os
import pygame
from config import WIDTH, HEIGHT, VEHICLE_CONFIGS, TRAILER_CONFIGS, TRAILER_WEIGHT_OPTIONS, COLORS
from simulation import Simulation
from vehicle import Vehicle
from trailer import Trailer
from drawing import draw_screen, draw_buttons
from menu import main_menu, get_custom_weight
import traceback
import sys
from background import Background

# Change the working directory to the project root
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Start Pygame
pygame.init()

# Set up the screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Vehicle Simulator")

# Set up font
font = pygame.font.Font(None, 36)

# Make a simulation
sim = Simulation()

# Print welcome message
print("Welcome to the Vehicle Dynamics Simulator!")
print("This project was developed for Code in Place (Stanford), 2024.")
print("Coded by isabytes https://github.com/isabytes")
print("Have fun!")

def make_vehicle(vehicle_type, trailer_weight=None, use_metric=True):
    print(f"Making a {vehicle_type}")
    if vehicle_type == "quit":
        return 
    vehicle_info = VEHICLE_CONFIGS[vehicle_type].copy()
    vehicle_info['name'] = vehicle_type
    try:
        vehicle = Vehicle(**vehicle_info)
    except Exception as e:
        print(f"Error creating vehicle: {str(e)}")
        traceback.print_exc()
        return None

    if vehicle_type == "Semi truck":
        trailer_info = TRAILER_CONFIGS["Standard trailer"].copy()
        try:
            if trailer_weight is not None:
                trailer_info['mass'] = float(trailer_weight)
            trailer = Trailer(**trailer_info)
            print(f"Trailer created: {trailer}")
            vehicle.trailer = trailer
            vehicle.setup_trailer({'trailer': trailer})  # Call setup_trailer after assigning the trailer
            vehicle.update_total_mass()
        
            print(f"Trailer weight: {trailer.mass} kg")
            print(f"Total weight (truck + trailer): {vehicle.total_mass} kg")
        except:
            print(f"Oops, couldn't make the trailer")
            traceback.print_exc()
            print(f"Trailer weight: {trailer.mass} kg")
            print(f"Total weight (truck + trailer): {vehicle.total_mass} kg")
            return None
    
    return vehicle

def run_sim(vehicle, use_metric):
    print(f"Starting simulation for: {vehicle.name}")
    background = Background(WIDTH, HEIGHT, vehicle.METERS_TO_PIXELS, vehicle.VISUAL_SPEED_FACTOR)
    sim = Simulation()
    sim.add_vehicle(vehicle)
    
    # Set up buttons
    simulation_started = False
    simulation_paused = False
    start_button, restart_button, back_button = draw_buttons(screen, font, WIDTH, HEIGHT, simulation_started, simulation_paused)

    # Set up other stuff
    speed = 0
    rpm = vehicle.current_rpm
    distance = 0
    emissions = 0

    # Main loop
    running = True
    clock = pygame.time.Clock()
    
    while running:
        delta_time = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                if start_button.collidepoint(mouse_pos):
                    print("Start button clicked")
                    if not simulation_started:
                        simulation_started = True
                        vehicle.start()
                        print("Simulation started")
                    else:
                        simulation_paused = not simulation_paused
                        background.set_paused(simulation_paused)
                        print(f"Simulation {'paused' if simulation_paused else 'unpaused'}")
                elif restart_button.collidepoint(mouse_pos):
                    # Reset everything
                    vehicle = make_vehicle(vehicle.name, str(vehicle.trailer.mass if vehicle.trailer else None), use_metric)
                    if vehicle is None:
                        print("Couldn't make vehicle. Quitting.")
                        return "quit"
                    sim.add_vehicle(vehicle)
                    simulation_started = False
                    simulation_paused = False
                    speed = 0
                    rpm = vehicle.current_rpm
                    distance = 0
                    emissions = 0
                    vehicle.throttle = 0
                    background.set_paused(False)
                elif back_button.collidepoint(mouse_pos):
                    return "menu"

        if simulation_started and not simulation_paused:
            screen.fill(COLORS['BLACK'])
            vehicle.update(delta_time)
            background.update(vehicle, delta_time)
            
            # Update stuff
            speed = vehicle.speed
            rpm = vehicle.current_rpm
            distance += (speed / 3.6) * delta_time

            emission_value = vehicle.calculate_emissions(delta_time)
            if emission_value is not None:
                emissions += emission_value
            else:
                print("Oops, emissions calculation didn't work")
            
            # Check if vehicle is off screen
            if vehicle.position[0] > WIDTH:
                # Reset simulation
                vehicle = make_vehicle(vehicle.name, use_metric)
                if vehicle is None:
                    print("Couldn't make vehicle. Quitting.")
                    return "quit"
                sim.add_vehicle(vehicle)
                simulation_started = False
                simulation_paused = False
                speed = 0
                rpm = vehicle.current_rpm
                distance = 0
                emissions = 0
                background.set_paused(False)
                print("Vehicle went off screen. Starting over.")

        # Draw stuff
        background.draw(screen, vehicle, delta_time)
        vehicle.draw(screen, HEIGHT)
        draw_screen(screen, vehicle, font, speed, rpm, distance, emissions, WIDTH, HEIGHT, delta_time, start_button, restart_button, back_button, simulation_started, simulation_paused, use_metric)
        pygame.display.flip()
        
    return "menu"

def show_loading(screen, font):
    screen.fill(COLORS['BLACK'])
    loading_text = font.render("Loading...", True, COLORS['WHITE'])
    screen.blit(loading_text, (WIDTH // 2 - loading_text.get_width() // 2, HEIGHT // 2 - loading_text.get_height() // 2))
    pygame.display.flip()
    pygame.time.wait(400)

def main():
    pygame.init()

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Vehicle Simulator")
    font = pygame.font.Font(None, 36)

    use_metric = True
    running = True

    while running:
        result = main_menu(screen, font, WIDTH, HEIGHT)
        if result == "quit":
            running = False
        elif result == "toggle_units":
            use_metric = not use_metric
        elif result:
            vehicle_type, trailer_weight, use_metric = result
            if vehicle_type == "Semi truck" and trailer_weight == "custom":
                trailer_weight = get_custom_weight(screen, font, use_metric)
                if not trailer_weight:
                    continue
            
            vehicle = make_vehicle(vehicle_type, trailer_weight, use_metric)
            if vehicle:
                show_loading(screen, font)
                sim_result = run_sim(vehicle, use_metric)
                if sim_result == "quit":
                    running = False
            else:
                print("Couldn't make vehicle. Quitting.")
                running = False

    pygame.quit()
    print("Simulation ended")

if __name__ == "__main__":
    main()