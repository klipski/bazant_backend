import asyncio
import http
import json
import signal

import websockets

import constants
import services


async def player_handler(websocket):
    """
    Handles player connections, receives player data, and updates other players.
    """
    player_id = None
    print("device connected to websocket")
    await websocket.send("device connected to websocket")
    try:
        while True:
            message = await websocket.recv()
            try:
                data = json.loads(message)
            except json.JSONDecodeError:
                print("Not supported message")
                await websocket.send(json.dumps({"message": "Message not supported"}))

                continue

            key = data.get("key")

            if key == "init":
                if not player_id:
                    player_id = services.initialize_player(data, websocket)
                await services.send_player_id(player_id, websocket)
                await services.send_new_player(player_id)
                await services.send_board_to_player(player_id)
            elif key == "start":
                await services.start_game(data, websocket)
                await services.send_board()
            elif key == "move":
                await services.move_player(data, websocket)
                await services.send_positions(data)
            elif key == "board_change":
                await services.board_change(data, websocket)
                services.send_game_ends_info()
            elif key == "hint":
                await services.handle_hints(data, websocket)
            elif key == "playerLeave":
                await services.remove_player(player_id)
                services.send_player_leave(player_id)
            elif key == "boneFound":
                await services.handle_bone_found(data, websocket)
                services.send_bones()
                services.send_game_ends_info()
            else:
                print("key", key)
                await websocket.send(json.dumps({"message": "Message not supported"}))
    except websockets.ConnectionClosedOK:
        await services.remove_player(player_id)
        services.send_player_leave(player_id)


async def health_check(path, request_headers):
    if path == "/healthz":
        return http.HTTPStatus.OK, [], b"OK\n"


async def main():
    # Set the stop condition when receiving SIGTERM.
    loop = asyncio.get_running_loop()
    stop = loop.create_future()
    loop.add_signal_handler(signal.SIGTERM, stop.set_result, None)

    async with websockets.serve(
            player_handler,
            host="",
            port=8001,
            process_request=health_check,
    ):
        await stop


if __name__ == "__main__":
    asyncio.run(main())
