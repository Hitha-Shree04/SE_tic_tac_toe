"""
GameEngine: owns the board, turn state, and round-end logic.

You (the player) always play X and click to move. The computer always
plays O and moves automatically right after you, using a simple
random-move AI (see game/ai.py) - this is given infrastructure, not
something you need to build.

Starter version: no scoreboard yet, no first-player choice, and only
one combined reset control. Win/draw detection has known bugs (see
game/rules.py and check_round_end below) that Task 1 asks you to fix,
and move validation has a known gap (see handle_click) that Task 3
asks you to fix.
"""

from game.rules import check_winner, is_board_full
from game.renderer import board_pos_to_cell
from game.ai import choose_move

HUMAN_SYMBOL = 'X'
COMPUTER_SYMBOL = 'O'


class GameEngine:
    def __init__(self):
        self.scores = {'X': 0, 'O': 0, 'Draws': 0}
        self.starting_player = HUMAN_SYMBOL
        self.start_new_round()

    def start_new_round(self):
        self.board = [[None] * 3 for _ in range(3)]
        self.current_player = self.starting_player
        self.round_over = False
        self.winner = None
        self._maybe_take_computer_turn()

    def reset_match(self):
        self.scores = {'X': 0, 'O': 0, 'Draws': 0}
        self.starting_player = HUMAN_SYMBOL
        self.start_new_round()

    def toggle_starting_player(self):
        self.starting_player = COMPUTER_SYMBOL if self.starting_player == HUMAN_SYMBOL else HUMAN_SYMBOL

    def handle_click(self, pos):
        if self.round_over:
            return
        if self.current_player != HUMAN_SYMBOL:
            return
        cell = board_pos_to_cell(pos)
        if cell is None:
            return
        row, col = cell
        if self.board[row][col] is not None:
            return  # Cell is already occupied, reject click without turn advancement

        self.board[row][col] = self.current_player
        self.check_round_end()
        if not self.round_over:
            self.current_player = COMPUTER_SYMBOL
            self._maybe_take_computer_turn()

    def _maybe_take_computer_turn(self):
        if self.round_over or self.current_player != COMPUTER_SYMBOL:
            return
        move = choose_move(self.board)
        if move is None:
            return
        row, col = move
        self.board[row][col] = self.current_player
        self.check_round_end()
        if not self.round_over:
            self.current_player = HUMAN_SYMBOL

    def handle_keydown(self, key):
        import pygame
        if key == pygame.K_r:
            self.start_new_round()
        elif key == pygame.K_m:
            self.reset_match()
        elif key in (pygame.K_x, pygame.K_o, pygame.K_s):
            if key == pygame.K_x:
                self.starting_player = 'X'
            elif key == pygame.K_o:
                self.starting_player = 'O'
            else:
                self.toggle_starting_player()

    def check_round_end(self):
        winner = check_winner(self.board)
        if winner:
            self.round_over = True
            self.winner = winner
            self.scores[winner] += 1
            return

        if is_board_full(self.board):
            self.round_over = True
            self.winner = None
            self.scores['Draws'] += 1
            return

    def draw(self, surface, font):
        from game import renderer
        renderer.draw_board(surface, self.board)

        # Persistent Scoreboard at top
        score_text = f"X: {self.scores['X']}   O: {self.scores['O']}   Draws: {self.scores['Draws']}"
        renderer.draw_text(surface, font, score_text, (10, 10))

        # Current Turn / Status & Starting player info
        if not self.round_over:
            turn_label = "Your turn (X)" if self.current_player == HUMAN_SYMBOL else "Computer's turn (O)"
        else:
            turn_label = f"{self.winner} wins!" if self.winner else "Round ended in a Draw!"
        renderer.draw_text(surface, font, turn_label, (10, 42))

        # Banner / Controls guide at bottom
        if self.round_over:
            renderer.draw_banner(surface, font, "R: New Round | M: Reset Match")
        else:
            renderer.draw_banner(surface, font, f"Next round starts: {self.starting_player} (X/O/S to set)", color=(80, 80, 80))

