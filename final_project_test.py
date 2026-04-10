
"""" This is a test file for the collabrative project 
due wednesday morning. """
import random

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
