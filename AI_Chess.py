import sys
import pygame
import chess

# Import the Minimax class
from Minimax_w_AB import find_best_move
from Minimax_w_AB_2 import find_best_move_2

# Initialize Pygame
pygame.init()

# Board settings
BOARD_SIZE = 512  # Size of the board in pixels
SQUARE_SIZE = BOARD_SIZE // 8  # Size of a square
BOARD_COLOR_1 = (240, 224, 200)  # Light square color
BOARD_COLOR_2 = (182, 113, 13)  # Dark square color
HIGHLIGHT_COLOR = (255, 0, 0)

# Load images
piece_images = {}
for color in ['w', 'b']:
    for piece in ['P', 'N', 'B', 'R', 'Q', 'K']:
        filename = f"pieceImages/{color}{piece}.svg"
        piece_images[color+piece] = pygame.transform.scale(pygame.image.load(filename), (140, 140))

# Initialize the board
board = chess.Board()


def draw_board(screen):
    for rank in range(8):
        for file in range(8):
            color = BOARD_COLOR_1 if (rank + file) % 2 == 0 else BOARD_COLOR_2
            pygame.draw.rect(screen, color, pygame.Rect(file*SQUARE_SIZE, rank*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))


def highlight_king_square(screen, board):
    king_pos = board.king(board.turn)
    if king_pos is not None:
        if board.is_check():
            file = chess.square_file(king_pos)
            rank = chess.square_rank(king_pos)
            pygame.draw.rect(screen, HIGHLIGHT_COLOR, pygame.Rect(file * SQUARE_SIZE, (7-rank) * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE), 5)


def draw_pieces(screen, board):
    for rank in range(8):
        for file in range(8):
            piece = board.piece_at(chess.square(file, 7-rank))
            if piece:
                piece_symbol = piece.symbol()
                color = 'w' if piece_symbol.isupper() else 'b'
                piece_image_key = color + piece_symbol.upper()
                screen.blit(piece_images[piece_image_key], pygame.Rect(file*SQUARE_SIZE+8, rank*SQUARE_SIZE+7, SQUARE_SIZE, SQUARE_SIZE))


def game_over_message(screen, result):
    font = pygame.font.SysFont(None, 64)
    text = font.render(result, True, (255, 255, 255))
    text_rect = text.get_rect(center=(BOARD_SIZE // 2, BOARD_SIZE // 2))
    pygame.draw.rect(screen, (0, 0, 255), (text_rect.x - 10, text_rect.y - 10, text_rect.width + 20, text_rect.height + 20))
    screen.blit(text, text_rect)
    pygame.display.flip()


def draw_new_game_button(screen):
    font = pygame.font.SysFont(None, 32)
    text = font.render("New Game", True, (255, 255, 255))
    text_rect = text.get_rect(center=(BOARD_SIZE // 2, BOARD_SIZE // 2 + 100))
    pygame.draw.rect(screen, (0, 0, 255), text_rect, border_radius=5)
    screen.blit(text, text_rect)


def main():
    screen = pygame.display.set_mode((BOARD_SIZE, BOARD_SIZE))
    pygame.display.set_caption('AI Chess')

    clock = pygame.time.Clock()

    selected_piece = None
    selected_piece_pos = None
    game_over = False
    initial_board_fen = board.fen()  # Initial positions of the pieces
    new_game_button_rect = pygame.Rect(BOARD_SIZE // 2 - 75, BOARD_SIZE // 2 + 100, 150, 40)
    rendered = False

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if game_over and new_game_button_rect.collidepoint(event.pos):
                    # Reset the game
                    board.set_fen(initial_board_fen)
                    game_over = False
                    rendered = False

                x, y = pygame.mouse.get_pos()
                file = x // SQUARE_SIZE
                rank = 7 - y // SQUARE_SIZE
                square = chess.square(file, rank)
                piece = board.piece_at(square)

                if piece and piece.color == board.turn:
                    selected_piece = piece
                    selected_piece_pos = square
                else:
                    selected_piece = None
                    selected_piece_pos = None

            elif event.type == pygame.MOUSEBUTTONUP:
                if selected_piece and selected_piece_pos is not None:
                    # Get the position where the mouse was released
                    x, y = pygame.mouse.get_pos()
                    new_file = x // SQUARE_SIZE
                    new_rank = 7 - y // SQUARE_SIZE
                    new_square = chess.square(new_file, new_rank)

                    # Create a potential move
                    move = chess.Move(selected_piece_pos, new_square)

                    # Check if this is a pawn reaching the opposite side for promotion
                    if board.piece_at(selected_piece_pos).piece_type == chess.PAWN and (new_rank == 0 or new_rank == 7):
                        # For simplicity, automatically promote to a Queen
                        move = chess.Move(selected_piece_pos, new_square, promotion=chess.QUEEN)

                    # Check if the move is legal, including the promotion
                    if move in board.legal_moves:
                        board.push(move)
                    else:
                        print("Illegal Move:", move)

                    # Reset selection
                    selected_piece = None
                    selected_piece_pos = None

        screen.fill((0, 0, 0))

        # Draw board and pieces
        draw_board(screen)
        highlight_king_square(screen, board)
        draw_pieces(screen, board)

        # Check for game over conditions
        if game_over:
            game_over_message(screen, "Draw!" if board.is_stalemate() else "Black Wins!" if board.turn == chess.WHITE else "White Wins!")
            pygame.draw.rect(screen, (0, 0, 255), new_game_button_rect, border_radius=5)
            font = pygame.font.SysFont(None, 32)
            text = font.render("New Game", True, (255, 255, 255))
            text_rect = text.get_rect(center=new_game_button_rect.center)
            screen.blit(text, text_rect)

        pygame.display.flip()
        clock.tick(60)

        # Check for game over conditions
        if not game_over and (board.is_stalemate() or board.is_checkmate()):
            game_over = True

        # Check for game over conditions
        if board.is_stalemate():
            game_over_message(screen, "Draw!")
            game_over = True
            rendered = True
        elif board.is_checkmate():
            if board.turn == chess.WHITE:
                game_over_message(screen, "Black Wins!")
            else:
                game_over_message(screen, "White Wins!")

            game_over = True
            rendered = True

        if game_over and (board.is_stalemate() or board.is_checkmate()) and not rendered:
            draw_new_game_button(screen)

        if not board.is_checkmate() and not board.is_stalemate():
            ######### BOT 1 ########
            if board.turn == chess.BLACK:
                print('BLACK Bot 1 AI is thinking...')
                move = find_best_move(board=board, depth=2)

                if move:
                    board.push(move)
                    print("Black played:", move)

            # if board.turn == chess.WHITE:
            #     print('WHITE Bot 1 AI is thinking...')
            #     move = find_best_move(board=board, depth=3)
            #
            #     if move:
            #         board.push(move)
            #         print("White played:", move)

            ######### BOT 2 ########
            # if board.turn == chess.BLACK:
            #     print('BLACK Bot 2 AI is thinking...')
            #     move = find_best_move(board=board, depth=20)
            #
            #     if move:
            #         board.push(move)
            #         print("Black played:", move)

            # if board.turn == chess.WHITE:
            #     print('WHITE Bot 2 AI is thinking...')
            #     move = find_best_move_2(board=board, depth=20)
            #
            #     if move:
            #         board.push(move)
            #         print("White played:", move)


if __name__ == '__main__':
    main()
