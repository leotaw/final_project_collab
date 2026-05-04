import tkinter as tk
import random

ROWS, COLS = 10, 10
tools     = ["key", "wood_plank", "rock", "ladder", "parachute"]
obstacles = ["door", "lava", "dragon", "up_cliff", "down_cliff"]
TOOL_MAP  = dict(zip(obstacles, tools))

OBS_ICON  = {"door":"🚪","lava":"🌋","dragon":"🐉","up_cliff":"⛰","down_cliff":"🕳"}
TOOL_ICON = {"key":"🔑","wood_plank":"🪵","rock":"🪨","ladder":"🪜","parachute":"🪂"}

COLORS = {
    "empty":    "#f5f5f0",
    "obstacle": "#fde8df",
    "tool":     "#e8f5e0",
    "both":     "#fef3d8",
    "exit":     "#dceefb",
    "player":   "#eeedfe",
}


def generate_world():
    grid = [[{"obstacle": None, "tool": None} for _ in range(COLS)] for _ in range(ROWS)]
    reserved = {(0,0),(0,1),(1,0),(ROWS-1,COLS-1)}
    positions = [(r,c) for r in range(ROWS) for c in range(COLS) if (r,c) not in reserved]
    random.shuffle(positions)
    pairs = list(zip(obstacles, tools))
    random.shuffle(pairs)
    for i, (obs, tool) in enumerate(pairs):
        r,c = positions[i*2];   grid[r][c]["obstacle"] = obs
        r,c = positions[i*2+1]; grid[r][c]["tool"]     = tool
    return grid


def draw_grid(canvas, grid, cell_size=60):
    canvas.delete("all")
    for r in range(ROWS):
        for c in range(COLS):
            x1, y1 = c*cell_size, r*cell_size
            x2, y2 = x1+cell_size, y1+cell_size
            cell = grid[r][c]

            # Pick background color
            if (r,c) == (0,0) or (r,c) == (0,1):
                bg = COLORS["player"]
            elif (r,c) == (ROWS-1, COLS-1):
                bg = COLORS["exit"]
            elif cell["obstacle"] and cell["tool"]:
                bg = COLORS["both"]
            elif cell["obstacle"]:
                bg = COLORS["obstacle"]
            elif cell["tool"]:
                bg = COLORS["tool"]
            else:
                bg = COLORS["empty"]

            canvas.create_rectangle(x1, y1, x2, y2, fill=bg, outline="#ccc", width=1)

            # Icon
            if (r,c) == (0,0):
                icon, label = "🧑", "P1"
            elif (r,c) == (0,1):
                icon, label = "🤖", "AI"
            elif (r,c) == (ROWS-1, COLS-1):
                icon, label = "🚪", "EXIT"
            elif cell["obstacle"] and cell["tool"]:
                icon  = OBS_ICON.get(cell["obstacle"], "?")
                label = cell["obstacle"][:6]
            elif cell["obstacle"]:
                icon  = OBS_ICON.get(cell["obstacle"], "?")
                label = cell["obstacle"][:6]
            elif cell["tool"]:
                icon  = TOOL_ICON.get(cell["tool"], "?")
                label = cell["tool"][:6]
            else:
                icon, label = "", f"{r},{c}"

            cx, cy = x1 + cell_size//2, y1 + cell_size//2
            canvas.create_text(cx, cy-8, text=icon, font=("Arial", 18))
            canvas.create_text(cx, cy+14, text=label, font=("Arial", 8), fill="#555")


def launch():
    grid_state = [generate_world()]   # mutable container so button can update it

    root = tk.Tk()
    root.title("generate_world() Preview")
    root.resizable(False, False)

    cell_size = 60
    width, height = COLS * cell_size, ROWS * cell_size

    # Legend bar
    legend = tk.Frame(root, bg="#fafafa", pady=6)
    legend.pack(fill="x", padx=10)
    items = [
        ("#fde8df", "Obstacle"),
        ("#e8f5e0", "Tool"),
        ("#fef3d8", "Both"),
        ("#dceefb", "Exit"),
        ("#eeedfe", "Player"),
        ("#f5f5f0", "Empty"),
    ]
    for color, label in items:
        box = tk.Label(legend, bg=color, width=2, relief="solid", bd=1)
        box.pack(side="left", padx=(6,2))
        tk.Label(legend, text=label, bg="#fafafa", font=("Arial", 10)).pack(side="left", padx=(0,8))

    # Canvas
    canvas = tk.Canvas(root, width=width, height=height, bg="#fff", highlightthickness=0)
    canvas.pack(padx=10, pady=6)
    draw_grid(canvas, grid_state[0], cell_size)

    # Tooltip label
    tip_var = tk.StringVar(value="Hover over a cell to inspect it")
    tip_label = tk.Label(root, textvariable=tip_var, font=("Arial", 10), fg="#555", bg="#fafafa")
    tip_label.pack(pady=(0, 4))

    # Hover tooltip
    def on_hover(event):
        c = event.x // cell_size
        r = event.y // cell_size
        if 0 <= r < ROWS and 0 <= c < COLS:
            cell = grid_state[0][r][c]
            if (r,c) == (0,0):
                tip_var.set("Player 1 start")
            elif (r,c) == (0,1):
                tip_var.set("Player 2 / AI start")
            elif (r,c) == (ROWS-1, COLS-1):
                tip_var.set("EXIT — both players must reach here")
            elif cell["obstacle"] and cell["tool"]:
                tip_var.set(f"Obstacle: {cell['obstacle']}  |  Tool here: {cell['tool']}  |  Need: {TOOL_MAP[cell['obstacle']]}")
            elif cell["obstacle"]:
                tip_var.set(f"Obstacle: {cell['obstacle']}  |  Required tool: {TOOL_MAP[cell['obstacle']]}")
            elif cell["tool"]:
                tip_var.set(f"Tool: {cell['tool']}  |  Clears: {[o for o,t in TOOL_MAP.items() if t==cell['tool']][0]}")
            else:
                tip_var.set(f"Empty cell ({r}, {c})")

    canvas.bind("<Motion>", on_hover)

    # Regenerate button
    def regenerate():
        grid_state[0] = generate_world()
        draw_grid(canvas, grid_state[0], cell_size)
        tip_var.set("New world generated!")

    btn = tk.Button(root, text="Regenerate World", command=regenerate,
                    font=("Arial", 11), padx=12, pady=6)
    btn.pack(pady=(0, 10))

    root.mainloop()


if __name__ == "__main__":
    launch()
