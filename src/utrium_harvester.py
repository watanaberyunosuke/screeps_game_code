from defs import *

__pragma__('noalias', 'name')
__pragma__('noalias', 'undefined')
__pragma__('noalias', 'Infinity')
__pragma__('noalias', 'keys')
__pragma__('noalias', 'get')
__pragma__('noalias', 'set')
__pragma__('noalias', 'type')
__pragma__('noalias', 'update')

MINERAL_TRANSFER_STRUCTURES = [
    STRUCTURE_STORAGE,
    STRUCTURE_TERMINAL,
    STRUCTURE_CONTAINER,
]


def get_utrium_mineral(room):
    """
    Returns the utrium mineral in the room, if any.
    :param room: The room to search
    """
    return _(room.find(FIND_MINERALS)) \
        .filter(lambda m: m.mineralType == RESOURCE_UTRIUM) \
        .first()


def run_utrium_harvester(creep):
    """
    Runs a creep as a utrium harvester.
    :param creep: The creep to run
    """
    utrium_amount = creep.store.getUsedCapacity(RESOURCE_UTRIUM)

    if creep.memory.filling and creep.store.getFreeCapacity(RESOURCE_UTRIUM) == 0:
        creep.memory.filling = False
        del creep.memory.target
    elif not creep.memory.filling and utrium_amount <= 0:
        creep.memory.filling = True
        del creep.memory.target

    if creep.memory.filling:
        if creep.memory.mineral:
            mineral = Game.getObjectById(creep.memory.mineral)
        else:
            mineral = get_utrium_mineral(creep.room)
            if mineral:
                creep.memory.mineral = mineral.id

        if not mineral:
            return

        if mineral.mineralAmount <= 0:
            return

        if creep.pos.isNearTo(mineral):
            result = creep.harvest(mineral)
            if result != OK:
                print("[{}] Unknown result from creep.harvest({}): {}".format(creep.name, mineral, result))
        else:
            creep.moveTo(mineral)
    else:
        if creep.memory.target:
            target = Game.getObjectById(creep.memory.target)
        else:
            target = _(creep.room.find(FIND_STRUCTURES)) \
                .filter(lambda s: s.structureType in MINERAL_TRANSFER_STRUCTURES
                        and s.store.getFreeCapacity(RESOURCE_UTRIUM) > 0) \
                .sample()
            if target:
                creep.memory.target = target.id

        if not target:
            return

        if creep.pos.isNearTo(target):
            result = creep.transfer(target, RESOURCE_UTRIUM)
            if result == OK or result == ERR_FULL:
                del creep.memory.target
            else:
                print("[{}] Unknown result from creep.transfer({}, {}): {}".format(
                    creep.name, target, RESOURCE_UTRIUM, result))
        else:
            creep.moveTo(target)
