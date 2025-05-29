import sys
import os
import pygame
import random

# Colors
WHITE = (245, 245, 245)         # Mist White
BLACK = (33, 33, 33)            # Charcoal
RED = (255, 127, 80)            # Coral (Fallback player color)
DARKGRAY = (72, 72, 72)         # Graphite (Default cell/wall color)
YELLOW = (255, 223, 100)        # Soft Gold (Path color)
BLUE = (0, 128, 128)            # Teal (Win message color)
LIGHTORANGE = (255, 204, 153)   # Apricot (Used in initial_screen)
INTERMEDIARYORANGE = (255, 160, 122) # Light Salmon (Used in initial_screen)
# Colors for BFS/Solution path (will be used more in Step 3)
PINK = (255, 182, 193)
ORANGE = (255, 140, 0)


# Maze Configuration
BORDER_THICKNESS = 1.0
SIZE = 25  # Size of each cell

# Screen Dimensions
WIDTH = 600 # Maze area width
HEIGHT = 600 # Maze area height
HEIGHT_TOTAL = 680 # Total screen height (Step 2 will only use basic info)
SCREEN_SIZE = (WIDTH, HEIGHT_TOTAL) # Use full height for consistency

# Font Sizes
FONTSIZE_STATUS = 20
FONTSIZE_MESSAGE = 28 # For win message
FONTSIZE_CONTROLS = 14 # For R and ESC text
# Constants from user's file, used in initial_screen (though initial_screen is more for Step 3)
FONTSIZE_START = 28
FONTSIZE_COMMANDS_INTIAL = 15


def text(background, message, color, size, coordinate_x=None, coordinate_y=None, center=False, align_right=False):
    font_path = os.path.join("fonts", "Orbitron-VariableFont_wght.ttf")
    try:
        font = pygame.font.Font(font_path, size)
    except FileNotFoundError:
        # print(f"Warning: Font file '{font_path}' not found. Using default system font.")
        font = pygame.font.SysFont("arial", size)
        
    text_surface = font.render(message, True, color)
    text_rect = text_surface.get_rect()

    if center:
        text_rect.center = (WIDTH // 2, coordinate_y)
    elif align_right:
        text_rect.topright = (coordinate_x, coordinate_y)
    else:
        text_rect.topleft = (coordinate_x, coordinate_y)

    background.blit(text_surface, text_rect)

class NodeBorder():
    def _init_(self, pos_x, pos_y, width, height):
        self.color = BLACK
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.width = width
        self.height = height

    def render(self, background):
        pygame.draw.rect(background, self.color, [self.pos_x, self.pos_y, self.width, self.height])

class Node():
    def _init_(self, screen_pos_x, screen_pos_y):
        self.color = DARKGRAY 
        self.visited = False 
        self.explored = False # For BFS (Step 3)
        self.matrix_pos_x = 0 
        self.matrix_pos_y = 0 
        self.pos_x = screen_pos_x
        self.pos_y = screen_pos_y
        self.width = SIZE
        self.height = SIZE
        self.top_border = NodeBorder(self.pos_x, self.pos_y, SIZE, BORDER_THICKNESS)
        self.bottom_border = NodeBorder(self.pos_x, self.pos_y + SIZE - BORDER_THICKNESS, SIZE, BORDER_THICKNESS)
        self.right_border = NodeBorder(self.pos_x + SIZE - BORDER_THICKNESS, self.pos_y, BORDER_THICKNESS, SIZE)
        self.left_border = NodeBorder(self.pos_x, self.pos_y, BORDER_THICKNESS, SIZE)
        self.neighbors = []
        self.neighbors_connected = [] 
        self.parent = None 
        self.special_icon = None # ENHANCEMENT FOR STEP 2

    def render(self, background):
        # Draw base cell color (e.g., YELLOW for path, DARKGRAY for unvisited)
        pygame.draw.rect(background, self.color, [self.pos_x, self.pos_y, self.width, self.height])
        
        # ENHANCEMENT FOR STEP 2: Render special icon if it exists
        if self.special_icon:
            icon_x = self.pos_x + (self.width - self.special_icon.get_width()) // 2
            icon_y = self.pos_y + (self.height - self.special_icon.get_height()) // 2
            background.blit(self.special_icon, (icon_x, icon_y))
        
        self.top_border.render(background)
        self.bottom_border.render(background)
        self.right_border.render(background)
        self.left_border.render(background)

class Maze():
    def _init_(self, background, initial_x_row, initial_y_col, final_x_row, final_y_col, 
                 start_cell_icon=None, finish_cell_icon=None): # ENHANCEMENT FOR STEP 2
        self.background_surface = background 
        self.maze = []
        self.total_nodes = 0
        self.maze_created = False
        self.initial_coordinate_x_row = initial_x_row
        self.initial_coordinate_y_col = initial_y_col
        self.final_coordinate_x_row = final_x_row
        self.final_coordinate_y_col = final_y_col
        self.num_rows = HEIGHT // SIZE
        self.num_cols = WIDTH // SIZE

        for r_idx in range(self.num_rows):
            maze_row_list = []
            for c_idx in range(self.num_cols):
                current_screen_x = c_idx * SIZE
                current_screen_y = r_idx * SIZE
                node = Node(current_screen_x, current_screen_y)
                node.matrix_pos_x = r_idx
                node.matrix_pos_y = c_idx
                maze_row_list.append(node)
                self.total_nodes += 1
            self.maze.append(maze_row_list)
        
        # ENHANCEMENT FOR STEP 2: Assign special icons and set base color to YELLOW
        if start_cell_icon:
            start_node = self.maze[self.initial_coordinate_x_row][self.initial_coordinate_y_col]
            start_node.special_icon = start_cell_icon
            start_node.color = YELLOW # Path color as background for icon
        if finish_cell_icon:
            finish_node = self.maze[self.final_coordinate_x_row][self.final_coordinate_y_col]
            finish_node.special_icon = finish_cell_icon
            finish_node.color = YELLOW # Path color as background for icon

        self.define_neighbors()

    def add_edge(self, node, neighbor):
        neighbor.neighbors_connected.append(node)
        node.neighbors_connected.append(neighbor)

    def remove_neighbors_visited(self, node):
        node.neighbors = [n for n in node.neighbors if not n.visited]
    
    def define_neighbors(self):
        for r in range(self.num_rows):
            for c in range(self.num_cols):
                node = self.maze[r][c]
                node.neighbors = []
                if r > 0: node.neighbors.append(self.maze[r - 1][c])
                if r < self.num_rows - 1: node.neighbors.append(self.maze[r + 1][c])
                if c > 0: node.neighbors.append(self.maze[r][c - 1])
                if c < self.num_cols - 1: node.neighbors.append(self.maze[r][c + 1])
                                
    def break_border(self, node1, node2): # Color parameter removed, path is always YELLOW
        path_color = YELLOW
        if node2.matrix_pos_y == node1.matrix_pos_y + 1 and node2.matrix_pos_x == node1.matrix_pos_x:
            node1.right_border.color = path_color
            node2.left_border.color = path_color
        elif node2.matrix_pos_y == node1.matrix_pos_y - 1 and node2.matrix_pos_x == node1.matrix_pos_x:
            node1.left_border.color = path_color
            node2.right_border.color = path_color
        elif node2.matrix_pos_x == node1.matrix_pos_x + 1 and node2.matrix_pos_y == node1.matrix_pos_y:
            node1.bottom_border.color = path_color
            node2.top_border.color = path_color
        elif node2.matrix_pos_x == node1.matrix_pos_x - 1 and node2.matrix_pos_y == node1.matrix_pos_y:
            node1.top_border.color = path_color
            node2.bottom_border.color = path_color
    
    def _reset_maze_state(self):
        for r in range(self.num_rows):
            for c in range(self.num_cols):
                node = self.maze[r][c]
                node.visited = False
                node.color = DARKGRAY 
                node.neighbors_connected = [] 
                node.parent = None
                node.top_border.color = BLACK
                node.bottom_border.color = BLACK
                node.left_border.color = BLACK
                node.right_border.color = BLACK
                # Reset special_icon if they are tied to a specific maze instance, 
                # but here they are passed in, so Node objects are new each time.
                # If special_icons were attributes of the Node class from its init, you might clear them here.
                # For this structure, special icons are re-assigned in Maze._init_
        self.define_neighbors()

    def dfs(self, background_surface_for_text=None):
        self._reset_maze_state() 
        start_row = random.randint(0, self.num_rows - 1)
        start_col = random.randint(0, self.num_cols - 1)
        current_cell = self.maze[start_row][start_col]
        current_cell.visited = True
        current_cell.color = YELLOW
        
        stack = [current_cell]
        visited_cells = 1
        render_counter = 0
        render_interval = max(1, self.total_nodes // 100 if self.total_nodes > 0 else 1) 

        while visited_cells < self.total_nodes or len(stack) > 0:
            if not stack:
                found_unvisited_component = False
                for r_find in range(self.num_rows):
                    for c_find in range(self.num_cols):
                        if not self.maze[r_find][c_find].visited:
                            current_cell = self.maze[r_find][c_find]
                            current_cell.visited = True
                            current_cell.color = YELLOW
                            stack.append(current_cell)
                            visited_cells +=1
                            found_unvisited_component = True
                            break
                    if found_unvisited_component: break
                if not found_unvisited_component and visited_cells < self.total_nodes:
                    print("Warning: DFS stack empty but not all cells visited. Maze might have isolated parts.")
                    break 
                if not stack: break

            current_cell = stack[-1]
            self.remove_neighbors_visited(current_cell)

            if len(current_cell.neighbors) > 0:
                random_neighbor = random.choice(current_cell.neighbors)
                self.break_border(current_cell, random_neighbor) 
                self.add_edge(current_cell, random_neighbor) 
                current_cell = random_neighbor
                current_cell.visited = True
                current_cell.color = YELLOW 
                stack.append(current_cell)
                visited_cells += 1
            else: 
                stack.pop()
            
            render_counter += 1
            if render_counter >= render_interval or not stack: 
                if background_surface_for_text: 
                    self.render(background_surface_for_text)
                    # text(background_surface_for_text, "Generating Maze...", WHITE, FONTSIZE_STATUS, 10, HEIGHT + 10)
                    pygame.display.update()
                render_counter = 0
        
        # Ensure start/finish cells with icons have YELLOW background if visited (they should be)
        start_node_final = self.maze[self.initial_coordinate_x_row][self.initial_coordinate_y_col]
        if start_node_final.special_icon and start_node_final.visited: # Ensure it was part of the path
            start_node_final.color = YELLOW
        
        finish_node_final = self.maze[self.final_coordinate_x_row][self.final_coordinate_y_col]
        if finish_node_final.special_icon and finish_node_final.visited: # Ensure it was part of the path
            finish_node_final.color = YELLOW
        
        self.maze_created = True
        if background_surface_for_text:
            self.render(background_surface_for_text)
            pygame.display.update()

    def render(self, background):
        for r in range(self.num_rows):
            for c in range(self.num_cols):
                self.maze[r][c].render(background)

class Player(): # IMPLEMENTATION FOR STEP 2
    def _init_(self, initial_x_row, initial_y_col, image_path="assets/player.png"):
        self.matrix_pos_x_row = initial_x_row
        self.matrix_pos_y_col = initial_y_col
        max_dim_scale = 0.8
        max_width = int(SIZE * max_dim_scale)
        max_height = int(SIZE * max_dim_scale)
        self.original_image = None 
        try:
            loaded_image = pygame.image.load(image_path).convert_alpha()
            self.original_image = loaded_image 
            original_width, original_height = loaded_image.get_size()
            if original_height == 0: aspect_ratio = 1
            else: aspect_ratio = original_width / float(original_height)
            if original_width > original_height:
                self.image_width = max_width
                self.image_height = int(self.image_width / aspect_ratio) if aspect_ratio != 0 else max_height
                if self.image_height > max_height:
                    self.image_height = max_height
                    self.image_width = int(self.image_height * aspect_ratio)
            else:
                self.image_height = max_height
                self.image_width = int(self.image_height * aspect_ratio)
                if self.image_width > max_width:
                    self.image_width = max_width
                    self.image_height = int(self.image_width / aspect_ratio) if aspect_ratio != 0 else max_height
            self.image_width = max(1, self.image_width)
            self.image_height = max(1, self.image_height)
            self.image = pygame.transform.smoothscale(loaded_image, (self.image_width, self.image_height))
        except pygame.error as e:
            print(f"Error: Could not load player image at '{image_path}': {e}")
            self.image = None
            self.fallback_color = RED
            self.image_width = int(SIZE * max_dim_scale) 
            self.image_height = int(SIZE * max_dim_scale)
        self._recalculate_screen_pos()

    def _recalculate_screen_pos(self):
        self.pos_x = self.matrix_pos_y_col * SIZE + (SIZE - self.image_width) // 2
        self.pos_y = self.matrix_pos_x_row * SIZE + (SIZE - self.image_height) // 2

    def update(self, maze_grid_nodes, events):
        moved = False
        for event in events:
            if event.type == pygame.KEYDOWN:
                current_node = maze_grid_nodes[self.matrix_pos_x_row][self.matrix_pos_y_col]
                if event.key == pygame.K_LEFT and self.matrix_pos_y_col > 0 and \
                   (current_node.left_border.color != BLACK):
                    self.matrix_pos_y_col -= 1; moved = True
                elif event.key == pygame.K_RIGHT and self.matrix_pos_y_col < (WIDTH // SIZE) - 1 and \
                     (current_node.right_border.color != BLACK):
                    self.matrix_pos_y_col += 1; moved = True
                elif event.key == pygame.K_UP and self.matrix_pos_x_row > 0 and \
                     (current_node.top_border.color != BLACK):
                    self.matrix_pos_x_row -= 1; moved = True
                elif event.key == pygame.K_DOWN and self.matrix_pos_x_row < (HEIGHT // SIZE) - 1 and \
                     (current_node.bottom_border.color != BLACK):
                    self.matrix_pos_x_row += 1; moved = True
        if moved:
            self._recalculate_screen_pos()

    def render(self, background):
        if self.image:
            background.blit(self.image, (self.pos_x, self.pos_y))
        elif hasattr(self, 'fallback_color'):
            # Fallback rendering if image fails
            fallback_rect_pos_x = self.pos_x # Use calculated pos_x, pos_y
            fallback_rect_pos_y = self.pos_y
            pygame.draw.rect(background, self.fallback_color, 
                             [fallback_rect_pos_x, fallback_rect_pos_y, self.image_width, self.image_height])

# Minimal Monster class for Step 2 (to avoid errors, fully implemented in Step 3)
class Monster():
    def _init_(self, start_row, start_col, image_path="assets/monster_1.png", move_delay=30):
        self.matrix_pos_x_row = start_row
        self.matrix_pos_y_col = start_col
        # Basic image loading, actual AI and full features in Step 3
        try:
            max_dim_scale = 0.8
            self.image_width = int(SIZE * max_dim_scale)
            self.image_height = int(SIZE * max_dim_scale)
            loaded_image = pygame.image.load(image_path).convert_alpha()
            self.image = pygame.transform.smoothscale(loaded_image, (self.image_width, self.image_height))
        except pygame.error as e:
            print(f"Minimal Monster: Error loading image '{image_path}': {e}")
            self.image = None
        self._recalculate_screen_pos()


    def _recalculate_screen_pos(self):
         self.pos_x = self.matrix_pos_y_col * SIZE + (SIZE - self.image_width) // 2
         self.pos_y = self.matrix_pos_x_row * SIZE + (SIZE - self.image_height) // 2
    def update(self, player, maze_nodes):
        pass # Monster AI and logic will be in Step 3
    def render(self, background):
        if self.image: # Only render if image loaded
             background.blit(self.image, (self.pos_x, self.pos_y))


class Game():
    def _init_(self): # ENHANCEMENT FOR STEP 2
        try:
            pygame.init()
            pygame.font.init()
        except Exception as e:
            print(f'Error initializing Pygame: {e}')
            sys.exit(1)
        self.screen = pygame.display.set_mode(SCREEN_SIZE)
        pygame.display.set_caption('Maze Game - Step 2: Player')
        
        self.maze = None
        self.player = None # ADDED FOR STEP 2
        self.monsters = [] # Placeholder for Step 3
        
        self.initial_coordinate_x_row = 0
        self.initial_coordinate_y_col = 0
        self.final_coordinate_x_row = 0
        self.final_coordinate_y_col = 0
        
        self.start_game_flow = False # Will be used more in Step 3 for intro screen
        self.winner = False # ADDED FOR STEP 2
        self.game_over = False # For Step 3
        self.solved_by_system = False # For Step 3

        self.exit_game = False
        self.clock = pygame.time.Clock()

        # Icons for cells on the maze board
        self.start_cell_icon_surf = None 
        self.finish_cell_icon_surf = None 
        self.cell_icon_size = int(SIZE * 0.9) 

        # Icons for Legend (can be loaded here too, or later in Step 3)
        self.legend_player_icon = None 
        self.legend_start_icon = None
        self.legend_finish_icon = None
        self.legend_icon_size = int(SIZE*0.8)


    def _load_icons(self): # NEW METHOD FOR STEP 2
        # Load icons for cells on the maze board
        try:
            start_cell_orig = pygame.image.load("assets/start.png").convert_alpha()
            self.start_cell_icon_surf = pygame.transform.smoothscale(start_cell_orig, (self.cell_icon_size, self.cell_icon_size))
        except pygame.error as e: print(f"Error loading start.png for maze cell: {e}")
        try:
            finish_cell_orig = pygame.image.load("assets/finish.png").convert_alpha()
            self.finish_cell_icon_surf = pygame.transform.smoothscale(finish_cell_orig, (self.cell_icon_size, self.cell_icon_size))
        except pygame.error as e: print(f"Error loading finish.png for maze cell: {e}")
        
        # Load player icon for legend (can also be used for player itself if not overridden)
        try:
            player_img_orig = pygame.image.load("assets/player.png").convert_alpha()
            self.legend_player_icon = pygame.transform.smoothscale(player_img_orig, (self.legend_icon_size, self.legend_icon_size))
        except pygame.error as e: print(f"Error loading player.png for legend: {e}")


    def setup_new_game(self): # ENHANCED FOR STEP 2
        self._load_icons() # Load icons first

        num_rows = HEIGHT // SIZE
        num_cols = WIDTH // SIZE
        
        min_dist_start_finish = max(5, (num_rows + num_cols) // 4) 
        valid_points = False
        attempts = 0
        max_attempts = 100 # Prevent infinite loop

        while not valid_points and attempts < max_attempts:
            self.initial_coordinate_x_row = random.randint(0, num_rows - 1)
            self.initial_coordinate_y_col = random.randint(0, num_cols - 1)
            self.final_coordinate_x_row = random.randint(0, num_rows - 1)
            self.final_coordinate_y_col = random.randint(0, num_cols - 1)
            
            dist = abs(self.initial_coordinate_x_row - self.final_coordinate_x_row) + \
                   abs(self.initial_coordinate_y_col - self.final_coordinate_y_col)
            
            if dist >= min_dist_start_finish and \
               not (self.initial_coordinate_x_row == self.final_coordinate_x_row and \
                    self.initial_coordinate_y_col == self.final_coordinate_y_col):
                valid_points = True
            attempts +=1
        
        if not valid_points:
            print("Warning: Could not find start/finish points with sufficient distance. Using last attempt.")

        self.maze = Maze(self.screen, 
                           self.initial_coordinate_x_row, self.initial_coordinate_y_col, 
                           self.final_coordinate_x_row, self.final_coordinate_y_col,
                           start_cell_icon=self.start_cell_icon_surf, 
                           finish_cell_icon=self.finish_cell_icon_surf)
        
        self.player = Player(self.initial_coordinate_x_row, self.initial_coordinate_y_col)
        self.winner = False # Reset winner status for new game

    def update_game_state(self, events): # NEW/ENHANCED FOR STEP 2
        if self.winner or self.game_over: # For Step 3 game_over
            return

        if self.player:
            self.player.update(self.maze.maze, events)

        # Check win condition
        if self.player and \
           self.player.matrix_pos_x_row == self.final_coordinate_x_row and \
           self.player.matrix_pos_y_col == self.final_coordinate_y_col:
            if not self.winner: print("Winner!")
            self.winner = True
    
    def render_game_elements(self): # NEW/ENHANCED FOR STEP 2
        self.screen.fill(BLACK) 
        if self.maze:
            self.maze.render(self.screen)
        if self.player:
            self.player.render(self.screen)
        
        # Display win message
        if self.winner:
            text(self.screen, "MAZE COMPLETED!", BLUE, FONTSIZE_MESSAGE, 
                 center=True, coordinate_y=HEIGHT // 2)
        
        # Display basic controls at the bottom (part of info panel for Step 3)
        info_panel_y = HEIGHT + 10
        text(self.screen, "R: Restart", WHITE, FONTSIZE_CONTROLS, 10, info_panel_y)
        text(self.screen, "ESC: Exit", WHITE, FONTSIZE_CONTROLS, 120, info_panel_y)
        
        pygame.display.flip()


    def run(self): # ENHANCED FOR STEP 2
        self.setup_new_game()
        
        # For Step 1 & 2, we directly go into the game after DFS
        # Intro screen logic can be added in Step 3's Game.run
        self.screen.fill(BLACK) 
        # text(self.screen, "Generating Maze...", WHITE, FONTSIZE_STATUS + 10, center=True, coordinate_y=HEIGHT//2)
        # pygame.display.flip()
        if self.maze:
            self.maze.dfs(self.screen) 

        running = True
        while running:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    if event.key == pygame.K_r: 
                        self.setup_new_game()
                        self.screen.fill(BLACK)
                        # text(self.screen, "Re-generating Maze...", WHITE, FONTSIZE_STATUS + 10, center=True, coordinate_y=HEIGHT//2)
                        # pygame.display.flip()
                        if self.maze:
                             self.maze.dfs(self.screen)
            
            self.update_game_state(events) # Update player
            self.render_game_elements()    # Render maze, player, and messages
            
            self.clock.tick(30)

        pygame.quit()
        sys.exit()
        
def main():
    if not os.path.exists("assets"):
        os.makedirs("assets")
        print("Created 'assets' folder. Please place 'player.png', 'start.png', and 'finish.png' in it for Step 2.")
    else:
        required_step2_assets = ["player.png", "start.png", "finish.png"]
        missing_assets = [asset for asset in required_step2_assets if not os.path.exists(os.path.join("assets", asset))]
        if missing_assets:
            print(f"Warning: Missing asset files in 'assets' folder for Step 2: {', '.join(missing_assets)}")

    if not os.path.exists("fonts"):
        # os.makedirs("fonts") # Only create if you intend to provide the font
        print("Warning: 'fonts' folder not found. Game will use system default font if Orbitron is not available.")
    elif not os.path.exists(os.path.join("fonts", "Orbitron-VariableFont_wght.ttf")):
        print("Warning: Font file 'Orbitron-VariableFont_wght.ttf' not found in 'fonts' folder.")

    game_instance = Game()
    game_instance.run()

if _name_ == '_main_':
    main()
