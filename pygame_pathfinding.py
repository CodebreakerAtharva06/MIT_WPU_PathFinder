import pygame
import numpy as np
import random
import speech_recognition as sr
import time
import os

# Initialize Pygame
pygame.init()

# Constants
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
WINDOW_SIZE = (800, 600)
STEP_SIZE = 10
MAX_ITERATIONS = 5000

# Initialize the screen
screen = pygame.display.set_mode(WINDOW_SIZE)
pygame.display.set_caption("Interactive Pathfinding")

class Environment:
    def __init__(self, colour, x, y, width, height):
        self.colour = colour
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def create(self, screen):
        pygame.draw.rect(screen, self.colour, [self.x, self.y, self.width, self.height])

def setup_environment():
    screen.fill(WHITE)
    building_centers = {}
    obstacles = []

    # Define buildings
    buildings = [
        Environment(BLACK, 50, 50, 80, 100),   # Main Hall
        Environment(BLACK, 50, 250, 80, 100),  # Library
        Environment(BLACK, 50, 450, 80, 100),  # Gym
        Environment(BLACK, 670, 50, 80, 100),  # Cafe
        Environment(BLACK, 670, 250, 80, 100), # Auditorium
        Environment(BLACK, 670, 450, 80, 100)  # Admin Office
    ]

    labels = ['main hall', 'library', 'gym', 'cafe', 'auditorium', 'admin office']
    names = ['Main Hall', 'Library', 'Gym', 'Cafeteria', 'Auditorium', 'Administrative Office']

    for i, building in enumerate(buildings):
        building.create(screen)
        obstacles.append(building)
        label = labels[i]
        name = names[i]
        font = pygame.font.Font(None, 18)
        text = font.render(label, True, WHITE)
        text_rect = text.get_rect(center=(building.x + building.width // 2, building.y + building.height // 2))
        screen.blit(text, text_rect)
        
        font_new = pygame.font.Font(None, 16)
        text_new = font_new.render(name, True, BLACK)
        text_rect_new = text_new.get_rect(center=(building.x + building.width // 2, building.y - 15))
        screen.blit(text_new, text_rect_new)
        
        if i < 3:  # Left side buildings
            building_centers[label] = (building.x + building.width + 10, building.y + building.height // 2)
        else:  # Right side buildings
            building_centers[label] = (building.x - 10, building.y + building.height // 2)

    # Define circular points
    circular_points = [
        (200, 150, 30, 'garden', 'Garden'),
        (200, 450, 30, 'courtyard', 'Library Courtyard'),
        (600, 150, 30, 'park', 'Park'),
        (600, 450, 30, 'fountain', 'Fountain')
    ]

    for x, y, r, label, name in circular_points:
        pygame.draw.circle(screen, BLACK, (x, y), r)
        obstacles.append(Environment(BLACK, x-r, y-r, 2*r, 2*r))
        font = pygame.font.Font(None, 18)
        text = font.render(label, True, WHITE)
        text_rect = text.get_rect(center=(x, y))
        screen.blit(text, text_rect)
        
        font_new = pygame.font.Font(None, 16)
        text_new = font_new.render(name, True, BLACK)
        text_rect_new = text_new.get_rect(center=(x, y - r - 10))
        screen.blit(text_new, text_rect_new)
        
        # Set the destination point just outside the circle
        angle = np.pi / 4
        building_centers[label] = (int(x + (r + 5) * np.cos(angle)), int(y + (r + 5) * np.sin(angle)))

    # Define triangles
    triangles = [
        ([(150, 50), (170, 90), (190, 50)], 'canteen', 'Canteen'),
        ([(400, 250), (420, 290), (440, 250)], 'fees dept', 'Fees Dept'),
        ([(250, 350), (270, 390), (290, 350)], '1st year', '1st Year'),
        ([(550, 350), (570, 390), (590, 350)], '2nd year', '2nd Year'),
        ([(400, 100), (420, 140), (440, 100)], 'cse', 'CSE')
    ]

    for triangle, label, name in triangles:
        pygame.draw.polygon(screen, BLACK, triangle)
        min_x = min(x for x, _ in triangle)
        max_x = max(x for x, _ in triangle)
        min_y = min(y for _, y in triangle)
        max_y = max(y for _, y in triangle)
        obstacles.append(Environment(BLACK, min_x, min_y, max_x-min_x, max_y-min_y))
        font = pygame.font.Font(None, 14)
        text = font.render(label, True, WHITE)
        text_rect = text.get_rect(center=(sum(x for x, _ in triangle) // 3, sum(y for _, y in triangle) // 3))
        screen.blit(text, text_rect)
        
        font_new = pygame.font.Font(None, 14)
        text_new = font_new.render(name, True, BLACK)
        text_rect_new = text_new.get_rect(center=(sum(x for x, _ in triangle) // 3, min(y for _, y in triangle) - 10))
        screen.blit(text_new, text_rect_new)
        
        # Set the destination point just outside the triangle
        triangle_center = (sum(x for x, _ in triangle) // 3, sum(y for _, y in triangle) // 3)
        building_centers[label] = (triangle_center[0] + 10, triangle_center[1] + 10)

    pygame.display.flip()
    return building_centers, obstacles

def is_valid_point(x, y, obstacles):
    if not (0 <= x < WINDOW_SIZE[0] and 0 <= y < WINDOW_SIZE[1]):
        return False
    for obs in obstacles:
        if obs.x <= x < obs.x + obs.width and obs.y <= y < obs.y + obs.height:
            return False
    return True

def RRT(start, goal, obstacles, max_iterations=MAX_ITERATIONS, step_size=STEP_SIZE):
    parent = {start: None}
    
    for _ in range(max_iterations):
        if random.random() < 0.1:
            x, y = goal
        else:
            x, y = random.randint(0, WINDOW_SIZE[0] - 1), random.randint(0, WINDOW_SIZE[1] - 1)
        
        if not is_valid_point(x, y, obstacles):
            continue
        
        nearest = min(parent.keys(), key=lambda p: ((p[0] - x) ** 2 + (p[1] - y) ** 2) ** 0.5)
        theta = np.arctan2(y - nearest[1], x - nearest[0])
        
        new_x = int(nearest[0] + step_size * np.cos(theta))
        new_y = int(nearest[1] + step_size * np.sin(theta))
        
        if is_valid_point(new_x, new_y, obstacles):
            new_point = (new_x, new_y)
            parent[new_point] = nearest
            pygame.draw.line(screen, BLUE, nearest, new_point, 1)
            pygame.display.update()
            
            if ((new_x - goal[0]) ** 2 + (new_y - goal[1]) ** 2) ** 0.5 < step_size:
                parent[goal] = new_point
                return parent
    
    return None

def backtrack_path(parent, start, goal):
    path = [goal]
    while path[-1] != start:
        path.append(parent[path[-1]])
    path.reverse()
    return path

def get_voice_input(prompt):
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print(prompt)
        audio = recognizer.listen(source)
    
    try:
        text = recognizer.recognize_google(audio).lower()
        print(f"You said: {text}")
        return text
    except sr.UnknownValueError:
        print("Sorry, I didn't understand that.")
        return None
    except sr.RequestError:
        print("Sorry, there was an error with the speech recognition service.")
        return None

def get_typed_input(prompt):
    font = pygame.font.Font(None, 32)
    input_box = pygame.Rect(300, 550, 400, 32)  # Moved the input box to the right
    color_inactive = pygame.Color('lightskyblue3')
    color_active = pygame.Color('dodgerblue2')
    color = color_inactive
    active = False
    text = ''
    done = False

    screen.fill(WHITE, (0, 540, WINDOW_SIZE[0], 60))
    prompt_surface = font.render(prompt, True, BLACK)
    screen.blit(prompt_surface, (10, 550))  # Keep the prompt on the left
    pygame.display.flip()

    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.MOUSEBUTTONDOWN:
                if input_box.collidepoint(event.pos):
                    active = not active
                else:
                    active = False
                color = color_active if active else color_inactive
            if event.type == pygame.KEYDOWN:
                if active:
                    if event.key == pygame.K_RETURN:
                        done = True
                    elif event.key == pygame.K_BACKSPACE:
                        text = text[:-1]
                    else:
                        text += event.unicode

        screen.fill(WHITE, input_box)
        txt_surface = font.render(text, True, color)
        width = max(400, txt_surface.get_width() + 10)  # Ensure minimum width of 400
        input_box.w = width
        screen.blit(txt_surface, (input_box.x + 5, input_box.y + 5))
        pygame.draw.rect(screen, color, input_box, 2)

        pygame.display.flip()

    return text.lower()

def main():
    building_centers, obstacles = setup_environment()
    
    input_method = os.environ.get('INPUT_METHOD', 'type').lower()
    
    if input_method == 'voice':
        start_input = get_voice_input("Please say the start point:")
        end_input = get_voice_input("Please say the destination:")
    else:
        start_input = get_typed_input("Enter start point:")
        end_input = get_typed_input("Enter destination:")

    if start_input in building_centers and end_input in building_centers:
        start = building_centers[start_input]
        end = building_centers[end_input]
        print(f"Calculating path from {start_input} to {end_input}")
        
        parent = RRT(start, end, obstacles)
        
        if parent:
            path = backtrack_path(parent, start, end)
            
            # Draw final path
            for i in range(len(path) - 1):
                pygame.draw.line(screen, YELLOW, path[i], path[i+1], 4)
                pygame.display.update()
                time.sleep(0.01)
            
            # Draw start and end points
            pygame.draw.circle(screen, RED, start, 5)
            pygame.draw.circle(screen, GREEN, end, 5)
            
            pygame.display.flip()
        else:
            print("No path found")
    else:
        print("Start point or destination not recognized.")
    
    # Keep the window open until user closes it
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
    
    pygame.quit()

if __name__ == '__main__':
    main()