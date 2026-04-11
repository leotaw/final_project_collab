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