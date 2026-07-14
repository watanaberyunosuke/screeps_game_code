from defs import *

__pragma__("noalias", "name")
__pragma__("noalias", "undefined")
__pragma__("noalias", "Infinity")
__pragma__("noalias", "keys")
__pragma__("noalias", "get")
__pragma__("noalias", "set")
__pragma__("noalias", "type")
__pragma__("noalias", "update")


def run_scout(creep):
    """
    Runs a creep as a scout: walks into the target room to grant vision, then sits still.
    :param creep: The creep to run
    """
    target_room = creep.memory.target_room
    if creep.room.name != target_room:
        creep.moveTo(__new__(RoomPosition(25, 25, target_room)))
