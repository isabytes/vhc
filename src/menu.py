# Game version
VERSION = "1.0.0"

# Importing necessary modules
import pygame
import time
from config import VEHICLE_CONFIGS, TRAILER_WEIGHT_OPTIONS, WIDTH, HEIGHT, COLORS
from utils import kg_to_lbs, lbs_to_kg

# Define button sizes
BUTTON_WIDTH = 200
BUTTON_HEIGHT = 50
FONT_SIZE = 32

def draw_button(screen, button_x, button_y, button_width, button_height, button_color, button_text=''):
    button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
    pygame.draw.rect(screen, button_color, button_rect)
    if button_text != '':
        button_font = pygame.font.Font(None, FONT_SIZE)
        text_surface = button_font.render(button_text, True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=(button_x + button_width/2, button_y + button_height/2))
        screen.blit(text_surface, text_rect)  # Draw text on the button
    return button_rect

def draw_text(screen, text, font, text_color, text_x, text_y):
    text_surface = font.render(text, True, text_color)
    screen.blit(text_surface, (text_x, text_y))  # Draw text on the screen

def draw_intro_page(screen, font):
    # Draw background gradient
    for y_coord in range(HEIGHT):
        gradient_red = int(50 * y_coord / HEIGHT)
        gradient_green = int(100 * y_coord / HEIGHT)
        gradient_blue = int(200 * y_coord / HEIGHT)
        gradient_color = (gradient_red, gradient_green, gradient_blue)
        pygame.draw.line(screen, gradient_color, (0, y_coord), (WIDTH, y_coord))
    
    # Draw road
    road_y_position = HEIGHT - 100
    road_color = (50, 50, 50)
    pygame.draw.rect(screen, road_color, (0, road_y_position, WIDTH, 100))
    
    # Draw road markings
    road_marking_color = (255, 255, 0)
    for x_coord in range(0, WIDTH, 80):
        pygame.draw.rect(screen, road_marking_color, (x_coord, road_y_position + 45, 40, 10))

    # Draw title
    title_font = pygame.font.Font(None, 80)
    title_text = "Vehicle Simulator"
    title_x = WIDTH // 2 - title_font.size(title_text)[0] // 2  # Center text
    title_y = HEIGHT // 4
    draw_text(screen, title_text, title_font, (255, 255, 255), title_x, title_y)
    
    # Draw subtitle
    subtitle_font = pygame.font.Font(None, 40)
    subtitle_text = "Start your engines!"
    subtitle_x = WIDTH // 2 - subtitle_font.size(subtitle_text)[0] // 2  # Center text
    subtitle_y = HEIGHT // 4 + 100
    draw_text(screen, subtitle_text, subtitle_font, (200, 200, 200), subtitle_x, subtitle_y)

    # Draw start button
    start_button_x = WIDTH // 2 - 100
    start_button_y = HEIGHT // 2 + 100
    start_button = draw_button(screen, start_button_x, start_button_y, BUTTON_WIDTH, BUTTON_HEIGHT, (0, 255, 0), "Start Simulation")

    # Draw version number
    version_x = 10
    version_y = HEIGHT - 30
    draw_text(screen, f"Version: {VERSION}", font, (255, 255, 255), version_x, version_y)

    return start_button  # Return the start button for event handling
def draw_vehicle_menu(screen, font, use_metric):
    vehicle_buttons = {}
    for index, vehicle_name in enumerate(VEHICLE_CONFIGS.keys()):
        button_x = WIDTH // 2 - 200
        button_y = HEIGHT // 2 - 150 + index * 60
        button = draw_button(screen, button_x, button_y, 400, 50, (200, 200, 200), vehicle_name)
        vehicle_buttons[vehicle_name] = button
    
    instruction_text = "Please select a vehicle to begin."
    if use_metric:
        unit_text = "Units: Metric (kg). Please change if necessary before selection."
    else:
        unit_text = "Units: Imperial (lbs). Please change if necessary before selection."
    
    unit_x = WIDTH // 2 - font.size(unit_text)[0] // 2
    unit_y = HEIGHT // 6
    draw_text(screen, unit_text, font, (255, 255, 255), unit_x, unit_y)
    
    instruction_x = WIDTH // 2 - font.size(instruction_text)[0] // 2
    instruction_y = HEIGHT // 6 + 40
    draw_text(screen, instruction_text, font, (255, 255, 255), instruction_x, instruction_y)
    
    version_x = 10
    version_y = HEIGHT - 30
    draw_text(screen, f"Version: {VERSION}", font, (255, 255, 255), version_x, version_y)
    
    return vehicle_buttons  # Return the vehicle buttons for event handling

def draw_trailer_menu(screen, font, WIDTH, HEIGHT, use_metric):
    weight_buttons = {}
    button_height = 60
    button_width = 300
    start_y = HEIGHT // 2 - (len(TRAILER_WEIGHT_OPTIONS) * button_height) // 2

    for index, (weight, label) in enumerate(TRAILER_WEIGHT_OPTIONS):
        if weight != "Custom":
            weight_value = float(weight.split()[0].replace(',', ''))
            if use_metric:
                display_weight = f"{weight_value:,.0f} kg"
            else:
                display_weight = f"{kg_to_lbs(weight_value):,.0f} lbs"
        else:
            display_weight = weight

        button_x = WIDTH // 2 - button_width // 2
        button_y = start_y + index * button_height
        button_rect = pygame.Rect(button_x, button_y, button_width, button_height - 10)
        pygame.draw.rect(screen, COLORS['WHITE'], button_rect, 2)  # Draw button outline
        
        label_x = button_rect.centerx - font.size(label)[0] // 2
        label_y = button_rect.centery - font.size(label)[1]
        draw_text(screen, label, font, COLORS['WHITE'], label_x, label_y)  # Draw button label
        
        weight_font = pygame.font.Font(None, 24)
        weight_x = button_rect.centerx - weight_font.size(f"({display_weight})")[0] // 2
        weight_y = button_rect.centery + 5
        draw_text(screen, f"({display_weight})", weight_font, COLORS['WHITE'], weight_x, weight_y)  # Draw weight text
        
        weight_buttons[weight] = button_rect

    # Add Back button
    back_button_x = WIDTH // 2 - button_width // 2
    back_button_y = start_y + len(TRAILER_WEIGHT_OPTIONS) * button_height + 20
    back_button = pygame.Rect(back_button_x, back_button_y, button_width, button_height - 10)
    pygame.draw.rect(screen, COLORS['DARK_GRAY'], back_button)
    pygame.draw.rect(screen, COLORS['WHITE'], back_button, 2)
    
    back_text_x = back_button.centerx - font.size("Back")[0] // 2
    back_text_y = back_button.centery - font.size("Back")[1] // 2
    draw_text(screen, "Back", font, COLORS['WHITE'], back_text_x, back_text_y)

    # Draw version number
    version_x = 10
    version_y = HEIGHT - 30
    draw_text(screen, f"Version: {VERSION}", font, COLORS['WHITE'], version_x, version_y)

    return weight_buttons, back_button  # Return the weight buttons and back button for event handling

def check_vehicle_click(event, vehicle_buttons):
    if event.type == pygame.MOUSEBUTTONDOWN:
        if vehicle_buttons is not None:
            mouse_pos = event.pos
            for vehicle_name, button in vehicle_buttons.items():
                if button.collidepoint(mouse_pos):
                    return vehicle_name  # Return the name of the clicked vehicle
    return None

def check_trailer_click(event, weight_buttons, back_button, screen, font, use_metric):
    if event.type == pygame.MOUSEBUTTONDOWN:
        mouse_pos = event.pos
        if back_button.collidepoint(mouse_pos):
            return "back"  # User clicked the back button
        for weight, button in weight_buttons.items():
            if button.collidepoint(mouse_pos):
                if weight == "Custom":
                    return "custom"  # User wants to enter a custom weight
                else:
                    weight_value = float(weight.split()[0].replace(',', ''))
                    return str(weight_value)  # Return the selected weight
    return None

def main_menu(screen, font, WIDTH, HEIGHT):
    current_menu = "intro"
    selected_vehicle = None
    use_metric = True
    vehicle_buttons = None
    weight_buttons = None
    back_button = None
    start_button = None

    running = True
    clock = pygame.time.Clock()
    FPS = 30

    while running:
        clock.tick(FPS)
        screen.fill(COLORS['BLACK'])
        
        if current_menu == "intro":
            start_button = draw_intro_page(screen, font)
        elif current_menu == "vehicle":
            vehicle_buttons = draw_vehicle_menu(screen, font, use_metric)    
            weight_buttons = None
            back_button = None
            # Unit conversion button
            unit_button_x = WIDTH // 2 - 70
            unit_button_y = HEIGHT // 10
            unit_button = pygame.Rect(unit_button_x, unit_button_y, 140, 40)
            pygame.draw.rect(screen, COLORS['LIGHT_BLUE'], unit_button)
            pygame.draw.rect(screen, COLORS['BLUE'], unit_button, 2)
            if use_metric:
                unit_text = "Units: kg"
            else:
                unit_text = "Units: lbs"
            unit_text_x = unit_button.centerx - font.size(unit_text)[0] // 2
            unit_text_y = unit_button.centery - font.size(unit_text)[1] // 2
            draw_text(screen, unit_text, font, COLORS['BLACK'], unit_text_x, unit_text_y)
        elif current_menu == "trailer":
            vehicle_buttons = None
            weight_buttons, back_button = draw_trailer_menu(screen, font, WIDTH, HEIGHT, use_metric)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if current_menu == "vehicle":
                    if unit_button.collidepoint(event.pos):
                        use_metric = not use_metric  # Toggle between metric and imperial units
                elif current_menu == "intro":
                    if start_button and start_button.collidepoint(event.pos):
                        current_menu = "vehicle"  # Move to vehicle selection menu
            
            if current_menu == "vehicle":
                result = check_vehicle_click(event, vehicle_buttons)
                if result is not None:
                    if result == "Semi truck":
                        selected_vehicle = "Semi truck"
                        current_menu = "trailer"  # Move to trailer selection for semi truck
                    else:
                        return result, None, use_metric  # Return selected vehicle (not semi truck)
            elif current_menu == "trailer":
                if weight_buttons is not None and back_button is not None:
                    result = check_trailer_click(event, weight_buttons, back_button, screen, font, use_metric)
                    if result is not None:
                        if result == "back":
                            current_menu = "vehicle"  # Go back to vehicle selection
                        elif result == "custom":
                            custom_weight = get_custom_weight(screen, font, use_metric)
                            if custom_weight:
                                return selected_vehicle, custom_weight, use_metric
                        else:
                            return selected_vehicle, result, use_metric  # Return selected vehicle and trailer weight
        
        pygame.display.flip()

    return "quit"

def get_custom_weight(screen, font, use_metric):
    input_text = ""
    input_rect = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2, 250, 40)
    cursor_visible = True
    cursor_timer = 0
    
    confirm_button = pygame.Rect(WIDTH // 2 - 200, HEIGHT // 2 + 60, 400, 40)
    cancel_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 110, 200, 40)

    clock = pygame.time.Clock()
    blink_speed = 0.5  # Cursor blink speed
    FPS = 30

    warning_text = ""
    warning_timer = 0

    while True:
        clock.tick(FPS)
        dt = clock.get_time() / 1000.0  # Convert milliseconds to seconds
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None  # Exit the function if user closes the window
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    input_text = input_text[:-1]  # Remove last character
                elif event.unicode.isnumeric() and len(input_text) < 3:
                    input_text += event.unicode  # Add numeric input (max 3 digits)
            if event.type == pygame.MOUSEBUTTONDOWN:
                if confirm_button.collidepoint(event.pos):
                    try:
                        weight = int(input_text) * 1000  # Convert input to actual weight
                        if use_metric:
                            max_weight = 100000  # Max weight in kg
                        else:
                            max_weight = int(kg_to_lbs(100000))  # Convert max weight to lbs
                        if weight >= 6000 and weight <= max_weight:
                            return str(weight)  # Return valid weight
                        else:
                            warning_text = "Weight out of range!"
                            warning_timer = 2  # Set warning message for 2 seconds
                    except ValueError:
                        warning_text = "Invalid input!"
                        warning_timer = 2  # Set warning message for 2 seconds
                elif cancel_button.collidepoint(event.pos):
                    return None  # Cancel input and return to previous menu

        screen.fill(COLORS['BLACK'])  # Clear screen with black color
        if use_metric:
            unit = "kg"
            min_weight = "1,000"
            max_weight = "100,000"
        else:
            unit = "lbs"
            min_weight = f"{int(kg_to_lbs(1000)):,}"
            max_weight = f"{int(kg_to_lbs(100000)):,}"
        prompt_text = f"Enter weight ({min_weight}-{max_weight} {unit}):"
        prompt_x = WIDTH // 2 - font.size(prompt_text)[0] // 2
        prompt_y = HEIGHT // 2 - 50
        draw_text(screen, prompt_text, font, COLORS['WHITE'], prompt_x, prompt_y)

        # Draw input box and text
        pygame.draw.rect(screen, COLORS['WHITE'], input_rect, 2)
        if input_text:
            display_text = f"{int(input_text):,},000"
        else:
            display_text = "0,000"
        txt_surface = font.render(display_text, True, COLORS['WHITE'])
        text_x = input_rect.right - txt_surface.get_width() - 5
        screen.blit(txt_surface, (text_x, input_rect.y + 5))
        
        # Draw unit outside the box
        unit_x = input_rect.right + 10
        unit_y = input_rect.centery - font.size(unit)[1] // 2
        draw_text(screen, unit, font, COLORS['WHITE'], unit_x, unit_y)

        # Draw cursor
        cursor_timer += dt
        if cursor_timer >= blink_speed:
            cursor_visible = not cursor_visible
            cursor_timer = 0
        if cursor_visible:
            cursor_pos = text_x + txt_surface.get_width()
            pygame.draw.line(screen, COLORS['WHITE'], (cursor_pos, input_rect.y + 5), (cursor_pos, input_rect.bottom - 5), 2)

        # Draw buttons
        pygame.draw.rect(screen, COLORS['GREEN'], confirm_button)
        pygame.draw.rect(screen, COLORS['RED'], cancel_button)
        draw_text(screen, "Confirm and Start Simulation", font, COLORS['BLACK'], confirm_button.centerx - font.size("Confirm and Start Simulation")[0] // 2, confirm_button.centery - font.size("Confirm and Start Simulation")[1] // 2)
        draw_text(screen, "Cancel", font, COLORS['BLACK'], cancel_button.centerx - font.size("Cancel")[0] // 2, cancel_button.centery - font.size("Cancel")[1] // 2)

        # Help text
        help_text = f"Enter weight in {'tonnes' if use_metric else 'thousands of lbs'} (1-100). This affects the vehicle's performance."
        draw_text(screen, help_text, font, COLORS['LIGHT_GRAY'], WIDTH // 2 - font.size(help_text)[0] // 2, HEIGHT // 2 + 160)

        # Draw warning text
        if warning_timer > 0:
            draw_text(screen, warning_text, font, COLORS['RED'], WIDTH // 2 - font.size(warning_text)[0] // 2, HEIGHT // 2 + 200)
            warning_timer -= dt

        # Draw version number
        draw_text(screen, f"Version: {VERSION}", font, COLORS['WHITE'], 10, HEIGHT - 30)

        pygame.display.flip()