
from collections import Counter
import copy
import time
import random


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
            self.board[xy] = +1
        for xy in black_tokens:
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
        # TODO: Decide what action to take, and return it

        '''Just play randomly among the possible moves'''
        moves = []
        if self.isAnyMovePossible() == True:
            moves = self.getAllPossibleMoves(self.board, self.colour)
    
        bestMove = moves[random.randint(0,len(moves) - 1)]
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
            if colour == "white":
                self.board[action[2]] -= action[1]
                self.board[action[3]] += action[1]
            else:
                self.board[action[2]] += action[1]
                self.board[action[3]] -= action[1]

            
    # Returns whether any of the <colour> pieces can make a valid move at this time
    def isAnyMovePossible(self):
        # Loop through all board positions
        for position, nb_token in self.board.items():
            x, y = position
            
            # Check if this position has our colour
            if (nb_token > 0 and self.colour == "white") or (nb_token < 0 and self.colour == "black"):
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
        if self.board[(x2,y2)] != 0:
            return False

        return True


    # Returns whether any of the <colour> pieces can make a Boom
    def isBoomPossible(self):
        # Loop through all board positions
        for position, nb_token in self.board.items():
            x, y = position
            
            # Check if this position has a enemy token next to him
            if nb_token > 0 and self.colour == "white":
                for i in range(x-1,x+2):
                    for j in range(y-1,y+2):
                        if self.board[(i,j)] < 0:
                            return True
            elif nb_token < 0 and self.colour == "black":
                for i in range(x-1,x+2):
                    for j in range(y-1,y+2):
                        if self.board[(i,j)] > 0:
                            return True  
        return False


    # Get a list of all possible moves of <colour>
    def getAllPossibleMoves(self, board, colour):
        moves = []
        
        # Loop through all board positions
        for position, nb_token in board.items():
            x, y = position
            
            # MOVE action
            if (nb_token > 0 and colour == "white") or (nb_token < 0 and colour == "black"):
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
            # if nb_token > 0 and colour == "white":
            #     for i in range(x-1,x+2):
            #         for j in range(y-1,y+2):
            #             # if there is a close enemy
            #             if i>=0 and i<=7 and j>=0 and j<=7:
            #                 if board[(i,j)] < 0:
            #                     moves.append(("BOOM", (x, y)))
            # elif nb_token < 0 and colour == "black":
            #     for i in range(x-1,x+2):
            #         for j in range(y-1,y+2):
            #             # if there is a close enemy
            #             if i>=0 and i<=7 and j>=0 and j<=7:
            #                 if board[(i,j)] > 0:
            #                     moves.append(("BOOM", (x, y)))   

            # # BOOM action
            if nb_token > 0 and colour == "white":
                moves.append(("BOOM", (x, y)))
            elif nb_token < 0 and colour == "black":
                moves.append(("BOOM", (x, y)))

        return moves

    def doMove(self, board, move):
        # Will perform the move
        if move[0] == "MOVE":
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
            print("it is a BOOM action")
            # current pos
            board[move[1]] = 0
            # Recursive booms
            booms = [move[1]]
            for boom_square in booms:
                board[boom_square] = 0
                for near_square in self.NEAR_SQUARES(boom_square):
                    if board[near_square] != 0:
                        booms.append(near_square)