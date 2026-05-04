import tkinter as tk
import random
from tkinter import messagebox

"""
Final Project: Grid Rivalry
Description: A collaborative survival game integrating team-defined 
mechanics for world generation, tool usage, and movement physics.
"""

class Person: 
    """
    Represents a person involved in the game system, used for identity tracking.
    
    Attributes:
        name (str): The name of the player or collaborator.
        role (str): The designated role (e.g., 'Explorer').
    """
    def __init__(self, name, role="Explorer"):
        """
        Initializes the Person object with a name and a role.
        
        Args:
            name (str): The name of the person.
            role (str): The role they play in the game context.
        """
        self.name = name
        self.role = role

class movement:
    """
    Handles the coordinate logic and energy costs for entity movement.
        
    Attributes:
        stamina (int): Current energy level for moving.
        cost_per_move (int): Stamina consumed per successful step.
    """
    def __init__(self, start_stamina=100):
        """
        Initializes the movement physics with a starting stamina pool.
        
        Args:
            start_stamina (int): Total energy the player starts with.
        """
        self.stamina = start_stamina
        self.cost_per_move = 5

    def calculate_move(self, current_r, current_c, dr, dc):
        """
        Checks if movement is possible based on stamina and grid boundaries.
        
        Args:
            current_r (int): Current row position.
            current_c (int): Current column position.
            dr (int): Change in row.
            dc (int): Change in column.
            
        Returns:
            tuple: (int, int, bool) representing (new_r, new_c, success_status).
        """
        if self.stamina >= self.cost_per_move:
            new_r = current_r + dr
            new_c = current_c + dc
            if 0 <= new_r < 10 and 0 <= new_c < 10:
                self.stamina -= self.cost_per_move
                return new_r, new_c, True
        return current_r, current_c, False


# Global Constants
ROWS, COLS = 10, 10
CELL_SIZE = 60
TOOLS = ["key", "wood_plank", "rock", "ladder", "parachute"]
OBSTACLES = ["door", "lava", "dragon_obs", "up_clif", "down_clif"]
TOOL_MAP = dict(zip(OBSTACLES, TOOLS))
MAX_LIVES = 3
THREAT_SPEED = 600

OBS_ICON = {"door": "🚪", "lava": "🌋", "dragon_obs": "🐉", "up_clif": "⛰", "down_clif": "🕳"}
TOOL_ICON = {"key": "🔑", "wood_plank": "🪵", "rock": "🪨", "ladder": "🪜", "parachute": "🪂"}


def generate_world():
    """
    Randomly populates the grid with obstacles and tools while reserving corners.
    
    Returns:
        list: A 2D list (grid) containing cell dictionaries with item data.
    """
    grid = [[{"obstacle": None, "tool": None, "rev": False} for _ in range(COLS)] for _ in range(ROWS)]
    reserved = {(0, 0), (0, 1), (1, 0), (ROWS - 1, COLS - 1)}
    positions = [(r, c) for r in range(ROWS) for c in range(COLS) if (r, c) not in reserved]
    random.shuffle(positions)
    pairs = list(zip(OBSTACLES, TOOLS))
    
    for i, (obs, tool) in enumerate(pairs):
        grid[positions[i*2][0]][positions[i*2][1]]["obstacle"] = obs
        grid[positions[i*2+1][0]][positions[i*2+1][1]]["tool"] = tool
    return grid

def obtain_tool(inventory, cell, max_size=5):
    """
    Processes the collection of a tool from a specific grid cell.
    
    Args:
        inventory (list): The player's current list of tools.
        cell (dict): The data dictionary for the current grid tile.
        max_size (int): The inventory capacity.
        
    Returns:
        list: The updated inventory.
    """
    if cell.get("tool") and len(inventory) < max_size:
        inventory.append(cell["tool"])
        cell["tool"] = None
    return inventory

def Use_tool(inventory, cell, tool_map):
    """
    Checks for an obstacle and attempts to clear it using the inventory.
    
    Args:
        inventory (list): Current tools held by the player.
        cell (dict): The data dictionary for the current grid tile.
        tool_map (dict): Mapping of obstacles to required tools.
        
    Returns:
        tuple: (list, bool) representing the (updated_inventory, success_flag).
    """
    obs = cell.get("obstacle")
    if not obs: return inventory, True
    req = tool_map.get(obs)
    if req in inventory:
        inventory.remove(req)
        return inventory, True
    return inventory, False


class Player:
    """
    Main entity class representing the player in the game.
    
    Attributes:
        identity (Person): The Person object representing the player.
        physics (movement): The movement object handling stamina and position.
        icon (str): Visual emoji representation.
        inventory (list): Tools currently held.
        lives (int): Remaining lives.
    """
    def __init__(self, name, icon):
        """
        Initializes player state and creates movement/identity instances.
        
        Args:
            name (str): Name of the player.
            icon (str): Emoji icon.
        """
        self.identity = Person(name)
        self.physics = movement()
        self.icon = icon
        self.r, self.c = 0, 0
        self.inventory = []
        self.lives = MAX_LIVES
        self.score = 0

    def attempt_move(self, dr, dc):
        """
        Updates the player's position using the internal movement physics engine.
        
        Args:
            dr (int): Delta row.
            dc (int): Delta column.
            
        Returns:
            bool: True if the move was successful and within stamina limits.
        """
        self.r, self.c, success = self.physics.calculate_move(self.r, self.c, dr, dc)
        return success

class Threat:
    """
    A dynamic enemy that moves independently around the grid.
    
    Attributes:
        icon (str): Visual emoji for the threat.
        name (str): Name of the threat.
        penalty (str): The type of penalty applied on collision.
    """
    def __init__(self, icon, name, penalty):
        """Initializes threat with starting random position."""
        self.icon, self.name, self.penalty = icon, name, penalty
        self.r, self.c = random.randint(3, 8), random.randint(3, 8)

    def roam(self):
        """Moves the threat one tile in a random cardinal direction."""
        dr, dc = random.choice([(0,1),(0,-1),(1,0),(-1,0)])
        if 0 <= self.r+dr < ROWS and 0 <= self.c+dc < COLS:
            self.r += dr
            self.c += dc

class CompetitiveGameApp:
    """
    The main controller class for the Tkinter application and game loop.
    
    Attributes:
        root (tk.Tk): The main window instance.
        world_grid (list): The 2D grid of tiles.
        player (Player): The active player instance.
        threats (list): List of active threats.
    """
    def __init__(self, root):
        """Initializes UI, bindings, and starts the game tick."""
        self.root = root
        self.root.title("INST326: Grid Rivalry")
        self.world_grid = generate_world()
        self.player = Player("Simran", "🧑‍🚀")
        self.threats = [Threat("🐉", "Dragon", "steal"), Threat("💣", "Bomb", "bomb")]
        self.game_active = True

        self._setup_ui()
        self.root.bind("<Up>", lambda e: self.process_step(-1, 0))
        self.root.bind("<Down>", lambda e: self.process_step(1, 0))
        self.root.bind("<Left>", lambda e: self.process_step(0, -1))
        self.root.bind("<Right>", lambda e: self.process_step(0, 1))
        
        self.tick()

    def _setup_ui(self):
        """Initializes the Canvas and status bar labels."""
        self.canvas = tk.Canvas(self.root, width=COLS*CELL_SIZE, height=ROWS*CELL_SIZE, bg="#1a1a2e")
        self.canvas.pack()
        self.status = tk.Label(self.root, text="Stamina: 100 | Lives: 3", fg="white", bg="#16213e")
        self.status.pack(fill="x")

    def process_step(self, dr, dc):
        """
        Executes a turn when the player moves, checking for items and collisions.
        
        Args:
            dr (int): Vertical direction.
            dc (int): Horizontal direction.
        """
        if not self.game_active: return
        
        if self.player.attempt_move(dr, dc):
            cell = self.world_grid[self.player.r][self.player.c]
            cell["rev"] = True
            
            self.player.inventory = obtain_tool(self.player.inventory, cell)
            new_inv, clear = Use_tool(self.player.inventory, cell, TOOL_MAP)