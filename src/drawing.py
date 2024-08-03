import pygame
from config import VEHICLE_CONFIGS
from utils import kmh_to_mph, km_to_miles, mps_to_kmh, mps_to_mph
import numpy as np
import math

def draw_background(screen):
    screen.fill((135, 206, 235))  # Light blue sky color

def draw_buttons(screen, font, screen_width, screen_height, simulation_started, simulation_paused):
    start_button = pygame.Rect(screen_width - 220, 10, 210, 50)
    restart_button = pygame.Rect(screen_width - 220, 70, 210, 50)
    menu_button = pygame.Rect(screen_width - 220, 130, 210, 50)

    pygame.draw.rect(screen, (0, 255, 0), start_button)
    pygame.draw.rect(screen, (255, 255, 0), restart_button)
    pygame.draw.rect(screen, (255, 0, 0), menu_button)

    if not simulation_started:
        start_text = font.render("Start", True, (0, 0, 0))
    elif simulation_paused:
        start_text = font.render("Resume", True, (0, 0, 0))
    else:
        start_text = font.render("Pause", True, (0, 0, 0))

    restart_text = font.render("Restart", True, (0, 0, 0))
    menu_text = font.render("Back to Menu", True, (0, 0, 0))

    screen.blit(start_text, (start_button.x + 10, start_button.y + 10))
    screen.blit(restart_text, (restart_button.x + 10, restart_button.y + 10))
    screen.blit(menu_text, (menu_button.x + 10, menu_button.y + 10))

    return start_button, restart_button, menu_button

def draw_metrics(screen, font, vehicle, current_speed, current_rpm, distance, emissions, HEIGHT, use_metric):
    if use_metric:
        speed_unit = "km/h"
        distance_unit = "km"
        emissions_unit = "kg CO2"
        speed_value = int(mps_to_kmh(current_speed))
        distance_value = distance / 1000
    else:
        speed_unit = "mph"
        distance_unit = "miles"
        emissions_unit = "lbs CO2"
        speed_value = int(mps_to_mph(current_speed))
        distance_value = km_to_miles(distance / 1000)
    
    emissions_value = emissions if use_metric else emissions * 2.20462  # kg to lbs

    speed_text = font.render(f"Speed: {speed_value} {speed_unit}", True, (0, 0, 0))
    rpm_text = font.render(f"RPM: {int(current_rpm)}", True, (0, 0, 0))
    distance_text = font.render(f"Distance: {distance_value:.2f} {distance_unit}", True, (0, 0, 0))
    emissions_text = font.render(f"Emissions: {emissions_value:.2f} {emissions_unit}", True, (0, 0, 0))
    gear_text = font.render(f"Gear: {vehicle.current_gear}", True, (0, 0, 0))

    screen.blit(speed_text, (10, 10))
    screen.blit(rpm_text, (10, 50))
    screen.blit(distance_text, (10, 90))
    screen.blit(emissions_text, (10, 130))
    if not vehicle.is_electric:
        screen.blit(gear_text, (10,170))

    if hasattr(vehicle, 'gear_shift_data'):
        draw_gear_info(screen, font, vehicle, HEIGHT)
        
def draw_screen(screen, vehicle, font, current_speed, current_rpm, distance, emissions, WIDTH, HEIGHT, delta_time, start_button, restart_button, back_to_menu_button, simulation_started, simulation_paused, use_metric):
    # Draw the vehicle on the screen
    vehicle.draw(screen, HEIGHT)

    # Draw buttons and other information
    draw_buttons(screen, font, WIDTH, HEIGHT, simulation_started, simulation_paused)
    draw_metrics(screen, font, vehicle, current_speed, current_rpm, distance, emissions, HEIGHT, use_metric)

    # Try to get the vehicle information
    try:
        vehicle_info = VEHICLE_CONFIGS[vehicle.name]
    except KeyError:
        # If we can't find the vehicle, print an error message
        print(f"Oops! Can't find info for vehicle named '{vehicle.name}'")
        print(f"Available vehicle types: {list(VEHICLE_CONFIGS.keys())}")
        # Use the first available vehicle as a backup
        vehicle_info = VEHICLE_CONFIGS[list(VEHICLE_CONFIGS.keys())[0]]

    # Set default values if we can't find the information
    max_rpm = vehicle_info.get('max_rpm', 6000)  # Use 6000 if 'max_rpm' is not found
    max_speed = vehicle_info.get('max_speed', 200)  # Use 200 if 'max_speed' is not found
    
    # Make sure current_rpm is not None
    if current_rpm is None:
        current_rpm = 0

    # Draw the appropriate gauge based on the vehicle type
    if vehicle.is_electric:
        draw_ev_power_gauge(screen, vehicle.throttle, WIDTH, HEIGHT, font, simulation_started)
    else:
        draw_rpm_gauge(screen, vehicle, current_rpm, 
                       WIDTH, HEIGHT, font,
                       vehicle_info.get("green_start"),
                       vehicle_info.get("green_end"),
                       vehicle_info.get("yellow_end"))
    
    # Draw the speed gauge
    draw_speed_gauge(screen, current_speed, max_speed, WIDTH, HEIGHT, font, use_metric)
    # Calculate and display acceleration times
    if vehicle.speed < 100 / 3.6:  # 3.6 is used to convert km/h to m/s
        acceleration_text = f"0-100 km/h: {vehicle.acceleration_timer:.1f} seconds"
    elif vehicle.zero_to_hundred_time is not None:
        acceleration_text = f"0-100 km/h: {vehicle.zero_to_hundred_time:.1f} seconds"
    else:
        acceleration_text = "0-100 km/h: N/A"

    # debug max speed counter
    # if vehicle.speed < vehicle.max_speed / 3.6:
    #     max_speed_text = f"0-{vehicle.max_speed} km/h: {vehicle.max_speed_acceleration_timer:.1f} seconds"
    # elif vehicle.zero_to_max_speed_time is not None:
    #     max_speed_text = f"0-{vehicle.max_speed} km/h: {vehicle.zero_to_max_speed_time:.1f} seconds"
    # else:
    #     max_speed_text = f"0-{vehicle.max_speed} km/h: N/A"

    # Draw acceleration times on the screen
    acceleration_surface = font.render(acceleration_text, True, (0, 0, 0))
    screen.blit(acceleration_surface, (10, HEIGHT - 40))  
    # max_speed_surface = font.render(max_speed_text, True, (0, 0, 0))
    # screen.blit(max_speed_surface, (10, HEIGHT - 40))

    # Update the display
    pygame.display.flip()
    
def draw_rpm_gauge(screen, vehicle, current_rpm, WIDTH, HEIGHT, font, green_start, green_end, yellow_end):
        # This part is pretty complex but also really cool! I got help from online sources
        # to make this realistic looking RPM gauge. I'm still learning how it all works, and encountered lot of issues
        # but it's awesome to finally see it in action! Here's how it works.It creates a circular RPM gauge using trigonometry.
        # Calculates points for arcs with math.cos() and math.sin(),
        # Draws a circular gauge with colored rpm ranges (green, yellow, red) as in real life.
        # Shows tick marks and numbers for RPM values
        # Moves a needle to show the current RPM
        # I add comments as always to break it down as best I can 
    # Set up the gauge position and size
    center_x, center_y = WIDTH - 120, HEIGHT - 120  # Position the gauge in the bottom right
    radius = 80  # Outer radius of the gauge
    inner_radius = 72  # Inner radius for the colored arcs
    max_rpm = vehicle.max_rpm  # Get the maximum RPM for this vehicle

    # This function creates points to draw arcs
    # It's complex, but it helps us draw the curved shapes of the gauge
    def get_arc_points(start_angle, end_angle, r1, r2, num_points=50):
        points = []
        # Create outer arc points
        for i in range(num_points):
            angle = start_angle + (end_angle - start_angle) * i / (num_points - 1)
            x = center_x + math.cos(angle) * r1
            y = center_y + math.sin(angle) * r1
            points.append((x, y))
        # Create inner arc points (in reverse order)
        for i in range(num_points):
            angle = end_angle - (end_angle - start_angle) * i / (num_points - 1)
            x = center_x + math.cos(angle) * r2
            y = center_y + math.sin(angle) * r2
            points.append((x, y))
        return points

    # Set up the start and end angles for the gauge
    start_angle = math.pi * 0.75  # 135 degrees (bottom left of the circle)
    end_angle = math.pi * 2.25    # 405 degrees (45 degrees past top right)

    # This function converts an RPM value to an angle on the gauge
    def rpm_to_angle(rpm):
        if max_rpm == 0:
            return start_angle  # Avoid division by zero
        # Calculate the angle based on the RPM
        return start_angle + (rpm / max_rpm) * (end_angle - start_angle)

    # Draw the white background circle
    pygame.draw.circle(screen, (255, 255, 255), (center_x, center_y), radius)

    # Draw the gray background for the gauge
    gray_points = get_arc_points(start_angle, end_angle, radius, inner_radius)
    pygame.draw.polygon(screen, (200, 200, 200), gray_points)

    # Define the colors and RPM ranges for the gauge
    colors = [
        ((0, 255, 0), green_start, green_end, "Green"),
        ((255, 255, 0), green_end, yellow_end, "Yellow"),
        ((255, 0, 0), yellow_end, max_rpm, "Red")
    ]

    # Draw each colored segment of the gauge
    for color, start, end, name in colors:
        start_angle_arc = rpm_to_angle(start)
        end_angle_arc = rpm_to_angle(end)
        color_points = get_arc_points(start_angle_arc, end_angle_arc, radius, inner_radius)
        pygame.draw.polygon(screen, color, color_points)

    # Draw the RPM marks and numbers
    draw_rpm_marks(screen, vehicle, font, center_x, center_y, radius, inner_radius, rpm_to_angle)

    # Draw the needle
    needle_angle = rpm_to_angle(current_rpm)
    needle_length = radius
    needle_end_x = center_x + math.cos(needle_angle) * needle_length
    needle_end_y = center_y + math.sin(needle_angle) * needle_length
    pygame.draw.line(screen, (255, 0, 0), (center_x, center_y), (needle_end_x, needle_end_y), 5)

    # Display the current RPM
    rpm_text = font.render(f"{int(current_rpm)} RPM", True, (0, 0, 0))
    rpm_rect = rpm_text.get_rect(center=(center_x, center_y + radius + 20))
    screen.blit(rpm_text, rpm_rect)

def draw_rpm_marks(screen, vehicle, font, center_x, center_y, radius, inner_radius, rpm_to_angle):
    if vehicle.name != "Semi truck" and not vehicle.is_electric:
        # Round max_rpm to the nearest thousand
        rounded_max_rpm = round(vehicle.max_rpm, -3)
        tick_interval = rounded_max_rpm // 8

        for i in range(0, 9):
            rpm = round(i * tick_interval, -3) # Round to the nearest thousand
            angle = rpm_to_angle(rpm)
            
            # Draw tick mark
            start_x = center_x + math.cos(angle) * radius
            start_y = center_y + math.sin(angle) * radius
            end_x = center_x + math.cos(angle) * (inner_radius - 5)
            end_y = center_y + math.sin(angle) * (inner_radius - 5)
            pygame.draw.line(screen, (0, 0, 0), (start_x, start_y), (end_x, end_y), 2)

            # Draw numbers
            x = center_x + math.cos(angle) * (inner_radius - 20)
            y = center_y + math.sin(angle) * (inner_radius - 20)
            num_text = font.render(f"{rpm // 1000}", True, (0, 0, 0))
            num_rect = num_text.get_rect(center=(x, y))
            screen.blit(num_text, num_rect)
    else:
        # Original tick marks for semi trucks and EVs
        for i in range(0, 30, 5):
            angle = rpm_to_angle(i * 100)
            
            # Draw tick mark
            start_x = center_x + math.cos(angle) * radius
            start_y = center_y + math.sin(angle) * radius
            end_x = center_x + math.cos(angle) * (inner_radius - 5)
            end_y = center_y + math.sin(angle) * (inner_radius - 5)
            pygame.draw.line(screen, (0, 0, 0), (start_x, start_y), (end_x, end_y), 2)

            # Draw numbers
            x = center_x + math.cos(angle) * (inner_radius - 20)
            y = center_y + math.sin(angle) * (inner_radius - 20)
            num_text = font.render(str(i), True, (0, 0, 0))
            num_rect = num_text.get_rect(center=(x, y))
            screen.blit(num_text, num_rect)
            
def draw_ev_power_gauge(screen, throttle, WIDTH, HEIGHT, font, simulation_started):
    # This function draws a power gauge for electric vehicles
    
    # Set up the position of the gauge
    center_x, center_y = WIDTH - 120, HEIGHT - 120
    radius = 80
    
    # Define the start and end angles for the gauge arc
    start_angle = 210  # 7 o'clock position
    end_angle = -30   # 5 o'clock position
    angle_range = end_angle - start_angle

    # Draw the gauge background
    pygame.draw.circle(screen, (200, 200, 200), (center_x, center_y), radius)
    pygame.draw.circle(screen, (255, 255, 255), (center_x, center_y), radius - 10)

    # Calculate and draw the needle position
    if simulation_started:
        # The needle moves based on the throttle (0 to 1)
        current_angle = start_angle + throttle * angle_range
    else:
        # If simulation hasn't started, keep needle at start position
        current_angle = start_angle
    
    # Convert angle to radians and calculate needle end position
    angle_rad = math.radians(current_angle)
    end_x = center_x + radius * math.cos(angle_rad)
    end_y = center_y - radius * math.sin(angle_rad)
    
    # Draw the needle
    pygame.draw.line(screen, (255, 0, 0), (center_x, center_y), (int(end_x), int(end_y)), 5)

    # Display the current power percentage
    power_text = font.render(f"Power: {int(throttle * 100)}%", True, (0, 0, 0))
    screen.blit(power_text, (center_x - 50, center_y + radius + 10))

def draw_speed_gauge(screen, current_speed,max_speed, WIDTH, HEIGHT, font, use_metric):  
    #This function draws a complex speed gauge was tricky to figure out how to code it.
    # It Renders a semi-circular speedometer using polar to cartesian coordinate conversion. 
    # map speed to angle, draw tick marks and numbers at intervals, and position needle.
    # Implemented by calculating angle ratios, using math.cos() and math.sin() for point positioning, 
    # and drawing elements with pygame shape functions. Handles both km/h and mph too    
    center_x, center_y = WIDTH - 300, HEIGHT - 120
    radius = 80
    pygame.draw.circle(screen, (255, 255, 255), (center_x, center_y), radius)    
    # We convert vehicle.speed to km/h or mph for user-friendly display
    # We use int() to round the speed to whole numbers for cleaner presentation
    speed_unit = "km/h" if use_metric else "mph"
    # This line converts speed from m/s to km/h or mph, then rounds it to an integer
    speed_value = mps_to_kmh(current_speed) if use_metric else mps_to_mph(current_speed)
    # max_speed is already in km/h, so we only need to convert it to mph if not using metric
    max_speed_value = int(max_speed) if use_metric else int(kmh_to_mph(max_speed))    
    # Debug print to check the speed value
    #print(f"Debug: Current speed: {speed_value:.1f} {speed_unit}")
    # Adjust the angle calculation to start from 7 o'clock (210 degrees)
    #adjusts angles based on vehicle type
    start_angle = 225  # 7:30 position
    end_angle = -45    # 4:30 position
    angle_range = start_angle - end_angle
    
    angle = start_angle - (speed_value / max_speed_value) * angle_range
    end_x = center_x + radius * math.cos(math.radians(angle))
    end_y = center_y - radius * math.sin(math.radians(angle))
    
    
    pygame.draw.line(screen, (255, 0, 0), (center_x, center_y), (end_x, end_y), 5)
    
    # Calculate the number of tick marks based on max_speed_value divided by 10
    num_marks = max_speed_value // 10 + 1
    for i in range(num_marks):
        speed = i * 10
        mark_angle = start_angle - (speed / max_speed_value) * angle_range
        angle_rad = math.radians(mark_angle)
        inner_r = radius - 4
        inner_x = center_x + inner_r * math.cos(angle_rad)
        inner_y = center_y - inner_r * math.sin(angle_rad)
        outer_x = center_x + radius * math.cos(angle_rad)
        outer_y = center_y - radius * math.sin(angle_rad)
        
        # Draw speed numbers (adaptive intervals based on max speed)
        interval = max(10, (max_speed_value // 6) // 10 * 10) #used 6 to decrease the number a bit
        # Use the interval logic to determine which ticks to thicken
        if speed % interval == 0:
            # Draw thicker and longer lines for major intervals
            inner_x_extended = center_x + (radius - 10) * math.cos(math.radians(mark_angle))
            inner_y_extended = center_y - (radius - 10) * math.sin(math.radians(mark_angle))
            pygame.draw.line(screen, (0, 0, 0), (inner_x_extended, inner_y_extended), (outer_x, outer_y), 6)  # Thicker and longer line
        else:
            pygame.draw.line(screen, (0, 0, 0), (inner_x, inner_y), (outer_x, outer_y), 2)  # Normal line
        
        if speed % interval == 0 and speed <= max_speed_value:
            number_x = center_x + (radius - 30) * math.cos(math.radians(mark_angle))
            number_y = center_y - (radius - 30) * math.sin(math.radians(mark_angle))
            smaller_font = pygame.font.Font(None, 25)  # Decrease font size
            number_text = smaller_font.render(str(speed), True, (0, 0, 0))
            number_rect = number_text.get_rect(center=(number_x, number_y))
            screen.blit(number_text, number_rect)
    speed_text = font.render(f"Speed: {int(speed_value)} {speed_unit}", True, (0, 0, 0))
    speed_text_rect = speed_text.get_rect()
    speed_text_rect.centerx = center_x  # Center the text using the actual center of the gauge
    speed_text_rect.top = center_y + radius + 10
    screen.blit(speed_text, speed_text_rect)
    
def draw_gear_info(screen, font, vehicle, HEIGHT):
    # Get gear info
    gear_info = vehicle.gear_shift_data

    # Start drawing from here
    y = HEIGHT - 150

    # Show info for each gear
    for i in range(len(gear_info)):
        gear = gear_info[i][0]
        time = gear_info[i][1]
        speed = gear_info[i][2]
        
        # Make text
        if i < len(gear_info) - 1:
            next_speed = gear_info[i+1][2]
            text = f"Gear {gear}: {time:.1f}s ({speed:.0f} - {next_speed:.0f} km/h)"
        else:
            text = f"Gear {gear}: {time:.1f}s ({speed:.0f} km/h+)"
        
        # Put text on screen
        words = font.render(text, True, (0, 0, 0))
        screen.blit(words, (10, y))
                # Move down
        y = y + 30
        
def draw_gear_indicator(screen, font, vehicle, WIDTH, HEIGHT):
    # Make text for current gear
    gear_text = font.render(f"Gear: {vehicle.current_gear}", True, (255, 255, 255))
    
    # text position
    text_width = gear_text.get_width()
    text_height = gear_text.get_height()
    x = WIDTH - text_width - 10
    y = 10
    
    # black box behind the text
    box_width = text_width + 20
    box_height = text_height + 10
    pygame.draw.rect(screen, (0, 0, 0), (x - 10, y - 5, box_width, box_height))
    
    # Put the text on the screen
    screen.blit(gear_text, (x, y))
    
    #end