import json
import uuid

from websockets import broadcast

import constants


def initialize_player(message, websocket):
    """
    Initialize player.
    """
    player_id = str(uuid.uuid4())  # Generate a unique player ID using UUID
    player_type = message.get("type")
    if player_type == "admin":
        constants.ADMINS[player_id] = websocket
    else:
        constants.PLAYERS[player_id] = websocket
    return player_id


async def start_game(data, websocket):
    """
    Updates game board.
    """
    payload = json.loads(data.get("payload"))
    constants.BOARD = payload
    constants.BONES = 0


async def move_player(data, websocket):
    """
    Updates players positions.
    """
    player_id = data.get("playerId")
    payload = json.loads(data.get("payload"))
    constants.POSITIONS[player_id] = payload


async def remove_player(player_id):
    """
    Removes player from data structures by player ID.
    """
    if player_id in constants.PLAYERS:
        del constants.PLAYERS[player_id]
    if player_id in constants.POSITIONS:
        del constants.POSITIONS[player_id]
    if player_id in constants.ADMINS:
        del constants.ADMINS[player_id]


async def send_player_id(player_id, websocket):
    """
    Sends playerId to player.
    """
    await websocket.send(json.dumps({"key": "assigned", "playerId": player_id}))


async def send_new_player(player_id):
    if player_id not in constants.ADMINS:
        message = json.dumps({"key": "new_player_enter", "playerId": player_id})
        broadcast(constants.ADMINS.values(), message)


async def send_board():
    """
    Notifies all players about the current state of the game board.
    """
    message = json.dumps({"key": "send_board", "payload": json.dumps(constants.BOARD)})
    broadcast([*constants.ADMINS.values(), *constants.PLAYERS.values()], message)


async def send_board_to_player(player_id):
    if player_id in constants.PLAYERS:
        message = json.dumps({"key": "send_board", "payload": json.dumps(constants.BOARD)})
        await constants.PLAYERS[player_id].send(message)


async def send_positions(data):
    """
    Notifies all players about the current players positions.
    """
    message = json.dumps(data)
    broadcast(constants.ADMINS.values(), message)


def send_player_leave(player_id):
    message = json.dumps({"key": "playerLeave", "playerId": player_id})
    broadcast(constants.ADMINS.values(), message)


async def board_change(data, websocket):
    """
    Updates game board and returns changed cell to admin.
    """
    payload = json.loads(data.get("payload"))
    player_id = data.get("playerId")
    cells = constants.BOARD.get("cells")
    [cell.update(payload) for cell in cells if payload["cellId"] == cell["cellId"]]

    message = json.dumps({"key": "board_change", "playerId": player_id, "payload": payload})
    broadcast([*constants.ADMINS.values(), *constants.PLAYERS.values()], message)


async def handle_hints(data, websocket):
    """
    Handles hints from admin to player.
    """
    player_id = data.get("playerId")
    if player_id in constants.PLAYERS:
        await constants.PLAYERS[player_id].send(json.dumps(data))


async def handle_bone_found(data, websocket):
    constants.BONES += 1


def send_bones():
    message = json.dumps({"bonesCount": constants.BONES})
    broadcast([*constants.ADMINS.values(), *constants.PLAYERS.values()], message)


def send_game_ends_info():
    if len([cell for cell in constants.BOARD.get("cells", []) if int(cell["type"]) == 1]) == 0:
        message = json.dumps({"key": "game_ends", "type": "win"})
        broadcast([*constants.ADMINS.values(), *constants.PLAYERS.values()], message)
