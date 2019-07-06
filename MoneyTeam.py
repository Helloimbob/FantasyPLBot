import asyncio
import json
import logging
import os
import re
from datetime import datetime

import aiohttp
from fpl import FPL
import fpl


def calc_roi(points, cost):
    return points / cost


class TeamSelector:
    def __init__(self, session):
        self.fpl = FPL(session)

    async def get_injured_players(self):
        players = await self.fpl.get_players()
        injured = []
        for player in players:
            if player.chance_of_playing_this_round != 100:
                injured.append(player)
        return injured

    async def points_top_players(self, position):
        players = await self.fpl.get_players()
        positionPlayers = []
        for player in players:
            if player.element_type == position:
                positionPlayers.append(player)
        positionPlayers.sort(key=lambda x: x.total_points, reverse=True)
        return positionPlayers

    # Only return non-premium players
    async def roi_top_players(self, position, premiumLimit):
        players = await self.fpl.get_players()
        positionPlayers = []
        for player in players:
            # Assign their calculated ROI
            if player.element_type == position and player.now_cost < premiumLimit:
                setattr(player, 'roi', calc_roi(
                    player.total_points, player.now_cost))
                positionPlayers.append(player)
        # sort by ROI
        positionPlayers.sort(key=lambda x: x.roi, reverse=True)
        return positionPlayers

    async def get_money_team_objects(self, budget=1000, premium_gk=0, premium_def=1, premium_mid=2, premium_fwd=1):
        money_team = []
        budget = budget
        injured = await self.get_injured_players()
        positions = {1: 2, 2: 5, 3: 5, 4: 3}
        premiums = {1: premium_gk, 2: premium_def,
                    3: premium_mid, 4: premium_fwd}
        premiumCount = sum(premiums.values())
        premium_limit = {1: 50, 2: 50, 3: 80, 4: 75}
        teamCount = dict()
        for x in range(1, 21):
            teamCount[x] = 0
        # Select premium players first
        for position in premiums.keys():
            for player in await self.points_top_players(position):
                if len(money_team) < premiumCount and player not in injured and budget >= player.now_cost and positions[player.element_type] > 0 and teamCount[player.team] < 3 and premiums[player.element_type] > 0:
                    money_team.append(player)
                    budget -= player.now_cost
                    positions[player.element_type] = positions[player.element_type] - 1
                    teamCount[player.team] = teamCount[player.team] + 1
                    premiums[player.element_type] = premiums[player.element_type] - 1

        for position in premiums.keys():
            for player in await self.roi_top_players(position, premium_limit[position]):
                if player not in money_team and budget >= player.now_cost and player not in injured and positions[player.element_type] > 0 and teamCount[player.team] < 3:
                    money_team.append(player)
                    budget -= player.now_cost
                    positions[player.element_type] = positions[player.element_type] - 1
                    teamCount[player.team] = teamCount[player.team] + 1
        final_team = [(item.web_name, item.element_type, item.now_cost)
                      for item in money_team]
        total_points = sum([item.total_points for item in money_team])
        print(total_points)
        return money_team

    async def print_money_team(self):
        for player in await self.get_money_team_objects():
            print(player)


async def main():
    async with aiohttp.ClientSession() as session:
        teamSelector = TeamSelector(session)

        await teamSelector.print_money_team()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except AttributeError:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())
        loop.close()
