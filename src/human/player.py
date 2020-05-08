
from collections import Counter
import copy
import time
import math
import random
import ast

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

    def action(self):
        """
        This method is called at the beginning of each of your turns to request 
        a choice of action from your program.

        Based on the current state of the game, your player should select and 
        return an allowed action to play on this turn. The action must be
        represented based on the spec's instructions for representing actions.
        """
        # TODO: Decide what action to take, and return it

        startTimer = time.time()
        bestMove = None

        moved = False
        while moved == False:
            print('Possible moves:', self.getAllPossibleMoves(self.board, self.colour))
            bestMove = input("Please enter your move(" + self.colour + "): ")
            try:
                bestMove = ast.literal_eval(bestMove)
            except:
                print("\nWrong input, try again:\n")
            if (len(bestMove) == 4 and bestMove[0] == "MOVE") or (len(bestMove) == 2 and bestMove[0] == "BOOM"):
                moved = True

        stopTimer =  time.time()
        self.timeRemaining =  self.timeRemaining - (stopTimer - startTimer)
        self.movesRemaining = self.movesRemaining - 1

        return bestMove


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
            position = action[1]
            x, y = position
            self.board[position] = 0
            # Recursive booms
            self.checkCollateralBOOM(self.board, x, y)
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
        #check (x2,y2) position if there is enemy token(s)
        if (self.colour == "white" and self.board[(x2,y2)] < 0) or (self.colour == "black" and self.board[(x2,y2)] > 0):
            return False

        return True

    # Returns whether any of the <colour> pieces can make a Boom
    def isBoomPossible(self):
        # Loop through all board positions
        for position, nb_token in self.board.items():
            x, y = position
            
            # Check if this position has a enemy token next to him
            if nb_token > 0 and self.colour == "white":
                for i in range(-1,2):
                    for j in range(-1,2):
                        if x+i >= 0 and y+j >= 0 and x+i <= 7 and y+j <= 7: # if (i,j) is inside the board
                            if self.board[(x+i,y+j)] < 0: # if there is an enemy token
                                return True
            elif nb_token < 0 and self.colour == "black":
                for i in range(-1,2):
                    for j in range(-1,2):
                        if x+i >= 0 and y+j >= 0 and x+i <= 7 and y+j <= 7: # if (i,j) is inside the board
                            if self.board[(x+i,y+j)] > 0: # if there is an enemy token
                                return True  
        return False


    # Get a list of all possible moves of <colour>
    def getAllPossibleMoves(self, board, colour):
        moves = []
        boom_moves = []

        isBoomPossible = self.isBoomPossible(board, colour)
        nb_boom_move = 0
        # Loop through all board positions
        for position, nb_token in board.items():
            x, y = position

            # check if that position has one of our token
            if (nb_token > 0 and colour == "white") or (nb_token < 0 and colour == "black"):
                boom_moves_for_position, moves_for_position, isBoom = self.getAllPossibleMovesAtPosition(board, colour, x, y, nb_token)
                moves = moves + moves_for_position
                boom_moves = boom_moves + boom_moves_for_position

        # ordering moves
        if colour == 'white':
            # boom_moves.sort(key = lambda x: x[1][1], reverse=True)
            moves.sort(key = lambda x: x[3][1], reverse=True)
        if colour == 'black':
            # boom_moves.sort(key = lambda x: x[1][1])
            moves.sort(key = lambda x: x[3][1])

        return boom_moves + moves

    # Returns a tuple : list of all possible moves at the current position and if the moves are Boom moves
    def getAllPossibleMovesAtPosition(self, board, colour, x, y, nb_token):
        # MOVE action
        moves = []
        isBoom = False

        boom_moves = self.getAllBoomMovesAtPosition(board, colour, x, y, nb_token)

        n = abs(nb_token)
        for i in range(1,n+1): # move to x/y +- i square
            for j in range(1,n+1): # move j nb token
                # Can move left
                if self.canMoveToPosition(board, colour, x, y, x-i, y) == True:
                    moves.append(("MOVE", j, (x, y), (x-i, y)))
                # Can move right
                if self.canMoveToPosition(board, colour, x, y, x+i, y) == True:  
                    moves.append(("MOVE", j, (x, y), (x+i, y)))
                # Can move down
                if self.canMoveToPosition(board, colour, x, y, x, y-i) == True:                                
                    moves.append(("MOVE", j, (x, y), (x, y-i)))
                # Can move up    
                if self.canMoveToPosition(board, colour, x, y, x, y+i) == True:                                
                    moves.append(("MOVE", j, (x, y), (x, y+i)))
        
        if len(boom_moves) == 0:
            isBoom == True

        return boom_moves, moves, isBoom

    # get all possible boom moves for a given position
    def getAllBoomMovesAtPosition(self, board, colour, x, y, nb_token):
        boom_moves = []
        if nb_token > 0 and colour == "white":
            for i in range(-1,2):
                for j in range(-1,2):
                    if x+i >= 0 and y+j >= 0 and x+i <= 7 and y+j <= 7: # if (i,j) is inside the board
                        if board[(x+i,y+j)] < 0: # if there is an enemy token
                            boom_moves.append(("BOOM", (x, y)))
        elif nb_token < 0 and colour == "black":
            for i in range(-1,2):
                for j in range(-1,2):
                    if x+i >= 0 and y+j >= 0 and x+i <= 7 and y+j <= 7: # if (i,j) is inside the board
                        if board[(x+i,y+j)] > 0: # if there is an enemy token
                            boom_moves.append(("BOOM", (x, y)))
        
        return boom_moves

    # perform the move and "updates" the board
    def doMove(self, board, move):
        # Will perform the move
        if move[0] == "MOVE":
            nb_token_moved = move[1]
            start_position = move[2]
            end_position = move[3]
            if board[start_position] > 0:
                # current pos
                board[start_position] -= nb_token_moved
                # next pos
                board[end_position] += nb_token_moved
            else:
                # current pos
                board[start_position] += nb_token_moved
                # next pos
                board[end_position] -= nb_token_moved
        else: # if move[0] == "BOOM"
            # current pos
            board[move[1]] = 0
            x, y = move[1]
            self.checkCollateralBOOM(board, x, y)

    # checks if there is a recursive explosion of token
    def checkCollateralBOOM(self, board, x, y):
        for i in range(-1,2):
            for j in range(-1,2):
                if x+i >= 0 and y+j >= 0 and x+i <= 7 and y+j <= 7: # if (i,j) is inside the board
                    if board[(x+i,y+j)] != 0: # if there is a token on position (i,j)
                        board[(x+i,y+j)] = 0
                        self.checkCollateralBOOM(board, x+i, y+j)
       

    # display board
    def print_board_prototype(self, board):

        new_board = []
        i=0
        j=8
        new_board = list(board.values())
        inter = list()
        for _ in range(8):
            inter.append(new_board[i:j])
            i = j
            j = j+8

        new_board = []
        for i in range(0,8):
            new_board.append([inter[j][7-i] for j in range(0,8)])

        stri = '-'*50
        for j in new_board:
            stri+='\n'
            for item in j:
                stri += '|\t'+ str(item)+'\t'
            stri += '\n'
            stri += '-'*50

        print(stri.expandtabs(3))

            

