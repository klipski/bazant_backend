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


# TODO: wyslij info o polozeniu wszystkich graczy
async def notify_players_about_position():
    """
    Notifies all players about the current state of the game, including player positions and colors.
    """
    # if PLAYERS:
    #     message = json.dumps(
    #         {"type": "update", "players": {player_id: player[0] for player_id, player in PLAYERS.items()}}
    #     )
    #     await asyncio.gather(*[player[1].send(message) for player in PLAYERS.values()])
    pass


# todo: zapisz ruch graczy
async def move_player(data, websocket):
    pass


# todo: start gry
async def start_game(data, websocket):
    pass


# todo: obsluga zmiany komorki
async def board_change(data, websocket):
    pass


# todo: usun gracza
async def remove_player(player_id):
    pass