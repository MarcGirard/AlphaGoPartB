import gamePlay
from copy import deepcopy
from getAllPossibleMoves import getAllPossibleMoves

'''
The code makes use of recursion to implement minimax with alpha beta pruning.
'''
def evaluation(board, color, depth, turn, opponentColor, alpha, beta):
    if depth > 1: #Comes here depth-1 times and goes to else for leaf nodes.
        depth -= 1
        opti = None
        if turn == 'max':
            moves = getAllPossibleMoves(board, color) #Gets all possible moves for player
            for move in moves:
                nextBoard = deepcopy(board)
                gamePlay.doMove(nextBoard,move)
                if beta > opti:
                    value = evaluation(nextBoard, color, depth, '9', opponentColor, alpha, beta)
                    if value > opti: #None is less than everything and anything so we don't need opti == None check
                        opti = value
                    if opti > alpha:
                        alpha = opti

        elif turn == 'min':
            moves = getAllPossibleMoves(board, opponentColor) #Gets all possible moves for the opponent
            for move in moves:
                nextBoard = deepcopy(board)
                gamePlay.doMove(nextBoard,move)
                if alpha == None or opti == None or alpha < opti: #None conditions are to check for the first times
                    value = evaluation(nextBoard, color, depth, 'max', opponentColor, alpha, beta)
                    if opti == None or value < opti: #opti = None for the first time
                        opti = value
                    if opti < beta:
                        beta = opti

        return opti # opti will contain the best value for player in MAX turn and worst value for player in MIN turn

    else: #Comes here for the last level i.e leaf nodes
        value = 0
        for piece in range(1, 33):
            xy = gamePlay.serialToGrid(piece)
            x = xy[0]
            y = xy[1]
            #Below, we count the number of kings and men for each color.
            #A player king is 1.5 times more valuable than a player man.
            #An opponent king is 1.5 times worse for the player than an opponent man.
            #By assigning more weight on kings, the AI will prefer killing opponent kings to killing opponent men.
            #It will also prefer saving player kings to saving player men when the situation demands.
            #If a player king is double the value of a man, then AI may choose to sacrifice a man to make a king.
            #To avoid this, a factor of 1.5 has been chosen.
            if board[x][y] == color.lower():
                value += 2
            elif board[x][y] == opponentColor.lower():
                value -= 2
            elif board[x][y] == color.upper():
                value += 3
            elif board[x][y] == opponentColor.upper():
                value -= 3
        return value

def nextMove(board, color, time, movesRemaining):
    moves = getAllPossibleMoves(board, color)
    opponentColor = gamePlay.getOpponentColor(color)
    depth = 5
    best = None
    alpha = None
    beta = float("inf")
    for move in moves: # this is the max turn(1st level of minimax), so next should be min's turn
        newBoard = deepcopy(board)
        gamePlay.doMove(newBoard,move)
        #Beta is always inf here as there is no parent MIN node. So no need to check if we can prune or not.
        moveVal = evaluation(newBoard, color, depth, 'min', opponentColor, alpha, beta)
        if best == None or moveVal > best:
            bestMove = move
            best = moveVal
        if best > alpha:
            alpha = best
    return bestMove