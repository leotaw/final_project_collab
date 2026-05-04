
import tkinter as tk
import random
from tkinter import messagebox

"""
Final Project: Grid Rivalry (Fixed + Merged)
Author: Simran Shergill

Description:
Single-player survival grid game where the player must explore,
collect tools, overcome obstacles, and avoid moving threats to reach the goal.

Key Features:
- Fog of war exploration
- Tools always visible 
- Obstacles require specific tools 
- Moving threats with penalties + life system
- Inventory + score tracking
"""

# CONFIG
ROWS, COLS = 10, 10
CELL_SIZE = 60

TOOLS = ["key", "wood_plank", "rock", "ladder", "parachute"]
OBSTACLES = ["door", "lava", "dragon_obs", "up_cliff", "down_cliff"]
TOOL_MAP = dict(zip(OBSTACLES, TOOLS))

MAX_LIVES = 3
MAX_INVENTORY = 5
THREAT_SPEED = 600

OBS_ICON = {"door": "🚪", "lava": "🌋", "dragon_obs": "🐉",
            "up_cliff": "⛰", "down_cliff": "🕳"}

TOOL_ICON = {"key": "🔑", "wood_plank": "🪵", "rock": "🪨",
             "ladder": "🪜", "parachute": "🪂"}

# TEAM FUNCTIONS 
def use_tool(inventory, obstacle):
    """Checks if player has required tool and removes it if used."""
    needed = TOOL_MAP[obstacle]
    if needed in inventory:
        inventory.remove(needed)
        return inventory, True
    return inventory, False


def obtain_tool(inventory, cell):
    """Adds tool to inventory if valid and space available."""
    tool = cell.get("tool")
    if not tool:
        return inventory

    if tool not in inventory and len(inventory) < MAX_INVENTORY:
        inventory.append(tool)
        cell["tool"] = None
    return inventory


# PLAYER
class Player:
    """Represents the player with position, inventory, lives, and score."""

    def __init__(self):
        self.r, self.c = 0, 0
        self.inventory = []
        self.lives = MAX_LIVES
        self.score = 0


class Threat:
    """Enemy that moves randomly and applies penalties on collision."""

    def __init__(self, icon, penalty):
        self.icon = icon
        self.penalty = penalty
        self.r = random.randint(2, ROWS - 3)
        self.c = random.randint(2, COLS - 3)

    def move(self):
        """Moves threat randomly in one direction."""
        dr, dc = random.choice([(0,1),(0,-1),(1,0),(-1,0)])
        nr, nc = self.r + dr, self.c + dc
        if 0 <= nr < ROWS and 0 <= nc < COLS:
            self.r, self.c = nr, nc

class GameWorld:
    """Handles grid creation, tools, and obstacles."""

    def __init__(self):
        self.grid = self._create_grid()
        self.threats = [
            Threat("🐲", "steal"),
            Threat("👻", "reset"),
            Threat("💣", "wipe")
        ]

    def _create_grid(self):
        """Creates grid and randomly places paired tools + obstacles."""
        grid = [[{"obs": None, "tool": None, "rev": False}
                 for _ in range(COLS)] for _ in range(ROWS)]

        reserved = {(0,0), (ROWS-1, COLS-1)}
        positions = [(r,c) for r in range(ROWS) for c in range(COLS)
                     if (r,c) not in reserved]
        random.shuffle(positions)

        pairs = list(zip(OBSTACLES, TOOLS))
        random.shuffle(pairs)

        for i, (obs, tool) in enumerate(pairs):
            r1,c1 = positions[i*2]
            grid[r1][c1]["obs"] = obs

            r2,c2 = positions[i*2+1]
            grid[r2][c2]["tool"] = tool

        return grid


# ---------------------------------------------------------------------------
# GAME APP
# ---------------------------------------------------------------------------
class GameApp:
    """Main game controller handling UI, input, and game loop."""

    def __init__(self, root):
        self.root = root
        self.root.title("Grid Rivalry")

        self.world = GameWorld()
        self.player = Player()

        self.canvas = tk.Canvas(root, width=COLS*CELL_SIZE,
                                height=ROWS*CELL_SIZE)
        self.canvas.pack()

        self.status = tk.Label(root, text="Explore the grid!")
        self.status.pack()

        root.bind("<Key>", self.handle_key)

        self.loop()
        self.draw()

    # -------------------------------------------------------------------
    def handle_key(self, event):
        """Handles player movement input."""
        moves = {"Up":(-1,0),"Down":(1,0),"Left":(0,-1),"Right":(0,1)}
        if event.keysym not in moves:
            return

        dr, dc = moves[event.keysym]
        nr = self.player.r + dr
        nc = self.player.c + dc

        if not (0 <= nr < ROWS and 0 <= nc < COLS):
            return

        cell = self.world.grid[nr][nc]

        # HARD WALL OBSTACLE
        if cell["obs"]:
            _, success = use_tool(self.player.inventory, cell["obs"])
            if not success:
                needed = TOOL_MAP[cell["obs"]]
                self.status.config(text=f"Blocked! Need {needed}")
                return
            else:
                cell["obs"] = None
                self.status.config(text="Obstacle cleared!")

        # MOVE
        self.player.r, self.player.c = nr, nc
        cell["rev"] = True

        # TOOL PICKUP
        self.player.inventory = obtain_tool(self.player.inventory, cell)

        # CHECK THREAT COLLISION
        for t in self.world.threats:
            if (t.r, t.c) == (self.player.r, self.player.c):
                self.apply_penalty(t)

        self.draw()

    def apply_penalty(self, threat):
        """Applies threat penalty and resets player."""
        p = self.player

        if threat.penalty == "steal" and p.inventory:
            p.inventory.pop()
        elif threat.penalty == "wipe":
            p.inventory.clear()

        p.lives -= 1
        p.r, p.c = 0, 0

        if p.lives <= 0:
            messagebox.showinfo("Game Over", "You lost!")
            self.root.destroy()

    def loop(self):
        """Moves threats continuously."""
        for t in self.world.threats:
            t.move()
            if (t.r, t.c) == (self.player.r, self.player.c):
                self.apply_penalty(t)

        self.draw()
        self.root.after(THREAT_SPEED, self.loop)

    def draw(self):
        """Draws grid, tools, obstacles, threats, and player."""
        self.canvas.delete("all")

        for r in range(ROWS):
            for c in range(COLS):
                x, y = c*CELL_SIZE, r*CELL_SIZE
                cell = self.world.grid[r][c]

                color = "#0f2040" if not cell["rev"] else "#1e3a5f"
                self.canvas.create_rectangle(x,y,x+CELL_SIZE,y+CELL_SIZE,
                                             fill=color)

                if cell["tool"]:
                    self.canvas.create_text(x+30,y+30,
                        text=TOOL_ICON[cell["tool"]], font=("Arial",20))

                # SHOW OBSTACLES ONLY IF REVEALED
                if cell["obs"] and cell["rev"]:
                    self.canvas.create_text(x+30,y+30,
                        text=OBS_ICON[cell["obs"]], font=("Arial",20))

        # DRAW THREATS
        for t in self.world.threats:
            self.canvas.create_text(t.c*CELL_SIZE+30,
                                    t.r*CELL_SIZE+30,
                                    text=t.icon)

        # DRAW PLAYER
        self.canvas.create_text(self.player.c*CELL_SIZE+30,
                                self.player.r*CELL_SIZE+30,
                                text="🧑‍🚀", font=("Arial",20))


if __name__ == "__main__":
    root = tk.Tk()
    game = GameApp(root)
    root.mainloop()