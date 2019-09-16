import argparse
import aiohttp
import asyncio

from Utils import print_team

from LineupPicker import LineupPicker
from TeamSelector import TeamSelector
from TransferPicker import TransferPicker

async def main(function):
    async with aiohttp.ClientSession() as session:
        if (function == 1):
            teamSelector = TeamSelector(session)
            await teamSelector.cache_data()
            money_team = teamSelector.get_money_team_objects()
            teamSelector.sort_by_adjusted_points(money_team)
            print_team(money_team)
        elif (function == 2):
            lineupPicker = LineupPicker(session)
            await lineupPicker.cache_data()
            curr = await lineupPicker.get_current_team()
            lineupPicker.sort_by_adjusted_points(curr)
            print_team(curr)
        elif (function == 3):
            transfer = TransferPicker(session)
            await transfer.cache_data()
            await transfer.pick_transfer(await transfer.get_current_team(), 2)



if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='FPL Auto Selection Bot')
    parser.add_argument('func', help='Which function to use: 1 to Select Team, or 2 to pick lineup', type=int)
    args = parser.parse_args()

    try:
        asyncio.run(main(args.func))
    except AttributeError:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main(args.func))
        loop.close()
