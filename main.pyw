import pygame
import random
import time

pygame.init()

WIDTH, HEIGHT = 650, 650
FIELD_WIDTH = 490
FIELD_HEIGHT = 490
PADDING_X = (WIDTH - FIELD_WIDTH) // 2
PADDING_Y = 100

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Strategic Game")

WHITE = (255, 255, 255)
BLACK = (32, 32, 32)
RED = (255, 117, 95) 
BLUE = (95, 156, 255)
LIGHT_RED = (255, 200, 200) 
LIGHT_BLUE = (200, 220, 255) 
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)

SQUARE_SIZE = 70

font = pygame.font.SysFont(None, 30)
header_font = pygame.font.SysFont(None, 40)

MAX_DICE_PER_SQUARE = 10

def create_board():
    board = [[{"player": None, "dice": 0} for _ in range(7)] for _ in range(7)]
    
    remaining_dice_player1 = 50
    while remaining_dice_player1 > 0:
        x, y = random.randint(0, 6), random.randint(0, 6)
        if board[x][y]["player"] is None:
            board[x][y]["player"] = 1
            dice_count = min(random.randint(1, MAX_DICE_PER_SQUARE), remaining_dice_player1)
            board[x][y]["dice"] = dice_count
            remaining_dice_player1 -= dice_count

    remaining_dice_player2 = 50
    while remaining_dice_player2 > 0:
        x, y = random.randint(0, 6), random.randint(0, 6)
        if board[x][y]["player"] is None:
            board[x][y]["player"] = 2
            dice_count = min(random.randint(1, MAX_DICE_PER_SQUARE), remaining_dice_player2)
            board[x][y]["dice"] = dice_count
            remaining_dice_player2 -= dice_count

    for x in range(7):
        for y in range(7):
            if board[x][y]["player"] is None:
                board[x][y]["dice"] = random.randint(1, 3)

    return board

def draw_board(board, selected=None, target=None, ai_attack=None, message="", current_player=1):
    screen.fill(BLACK)
    player1_squares = sum(1 for x in range(7) for y in range(7) if board[x][y]["player"] == 1)
    player2_squares = sum(1 for x in range(7) for y in range(7) if board[x][y]["player"] == 2)
    header_text = f"{player1_squares} YOU VS OPPONENT {player2_squares}"
    header_render = header_font.render(header_text, True, WHITE)
    screen.blit(header_render, (WIDTH // 2 - header_render.get_width() // 2, 20))

    field_color = LIGHT_RED if current_player == 1 else LIGHT_BLUE
    pygame.draw.rect(screen, field_color, (PADDING_X, PADDING_Y, FIELD_WIDTH, FIELD_HEIGHT))

    for x in range(7):
        for y in range(7):
            color = BLACK
            if board[x][y]["player"] == 1:
                color = RED
            elif board[x][y]["player"] == 2:
                color = BLUE
            pygame.draw.rect(screen, color, (x * SQUARE_SIZE + PADDING_X, y * SQUARE_SIZE + PADDING_Y, SQUARE_SIZE, SQUARE_SIZE))
            if board[x][y]["dice"] > 0:
                text = font.render(str(board[x][y]["dice"]), True, WHITE)
                screen.blit(text, (x * SQUARE_SIZE + PADDING_X + 25, y * SQUARE_SIZE + PADDING_Y + 25))

    if selected:
        pygame.draw.rect(screen, GREEN, (selected[0] * SQUARE_SIZE + PADDING_X, selected[1] * SQUARE_SIZE + PADDING_Y, SQUARE_SIZE, SQUARE_SIZE), 3)

    if target:
        pygame.draw.rect(screen, YELLOW, (target[0] * SQUARE_SIZE + PADDING_X, target[1] * SQUARE_SIZE + PADDING_Y, SQUARE_SIZE, SQUARE_SIZE), 3)

    if ai_attack:
        attacker, target_ai = ai_attack
        pygame.draw.rect(screen, GREEN, (attacker[0] * SQUARE_SIZE + PADDING_X, attacker[1] * SQUARE_SIZE + PADDING_Y, SQUARE_SIZE, SQUARE_SIZE), 3)
        pygame.draw.rect(screen, YELLOW, (target_ai[0] * SQUARE_SIZE + PADDING_X, target_ai[1] * SQUARE_SIZE + PADDING_Y, SQUARE_SIZE, SQUARE_SIZE), 3)

    if message:
        text = font.render(message, True, WHITE)
        screen.blit(text, (10, HEIGHT - 50))

    pygame.display.flip()

def is_adjacent(x1, y1, x2, y2):
    return abs(x1 - x2) + abs(y1 - y2) == 1

def add_dice_randomly(board, player):
    controlled_squares = [(x, y) for x in range(7) for y in range(7) if board[x][y]["player"] == player]
    total_dice_to_add = len(controlled_squares)
    
    while total_dice_to_add > 0:
        x, y = random.choice(controlled_squares)
        if board[x][y]["dice"] < MAX_DICE_PER_SQUARE:
            dice_to_add = random.randint(1, min(total_dice_to_add, MAX_DICE_PER_SQUARE - board[x][y]["dice"]))
            board[x][y]["dice"] += dice_to_add
            total_dice_to_add -= dice_to_add

def ai_move(board):
    possible_moves = []
    for x in range(7):
        for y in range(7):
            if board[x][y]["player"] == 2 and board[x][y]["dice"] > 1:
                for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < 7 and 0 <= ny < 7 and board[nx][ny]["player"] != 2:
                        possible_moves.append(((x, y), (nx, ny)))
    if possible_moves:
        best_move = min(possible_moves, key=lambda move: board[move[1][0]][move[1][1]]["dice"])
        return best_move
    return None

def main():
    board = create_board()
    current_player = 1
    selected = None
    target = None

    running = True
    while running:
        if current_player == 2:
            while True:
                move = ai_move(board)
                if not move:
                    break

                attacker, target_ai = move
                attacker_dice = board[attacker[0]][attacker[1]]["dice"]
                target_player = board[target_ai[0]][target_ai[1]]["player"]
                target_dice = board[target_ai[0]][target_ai[1]]["dice"]

                draw_board(board, ai_attack=(attacker, target_ai), message="AI is choosing a move...", current_player=current_player)
                time.sleep(1)

                if target_player is not None:
                    attacker_roll = sum(random.randint(1, 6) for _ in range(attacker_dice))
                    defender_roll = sum(random.randint(1, 6) for _ in range(target_dice))
                    result_message = f"AI: {attacker_roll} vs {defender_roll}"
                    draw_board(board, message=result_message, current_player=current_player)
                    time.sleep(0.5)
                    if attacker_roll > defender_roll:
                        board[target_ai[0]][target_ai[1]]["player"] = 2
                        board[target_ai[0]][target_ai[1]]["dice"] = min(attacker_dice - 1, MAX_DICE_PER_SQUARE)
                        board[attacker[0]][attacker[1]]["dice"] = 1
                        result_message = "AI won!"
                    else:
                        board[attacker[0]][attacker[1]]["dice"] = 1
                        result_message = "AI lost!"
                    draw_board(board, message=result_message, current_player=current_player)
                    time.sleep(0.5)
                else:
                    board[target_ai[0]][target_ai[1]]["player"] = 2
                    board[target_ai[0]][target_ai[1]]["dice"] = min(attacker_dice - 1, MAX_DICE_PER_SQUARE)
                    board[attacker[0]][attacker[1]]["dice"] = 1
                    result_message = "AI captured the territory!"
                    draw_board(board, message=result_message, current_player=current_player)
                    time.sleep(0.5)

                draw_board(board, current_player=current_player)
            add_dice_randomly(board, 2)
            current_player = 1
        else:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    x = (event.pos[0] - PADDING_X) // SQUARE_SIZE
                    y = (event.pos[1] - PADDING_Y) // SQUARE_SIZE
                    if event.button == 3:
                        add_dice_randomly(board, 1)
                        current_player = 2
                    elif 0 <= x < 7 and 0 <= y < 7 and board[x][y]["player"] == 1 and board[x][y]["dice"] > 1:
                        selected = (x, y)
                        target = None
                    elif selected and is_adjacent(selected[0], selected[1], x, y):
                        target = (x, y)
                        attacker_dice = board[selected[0]][selected[1]]["dice"]
                        target_player = board[target[0]][target[1]]["player"]
                        target_dice = board[target[0]][target[1]]["dice"]

                        draw_board(board, selected=selected, target=target, message="You are choosing a move...", current_player=current_player)
                        time.sleep(1)

                        if target_player is not None and target_player != 1:
                            attacker_roll = sum(random.randint(1, 6) for _ in range(attacker_dice))
                            defender_roll = sum(random.randint(1, 6) for _ in range(target_dice))
                            result_message = f"You: {attacker_roll} vs {defender_roll}"
                            draw_board(board, message=result_message, current_player=current_player)
                            time.sleep(0.5)
                            if attacker_roll > defender_roll:
                                board[target[0]][target[1]]["player"] = 1
                                board[target[0]][target[1]]["dice"] = min(attacker_dice - 1, MAX_DICE_PER_SQUARE)
                                board[selected[0]][selected[1]]["dice"] = 1
                                result_message = "You won!"
                            else:
                                board[selected[0]][selected[1]]["dice"] = 1
                                result_message = "You lost!"
                            draw_board(board, message=result_message, current_player=current_player)
                            time.sleep(0.5)
                        elif target_player is None:
                            board[target[0]][target[1]]["player"] = 1
                            board[target[0]][target[1]]["dice"] = min(attacker_dice - 1, MAX_DICE_PER_SQUARE)
                            board[selected[0]][selected[1]]["dice"] = 1
                        selected = None
                        target = None

        draw_board(board, selected=selected, target=target, current_player=current_player)

    pygame.quit()

if __name__ == "__main__":
    main()