# gear_shifting.py
import pygame
from datetime import datetime

class GearShiftingSystem:
    def __init__(self, vehicle, rev_drop_rate):
        self.rev_drop_rate = rev_drop_rate
        self.vehicle = vehicle
        self.gear_ratios = vehicle.gear_ratios  
        self._shifting = False
        self.next_gear = None
        self.shift_cooldown = 0.4
        self.last_shift_time = 0
        self.shift_start_rpm = None
        self.shift_target_rpm = None
        self._clutch_position = 1  # Fully engaged
        self._clutch_engaged = True
        self.rpm_drop_rate = 1000
        self.gear_start_times = [0] * len(self.gear_ratios)
        self.gear_shift_times = [0] * len(self.gear_ratios)
        self.gear_start_speeds = [0] * (len(self.gear_ratios) + 1)
        self.gear_stats = []
        self.gear_stats = [{'time_spent': 0, 'distance_traveled': 0, 'max_speed': 0} for _ in range(len(self.gear_ratios))]
        self.gear_start_time = None
        self.gear_max_speed = 0
        self.throttle = 1
        self.throttle_ramp = 0
        self.shift_progress = 0

        
    @property
    def shifting(self):
        return self._shifting

    @shifting.setter
    def shifting(self, value):
        print(f"Debug: shifting state changed from {self._shifting} to {value}")
        self._shifting = value

    @property
    def clutch_position(self):
        return self._clutch_position

    @clutch_position.setter
    def clutch_position(self, value):
        self._clutch_position = value
        self._clutch_engaged = (value == 1)

    @property
    def clutch_engaged(self):
        return self._clutch_engaged

    @clutch_engaged.setter
    def clutch_engaged(self, value):
        self._clutch_engaged = value
        self._clutch_position = 1 if value else 0
        
    def handle_gear_shifting(self, delta_time):
        if self.vehicle.is_electric:
            return # Electric cars don't change gears like normal cars.

        current_time = pygame.time.get_ticks() / 1000
        
        # Update throttle ramp
        self.vehicle.update_throttle_ramp(delta_time)

        # Check if we're currently shifting gears
        if self.shifting:
            if self.shift_start_rpm is None:
                self.shift_start_rpm = self.vehicle.current_rpm
                self.shift_target_rpm = self.calculate_target_rpm()
                print(f"Debug: Calculated new target RPM: {self.shift_target_rpm}")
                
            rpm_drop = self.rev_drop_rate * delta_time
            self.vehicle.current_rpm = max(self.shift_target_rpm, self.vehicle.current_rpm - rpm_drop)
            
            rpm_difference = self.shift_target_rpm - self.vehicle.current_rpm
            rpm_tolerance = 50  # Adjust this value as needed
            print(f"Debug: Shifting in progress. Current RPM: {self.vehicle.current_rpm:.2f}, Target RPM: {self.shift_target_rpm:.2f}")
            print(f"Debug: RPM difference: {rpm_difference:.2f}, Tolerance: {rpm_tolerance}")
            
            if abs(rpm_difference) <= rpm_tolerance:
                target_rpm = self.shift_target_rpm  # Store the target RPM before completing the shift
                self.complete_gear_shift()
                print(f"Debug: Gear shift completed. Current RPM: {self.vehicle.current_rpm:.2f}, Final Target RPM: {target_rpm:.2f}")
        else:
            self.clutch_position = 1
            self.clutch_engaged = True
            if current_time - self.last_shift_time < self.shift_cooldown:
                print(f"Debug: Shift cooldown active. Time since last shift: {current_time - self.last_shift_time:.2f}s")
                return  # Still in cooldown, don't shift
            
            wheel_rpm = (self.vehicle.speed / self.vehicle.wheel_circumference) * 60 # Calculate current wheel RPM
            
            # Main logic for shifting based on shift_up_rpm and shift_down_rpm
            shifting_up = self.vehicle.current_rpm > self.vehicle.shift_up_rpm 
            shifting_down = self.vehicle.current_rpm < self.vehicle.shift_down_rpm
            
            if shifting_up or shifting_down:
                print(f"Debug: Shifting up: {shifting_up}, Shifting down: {shifting_down}")
                target_gear = self.find_optimal_gear(wheel_rpm, shifting_up)
                print(f"Debug: Target gear found: {target_gear}")
            
                if target_gear != self.vehicle.current_gear:
                    if shifting_up:
                        print(f"Debug: Calling start_shift_up with target_gear: {target_gear}")
                        self.start_shift_up(target_gear)
                    else:
                        self.start_shift_down(target_gear)
                        
    def find_optimal_gear(self, wheel_rpm, shifting_up):
        optimal_gear = self.vehicle.current_gear
        print(f"Debug: Finding optimal gear. Current gear: {optimal_gear}, Wheel RPM: {wheel_rpm:.2f}, Shifting up: {shifting_up}")
        
        if shifting_up:
            target_rpm = self.vehicle.shift_up_rpm - 500  # Subtract 500 to ensure it's worth shifting
            gear_range = range(self.vehicle.current_gear + 1, len(self.gear_ratios) + 1)
            
        
        else:
            target_rpm = self.vehicle.shift_down_rpm + 500  # Add 500 for downshifting
            gear_range = range(self.vehicle.current_gear - 1, 0, -1)
        
        
        for gear in gear_range:
            print(f"find optimal gear checking the gear: {gear}")
            print(f"gear ratio for gear {gear} is {self.gear_ratios[gear - 1]}")
            gear_rpm = wheel_rpm * self.gear_ratios[gear - 1] * self.vehicle.final_drive_ratio
            print(f"Debug: Checking gear {gear}. Gear RPM: {gear_rpm:.2f}, Target RPM: {target_rpm:.2f}")
            print(f"Debug: Gear {gear} - Ratio: {self.gear_ratios[gear - 1]:.2f}, Resulting Engine RPM: {gear_rpm:.2f}")
            
            if shifting_up and gear_rpm < target_rpm:
                optimal_gear = gear
                print(f"Debug: Found better gear: {optimal_gear}")
                break  # Stop searching once we find a suitable gear
            elif not shifting_up and gear_rpm > target_rpm:
                optimal_gear = gear
                print(f"Debug: Found better gear: {optimal_gear}")
                break  # Stop searching once we find a suitable gear
            else:
                print(f"Debug: Gear {gear} not suitable, continuing search")
        
        print(f"Debug: Optimal gear selected: {optimal_gear}")
        return optimal_gear
    
        
    def calculate_target_rpm(self, gear):
        wheel_rps = self.vehicle.speed / self.vehicle.wheel_circumference
        gear_ratio = self.gear_ratios[gear - 1]
        target_rpm = wheel_rps * gear_ratio * self.vehicle.final_drive_ratio * 60
        
        # Ensure the target RPM is within a realistic range
        min_rpm = self.vehicle.idle_rpm
        max_rpm = self.vehicle.max_rpm
        target_rpm = max(min_rpm, min(target_rpm, max_rpm))
        
        print(f"Debug: calculate_target_rpm - Speed: {self.vehicle.speed:.2f} km/h, Wheel RPS: {wheel_rps:.2f}, Target gear: {gear}, Target RPM: {target_rpm:.2f}")
        return target_rpm

    def start_shift_up(self, target_gear):
        print(f"Debug: start_shift_up called with target_gear: {target_gear}")
        print(f"Debug: Shift up initiated. Current gear: {self.vehicle.current_gear}, Next gear: {self.next_gear}")
        print(f"Debug: Shifting state before: {self.shifting}")
    
        if target_gear is None:
            print("Error: target_gear is None. Aborting shift.")
            return
        
        if target_gear <= self.vehicle.current_gear or target_gear > len(self.vehicle.gear_ratios):
            print(f"Invalid upshift to gear {target_gear}. Current gear: {self.vehicle.current_gear}")
            return
        if not self.shifting:
            print("self shifting was detected as false inside start shift up")
            self.shifting = True
            print(f"Debug: Shift up initiated. Shifting state set to True")
            self.shift_progress = 0
            self.clutch_engaged = False
            self.clutch_position = 0  # Fully disengaged
            self.next_gear = target_gear
            self.shift_start_rpm = self.vehicle.current_rpm
            self.shift_target_rpm = self.calculate_target_rpm(target_gear)
            print(f"Debug: start_shift_up - Speed: {self.vehicle.speed:.2f} km/h, Target gear: {target_gear}")
            print(f"Debug: Shift start RPM: {self.shift_start_rpm:.2f}, Shift target RPM: {self.shift_target_rpm:.2f}")

            print(f"Debug: Starting shift up from gear {self.vehicle.current_gear} to {self.next_gear}")
            print(f"Debug: Shifting state after: {self.shifting}")
    
    def start_shift_down(self, target_gear):
        if target_gear is None or target_gear < 1 or target_gear > len(self.gear_ratios):
            print(f"Invalid target gear for downshift: {target_gear}. Current gear: {self.vehicle.current_gear}")
            return
        if not self.shifting: 
            self.shifting = True
            self.shift_progress = 0
            self.next_gear = target_gear
            self.clutch_engaged = False
            self.shift_start_rpm = self.vehicle.current_rpm
            wheel_speed = self.vehicle.calculate_wheel_speed()
            self.shift_target_rpm = self.vehicle.calculate_rpm_for_gear(wheel_speed, target_gear)        

    def complete_gear_shift(self): # final step of the gear shifting process, needed for the shifting process to work
        print("complete_gear_shift is called")
            
        old_gear = self.vehicle.current_gear
        self.vehicle.current_gear = self.next_gear
        # Calculate new RPM based on current speed and new gear ratio
        wheel_rps = self.vehicle.speed / self.vehicle.wheel_circumference
        new_rpm = wheel_rps * self.gear_ratios[self.vehicle.current_gear - 1] * self.vehicle.final_drive_ratio * 60
        
        print(f"Debug: Old Gear: {old_gear}, Old RPM: {self.vehicle.current_rpm:.2f}")
        print(f"Debug: New Gear: {self.vehicle.current_gear}, New RPM: {new_rpm:.2f}")
        
        self.vehicle.current_rpm = new_rpm
        self.shifting = False  # Set the shifting process as complete
        self.clutch_engaged = True  # Re-engage the clutch after shifting (as if releasing the pedal)
        self.clutch_position = 1  # Ensure clutch is fully engaged
        self.last_shift_time = pygame.time.get_ticks() / 1000
        self.shift_start_rpm = None
        self.shift_target_rpm = None
        self.next_gear = None
        print(f"Debug: Shift completed. Current Gear: {self.vehicle.current_gear}, RPM: {self.vehicle.current_rpm:.2f}")
        self.throttle_ramp = 0  # Reset throttle ramp
        self.vehicle.throttle = 0.1    
        self.vehicle.post_shift_adjustment = True
        duration = self.vehicle.calculate_post_shift_duration()
        self.vehicle.post_shift_adjustment_time = 0
        print(f"Debug: Shift completed. Current Gear: {self.vehicle.current_gear}, RPM: {self.vehicle.current_rpm:.2f}")
        print(f"Debug: Post-shift throttle adjustment started, duration: {duration:.2f}s")
    def record_gear_shift_time(self): # records the time spent in each gear and the speed at which shifts occur
   
         if not self.vehicle.is_electric and self.vehicle.current_gear != self.vehicle.previous_gear: # only for non-electric vehicles
            current_speed = self.vehicle.speed * 3.6  # Convert to km/h
            gear_time = self.vehicle.time_elapsed - self.gear_start_times[self.vehicle.previous_gear - 1] # time elapsed from the start of the previous gear to the current gear
            
            for i, (gear, _, _) in enumerate(self.vehicle.gear_shift_data): # Iterates through existing data, updates if gear exists, or appends new entry
                if gear == self.vehicle.previous_gear:
                    self.vehicle.gear_shift_data[i] = (self.vehicle.previous_gear, gear_time, current_speed)
                    break
            else:
                self.vehicle.gear_shift_data.append((self.vehicle.previous_gear, gear_time, current_speed))
            
            # Set the start time for the new gear
            self.gear_start_times[self.vehicle.current_gear - 1] = self.vehicle.time_elapsed
            self.gear_start_speeds[self.vehicle.current_gear - 1] = self.vehicle.speed
            self.vehicle.previous_gear = self.vehicle.current_gear          
