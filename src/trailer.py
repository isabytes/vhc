import pygame

class Trailer:
    def __init__(self, **config):
        # Get trailer details from config
        self.image_path = config['image_path']
        self.wheel_image_path = config['wheel_image_path']
        self.wheel_positions = config['wheel_positions']
        self.wheel_size = config['wheel_size']
        self.mass = float(config['mass'])
        if self.mass <= 0:
            self.mass = 1000  # Use default weight if invalid
        self.wheel_rotation = 0
        
        print(f"Making trailer with: {config}")
        
        self.initial_position = config['initial_position']
        # Load trailer picture
        self.image = pygame.image.load(self.image_path).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.topleft = self.initial_position
        print(f"Trailer starts at: {self.initial_position}")
        print(f"Trailer is at: {self.rect.topleft}")
        
        # Load wheel picture
        self.wheel_image = pygame.image.load(self.wheel_image_path).convert_alpha()

        # Start wheel rotation at 0
        self.wheel_rotation = 0
        
    def update_wheel_rotation(self, delta_time, speed, wheel_circumference, VISUAL_SPEED_FACTOR, METERS_TO_PIXELS):
        # Calculate how much to rotate wheels
        distance_traveled = speed * delta_time
        # Apply visual speed factor to get the visual distance traveled
        visual_distance = distance_traveled * VISUAL_SPEED_FACTOR
        # Convert visual distance to pixels
        pixels_moved = visual_distance * METERS_TO_PIXELS
        wheel_circumference_pixels = wheel_circumference * METERS_TO_PIXELS
        rotation_amount = (pixels_moved / wheel_circumference_pixels) * 360
        self.wheel_rotation += rotation_amount
        self.wheel_rotation = self.wheel_rotation % 360  # Keep rotation between 0 and 360
       
    def draw(self, screen):
        # Draw trailer
        screen.blit(self.image, self.rect.topleft)
        
        # Draw wheels
        for pos in self.wheel_positions:
            # Make wheel the right size
            scaled_wheel = pygame.transform.smoothscale(self.wheel_image, self.wheel_size)
            # Rotate wheel
            rotated_wheel = pygame.transform.rotate(scaled_wheel, -self.wheel_rotation)
            # Find where to put wheel
            wheel_x = self.rect.x + pos[0]
            wheel_y = self.rect.y + pos[1]
            wheel_rect = rotated_wheel.get_rect(center=(wheel_x, wheel_y))
            # Draw wheel
            screen.blit(rotated_wheel, wheel_rect)
