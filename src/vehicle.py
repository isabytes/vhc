import random 
import pygame
import math
import bisect
from datetime import datetime
from gear_shifting import GearShiftingSystem
import time #for debug prints
from config import VEHICLE_CONFIGS

# vehicle.py is the central module for our vehicle simulation
# This file defines the Vehicle class, which is the core component of the simulation
# It manages both electric and internal combustion engine (ICE) vehicles, handling their
# physical properties, performance characteristics, and simulation logic
# The class is designed to be adaptable, accommodating various vehicle types and configurations
# All vehicle attributes are dynamically set through the kwargs system, allowing for flexible
# initialization without constant values. This enables easy creation of diverse vehicle types with
# different characteristics, from compact cars to heavy trucks, and from internal combustion engines
# to electric powertrains. 

# Constants for physical calculations

GRAVITY = 9.81 # These constants are defined to accurately simulate real-world physics in our vehicle model.
AIR_DENSITY = 1.225 # They are important for calculating vehicle performance specifcially aerodynamic  resistence in the simulation.

class Vehicle(pygame.sprite.Sprite):
    def __init__(self, mass=None, **kwargs):
        """
        Initialize a new Vehicle instance.
        
        This constructor sets up the basic attributes of the vehicle, including its mass,
        type (electric or ICE), and name. It uses a flexible kwargs system to allow for
        easy extension and customization of vehicle properties.
        
        :param kwargs: Dictionary of vehicle attributes. For example:'mass' Vehicle mass in kg
        """
        pygame.sprite.Sprite.__init__(self)
        print("Creating a new vehicle")
        print("Vehicle __init__ called with kwargs:", kwargs)
        
        # Set up mass (crucial for physics calculations)
        self.mass = mass if mass is not None else kwargs.get('mass')
        if self.mass is None or self.mass <= 0:
            raise ValueError(f"Vehicle mass must be specified and greater than zero. Received: {self.mass}")
        print(f"Mass set to: {self.mass}")
        
        # Common attributes for all vehicle types
        self.is_electric = kwargs.get('is_electric', False)
        print(f"Vehicle is electric: {self.is_electric}")
        self.name = kwargs.get('name', 'Unknown Vehicle')
        self.gear_system = None 
        print(f"Vehicle initialized with name: {self.name}")  # Debug print
        self.engine_power = kwargs['engine_power']
        self.max_torque = kwargs['max_torque']
        self.max_rpm = kwargs['max_rpm']
        self.max_speed = kwargs['max_speed']
        self.wheel_circumference = kwargs['wheel_circumference']
        self.friction_coefficient = kwargs['friction_coefficient']
        self.air_resistance_coefficient = kwargs['air_resistance_coefficient']
        self.power_curve = kwargs['power_curve']
        self.torque_curve = kwargs['torque_curve']
        if len(self.power_curve) < 2 or len(self.torque_curve) < 2:
            raise ValueError("Power and torque curves must have at least two points each")
        # Initialize vehicle based on type
        if self.is_electric:
            self.setup_electric_vehicle(kwargs)
        else:
            self.setup_ice_vehicle(kwargs)
        # Set up visuals
        self.set_up_visuals(kwargs)
        # Set up performance attributes
        self.setup_performance_attributes()
        # Set up additional attributes
        self.setup_additional_attributes(kwargs)
        # Set up trailer
        self.setup_trailer(kwargs)

    def setup_electric_vehicle(self, kwargs):
        self.max_motor_speed = kwargs['max_rpm']
        self.single_gear_ratio = kwargs['single_gear_ratio']
        self.battery_capacity = kwargs['battery_capacity']
        self.current_motor_speed = 0
        self.final_drive_ratio = 1
        self.current_rpm = 0
        self.current_gear = 1
        self.fuel_efficiency = float('inf')
        self.throttle = 0  # Set throttle to a non-zero value to ensure proper rendering of the throttle gauge at drawing.py
        
    def setup_ice_vehicle(self, kwargs):
        if self.is_electric:
            raise ValueError("Cannot setup ICE vehicle for an electric vehicle")
        self.shift_up_rpm = kwargs['shift_up_rpm']
        self.shift_down_rpm = kwargs['shift_down_rpm']
        self.gear_ratios = kwargs['gear_ratios']
        self.rev_drop_rate = kwargs.get('rev_drop_rate', 200)
        self.post_shift_adjustment_factor = kwargs.get('post_shift_adjustment_factor', 1.0)
        
        if not self.gear_ratios or len(self.gear_ratios) == 0:
            raise ValueError("gear_ratios must be provided and non-empty for ICE vehicles")
        
        self.gear_system = GearShiftingSystem(self, self.rev_drop_rate)
        print(f"Debug: gear_system initialized at {id(self.gear_system)}")

        self.final_drive_ratio = kwargs['final_drive_ratio']
        self.idle_rpm = kwargs['idle_rpm']
        self.current_rpm = self.idle_rpm
        self.current_gear = 1
        self.fuel_efficiency = kwargs['fuel_efficiency']
        self.emission_factor = kwargs['emission_factor']
        self.throttle = 0
        self.throttle_ramp = 1  # Add this line to initialize throttle_ramp
        self.throttle_ramp_duration = 1.0  # Duration of throttle ramp in seconds
        self.throttle_ramp_start_time = None
        self.is_idling = True

        
        # Initialize gear system attributes
        self.gear_system.clutch_engaged = True
        self.gear_system.shifting = False
        self.gear_system.throttle_ramp = 0
        self.post_shift_adjustment = False
        self.post_shift_adjustment_time = 0
        # emission factors
        self.speed_emission_coefficient = kwargs.get('speed_emission_coefficient', 0.2)
        self.min_gear_efficiency = kwargs.get('min_gear_efficiency', 0.7)
        self.throttle_efficiency_factor = kwargs.get('throttle_efficiency_factor', 0.4)
        self.base_engine_efficiency = kwargs.get('base_engine_efficiency', 0.35)      

        
    def set_up_visuals(self, kwargs):
        self.image_path = kwargs['image_path']
        print(f"Loading vehicle image from: {self.image_path}")
        try:
            self.image = pygame.image.load(self.image_path)
            self.image = self.image.convert_alpha()
            print(f"Vehicle image loaded successfully. Size: {self.image.get_size()}")
        except pygame.error:
            print(f"Failed to load vehicle image from {self.image_path}")
            self.image = pygame.Surface((100, 50))  # Create a default surface if image fails to load
            self.image.fill((255, 0, 0))  # Fill with red color
        self.rect = self.image.get_rect()
        print(f"Vehicle rect created with initial topleft: {self.rect.topleft}")
        self.height = self.rect.height  # Use the height of the loaded image
        self.position = list(kwargs['initial_position'])
        print(f"Vehicle position set to: {self.position}")
        self.rect.topleft = self.position
        print(f"Vehicle rect.topleft set to: {self.rect.topleft}")
        width, height = self.rect.size
        self.frontal_area = kwargs.get('frontal_area')
        self.is_truck = kwargs.get('is_truck', False)
        self.setup_wheels(kwargs)
    def setup_wheels(self, kwargs):
        if self.is_truck:
            self.front_wheel_image = pygame.image.load(kwargs['front_wheel_image_path']).convert_alpha()
            self.rear_wheel_image = pygame.image.load(kwargs['rear_wheel_image_path']).convert_alpha()
        else:
            self.wheel_image = pygame.image.load(kwargs['wheel_image_path']).convert_alpha()
        self.wheel_positions = kwargs['wheel_positions']
        self.wheel_size = kwargs['wheel_size']
        self.wheel_rotation = 0
    def setup_performance_attributes(self):
        # Set performance-related attributes
        self.speed = 0  # Current speed in meters per second
        self.visual_speed = 0  # Speed for visual representation (may be different from actual speed for smoother visuals)
        self.VISUAL_SPEED_FACTOR = 0.5
        self.acceleration = 0  # Current acceleration in meters per second squared it represents the rate of change of velocity over time, this is important for simulating realistic vehicle behavior.
                                # It is for easy integration with other physics calculations, such as force (F = ma) and kinematic equations.
        self.co2_emissions = 0  # Total CO2 emissions in kg - important for environmental impact
        self.distance_traveled = 0  # Total distance traveled in meters 
        self.time_elapsed = 0  # Total time elapsed in seconds 
        self.zero_to_hundred_time = None  # Time to accelerate from 0 to 100 km/h a common performance metric
        self.acceleration_timer = 0  # Timer for acceleration calculation 
        self.max_speed_acceleration_timer = 0  # Timer for 0 to max speed acceleration
        print("Performance attributes set up")
    def setup_additional_attributes(self, kwargs):
        # Set up additional attributes for the vehicle
        self.METERS_TO_PIXELS = 45  # Conversion factor from meters to pixels for translating real-world distances to screen ratios
        self.ROAD_MARK_CYCLE = 12 * self.METERS_TO_PIXELS  # Length of road marking in pixels for creating realistic road markings
        # I've set these RPM thresholds for gear shifting to optimize performance and stabilize the engine
        self.yellow_line = self.max_rpm * 0.8  # Threshold for high RPM range, optimal shift point, used to draw 
        self.red_line = self.max_rpm * 0.9  # Red line RPM threshold - danger level , very high RPM
        self.gear_shift_data = []  # List to store gear shift data - useful for analyzing shifting times and debuging
        self.last_gear_shift_time = 0  # Time of the last gear shift - helps in preventing too frequent shifting
        self.previous_gear = 1  # Previous gear. Very important to detect gear changes
        self.rpm_smoothing_factor = 0.1  # This factor smooths RPM changes,I've chosen it for creating the illusion of a rev drop without simulating mechanical engine parts like the flywheel. It makes RPM changes appear more natural and less abrupt.
        print("Additional attributes set up")
        #debug print
        self.last_debug_print_time = 0
        self.debug_print_interval = 1.0  # Print debug messages every 1 second
        self.simulation_start_time = time.time()

    def setup_trailer(self, kwargs):
        print("setup_trailer called")
        # Setting up trailer if it exists; trailers affect vehicle performance and visuals
        self.trailer = kwargs.get('trailer', None)
        if self.trailer:
            print("trailer is passed to the vehicle class successfully")
            # Store the initial offset of the trailer relative to the vehicle, important for positioning, I've had a lot of issues about trailer positioning due to absolute coordinates, setting up a relative position to semitruck was always more reliable
            self.trailer_offset_x = self.trailer.initial_position[0]
            self.trailer_absolute_y = self.trailer.initial_position[1]
            # Set the trailer's initial position based on the vehicle's position and the offset
            self.trailer.rect.topleft = (self.rect.topleft[0] + self.trailer_offset_x, 
                                        self.trailer_absolute_y)
            print(f"Trailer initial position set to: {self.trailer.rect.topleft}")
        else:
            if self.name == "Semi truck":
                print("!!!!Error: Trailer not passed to the Vehicle class during initialization.")
        self.update_total_mass()  # Update mass to include trailer too
        print(f"Total mass after trailer setup: {self.total_mass} kg")
        
    def update_total_mass(self):
        self.total_mass = self.mass
        if self.trailer:
            self.total_mass += self.trailer.mass
        print(f"Updated total_mass: {self.total_mass}")
        
    def is_debug_print_allowed(self):    # These methods help manage debug print frequency, preventing console spam
        current_time = pygame.time.get_ticks() / 1000  # Get current time in seconds
        if current_time - self.last_debug_print_time >= self.debug_print_interval:  # Check if debug interval has passed
            return True  # Allow debug print
        return False  # Prevent excessive debug prints
    
    def debug_print(self,message):
        current_time = time.time()
        elapsed_time = current_time - self.simulation_start_time
        timestamp = f"[{elapsed_time:.3f}s]"
        print(f"{timestamp} {message}")
    
    def reset_debug_print_timer(self):
        self.last_debug_print_time = pygame.time.get_ticks() / 1000  # Reset timer to control debug print frequency
    
    def start(self):
        if self.is_electric:
            self.current_rpm = 100  # Start at a low RPM for electric vehicles, This is important to not have 'motionless vehicle' bug when starting the game
            self.throttle  =  1 # full throttle for moving right away
        else:
            self.current_rpm = self.idle_rpm
            self.is_idling = False
            self.throttle = 1 
        print(f"Vehicle started. Current RPM: {self.current_rpm}")
        print(f"Debug: Total Mass: {self.total_mass:.2f} kg")
        if not self.is_electric:
            print(f"Debug: Gear ratios: {self.gear_ratios}")
        print(f"Debug: Final drive ratio: {self.final_drive_ratio}")
        
    def calculate_engine_force(self):
        print("calculate_engine_force is called")
        # Use the vehicle-specific power and torque curves
        power, torque = self.calculate_power_at_rpm(self.current_rpm)        
        # Apply throttle to torque
        torque *= self.throttle
        gear_ratio = self.gear_ratios[self.current_gear - 1]        
        # Calculate force based on torque, gear ratio, and wheel size
        force = (torque * gear_ratio * self.final_drive_ratio) / (self.wheel_circumference / 2)
        
        # Limit force to prevent exceeding engine's power output
        max_force = (power * 1000) / max(self.speed, 0.1)  # Convert kW to W
        force = min(force, max_force)
        
        # a low-speed power boost logic 
        boost_range = 0.2  # The range of boost (1.2 to 1.0)
        speed_range = 10  # The speed range over which boost decreases kmh
        boost = 1.2 - (self.speed * 3.6 * boost_range / speed_range)  # Convert speed to km/h
        boost = max(1.0, boost)  # Ensuring boost doesn't go below 1.0
        force *= boost
        
        return force
    def calculate_resistance_force(self):
        # I've included both rolling resistance and air resistance for more accurate simulation
        # Rolling resistance: F_r = u_r * m * g
        # where u_r is the rolling resistance coefficient, m is mass, and g is gravity (9.81)
        # Added speed dependency to rolling resistance for increased realism
        rolling_resistance = self.total_mass * GRAVITY * (self.friction_coefficient + self.speed * 0.0001)
        # Air resistance: F_a = 0.5 * rho * A * v^2
        # where rho is the density of air (1.225 kg/m^3) A is the frontal area, and v is the velocity
        # Frontal area is calculated using a rough formula for simplicity over realism.
        min_speed_for_air_resistance = 0.1  # m/s    
        air_resistance = 0.5 * AIR_DENSITY * self.air_resistance_coefficient * self.frontal_area * (max(self.speed, min_speed_for_air_resistance) ** 2)#prevent that air resistance is never zero when the car is not moving
        return rolling_resistance + air_resistance
    
    def rapid_rpm_adjustment(self, target_rpm, delta_time):
        return self.gear_system.rapid_rpm_adjustment(target_rpm, delta_time)
    
    def handle_gear_shifting(self, delta_time):
        return self.gear_system.handle_gear_shifting(delta_time)

    def find_optimal_gear(self, wheel_rpm, shifting_up):
        return self.gear_system.find_optimal_gear(wheel_rpm, shifting_up)
   
    def calculate_wheel_speed(self):
        print("debug: calculate wheel speed current rpm", self.current_rpm, "gear ratio", self.gear_ratios[self.current_gear - 1], "current gear", self.current_gear, "final drive", self.final_drive_ratio)
        return self.current_rpm / (self.gear_ratios[self.current_gear - 1] * self.final_drive_ratio)
    
    def calculate_rpm_for_gear(self, gear): # used in gear shifting class not here
        print("calcluate rpm for gear called with gear", gear)
        wheel_rps = self.calculate_wheel_speed()
        engine_rps = wheel_rps * self.gear_ratios[gear - 1] * self.final_drive_ratio
        rpm = engine_rps * 60
        print(f"Debug: calculate_rpm_for_gear - Wheel speed: {wheel_rps:.2f} m/s, Gear: {gear}, Wheel circ: {self.wheel_circumference:.4f} m")
        print(f"Debug: Wheel RPS: {wheel_rps/self.wheel_circumference:.2f}, Engine RPS: {wheel_rps/self.wheel_circumference*self.gear_ratios[gear-1]*self.final_drive_ratio:.2f}")
        print(f"Debug: Gear ratio: {self.gear_ratios[gear-1]:.4f}, Final drive: {self.final_drive_ratio:.4f}, RPM: {rpm:.2f}")
        print(f"Debug: Calculated - Wheel RPS: {wheel_rps:.2f}, Engine RPS: {engine_rps:.2f}, RPM: {rpm:.2f}")
        return rpm

    def start_shift_up(self, target_gear):
        return self.gear_system.start_shift_up(target_gear)
    
    def start_shift_down(self, target_gear):
        return self.gear_system.start_shift_down(target_gear)

    def update_rpm_during_shift(self, delta_time):
        return self.gear_system.update_rpm_during_shift(delta_time)

    def complete_gear_shift(self):
        return self.gear_system.complete_gear_shift()
    
    def update_throttle_ramp(self, delta_time):
        if self.post_shift_adjustment:
            old_throttle = self.throttle
            duration = self.calculate_post_shift_duration()
            throttle_increase = (1 / duration) * delta_time
            self.throttle = min(1, self.throttle + throttle_increase)
            self.post_shift_adjustment_time += delta_time
            
            if old_throttle != self.throttle:
                print(f"Debug: Throttle updated from {old_throttle:.2f} to {self.throttle:.2f}")
            
            if self.post_shift_adjustment_time >= duration:
                self.post_shift_adjustment = False
                self.post_shift_adjustment_time = 0
                print(f"Debug: Post-shift throttle adjustment completed after {duration:.2f} seconds")
                
    def calculate_post_shift_duration(self):
        print("REV DROP RATE is going to be used to calculate post shift duration")
        # Base duration inversely proportional to rev_drop_rate, normalized to 1 second at 682 rev/s
        base_duration = 682 / self.rev_drop_rate    # Apply the adjustment factor
        duration = base_duration * self.post_shift_adjustment_factor        
        return max(0.1, min(duration, 2.0)) # Clamp the duration between 0.1 and 2.0 seconds
    
    def calculate_emissions(self, delta_time):
        # This emissions calculation simulates a worst-case scenario with full-throttle
        # acceleration, not typical driving conditions. It's a simplified educational
        # model demonstrating maximum potential emissions under extreme laboratory-like
        # conditions, resulting in much higher values than normal driving would produce.
        if self.is_electric:
            return 0
        else:
            # RPM factor
            rpm_factor = min(1.0, self.current_rpm / self.max_rpm)
            rpm_coefficient = 1 + 0.2 * (1 - rpm_factor)  # Further reduced from 0.3 to 0.2

            # Speed factor (unchanged)
            speed_factor = 1 + self.speed_emission_coefficient * (self.speed / 100) ** 2

            # Gear efficiency (adjusted)
            total_gears = len(self.gear_ratios)
            gear_factor = self.current_gear / total_gears
            gear_efficiency = 0.85 + 0.15 * gear_factor  

            # Fuel efficiency (adjusted)
            full_throttle_efficiency = self.fuel_efficiency * 0.7  

            # Fuel consumption
            distance_km = self.speed * delta_time / 3600  # Convert to km
            base_fuel_consumption = distance_km / (full_throttle_efficiency / 100)
            adjusted_fuel_consumption = base_fuel_consumption * speed_factor * rpm_coefficient / gear_efficiency

            # Emission factor (adjusted)
            engine_efficiency = max(0.3, self.base_engine_efficiency * gear_efficiency)  # Increased minimum efficiency
            adjusted_emission_factor = self.emission_factor / engine_efficiency * 1.02  

            # Emissions
            emissions = adjusted_fuel_consumption * adjusted_emission_factor / 1000  # Convert g to kg
            return emissions  # kg CO2
        
        
    def speed_debug(self): # For electric vehicles, we display some debug info
        if self.is_electric:
            print(f"Speed: {self.speed * 3.6:.1f} km/h, Motor Speed: {self.current_rpm:.0f} RPM, "
                  f"Battery: {self.battery_capacity:.1f} kWh")
            
        if not self.is_electric: # Debug prints For non-electric vehicles
        
            engine_force = self.calculate_engine_force()
            resistance_force = self.calculate_resistance_force() # Stores result for debug printing and force calculations
            net_force = engine_force - resistance_force
            #print(f"Debug: Total Mass: {self.total_mass:.2f} kg")
            print(f"Debug: Engine Force: {engine_force:.2f} N, Resistance: {resistance_force:.2f} N, Net Force: {net_force:.2f} N")
            print(f"Debug: Acceleration: {self.acceleration:.2f} m/s^2, Current Gear: {self.current_gear if not self.is_electric else 'N/A'}")
            print(f"Debug: Speed: {self.speed * 3.6:.2f} km/h")
            #print(f"Debug: Position: {self.position[0]:.2f}")
            print(f"RPM: {self.current_rpm:.2f}, Throttle: {self.throttle:.2f}, Idling: {self.is_idling if not self.is_electric else 'N/A'},Clutch Engaged: {self.gear_system.clutch_engaged}")
            
    def update_rpm(self, delta_time, throttle):
        wheel_rps = self.speed / self.wheel_circumference  # Calculate wheel revolutions per second
        target_rpm = wheel_rps * self.gear_ratios[self.current_gear - 1] * self.final_drive_ratio * 60  # target RPM based on wheel speed and gear ratios
        
        if self.shifting or not self.clutch_engaged:
            # Rapid RPM drop during shifting or when clutch is disengaged
            rpm_fall_rate = 500  # RPM fall per second
            rpm_drop = rpm_fall_rate * delta_time
            self.current_rpm = max(self.idle_rpm, self.current_rpm - rpm_drop)
        else:
            # Gradual adjustment towards calculated RPM
            self.current_rpm = target_rpm

        # Apply a small throttle effect for more dynamic behavior
        throttle_effect = 1 + (throttle - 0.5) * 0.1  # 10% variation based on throttle
        self.current_rpm *= throttle_effect

        # Keep RPM between idle_rpm and max_rpm
        self.current_rpm = max(self.idle_rpm, min(self.current_rpm, self.max_rpm))

        print(f"Speed: {self.speed * 3.6:.2f}, gear {self.current_gear}, GR {self.gear_ratios[self.current_gear - 1]:.2f}, CurRPM: {self.current_rpm:.2f}, TgtRPM: {target_rpm:.2f}, Shifting: {self.shifting}, Clutch: {self.clutch_engaged}")


    def update(self, delta_time):
        if not self.is_electric:
            pass
        # Update position
        previous_position = self.rect.x
        previous_speed = self.speed
        self.update_total_mass()
        if self.is_electric:
            self.update_electric(delta_time)
        else:
            self.update_ice(delta_time)

        # Calculate resistance force using the existing method
        resistance_force = self.calculate_resistance_force()
        # Calculate net force
        net_force = self.wheel_force - resistance_force
        # Apply traction limit
        static_friction_coefficient = 0.8  # Typical value for rubber on dry asphalt
        max_traction_force = static_friction_coefficient * self.total_mass * 9.81

        if abs(net_force) > max_traction_force:
            
            net_force = max_traction_force if net_force > 0 else -max_traction_force

        # Calculate acceleration (F = ma)
        self.acceleration = net_force / self.total_mass
        print(f"Net force: {net_force:.2f} N / Total mass: {self.total_mass:.2f} kg = Acceleration: {self.acceleration:.2f} m/s^2")
        # User-friendly debug print for incoherent acceleration cases
        if self.acceleration > 0 and self.wheel_force <= resistance_force:
            print("!!! Unexpected Behavior: The vehicle is accelerating forward even though the engine isn't producing enough force to overcome resistance. This might be a calculation error.")
        elif self.acceleration < 0 and self.wheel_force >= resistance_force:
            print("!!! Unexpected Behavior: The vehicle is slowing down even though the engine is producing more force than the resistance. This might be a calculation error.")
        elif abs(self.acceleration) > 10:  # Unrealistic acceleration
            print(f"!!! Unusual Acceleration: The vehicle is experiencing very high acceleration ({self.acceleration:.2f} m/s^2). This might be unrealistic for a typical vehicle.")
        # Note for me : Check the values of self.acceleration, self.wheel_force, and resistance_force
        # in the debug prints above to identify any inconsistencies in the physics calculations.
        # Update speed (in m/s)
        self.speed += self.acceleration * delta_time        
        self.speed = max(0, self.speed)  # Ensure speed doesn't go negative
        # Update position
        self.position[0] += self.speed * delta_time
        self.rect.x = int(self.position[0])
        position_change = self.rect.x - previous_position
        # Update other metrics
        self.distance_traveled += self.speed * delta_time
        self.time_elapsed += delta_time
        if not self.is_electric:
            self.co2_emissions += self.calculate_emissions(delta_time)
            self.is_idling = self.speed < 0.1 and self.current_rpm <= self.idle_rpm + 50

        # Update performance metrics
        self.update_performance_metrics(delta_time)
        # Update visual elements
        self.update_visual_elements(delta_time, position_change)
        
        if self.is_debug_print_allowed():
            self.debug_print(f"Debug: WheelF: {self.wheel_force:.2f}N - ResistF: {resistance_force:.2f}N = NetF: {net_force:.2f}N, Accel: {self.acceleration:.4f}m/s^2, RPM: {self.current_rpm:.2f}, Speed: {self.speed*3.6:.2f}km/h, Mass: {self.total_mass:}kg")
            self.reset_debug_print_timer()
        print(f"NetF: {net_force:.2f}N,", "speed", f"{self.speed * 3.6:.2f} km/h")
        if net_force < 0 and not self.gear_system.shifting == True and self.throttle == 1 :
            print("//////////////////////////////////////////////////////") 
            print ("CRITICAL WARNING , NET FORCE IS NEGATIVE !! ") 
            #The engine force can not be lower than the resistance force in not shifting case
            print("//////////////////////////////////////////////////////")            
            
    def update_electric(self, delta_time):
        self.wheel_force = self.calculate_motor_force()
        
        # Update motor speed (RPM)
        wheel_rps = self.speed / self.wheel_circumference
        self.current_rpm = wheel_rps * self.single_gear_ratio * 60
        self.current_rpm = min(self.current_rpm, self.max_rpm)
        if self.current_rpm >= 19500:
            self.current_rpm -= random.uniform(0, 500) #random RPM drop to simulate aero drag
        
        if self.is_debug_print_allowed():
            self.debug_print(f"Debug Electric: Speed: {self.speed * 3.6:.2f} km/h, Motor RPM: {self.current_rpm:.2f}")
            self.reset_debug_print_timer()

    def update_ice(self, delta_time):
        self.gear_system.handle_gear_shifting(delta_time)
        # Update throttle only if in post-shift adjustment period
        if self.post_shift_adjustment:
            self.update_throttle_ramp(delta_time)
    
        # Calculate target RPM based on current speed and gear ratio
        wheel_rps = self.speed / self.wheel_circumference
        target_rpm = wheel_rps * self.gear_ratios[self.current_gear - 1] * self.final_drive_ratio * 60
        if self.gear_system.shifting or not self.gear_system.clutch_engaged:
            # During shifting, gradually decrease RPM
            rpm_fall_rate = 1000  # RPM fall per second
            rpm_drop = rpm_fall_rate * delta_time
            self.current_rpm = max(self.idle_rpm, self.current_rpm - rpm_drop)
            engine_torque = 0
            engine_power = 0
        else:
            # Gradually adjust current RPM towards target RPM
            rpm_difference = target_rpm - self.current_rpm
            adjustment_factor = 0.8  # Adjust this value to control how quickly RPM changes
            self.current_rpm += rpm_difference * adjustment_factor
            self.current_rpm = max(self.idle_rpm, min(self.current_rpm, self.max_rpm))
            engine_torque = self.estimate_engine_output(self.current_rpm, self.torque_curve) #only calculated when not shifting
            engine_power = self.estimate_engine_output(self.current_rpm, self.power_curve)
            print("update ice engine_power is set to", engine_power)

        # Apply throttle directly to engine torque
        engine_torque *= self.throttle
        
        # Calculate wheel torque using gear ratios
        total_gear_ratio = self.gear_ratios[self.current_gear - 1] * self.final_drive_ratio
        wheel_torque = engine_torque * total_gear_ratio * 0.9  # Assuming 90% drivetrain efficiency
        print("drivetrain efficiency is implemented as 90%")
        print("update ice calculated  wheel_torque", wheel_torque)
        # Calculate wheel force
        wheel_radius = self.wheel_circumference / (2 * math.pi)
        self.wheel_force = wheel_torque / wheel_radius
        print("update ice calculated wheel_force", self.wheel_force)
        
        # Limit wheel force based on theoretical power limits based in config.py
        max_force = (engine_power * 1000) / max(self.speed, 0.1)
        self.wheel_force = min(self.wheel_force, max_force)
        print(f"Debug: Engine theoretical Power: {engine_power:.2f} kW, Speed: {self.speed * 3.6:.2f} km/h, Max Force: {max_force:.2f} N")
        print("debug:update_ice wheel_force", self.wheel_force, "= wheel_torque", wheel_torque, "/ wheel_radius", wheel_radius)
        print(f"Debug ICE: Speed: {self.speed*3.6:.2f}km/h, RPM: {self.current_rpm:.2f}, Gear: {self.current_gear}, Throttle: {self.throttle:.2f}, Shifting: {self.gear_system.shifting}, Clutch: {self.gear_system.clutch_engaged}")
            
    def update_performance_metrics(self, delta_time):
        if self.speed < 100 / 3.6:
            self.acceleration_timer += delta_time
        elif self.zero_to_hundred_time is None:
            self.zero_to_hundred_time = self.acceleration_timer

        if self.speed < self.max_speed / 3.6:
            self.max_speed_acceleration_timer += delta_time
        elif not hasattr(self, 'zero_to_max_speed_time'):
            self.zero_to_max_speed_time = self.max_speed_acceleration_timer

    def update_visual_elements(self, delta_time, position_change):
        # Calculate the actual distance traveled in meters
        distance_traveled = self.speed * delta_time
        # Apply visual speed factor to get the visual distance traveled
        visual_distance = distance_traveled * self.VISUAL_SPEED_FACTOR
        # Convert visual distance to pixels
        pixels_moved = visual_distance * self.METERS_TO_PIXELS
        # Calculate wheel rotation based on visual pixels moved
        wheel_circumference_pixels = self.wheel_circumference * self.METERS_TO_PIXELS
        rotation_amount = (pixels_moved / wheel_circumference_pixels) * 360
        self.wheel_rotation += rotation_amount        
        self.wheel_rotation %= 360
        if self.is_truck and hasattr(self, 'trailer'):
            self.trailer.rect.x += position_change
            self.trailer.update_wheel_rotation(delta_time, self.speed, self.wheel_circumference, self.VISUAL_SPEED_FACTOR, self.METERS_TO_PIXELS)

    def get_speed_kmh(self): # This method provides the vehicle's speed in a more familiar unit (km/h) for display purposes
        return self.speed * 3.6  # Convert m/s to km/h

    def calculate_motor_force(self):
        if not self.is_electric:
            return 0
        
        wheel_rps = self.speed / self.wheel_circumference
        self.current_rpm = wheel_rps * self.single_gear_ratio * 60
        
        current_torque = self.estimate_engine_output(self.current_rpm, self.torque_curve)
        current_power = self.estimate_engine_output(self.current_rpm, self.power_curve) * 1000  # kW to W
        
        if self.speed < 1:  # Use torque-based calculation for low speeds
            force = (current_torque * self.single_gear_ratio) / (self.wheel_circumference / 2)
        else:  # Use power-based calculation for higher speeds
            force = current_power / max(self.speed, 0.1)  # Prevent division by zero
        
        force *= self.throttle
        
        resistance = self.calculate_resistance_force()
        
        # Debug output (unchanged)
        
        return force
    def get_performance_indicators(self): #This method provides a list of performance indicators,
        # different for electric and petrol engines. useful for displaying performance data to the user
        indicators = []
        if self.is_electric:
            # For electric vehicles, we'll just show the current speed and motor RPM
            current_speed = self.speed * 3.6  # Convert to km/h
            indicators.append(f"Speed: {current_speed:.1f} km/h")
            indicators.append(f"Motor Speed: {self.current_rpm:.0f} RPM")
        else:
            # For non-electric vehicles, show gear shift data
            for i, (gear, time, speed) in enumerate(self.gear_shift_data):  # Iterate through gear shift data
                if time > 0:  # Check if shift time is greater than zero
                    indicators.append(f"Gear {gear}: {time:.2f}s ({speed:.1f} km/h)")  # Add formatted string to indicators
        
        return indicators  # Return the list of performance indicators
    def draw(self, screen, height):
        screen.blit(self.image, self.rect)  # Draw the main vehicle image on the screen

        def draw_wheel(wheel_image, pos):
            # Use smoothscale for better quality scaling
            scaled_wheel = pygame.transform.smoothscale(wheel_image, self.wheel_size)  # Scale the wheel image for better quality
            rotated_wheel = pygame.transform.rotate(scaled_wheel, -self.wheel_rotation)  # Rotate the wheel based on vehicle movement
            wheel_x = self.rect.x + pos[0]  # Calculate x-position of the wheel
            wheel_y = self.rect.y + pos[1]  # Calculate y-position of the wheel
            wheel_rect = rotated_wheel.get_rect(center=(wheel_x, wheel_y))  # Create a rectangle for the wheel
            screen.blit(rotated_wheel, wheel_rect)  # Draw the wheel on the screen
        if self.is_truck:
            for i, pos in enumerate(self.wheel_positions):
                wheel_image = self.front_wheel_image if i == 0 else self.rear_wheel_image  # Choose front or rear wheel image
                draw_wheel(wheel_image, pos)  # Draw each wheel for the truck
        else:
            for pos in self.wheel_positions:
                draw_wheel(self.wheel_image, pos)  # Draw each wheel for non-truck vehicles

        # Draw the trailer if it exists and the vehicle is a truck
        if self.is_truck and hasattr(self, 'trailer') and self.trailer is not None:
            self.trailer.draw(screen)
    def get_distance_km(self): #returns the total distance traveled in kilometers
        return self.distance_traveled / 1000

    def get_emissions_kg(self): #returns the total CO2 emissions in kg
        return self.co2_emissions

    def get_zero_to_hundred_time(self): # returns the time taken to accelerate from 0 to 100 km/h
        return self.zero_to_hundred_time if self.zero_to_hundred_time is not None else "N/A"
    
    def record_gear_shift_time(self): # records the time spent in each gear and the speed at which shifts occur
   
         if not self.is_electric and self.current_gear != self.previous_gear: # only for non-electric vehicles
            current_speed = self.speed * 3.6  # Convert to km/h
            gear_time = self.time_elapsed - self.gear_start_times[self.previous_gear - 1] # time elapsed from the start of the previous gear to the current gear
            
            for i, (gear, _, _) in enumerate(self.gear_shift_data): # Iterates through existing data, updates if gear exists, or appends new entry
                if gear == self.previous_gear:
                    self.gear_shift_data[i] = (self.previous_gear, gear_time, current_speed)
                    break
            else:
                self.gear_shift_data.append((self.previous_gear, gear_time, current_speed)) # Appends a new tuple to the list if the gear is not found in existing data
            
            # Set the start time for the new gear
            self.gear_start_times[self.current_gear - 1] = self.time_elapsed
            self.gear_start_speeds[self.current_gear - 1] = self.speed
            self.previous_gear = self.current_gear

    def estimate_engine_output(self, x, curve):
        # This function helps us estimate values between known points on a power curve.
        # A power curve represents how an engine's power output changes with RPM. 
        # It's important for understanding engine performance characteristics.
        # Typically, power increases with RPM up to a peak, then drops off.
        # This function interpolates between known points to estimate power or torque at any RPM,
        # allowing for a more realistic simulation of engine behavior across its entire RPM range.
        # The math here performs linear interpolation between two adjacent known points on the curve.
        # Sort the curve points by RPM (x-value) to ensure they're in order
        sorted_curve = sorted(curve, key=lambda point: point[0])# Sort the curve points by RPM (first element of each pair)
        # This line arranges the curve data in order of increasing RPM values
        rpms = [point[0] for point in sorted_curve] # Extract RPM values from sorted curve
        values = [point[1] for point in sorted_curve] # Extract power/torque values from sorted curve
        if x <= rpms[0]:# If RPM is below or equal to the lowest rpm, return the corresponding value
            return values[0]
        if x >= rpms[-1]:# If RPM is above or equal to the highest rpm, return the corresponding value
            return values[-1]
        
        
        i = bisect.bisect_right(rpms, x) # Find the index where x would be inserted in the sorted list of RPMs
        x0, y0 = sorted_curve[i-1]  # Retrieve the lower bounding point (x0, y0) from the sorted curve
        x1, y1 = sorted_curve[i]    # Retrieve the upper bounding point (x1, y1) for estimation between points
        
        return y0 + (y1 - y0) * (x - x0) / (x1 - x0)  # Interpolate between the two points to estimate the value at x

    def calculate_power_at_rpm(self, rpm):# This method uses the estimate_engine_output method to interpolate values from the power and torque curves
        if self.is_electric:
            return self.calculate_power_and_torque(rpm)  # For electric vehicles, use other  method
        else:
            power = self.estimate_engine_output(rpm, self.power_curve)  # Estimate power for ICE
            torque = self.estimate_engine_output(rpm, self.torque_curve)  # Estimate torque for ICE
            return power, torque  # Return estimated power and torque
    def update_total_mass(self):
        self.total_mass = self.mass
        if self.trailer:
            self.total_mass += self.trailer.mass
    # End of Vehicle class definition# Note: Additional helper functions or related classes could be added below if needed in the future.
   