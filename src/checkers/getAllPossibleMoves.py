import gamePlay
from copy import deepcopy

def gridToSerial(x, y):
	# Returns the serial 1~32 of cell given the grid position(0,0)~(7,7)
	
	return 4*x+y//2+1
	
def getAllJumpMovesAtPosition(board, x, y):
	# Get all jump moves of position board(x,y)
	
	moves = []
	serial = gridToSerial(x, y)
	
	for i in [-2,2]:
		for j in [-2,2]:
			# Check all four directions
			if gamePlay.canMoveToPosition(board, x, y, x+i, y+j):
				tempBoard = deepcopy(board)	
				gamePlay.doMovePosition(tempBoard, x, y, x+i, y+j)
				childJumpMoves = getAllJumpMovesAtPosition(tempBoard, x+i, y+j)				
				if len(childJumpMoves) == 0:					
					moves.append([serial, gridToSerial(x+i, y+j)])
				else:					
					for m in childJumpMoves:
						l = [serial]
						l.extend(m)
						moves.append(l)
	
	return moves
	
def getAllPossibleMovesAtPosition(board, x, y):
	# Returns a tuple 
	# 1) list of all possible moves of the piece board[x][y]
	# 2) True/False, whether the moves are capture moves or not
	
	moves = []
	isCapture = False
		
	# Look for jumps
	l = getAllJumpMovesAtPosition(board, x, y)
	for m in l:
		moves.append(m)
		
	if len(moves) == 0: # No jump moves available
	
		# Look for plain moves
		serial = gridToSerial(x,y)
		
		if gamePlay.canMoveToPosition(board, x, y, x-1, y-1):
			moves.append([serial,gridToSerial(x-1,y-1)])
		if gamePlay.canMoveToPosition(board, x, y, x-1, y+1):
			moves.append([serial,gridToSerial(x-1,y+1)])
		if gamePlay.canMoveToPosition(board, x, y, x+1, y-1):
			moves.append([serial,gridToSerial(x+1,y-1)])
		if gamePlay.canMoveToPosition(board, x, y, x+1, y+1):
			moves.append([serial,gridToSerial(x+1,y+1)])
	else:
		isCapture = True
		
	return moves, isCapture
	
	
def getAllPossibleMoves(board, color):
	# Get a list of all possible moves of <color>
	
	moves = []
	
	isCapturePossible = gamePlay.isCapturePossible(board, color)
	
	# Loop through all board positions
	for piece in range(1, 33):
		xy = gamePlay.serialToGrid(piece)
		x = xy[0]
		y = xy[1]
		
		# Check whether this board position is our color
		if board[x][y].upper() == color.upper():
			
			l, isCapture = getAllPossibleMovesAtPosition(board, x, y)
			
			if isCapturePossible == isCapture:
				for m in l:
					moves.append(m)
	return moves