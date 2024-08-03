import pygame
# Configuration Module for Vehicle Simulation
"""
This file, config.py, serves as the main configuration file for our vehicle simulation game.
It contains essential settings that control various aspects of the game, including:

1. Game Window Size: Dimensions of the game window.
2. Vehicle Settings: Detailed specifications for different vehicle types.
3. Trailer Settings: Information about different trailers, including dimensions and wheel positions.
4. Colors: Color definitions used throughout the game.

We use dictionaries to store vehicle and trailer info. This makes it easy to add new ones and get
their properties fast. Each vehicle or trailer type is a key in the dictionary, with its properties
stored as nested dictionaries.
By centralizing all these settings in one place, we can change how the game looks and works without
changing the main game code. This helps keep the game working well and lets us adjust things quickly.

Note: Even though these settings are easy to change, be careful to keep the game realistic and
working right when you make changes.
"""

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 1200, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))

# Define colors
COLORS = {
    'WHITE': (255, 255, 255),
    'BLACK': (0, 0, 0),
    'RED': (255, 0, 0),
    'BLUE': (0, 0, 255),
    'GREEN': (0, 255, 0),
    'YELLOW': (255, 255, 0),
    'LIGHT_GRAY': (200, 200, 200),
    'DARK_GRAY': (100, 100, 100),
    'LIGHT_BLUE': (173, 216, 230),
}

# Trailer configurations
TRAILER_CONFIGS = {
    "Standard trailer": {
        "image_path": "assets/images/trailer.png",
        "wheel_image_path": "assets/images/tires/tire2.png",
        "wheel_positions": [(145, 138), (191, 138), (99, 138)],
        "wheel_size": (45, 45),
        "initial_position": [-360, 305],  # Offset from the vehicle's position
        "mass": 1000.0  # Weight of the trailer in kg
        # Note: 'initial_position' here acts as an offset from the vehicle's position,
        # not as an absolute position. [0, 0] means the trailer will be at the exact
        # same position as the vehicle. Adjust this to offset the trailer from the vehicle.
        
    }
}

# Trailer weight options
TRAILER_WEIGHT_OPTIONS = [
    ("7000 kg", "Empty Trailer"),
    ("15000 kg", "Light Load"),
    ("25000 kg", "Moderate Load"),
    ("35000 kg", "Heavy Load"),
    ("Custom", "Custom Weight")
]

# Vehicle configurations
VEHICLE_CONFIGS = {
    "Semi truck": {
        "is_truck": True,
        "initial_position": [50, 315],
        "max_rpm": 2500,
        "gear_ratios": [14.94, 8.05, 5.37, 3.78, 2.88, 2.33, 1.91, 1.61, 1.38, 1.18, 1.00, 0.84, 0.74],
        "max_speed": 120,  # km/h
        "low_rpm_threshold": 1200,
        "mid_rpm_threshold": 1500,
        "high_rpm_threshold": 2000,
        "green_start": 1000,
        "green_end": 1600,
        "yellow_end": 2000,
        "engine_power": 388,  # kW
        "fuel_efficiency": 35,  # L/100km
        "final_drive_ratio": 3.73,
        "wheel_circumference": 3.2,  # meters
        "friction_coefficient": 0.015,
        "air_resistance_coefficient": 0.6,
        "idle_rpm": 600,
        "mass": 7000.0,  # kg
        "emission_factor": 1000,  # g CO2/km
        "front_wheel_image_path": 'assets/images/tires/tire1.png',
        "rear_wheel_image_path": 'assets/images/tires/tire2.png',
        "wheel_positions": [(224, 128), (79, 128), (29, 128)], #119 in old config 123 news 
        "wheel_size": (45, 45),
        "image_path": 'assets/images/semi_truck.png',
        "max_torque": 2500,  # Nm
        "max_power": 388,    # kW
        "power_curve": [
            (0, 0), (600, 50), (800, 150), (1000, 220), (1200, 280),
            (1400, 330), (1600, 365), (1800, 385), (2000, 388), (2100, 380),
        ],
        "torque_curve": [
            (0, 2500), (600, 2500), (800, 2500), (1000, 2450), (1200, 2400),
            (1400, 2300), (1600, 2200), (1800, 2050), (2000, 1900), (2200, 1100),
        ],
        "shift_up_rpm": 2000,
        "shift_down_rpm": 1000,
        "rev_drop_rate": 680,
        "post_shift_adjustment_factor": 2,
        "frontal_area": 9.0,  # m²
    },
    "Pickup truck": {
        "initial_position": [50, 352],
        "max_rpm": 6000,
        "gear_ratios": [4.17, 2.34, 1.52, 1.15, 0.85, 0.67],
        "max_speed": 180,  # km/h
        "low_rpm_threshold": 1500,
        "mid_rpm_threshold": 3000,
        "high_rpm_threshold": 5000,
        "green_start": 1500,
        "green_end": 3000,
        "yellow_end": 5000,
        "fuel_efficiency": 12,  # L/100km
        "final_drive_ratio": 3.73,
        "wheel_circumference": 2.4,
        "friction_coefficient": 0.014,
        "air_resistance_coefficient": 0.41,
        "idle_rpm": 750,
        "mass": 2500,  # kg
        "emission_factor": 300,  # g CO2/km
        "image_path": "assets/images/pickup_truck.png",
        "wheel_image_path": "assets/images/tires/tire2.png",
        "wheel_positions": [(62, 80), (254, 80)],
        "wheel_size": (45, 45),
        "shift_up_rpm": 4200,
        "shift_down_rpm": 2000,
        "max_power": 200,  # kW
        "engine_power": 200,  # kW
        "max_torque": 460,  # Nm
        "power_curve": [
            (0, 0),    (1000, 40),  (1500, 80),  (2000, 120),
            (2500, 150), (3000, 175), (3500, 190), (4000, 200),
            (4500, 195), (5000, 185), (5500, 170), (6000, 150)
        ],
        "torque_curve": [
            (0, 300),   (1000, 400), (1500, 440), (2000, 460),
            (2500, 460), (3000, 450), (3500, 420), (4000, 390),
            (4500, 360), (5000, 330), (5500, 300), (6000, 270)
        ],
        "rev_drop_rate": 2000,
        "frontal_area": 3.2,  # m²
    },
    "Sports car": {
        "initial_position": [50, 400],
        "max_rpm": 7500,
        "gear_ratios": [3.82, 2.15, 1.56, 1.21, 0.97, 0.82],
        "max_speed": 308,  # km/h
        "engine_power": 331,  # kW
        "max_torque": 530,  # Nm
        "mass": 1480,  # kg
        "air_resistance_coefficient": 0.32,
        "final_drive_ratio": 3.39,
        "power_curve": [
            (0, 0), (1000, 50), (2000, 120), (3000, 200), (4000, 260),
            (5000, 300), (6000, 325), (7000, 331), (7300, 300), (7500, 200)
        ],
        "torque_curve": [
            (0, 530), (1000, 530), (2000, 530), (3000, 530), (4000, 525),
            (5000, 515), (6000, 500), (7000, 450), (7300, 350), (7500, 250)
        ],
        "low_rpm_threshold": 2000,
        "mid_rpm_threshold": 4500,
        "high_rpm_threshold": 6500,
        "green_start": 2000,
        "green_end": 4500,
        "yellow_end": 6500,
        "friction_coefficient": 0.01,
        "fuel_efficiency": 9.5,  # L/100km
        "idle_rpm": 800,
        "emission_factor": 250,  # g CO2/km
        "wheel_circumference": 2.0,  # meters
        "image_path": "assets/images/sports_car.png",
        "wheel_image_path": "assets/images/tires/tire4.png",
        "wheel_positions": [(45, 52), (196, 52)],
        "wheel_size": (36, 36),
        "shift_up_rpm": 6800,
        "shift_down_rpm": 3500,
        "rev_drop_rate": 4500,
        "post_shift_adjustment_factor": 0.5,
        "frontal_area": 2.0,  # m²
    },
    "Electric car": {
        "is_electric": True,
        "initial_position": [50, 400],
        "max_rpm": 20000,
        "single_gear_ratio": 7.8,
        "max_speed": 332,
        "engine_power": 760,
        "max_torque": 1420,
        "power_curve": [
            (0, 760), (2000, 760), (4000, 760), (6000, 760), (8000, 760),
            (10000, 760), (12000, 750), (14000, 730), (16000, 700),
            (18000, 660), (20000, 600)
        ],
        "torque_curve": [
            (0, 1420), (2000, 1420), (4000, 1420), (6000, 1400), (8000, 1350),
            (10000, 1300), (12000, 1200), (14000, 1100), (16000, 1000),
            (18000, 900), (20000, 800)
        ],
        "battery_capacity": 100,  # kWh
        "energy_consumption": 18,  # kWh/100km
        "mass": 2162,  # kg
        "friction_coefficient": 0.01,
        "air_resistance_coefficient": 0.208,  # Extremely low drag coefficient for better acceleration
        "wheel_circumference": 2.06,  # For 21" wheels (265/35R21)
        "image_path": "assets/images/electric_car.png",
        "wheel_image_path": "assets/images/tires/tire4.png",
        "wheel_positions": [(36, 55), (168, 55)],
        "wheel_size": (32, 32),
        "frontal_area": 2.4,  # m^2
    },
    "Compact car": {
        "initial_position": [50, 390],
        "max_rpm": 6500,
        "gear_ratios": [3.727, 2.048, 1.393, 1.029, 0.820],
        "max_speed": 180,
        "low_rpm_threshold": 1500,
        "mid_rpm_threshold": 3000,
        "high_rpm_threshold": 5000,
        "green_start": 1500,
        "green_end": 3000,
        "yellow_end": 5000,
        "mass": 1150,
        "engine_power": 66,  # kW (about 88 hp)
        "friction_coefficient": 0.013,
        "air_resistance_coefficient": 0.30,
        "fuel_efficiency": 6,  # L/100km
        "idle_rpm": 800,
        "emission_factor": 150,  # g CO2/km
        "final_drive_ratio": 4.21, 
        "wheel_circumference": 1.96,
        "image_path": "assets/images/compact_car.png",
        "wheel_image_path": "assets/images/tires/tire5.png",
        "wheel_positions": [(158, 64), (32, 64)],
        "wheel_size": (31, 31),
        "max_torque": 130,  # Nm
        "max_power": 66,    # kW
        "power_curve": [
            (0, 0), (1000, 15), (2000, 30), (3000, 45), (4000, 55),
            (5000, 62), (6000, 66), (6500, 64)
        ],
        "torque_curve": [
            (0, 90), (1500, 130), (2000, 130), (3500, 125), (5000, 115), (6000, 105), (6500, 100)
        ],
        "shift_up_rpm": 5200,
        "shift_down_rpm": 2000,
        "rev_drop_rate": 1900,
        "frontal_area": 2.1,  # m²
    }
}

# Traffic cone configuration this is for debugging purposes 
TRAFFIC_CONE_CONFIG = {
    "image_path": "assets/images/traffic_cone.png",
    "height": 0.75  # meters
}
# Simulation parameters
TIME_STEP = 0.1  # seconds
# Print initial positions of vehicles for debugging
print("VEHICLE_CONFIGS:")
for vehicle_type, config in VEHICLE_CONFIGS.items():
    print(f"{vehicle_type}: {config.get('initial_position', 'No initial_position')}")
