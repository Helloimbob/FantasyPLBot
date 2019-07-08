import asyncio
import json
import logging
import os
import re
from datetime import datetime

import aiohttp
from fpl import FPL
import fpl
from constants import NEXT_GAMEWEEK
from constants import FIXTURE_DIFFICULTY_SCALE
from fpl.utils import position_converter
from fpl.utils import team_converter

def calc_roi(points, cost):
    return points / cost

def print_team(team):
    for index, player in enumerate(team):
        if index == 0:
            print(f"{player.web_name} (C) - "
                f"{position_converter(player.element_type)} - "
                f"{team_converter(player.team)}")
        elif index == 1:
            print(f"{player.web_name} (VC) - "
                f"{position_converter(player.element_type)} - "
                f"{team_converter(player.team)}")
        else:
            print(player)

class TeamSelector:

    def __init__(self, session):
        self.fpl = FPL(session)
        self.players = []
        self.fixtures = []
        self.positions = {1: 2, 2: 5,
                          3: 5, 4: 3}
        self.premium_limit = {1: 50, 2: 50,
                              3: 80, 4: 75}
        self.teamCount = dict()
        for x in range(1, 21):
            self.teamCount[x] = 0
        self.injured = []

    async def cache_data(self):
        self.players = await self.fpl.get_players()
        self.fixtures = await self.fpl.get_fixtures_by_gameweek(NEXT_GAMEWEEK)

    def get_injured_players(self):
        for player in self.players:
            if player.status == 'i':
                self.injured.append(player)

    def points_top_players(self, position):
        positionPlayers = []
        for player in self.players:
            if player.element_type == position:
                positionPlayers.append(player)
        positionPlayers.sort(key=lambda x: x.total_points, reverse=True)
        return positionPlayers

    # Only return non-premium players
    def roi_top_players(self, position, premiumLimit):
        positionPlayers = []
        for player in self.players:
            # Assign their calculated ROI
            if player.element_type == position and player.now_cost < premiumLimit:
                setattr(player, 'roi', calc_roi(
                    player.total_points, player.now_cost))
                positionPlayers.append(player)
        # sort by ROI
        positionPlayers.sort(key=lambda x: x.roi, reverse=True)
        return positionPlayers

    def player_allowed(self, player):
        if not self.injured:
            self.get_injured_players()
        if player not in self.injured and self.budget >= player.now_cost and self.positions[player.element_type] > 0 and self.teamCount[player.team] < 3:
            return True
        else:
            return False

    def select_player(self, team, player):
        team.append(player)
        self.budget -= player.now_cost
        self.positions[player.element_type] = self.positions[player.element_type] - 1
        self.teamCount[player.team] = self.teamCount[player.team] + 1

    def get_money_team_objects(self, budget=1000, premium_gk=0, premium_def=1, premium_mid=2, premium_fwd=1):
        money_team = []
        self.budget = budget
        premiums = {1: premium_gk, 2: premium_def,
                    3: premium_mid, 4: premium_fwd}
        premiumCount = sum(premiums.values())
        # Select premium players first
        for position in premiums.keys():
            for player in self.points_top_players(position):
                if len(money_team) < premiumCount and self.player_allowed(player) and premiums[player.element_type] > 0:
                        self.select_player(money_team, player)
                        premiums[player.element_type] = premiums[player.element_type] - 1

        for position in premiums.keys():
            for player in self.roi_top_players(position, self.premium_limit[position]):
                if self.player_allowed(player):
                    self.select_player(money_team, player)

        total_points = sum([item.total_points for item in money_team])
        print(total_points)
        return money_team

    def get_next_fixture_difficulty(self, team):
        # Get the fixtures list for next gameweek
        for fixture in self.fixtures:
            if fixture.team_h == team:
                return fixture.team_h_difficulty
            elif fixture.team_a == team:
                return fixture.team_a_difficulty

    def sort_by_adjusted_points(self, currentTeam):
        for player in currentTeam:
            # Work out the highest scoring player with the easiest fixture
            diff = self.get_next_fixture_difficulty(player.team)
            # Difficulty 1 = 100% of points, 2 = 80% etc etc.
            setattr(player, 'adj_points', player.total_points * FIXTURE_DIFFICULTY_SCALE[diff])
        currentTeam.sort(key=lambda x: x.adj_points, reverse=True)


async def main():
    async with aiohttp.ClientSession() as session:
        teamSelector = TeamSelector(session)
        await teamSelector.cache_data()
        money_team = teamSelector.get_money_team_objects()
        teamSelector.sort_by_adjusted_points(money_team)
        print_team(money_team)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except AttributeError:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())
        loop.close()
