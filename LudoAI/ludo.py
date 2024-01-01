# WIP - Minimax for Ludo

import random, re, cProfile

def did_win(pieces):
    win_cond = False
    turn_won = -1
    for color,color_pieces in enumerate(pieces):
        same = True
        for pos in color_pieces:
            if pos != fix_pos(55,color) or pos == -1:
                same = False
                break
        if same:
            turn_won = color
            win_cond = True
            break
    return turn_won, win_cond

def print_board_state(pieces):
    for color,color_pieces in enumerate(pieces):
        print(f"---------\nColor: {color}")
        for piece,pos in enumerate(color_pieces):
            if pos != -1:
                if pos < fix_pos(50,color):
                    print(f'Piece {piece} in {pos%52+1} needs {55-(pos-13*color)} {"moves" if 55-(pos-13*color)>1 else "move"} to reach the goal!')
                elif pos < fix_pos(55,color):
                    print(f'Piece {piece} needs {55-(pos-13*color)} {"moves" if 55-(pos-13*color)>1 else "move"} to reach the goal!')
                else:
                    print(f'Piece {piece} reached the goal!')

def proper_input(text, handler, condition):
    try:
        raw = handler(input(text))
    except:
        raise Exception("Error while handling the input!")
    while not(condition(raw)):
        try:
            raw = handler(input(text))
        except:
            raise Exception("Error while handling the input!")
    return raw

def int_handler(x):
    raw_int_list = re.findall(r'-?\d+',x)
    if len(raw_int_list) == 0:
        return '<invalid>'
    else:
        return int(raw_int_list[0])

def pieces_in_yard(pieces, turn):
    return [piece for piece,pos in enumerate(pieces[turn]) if pos == -1]

def movable_pieces_in_board(pieces, turn, dice):
    return [piece for piece,pos in enumerate(pieces[turn]) if (pos != -1) and (pos+dice<=56+13*turn-1)]

def pieces_in_pos(pieces, pos):
    return [{'color':color, 'piece':piece} for color, turn_pieces in enumerate(pieces) for piece,cur_pos in enumerate(turn_pieces) if cur_pos%52 == pos]

def fix_pos(rel_pos, turn):
    return rel_pos+13*turn

def aval_moves(pieces, turn, dice, skip_bonus, player):
    # TODO: Implement blockade mechanic
    aval_new_pieces = []
    aval_pieces = []
    if player:
        print('Choose the piece be moved:')
    if dice == 6 and not(skip_bonus):
        aval_new_pieces = pieces_in_yard(pieces, turn)
        for new_piece in aval_new_pieces:
            if player:
                print(f"New piece can be brought from the yard: Piece {new_piece}")
    aval_pieces = movable_pieces_in_board(pieces, turn, dice)
    for cur_piece in aval_pieces:
        if player:
            print(f"Piece {cur_piece} can be moved {dice} {'times' if dice>1 else 'time'}")
    moves = aval_new_pieces + aval_pieces
    return moves


def do_move(pieces, color, piece, dice):
    # TODO: Implement capture mechanic
    new_pieces = [color_pieces.copy() for color_pieces in pieces]
    if piece in pieces_in_yard(pieces, color):
        new_pieces[color][piece] = fix_pos(0, color)
    else:
        new_pieces[color][piece] += dice
    return new_pieces

def score_game(pieces, turn):
    score = 0
    for pos in pieces[turn]:
        if pos == fix_pos(55,turn):
            score += 20+pos
        elif pos != -1:
            score += pos-13*turn
        else:
            score -= 1
    return score

def find_best_move(pieces, moves, turn, dice):
    best_move = 0
    best_score = -1000
    for choice,move in enumerate(moves):
        expected_score = MaxN(do_move(pieces, turn, move, dice), 10, (turn+1)%4, -1, False)[turn]
        if best_score < expected_score:
            best_score = expected_score
            best_move = choice
    return moves[best_move]

def MaxN(pieces, depth, turn, dice, recent_6):
    # Minimax variant for multiplayer games
    # Based on: https://stackoverflow.com/questions/14826451/extending-minimax-algorithm-for-multiple-opponents
    # TODO: Devise a pruning strategy to reduce the search space
    # Idea: https://faculty.cc.gatech.edu/~thad/6601-gradAI-fall2015/Korf_Multi-player-Alpha-beta-Pruning.pdf
    new_pieces = [color_pieces.copy() for color_pieces in pieces]
    win_turn, win_cond = did_win(new_pieces)
    if depth == 0 or win_cond:
        return [score_game(pieces, color) for color in range(4)]
    # Chance node
    if dice == -1:
        value = [0]*4
        ex_1 = MaxN(new_pieces, depth-1, turn, 1, recent_6)
        ex_2 = MaxN(new_pieces, depth-1, turn, 2, recent_6)
        ex_3 = MaxN(new_pieces, depth-1, turn, 3, recent_6)
        ex_4 = MaxN(new_pieces, depth-1, turn, 4, recent_6)
        ex_5 = MaxN(new_pieces, depth-1, turn, 5, recent_6)
        ex_6 = MaxN(new_pieces, depth-1, turn, 6, recent_6)
        value = [i_val + 1/6*ex_1[i] for i,i_val in enumerate(value)]
        value = [i_val + 1/6*ex_2[i] for i,i_val in enumerate(value)]
        value = [i_val + 1/6*ex_3[i] for i,i_val in enumerate(value)]
        value = [i_val + 1/6*ex_4[i] for i,i_val in enumerate(value)]
        value = [i_val + 1/6*ex_5[i] for i,i_val in enumerate(value)]
        value = [i_val + 1/6*ex_6[i] for i,i_val in enumerate(value)]
    # Decision node
    else:
        aval_pieces = aval_moves(new_pieces, turn, dice, False, False)
        value = [-1000]*4
        if len(aval_pieces) == 0:
            value = MaxN(new_pieces, depth-1, (turn+1)%4, -1, recent_6)
        for piece in aval_pieces:
            after_move = do_move(new_pieces, turn, piece, dice)
            if dice == 6 and not(recent_6):
                expected_score = MaxN(after_move, depth-1, turn, -1, True)
                if value[turn]<expected_score[turn]:
                    value = expected_score
            else:
                expected_score = MaxN(after_move, depth-1, (turn+1)%4, -1, False)
                if value[turn]<expected_score[turn]:
                    value = expected_score
    return value

running = True
turn = 0
pieces=[[-1 for i in range(4)] for j in range(4)]

PLAYER_TURN = -1

while running:
    print('--------------------------------------------\n\n')
    print_board_state(pieces)
    win_turn, win_cond = did_win(pieces)
    if win_cond:
        print(f'Player {win_turn} has won!')
        break
    print(f'\nTurn: {turn}')
    dice = random.randint(1,6)
    print(f'Dice: {dice}')
    print(f'Score: {[score_game(pieces,color) for color in range(4)]}')
    # Available moves
    cur_moves = aval_moves(pieces, turn, dice, False, turn == PLAYER_TURN)
    if len(cur_moves) > 0:
        if turn == 0:
            # Selecting the move(player)
            # Currently comparing a random player with the minimax heuristic
            #sel_move = proper_input("Select your move: ", int_handler, lambda x: x in cur_moves)
            sel_move = random.choice(cur_moves)
        else:
            # Selecting the best move(AI)
            sel_move = find_best_move(pieces, cur_moves, turn, dice)
        if sel_move in pieces_in_yard(pieces, turn):
            pieces = do_move(pieces, turn, sel_move, dice)
            rethrow = random.randint(1,6)
            print(f'Rethrow: {rethrow}')
            next_moves = aval_moves(pieces, turn, rethrow, True, turn == PLAYER_TURN)
            if turn == PLAYER_TURN:
                sel_move = proper_input("Select your next move: ", int_handler, lambda x: x in next_moves)
            else:
                sel_move = random.choice(next_moves)
            # Move execution
            pieces = do_move(pieces, turn, sel_move, rethrow)
        else:
            pieces = do_move(pieces, turn, sel_move, dice)
    # Turn advancement
    turn = (turn + 1)%4




# Edge case test

# pieces[0][0] = fix_pos(51,0)
# pieces[0][1] = fix_pos(53,0)
# print([score_game(pieces,color) for color in range(4)])
# test_moves = aval_moves(pieces, 0, 2, False, False)
# print(test_moves)
# move = find_best_move(pieces, test_moves, 0, 2)
# print(move)

# Profiling test    

# cProfile.run('print(MaxN(pieces, 12, turn, random.randint(1,6), False))')