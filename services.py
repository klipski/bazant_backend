import asyncio
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
    payload = data.get("payload")
    constants.BOARD = payload


async def move_player(data, websocket):
    """
    Updates players positions.
    """
    player_id = data.get("playerId")
    payload = data.get("payload")
    constants.POSITIONS[player_id] = payload


async def remove_player(player_id):
    """
    Removes player from data structures by player ID.
    """
    if player_id in constants.PLAYERS:
        del constants.PLAYERS[player_id]
    if player_id in constants.POSITIONS:
        del constants.PLAYERS[player_id]
    if player_id in constants.ADMINS:
        del constants.ADMINS[player_id]


async def send_player_id(player_id, websocket):
    """
    Sends playerId to player.
    """
    await websocket.send(json.dumps({"key": "assigned", "playerId": player_id}))


async def send_board():
    """
    Notifies all players about the current state of the game board.
    """
    message = json.dumps({"key": "send_board", "payload": constants.BOARD})
    broadcast(constants.ADMINS.values(), message)


async def send_positions():
    """
    Notifies all players about the current players positions.
    """
    if constants.PLAYERS:
        message = json.dumps({"key": "positions", "payload": constants.POSITIONS})
        broadcast(constants.ADMINS.values(), message)


def send_player_leave(player_id):
    message = json.dumps({"key": "playerLeave", "playerId": player_id})
    broadcast(constants.ADMINS.values(), message)


async def board_change(data, websocket):
    """
    Updates game board and returns changed cell to admin.
    """
    payload = data.get("payload")
    player_id = data.get("playerId")
    cells = constants.BOARD.get("cells")
    [cell.update(payload) for cell in cells if payload["cellID"] == cell["cellID"]]

    message = json.dumps({"key": "board_change", "playerId": player_id, "payload": payload})
    broadcast(constants.ADMINS.values(), message)


async def handle_hints(data, websocket):
    """
    Handles hints from admin to player.
    """
    player_id = data.get("playerId")
    if player_id in constants.PLAYERS:
        await constants.PLAYERS[player_id].send(json.dumps(data))
