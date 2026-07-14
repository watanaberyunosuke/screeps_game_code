import builder

from defs import *

__pragma__("noalias", "name")
__pragma__("noalias", "undefined")
__pragma__("noalias", "Infinity")
__pragma__("noalias", "keys")
__pragma__("noalias", "get")
__pragma__("noalias", "set")
__pragma__("noalias", "type")
__pragma__("noalias", "update")

SPAWN_OFFSETS = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]


def _place_spawn_site(room):
    controller = room.controller
    terrain = room.getTerrain()
    for dx, dy in SPAWN_OFFSETS:
        x = controller.pos.x + dx
        y = controller.pos.y + dy
        if x < 1 or x > 48 or y < 1 or y > 48:
            continue
        if terrain.get(x, y) & TERRAIN_MASK_WALL:
            continue
        if room.createConstructionSite(x, y, STRUCTURE_SPAWN) == OK:
            return


def run_pioneer(creep):
    """
    Runs a creep as a pioneer: travels to the target room, places a spawn construction
    site if needed, then works exactly like a builder until the room is self-sufficient.
    :param creep: The creep to run
    """
    target_room = creep.memory.target_room
    room = Game.rooms[target_room]

    if room:
        existing_spawn = _(room.find(FIND_MY_SPAWNS)).first()
        if existing_spawn:
            creep.memory.role = "builder"
            del creep.memory.target_room
            return

        if creep.room.name == target_room:
            existing_site = _(room.find(FIND_CONSTRUCTION_SITES)) \
                .filter(lambda cs: cs.structureType == STRUCTURE_SPAWN) \
                .first()
            if not existing_site:
                _place_spawn_site(room)

    if creep.room.name != target_room:
        creep.moveTo(__new__(RoomPosition(25, 25, target_room)))
        return

    builder.run_builder(creep)
