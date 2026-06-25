import builder
import harvester
import utrium_harvester
# defs is a package which claims to export all constants and some JavaScript objects, but in reality does
#  nothing. This is useful mainly when using an editor like PyCharm, so that it 'knows' that things like Object, Creep,
#  Game, etc. do exist.
from defs import *

# These are currently required for Transcrypt in order to use the following names in JavaScript.
# Without the 'noalias' pragma, each of the following would be translated into something like 'py_Infinity' or
#  'py_keys' in the output file.
__pragma__('noalias', 'name')
__pragma__('noalias', 'undefined')
__pragma__('noalias', 'Infinity')
__pragma__('noalias', 'keys')
__pragma__('noalias', 'get')
__pragma__('noalias', 'set')
__pragma__('noalias', 'type')
__pragma__('noalias', 'update')

MAX_CREEPS = 15
BUILDER_HARVESTER_RATIO = 3


def is_harvester(creep):
    role = creep.memory.role
    return not role or role == 'harvester'


def count_room_creeps(room, predicate):
    return _.sum(Game.creeps, lambda c: c.pos.roomName == room.name and predicate(c))


def harvester_body(room):
    if room.energyCapacityAvailable >= 350:
        return [WORK, CARRY, CARRY, MOVE, MOVE, MOVE]
    return [WORK, CARRY, MOVE, MOVE]


def builder_body(room):
    if room.energyCapacityAvailable >= 400:
        return [WORK, WORK, CARRY, CARRY, MOVE, MOVE]
    return [WORK, CARRY, CARRY, MOVE, MOVE]


def main():
    """
    Main game logic loop.
    """

    # Run each creep
    for name in Object.keys(Game.creeps):
        creep = Game.creeps[name]
        role = creep.memory.role
        if role == 'utrium_harvester':
            utrium_harvester.run_utrium_harvester(creep)
        elif role == 'builder':
            builder.run_builder(creep)
        else:
            harvester.run_harvester(creep)

    # Run each spawn
    for name in Object.keys(Game.spawns):
        spawn = Game.spawns[name]
        if spawn.spawning:
            continue

        room = spawn.room
        num_harvesters = count_room_creeps(room, is_harvester)
        num_builders = count_room_creeps(room, lambda c: c.memory.role == 'builder')
        num_utrium_harvesters = count_room_creeps(
            room, lambda c: c.memory.role == 'utrium_harvester')
        num_creeps = num_harvesters + num_builders + num_utrium_harvesters

        if (num_utrium_harvesters < 1
                and utrium_harvester.get_utrium_mineral(room)
                and room.energyAvailable >= 250):
            spawn.createCreep(
                [WORK, CARRY, CARRY, MOVE, MOVE],
                None,
                {'role': 'utrium_harvester', 'filling': True})
        elif num_creeps < MAX_CREEPS and room.energyAvailable >= room.energyCapacityAvailable:
            target_builders = num_harvesters // BUILDER_HARVESTER_RATIO
            if num_builders < target_builders:
                spawn.createCreep(
                    builder_body(room),
                    None,
                    {'role': 'builder', 'building': False})
            else:
                spawn.createCreep(
                    harvester_body(room),
                    None,
                    {'role': 'harvester', 'filling': True})
        elif num_creeps == 0 and room.energyAvailable >= 250:
            spawn.createCreep(
                harvester_body(room),
                None,
                {'role': 'harvester', 'filling': True})


module.exports.loop = main
