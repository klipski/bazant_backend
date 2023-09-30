import asyncio
import json
import uuid

import constants


async def initialize_player(message, websocket):
    player_id = str(uuid.uuid4())  # Generate a unique player ID using UUID
    player_type = message.get("type")
    if player_type == "admin":
        constants.ADMINS[player_id] = websocket
    else:
        constants.PLAYERS[player_id] = websocket
    await websocket.send(json.dumps({"key": "assigned", "playerId": player_id}))


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


async def send_board():
    """
    Notifies all players about the current state of the game board.
    """
    message = json.dumps(constants.BOARD)
    await asyncio.gather(
        *[player.send(message) for player in [*constants.PLAYERS.values(), *constants.ADMINS.values()]]
    )


async def send_positions():
    """
    Notifies all players about the current players positions.
    """
    if constants.PLAYERS:
        message = json.dumps(constants.POSITIONS)
        await asyncio.gather(
            *[player.send(message) for player in [*constants.PLAYERS.values(), *constants.ADMINS.values()]]
        )


# todo: obsluga zmiany komorki
async def board_change(data, websocket):
    pass


# todo: usun gracza
async def remove_player(player_id):
    pass
