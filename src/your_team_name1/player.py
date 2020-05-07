
from collections import Counter
import copy
import time
import random

WhiteInitialMoves = [('MOVE', 1, (0, 0), (0, 1)),
('MOVE', 1, (0, 1), (0, 3)),
('MOVE', 1, (3, 0), (3, 1)),
('MOVE', 1, (3, 1), (3, 3)),
('MOVE', 1, (6, 0), (6, 1)),
('MOVE', 1, (6, 1), (6, 3))]

BlackInitialMoves = [('MOVE', 1, (0, 7), (0, 6)),
('MOVE', 1, (0, 6), (0, 4)),
('MOVE', 1, (3, 7), (3, 6)),
('MOVE', 1, (3, 6), (3, 4)),
('MOVE', 1, (6, 7), (6, 6)),
('MOVE', 1, (6, 6), (6, 4))]


class ExamplePlayer:
    def __init__(self, colour):
        """
        This method is called once at the beginning of the game to initialise
        your player. You should use this opportunity to set up your own internal
        representation of the game state, and any other information about the 
        game state you would like to maintain for the duration of the game.

        The parameter colour will be a string representing the player your 
        program will play as (White or Black). The value will be one of the 
        strings "white" or "black" correspondingly.
        """
        # TODO: Set up state representation.

        self.colour = colour
        if self.colour == "white":
            self.opponentColour = "black"
        else:
            self.opponentColour = "white"
        
        self.movesRemaining = 250
        self.timeRemaining = 60
        
        self.board = {(x, y):0 for x in range(8) for y in range(8)}

        white_tokens = [(0,1), (1,1),   (3,1), (4,1),   (6,1), (7,1),
                        (0,0), (1,0),   (3,0), (4,0),   (6,0), (7,0)]
        black_tokens = [(0,7), (1,7),   (3,7), (4,7),   (6,7), (7,7),
                        (0,6), (1,6),   (3,6), (4,6),   (6,6), (7,6)]

        for xy in white_tokens:
            if colour == "white":
                self.board[xy] = +1
            else:
                self.board[xy] = -1
        for xy in black_tokens:
            if colour == "black":
                self.board[xy] = +1
            else:
                self.board[xy] = -1

        # print(self.board)


    def action(self):
        """
        This method is called at the beginning of each of your turns to request 
        a choice of action from your program.

        Based on the current state of the game, your player should select and 
        return an allowed action to play on this turn. The action must be
        represented based on the spec's instructions for representing actions.
        """

        self.depth = 1
        best = None
        alpha = None
        beta = float("inf")

        if self.colour == 'white':
            initialMoves = WhiteInitialMoves
        if self.colour == 'black':
            initialMoves = BlackInitialMoves

        while(len(initialMoves) != 0):
            return initialMoves.pop(0)


        # TODO: Decide what action to take, and return it

        startTimer = time.time()
        if self.isAnyMovePossible() == True:
            moves = self.getAllPossibleMoves(self.board, self.colour, False)
            print("board:", self.board)

       
        
    #Changing the number of ply for minimax tree to budget time and get best possible moves         
        if self.timeRemaining < 4:
            self.depth = 8
        elif self.timeRemaining < 10:
            self.depth = 6
        elif self.timeRemaining < 30:
            self.depth = 4
        else:
            if self.movesRemaining > 65:
                self.depth = 2
            else:
                self.depth = 2
#       
        

        for move in moves: # this is the max turn(1st level of minimax), so next should be min's turn
            newBoard = copy.deepcopy(self.board)
            self.doMove(newBoard,move)
            #Beta is always inf here as there is no parent MIN node. So no need to check if we can prune or not.
            moveVal = self.alphaBeta_pruning(newBoard, self.colour, self.depth, 'min', self.opponentColour, alpha, beta)
            print(move,moveVal)

            if moveVal == None:
                moveVal = -float("inf")

            if best == None or moveVal > best:
                bestMove = move
                best = moveVal
            if alpha == None or best > alpha:
                alpha = best
                
        stopTimer =  time.time()
        self.timeRemaining =  self.timeRemaining - (stopTimer - startTimer)
        self.movesRemaining = self.movesRemaining - 1
       
        return bestMove
    
    def NEAR_SQUARES(self, square):
        # Code borrowed from the refree function
        x, y = square
        return {(x-1,y+1),(x,y+1),(x+1,y+1),
                (x-1,y),          (x+1,y),
                (x-1,y-1),(x,y-1),(x+1,y-1)} & set(self.board.keys())


    def update(self, colour, action):
        """
        This method is called at the end of every turn (including your player’s 
        turns) to inform your player about the most recent action. You should 
        use this opportunity to maintain your internal representation of the 
        game state and any other information about the game you are storing.

        The parameter colour will be a string representing the player whose turn
        it is (White or Black). The value will be one of the strings "white" or
        "black" correspondingly.

        The parameter action is a representation of the most recent action
        conforming to the spec's instructions for representing actions.

        You may assume that action will always correspond to an allowed action 
        for the player colour (your method does not need to validate the action
        against the game rules).
        """
        # TODO: Update state representation in response to action.
        
        if action[0] == "BOOM":
           # Recursive booms
            booms = [action[1]]
            for boom_square in booms:
                self.board[boom_square] = 0
                for near_square in self.NEAR_SQUARES(boom_square):
                    if self.board[near_square] != 0:
                        booms.append(near_square)
            
        else:
            nb_token_moved = action[1]
            start_position = action[2]
            end_position = action[3]
            if self.board[start_position] > 0:
                self.board[start_position] -= nb_token_moved
                self.board[end_position] += nb_token_moved
            elif self.board[start_position] < 0:
                self.board[start_position] += nb_token_moved
                self.board[end_position] -= nb_token_moved
            else:
                print("Action ERROR")

                
            
    # Returns whether any of the <colour> pieces can make a valid move at this time
    def isAnyMovePossible(self):
        # Loop through all board positions
        for position, nb_token in self.board.items():
            x, y = position
            
            # Check if this position has our colour
            if (nb_token > 0):
                nb_token = abs(nb_token)
                for i in range(1,nb_token+1):
                    if self.canMoveToPosition(x, y, x-i, y) == True:            
                        # Can move left
                        return True
                    if self.canMoveToPosition(x, y, x+i, y) == True:            
                        # Can move right
                        return True
                    if self.canMoveToPosition(x, y, x, y-i) == True:            
                        # Can move down
                        return True
                    if self.canMoveToPosition(x, y, x, y+i) == True:            
                        # Can move up
                        return True
        
        # If it can eliminate an enemy token, it has move
        if self.isBoomPossible() == True:
            return True
            
        return False

    # Check whether (x1,y1) can move to (x2,y2) in one move
    def canMoveToPosition(self, x1, y1, x2, y2):
        # check if positions are inside the board
        if x1 < 0 or y1 < 0 or x2 < 0 or y2 < 0 or x1 > 7 or y1 > 7 or x2 > 7 or y2 > 7:
            return False
        #check (x2,y2) position if non-empty
        if self.board[(x2,y2)] < 0:
            return False

        return True


    # Returns whether any of the <colour> pieces can make a Boom
    def isBoomPossible(self):
        # Loop through all board positions
        for position, nb_token in self.board.items():
            x, y = position
            
            # Check if this position has a enemy token next to him
            if nb_token >= 1 and self.colour == "white":
                for i in range(x-1,x+2):
                    for j in range(y-1,y+2):
                        if self.board[(i,j)] < 0:
                            return True
            elif nb_token <= -1 and self.colour == "black":
                for i in range(x-1,x+2):
                    for j in range(y-1,y+2):
                        if self.board[(i,j)] > 0:
                            return True  
        return False


    # Get a list of all possible moves of <colour>
    def getAllPossibleMoves(self, board, colour, lastlayer):
        moves = []
        
        # Loop through all board positions
        for position, nb_token in board.items():
            x, y = position
            
            # MOVE action
            if (nb_token > 0 ):
                if lastlayer == False:
                    n = abs(nb_token)
                    for i in range(1,n+1):
                        # Can move left
                        if self.canMoveToPosition(x, y, x-i, y) == True:                           
                            moves.append(("MOVE", i, (x, y), (x-i, y)))
                        # Can move right
                        if self.canMoveToPosition(x, y, x+i, y) == True:                                
                            moves.append(("MOVE", i, (x, y), (x+i, y)))
                        # Can move down
                        if self.canMoveToPosition(x, y, x, y-i) == True:                                
                            moves.append(("MOVE", i, (x, y), (x, y-i)))
                        # Can move up    
                        if self.canMoveToPosition(x, y, x, y+i) == True:                                
                            moves.append(("MOVE", i, (x, y), (x, y+i)))
                
            # # BOOM action
            # if nb_token > 0:
            #     for i in range(x-1,x+2):
            #         for j in range(y-1,y+2):
            #             # if there is a close enemy
            #             if i>=0 and i<=7 and j>=0 and j<=7: 
            #                 if board[(i,j)] < 0:
            #                     moves.append(("BOOM", (x, y)))  

            if nb_token > 0 :
                moves.append(("BOOM", (x, y)))

        return moves

    def doMove(self, board, move, lastlayer=True):
        # Will perform the move
        if move[0] == "MOVE":
                # print("it is a MOVE action")
                if self.colour == "white":
                    # next pos
                    board[move[3]] += move[1]
                    # current pos
                    board[move[2]] -= move[1]
                else:
                    # next pos
                    board[move[3]] -= move[1]
                    # current pos
                    board[move[2]] += move[1]
        else:
            # print("it is a BOOM action")
            # current pos
            board[move[1]] = 0
            # Recursive booms
            booms = [move[1]]
            for boom_square in booms:
                board[boom_square] = 0
                for near_square in self.NEAR_SQUARES(boom_square):
                    if board[near_square] != 0:
                        booms.append(near_square)
            

    def alphaBeta_pruning(self, board, colour, depth, turn, opponentColour, alpha, beta):
        if depth > 1: #Comes here depth-1 times and goes to else for leaf nodes.
            depth -= 1
            opti = None

            layer = False
            if depth == 1:
                layer = True


            if turn == 'max':
                moves = self.getAllPossibleMoves(board, colour, layer) #Gets all possible moves for player
                for move in moves:
                    nextBoard = copy.deepcopy(board)
                    self.doMove(nextBoard,move)
                    if opti == None or beta > opti:
                        value = self.alphaBeta_pruning(nextBoard, colour, depth, 'min', opponentColour, alpha, beta)
                        
                        if value == None:
                            value = -float("inf")

                        if value > opti:
                            opti = value

                        if alpha == None or opti > alpha:
                            alpha = opti

            elif turn == 'min':
                moves = self.getAllPossibleMoves(board, opponentColour, layer) #Gets all possible moves for the opponent
                for move in moves:
                    nextBoard = copy.deepcopy(board)
                    self.doMove(nextBoard,move)
                    if alpha == None or opti == None or alpha < opti: #None conditions are to check for the first times
                        value = self.alphaBeta_pruning(nextBoard, colour, depth, 'max', opponentColour, alpha, beta)
                        
                        if value == None:
                            value = float("inf")

                        if opti == None or value < opti: #opti = None for the first time
                            opti = value
                        if opti < beta:
                            beta = opti

            return opti # opti will contain the best value for player in MAX turn and worst value for player in MIN turn

        else: #Comes here for the last level i.e leaf nodes
            value = 0
            # for position, nb_token in board.items():
            #     # Below, we count the number of token in a stack for each colour.
            #     # A player stack of more than 1 token is 1.5 times more valuable than a stack of 1 token.
            #     # An opponent stack of more than 1 token is 1.5 times worse for the player than a stack of 1 token.
            #     # By assigning more weight on stacks with several tokens, the AI will prefer killing opponent stacks of several token to killing a stack of 1 token.
            #     # It will also prefer saving player stacks of several tokens to saving player stack of 1 token when the situation demands.
            #     if board[position] == 1:
            #         value += 1
            #     elif board[position] == -1:
            #         value -= 1
            #     elif board[position] > 1:
            #         value += nb_token
            #     elif board[position] < -1:
            #         value -= nb_token
            
            preStacks =  {token for token in self.board if self.board[token] > 0}
            preClusters = find_explosion_groups(self.board, preStacks)
            posStacks =  {token for token in board if board[token] > 0}
            posClusters =  find_explosion_groups(self.board, posStacks)
            nb_preClusters = sum([len(clus) for clus in preClusters if len(clus) > 1 or self.board[list(list(clus))[0]] > 1])
            nb_posClusters = sum([len(clus) for clus in posClusters if len(clus) > 1 or board[list(list(clus))[0]] > 1])
            
            value += 0.25*(nb_posClusters - nb_preClusters)
            # Change in number of our tokens
            deltaSelf = abs(sum([board[position] for position in board if board[position] > 0 ])) - abs(sum([self.board[position] for position in self.board if self.board[position] > 0 ]))

            # Change in number of opponent tokens
            deltaOpponent = sum([board[position] for position in board if board[position] < 0 ]) - sum([self.board[position] for position in self.board if self.board[position] < 0 ])

            print("deltas",deltaOpponent,deltaSelf)
            if deltaSelf == 0:
                deltaSelf = 1
            value = deltaOpponent/-deltaSelf

            # # for position, nb_token in board.items():
            # #     if (nb_token < 0 and self.depth != 1) or (nb_token > 0 and self.depth == 1):
            # #         booms = [position]
            # #         for boom_square in booms:
            # #             value += nb_token
            # #             for near_square in self.NEAR_SQUARES(boom_square):
            # #                 if board[near_square] != 0:
            # #                     booms.append(near_square)

            return value



BOOM_RADIUS = [(-1,+1), (+0,+1), (+1,+1),
            (-1,+0),          (+1,+0),
            (-1,-1), (+0,-1), (+1,-1)]
def around_squares(BOARD_SQUARES, xy):
    """
    Generate the list of squares surrounding a square
    (those affected by a boom action).
    """
    x, y = xy
    for dx, dy in BOOM_RADIUS:
        square = x+dx, y+dy
        if square in BOARD_SQUARES:
            yield square




def find_explosion_groups(BOARD_SQUARES,targets):

        # Part A sample solution
        """
        Partition a set of targets into groups that will 'boom' together.
        'targets' is a set of coordinate pairs. Return a set of frozensets
        representing the partition.
        """
        # 'up' is a union-find tree-based data structure
        up = {t: t for t in targets}
        # find performs a root lookup with path compression in 'up'
        def find(t):
            if up[t] == t:
                return t
            top = find(up[t])
            up[t] = top
            return top
        # run disjoint set formation algorithm to identify groups
        for t in targets:
            ttop = find(t)
            for u in around_squares(BOARD_SQUARES, t):
                if u in targets:
                    utop = find(u)
                    if ttop != utop:
                        up[utop] = ttop
        # convert disjoint set trees into Python sets
        groups = {}
        for t in targets:
            top = find(t)
            if top in groups:
                groups[top].add(t)
            else:
                groups[top] = {t}
        # return the partition
        return {frozenset(group) for group in groups.values()}

