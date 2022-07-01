import threading
from multiprocessing import Event, Process

from module.webui.setting import State


def func(ev: threading.Event):
    import argparse
    import asyncio
    import sys

    import uvicorn

    if sys.platform.startswith("win"):
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

    State.restart_event = ev

    parser = argparse.ArgumentParser(description="Alas web service")
    parser.add_argument(
        "--host",
        type=str,
        help="Host to listen. Default to WebuiHost in deploy setting",
    )
    parser.add_argument(
        "-p",
        "--port",
        type=int,
        help="Port to listen. Default to WebuiPort in deploy setting",
    )
    args, _ = parser.parse_known_args()

    host = args.host or State.deploy_config.WebuiHost or "0.0.0.0"
    port = args.port or int(State.deploy_config.WebuiPort) or 22267

    uvicorn.run("module.webui.app:app", host=host, port=port, factory=True)


if __name__ == "__main__":
    if State.deploy_config.EnableReload:
        should_exit = False
        while not should_exit:
            event = Event()
            process = Process(target=func, args=(event,))
            process.start()
            while not should_exit:
                if event.wait(5):
                    process.kill()
                    break
                elif process.is_alive():
                    continue
                else:
                    should_exit = True
    else:
        func(None)
