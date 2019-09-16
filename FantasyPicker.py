from fpl import FPL
from Utils import calc_roi
import FPLConstants

class FantasyPicker(object):
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
        self.unvailable = []

    async def cache_data(self):
        self.players = await self.fpl.get_players()
        self.fixtures = await self.fpl.get_fixtures_by_gameweek(FPLConstants.NEXT_GAMEWEEK)

    def sort_by_adjusted_points(self, currentTeam):
        for player in currentTeam:
            # Work out the highest scoring player with the easiest fixture
            diff = self.get_next_fixture_difficulty(player.team)
            # Difficulty 1 = 100% of points, 2 = 80% etc etc.
            setattr(player, 'adj_points', player.total_points * FPLConstants.FIXTURE_DIFFICULTY_SCALE[diff])
        currentTeam.sort(key=lambda x: x.adj_points, reverse=True)

    def get_next_fixture_difficulty(self, team):
        # Get the fixtures list for next gameweek
        for fixture in self.fixtures:
            if fixture.team_h == team:
                return fixture.team_h_difficulty
            elif fixture.team_a == team:
                return fixture.team_a_difficulty

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