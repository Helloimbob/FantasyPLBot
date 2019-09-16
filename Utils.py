from fpl.utils import position_converter
from fpl.utils import team_converter

def calc_roi(points, cost):
    return points / cost

def print_team(team, captain=True):
    for index, player in enumerate(team):
        if captain and index == 0:
            print(f"{player.web_name} (C) - "
                f"{position_converter(player.element_type)} - "
                f"{team_converter(player.team)}")
        elif captain and index == 1:
            print(f"{player.web_name} (VC) - "
                f"{position_converter(player.element_type)} - "
                f"{team_converter(player.team)}")
        else:
            print(player)

def sort_by_roi(playerList, ascending=True):
    roiPlayers = []
    for player in playerList:
        # Assign their calculated ROI
        setattr(player, 'roi', calc_roi(
            player.total_points, player.now_cost))
        roiPlayers.append(player)
    # sort by ROI
    roiPlayers.sort(key=lambda x: x.roi, reverse=ascending)
    return roiPlayers

def is_in_team(player, team):
    for currPlayer in team:
        if player.id == currPlayer.id:
            return True
    return False