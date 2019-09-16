from Utils import calc_roi
from Utils import sort_by_roi
from Utils import print_team
from Utils import is_in_team

from fpl import user
from FPLConstants import NEXT_GAMEWEEK
from FPLConstants import PREV_GAMEWEEK
from FPLConstants import FIXTURE_DIFFICULTY_SCALE
from FPLConstants import BOT_ID
from FantasyPicker import FantasyPicker

class TeamSelector(FantasyPicker):
    def get_unavailable_players(self):
        for player in self.players:
            if player.status == 'i' or player.status == 'n':
                self.unvailable.append(player)

    def points_top_players(self, position):
        positionPlayers = []
        for player in self.players:
            if player.element_type == position:
                positionPlayers.append(player)
        positionPlayers.sort(key=lambda x: x.total_points, reverse=True)
        return positionPlayers

    def player_allowed(self, player):
        if not self.unvailable:
            self.get_unavailable_players()
        if player not in self.unvailable and self.budget >= player.now_cost and self.positions[player.element_type] > 0 and self.teamCount[player.team] < 3:
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


