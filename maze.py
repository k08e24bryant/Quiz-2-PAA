import sys
import os
import pygame
import random

# Colors
WHITE = (245, 245, 245)         # Mist White
BLACK = (33, 33, 33)            # Charcoal
RED = (255, 127, 80)            # Coral
GREEN = (144, 238, 144)         # Light Green (Old DFS active path color)
DARKGRAY = (72, 72, 72)         # Graphite (Default cell color, wall color)
YELLOW = (255, 223, 100)        # Soft Gold (Path color)
PINK = (255, 182, 193)          # Light Rose (BFS exploration)
BLUE = (0, 128, 128)            # Teal (Win message color)
ORANGE = (255, 140, 0)          # Deep Orange (BFS solution path)
LIGHTORANGE = (255, 204, 153)   # Apricot
LIGHTBLUE = (173, 216, 230)     # Powder Blue (Old Goal cell color for legend)
DARKBLUE = (54, 81, 94)         # Steel Blue (Intro background)
BEIGE = (245, 222, 179)         # Wheat (Old Start cell color for legend)
INTERMEDIARYORANGE = (255, 160, 122) # Light Salmon


# Maze Configuration
BORDER_THICKNESS = 1.0
SIZE = 25  # Size of each cell

# Screen Dimensions
WIDTH = 600 # Maze area width
HEIGHT = 600 # Maze area height
HEIGHT_TOTAL = 680 # Total screen height including info panel
SCREEN_SIZE = (WIDTH, HEIGHT_TOTAL)

# Font Sizes
FONTSIZE_START = 28
FONTSIZE_COMMANDS_INTIAL = 15
FONTSIZE_MAZE = 14

def text(background, message, color, size, coordinate_x=None, coordinate_y=None, center=False, align_right=False):
    font_path = os.path.join("fonts", "Orbitron-VariableFont_wght.ttf")
    try:
        font = pygame.font.Font(font_path, size)
    except FileNotFoundError:
        print(f"Warning: Font file '{font_path}' not found. Using default system font.")
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
    def __init__(self, pos_x, pos_y, width, height):
        self.color = BLACK
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.width = width
        self.height = height

    def render(self, background):
        pygame.draw.rect(background, self.color, [self.pos_x, self.pos_y, self.width, self.height])

class Node():
    def __init__(self, screen_pos_x, screen_pos_y):
        self.color = DARKGRAY 
        self.visited = False 
        self.explored = False
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
        self.special_icon = None 

    def render(self, background):
        pygame.draw.rect(background, self.color, [self.pos_x, self.pos_y, self.width, self.height])
        if self.special_icon:
            icon_x = self.pos_x + (self.width - self.special_icon.get_width()) // 2
            icon_y = self.pos_y + (self.height - self.special_icon.get_height()) // 2
            background.blit(self.special_icon, (icon_x, icon_y))
        self.top_border.render(background)
        self.bottom_border.render(background)
        self.right_border.render(background)
        self.left_border.render(background)

class Maze():
    def __init__(self, background, initial_x_row, initial_y_col, final_x_row, final_y_col, start_cell_icon=None, finish_cell_icon=None):
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
                maze_row_list.append(node)
                self.total_nodes += 1
            self.maze.append(maze_row_list)
        
        if start_cell_icon:
            start_node = self.maze[self.initial_coordinate_x_row][self.initial_coordinate_y_col]
            start_node.special_icon = start_cell_icon
            start_node.color = YELLOW 
        if finish_cell_icon:
            finish_node = self.maze[self.final_coordinate_x_row][self.final_coordinate_y_col]
            finish_node.special_icon = finish_cell_icon
            finish_node.color = YELLOW

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
                node.matrix_pos_x = r
                node.matrix_pos_y = c
                node.neighbors = []
                if r > 0: node.neighbors.append(self.maze[r - 1][c])
                if r < self.num_rows - 1: node.neighbors.append(self.maze[r + 1][c])
                if c > 0: node.neighbors.append(self.maze[r][c - 1])
                if c < self.num_cols - 1: node.neighbors.append(self.maze[r][c + 1])
                                
    def break_border(self, node1, node2, color_ignored=None):
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
    
    def dfs(self, background):
        # Reset all node colors to DARKGRAY (unvisited) before DFS
        for r_idx_reset in range(self.num_rows):
            for c_idx_reset in range(self.num_cols):
                node_to_reset = self.maze[r_idx_reset][c_idx_reset]
                node_to_reset.color = DARKGRAY
                node_to_reset.visited = False # Reset visited status
                node_to_reset.neighbors_connected = [] # Clear previous connections
                # Reset borders to black
                node_to_reset.top_border.color = BLACK
                node_to_reset.bottom_border.color = BLACK
                node_to_reset.left_border.color = BLACK
                node_to_reset.right_border.color = BLACK
                 # Keep special icons, but ensure their background will be correctly set by DFS
                if node_to_reset.special_icon:
                     if (r_idx_reset == self.initial_coordinate_x_row and c_idx_reset == self.initial_coordinate_y_col) or \
                        (r_idx_reset == self.final_coordinate_x_row and c_idx_reset == self.final_coordinate_y_col):
                         pass # Will be colored YELLOW by DFS pathing
                     else: # Should not happen if icons are only for start/finish
                         node_to_reset.color = DARKGRAY


        start_row = random.randint(0, self.num_rows - 1)
        start_col = random.randint(0, self.num_cols - 1)
        current_cell = self.maze[start_row][start_col]
        current_cell.visited = True
        current_cell.color = YELLOW
        
        stack = [current_cell]
        visited_cells = 1
        render_counter = 0
        render_interval = max(1, self.total_nodes // 100) 

        while visited_cells < self.total_nodes or len(stack) > 0:
            if not stack:
                found_unvisited = False
                for r_find in range(self.num_rows):
                    for c_find in range(self.num_cols):
                        if not self.maze[r_find][c_find].visited:
                            current_cell = self.maze[r_find][c_find]
                            current_cell.visited = True
                            current_cell.color = YELLOW 
                            stack.append(current_cell)
                            visited_cells +=1
                            found_unvisited = True
                            break
                    if found_unvisited: break
                if not found_unvisited and visited_cells < self.total_nodes:
                    print("Error: DFS stack empty but not all cells visited.")
                    break 
                if not stack: break

            current_cell = stack[-1]
            self.remove_neighbors_visited(current_cell) # Uses node.visited status

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
                self.render(background)
                text(background, "PREPARING YOUR CHALLENGE...", WHITE, FONTSIZE_COMMANDS_INTIAL + 5, coordinate_y=HEIGHT + 40, center=True)
                pygame.display.update()
                render_counter = 0
        
        # Ensure start/finish cells with icons have YELLOW background if visited
        start_node_final = self.maze[self.initial_coordinate_x_row][self.initial_coordinate_y_col]
        if start_node_final.special_icon and start_node_final.visited:
            start_node_final.color = YELLOW
        
        finish_node_final = self.maze[self.final_coordinate_x_row][self.final_coordinate_y_col]
        if finish_node_final.special_icon and finish_node_final.visited:
            finish_node_final.color = YELLOW

        self.maze_created = True
        self.render(background)
        pygame.display.update()

    def bfs(self, background, player):
        for r_idx in range(self.num_rows):
            for c_idx in range(self.num_cols):
                node = self.maze[r_idx][c_idx]
                node.explored = False
                node.parent = None
                if node.color == PINK or node.color == ORANGE:
                    node.color = YELLOW 

        initial_node = self.maze[player.matrix_pos_x_row][player.matrix_pos_y_col]
        initial_node.explored = True
        find = False
        queue = [initial_node]
        bfs_exploration_colors = {}

        while len(queue) > 0 and not find:
            u = queue.pop(0)
            if not u.special_icon and u != initial_node:
                 bfs_exploration_colors[(u.matrix_pos_x, u.matrix_pos_y)] = PINK
            
            for neighbor_node in u.neighbors_connected:
                if not neighbor_node.explored:
                    neighbor_node.parent = u
                    neighbor_node.explored = True
                    queue.append(neighbor_node)
                    if neighbor_node.matrix_pos_x == self.final_coordinate_x_row and \
                       neighbor_node.matrix_pos_y == self.final_coordinate_y_col:
                        find = True
                        break
            if find: break
            
            original_node_colors_backup = {} 
            for (r_bfs, c_bfs), temp_color in bfs_exploration_colors.items():
                node_to_color = self.maze[r_bfs][c_bfs]
                original_node_colors_backup[(r_bfs, c_bfs)] = node_to_color.color
                if not node_to_color.special_icon and node_to_color != initial_node: 
                    node_to_color.color = temp_color
            
            self.render(background)
            
            for (r_bfs, c_bfs), original_color in original_node_colors_backup.items(): 
                self.maze[r_bfs][c_bfs].color = original_color

            text(background, "SYSTEM SOLVING...", WHITE, FONTSIZE_COMMANDS_INTIAL + 5, coordinate_y=HEIGHT + 40, center=True)
            player.render(background)
            pygame.display.update()
            pygame.time.wait(10)

        if find:
            path_node = self.maze[self.final_coordinate_x_row][self.final_coordinate_y_col]
            while path_node.parent is not None and path_node != initial_node:
                if path_node != self.maze[self.final_coordinate_x_row][self.final_coordinate_y_col] and \
                   path_node != initial_node and not path_node.special_icon:
                    path_node.color = ORANGE
                path_node = path_node.parent
                
                self.render(background)
                player.render(background)
                text(background, "PATH REVEALED!", ORANGE, FONTSIZE_COMMANDS_INTIAL + 5, coordinate_y=HEIGHT + 40, center=True)
                pygame.display.update()
                pygame.time.wait(35)
        else:
            text(background, "NO PATH FOUND (ERROR?)", RED, FONTSIZE_COMMANDS_INTIAL + 5, coordinate_y=HEIGHT + 40, center=True)
            pygame.display.update()
            pygame.time.wait(1000)

    def render(self, background):
        for r_idx in range(self.num_rows):
            for c_idx in range(self.num_cols):
                self.maze[r_idx][c_idx].render(background)

class Player():
    def __init__(self, initial_x_row, initial_y_col, image_path="assets/player.png"):
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
            fallback_rect_pos_x = self.matrix_pos_y_col * SIZE + (SIZE - self.image_width) // 2 
            fallback_rect_pos_y = self.matrix_pos_x_row * SIZE + (SIZE - self.image_height) // 2
            pygame.draw.rect(background, self.fallback_color, 
                             [fallback_rect_pos_x, fallback_rect_pos_y, self.image_width, self.image_height])

class Monster():
    def __init__(self, start_row, start_col, image_path="assets/monster.png", move_delay=30):
        self.matrix_pos_x_row = start_row
        self.matrix_pos_y_col = start_col
        max_dim_scale = 0.8
        max_width = int(SIZE * max_dim_scale)
        max_height = int(SIZE * max_dim_scale)
        try:
            original_image = pygame.image.load(image_path).convert_alpha()
            original_width, original_height = original_image.get_size()
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
            self.image = pygame.transform.smoothscale(original_image, (self.image_width, self.image_height))
        except pygame.error as e:
            print(f"Error: Could not load monster image at '{image_path}': {e}")
            self.image = None
            self.image_width = int(SIZE * max_dim_scale) 
            self.image_height = int(SIZE * max_dim_scale)
        self.move_timer = 0
        self.move_delay = move_delay
        self._recalculate_screen_pos()

    def _recalculate_screen_pos(self):
        self.pos_x = self.matrix_pos_y_col * SIZE + (SIZE - self.image_width) // 2
        self.pos_y = self.matrix_pos_x_row * SIZE + (SIZE - self.image_height) // 2

    def render(self, background):
        if self.image:
            background.blit(self.image, (self.pos_x, self.pos_y))

    def update(self, player, maze_nodes):
        self.move_timer += 1
        if self.move_timer < self.move_delay:
            return 
        self.move_timer = 0
        possible_moves = []
        current_r, current_c = self.matrix_pos_x_row, self.matrix_pos_y_col
        current_node = maze_nodes[current_r][current_c]
        if not current_node.neighbors_connected:
            return 
        for neighbor_node in current_node.neighbors_connected:
            nr, nc = neighbor_node.matrix_pos_x, neighbor_node.matrix_pos_y
            dist_to_player = abs(nr - player.matrix_pos_x_row) + abs(nc - player.matrix_pos_y_col)
            possible_moves.append(((nr, nc), dist_to_player))
        if not possible_moves:
            return
        possible_moves.sort(key=lambda item: item[1])
        best_dist = possible_moves[0][1]
        equally_good_moves = [move_info for move_info in possible_moves if move_info[1] == best_dist]
        chosen_move_coords, _ = random.choice(equally_good_moves)
        best_next_r, best_next_c = chosen_move_coords
        self.matrix_pos_x_row = best_next_r
        self.matrix_pos_y_col = best_next_c
        self._recalculate_screen_pos()

class Game():
    def __init__(self):
        try:
            pygame.init()
            pygame.font.init()
        except Exception as e:
            print(f'Error initializing Pygame: {e}')
            sys.exit(1)
        self.background = None
        self.maze = None
        self.player = None
        self.initial_coordinate_x_row = 0
        self.initial_coordinate_y_col = 0
        self.final_coordinate_x_row = 0
        self.final_coordinate_y_col = 0
        self.start_game_flow = False
        self.solved_by_system = False
        self.winner = False
        self.exit_game = False
        self.monsters = []
        self.game_over = False
        self.num_monsters = 2
        self.legend_player_icon = None
        self.legend_start_icon = None
        self.legend_finish_icon = None
        self.legend_icon_size = int(SIZE * 0.8)
        self.start_cell_icon_surf = None 
        self.finish_cell_icon_surf = None 
        self.cell_icon_size = int(SIZE * 0.9)

    def _load_icons(self):
        try:
            player_img_orig = pygame.image.load("assets/player.png").convert_alpha()
            self.legend_player_icon = pygame.transform.smoothscale(player_img_orig, (self.legend_icon_size, self.legend_icon_size))
        except pygame.error as e: print(f"Error loading player.png for legend: {e}")
        try:
            start_img_orig = pygame.image.load("assets/start.png").convert_alpha()
            self.legend_start_icon = pygame.transform.smoothscale(start_img_orig, (self.legend_icon_size, self.legend_icon_size))
        except pygame.error as e: print(f"Error loading start.png for legend: {e}")
        try:
            finish_img_orig = pygame.image.load("assets/finish.png").convert_alpha()
            self.legend_finish_icon = pygame.transform.smoothscale(finish_img_orig, (self.legend_icon_size, self.legend_icon_size))
        except pygame.error as e: print(f"Error loading finish.png for legend: {e}")
        try:
            start_cell_orig = pygame.image.load("assets/start.png").convert_alpha()
            self.start_cell_icon_surf = pygame.transform.smoothscale(start_cell_orig, (self.cell_icon_size, self.cell_icon_size))
        except pygame.error as e: print(f"Error loading start.png for maze cell: {e}")
        try:
            finish_cell_orig = pygame.image.load("assets/finish.png").convert_alpha()
            self.finish_cell_icon_surf = pygame.transform.smoothscale(finish_cell_orig, (self.cell_icon_size, self.cell_icon_size))
        except pygame.error as e: print(f"Error loading finish.png for maze cell: {e}")

    def setup_new_game(self):
        self.background = pygame.display.set_mode(SCREEN_SIZE)
        pygame.display.set_caption('Maze Game with Monsters')
        self._load_icons() 
        num_rows = HEIGHT // SIZE
        num_cols = WIDTH // SIZE
        
        # Ensure start and finish points are sufficiently far apart
        min_dist_start_finish = (num_rows + num_cols) // 4 # Heuristic for minimum distance
        while True:
            self.initial_coordinate_x_row = random.randint(0, num_rows - 1)
            self.initial_coordinate_y_col = random.randint(0, num_cols - 1)
            self.final_coordinate_x_row = random.randint(0, num_rows - 1)
            self.final_coordinate_y_col = random.randint(0, num_cols - 1)
            
            # Calculate Manhattan distance
            dist = abs(self.initial_coordinate_x_row - self.final_coordinate_x_row) + \
                   abs(self.initial_coordinate_y_col - self.final_coordinate_y_col)
            
            if dist >= min_dist_start_finish and \
               not (self.initial_coordinate_x_row == self.final_coordinate_x_row and \
                    self.initial_coordinate_y_col == self.final_coordinate_y_col): # Ensure not same cell
                break # Found suitable points

        self.maze = Maze(self.background, 
                           self.initial_coordinate_x_row, self.initial_coordinate_y_col, 
                           self.final_coordinate_x_row, self.final_coordinate_y_col,
                           start_cell_icon=self.start_cell_icon_surf, 
                           finish_cell_icon=self.finish_cell_icon_surf)
        self.player = Player(self.initial_coordinate_x_row, self.initial_coordinate_y_col)
        self.solved_by_system = False
        self.winner = False
        self.game_over = False
        self.monsters = []     
        spawned_monster_positions = []
        for i in range(self.num_monsters):
            monster_row, monster_col = -1, -1
            valid_spawn = False
            attempts = 0 
            max_attempts = num_rows * num_cols 
            while not valid_spawn and attempts < max_attempts:
                attempts += 1
                monster_row = random.randint(0, num_rows - 1)
                monster_col = random.randint(0, num_cols - 1)
                on_player_start = (monster_row == self.initial_coordinate_x_row and \
                                   monster_col == self.initial_coordinate_y_col)
                on_player_goal = (monster_row == self.final_coordinate_x_row and \
                                  monster_col == self.final_coordinate_y_col)
                on_other_monster = False
                for M_pos_r, M_pos_c in spawned_monster_positions:
                    if monster_row == M_pos_r and monster_col == M_pos_c:
                        on_other_monster = True
                        break
                if not on_player_start and not on_player_goal and not on_other_monster:
                    distance_to_player = abs(monster_row - self.initial_coordinate_x_row) + \
                                         abs(monster_col - self.initial_coordinate_y_col)
                    if distance_to_player > 7: # Min distance from player start for monster spawn
                        valid_spawn = True
            if valid_spawn: 
                if i == 0: 
                    monster_image_path = "assets/monster_1.png"
                elif i == 1: 
                    monster_image_path = "assets/monster_2.png"
                else: 
                    monster_image_path = "assets/monster.png" 
                new_monster = Monster(monster_row, monster_col, image_path=monster_image_path, move_delay=random.randint(25, 30 + i*5))
                self.monsters.append(new_monster)
                spawned_monster_positions.append((monster_row, monster_col))
            else:
                print(f"Warning: Could not find a valid spawn position for monster {i+1} after {max_attempts} attempts.")

    def update_game_state(self, events):
        if self.game_over or self.winner or self.solved_by_system:
            return
        self.player.update(self.maze.maze, events)
        for monster_obj in self.monsters:
            monster_obj.update(self.player, self.maze.maze)
        if self.player.matrix_pos_x_row == self.final_coordinate_x_row and \
           self.player.matrix_pos_y_col == self.final_coordinate_y_col:
            if not self.winner: print("Winner!")
            self.winner = True
            return
        for monster_obj in self.monsters:
            if self.player.matrix_pos_x_row == monster_obj.matrix_pos_x_row and \
               self.player.matrix_pos_y_col == monster_obj.matrix_pos_y_col:
                print("Game Over - Caught by Monster!")
                self.game_over = True
                return

    def initial_screen(self):
        self.background.fill(DARKBLUE)
        pygame.draw.rect(self.background, BEIGE, [40, 40, WIDTH - 80, HEIGHT_TOTAL - 80])
        pygame.draw.rect(self.background, LIGHTBLUE, [40, 100, WIDTH - 80, HEIGHT_TOTAL - 220])
        pygame.draw.rect(self.background, BLACK, [110, 150, WIDTH - 220, HEIGHT_TOTAL - 350])
        pygame.draw.rect(self.background, DARKBLUE, [110, 150, WIDTH - 220, 100])
        text(self.background, "ESCAPE THE MAZE", LIGHTORANGE, FONTSIZE_START, coordinate_y=197, center=True)
        text(self.background, "(ESC) TO EXIT ADVENTURE", INTERMEDIARYORANGE, FONTSIZE_COMMANDS_INTIAL, coordinate_y=HEIGHT_TOTAL - 150, center=True)
        pygame.display.update()
        pygame.time.wait(180)
        text(self.background, "READY? PRESS (S) TO START!", INTERMEDIARYORANGE, FONTSIZE_COMMANDS_INTIAL, coordinate_y=HEIGHT_TOTAL - 175, center=True)
        pygame.display.update()
        pygame.time.wait(180)

    def render_game_elements(self):
        self.background.fill(BLACK)
        self.maze.render(self.background)
        self.player.render(self.background)
        for monster_obj in self.monsters:
            monster_obj.render(self.background)
        try:
            arial_font = pygame.font.SysFont("arial", FONTSIZE_MAZE)
            arial_font_bigger = pygame.font.SysFont("arial", FONTSIZE_MAZE + 6)
        except Exception as e:
            print(f"Error loading system font: {e}")
            arial_font = pygame.font.Font(None, FONTSIZE_MAZE + 3)
            arial_font_bigger = pygame.font.Font(None, FONTSIZE_MAZE + 9)

        def draw_text_arial(surface, msg, color, font, x, y, align_right=False, center=False):
            text_surface_arial = font.render(msg, True, color)
            text_rect_arial = text_surface_arial.get_rect()
            if center: text_rect_arial.center = (x, y)
            elif align_right: text_rect_arial.topright = (x, y)
            else: text_rect_arial.topleft = (x, y)
            surface.blit(text_surface_arial, text_rect_arial)

        base_info_y = HEIGHT + 5
        icon_x_pos = 5 
        text_x_offset = icon_x_pos + self.legend_icon_size + 5 
        icon_y_center_offset = (self.legend_icon_size - FONTSIZE_MAZE) // 2

        if self.game_over:
            draw_text_arial(self.background, "GAME OVER - CAUGHT!", RED, arial_font_bigger, WIDTH // 2, HEIGHT + (HEIGHT_TOTAL - HEIGHT) // 2 - 10, center=True)
            draw_text_arial(self.background, "R → TRY AGAIN", WHITE, arial_font, WIDTH - 15, HEIGHT + 30, align_right=True)
            draw_text_arial(self.background, "ESC → EXIT", WHITE, arial_font, WIDTH - 15, HEIGHT + 50, align_right=True)
        elif self.winner:
            draw_text_arial(self.background, "MAZE COMPLETED!", BLUE, arial_font_bigger, WIDTH // 2, HEIGHT + (HEIGHT_TOTAL - HEIGHT) // 2 - 10, center=True)
            draw_text_arial(self.background, "R → TRY AGAIN", WHITE, arial_font, WIDTH - 15, HEIGHT + 30, align_right=True)
            draw_text_arial(self.background, "ESC → EXIT", WHITE, arial_font, WIDTH - 15, HEIGHT + 50, align_right=True)
        elif self.solved_by_system:
            draw_text_arial(self.background, "MAZE SOLVED BY SYSTEM!", PINK, arial_font_bigger, WIDTH // 2, HEIGHT + (HEIGHT_TOTAL - HEIGHT) // 2 -10, center=True)
            draw_text_arial(self.background, "R → TRY AGAIN", WHITE, arial_font, WIDTH - 15, HEIGHT + 30, align_right=True)
            draw_text_arial(self.background, "ESC → EXIT", WHITE, arial_font, WIDTH - 15, HEIGHT + 50, align_right=True)
        else: 
            current_y = base_info_y
            if self.legend_player_icon:
                self.background.blit(self.legend_player_icon, (icon_x_pos, current_y))
            else: pygame.draw.rect(self.background, RED, [icon_x_pos, current_y, self.legend_icon_size, self.legend_icon_size]) 
            draw_text_arial(self.background, "- YOU (AVOID MONSTERS!)", WHITE, arial_font, text_x_offset, current_y + icon_y_center_offset)
            current_y += self.legend_icon_size + 5
            if self.legend_start_icon:
                self.background.blit(self.legend_start_icon, (icon_x_pos, current_y))
            else: pygame.draw.rect(self.background, BEIGE, [icon_x_pos, current_y, self.legend_icon_size, self.legend_icon_size])
            draw_text_arial(self.background, "- ENTRY POINT", WHITE, arial_font, text_x_offset, current_y + icon_y_center_offset)
            current_y += self.legend_icon_size + 5
            if self.legend_finish_icon:
                self.background.blit(self.legend_finish_icon, (icon_x_pos, current_y))
            else: pygame.draw.rect(self.background, LIGHTBLUE, [icon_x_pos, current_y, self.legend_icon_size, self.legend_icon_size])
            draw_text_arial(self.background, "- GOAL", WHITE, arial_font, text_x_offset, current_y + icon_y_center_offset)
            controls_text_y = base_info_y + 5
            draw_text_arial(self.background, "R → TRY AGAIN", WHITE, arial_font, WIDTH - 15, controls_text_y, align_right=True)
            draw_text_arial(self.background, "Q → SHOW SOLUTION", WHITE, arial_font, WIDTH - 15, controls_text_y + 15, align_right=True)
            draw_text_arial(self.background, "ESC → EXIT GAME", WHITE, arial_font, WIDTH - 15, controls_text_y + 30, align_right=True)
        pygame.display.update()

    def run(self):
        self.setup_new_game()
        while not self.start_game_flow and not self.exit_game:
            self.initial_screen()
            for event in pygame.event.get():
                if event.type == pygame.QUIT: self.exit_game = True
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE: self.exit_game = True
                    if event.key == pygame.K_s: self.start_game_flow = True
            pygame.display.update()
        if self.exit_game: pygame.quit(); sys.exit(0)

        self.background.fill(BLACK)
        self.maze.dfs(self.background)
        self.render_game_elements()

        clock = pygame.time.Clock()
        while not self.exit_game:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT: self.exit_game = True
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE: self.exit_game = True
                    if event.key == pygame.K_r:
                        self.setup_new_game()
                        self.background.fill(BLACK)
                        self.maze.dfs(self.background)
                    if not self.game_over and not self.solved_by_system and not self.winner and event.key == pygame.K_q:
                        self.background.fill(BLACK)
                        self.maze.bfs(self.background, self.player)
                        self.solved_by_system = True
            if not self.exit_game:
                self.update_game_state(events) 
                self.render_game_elements()
            clock.tick(30)
        pygame.quit()
        sys.exit(0)
        
def main():
    if not os.path.exists("assets"):
        os.makedirs("assets")
        print("Created 'assets' folder. Please place 'player.png', 'monster_1.png', 'monster_2.png', 'start.png', and 'finish.png' in it.")
    else:
        required_assets = ["player.png", "monster_1.png", "monster_2.png", "start.png", "finish.png"]
        missing_assets = [asset for asset in required_assets if not os.path.exists(os.path.join("assets", asset))]
        if missing_assets:
            print(f"Warning: Missing asset files in 'assets' folder: {', '.join(missing_assets)}")

    if not os.path.exists("fonts"):
        os.makedirs("fonts")
        print("Created 'fonts' folder. Please place 'Orbitron-VariableFont_wght.ttf' in it.")
    elif not os.path.exists(os.path.join("fonts", "Orbitron-VariableFont_wght.ttf")):
        print("Warning: Font file 'Orbitron-VariableFont_wght.ttf' not found in 'fonts' folder.")

    mygame = Game()
    mygame.run()

if __name__ == '__main__':
    main()