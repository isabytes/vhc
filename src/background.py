import pygame
import random
import numpy as np
import vehicle

class Background:
    def __init__(self, width, height, meters_to_pixels, visual_speed_factor):
        self.width = width
        self.height = height
        self.sky_color = (158, 206, 235)  # Soft blue sky
        self.ground_color = (95, 141, 78)  # Muted green
        self.road_color = (120, 120, 120)  # Soft gray for road
        self.mountain_color = (131, 149, 167)  # Soft blue-gray
        self.snow_color = (255, 255, 255)  # White for snow caps
        self.mountain_border_color = (121, 139, 157)  # Slightly darker than mountain color
        self.cloud_color = (255, 255, 255, 128)  # Semi-transparent white for clouds
        
        self.horizon = int(self.height * 0.4)
        self.road_thickness = int(self.height * 0.1)
        self.road_top_position = int(self.height * 0.5)
        
        # Define the safe zone for the vehicle
        self.vehicle_safe_zone = (int(height * 0.5), int(height * 0.8))  # Adjust these values as needed
        #
        self.road_buffer = 20 #buffer zone for trees
        self.road_marks_offset = 0
        self.tree_offset = 0
        self.mountain_offset = 0.01  # Small positive value to prevent initial leftward movement
        self.cloud_offset = 0
        
        #dragging issue
        self.mountain_offset = 0  # Small positive value to prevent initial leftward movement
        self.start_smoothing_duration = 1.0  # Duration of smooth start in seconds
        self.start_time = 0.0

        
        self.VISUAL_SPEED_FACTOR = visual_speed_factor
        self.METERS_TO_PIXELS = meters_to_pixels
        self.DASH_LENGTH = 3 * self.METERS_TO_PIXELS
        self.GAP_LENGTH = 9 * self.METERS_TO_PIXELS
        self.ROAD_MARK_CYCLE = self.DASH_LENGTH + self.GAP_LENGTH
        
        self.paused = False
         # Generate landscape elements after all necessary attributes are initialized
        
        self.mountains = self.make_mountains()
        self.trees = self.generate_trees()
        self.clouds = self.generate_clouds()
        

    def make_mountains(self):
        mountains = []
        for i in range(5):
            x = i * self.width // 4
            y = self.horizon
            width = random.randint(200, 300)
            height = random.randint(50, 100)
            peak_offset = random.randint(-width//8, width//8)
            mountains.append([x, y, width, height, peak_offset])
        return mountains
    
    def generate_trees(self):
        trees = []
        green_area_top = self.horizon
        green_area_bottom = self.height
        road_top = self.road_top_position
        road_bottom = self.road_top_position + self.road_thickness

        # Create a list to keep track of occupied x-positions
        occupied_spaces = [False] * self.width

        attempts = 0
        max_attempts = 200  # Limit attempts to prevent infinite loop

        while len(trees) < 50 and attempts < max_attempts:
            x = random.randint(0, self.width - 1)
            
            # Create a non-uniform distribution favoring medium-sized trees
            if random.random() < 0.5:  # 70% chance for medium trees
                trunk_height = random.randint(30, 50)
            elif random.random() < 0.4:  
                trunk_height = random.randint(20, 30)
            else:  #
                trunk_height = random.randint(100, 150)
            
            leaves_height = trunk_height  # Make leaves as tall as the trunk
            full_tree_height = trunk_height + leaves_height
            tree_width = trunk_height // 2  # Adjust if needed

            # Check if there's enough space for the tree
            if all(not occupied_spaces[i % self.width] for i in range(x - tree_width // 2, x + tree_width // 2 + 1)):
                # Above road
                above_road_max = road_top - self.road_buffer - full_tree_height
                if above_road_max > green_area_top:
                    above_road_range = (green_area_top, above_road_max)
                else:
                    above_road_range = None

                # Below road
                below_road_min = road_bottom + self.road_buffer
                if below_road_min < green_area_bottom - full_tree_height:
                    below_road_range = (below_road_min, green_area_bottom - full_tree_height)
                else:
                    below_road_range = None

                # Choose placement based on available ranges
                if above_road_range and below_road_range:
                    if random.choice([True, False]):
                        tree_bottom = random.randint(*above_road_range) + full_tree_height
                    else:
                        tree_bottom = random.randint(*below_road_range) + full_tree_height
                elif above_road_range:
                    tree_bottom = random.randint(*above_road_range) + full_tree_height
                elif below_road_range:
                    tree_bottom = random.randint(*below_road_range) + full_tree_height
                else:
                    attempts += 1
                    continue  # Skip this tree if no valid placement
                trees.append({"x": x, "y": tree_bottom, "trunk_height": trunk_height, "leaves_height": leaves_height})
                # Mark the space as occupied
                for i in range(x - tree_width // 2, x + tree_width // 2 + 1):
                    occupied_spaces[i % self.width] = True
            attempts += 1
        return trees
    
    def generate_clouds(self):
        clouds = []
        for _ in range(5):
            x = random.randint(0, self.width)
            y = random.randint(0, int(self.height * 0.3))
            clouds.append({"x": x, "y": y})
        return clouds

    def draw_pixel_tree(self, screen, x, y, trunk_height, leaves_height):
        trunk_color = (101, 67, 33)  # Muted brown
        leaves_color = (76, 115, 76)  # Muted green
        
        trunk_width = max(2, trunk_height // 4)
        leaves_width = trunk_height // 2
        
        # Draw trunk from bottom up
        pygame.draw.rect(screen, trunk_color, (x - trunk_width // 2, y - trunk_height // 2, trunk_width, trunk_height // 2))
        
        # Draw lower part of the leaves as a larger triangle
        pygame.draw.polygon(screen, leaves_color, [
            (x, y - trunk_height // 2 - leaves_height),
            (x - leaves_width, y - trunk_height // 2),
            (x + leaves_width, y - trunk_height // 2)
        ])
        
        # Draw upper part of the leaves as a smaller triangle, intertwined with the lower part
        pygame.draw.polygon(screen, leaves_color, [
            (x, y - trunk_height // 2 - leaves_height * 1.3),
            (x - leaves_width * 0.7, y - trunk_height // 2 - leaves_height * 0.5),
            (x + leaves_width * 0.7, y - trunk_height // 2 - leaves_height * 0.5)
        ])

    def draw_pixel_cloud(self, screen, x, y):
        cloud_color = (255, 255, 255)  # White
        
        pygame.draw.rect(screen, cloud_color, (x, y, 30, 15))
        pygame.draw.rect(screen, cloud_color, (x + 5, y - 5, 20, 5))
        pygame.draw.rect(screen, cloud_color, (x + 10, y + 15, 15, 5))
        
    def draw_mountain(self, screen, x, y, width, height, snow_height):
        # Draw the main mountain body
        mountain_color = (100, 100, 100)  # Gray
        mountain_points = [
            (x, y),
            (x + width // 2, y - height),
            (x + width, y)
        ]
        pygame.draw.polygon(screen, mountain_color, mountain_points)

        # Calculate snow cap points
        snow_width = width * snow_height // height  # Adjust snow width based on mountain proportions
        snow_points = [
            (x + width // 2, y - height),
            (x + (width - snow_width) // 2, y - height + snow_height),
            (x + (width + snow_width) // 2, y - height + snow_height)
        ]

        # Draw the snow cap
        snow_color = (255, 255, 255)  # White
        pygame.draw.polygon(screen, snow_color, snow_points)

    def draw(self, screen, vehicle,delta_time):
        screen.fill(self.sky_color)
        pygame.draw.rect(screen, self.ground_color, (0, self.horizon, self.width, self.height - self.horizon))
        # Draw road 
        pygame.draw.rect(screen, self.road_color, (0, self.road_top_position, self.width, self.road_thickness))
        self.update(vehicle, delta_time)
        # Draw mountains
        for mountain in self.mountains:
            x, y, width, height, peak_offset = mountain
            adjusted_x = (x + self.mountain_offset) % self.width
            self.draw_mountain(screen, adjusted_x, self.horizon, width, height, height // 4)
            if adjusted_x + width > self.width:
                self.draw_mountain(screen, adjusted_x - self.width, self.horizon, width, height, height // 4)
        
        # Draw clouds
        sky_height_limit = int(self.height * 0.19)  # Set the sky height limit to 19% of the screen height
        for cloud in self.clouds:
            adjusted_x = (cloud["x"] + self.cloud_offset) % self.width
            adjusted_y = min(cloud["y"], sky_height_limit - 20)  # Ensure clouds are above the sky height limit
            self.draw_pixel_cloud(screen, adjusted_x, adjusted_y)
            if adjusted_x + 30 > self.width:  # 30 is the width of the cloud in draw_pixel_cloud
                self.draw_pixel_cloud(screen, adjusted_x - self.width, adjusted_y)

        # Draw trees
        for tree in self.trees:
            adjusted_x = (tree["x"] + self.tree_offset) % self.width
            self.draw_pixel_tree(screen, adjusted_x, tree["y"], tree["trunk_height"], tree["leaves_height"])
            if adjusted_x + tree["trunk_height"] // 2 > self.width:
                self.draw_pixel_tree(screen, adjusted_x - self.width, tree["y"], tree["trunk_height"], tree["leaves_height"])

        # Draw road marks
        marking_y = self.road_top_position + self.road_thickness // 2
        for x in range(int(self.road_marks_offset) % self.ROAD_MARK_CYCLE - self.ROAD_MARK_CYCLE, self.width, self.ROAD_MARK_CYCLE):
            pygame.draw.line(screen, (255, 255, 255), (x, marking_y), (x + self.DASH_LENGTH, marking_y), 2)
    
    def update(self, vehicle, delta_time):
        if not self.paused:
            try:
                speed = vehicle.speed  # Try to access the speed attribute
            except AttributeError:
                print("Error: 'vehicle' object has no attribute 'speed'")
                speed = 0  # Set a default speed to avoid further errors

        if not self.paused:
            visual_speed = speed * self.VISUAL_SPEED_FACTOR
            self.road_marks_offset -= visual_speed * self.METERS_TO_PIXELS * delta_time
            self.tree_offset -= visual_speed * self.METERS_TO_PIXELS * delta_time
            self.mountain_offset -= visual_speed * delta_time *2
            self.cloud_offset -= visual_speed * delta_time / 40

    def set_paused(self, paused):
        self.paused = paused