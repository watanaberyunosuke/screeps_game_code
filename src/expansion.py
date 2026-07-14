from defs import *

__pragma__("noalias", "name")
__pragma__("noalias", "undefined")
__pragma__("noalias", "Infinity")
__pragma__("noalias", "keys")
__pragma__("noalias", "get")
__pragma__("noalias", "set")
__pragma__("noalias", "type")
__pragma__("noalias", "update")

PIONEER_COUNT = 2


def _my_username():
    for name in Object.keys(Game.spawns):
        return Game.spawns[name].owner.username
    return None


def _owned_room_names():
    names = []
    for name in Object.keys(Game.rooms):
        room = Game.rooms[name]
        if room.controller and room.controller.my:
            names.append(name)
    return names


def _find_expansion_target(ruled_out):
    owned = _owned_room_names()
    for room_name in owned:
        exits = Game.map.describeExits(room_name)
        for direction in Object.keys(exits):
            neighbor = exits[direction]
            if _.includes(owned, neighbor) or _.includes(ruled_out, neighbor):
                continue
            return neighbor
    return None


def _count_creeps_for(role, target_room):
    return _.sum(
        Game.creeps,
        lambda c: c.memory.role == role and c.memory.target_room == target_room,
    )


def _init_state():
    if not Memory.expansion:
        Memory.expansion = {"state": "idle", "target_room": None, "ruled_out": []}
    return Memory.expansion


def _handle_scouting(state, target_room):
    room = Game.rooms[target_room]
    if room:
        controller = room.controller
        my_name = _my_username()
        occupied = (
            not controller
            or (controller.owner and not controller.my)
            or (controller.reservation and controller.reservation.username != my_name)
        )
        if occupied:
            state.ruled_out.append(target_room)
            state.state = "idle"
            state.target_room = None
        else:
            state.state = "claiming"
        return None

    if _count_creeps_for("scout", target_room) == 0:
        return [MOVE], {"role": "scout", "target_room": target_room}
    return None


def _handle_claiming(state, target_room):
    room = Game.rooms[target_room]
    if room and room.controller and room.controller.my:
        state.state = "pioneering"
        return None

    if _count_creeps_for("claimer", target_room) == 0:
        return [CLAIM, MOVE], {"role": "claimer", "target_room": target_room}
    return None


def _handle_pioneering(state, target_room):
    room = Game.rooms[target_room]
    if room:
        existing_spawn = _(room.find(FIND_MY_SPAWNS)).first()
        if existing_spawn:
            state.state = "idle"
            state.target_room = None
            return None

    if _count_creeps_for("pioneer", target_room) < PIONEER_COUNT:
        return [WORK, CARRY, MOVE, MOVE], {
            "role": "pioneer",
            "target_room": target_room,
            "building": False,
        }
    return None


def get_next_spawn_order(coordinator_room):
    """
    Returns the next (body, memory) expansion creep to spawn, or None.
    :param coordinator_room: The room deciding whether to issue an expansion spawn order.
    """
    state = _init_state()

    if state.state == "idle":
        target = _find_expansion_target(state.ruled_out)
        if target:
            state.target_room = target
            state.state = "scouting"
        return None

    target_room = state.target_room

    if state.state == "scouting":
        return _handle_scouting(state, target_room)
    elif state.state == "claiming":
        return _handle_claiming(state, target_room)
    elif state.state == "pioneering":
        return _handle_pioneering(state, target_room)
    return None
