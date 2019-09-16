
from Utils import sort_by_roi
from Utils import is_in_team
from Utils import print_team
from LineupPicker import LineupPicker

class TransferPicker(LineupPicker):
    async def pick_transfer(self, currentTeam, freeTransfers):
        # For each transfer
        transfersOut = []
        transferBudget = 3
        transferPositions = {1: 0, 2 : 0, 3 : 0, 4 : 0}

        sortedTeam = sort_by_roi(currentTeam, False)

        for player in sortedTeam:
            if (player not in transfersOut):
                transfersOut.append(player)
                transferPositions[player.element_type] += 1
                transferBudget += player.selling_price
                if (len(transfersOut) == freeTransfers):
                    break
        
        # First transfer out any unavailable players
        # then transfer out the worst performing player
        makeTransfers = []
        for position in transferPositions.keys():
            for player in self.roi_top_players(position, self.premium_limit[position]):
                if player not in self.unvailable and not is_in_team(player, currentTeam) and transferBudget >= player.now_cost and transferPositions[player.element_type] > 0:
                    makeTransfers.append(player)
                    transferBudget -= player.now_cost
                    transferPositions[player.element_type] = transferPositions[player.element_type] - 1
        
        print ('Out: ')
        print_team(transfersOut, False)
        print ('In: ')
        print_team(makeTransfers, False)
        print ('')
        # next find out 
        return makeTransfers