"""
Jawad Mohammed: 1032222
Marc Girard: 1155873

inspired by the checkers game:
https://github.com/vikaspro90/Checkers-game/blob/master/gamePlay.py
"""
from collections import Counter
import copy
import time
import math
import numpy as np

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

        # create and initialise the board
        self.board = {(x, y):0 for x in range(8) for y in range(8)}

        white_tokens = [(0,1), (1,1),   (3,1), (4,1),   (6,1), (7,1),
                        (0,0), (1,0),   (3,0), (4,0),   (6,0), (7,0)]
        black_tokens = [(0,7), (1,7),   (3,7), (4,7),   (6,7), (7,7),
                        (0,6), (1,6),   (3,6), (4,6),   (6,6), (7,6)]

        # fill up the board
        for xy in white_tokens:
            self.board[xy] = +1
        for xy in black_tokens:
            self.board[xy] = -1

        if self.colour == "white":
            self.opponentColour = "black"
            # get my tokens and opponent's positions
            self.my_tokens = [[key, value] for key, value in self.board.items() if value > 0]
            self.opponent_tokens = [[key, value] for key, value in self.board.items() if value < 0]
        else:
            self.opponentColour = "white"
            # get my tokens and opponent's positions
            self.my_tokens = [[key, value] for key, value in self.board.items() if value < 0]
            self.opponent_tokens = [[key, value] for key, value in self.board.items() if value > 0]

        self.movesRemaining = 250
        self.timeRemaining = 60

        self.depth = 3

        # compute nb of token left for each player
        self.total_nb_token_left = sum(abs(item[1]) for item in self.my_tokens)
        self.total_nb_token_left_opponent = sum(abs(item[1]) for item in self.opponent_tokens)

        self.save_last_board_states = []

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

        # if a move is possible -> play
        if self.isAnyMovePossible(self.board, self.colour) == True:
            #Changing the number of ply for minimax tree to budget time and get best possible moves
            # conditions regarding the amount of time left, the nb of remaining move left and the nb of token current player has
            if self.timeRemaining < 8:
                self.depth = 1
            elif self.timeRemaining < 15:
                self.depth = 2
            elif self.timeRemaining < 30:
                self.depth = 3
            else:
                if self.movesRemaining > 40:
                    self.depth = 3
                else:
                    self.depth = 4

            # get all possible move
            moves = self.getAllPossibleMoves(self.board, self.colour) 

            # if opponent player has one token left -> finish game quickly
            if self.total_nb_token_left >= 1 and self.total_nb_token_left_opponent == 1:
                # return move that will get us the closest as possible to opponent token
                bestMove = self.quickestMove(moves, self.opponent_tokens)
                if bestMove != None:
                    return bestMove

            best = None
            bestMove = None
            alpha = None
            beta = None
            for move in moves: # this is the max turn(1st level of minimax), so next should be min's turn                
                # evaluate if we take a smaller depth for search tree for current move
                if self.depth > 1:
                    depth = self.checkDistance_token_to_opponents(self.depth, move, self.my_tokens, self.opponent_tokens)
                else:
                    depth = self.depth
                # if the algorithm takes too much time, reduce depth to go
                intermidiateTimer = time.time()
                if intermidiateTimer - startTimer > 5 and depth > 2:
                    depth -= 1

                newBoard = copy.deepcopy(self.board)
                # perform move
                self.doMove(newBoard,move)
                
                # finish the game if possible (if no enemy token left after this move)
                finish_game = self.finishTheGame(newBoard,self.colour)
                if finish_game == True:
                    return move

                # check if state of board is repeated
                is_repeated_state = self.checkRepeatedBoardState(newBoard)
                if is_repeated_state == False:
                    #Beta is always None here as there is no parent MIN node. So no need to check if we can prune or not.
                    moveVal = self.alphaBeta_pruning(newBoard, self.colour, depth, 'min', self.opponentColour, alpha, beta)
                    if moveVal != None:
                        if best == None or moveVal > best:
                            bestMove = move
                            best = moveVal
                        if alpha == None or best > alpha:
                            alpha = best
                    if bestMove == None: # not possible normally
                        bestMove = moves[0]                   
        else:
            print("\n\nERROR: No Possible move!\n\n")

        stopTimer =  time.time()
        self.timeRemaining =  self.timeRemaining - (stopTimer - startTimer)
        self.movesRemaining = self.movesRemaining - 1

        return bestMove

    # evaluate if we take a smaller depth for search tree for current move
    def checkDistance_token_to_opponents(self, depth, move, my_tokens, opponent_tokens):
        
        if move[0] == "MOVE":
            x, y = move[2]
            nb_token_initially_at_move = [item[1] for item in my_tokens if item[0] == move[2]]

            if nb_token_initially_at_move[0] < 3: # if position has a stack of less than 3 tokens
                # compute euclidean with all opponent tokens
                for j in range(len(opponent_tokens)):
                    eucl_dist = math.sqrt((x-opponent_tokens[j][0][0])**2+(y-opponent_tokens[j][0][1])**2)
                    # if at least an opponent token is under 4 squares distance -> continue with given depth   
                    if eucl_dist <= 3.6:
                        return depth
            else: # if position has more than 3 tokens
                return depth

            # if no opponent token is under 3.6 squares distance -> continue with depth = 2
            depth = 2

        return depth

    # check if state of board already occured before
    def checkRepeatedBoardState(self, board):
        # convert to list and sort
        dic_to_list = [(k, v) for k, v in board.items()]
        # dic_to_list.sort(key = lambda x: x[0])
        # count = self.save_last_board_states.count(board) # count occurence
        count = 0
        for i in range(len(self.save_last_board_states)):
            flag = True
            for j in range(len(dic_to_list)):
                if dic_to_list[j] != self.save_last_board_states[i][j]:
                    flag = False
                    continue
            if flag == True:
                count += 1

        # if state of board has occurred more than twice, disregard current move (flag to True)
        if count > 1:
            return True
        return False

    # evaluate if the board given states that the game ends. is called after self.doMove function
    def finishTheGame(self, board, colour):
        finish_game = True
        if colour == "white":
            for value in board.values():
                if value < 0:
                    finish_game = False
        else:
            for value in board.values():
                if value > 0:
                    finish_game = False
        return finish_game

    # return move that will get us the closest as possible to opponent token
    def quickestMove(self, moves, opponent_tokens):
        bestMove = None
        pos_last_opp_token = opponent_tokens[0][0]
        best_next_pos = None
        # for each move, compute euclidean dist and return the move that will get our token closer to the opponents' one
        for move in moves:
            if move[0] == "MOVE":
                # eucl_dist_current_pos = math.sqrt((move[2][0]-pos_last_opp_token[0])**2+(move[2][1]-pos_last_opp_token[1])**2)
                eucl_dist_next_pos = math.sqrt((move[3][0]-pos_last_opp_token[0])**2+(move[3][1]-pos_last_opp_token[1])**2)
                if best_next_pos == None or (eucl_dist_next_pos <= best_next_pos[0] and move[1] <= best_next_pos[1]):
                   bestMove = move
                   best_next_pos = (eucl_dist_next_pos,move[1])
            else:
                return move
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

        # save up to 10 last states of the board and add to save state list
        dic_to_list = [(k, v) for k, v in self.board.items()]
        self.save_last_board_states.append(copy.deepcopy(dic_to_list))
        
        # get my tokens and opponent's positions
        if self.colour == "white":
            self.my_tokens = [[key, value] for key, value in self.board.items() if value > 0]
            self.opponent_tokens = [[key, value] for key, value in self.board.items() if value < 0]
        else:
            self.my_tokens = [[key, value] for key, value in self.board.items() if value < 0]
            self.opponent_tokens = [[key, value] for key, value in self.board.items() if value > 0]

        # update nb token left for each player
        self.total_nb_token_left = sum(abs(item[1]) for item in self.my_tokens)
        self.total_nb_token_left_opponent = sum(abs(item[1]) for item in self.opponent_tokens)

    # Returns whether any of the <colour> pieces can make a valid move at this time
    def isAnyMovePossible(self, board, colour):
        # Loop through all board positions
        for position, nb_token in board.items():
            x, y = position
            
            # Check if this position has our colour
            if (nb_token > 0 and colour == "white") or (nb_token < 0 and colour == "black"):
                nb_token = abs(nb_token)
                for i in range(1,nb_token+1):
                    if self.canMoveToPosition(board, colour, x, y, x-i, y) == True:            
                        # Can move left
                        return True
                    if self.canMoveToPosition(board, colour, x, y, x+i, y) == True:            
                        # Can move right
                        return True
                    if self.canMoveToPosition(board, colour, x, y, x, y-i) == True:            
                        # Can move down
                        return True
                    if self.canMoveToPosition(board, colour, x, y, x, y+i) == True:            
                        # Can move up
                        return True
        
        # If it can eliminate an enemy token, it has move
        if self.isBoomPossible(board, colour) == True:
            return True
            
        return False

    # Check whether (x1,y1) can move to (x2,y2) in one move
    def canMoveToPosition(self, board, colour, x1, y1, x2, y2):
        # check if positions are inside the board
        if x1 < 0 or y1 < 0 or x2 < 0 or y2 < 0 or x1 > 7 or y1 > 7 or x2 > 7 or y2 > 7:
            return False
        #check (x2,y2) position if there is enemy token(s)
        if (colour == "white" and board[(x2,y2)] < 0) or (colour == "black" and board[(x2,y2)] > 0):
            return False

        return True

    # Returns whether any of the <colour> pieces can make a Boom
    def isBoomPossible(self, board, colour):
        # Loop through all board positions
        for position, nb_token in board.items():
            x, y = position
            
            # Check if this position has a enemy token next to him
            if nb_token > 0 and colour == "white":
                for i in range(-1,2):
                    for j in range(-1,2):
                        if x+i >= 0 and y+j >= 0 and x+i <= 7 and y+j <= 7: # if (i,j) is inside the board
                            if board[(x+i,y+j)] < 0: # if there is an enemy token
                                return True
            elif nb_token < 0 and colour == "black":
                for i in range(-1,2):
                    for j in range(-1,2):
                        if x+i >= 0 and y+j >= 0 and x+i <= 7 and y+j <= 7: # if (i,j) is inside the board
                            if board[(x+i,y+j)] > 0: # if there is an enemy token
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
                for boom in boom_moves_for_position:
                    if boom not in boom_moves:
                        boom_moves.append(boom)

        moves = self.sortListMoves(board, colour, copy.deepcopy(moves))

        return boom_moves + moves

    def sortListMoves(self, board, colour, moves):
        # get side of each opponent token
        dic = {"bottom" : 0, "top" : 0}
        if colour == "white":
            for key, value in board.items():
                if value < 0 and key[1] >= 4:
                    dic["top"] += 1
                elif value < 0 and key[1] < 4:
                    dic["bottom"] += 1
        else:
            for key, value in board.items():
                if value > 0 and key[1] >= 4:
                    dic["top"] += 1
                elif value > 0 and key[1] < 4:
                    dic["bottom"] += 1

        # get side that has the more opponent tokens
        max_side = max(dic, key=lambda key: dic[key])
        # sort moves depending on where the most opponent's tokens are
        if max_side == "bottom":
            moves = sorted(moves, key = lambda x: x[3][1])
        else:
            moves = sorted(moves, key = lambda x: x[3][1], reverse = True)

        return moves

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


    # Alpha Beta pruning algorithm
    def alphaBeta_pruning(self, board, colour, depth, turn, opponentColour, alpha, beta):
        if depth > 1 and self.isAnyMovePossible(board, colour) == True: #Comes here depth-1 times and goes to else for leaf nodes.
            depth -= 1
            opti = None
            # MAX turn
            if turn == 'max' and self.isAnyMovePossible(board, colour) == True:
                moves = self.getAllPossibleMoves(board, colour) #Gets all possible moves for player
                # for each move, do algo
                for move in moves:
                    nextBoard = copy.deepcopy(board)
                    self.doMove(nextBoard,move)
                    if opti == None or beta == None or beta > opti: #None conditions are to check for the first times
                        value = self.alphaBeta_pruning(nextBoard, colour, depth, 'min', opponentColour, alpha, beta)
                        if value != None:
                            if opti == None or value > opti:
                                opti = value
                            if alpha == None or opti > alpha:
                                alpha = opti

            # MIN turn
            elif turn == 'min' and self.isAnyMovePossible(board, colour) == True:
                moves = self.getAllPossibleMoves(board, opponentColour) #Gets all possible moves for the opponent
                # for each move, do algo
                for move in moves:
                    nextBoard = copy.deepcopy(board)
                    self.doMove(nextBoard,move)
                    if alpha == None or opti == None or alpha < opti: #None conditions are to check for the first times
                        value = self.alphaBeta_pruning(nextBoard, colour, depth, 'max', opponentColour, alpha, beta)
                        if value != None:
                            if opti == None or value < opti: 
                                opti = value
                            if beta == None or opti < beta:
                                beta = opti
            # input("Press the <ENTER> key to continue...")
            return opti # opti will contain the best value for player in MAX turn and worst value for player in MIN turn

        else: #Comes here for the last level i.e leaf nodes
            value = 0
            for position, nb_token in board.items():
                x, y = position
                # Below, we count the number of token in a stack for each colour.
                # A player stack of more than 1 token is 1.1 times more valuable than a stack of 1 token.
                # An opponent stack of more than 1 token is 1.1 times worse for the player than a stack of 1 token.
                # By assigning more weight on stacks with several tokens, the AI will prefer killing opponent stacks of several token to killing a stack of 1 token.
                # It will also prefer saving player stacks of several tokens to saving player stack of 1 token when the situation demands.
                
                # evaluation of state of board
                if (colour == "white" and board[position] == 1) or (colour == "black" and board[position] == -1): # if my colour and position has 1 token
                    value += 1
                elif (colour == "white" and board[position] == -1) or (colour == "black" and board[position] == 1): # if opponent colour and position has 1 token
                    value -= 1
                elif (colour == "white" and board[position] > 1) or (colour == "black" and board[position] < -1): # if my colour and position has stack of tokens
                    value += (abs(board[position]) *1.1)
                elif (colour == "white" and board[position] < -1) or (colour == "black" and board[position] > 1): # if opponent colour and position has stack of tokens
                    value -= (abs(board[position]) *1.1)

            # calculate number of white and black tokens 
            if colour == "white":
                nb_my_token = sum(value for value in board.values() if value > 0)
                nb_opponent_token = sum(value for value in board.values() if value < 0)
            else:
                nb_my_token = sum(value for value in board.values() if value < 0)
                nb_opponent_token = sum(value for value in board.values() if value > 0)

            # draw move
            if nb_my_token == 0 and nb_opponent_token == 0:
                value += 10
            # win move
            if nb_opponent_token == 0:
                value += 40

            return value

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

            

