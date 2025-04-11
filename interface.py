#!/usr/bin/env python3
import tkinter as tk
import math
import time
from utils import State, Action, convert_board_to_string
import AIplayer


# Constants for drawing
WINDOW_SIZE = 600
MACRO_SIZE = 3           # 3x3 macro board
LOCAL_SIZE = 3           # Each local board is 3x3
CELL_SIZE = WINDOW_SIZE // (MACRO_SIZE * LOCAL_SIZE)
LINE_WIDTH = 2
MACRO_LINE_WIDTH = 4

class UltimateTicTacToeGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Ultimate Tic Tac Toe - Human vs AI")
        self.canvas = tk.Canvas(root, width=WINDOW_SIZE, height=WINDOW_SIZE)
        self.canvas.pack()

        # Define markers
        self.human_marker = 2  # Human plays as X
        self.ai_marker = 1    # AI plays as O

        # Initialize game state to None (game starts after user choice)
        self.state = None
        self.ai_agent = AIplayer.StudentAgent() # AI agent

        # Pause flag
        self.paused = False

        # Add start buttons to choose who goes first
        self.start_human_button = tk.Button(root, text="Start with Human (X)", command=lambda: self.start_game(self.human_marker))
        self.start_human_button.pack(side=tk.LEFT, padx=10)

        self.start_ai_button = tk.Button(root, text="Start with AI (O)", command=lambda: self.start_game(self.ai_marker))
        self.start_ai_button.pack(side=tk.LEFT, padx=10)

        # Add Pause/Resume button
        self.pause_button = tk.Button(root, text="Pause", command=self.toggle_pause)
        self.pause_button.pack(side=tk.LEFT, padx=10)

        # Bind click events for human input
        self.canvas.bind("<Button-1>", self.on_click)

    def start_game(self, starting_player):
        """Initialize and start the game with the chosen starting player."""
        self.state = State(fill_num=starting_player)
        self.paused = False
        self.pause_button.config(text="Pause")
        self.draw_board()
        # If AI goes first, schedule its move
        if starting_player == self.ai_marker:
            self.root.after(500, self.ai_move)

    def toggle_pause(self):
        """Toggle pause state and handle AI move on resume."""
        self.paused = not self.paused
        if self.paused:
            self.pause_button.config(text="Resume")
        else:
            self.pause_button.config(text="Pause")
            # If resumed and it’s AI’s turn, schedule the next move
            if self.state and self.state.fill_num == self.ai_marker:
                self.root.after(500, self.ai_move)

    def draw_board(self):
        """Draw the current game state on the canvas."""
        if self.state is None:
            return
        self.canvas.delete("all")
        # Draw local grid lines for each macro board
        for macro_row in range(MACRO_SIZE):
            for macro_col in range(MACRO_SIZE):
                x0 = macro_col * LOCAL_SIZE * CELL_SIZE
                y0 = macro_row * LOCAL_SIZE * CELL_SIZE
                for i in range(1, LOCAL_SIZE):
                    x = x0 + i * CELL_SIZE
                    self.canvas.create_line(x, y0, x, y0 + LOCAL_SIZE * CELL_SIZE, width=LINE_WIDTH)
                    y = y0 + i * CELL_SIZE
                    self.canvas.create_line(x0, y, x0 + LOCAL_SIZE * CELL_SIZE, y, width=LINE_WIDTH)
        # Draw macro grid lines (thicker)
        for i in range(1, MACRO_SIZE):
            x = i * LOCAL_SIZE * CELL_SIZE
            self.canvas.create_line(x, 0, x, WINDOW_SIZE, width=MACRO_LINE_WIDTH)
            y = i * LOCAL_SIZE * CELL_SIZE
            self.canvas.create_line(0, y, WINDOW_SIZE, y, width=MACRO_LINE_WIDTH)

        # Draw markers on individual cells
        board = self.state.board
        for macro_row in range(MACRO_SIZE):
            for macro_col in range(MACRO_SIZE):
                local_board = board[macro_row][macro_col]
                for local_row in range(LOCAL_SIZE):
                    for local_col in range(LOCAL_SIZE):
                        val = local_board[local_row][local_col]
                        if val != 0:
                            x = (macro_col * LOCAL_SIZE + local_col) * CELL_SIZE + CELL_SIZE // 2
                            y = (macro_row * LOCAL_SIZE + local_row) * CELL_SIZE + CELL_SIZE // 2
                            if val == self.human_marker:
                                self.draw_x(x, y, scale=0.5)
                            elif val == self.ai_marker:
                                self.draw_o(x, y, scale=0.5)

        # Overlay mini-board results if a board is won or drawn
        for macro_row in range(MACRO_SIZE):
            for macro_col in range(MACRO_SIZE):
                status = self.state.local_board_status[macro_row][macro_col]
                if status != 0:
                    x0 = macro_col * LOCAL_SIZE * CELL_SIZE
                    y0 = macro_row * LOCAL_SIZE * CELL_SIZE
                    x1 = x0 + LOCAL_SIZE * CELL_SIZE
                    y1 = y0 + LOCAL_SIZE * CELL_SIZE
                    if status == self.human_marker:
                        self.draw_big_x(x0, y0, x1, y1)
                    elif status == self.ai_marker:
                        self.draw_big_o(x0, y0, x1, y1)
                    else:
                        self.canvas.create_rectangle(x0, y0, x1, y1, fill="gray", stipple="gray50")

        # Highlight the active local board if applicable
        if self.state.prev_local_action is not None:
            pr, pc = self.state.prev_local_action
            if self.state.local_board_status[pr][pc] == 0:
                x0 = pc * LOCAL_SIZE * CELL_SIZE
                y0 = pr * LOCAL_SIZE * CELL_SIZE
                self.canvas.create_rectangle(x0, y0, x0 + LOCAL_SIZE * CELL_SIZE, y0 + LOCAL_SIZE * CELL_SIZE,
                                             outline="red", width=MACRO_LINE_WIDTH)

    def draw_x(self, cx, cy, scale=1.0):
        """Draw an X at the given center position."""
        offset = int(CELL_SIZE // 3 * scale)
        self.canvas.create_line(cx - offset, cy - offset, cx + offset, cy + offset,
                                width=LINE_WIDTH, fill="blue")
        self.canvas.create_line(cx - offset, cy + offset, cx + offset, cy - offset,
                                width=LINE_WIDTH, fill="blue")

    def draw_o(self, cx, cy, scale=1.0):
        """Draw an O at the given center position."""
        radius = int(CELL_SIZE // 3 * scale)
        self.canvas.create_oval(cx - radius, cy - radius, cx + radius, cy + radius,
                                width=LINE_WIDTH, outline="green")

    def draw_big_x(self, x0, y0, x1, y1):
        """Draw a large X across a local board."""
        margin = CELL_SIZE // 6
        self.canvas.create_line(x0 + margin, y0 + margin, x1 - margin, y1 - margin,
                                width=MACRO_LINE_WIDTH, fill="blue")
        self.canvas.create_line(x0 + margin, y1 - margin, x1 - margin, y0 + margin,
                                width=MACRO_LINE_WIDTH, fill="blue")

    def draw_big_o(self, x0, y0, x1, y1):
        """Draw a large O across a local board."""
        margin = CELL_SIZE // 6
        self.canvas.create_oval(x0 + margin, y0 + margin, x1 - margin, y1 - margin,
                                width=MACRO_LINE_WIDTH, outline="green")

    def on_click(self, event):
        """Handle human player’s click to make a move."""
        if self.state is None or self.state.fill_num != self.human_marker:
            return

        col = event.x // CELL_SIZE
        row = event.y // CELL_SIZE
        macro_row = row // LOCAL_SIZE
        macro_col = col // LOCAL_SIZE
        local_row = row % LOCAL_SIZE
        local_col = col % LOCAL_SIZE

        action = (macro_row, macro_col, local_row, local_col)
        if not self.state.is_valid_action(action):
            print("Invalid move. Please click on a valid empty cell in the active board.")
            return

        self.state = self.state.change_state(action)
        self.draw_board()

        if self.state.is_terminal():
            self.end_game()
        else:
            # Schedule AI move if it’s their turn
            self.root.after(500, self.ai_move)

    def ai_move(self):
        """Handle AI’s move."""
        if self.state is None or self.paused or self.state.fill_num != self.ai_marker:
            return

        print("AI is thinking...")
        start = time.time()
        action = self.ai_agent.choose_action(self.state)
        end = time.time()
        print(f"AI chose: {action} (in {end - start:.2f} seconds)")
        self.state = self.state.change_state(action)
        self.draw_board()
        if not self.state.is_terminal():
            # If AI gets another turn (e.g., due to a won board), schedule next move
            if self.state.fill_num == self.ai_marker:
                self.root.after(500, self.ai_move)
        else:
            self.end_game()

    def end_game(self):
        """Display the game result."""
        print("Game over!")
        terminal_value = self.state.terminal_utility()
        if terminal_value == 1.0:
            result_text = "Human (X) wins!"
        elif terminal_value == 0.0:
            result_text = "AI (O) wins!"
        else:
            result_text = "Draw!"
        self.canvas.create_text(WINDOW_SIZE // 2, WINDOW_SIZE // 2, text=result_text,
                                font=("Arial", 32), fill="red")

if __name__ == "__main__":
    root = tk.Tk()
    gui = UltimateTicTacToeGUI(root)
    root.mainloop()