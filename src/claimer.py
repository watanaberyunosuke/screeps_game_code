from defs import *

__pragma__("noalias", "name")
__pragma__("noalias", "undefined")
__pragma__("noalias", "Infinity")
__pragma__("noalias", "keys")
__pragma__("noalias", "get")
__pragma__("noalias", "set")
__pragma__("noalias", "type")
__pragma__("noalias", "update")


def run_claimer(creep):
    """
    Runs a creep as a claimer: travels to the target room and claims its controller.
    :param creep: The creep to run
    """
    target_room = creep.memory.target_room
    room = Game.rooms[target_room]
    if not room or not room.controller:
        creep.moveTo(__new__(RoomPosition(25, 25, target_room)))
        return

    controller = room.controller
    if controller.my:
        return

    if creep.pos.isNearTo(controller):
        result = creep.claimController(controller)
        if result != OK:
            print("[{}] Unknown result from creep.claimController({}): {}".format(
                creep.name, controller, result))
    else:
        creep.moveTo(controller)
