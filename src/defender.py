from defs import *

__pragma__("noalias", "name")
__pragma__("noalias", "undefined")
__pragma__("noalias", "Infinity")
__pragma__("noalias", "keys")
__pragma__("noalias", "get")
__pragma__("noalias", "set")
__pragma__("noalias", "type")
__pragma__("noalias", "update")


def run_defender(creep):
    """
    Runs a creep as a defender: engages the closest hostile creep in its room, using
    ranged/melee attacks and self-healing according to its body parts. When no hostiles
    are present, it waits near the room's spawn.
    :param creep: The creep to run
    """
    hostiles = creep.room.find(FIND_HOSTILE_CREEPS)
    target = creep.pos.findClosestByRange(hostiles)

    if target:
        if creep.getActiveBodyparts(RANGED_ATTACK) and creep.pos.inRangeTo(target, 3):
            result = creep.rangedAttack(target)
            if result != OK:
                print("[{}] Unknown result from creep.rangedAttack({}): {}".format(
                    creep.name, target, result))
        if creep.getActiveBodyparts(ATTACK) and creep.pos.isNearTo(target):
            result = creep.attack(target)
            if result != OK:
                print("[{}] Unknown result from creep.attack({}): {}".format(
                    creep.name, target, result))
        if not creep.pos.isNearTo(target):
            creep.moveTo(target)
    else:
        spawn = _(creep.room.find(FIND_MY_SPAWNS)).first()
        if spawn and not creep.pos.isNearTo(spawn):
            creep.moveTo(spawn)

    if creep.getActiveBodyparts(HEAL) and creep.hits < creep.hitsMax:
        result = creep.heal(creep)
        if result != OK:
            print("[{}] Unknown result from creep.heal({}): {}".format(
                creep.name, creep.name, result))
