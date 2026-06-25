from defs import *

__pragma__('noalias', 'name')
__pragma__('noalias', 'undefined')
__pragma__('noalias', 'Infinity')
__pragma__('noalias', 'keys')
__pragma__('noalias', 'get')
__pragma__('noalias', 'set')
__pragma__('noalias', 'type')
__pragma__('noalias', 'update')

ENERGY_SOURCES = [
    STRUCTURE_SPAWN,
    STRUCTURE_EXTENSION,
    STRUCTURE_CONTAINER,
    STRUCTURE_STORAGE,
]


def run_builder(creep):
    """
    Runs a creep as a builder.
    :param creep: The creep to run
    """
    if creep.memory.building and creep.carry.energy <= 0:
        creep.memory.building = False
        del creep.memory.target
    elif not creep.memory.building and creep.carry.energy >= creep.carryCapacity:
        creep.memory.building = True
        del creep.memory.source

    if creep.memory.building:
        if creep.memory.target:
            target = Game.getObjectById(creep.memory.target)
        else:
            target = _(creep.room.find(FIND_CONSTRUCTION_SITES)).sample()
            if target:
                creep.memory.target = target.id

        if not target:
            if creep.pos.inRangeTo(creep.room.controller, 3):
                result = creep.upgradeController(creep.room.controller)
                if result != OK:
                    print("[{}] Unknown result from creep.upgradeController({}): {}".format(
                        creep.name, creep.room.controller, result))
            else:
                creep.moveTo(creep.room.controller)
            return

        if creep.pos.isNearTo(target):
            result = creep.build(target)
            if result == OK:
                del creep.memory.target
            elif result != ERR_NOT_ENOUGH_RESOURCES:
                print("[{}] Unknown result from creep.build({}): {}".format(creep.name, target, result))
        else:
            creep.moveTo(target)
    else:
        if creep.memory.source:
            source = Game.getObjectById(creep.memory.source)
        else:
            source = _(creep.room.find(FIND_STRUCTURES)) \
                .filter(lambda s: s.structureType in ENERGY_SOURCES and s.store.energy > 0) \
                .sample()
            if not source:
                source = _.sample(creep.room.find(FIND_SOURCES))
            if source:
                creep.memory.source = source.id

        if not source:
            return

        if source.structureType in ENERGY_SOURCES:
            if creep.pos.isNearTo(source):
                result = creep.withdraw(source, RESOURCE_ENERGY)
                if result != OK and result != ERR_NOT_ENOUGH_RESOURCES:
                    print("[{}] Unknown result from creep.withdraw({}, {}): {}".format(
                        creep.name, source, RESOURCE_ENERGY, result))
            else:
                creep.moveTo(source)
        elif creep.pos.isNearTo(source):
            result = creep.harvest(source)
            if result != OK:
                print("[{}] Unknown result from creep.harvest({}): {}".format(creep.name, source, result))
        else:
            creep.moveTo(source)
