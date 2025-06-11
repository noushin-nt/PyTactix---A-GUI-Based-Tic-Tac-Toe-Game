import tkinter as tk
from tkinter import messagebox
import random
import sys

class TicTacToe:
    def __init__(self, root):
        self.root = root
        self.root.title("PyTactix - Tic Tac Toe")
        self.root.geometry("400x600")
        self.root.resizable(False, False)

        self.player1_symbol = tk.StringVar(value="X")
        self.current_symbol = self.player1_symbol.get()
        self.board = ["" for _ in range(9)]
        self.game_over = False
        self.is_two_player = True
        self.waiting_for_ai = False
        self.scores = {"X": 0, "O": 0}

        self.round_count = 0
        self.total_rounds = tk.IntVar(value=3)

        self.create_widgets()

    def create_widgets(self):
        theme_frame = tk.Frame(self.root)
        theme_frame.pack(pady=5)
        tk.Label(theme_frame, text="Theme:").pack(side=tk.LEFT)
        self.theme = tk.StringVar(value="Classic")
        tk.OptionMenu(theme_frame, self.theme, "Classic", "Ocean", "Forest", command=self.theme_changed).pack(side=tk.LEFT)

        option_frame = tk.Frame(self.root)
        option_frame.pack(pady=5)
        tk.Label(option_frame, text="Player 1: ").pack(side=tk.LEFT)
        tk.Radiobutton(option_frame, text="X", variable=self.player1_symbol, value="X", command=self.options_changed).pack(side=tk.LEFT)
        tk.Radiobutton(option_frame, text="O", variable=self.player1_symbol, value="O", command=self.options_changed).pack(side=tk.LEFT)

        mode_frame = tk.Frame(self.root)
        mode_frame.pack(pady=5)
        tk.Label(mode_frame, text="Mode:").pack(side=tk.LEFT)
        self.mode_var = tk.StringVar(value="2P")
        tk.Radiobutton(mode_frame, text="2P", variable=self.mode_var, value="2P", command=self.options_changed).pack(side=tk.LEFT)
        tk.Radiobutton(mode_frame, text="vs AI", variable=self.mode_var, value="AI", command=self.options_changed).pack(side=tk.LEFT)

        round_frame = tk.Frame(self.root)
        round_frame.pack(pady=5)
        tk.Label(round_frame, text="Rounds:").pack(side=tk.LEFT)
        tk.Radiobutton(round_frame, text="1", variable=self.total_rounds, value=1, command=self.options_changed).pack(side=tk.LEFT)
        tk.Radiobutton(round_frame, text="3", variable=self.total_rounds, value=3, command=self.options_changed).pack(side=tk.LEFT)
        tk.Radiobutton(round_frame, text="5", variable=self.total_rounds, value=5, command=self.options_changed).pack(side=tk.LEFT)
        tk.Radiobutton(round_frame, text="7", variable=self.total_rounds, value=7, command=self.options_changed).pack(side=tk.LEFT)

        self.canvas = tk.Canvas(self.root, width=300, height=300, bg="white")
        self.canvas.pack(pady=10)
        self.canvas.bind("<Button-1>", self.handle_click)

        self.status_label = tk.Label(self.root, text="Player X's Turn", font=("Arial", 14))
        self.status_label.pack()

        self.score_label = tk.Label(self.root, text="Score - X: 0 | O: 0", font=("Arial", 12))
        self.score_label.pack()

        control_frame = tk.Frame(self.root)
        control_frame.pack(pady=5)

        reset_round_btn = tk.Button(control_frame, text="Reset Round", command=self.reset_game, bg="#0275d8", fg="white", font=("Arial", 12, "bold"))
        reset_round_btn.pack(side=tk.LEFT, padx=5)

        reset_game_btn = tk.Button(control_frame, text="Reset Game", command=self.reset_score_and_game, bg="#d9534f", fg="white", font=("Arial", 12, "bold"))
        reset_game_btn.pack(side=tk.LEFT, padx=5)

        self.draw_board()

    def theme_changed(self, _):
        self.update_theme(self.theme.get())
        self.reset_game()

    def options_changed(self):
        self.toggle_mode()
        self.reset_score_and_game()

    def update_theme(self, theme):
        colors = {
            "Classic": "white",
            "Ocean": "lightblue",
            "Forest": "lightgreen"
        }
        self.canvas.configure(bg=colors.get(theme, "white"))

    def draw_board(self):
        self.canvas.delete("all")
        w = 100
        for i in range(1, 3):
            self.canvas.create_line(i * w, 0, i * w, 300, width=2)
            self.canvas.create_line(0, i * w, 300, i * w, width=2)

        for idx, symbol in enumerate(self.board):
            if symbol:
                x = (idx % 3) * 100 + 50
                y = (idx // 3) * 100 + 50
                self.canvas.create_text(x, y, text=symbol, font=("Arial", 48), tags=f"cell{idx}")

    def handle_click(self, event):
        if self.game_over or self.waiting_for_ai:
            return

        row, col = event.y // 100, event.x // 100
        idx = row * 3 + col

        if self.board[idx] == "":
            self.board[idx] = self.current_symbol
            self.draw_board()
            winner_indices = self.check_winner()
            if winner_indices:
                self.highlight_winner(winner_indices)
                winner_text = "Player" if self.is_two_player or self.current_symbol == self.player1_symbol.get() else "Device Player"
                self.status_label.config(text=f"{winner_text} {self.current_symbol} wins this round!")
                self.scores[self.current_symbol] += 1
                self.update_score()
                self.round_count += 1
                self.game_over = True
                self.check_round_end()
                return
            elif "" not in self.board:
                self.status_label.config(text="It's a draw!")
                self.round_count += 1
                self.game_over = True
                self.check_round_end()
                return

            self.current_symbol = "O" if self.current_symbol == "X" else "X"
            self.status_label.config(text=f"Player {self.current_symbol}'s Turn")

            if self.mode_var.get() == "AI" and self.current_symbol != self.player1_symbol.get():
                self.waiting_for_ai = True
                self.root.after(500, self.ai_move)

    def ai_move(self):
        available = [i for i in range(9) if self.board[i] == ""]
        if not available:
            return
        idx = self.best_ai_move()
        self.board[idx] = self.current_symbol
        self.draw_board()

        winner_indices = self.check_winner()
        if winner_indices:
            self.highlight_winner(winner_indices)
            self.status_label.config(text="Device Player wins this round!")
            self.scores[self.current_symbol] += 1
            self.update_score()
            self.round_count += 1
            self.game_over = True
            self.check_round_end()
        elif "" not in self.board:
            self.status_label.config(text="It's a draw!")
            self.round_count += 1
            self.game_over = True
            self.check_round_end()
        else:
            self.current_symbol = "O" if self.current_symbol == "X" else "X"
            self.status_label.config(text=f"Player {self.current_symbol}'s Turn")

        self.waiting_for_ai = False

    def best_ai_move(self):
        for idx in range(9):
            if self.board[idx] == "":
                self.board[idx] = self.current_symbol
                if self.check_winner():
                    self.board[idx] = ""
                    return idx
                self.board[idx] = ""
        opponent = "O" if self.current_symbol == "X" else "X"
        for idx in range(9):
            if self.board[idx] == "":
                self.board[idx] = opponent
                if self.check_winner():
                    self.board[idx] = ""
                    return idx
                self.board[idx] = ""
        return random.choice([i for i in range(9) if self.board[i] == ""])

    def check_winner(self):
        wins = [
            (0, 1, 2), (3, 4, 5), (6, 7, 8),
            (0, 3, 6), (1, 4, 7), (2, 5, 8),
            (0, 4, 8), (2, 4, 6)
        ]
        for i, j, k in wins:
            if self.board[i] == self.board[j] == self.board[k] != "":
                return (i, j, k)
        return None

    def highlight_winner(self, indices):
        for idx in indices:
            row, col = divmod(idx, 3)
            x = col * 100 + 50
            y = row * 100 + 50
            self.canvas.itemconfig(f"cell{idx}", fill="red")

    def reset_game(self):
        self.board = ["" for _ in range(9)]
        self.current_symbol = self.player1_symbol.get()
        self.game_over = False
        self.waiting_for_ai = False
        self.status_label.config(text=f"Player {self.current_symbol}'s Turn")
        self.draw_board()

    def reset_score_and_game(self):
        self.scores = {"X": 0, "O": 0}
        self.round_count = 0
        self.update_score()
        self.reset_game()

    def toggle_mode(self):
        self.is_two_player = self.mode_var.get() == "2P"

    def update_score(self):
        self.score_label.config(text=f"Score - X: {self.scores['X']} | O: {self.scores['O']}")

    def check_round_end(self):
        if self.round_count >= self.total_rounds.get():
            winner = "Draw"
            if self.scores["X"] > self.scores["O"]:
                winner = "Player X"
            elif self.scores["O"] > self.scores["X"]:
                winner = "Player O"
            play_again = messagebox.askyesno("Game Over", f"Game over! Winner: {winner}\nDo you want to play again?")
            if play_again:
                self.reset_score_and_game()
            else:
                self.reset_score_and_game()
                self.root.destroy()
                sys.exit()
        else:
            self.root.after(2000, self.reset_game)

if __name__ == "__main__":
    root = tk.Tk()
    game = TicTacToe(root)
    root.mainloop()
