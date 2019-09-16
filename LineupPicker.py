from fpl import FPL
import FPLConstants
from FantasyPicker import FantasyPicker

class LineupPicker(FantasyPicker):
    async def get_current_team(self):
        user = await self.fpl.get_user(FPLConstants.BOT_ID)
        await self.fpl.login()
        picks = await user.get_team()

        currentTeamIds = []
        currentTeam = []

        for player in picks:
            currentTeamIds.append(player.get('element'))

        currentTeam = await self.fpl.get_players(currentTeamIds)
        for player in currentTeam:
            for pick in picks:
                if (player.id == pick.get('element')):
                    setattr(player, 'selling_price', pick.get('selling_price'))
                    break

        return currentTeam