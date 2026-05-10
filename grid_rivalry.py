
import curses
import random
import time
import argparse

rows             = 10
cols             = 10
max_lives        = 3
threat_interval  = 0.5
spawn_interval   = 8


tools     = ["key", "wood_plank", "rock", "ladder", "parachute"]
obstacles = ["door", "lava", "dragon_obs", "up_cliff", "down_cliff"]
tool_map  = dict(zip(obstacles, tools))


obs_char = {
   "door":       ("D", "DOOR"),
   "lava":       ("L", "LAVA"),
   "dragon_obs": ("X", "DRGN"),
   "up_cliff":   ("^", "CLIF"),
   "down_cliff": ("V", "HOLE"),
}


tool_char = {
   "key":        ("k", "KEY "),
   "wood_plank": ("w", "PLNK"),
   "rock":       ("r", "ROCK"),
   "ladder":     ("l", "LADR"),
   "parachute":  ("p", "PARA"),
}


color_normal   = 1
color_player   = 2
color_tool     = 3
color_obstacle = 4
color_threat   = 5
color_goal     = 6
color_fog      = 7
color_status   = 8
color_header   = 9


def init_colors():
   """Registers all curses color pairs used throughout the game display."""
   curses.start_color()
   curses.use_default_colors()
   curses.init_pair(color_normal,   curses.COLOR_WHITE,  curses.COLOR_BLACK)
   curses.init_pair(color_player,   curses.COLOR_BLACK,  curses.COLOR_CYAN)
   curses.init_pair(color_tool,     curses.COLOR_BLACK,  curses.COLOR_GREEN)
   curses.init_pair(color_obstacle, curses.COLOR_WHITE,  curses.COLOR_RED)
   curses.init_pair(color_threat,   curses.COLOR_BLACK,  curses.COLOR_YELLOW)
   curses.init_pair(color_goal,     curses.COLOR_BLACK,  curses.COLOR_MAGENTA)
   curses.init_pair(color_fog,      curses.COLOR_BLACK,  curses.COLOR_BLACK)
   curses.init_pair(color_status,   curses.COLOR_YELLOW, curses.COLOR_BLACK)
   curses.init_pair(color_header,   curses.COLOR_CYAN,   curses.COLOR_BLACK)

class DifficultyManager:
    def __init__(self, level="easy"):
        self.level = level
        self.speed = 0.7 if level == "easy" else \
                     (0.4 if level == "medium" else 0.2)
        
    def get_spawn_rate(self):
        rates = {"easy": 10, "medium": 7, "hard": 5}
        return rates.get(self.level, 8)

class Player:
   """Represents the player's position, inventory, lives, and score."""


   def __init__(self):
       """Places the player at the top-left corner with 3 lives and an empty bag.
       Initializes Player object.
       
       Attributes: 
            r (int): player's starting row position
            c (int): player's starting collumn position 
            inventory (list of str): stores collected tools/items
            lives (int): player's starting number of lives
            score (int): player's starting score
       
        Side Effects: 
            Creates new Player instance with starting values  
       """
       self.r         = 0
       self.c         = 0
       self.inventory = []
       self.lives     = max_lives
       self.score     = 0


   def reset_position(self):
       """Moves the player back to the starting cell at row 0, column 0.
       
        Attributes: 
            r (int): player row position 
            c (int): player collumn position
            
        Side Effects: 
            resets Player's position only. 
       
       """
       self.r = 0
       self.c = 0


   def lose_life(self):
       """Subtracts one life and returns True if the player still has lives 
       remaining.
       
        Attributes: 
            lives (int): player's number of lives
       
        Side Effects; 
            subtracts 1 from Player object's lives attribute
       """
       self.lives -= 1
       return self.lives > 0

class Threat:
   """A moving enemy that roams the grid every half second and penalizes the 
    player on contact."""


   def __init__(self, char, name, penalty_type):
       """
       Sets up the threat with its display character, name, and penalty behavior.

        Args:
           char (str): single character shown on the grid for this threat
           name (str): human-readable name used in status messages
           penalty_type (str): one of 'steal', 'reset', or 'bomb'
           
        Attributes: 
            r (int): Threat's row position 
            c (int): Threat's column position 
            
        Side Effects: 
            Creates new Threat instance with its corresponding values and 
            starting position. 
       """
       self.char         = char
       self.name         = name
       self.penalty_type = penalty_type
       self.r            = random.randint(3, rows - 4)
       self.c            = random.randint(3, cols - 4)


   def roam(self, forbidden):
       """
        Moves one step in a random valid direction, skipping any forbidden cells.

        Args:
           forbidden: a set of (row, col) tuples the threat must not enter
           
        Attributes: 
            r (int): Threat row powisiton 
            c (int): Threat collumn position 
            
        Side Effects: 
            updates Threat object's position
       """
       directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
       random.shuffle(directions)
       for dr, dc in directions:
           nr, nc = self.r + dr, self.c + dc
           if 0 <= nr < rows and 0 <= nc < cols and (nr, nc) not in forbidden:
               self.r, self.c = nr, nc
               return


class GameWorld:
   """Holds the 10x10 grid and manages placement of tools, obstacles, and threats."""


   def __init__(self):
       """Creates the three threats first, then builds the grid so their cells 
       stay clear.
       
        Attributes:
            threats (int): collection of threat objects in the game 
            grid (int): grid created by _create_grid() module 
            
        Side Effects: 
            Creates 3 threat objects and builds gameworld grid. 
       """
       self.threats = [
           Threat("S", "Shadow", "steal"),
           Threat("G", "Ghost",  "reset"),
           Threat("B", "Bomber", "bomb"),
       ]
       self.grid = self._create_grid()


   def _create_grid(self):
       """
       Builds the 10x10 grid as a list of lists of dicts and randomly places
       all five tools and all five obstacles on cells that are not the start,
       goal, or any threat's starting position.


       Returns:
           A 10x10 list of dicts, each with keys 'obs', 'tool', and 'rev'.
       """
       grid = [
           [{"obs": None, "tool": None, "rev": False} for _ in range(cols)]
           for _ in range(rows)
       ]


       excluded = {(0, 0), (rows - 1, cols - 1)}
       for threat in self.threats:
           excluded.add((threat.r, threat.c))


       valid_cells = [
           (r, c)
           for r in range(rows)
           for c in range(cols)
           if (r, c) not in excluded
       ]
       random.shuffle(valid_cells)

       for tool in tools:
           r, c = valid_cells.pop()
           grid[r][c]["tool"] = tool


       for obs in obstacles:
           r, c = valid_cells.pop()
           grid[r][c]["obs"] = obs


       return grid

   def spawn_obstacle(self, player_pos):
       """
       Places one new random obstacle on a free, non-critical cell and marks it 
       revealed.


       Arguments:
           player_pos (tuple): row and col of the player's current position, which 
           is excluded
       """
       candidates = [
           (r, c)
           for r in range(rows)
           for c in range(cols)
           if self.grid[r][c]["obs"] is None
           and self.grid[r][c]["tool"] is None
           and (r, c) != player_pos
           and (r, c) != (rows - 1, cols - 1)
           and (r, c) != (0, 0)
       ]
       if candidates:
           r, c = random.choice(candidates)
           self.grid[r][c]["obs"] = random.choice(obstacles)
           self.grid[r][c]["rev"] = True




class Game:
   """
   Central controller that owns the game loop, input handling, turn logic,
   threat movement, and all terminal rendering via curses.
   """


   def __init__(self, stdscr, difficulty="easy"):
       """
       Initializes curses settings, creates the world and player, and sets
       the starting status message and internal timers.


        Arguments:
           stdscr: the curses standard screen object passed in by curses.wrapper
           
        Attributes:
            stdscr: the curses standard screen object for rendering/keyboard input
            player: represenging current player state 
            game_running (bool): boolean value, determining if game loop continues 
            status_msg (str): instruction/status message for player 
            move_count (int): counter tracking player moves 
            last_threat_time: Timestamp of last threat update 
        
        Side Effects: 
            Creates new GameWorld() and Player() objects. Turns off visibility of 
            cursor in the Terminal. Initializes curses color pairs with init_colors(). 
            records current system time with time.time() 
       """
       self.stdscr           = stdscr
       self.diff_settings    = DifficultyManager(difficulty)
       self.threat_interval  = self.diff_settings.speed
       self.spawn_rate       = self.diff_settings.get_spawn_rate()
       self.diff_name        = difficulty
       self.world            = GameWorld()
       self.player           = Player()
       self.game_running     = True
       self.status_msg       = "Find tools (green), avoid threats. Reach [*] to win!"
       self.move_count       = 0
       self.last_threat_time = time.time()


       curses.curs_set(0)
       stdscr.nodelay(True)
       stdscr.timeout(100)
       init_colors()


   def run(self):
       """Runs the main game loop: reads input, ticks threats on a timer, and 
        redraws each frame.
       
        Attributes: 
            game_running: Controls whether the game loop continues executing
            stdcr: Used to capture keyboard input through getch() and display
                    updated game frames
            last_threat_time: Stores the timestamp of the most recent threat 
                    movement update
            
        Side Effects: 
        Continuously redraws the game screen using self.draw().
        Reads player keyboard input with self.stdscr.getch().
        May update player position and game state through self._handle_input(key).
        Alters Threats position periodically through self._move_threats().
        Updates self.last_threat_time with the current system time.
        Displays the end-game screen by calling self._show_end_screen()
        after the loop exits.
        Continuously accesses system time using time.time().
       
       """
       while self.game_running:
           self.draw()
           key = self.stdscr.getch()
           self._handle_input(key)


           now = time.time()
           if now - self.last_threat_time >= self.threat_interval:
               self._move_threats()
               self.last_threat_time = now


       self._show_end_screen()


   def _handle_input(self, key):
       """
       Maps a pressed key to a movement direction and delegates to _process_turn,
       or sets game_running to False if the player presses Q.


       Arguments:
           key: integer key code returned by stdscr.getch()
           
        Attributes:  
            game_running (bool): Boolean flag controlling whether the game loop 
                                    should continue
        Side Effects: 
            May call self._process_turn(dr, dc) to update player movement, 
            advance the game state
            May cause the game loop to exit, setting self.game_running to False
            Interprets keyboard input using curses key constants
       """
       move_keys = {
           curses.KEY_UP:    (-1,  0),
           curses.KEY_DOWN:  ( 1,  0),
           curses.KEY_LEFT:  ( 0, -1),
           curses.KEY_RIGHT: ( 0,  1),
       }
       if key in move_keys:
           dr, dc = move_keys[key]
           self._process_turn(dr, dc)
       elif key in (ord("q"), ord("Q")):
           self.game_running = False


   def _process_turn(self, dr, dc):
       """
       Attempts to move the player one cell in the given direction.


       If the target cell holds an obstacle and the player has the matching tool,
       the tool is consumed and the obstacle is cleared. If the player lacks the
       tool, movement is blocked. Otherwise the player moves normally, picks up
       any tool present, and the win condition and threat collision are checked.
       A new obstacle spawns every spawn_interval moves.


       Args:
           dr: row delta (-1 for up, +1 for down, 0 for horizontal)
           dc: column delta (-1 for left, +1 for right, 0 for vertical)
           
       Attributes: 
           r (int): player row position
           c (int): player collumn position
           inventory (list of str): collection of tools/items held by player
           score (int): current player score
           grid (list of dicts): Mapping of obstacle names to the tool required to clear them
           move_count (int): Number of moves between obstacle spawns

       Side Effects: 
           Removes/adds to inventory, inspects cells on contact, moves player to new position, removes/spawns
           obstacles/collected tools on grid, updates player score.
       """
       p      = self.player
       nr, nc = p.r + dr, p.c + dc


       if not (0 <= nr < rows and 0 <= nc < cols):
           return


       target        = self.world.grid[nr][nc]
       target["rev"] = True


       if target["obs"]:
           obs    = target["obs"]
           needed = tool_map[obs]
           if needed in p.inventory:
               p.inventory.remove(needed)
               target["obs"] = None
               p.r, p.c      = nr, nc
               p.score      += 20
               self.status_msg = (
                   f"Used {needed.replace('_',' ')} to clear "
                   f"{obs.replace('_',' ')}! +20pts"
               )
           else:
               self.status_msg = (
                   f"Blocked by {obs.replace('_',' ')}! "
                   f"You need: {needed.replace('_',' ')}"
               )
           return


       p.r, p.c    = nr, nc
       cell        = self.world.grid[p.r][p.c]
       cell["rev"] = True


       if cell["tool"]:
           tool = cell["tool"]
           p.inventory.append(tool)
           cell["tool"]    = None
           p.score        += 10
           self.status_msg = (
               f"Picked up {tool.replace('_',' ')}! +10pts  "
               f"[{len(p.inventory)} item(s) in bag]"
           )


       if (p.r, p.c) == (rows - 1, cols - 1):
           self.game_running = False
           return


       self._check_threat_collision()


       self.move_count += 1
       if self.move_count % self.spawn_rate == 0:
           self.world.spawn_obstacle((p.r, p.c))
           self.status_msg = "A new obstacle appeared somewhere on the map!"


   def _move_threats(self):
       """Advances every threat one step and then checks whether any now overlap the player.
       
       Attributes: 
       self.world.threats (list): list of threats active in game world
       
       Side Effects: 
           Updates position of threats, prevents threats from entering specific cells on grid, 
           checks threat collision, may change player attributes/state depending on collision. 
       """
       forbidden = {(0, 0), (rows - 1, cols - 1)}
       for threat in self.world.threats:
           threat.roam(forbidden)
       self._check_threat_collision()


   def _check_threat_collision(self):
       """Scans all threats and triggers a penalty for any that share the player's cell.

       Attributes: 
           self.world.threats (list): list of threats active in game world

       Side Effects: 
           may reset player to start, subtract from player inventory or deduct a life using _apply_penalty()
           if player object comes in contact with threat. 
       """
       p = self.player
       for threat in self.world.threats:
           if (p.r, p.c) == (threat.r, threat.c):
               self._apply_penalty(threat)
               if not self.game_running:
                   return


   def _apply_penalty(self, threat):
       """
       Applies the specific penalty for a threat, resets the player to the start,
       deducts a life, and ends the game if no lives remain.


       Args:
           threat: the Threat instance that collided with the player

       Attributes: 
           penalty_type (str): "steal", "reset", or "bomb", description of type of penalty
           status_msg (f str): a message corresponding to its penalty type

       Side Effects: 
          may update status message and player status to its respective penalty_type. 
          Resets position of player using reset_position(). Discontinues game using game_running 
          if lives run out using p.lose_life(). 
       """
       p = self.player


       if threat.penalty_type == "steal" and p.inventory:
           stolen          = p.inventory.pop()
           self.status_msg = (
               f"[{threat.name}] caught you! Lost {stolen.replace('_',' ')}. "
               f"Back to start!"
           )
       elif threat.penalty_type == "reset":
           self.status_msg = f"[{threat.name}] caught you! Sent back to start!"
       elif threat.penalty_type == "bomb":
           p.inventory.clear()
           self.status_msg = f"[{threat.name}] wiped your bag! Back to start!"
       else:
           self.status_msg = f"[{threat.name}] caught you! Back to start!"


       p.reset_position()


       still_alive = p.lose_life()
       if not still_alive:
           self.game_running = False


   def draw(self):
       """Clears the terminal and redraws the header, grid, legend, and HUD each frame. 

       Side Effects: 
           calls methods for erasing stdscr, resets header, grid, legend, HUD, and refreshes game. 
       """
       self.stdscr.erase()
       self._draw_header()
       self._draw_grid()
       self._draw_legend()
       self._draw_hud()
       self.stdscr.refresh()


   def _draw_header(self):
       """Renders the game title bar centered across the top of the terminal.
       Attributes: 
           stdscr (curses): curses window for terminal rendering and outputs 
       
       Side Effects:
           Writes to stdout formatted/rendered/bolded/colored text 
           
       Raises: 
           curses.error: if drawing operations cannot be rendered/outside terminal boundaries. 
       """
       title = " GRID RIVALRY "
       try:
           self.stdscr.addstr(
               0, 0, title.center(60, "="),
               curses.color_pair(color_header) | curses.A_BOLD
           )
       except curses.error:
           pass


   def _draw_grid(self):
       """
       Iterates every cell in the 10x10 grid and renders it at the correct
       terminal position with the appropriate character and color.
       Rendering priority from highest to lowest:
           player > threat > goal > tool > obstacle > revealed empty > fog
       
       Attributes:
           world.grid: 2D game map containing cell dictionaries with information
           about tools, obstacles, and reveal status
           p.r (int): player row position
           p.c (int): player collumn position
           stdscr: curses window object for terminal rendering and outputs 

       
       Side Effects:
           Writes to stdout formatted/rendered/bolded/colored text with priorotized renderings
           
       Raises: 
           curses.error: if drawing operations cannot be rendered/outside terminal boundaries. 
       """
       start_row        = 2
       cell_width       = 6
       threat_positions = {(t.r, t.c): t for t in self.world.threats}
       p                = self.player


       for r in range(rows):
           for c in range(cols):
               cell    = self.world.grid[r][c]
               scr_r   = start_row + r
               scr_c   = c * cell_width
               is_goal = (r, c) == (rows - 1, cols - 1)


               if (r, c) == (p.r, p.c):
                   ch    = " Player "
                   color = curses.color_pair(color_player) | curses.A_BOLD
               elif (r, c) in threat_positions:
                   threat = threat_positions[(r, c)]
                   ch     = f" {threat.char} "
                   color  = curses.color_pair(color_threat) | curses.A_BOLD
               elif is_goal:
                   ch    = "[*]"
                   color = curses.color_pair(color_goal) | curses.A_BOLD
               elif cell["tool"]:
                   ch    = f"({tool_char[cell['tool']][0]})"
                   color = curses.color_pair(color_tool) | curses.A_BOLD
               elif cell["obs"]:
                   ch    = f"[{obs_char[cell['obs']][0]}]"
                   color = curses.color_pair(color_obstacle) | curses.A_BOLD
               elif cell["rev"]:
                   ch    = " . "
                   color = curses.color_pair(color_normal)
               else:
                   ch    = " ? "
                   color = curses.color_pair(color_fog) | curses.A_DIM


               try:
                   self.stdscr.addstr(
                       scr_r, scr_c,
                       ch.ljust(cell_width - 1) + "|",
                       color
                   )
               except curses.error:
                   pass


   def _draw_legend(self):
       """
       Renders the reference panel to the right of the grid showing the
       tool-obstacle pairs, threat descriptions, and symbol key.
       """
       legend_col = cols * 6 + 2
       row        = 2


       def put(r, text, pair=color_header):
           """Writes one line to the legend column, silently ignoring terminal overflow.

           Attributes: 
               stdscr: curses window object for terminal rendering and outputs 

           Raises: 
               curses.error: if drawing operations cannot be rendered/outside terminal boundaries. 
           """
           try:
               self.stdscr.addstr(r, legend_col, text, curses.color_pair(pair))
           except curses.error:
               pass


       put(row, "=== TOOLS ===")
       row += 1
       for obs, tool in tool_map.items():
           put(
               row,
               f"[{obs_char[obs][0]}]{obs_char[obs][1]} <- "
               f"({tool_char[tool][0]}){tool_char[tool][1]}",
               color_normal,
           )
           row += 1


       row += 1
       put(row, "=== THREATS ===")
       row += 1
       threat_descriptions = [
           ("S", "Shadow", "steals item"),
           ("G", "Ghost",  "resets pos"),
           ("B", "Bomber", "clears bag"),
       ]
       for char, name, effect in threat_descriptions:
           put(row, f" {char}  {name}: {effect}", color_status)
           row += 1


       row += 1
       put(row, "=== LEGEND ===")
       row += 1
       put(row, " @  You",          color_player)
       row += 1
       put(row, "(x) Tool",         color_tool)
       row += 1
       put(row, "[x] Obstacle",     color_obstacle)
       row += 1
       put(row, "[*] Exit (goal)",  color_goal)
       row += 1
       put(row, " ?  Unexplored",   color_fog)
       row += 1
       put(row, "Arrows = move",    color_normal)
       row += 1
       put(row, "Q = quit",         color_normal)

   def _draw_hud(self):
       """
       Renders the heads-up display below the grid showing lives, score,
       progress bar, current bag contents, and the latest status message.
       """
       p = self.player
       hud_row = rows + 3

       hearts    = "♥ " * p.lives + "♡ " * (max_lives - p.lives)
       lives_str = f" Lives: {hearts.strip()} "
       
       try:
           self.stdscr.addstr(
               hud_row, 0, lives_str,
               curses.color_pair(color_obstacle) | curses.A_BOLD
           )
       except curses.error:
           pass


       dist      = abs(p.r - (rows - 1)) + abs(p.c - (cols - 1))
       max_dist  = (rows - 1) + (cols - 1)
       filled    = int((1 - dist / max_dist) * 20)
       bar       = "[" + "#" * filled + "-" * (20 - filled) + "]"
       score_str = f"  Score: {p.score}   Progress: {bar}"
       try:
           self.stdscr.addstr(
               hud_row, len(lives_str), score_str,
               curses.color_pair(color_header)
           )
       except curses.error:
           pass

       hud_row += 1
       if p.inventory:
           bag_contents = "  ".join(
               f"({tool_char[t][0]}){t.replace('_',' ')}" for t in p.inventory
           )
           bag_str = f" Bag: {bag_contents} "
       else:
           bag_str = " Bag: (empty)  walk onto green cells to collect tools! "
       try:
           self.stdscr.addstr(hud_row, 0, bag_str, curses.color_pair(color_tool))
       except curses.error:
           pass


       hud_row += 1
       msg = self.status_msg[:78]
       try:
           self.stdscr.addstr(
               hud_row, 0,
               f" {msg} ".ljust(80),
               curses.color_pair(color_status)
           )
       except curses.error:
           pass
       
       hud_row += 1
       msg = f" {self.diff_name.upper()} | {self.status_msg}"[:79]
       try:
           self.stdscr.addstr(hud_row, 0, msg, curses.color_pair(color_status))
       except curses.error:
           pass


   def _show_end_screen(self):
       """Displays a win or game-over box centered on the screen and waits for a keypress before exiting
       Attributes:
           stdscr: curses window object for terminal rendering and outputs 
           p.r (int): player row pos
           p.c (int): player col pos
           p.score (int): player score displayed
           p.lives (int): player number of lives left displayed 

       Side Effects: 
           clears terminal display, renders status of player score/lives message, stops program until 
           user presses key, formats/color/bolds displayed text. 
       """
       self.stdscr.nodelay(False)
       self.stdscr.erase()
       p = self.player


       if (p.r, p.c) == (rows - 1, cols - 1):
           lines = [
               "+---------------------------------+",
               "|       YOU ESCAPED!              |",
               f"|  Final Score:  {p.score:<17}|",
               f"|  Lives Left:   {p.lives:<17}|",
               "|                                 |",
               "|  Press any key to exit          |",
               "+---------------------------------+",
           ]
           pair = curses.color_pair(color_goal) | curses.A_BOLD
       else:
           lines = [
               "+---------------------------------+",
               "|          GAME  OVER             |",
               f"|  Final Score:  {p.score:<17}|",
               "|                                 |",
               "|  Press any key to exit          |",
               "+---------------------------------+",
           ]
           pair = curses.color_pair(color_obstacle) | curses.A_BOLD


       start_r = rows // 2 - len(lines) // 2
       for i, line in enumerate(lines):
           try:
               self.stdscr.addstr(start_r + i, 10, line, pair)
           except curses.error:
               pass


       self.stdscr.refresh()
       self.stdscr.getch()

def get_args():
    """ ArgumentParser for terminal, used to specify difficulty in the game"""
    parser = argparse.ArgumentParser(description="Grid Rivalry")
    parser.add_argument(
        "--diff", 
        type=str, 
        choices=["easy", "medium", "hard"], 
        default="easy",
        help="Set the game difficulty"
    )
    return parser.parse_args()

def main(stdscr, difficulty="easy"):
    game = Game(stdscr, difficulty=difficulty)
    game.run()

if __name__ == "__main__":
    args = get_args()
    curses.wrapper(main, difficulty=args.diff)

