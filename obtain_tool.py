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