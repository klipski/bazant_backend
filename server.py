import asyncio
import json
import uuid

import websockets
import constants
import services


async def player_handler(websocket):
    """
    Handles player connections, receives player data, and updates other players.
    """
    player_id = None
    while True:
        try:
            print("PLAYERS", constants.PLAYERS)
            print("ADMINS", constants.ADMINS)

            message = await websocket.recv()
            data = json.loads(message)
            key = data.get("key")

            if key == "init":
                await services.initialize_player(data, websocket)
            elif key == "start":
                await services.start_game(data, websocket)
            elif key == "move":
                await services.move_player(data, websocket)
                await services.notify_players_about_position()
            elif key == "board_change":
                await services.board_change(data, websocket)
            else:
                print("key", key)
        except json.JSONDecodeError:
            print("Not supported message")
        except websockets.ConnectionClosedOK:
            await services.remove_player(player_id)


async def main():
    """
    Main function to run the WebSocket server.
    """
    async with websockets.serve(player_handler, "", 8001):
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
