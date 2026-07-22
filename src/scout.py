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


def _pick_patrol_target(current_room_name):
    exits = Game.map.describeExits(current_room_name)
    best_name = None
    best_last_seen = None
    for direction in Object.keys(exits):
        neighbor = exits[direction]
        last_seen = _.get(Memory.rooms, [neighbor, "lastSeen"], 0)
        if best_name is None or last_seen < best_last_seen:
            best_name = neighbor
            best_last_seen = last_seen
    return best_name


def run_patrol_scout(creep):
    """
    Runs a creep as a patrol scout: continually wanders into whichever neighboring
    room has gone longest without a visit, refreshing Memory.rooms intel as it goes.
    :param creep: The creep to run
    """
    target_room = creep.memory.target_room

    if not target_room or creep.room.name == target_room:
        next_room = _pick_patrol_target(creep.room.name)
        if next_room:
            creep.memory.target_room = next_room
            target_room = next_room

    if target_room and creep.room.name != target_room:
        creep.moveTo(__new__(RoomPosition(25, 25, target_room)))
