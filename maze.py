import sys
import os
import pygame
import random

# Colors
BLACK = (33, 33, 33)            # Charcoal (For borders)
DARKGRAY = (72, 72, 72)         # Graphite (For unvisited cells/walls)
YELLOW = (255, 223, 100)        # Soft Gold (For maze paths and broken borders)
WHITE = (245, 245, 245)         # For any text, if needed in this step

# Maze Configuration
BORDER_THICKNESS = 1.0
SIZE = 25  # Size of each cell

# Screen Dimensions
WIDTH = 600 # Maze area width
HEIGHT = 600 # Maze area height
# HEIGHT_TOTAL is not strictly needed for Step 1 as there's no info panel yet,
# but we can define it for consistency with later steps.
HEIGHT_TOTAL = 680 
SCREEN_SIZE = (WIDTH, HEIGHT) # Step 1 will only use the maze area height

# Font Sizes (only if text function is used for status)
FONTSIZE_STATUS = 20

def text(background, message, color, size, coordinate_x=None, coordinate_y=None, center=False, align_right=False):
    """
    Renders text on the given background surface.
    Not heavily used in Step 1 but included as requested.
    """
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
    """
    Represents a border segment of a Node.
    Developer A is responsible for this class.
    """
    def _init_(self, pos_x, pos_y, width, height):
        self.color = BLACK  # All borders start as black (solid walls)
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.width = width
        self.height = height

    def render(self, background):
        pygame.draw.rect(background, self.color, [self.pos_x, self.pos_y, self.width, self.height])

class Node():
    """
    Represents a single cell in the maze.
    Developer A is responsible for this class.
    """
    def _init_(self, screen_pos_x, screen_pos_y):
        self.color = DARKGRAY  # Default color for unvisited cells (walls)
        self.visited = False   # For DFS maze generation
        self.neighbors = []    # Potential neighbors for DFS
        self.neighbors_connected = [] # Actual connected neighbors (path exists) - for later steps
        self.parent = None     # For BFS path reconstruction - for later steps
        
        self.matrix_pos_x = 0  # Row index in the maze grid (will be set by Maze class)
        self.matrix_pos_y = 0  # Column index in the maze grid (will be set by Maze class)

        self.pos_x = screen_pos_x # Screen X coordinate (top-left)
        self.pos_y = screen_pos_y # Screen Y coordinate (top-left)
        self.width = SIZE
        self.height = SIZE

        # Borders
        self.top_border = NodeBorder(self.pos_x, self.pos_y, SIZE, BORDER_THICKNESS)
        self.bottom_border = NodeBorder(self.pos_x, self.pos_y + SIZE - BORDER_THICKNESS, SIZE, BORDER_THICKNESS)
        self.right_border = NodeBorder(self.pos_x + SIZE - BORDER_THICKNESS, self.pos_y, BORDER_THICKNESS, SIZE)
        self.left_border = NodeBorder(self.pos_x, self.pos_y, BORDER_THICKNESS, SIZE)
        
        self.special_icon = None # Placeholder for Step 2/3

    def render(self, background):
        # Draw base cell color
        pygame.draw.rect(background, self.color, [self.pos_x, self.pos_y, self.width, self.height])
        
        # Render borders on top
        self.top_border.render(background)
        self.bottom_border.render(background)
        self.right_border.render(background)
        self.left_border.render(background)

class Maze():
    """
    Manages the grid of Nodes and maze generation logic.
    Developer A is responsible for this class.
    """
    def _init_(self, background): # No icons passed in Step 1
        self.background_surface = background # Store for potential status text
        self.maze = []
        self.total_nodes = 0
        self.maze_created = False # Will be set to True after DFS
        
        self.num_rows = HEIGHT // SIZE
        self.num_cols = WIDTH // SIZE

        # Create the grid of Node objects
        for r_idx in range(self.num_rows):
            maze_row_list = []
            for c_idx in range(self.num_cols):
                current_screen_x = c_idx * SIZE
                current_screen_y = r_idx * SIZE
                node = Node(current_screen_x, current_screen_y)
                node.matrix_pos_x = r_idx # Set matrix position
                node.matrix_pos_y = c_idx # Set matrix position
                maze_row_list.append(node)
                self.total_nodes += 1
            self.maze.append(maze_row_list)
        
        self.define_neighbors()

    def add_edge(self, node, neighbor):
        # This function will be more relevant for BFS in later steps,
        # but DFS uses it to know which cells are connected.
        neighbor.neighbors_connected.append(node)
        node.neighbors_connected.append(neighbor)

    def remove_neighbors_visited(self, node):
        # Filters out neighbors that have already been visited by DFS
        node.neighbors = [n for n in node.neighbors if not n.visited]
    
    def define_neighbors(self):
        # Populates the .neighbors list for each node (potential connections)
        for r in range(self.num_rows):
            for c in range(self.num_cols):
                node = self.maze[r][c]
                node.neighbors = [] # Clear previous list
                # Top neighbor
                if r > 0: node.neighbors.append(self.maze[r - 1][c])
                # Bottom neighbor
                if r < self.num_rows - 1: node.neighbors.append(self.maze[r + 1][c])
                # Left neighbor
                if c > 0: node.neighbors.append(self.maze[r][c - 1])
                # Right neighbor
                if c < self.num_cols - 1: node.neighbors.append(self.maze[r][c + 1])
                                
    def break_border(self, node1, node2):
        # Changes the color of the border between node1 and node2 to YELLOW (path color)
        # node1 is current, node2 is the chosen neighbor
        
        # node2 is to the RIGHT of node1
        if node2.matrix_pos_y == node1.matrix_pos_y + 1 and node2.matrix_pos_x == node1.matrix_pos_x:
            node1.right_border.color = YELLOW
            node2.left_border.color = YELLOW
        # node2 is to the LEFT of node1
        elif node2.matrix_pos_y == node1.matrix_pos_y - 1 and node2.matrix_pos_x == node1.matrix_pos_x:
            node1.left_border.color = YELLOW
            node2.right_border.color = YELLOW
        # node2 is BELOW node1
        elif node2.matrix_pos_x == node1.matrix_pos_x + 1 and node2.matrix_pos_y == node1.matrix_pos_y:
            node1.bottom_border.color = YELLOW
            node2.top_border.color = YELLOW
        # node2 is ABOVE node1
        elif node2.matrix_pos_x == node1.matrix_pos_x - 1 and node2.matrix_pos_y == node1.matrix_pos_y:
            node1.top_border.color = YELLOW
            node2.bottom_border.color = YELLOW
    
    def _reset_maze_state(self):
        """ Helper to reset nodes for new maze generation. """
        for r in range(self.num_rows):
            for c in range(self.num_cols):
                node = self.maze[r][c]
                node.visited = False
                node.color = DARKGRAY # Reset to wall color
                node.neighbors_connected = [] # Clear connections
                node.parent = None
                # Reset borders to black
                node.top_border.color = BLACK
                node.bottom_border.color = BLACK
                node.left_border.color = BLACK
                node.right_border.color = BLACK
        self.define_neighbors() # Re-define potential neighbors

    def dfs(self, background_surface_for_text=None):
        """ Generates the maze using Depth-First Search algorithm. """
        self._reset_maze_state() # Ensure maze is clean before generation

        # Start DFS from a random cell
        start_row = random.randint(0, self.num_rows - 1)
        start_col = random.randint(0, self.num_cols - 1)
        current_cell = self.maze[start_row][start_col]
        
        current_cell.visited = True
        current_cell.color = YELLOW # Path cells are YELLOW
        stack = [current_cell]
        visited_cells = 1
        
        render_counter = 0
        # Render approximately 100 times during generation, or at least once per node if very small maze
        render_interval = max(1, self.total_nodes // 100 if self.total_nodes > 0 else 1) 

        while visited_cells < self.total_nodes or len(stack) > 0:
            if not stack: # Should ideally not happen if all cells are reachable
                # Attempt to find an unvisited cell if stack becomes empty (for disconnected components)
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
                    # This indicates a potential issue if not all cells were made reachable
                    print("Warning: DFS stack empty but not all cells visited. Maze might have isolated parts.")
                    break 
                if not stack: # Still no stack, means all processed or truly isolated
                     break

            current_cell = stack[-1] # Peek
            self.remove_neighbors_visited(current_cell) # Filter out already visited neighbors

            if len(current_cell.neighbors) > 0:
                random_neighbor = random.choice(current_cell.neighbors)
                self.break_border(current_cell, random_neighbor) # Breaks border, sets color to YELLOW
                self.add_edge(current_cell, random_neighbor) # For later use (BFS, monster AI)
                
                current_cell = random_neighbor # Move to the neighbor
                current_cell.visited = True
                current_cell.color = YELLOW # New path cell is YELLOW
                stack.append(current_cell)
                visited_cells += 1
            else: # No unvisited neighbors, backtrack
                # current_cell.color is already YELLOW as it's part of the path
                stack.pop()
            
            # Render periodically for visualization during generation
            render_counter += 1
            if render_counter >= render_interval or not stack: 
                if background_surface_for_text: # Only render text if surface provided
                    self.render(background_surface_for_text) # Render maze on the game's background
                    # Optional status text:
                    # text(background_surface_for_text, "Generating Maze...", WHITE, FONTSIZE_STATUS, 10, HEIGHT + 10)
                    pygame.display.update()
                render_counter = 0
        
        self.maze_created = True
        # Final render after DFS is complete (on the main game background)
        if background_surface_for_text:
            self.render(background_surface_for_text)
            pygame.display.update()


    def render(self, background):
        # Iterates through all nodes and calls their render method.
        # Specific coloring for start/end (BEIGE/LIGHTBLUE) is removed as per Step 1.
        # Path cells are YELLOW, walls are DARKGRAY, borders are BLACK/YELLOW.
        for r in range(self.num_rows):
            for c in range(self.num_cols):
                self.maze[r][c].render(background)

class Game():
    """
    Manages the main game loop and game states.
    Minimal version for Step 1. Developer A is responsible for this initial structure.
    """
    def _init_(self):
        try:
            pygame.init()
            pygame.font.init() # Initialize font module if text() is used
        except Exception as e:
            print(f'Error initializing Pygame: {e}')
            sys.exit(1)

        self.screen = pygame.display.set_mode(SCREEN_SIZE) # Use full screen size for consistency
        pygame.display.set_caption('Maze Game - Step 1: Framework')
        
        self.maze = None
        self.clock = pygame.time.Clock()

    def setup_new_game(self):
        # Instantiate the Maze object
        # Pass self.screen so Maze.dfs can update display during generation
        self.maze = Maze(self.screen) 

    def run(self):
        self.setup_new_game()
        
        # Display "Generating Maze..." text (optional)
        self.screen.fill(BLACK) # Clear screen
        # text(self.screen, "Generating Maze...", WHITE, FONTSIZE_STATUS + 10, center=True, coordinate_y=HEIGHT//2)
        # pygame.display.flip()

        self.maze.dfs(self.screen) # Generate the maze, pass screen for updates

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    if event.key == pygame.K_r: # Simple restart for testing Step 1
                        self.screen.fill(BLACK)
                        # text(self.screen, "Re-generating Maze...", WHITE, FONTSIZE_STATUS + 10, center=True, coordinate_y=HEIGHT//2)
                        # pygame.display.flip()
                        self.maze.dfs(self.screen)


            self.screen.fill(BLACK) # Clear screen before rendering maze
            if self.maze:
                self.maze.render(self.screen)
            
            pygame.display.flip() # Update the full display
            self.clock.tick(30) # Limit FPS

        pygame.quit()
        sys.exit()
        
def main():
    # Check for fonts folder (optional, as text() has a fallback)
    if not os.path.exists("fonts"):
        print("Warning: 'fonts' folder not found. Game will use system default font if text is displayed.")
    
    game_instance = Game()
    game_instance.run()

if  __name__ == '_main_':
    main()