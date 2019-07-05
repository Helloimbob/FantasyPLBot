import asyncio
import json
import logging
import os
import re
from datetime import datetime

import aiohttp
from fpl import FPL
import fpl

async def main():
    async with aiohttp.ClientSession() as session:
        fpl = FPL(session)
        players = await fpl.get_players()
        for player in players:
            print(player)

        team = await fpl.get_user("24681").get_team()
        for player in team:
            print(player)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except AttributeError:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())
        loop.close()

