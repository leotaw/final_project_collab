
import tkinter as tk
import random
from tkinter import messagebox

"""
Escape game 

Features:
- Fog of war exploration
- Tools always visible (even in fog)
- Obstacles require specific tools (hard walls)
- TAB key shows nearby obstacle requirements
- Moving threats with penalties
- Lives + inventory system
- Start + Finish clearly marked
"""

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

# ---------------- TEAM FUNCTIONS ----------------
def use_tool(inventory, obstacle):
    needed = TOOL_MAP[obstacle]
    if needed in inventory:
        inventory.remove(needed)
        return inventory, True
    return inventory, False


def obtain_tool(inventory, cell):
    tool = cell.get("tool")
    if not tool:
        return inventory
    if tool not in inventory and len(inventory) < MAX_INVENTORY:
        inventory.append(tool)
        cell["tool"] = None
    return inventory

class Player:
    """
    Represents the player in the game.

    Attributes:
        r (int): Current row position
        c (int): Current column position
        inventory (list): Tools collected by the player
        lives (int): Remaining lives
    """
    def __init__(self):
        self.r, self.c = 0, 0
        self.inventory = []
        self.lives = MAX_LIVES

class Threat:
    """
    Represents a moving enemy on the grid.

    Attributes:
        icon (str): Visual representation of the threat
        penalty (str): Type of penalty ('steal', 'wipe', 'reset')
        r (int): Row position
        c (int): Column position
    """
    def __init__(self, icon, penalty):
        self.icon = icon
        self.penalty = penalty
        self.r = random.randint(2, ROWS-3)
        self.c = random.randint(2, COLS-3)

    def move(self):
        """
        Moves the threat randomly one step in any direction
        within grid boundaries.
        """ 
        dr, dc = random.choice([(0,1),(0,-1),(1,0),(-1,0)])
        nr, nc = self.r + dr, self.c + dc
        if 0 <= nr < ROWS and 0 <= nc < COLS:
            self.r, self.c = nr, nc

class GameWorld:
    """
    Creates and manages the game grid.

    The grid stores:
        - obstacles (obs)
        - tools
        - revealed state (rev)
    """    
    def __init__(self):
        self.grid = self.create_grid()
        self.threats = [
            Threat("🐲","steal"),
            Threat("👻","reset"),
            Threat("💣","wipe")
        ]

    def create_grid(self):
        grid = [[{"obs":None,"tool":None,"rev":False}
                 for _ in range(COLS)] for _ in range(ROWS)]

        reserved = {(0,0),(ROWS-1,COLS-1)}
        positions = [(r,c) for r in range(ROWS) for c in range(COLS)
                     if (r,c) not in reserved]
        random.shuffle(positions)

        pairs = list(zip(OBSTACLES, TOOLS))
        random.shuffle(pairs)

        for i,(obs,tool) in enumerate(pairs):
            r1,c1 = positions[i*2]
            r2,c2 = positions[i*2+1]
            grid[r1][c1]["obs"] = obs
            grid[r2][c2]["tool"] = tool

        return grid

class GameApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Grid Rivalry")

        self.world = GameWorld()
        self.player = Player()

        self.canvas = tk.Canvas(root,
                                width=COLS*CELL_SIZE,
                                height=ROWS*CELL_SIZE)
        self.canvas.pack()

        self.status = tk.Label(root, text="Explore and survive!")
        self.status.pack()

        self.inv_label = tk.Label(root, text="Inventory: []")
        self.inv_label.pack()

        root.bind("<Key>", self.handle_key)
        root.bind("<Tab>", self.show_tool_helper)

        self.loop()
        self.draw()

    def handle_key(self, event):
        """
    Handles player movement based on key presses.

    Steps:
        1. Determine movement direction using dr, dc
        2. Check bounds
        3. Check obstacle interaction
        4. Move player
        5. Handle tool pickup
        6. Check win condition
        7. Check threat collisions
    """
        moves = {"Up":(-1,0),"Down":(1,0),"Left":(0,-1),"Right":(0,1)}
        if event.keysym not in moves:
            return

        dr, dc = moves[event.keysym]
        nr = self.player.r + dr
        nc = self.player.c + dc

        if not (0 <= nr < ROWS and 0 <= nc < COLS):
            return

        cell = self.world.grid[nr][nc]

        if cell["obs"]:
            _, success = use_tool(self.player.inventory, cell["obs"])
            if not success:
                needed = TOOL_MAP[cell["obs"]]
                self.status.config(
                    text=f"⛔ {cell['obs']} ahead! Press TAB → Need: {needed}"
                )
                return
            else:
                cell["obs"] = None
                self.status.config(text="✅ Obstacle cleared!")

        # move
        self.player.r, self.player.c = nr, nc
        cell["rev"] = True

        # pickup tool
        self.player.inventory = obtain_tool(self.player.inventory, cell)

        # win check
        if (nr, nc) == (ROWS-1, COLS-1):
            messagebox.showinfo("WIN", "🏆 You reached the finish!")
            self.root.destroy()
            return

        # threat collision
        for t in self.world.threats:
            if (t.r, t.c) == (nr, nc):
                self.apply_penalty(t)

        self.draw()

    def show_tool_helper(self, event=None):
        """
    Displays nearby obstacles and the required tools
    when the player presses the TAB key.
    """
        r, c = self.player.r, self.player.c
        nearby = []

        for dr,dc in [(0,1),(0,-1),(1,0),(-1,0)]:
            nr,nc = r+dr, c+dc
            if 0 <= nr < ROWS and 0 <= nc < COLS:
                obs = self.world.grid[nr][nc]["obs"]
                if obs:
                    nearby.append(f"{obs} → {TOOL_MAP[obs]}")

        msg = "\n".join(nearby) if nearby else "No nearby obstacles"
        messagebox.showinfo("Tool Helper", msg)

    def apply_penalty(self, threat):
        """
    Applies the effect of a threat collision.

    Effects:
        - Removes tools (depending on threat type)
        - Reduces player lives
        - Resets player to starting position
    """
        p = self.player

        if threat.penalty == "steal" and p.inventory:
            p.inventory.pop()
        elif threat.penalty == "wipe":
            p.inventory.clear()

        p.lives -= 1
        p.r, p.c = 0, 0

        self.status.config(text=f"💀 Hit by {threat.icon}! Lives: {p.lives}")

        if p.lives <= 0:
            messagebox.showinfo("Game Over", "You lost!")
            self.root.destroy()

    def loop(self):
        """
    Main game loop.

    Runs repeatedly to:
        - Move threats
        - Check collisions
        - Redraw the game
    """
        for t in self.world.threats:
            t.move()
            if (t.r, t.c) == (self.player.r, self.player.c):
                self.apply_penalty(t)

        self.draw()
        self.root.after(THREAT_SPEED, self.loop)
    
    
    def draw(self):
        """
    Renders the entire game state onto the canvas.

    Includes:
        - Grid cells
        - Start and finish tiles
        - Tools (always visible)
        - Obstacles (only when revealed)
        - Player
        - Threats
    """
        self.canvas.delete("all")

        for r in range(ROWS):
            for c in range(COLS):
                x, y = c * CELL_SIZE, r * CELL_SIZE
                cell = self.world.grid[r][c]

                is_start = (r, c) == (0, 0)
                is_goal = (r, c) == (ROWS - 1, COLS - 1)

                if is_start:
                    color = "#22c55e"
                elif is_goal:
                    color = "#fbbf24"
                elif not cell["rev"]:
                    color = "#0f2040"
                else:
                    color = "#1e3a5f"

                self.canvas.create_rectangle(
                    x, y, x + CELL_SIZE, y + CELL_SIZE,
                    fill=color
                )

                if is_start:
                    self.canvas.create_text(x+30, y+30, text="🏁")
                if is_goal:
                    self.canvas.create_text(x+30, y+30, text="🏆")

                if cell["tool"]:
                    self.canvas.create_oval(x+10, y+10, x+50, y+50,
                                            fill="#22c55e")
                    self.canvas.create_text(
                        x+30, y+30,
                        text=TOOL_ICON[cell["tool"]]
                    )

                if cell["obs"] and cell["rev"]:
                    self.canvas.create_text(
                        x+30, y+30,
                        text=OBS_ICON[cell["obs"]]
                    )

        for t in self.world.threats:
            self.canvas.create_text(
                t.c * CELL_SIZE + 30,
                t.r * CELL_SIZE + 30,
                text=t.icon
            )

        self.canvas.create_text(
            self.player.c * CELL_SIZE + 30,
            self.player.r * CELL_SIZE + 30,
            text="🧑‍🚀"
        )

        self.inv_label.config(text=f"Inventory: {self.player.inventory}")


if __name__ == "__main__":
    root = tk.Tk()
    GameApp(root)
    root.mainloop()