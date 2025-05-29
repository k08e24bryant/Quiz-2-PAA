# Maze Game Project

## Description
"Maze Game" is a 2D game developed using Python and Pygame. Players must navigate a randomly generated maze from an Entry Point to a Goal while avoiding two chasing monsters. The game also features a "Show Solution" option that utilizes the BFS algorithm to display the shortest path. This project was created as part of the Quiz 2 for the Design & Analysis of Algorithms course.

## Key Features
* **Random Maze Generation**: Each game session presents a new, unique maze generated using the Depth-First Search (DFS) algorithm.
* **Player Character**: Players control a character represented by a PNG image (`player.png`).
* **Chasing Monsters**: Two monsters (`monster_1.png`, `monster_2.png`) with a simple AI will pursue the player through valid maze paths.
* **Visual Start and Finish Points**: The maze's entry and goal points are clearly marked with PNG icons (`start.png`, `finish.png`) directly on the game board.
* **Challenging Start/Finish Placement**: Start and finish points are ensured to be a minimum distance apart to enhance the challenge.
* **Maze Solution (BFS)**: Players can opt to see the shortest solution path from their current position to the goal, visualized using the Breadth-First Search (BFS) algorithm.
* **Informative User Interface**:
    * An initial screen to start the game.
    * An information panel below the maze displaying an icon legend (Player, Entry Point, Goal) and game controls.
    * Status messages for win, lose (caught by a monster), or when the solution is displayed.

## Algorithms Implemented
* **Depth-First Search (DFS)**: Used for the random generation of the maze structure. This algorithm explores as far as possible along each branch before backtracking, resulting in mazes with characteristic paths where all areas are connected.
* **Breadth-First Search (BFS)**: Implemented for the "Show Solution" feature. BFS explores the maze level by level from the player's position to find the shortest path (in terms of steps) to the goal.
* **Simple Monster AI (Distance-Based Greedy)**: Monsters determine their next move by evaluating all valid (connected) neighboring paths and choosing the one that results in the shortest Manhattan distance to the player. If multiple options are equally good, the monster chooses one randomly.

## Visuals

* Screenshot of the initial screen
![image](https://github.com/user-attachments/assets/44a8fd54-b4d0-4b29-9fbe-fca99e1172be)
* Screenshot of gameplay showing the player and monsters in the maze
![image](https://github.com/user-attachments/assets/8a54c527-4370-419d-9b73-a5a883ce040a)
* (Screenshot of the BFS "Show Solution" feature)
![image](https://github.com/user-attachments/assets/f3a4e14d-738c-4d62-926d-f0417c9ce400)


## Technologies Used
* **Programming Language**: Python (version 3.x)
* **Library**: Pygame (version 2.x) for graphics, sound (not yet implemented), and input handling
* **Standard Python Modules**: `os`, `sys`, `random`

## Getting Started

### Prerequisites
* Python 3.7 or higher.
* Pygame installed. You can install it using pip:
    ```bash
    pip install pygame
    ```

### Installation & Setup
1.  Clone this repository:
    ```bash
    git clone [https://github.com/k08e24bryant/Quiz-2-PAA.git](https://github.com/k08e24bryant/Quiz-2-PAA.git)
    ```
2.  Navigate to the project directory:
    ```bash
    cd Quiz-2-PAA 
    ```
    (or your appropriate folder name)
3.  Ensure you have an `assets` folder within the project directory containing the following image files:
    * `player.png`
    * `monster_1.png`
    * `monster_2.png`
    * `start.png`
    * `finish.png`
4.  Ensure you have a `fonts` folder within the project directory containing the font file:
    * `Orbitron-VariableFont_wght.ttf` (If not found, the game will use a default system font).

### Running the Game
To run the game, execute the main Python file from your terminal:
```bash
python maze.py
