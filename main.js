const roles = require("roles");

const spawnPriority = ["harvester", "builder"];

module.exports.loop = function () {
  for (const name in Memory.creeps) {
    if (!Game.creeps[name]) {
      delete Memory.creeps[name];
    }
  }

  const spawn = Game.spawns["Spawn1"];

  if (!spawn.spawning) {
    for (const roleName of spawnPriority) {
      const role = roles[roleName];
      const count = _.filter(
        Game.creeps,
        (creep) => creep.memory.role === roleName,
      ).length;
      const needed = role.minCount(spawn);

      if (count < needed) {
        const name = `${roleName}_${Game.time}`;
        const result = spawn.spawnCreep(role.body, name, {
          memory: {
            role: roleName,
            homeRoom: spawn.room.name,
          },
        });

        if (result === OK) {
          console.log(`Spawning ${name}`);
        }
        break;
      }
    }
  }

  for (const name in Game.creeps) {
    const creep = Game.creeps[name];
    const role = roles[creep.memory.role];

    if (role) {
      role.run(creep);
    }
  }
};
