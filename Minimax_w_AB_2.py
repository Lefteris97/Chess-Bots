import chess
import math

# Global constants for null move pruning
NULL_MOVE_REDUCTION = 2  # Reduction depth for null move
NULL_MOVE_MARGIN = 100  # Score margin for null move cutoff

# Initialize hashmaps
history_score = {}
capture_moves = {}

# Define number of top moves
N = 3


# Function for null-move pruning
def null_move_pruning(board, depth, alpha, beta, maximizing_player):  # Add maximizing_player parameter
    if depth <= 0:
        return quiescence_search(board, alpha, beta, depth)

    # Null move cutoff condition
    if not board.is_check() and depth >= NULL_MOVE_REDUCTION:
        board.push(chess.Move.null())
        null_move_score = -null_move_pruning(board, depth - NULL_MOVE_REDUCTION - 1, -beta, -beta + 1, maximizing_player)
        board.pop()

        if null_move_score >= beta:
            return beta

    return -minimax(board, depth - 1, -beta, -alpha, not maximizing_player)


# Function to update killer moves
def update_capture_moves(move, depth):
    if depth not in capture_moves:
        capture_moves[depth] = [move]
    else:
        if move not in capture_moves[depth]:
            capture_moves[depth].insert(0, move)
            # Keep only the top N killer moves (N is defined above)
            capture_moves[depth] = capture_moves[depth][:N]


# Function for history heuristic
def prioritize_moves(board, maximizing_player):
    moves = list(board.legal_moves)
    # print('MOVES: ', moves)
    moves.sort(key=lambda move: -get_move_score(board, move, maximizing_player))

    return moves


# Function to get the score of a move based on history and evaluation score
def get_move_score(board, move, maximizing_player):
    score = history_score.get(move, 0)

    if maximizing_player:
        return score + evaluate_move(board, move)
    else:
        return -score - evaluate_move(board, move)


# Function to evaluate the impact of a move based on the current position
def evaluate_move(board, move):
    # Make the move on a copy of the board to evaluate its impact
    board_copy = board.copy()
    board_copy.push(move)

    # Evaluate the new position after making the move
    score_after_move = evaluate_board(board_copy)

    # Evaluate the current position before making the move
    score_before_move = evaluate_board(board)

    # Calculate the delta score (the difference between the scores after and before the move)
    delta_score = score_after_move - score_before_move

    return delta_score


# Update history table during search
def update_history(move, depth):
    if move in history_score:
        history_score[move] += depth * depth  # Adjust the increment based on depth
    else:
        history_score[move] = depth * depth


def find_best_move_2(board, depth):
    global history_score
    best_move = None
    max_eval = -math.inf
    alpha = -math.inf
    beta = math.inf
    maximizing_player = True

    moves = prioritize_moves(board, maximizing_player)

    for move in moves:
        board.push(move)
        eval_score = null_move_pruning(board, depth - 1, alpha, beta, maximizing_player)
        update_history(move, depth)
        board.pop()

        if eval_score is None:
            eval_score = -math.inf

        if eval_score > max_eval:
            max_eval = eval_score
            best_move = move

        alpha = max(alpha, eval_score)

    return best_move


def minimax(board, depth, alpha, beta, maximizing_player):

    if depth == 0:
        return quiescence_search(board, alpha, beta, depth)

    if maximizing_player:
        max_eval = -math.inf

        for move in board.legal_moves:
            board.push(move)
            eval_score = minimax(board, depth - 1, alpha, beta, False)
            board.pop()
            max_eval = max(max_eval, eval_score)
            alpha = max(alpha, eval_score)

            if beta <= alpha:
                break  # Beta cut-off

            # Update capture moves if it's a capture
            if board.is_capture(move):
                update_capture_moves(move, depth)

        return max_eval
    else:
        min_eval = math.inf

        for move in board.legal_moves:
            board.push(move)
            eval_score = minimax(board, depth - 1, alpha, beta, True)
            board.pop()
            min_eval = min(min_eval, eval_score)
            beta = min(beta, eval_score)

            if beta <= alpha:
                break  # Alpha cut-off

            # Update capture moves if it's a capture
            if board.is_capture(move):
                update_capture_moves(move, depth)

        return min_eval


def quiescence_search(board, alpha, beta, depth):
    stand_pat = evaluate_board(board)

    if stand_pat >= beta:
        return beta

    if alpha < stand_pat:
        alpha = stand_pat

    # Consider only capturing moves and checks
    if depth in capture_moves:
        moves = capture_moves[depth]
    else:
        moves = [move for move in board.legal_moves if board.is_capture(move) or board.is_check()]

    for move in moves:

        if move not in board.legal_moves:
            continue

        board.push(move)
        score = -quiescence_search(board, -beta, -alpha, depth)
        board.pop()

        if score >= beta:
            return beta
        if score > alpha:
            alpha = score

        # Update capture moves during quiescence search
        if board.is_capture(move):
            update_capture_moves(move, depth)

    return alpha


def evaluate_board(board):

    white_score = 0
    black_score = 0

    # Check for checkmate and stalemate
    if board.is_checkmate():
        if board.turn == chess.WHITE:
            return -100000  # Black wins, so return a very low score
        else:
            return 100000  # White wins, so return a very high score
    elif board.is_stalemate():
        return 0  # Stalemate, return a neutral score

    # Evaluate material advantage
    piece_values = {
        chess.PAWN: 100,
        chess.KNIGHT: 320,
        chess.BISHOP: 330,
        chess.ROOK: 500,
        chess.QUEEN: 900,
    }

    # Evaluate piece positioning
    pawn_table = [
        0, 0, 0, 0, 0, 0, 0, 0,
        50, 50, 50, 50, 50, 50, 50, 50,
        10, 10, 20, 30, 30, 20, 10, 10,
        5, 5, 10, 25, 25, 10, 5, 5,
        0, 0, 0, 20, 20, 0, 0, 0,
        5, -5, -10, 0, 0, -10, -5, 5,
        5, 10, 10, -20, -20, 10, 10, 5,
        0, 0, 0, 0, 0, 0, 0, 0
    ]

    knight_table = [
        -50, -40, -30, -30, -30, -30, -40, -50,
        -40, -20, 0, 0, 0, 0, -20, -40,
        -30, 0, 10, 15, 15, 10, 0, -30,
        -30, 5, 15, 20, 20, 15, 5, -30,
        -30, 0, 15, 20, 20, 15, 0, -30,
        -30, 5, 10, 15, 15, 10, 5, -30,
        -40, -20, 0, 5, 5, 0, -20, -40,
        -50, -40, -30, -30, -30, -30, -40, -50,
    ]

    bishop_table = [
        -20, -10, -10, -10, -10, -10, -10, -20,
        -10, 0, 0, 0, 0, 0, 0, -10,
        -10, 0, 5, 10, 10, 5, 0, -10,
        -10, 5, 5, 10, 10, 5, 5, -10,
        -10, 0, 10, 10, 10, 10, 0, -10,
        -10, 10, 10, 10, 10, 10, 10, -10,
        -10, 5, 0, 0, 0, 0, 5, -10,
        -20, -10, -10, -10, -10, -10, -10, -20,
    ]

    rook_table = [
        0, 0, 0, 0, 0, 0, 0, 0,
        5, 10, 10, 10, 10, 10, 10, 5,
        -5, 0, 0, 0, 0, 0, 0, -5,
        -5, 0, 0, 0, 0, 0, 0, -5,
        -5, 0, 0, 0, 0, 0, 0, -5,
        -5, 0, 0, 0, 0, 0, 0, -5,
        -5, 0, 0, 0, 0, 0, 0, -5,
        0, 0, 0, 5, 5, 0, 0, 0
    ]

    queen_table = [
        -20, -10, -10, -5, -5, -10, -10, -20,
        -10, 0, 0, 0, 0, 0, 0, -10,
        -10, 0, 5, 5, 5, 5, 0, -10,
        -5, 0, 5, 5, 5, 5, 0, -5,
        0, 0, 5, 5, 5, 5, 0, -5,
        -10, 5, 5, 5, 5, 5, 0, -10,
        -10, 0, 5, 0, 0, 0, 0, -10,
        -20, -10, -10, -5, -5, -10, -10, -20
    ]

    king_table = [
        -30, -40, -40, -50, -50, -40, -40, -30,
        -30, -40, -40, -50, -50, -40, -40, -30,
        -30, -40, -40, -50, -50, -40, -40, -30,
        -30, -40, -40, -50, -50, -40, -40, -30,
        -20, -30, -30, -40, -40, -30, -30, -20,
        -10, -20, -20, -20, -20, -20, -20, -10,
        20, 20, 0, 0, 0, 0, 20, 20,
        20, 30, 10, 0, 0, 10, 30, 20
    ]

    # king table end game
    king_table_eg = [
        -50, -40, -30, -20, -20, -30, -40, -50,
        -30, -20, -10, 0, 0, -10, -20, -30,
        -30, -10, 20, 30, 30, 20, -10, -30,
        -30, -10, 30, 40, 40, 30, -10, -30,
        -30, -10, 30, 40, 40, 30, -10, -30,
        -30, -10, 20, 30, 30, 20, -10, -30,
        -30, -30, 0, 0, 0, 0, -30, -30,
        -50, -30, -30, -30, -30, -30, -30, -50
    ]

    # Create mirrored versions of the tables for black
    mirrored_pawn_table = pawn_table[::-1]
    mirrored_knight_table = knight_table[::-1]
    mirrored_bishop_table = bishop_table[::-1]
    mirrored_rook_table = rook_table[::-1]
    mirrored_queen_table = queen_table[::-1]
    mirrored_king_table = king_table[::-1]
    mirrored_king_table_eg = king_table_eg[::-1]

    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            if piece.color == chess.WHITE:
                white_score += piece_values.get(piece.piece_type, 0)

                if piece.piece_type == chess.PAWN:
                    white_score += pawn_table[square]
                elif piece.piece_type == chess.KNIGHT:
                    white_score += knight_table[square]
                elif piece.piece_type == chess.BISHOP:
                    white_score += bishop_table[square]
                elif piece.piece_type == chess.ROOK:
                    white_score += rook_table[square]
                elif piece.piece_type == chess.QUEEN:
                    white_score += queen_table[square]
                elif piece.piece_type == chess.KING:
                    white_score += king_table[square]
                    # white_score += king_table[square] + king_table_eg[square]

            else:
                black_score -= piece_values.get(piece.piece_type, 0)

                if piece.piece_type == chess.PAWN:
                    black_score -= mirrored_pawn_table[chess.square_mirror(square)]
                elif piece.piece_type == chess.KNIGHT:
                    black_score -= mirrored_knight_table[chess.square_mirror(square)]
                elif piece.piece_type == chess.BISHOP:
                    black_score -= mirrored_bishop_table[chess.square_mirror(square)]
                elif piece.piece_type == chess.ROOK:
                    black_score -= mirrored_rook_table[chess.square_mirror(square)]
                elif piece.piece_type == chess.QUEEN:
                    black_score -= mirrored_queen_table[chess.square_mirror(square)]
                elif piece.piece_type == chess.KING:
                    black_score -= mirrored_king_table[chess.square_mirror(square)]
                    # black_score -= mirrored_king_table[chess.square_mirror(square)] - mirrored_king_table_eg[chess.square_mirror(square)]

    white_score += evaluate_piece_mobility(board)
    black_score -= evaluate_piece_mobility(board)

    white_score += evaluate_pawn_structure(board)
    black_score -= evaluate_pawn_structure(board)

    # Evaluate king safety (number of safe squares around the king)
    white_score += evaluate_king_safety(board)
    black_score += evaluate_king_safety(board)

    # Evaluate center control
    white_score += evaluate_center_control(board)
    black_score += evaluate_center_control(board)

    # print('WHITE SCORE: ', white_score)
    # print('BLACK SCORE: ', black_score)

    return white_score - black_score


def evaluate_piece_mobility(board):
    white_mobility = len(list(board.legal_moves))
    board.turn = not board.turn  # Switch sides temporarily
    black_mobility = len(list(board.legal_moves))
    board.turn = not board.turn  # Switch back
    # print('PIECE MOBILITY', white_mobility - black_mobility, board.turn)

    return white_mobility - black_mobility


def evaluate_pawn_structure(board):
    white_pawns = board.pieces(chess.PAWN, chess.WHITE)
    black_pawns = board.pieces(chess.PAWN, chess.BLACK)
    white_doubled_pawns = sum(1 for square in white_pawns if is_doubled_pawn(board, square))
    black_doubled_pawns = sum(1 for square in black_pawns if is_doubled_pawn(board, square))
    # print('PAWN STRUCTURE: ', (white_doubled_pawns - black_doubled_pawns) * 10, board.turn)

    return (white_doubled_pawns - black_doubled_pawns) * 10


def is_doubled_pawn(board, square):
    file = chess.square_file(square)
    rank = chess.square_rank(square)
    color = board.piece_at(square).color

    return sum(1 for f in range(8) if board.piece_at(chess.square(f, rank)) == chess.PAWN and chess.square_file(f) == file and board.piece_at(chess.square(f, rank)).color == color) > 1


def evaluate_king_safety(board):
    white_king_square = board.king(chess.WHITE)
    black_king_square = board.king(chess.BLACK)
    white_safety = len(board.attackers(chess.WHITE, white_king_square))
    black_safety = len(board.attackers(chess.BLACK, black_king_square))

    # print('KING SAFETY: ', white_safety - black_safety, board.turn)

    return (white_safety - black_safety) * 10


def evaluate_center_control(board):
    center_score = 0
    central_squares = [chess.E4, chess.D4, chess.E5, chess.D5]
    for square in central_squares:
        piece = board.piece_at(square)
        if piece:
            if piece.color == chess.WHITE:
                center_score += 10  # Reward control of central squares for white
            else:
                center_score -= 10  # Reward control of central squares for black

    return center_score * 10
