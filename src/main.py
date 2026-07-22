import builder
import claimer
import defender
import expansion
import harvester
import intel
import pioneer
import scout
import utrium_harvester

# defs is a package which claims to export all constants and some JavaScript objects, but in reality does
#  nothing. This is useful mainly when using an editor like PyCharm, so that it 'knows' that things like Object, Creep,
#  Game, etc. do exist.
from defs import *

# These are currently required for Transcrypt in order to use the following names in JavaScript.
# Without the 'noalias' pragma, each of the following would be translated into something like 'py_Infinity' or
#  'py_keys' in the output file.
__pragma__("noalias", "name")
__pragma__("noalias", "undefined")
__pragma__("noalias", "Infinity")
__pragma__("noalias", "keys")
__pragma__("noalias", "get")
__pragma__("noalias", "set")
__pragma__("noalias", "type")
__pragma__("noalias", "update")

MAX_CREEPS = 15
BUILDER_HARVESTER_RATIO = 3


def is_harvester(creep):
    role = creep.memory.role
    return not role or role == "harvester"


def count_room_creeps(room, predicate):
    return _.sum(Game.creeps, lambda c: c.pos.roomName == room.name and predicate(c))


def get_coordinator_room_name():
    """
    Picks a single owned room to be responsible for issuing expansion spawn orders each
    tick, so that two fully-staffed rooms don't race to spawn duplicate scouts/claimers
    for the same target room on the same tick.
    """
    coordinator = None
    for name in Object.keys(Game.spawns):
        room_name = Game.spawns[name].room.name
        if coordinator is None or room_name < coordinator:
            coordinator = room_name
    return coordinator


def harvester_body(room):
    if room.energyCapacityAvailable >= 350:
        return [WORK, CARRY, CARRY, MOVE, MOVE, MOVE]
    return [WORK, CARRY, MOVE, MOVE]


def builder_body(room):
    if room.energyCapacityAvailable >= 400:
        return [WORK, WORK, CARRY, CARRY, MOVE, MOVE]
    return [WORK, CARRY, CARRY, MOVE, MOVE]


def defender_body(room):
    if room.energyCapacityAvailable >= 650:
        return [ATTACK, RANGED_ATTACK, HEAL, MOVE, MOVE, MOVE]
    elif room.energyCapacityAvailable >= 330:
        return [ATTACK, RANGED_ATTACK, MOVE, MOVE]
    return [ATTACK, MOVE, MOVE]


def main():
    """
    Main game logic loop.
    """

    intel.record_visible_rooms()

    # Run each creep
    for name in Object.keys(Game.creeps):
        creep = Game.creeps[name]
        role = creep.memory.role
        if role == "utrium_harvester":
            utrium_harvester.run_utrium_harvester(creep)
        elif role == "builder":
            builder.run_builder(creep)
        elif role == "scout":
            scout.run_scout(creep)
        elif role == "patrol_scout":
            scout.run_patrol_scout(creep)
        elif role == "claimer":
            claimer.run_claimer(creep)
        elif role == "pioneer":
            pioneer.run_pioneer(creep)
        elif role == "defender":
            defender.run_defender(creep)
        else:
            harvester.run_harvester(creep)

    coordinator_room_name = get_coordinator_room_name()

    # Run each spawn
    for name in Object.keys(Game.spawns):
        spawn = Game.spawns[name]
        if spawn.spawning:
            continue

        room = spawn.room
        hostile = _(room.find(FIND_HOSTILE_CREEPS)).first()
        num_defenders = count_room_creeps(room, lambda c: c.memory.role == "defender")
        num_harvesters = count_room_creeps(room, is_harvester)
        num_builders = count_room_creeps(room, lambda c: c.memory.role == "builder")
        num_utrium_harvesters = count_room_creeps(
            room, lambda c: c.memory.role == "utrium_harvester"
        )
        num_creeps = num_harvesters + num_builders + num_utrium_harvesters

        if hostile and num_defenders < 2:
            body = defender_body(room)
            if room.energyAvailable >= _.sum(body, lambda p: BODYPART_COST[p]):
                spawn.createCreep(body, None, {"role": "defender"})
        elif (
            num_utrium_harvesters < 1
            and utrium_harvester.get_utrium_mineral(room)
            and room.energyAvailable >= 250
        ):
            spawn.createCreep(
                [WORK, CARRY, CARRY, MOVE, MOVE],
                None,
                {"role": "utrium_harvester", "filling": True},
            )
        elif (
            num_creeps < MAX_CREEPS
            and room.energyAvailable >= room.energyCapacityAvailable
        ):
            target_builders = num_harvesters // BUILDER_HARVESTER_RATIO
            if num_builders < target_builders:
                spawn.createCreep(
                    builder_body(room), None, {"role": "builder", "building": False}
                )
            else:
                spawn.createCreep(
                    harvester_body(room), None, {"role": "harvester", "filling": True}
                )
        elif num_creeps == 0 and room.energyAvailable >= 250:
            spawn.createCreep(
                harvester_body(room), None, {"role": "harvester", "filling": True}
            )
        elif num_creeps >= MAX_CREEPS and room.name == coordinator_room_name:
            order = expansion.get_next_spawn_order(room)
            if not order and _.sum(Game.creeps, lambda c: c.memory.role == "patrol_scout") < 1:
                order = ([MOVE], {"role": "patrol_scout"})
            if order:
                body, memory = order
                if room.energyAvailable >= _.sum(body, lambda p: BODYPART_COST[p]):
                    spawn.createCreep(body, None, memory)


module.exports.loop = main
