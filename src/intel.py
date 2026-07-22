from defs import *

__pragma__("noalias", "name")
__pragma__("noalias", "undefined")
__pragma__("noalias", "Infinity")
__pragma__("noalias", "keys")
__pragma__("noalias", "get")
__pragma__("noalias", "set")
__pragma__("noalias", "type")
__pragma__("noalias", "update")


def record_visible_rooms():
    """
    Snapshots intel (sources, controller ownership/reservation, hostile presence)
    for every room currently visible into Memory.rooms, so other systems can consult
    recent room data without needing direct vision.
    """
    if not Memory.rooms:
        Memory.rooms = {}

    for name in Object.keys(Game.rooms):
        room = Game.rooms[name]
        controller = room.controller

        _.set(Memory.rooms, name, {
            "lastSeen": Game.time,
            "sources": _.size(room.find(FIND_SOURCES)),
            "owner": controller.owner.username if controller and controller.owner else None,
            "reservedBy": controller.reservation.username if controller and controller.reservation else None,
            "hostileCount": _.size(room.find(FIND_HOSTILE_CREEPS)),
        })
