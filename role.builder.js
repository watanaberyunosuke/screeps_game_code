module.exports = {
  body: [WORK, CARRY, MOVE],

  /** @param {StructureSpawn} spawn */
  minCount(spawn) {
    return spawn.room.find(FIND_CONSTRUCTION_SITES).length > 0 ? 1 : 0;
  },

  /** @param {Creep} creep */
  run(creep) {
    if (creep.store.getFreeCapacity() > 0) {
      const target = creep.pos.findClosestByPath(FIND_STRUCTURES, {
        filter: (structure) =>
          (structure.structureType === STRUCTURE_SPAWN ||
            structure.structureType === STRUCTURE_EXTENSION) &&
          structure.store.getUsedCapacity(RESOURCE_ENERGY) > 0,
      });

      if (target) {
        if (creep.withdraw(target, RESOURCE_ENERGY) === ERR_NOT_IN_RANGE) {
          creep.moveTo(target, { visualizePathStyle: { stroke: "#ffaa00" } });
        }
        return;
      }

      const source = creep.pos.findClosestByPath(FIND_SOURCES);

      if (source && creep.harvest(source) === ERR_NOT_IN_RANGE) {
        creep.moveTo(source, { visualizePathStyle: { stroke: "#ffaa00" } });
      }
    } else {
      const site = creep.pos.findClosestByPath(FIND_CONSTRUCTION_SITES);

      if (site && creep.build(site) === ERR_NOT_IN_RANGE) {
        creep.moveTo(site, { visualizePathStyle: { stroke: "#ffffff" } });
      }
    }
  },
};
