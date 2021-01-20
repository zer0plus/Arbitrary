import sys
import math
#Name = Mitansh Desai
#Student ID = 101168117

def raise_exception(reason):
	"""
	HELPER FUNCTION
	Raises an 'exception' and quits program entirely
	"""
	print(f'Exception occurred: {reason}. The program will now exit.')
	sys.exit()

def get_direction(a, b):
	"""
	HELPER FUNCTION
	Get the direction from point a towards b
	"""
	diff_y = b[0] - a[0]
	diff_x = b[1] - a[1]

	if diff_y != 0 and diff_x != 0:
		return 'diagonal'

	return 'vertical' if diff_y != 0 else 'horizontal'

def validate_points(a, b):
	"""
	HELPER FUNCTION
	Make sure the difference between points is strictly (horizontal) or (vertical) or (diagonal)
	"""
	diff_y = b[0] - a[0]
	diff_x = b[1] - a[1]

	return (diff_y == 0 and diff_x != 0) or (diff_x == 0 and diff_y != 0) or abs(diff_x) == abs(diff_y)

def get_offset(a, b):
	"""
	HELPER FUNCTION
	Calculate the offset for stepping through path given by 2 points 1 at a time
	"""
	diff_y = b[0] - a[0]
	diff_x = b[1] - a[1]
	offset_x = 0
	offset_y = 0

	if diff_y > 0:
		offset_y = 1
	elif diff_y < 0:
		offset_y = -1

	if diff_x > 0:
		offset_x = 1
	elif diff_x < 0:
		offset_x = -1

	return (offset_x, offset_y)

def get_play_state():
	"""
	HELPER FUNCTION
	Asks user to play/quit, keeps running until valid input is given
	"""
	option = input('Choose P/p to Play, or Q/q to Quit: ').lower()
	if option == 'q':
		return False
	elif option == 'p':
		return True

	print('Invalid entry. Try again.')

	return get_play_state() # Run function again until valid user input

def get_coords(msg, bound, retry=False):
	"""
	HELPER FUNCTION
	Gets coordinates from user input to use for selecting & moving agents
	"""
	if retry:
		selection = input('Enter location: ')
	else:
		print(msg)
		selection = input('Enter location: ')

	try:
		# Make a temporary list for unpacking purposes to determine if one or both of the points were out of bounds
		point = [int(x) for x in selection.split(',') if int(x) > -1 and int(x) <= bound]
		row, col = point
	except Exception as e:
		if str(e).find('int()') != -1:
			# Cast to int() was not possible, user gave a string input
			print('Please enter 2 positive integers between [0,9] separated by \',\'.')
		else:
			# One or both of the values given were out of bounds
			print('At least one input is out of bound.')
		return get_coords(msg, bound, retry=True)
	
	return row, col

def get_pieces_left(board, piece):
	"""
	HELPER FUNCTION
	Get remaining pieces left on the board, used for enemies/agents
	"""
	pieces = 0
	for row in board:
		for col in row:
			if col == piece:
				pieces += 1

	return pieces

def display_endgame_board(board, trap_board):
	"""
	HELPER FUNCTION
	Combine the trap board with game board to reveal all hidden traps to display once the game is finished
	"""
	for t_row, cells in enumerate(trap_board):
		for t_col, cell in enumerate(cells):
			if cell == 'T':
				board[t_row][t_col] = 'T'

	display_board(board)

def display_board_stats(board, trap_board):
	"""
	HELPER FUNCTION
	Displays the board stats (agents/enemies/traps and the trap bounds)
	"""
	agents = 0
	enemies = 0
	traps = 0
	trap_bound = [999, 0] # start, finish trap rows

	for row, cells in enumerate(board):
		for col, cell in enumerate(cells):
			if cell == 'A':
				agents += 1
			elif cell == 'E':
				enemies += 1
			elif trap_board[row][col] == 'T':
				traps += 1
				if row < trap_bound[0]:
					trap_bound[0] = row
				if row > trap_bound[1]:
					trap_bound[1] = row

	print('Board stats:\n============')
	print(f'Total Agents (A): {agents}')
	print(f'Total Enemies (E): {enemies}')
	print(f'This board also has {traps} hidden traps (T) on rows [{trap_bound[0]} - {trap_bound[1]}]')

def read_file(filename):
    board = []
    try:
        # Dump each line into a new list containing pieces given by the file removing commas
        with open(filename) as f:
            for line in f:
                pieces = line.replace('\n', '').split(',')
                if pieces and pieces[0] != '':
                    board.append(pieces)
    except Exception as e:
        raise_exception('{} ({})'.format(e, type(e).__name__))

    # Verify the board is same width & length
    length = len(board)
    if length == 0:
        raise_exception('Board must not be empty')

    for i, row in enumerate(board):
        if len(row) != length:
            raise_exception(f'Row {i+1} is not the same width ({len(row)}) as the board length ({length})')
    return board

def display_board(board):
	rows = len(board)
	rows_str = ' '.join(str(i) for i in range(rows)).rjust(rows + 9)
	separator = '+ {} +'.format(' '.join('=' for i in range(rows))).rjust(rows + 11)

	print(rows_str)
	print(separator)
	for row, cells in enumerate(board):
		cells_str = ' '.join(x for x in cells)
		print('{} | {} | {}'.format(str(row), cells_str, str(row)).rjust(rows+13))
	print(separator)
	print(rows_str)

def check_for_valid_moves(board, r1, c1, r2, c2):
	# Check if distance between points is 1 or less (valid move attempt)
	if validate_points((r1, c1), (r2,c2)):
		selection = board[r1][c1]
		destination = board[r2][c2]

		# User selected empty space
		if selection == '-':
			return False

		# Hit another agent
		if destination == 'A':
			return False

		return True

	return False

def check_for_traps(board, r1, c1, r2, c2):
	# Find directionality offsets
	offset_x, offset_y = get_offset((r1, c1), (r2, c2))

	# Trap hit
	if board[r1][c1] == 'T':
		return True, r1, c1

	# Reached the destination without hitting traps
	if r1 == r2 and c1 == c2:
		return False, -1, -1

	# Step into next cell towards the destination to check for trap
	return check_for_traps(board, r1+offset_y, c1+offset_x, r2, c2)

def main():
	board = read_file('board.txt')
	trap_board = read_file('trap.txt')
	bound = len(board)-1
	desc = """
	You must kill all enemies to win this board.
	To kill an enemy, move an Agent to that Enemy's location.
	You can move Agents horizontally, vertically or diagonally.
	If your Agent walks on a hidden trap, they will die.
	If you choose a wrong move, you'll lose 2 points.
	If you kill an Enemy, you'll get 5 points.
	If you finish the board (kill all enemies), you'll get 10 more points.
	Game continues until you finish the board, or all Agents are dead, or you choose to quit.
	"""

	display_board(board)
	print('\n\n')
	display_board_stats(board, trap_board)
	print(desc.replace('\t', ''))

	score = 0
	started = False

	# Game loop
	while True:
		# Print board + score after initial game start
		if started:
			print('Current board:')
			display_board(board)
			print(f'Your current score is {score}\n')
		else:
			started = True

		# P/p Q/q input
		if not get_play_state():
			print('You have decided to quit the game..')
			break

		# Select coordinates to move agent
		sel_r, sel_c = get_coords('Choose the row,col of the Agent that you want to move:', bound)
		dest_r, dest_c = get_coords('Choose the row,col where you want to move your Agent to:', bound)

		point_a = (sel_r, sel_c)
		point_b = (dest_r, dest_c)

		# Check for valid move
		valid = check_for_valid_moves(board, sel_r, sel_c, dest_r, dest_c)
		if valid:
			direction = get_direction(point_a, point_b)
			print(f'Validating move.... valid {direction} move')
		else:
			if validate_points(point_a, point_b) and board[sel_r][sel_c] == 'A':
				print('Validating move.... Another agent is already there. Invalid Move!')
			else:
				print('Validating move.... invalid move')
			score -= 2
			continue

		# Check for traps if previous move was valid
		trap, row, col = check_for_traps(trap_board, sel_r, sel_c, dest_r, dest_c)
		if trap:
			board[sel_r][sel_c] = '-'
			board[row][col] = 'T'
			print(f'Oh no! A trap is found at {row},{col} and now your agent is dead! You lost 2 points.')
			score -= 2

			# All agents are dead, show endgame board revealing all traps
			if get_pieces_left(board, 'A') == 0:
				print('All agents are now dead..')
				display_endgame_board(board, trap_board)
				print(f'Your final score is {score}. Game is terminating.')
				break
			continue

		# Check if player has captured an enemy since they didn't step on any traps
		if board[dest_r][dest_c] == 'E':
			print('GOT an ENEMY!!! Scored 5..')
			score += 5

		# Move agent to destination
		board[sel_r][sel_c] = '-'
		board[dest_r][dest_c] = 'A'

		# All enemies are dead, add +10 to score and show endgame board revealing all traps
		if get_pieces_left(board, 'E') == 0:
			print('Well done!! All enemies are dead.')
			display_endgame_board(board, trap_board)
			score += 10
			print(f'Your final score is {score}! Game is terminating.')
			break

		print(f'You\'ve successfully moved to {dest_r},{dest_c}, no points are scored in this step though.')
if __name__ == "__main__":
	main()