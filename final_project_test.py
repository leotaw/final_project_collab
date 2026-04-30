
import random
import os
import sys

"""Constants """

ROWS = 10
COLS = 10
MAX_INVENTORY = 5

class Person: 
    """A person making the commit
    
    Attributes: 
        name (str): the Person's name
    """
    """Elizabeth made this commit"""
    
class movement:
    """ This is just a make believe part of the test file, but it involves movement
        
    Attributes:
        x, y: character positions
        Stamina(int): Energy for moving
        Movement will be up, down, left, and right.
         """
    """ DeMarcus made this commit"""
    
    
    
def generate_world():
    rows = 10 # still unsure what to do yet for this 
    cols = 10
    tools = ["key", "wood_plank", "rock", "ladder", "parachute"]
    obstacles = ["door", "lava", "dragon", "up_clif", "down_clif"]
    TOOL_MAP = dict(zip(obstacles, tools)) 
    
    #Build empty grid
    grid = [[{"obstacle": None, "tool": None} for _ in range(cols)]
            for _ in range(rows)]
    
    # Reserve corners: (0,0) player starts, (rows-1, cols-1) exit
    reserved = {(0, 0), (0, 1), (1, 0), (rows - 1, cols - 1)}
 
    # Collect valid positions
    positions = [(r, c) for r in range(rows) for c in range(cols)
                 if (r, c) not in reserved]
    random.shuffle(positions)
 
    
    
    obstacles_info = []
    tools_info = []
    for o in obstacles: 
        # adding random obstacles to info list
        e_number = random.randint(0, 4)
        e_item = obstacles[e_number]
        obstacles_info.append(e_item)
        # adding corresponding tools to info list
        t_item = tools[e_number]
        tools_info.append(t_item)

    #dictionary for each obstacle and tool for the world
    elements_info = {t:o for t,o in zip(tools_info, obstacles_info)}

    return elements_info

def Use_tool(inventory, cell, tool_map):
    """Confirms and processes the use of a tool to get pass an obstacle

    Args:
        inventory (list): A list of strings representing the players inventory
        cell (dict): the current location data
        tool_map (dict): A dictionary mapping obstacle names to their required 
        tools
        

    Raises:
        ValueError: If the player does not posses the specific tool required by
        the tool map

    Returns:
        _type_: (update_inventory, sucess_boolean)
            -update_inventory (list): The inventory after removing the used tool
            - sucess_boolean (bool): True if the obstacle was cleared or if 
            none existed
    """
    obstacle = cell.get('obstacle')
    
    if not obstacle:
        return inventory, True

    required_tool = tool_map.get(obstacle)
    tool_found_index = -1
    i = 0

    while i < len(inventory):
        if inventory[i] == required_tool:
            tool_found_index = i
            break
        i += 1

    if tool_found_index == -1:
        raise ValueError(f"Player lacks the required tool: {required_tool}")

    updated_inventory = []
    for j in range(len(inventory)):
        if j != tool_found_index:
            updated_inventory.append(inventory[j])

    return updated_inventory, True

def obtain_tool(inventory, cell, max_inventory_size):
    """
    Handles the process of a player picking up a tool from their
    current position in the world.

    Parameters:
        inventory (list of str): The tools currently held by the player.
        cell (dict): Represents the current cell and may contain a "tool" key.
        max_inventory_size (int): Maximum number of tools a player may carry.

    Returns:
        list of str: Updated inventory after attempting to collect the tool.

    Side Effects:
        Removes the tool from the cell if successfully collected.
    """

    valid_tools = ["key", "wood_plank", "rock", "ladder", "parachute"]

    if "tool" not in cell or cell["tool"] is None:
        return inventory

    tool = cell["tool"]

    if tool not in valid_tools:
        return inventory

    if tool in inventory:
        return inventory

    if len(inventory) >= max_inventory_size:
        return inventory

    inventory.append(tool)
    cell["tool"] = None

    return inventory
    
    
