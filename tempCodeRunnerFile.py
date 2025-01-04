import random
import tkinter as tk
from tkinter import messagebox
import itertools

class GeneralGameGUI:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("General Game")
        self.window.geometry("640x780")
        self.dice = [0] * 5
        self.selected_dice = [False] * 5
        self.player_scores = {"Player": 0, "Computer": 0}
        self.round = 1
        self.max_rounds = 10
        self.current_player = "Player"
        self.roll_count = 0
        self.max_rolls = 3

        self.combinations = {
            "General": 60,
            "Four of a Kind": 40,
            "Full House": 35,
            "Straight": 25,
            "1s": 0,
            "2s": 0,
            "3s": 0,
            "4s": 0,
            "5s": 0,
            "6s": 0,
            "Other": 0
        }
        self.used_combinations = {"Player": set(), "Computer": set()}
        self.available_combinations = []

        self.setup_ui()

    def setup_ui(self):
        self.dice_frames = []
        self.dice_labels = []
        self.select_buttons = []

        for i in range(5):
            frame = tk.Frame(self.window, relief=tk.RAISED, borderwidth=2)
            frame.grid(row=0, column=i, padx=10, pady=10)
            self.dice_frames.append(frame)

            label = tk.Label(frame, text="0", font=("Arial", 28), width=3, height=2, bg="white")
            label.pack()
            self.dice_labels.append(label)

            button = tk.Checkbutton(self.window, text=f"Select {i+1}", command=lambda i=i: self.toggle_select(i))
            button.grid(row=1, column=i)
            self.select_buttons.append(button)

        self.roll_button = tk.Button(self.window, text="Roll Dice", command=self.roll_dice, font=("Arial", 14))
        self.roll_button.grid(row=2, column=0, columnspan=3, pady=10)

        self.reroll_button = tk.Button(self.window, text="Reroll Selected", command=self.reroll_selected, state=tk.DISABLED, font=("Arial", 14))
        self.reroll_button.grid(row=2, column=2, columnspan=3, pady=10)

        self.status_label = tk.Label(self.window, text="Player's Turn", font=("Arial", 18))
        self.status_label.grid(row=3, column=0, columnspan=5)

        self.score_label = tk.Label(self.window, text="Scores: Player 0 - 0 Computer", font=("Arial", 16))
        self.score_label.grid(row=4, column=0, columnspan=5, pady=10)

        self.combination_frame = tk.Frame(self.window, relief=tk.RAISED, borderwidth=2)
        self.combination_frame.grid(row=0, column=5, rowspan=5, padx=20, pady=10, sticky="n")

        tk.Label(self.combination_frame, text="Combinations", font=("Arial", 16)).pack(pady=5)
        self.combination_buttons = {}

        for combo in self.combinations.keys():
            btn = tk.Button(self.combination_frame, text=combo, font=("Arial", 12), state=tk.DISABLED, 
                            command=lambda c=combo: self.choose_combination(c))
            btn.pack(pady=5, fill=tk.X)
            self.combination_buttons[combo] = btn

        self.log_label = tk.Label(self.window, text="Game Log", font=("Arial", 16))
        self.log_label.grid(row=5, column=0, columnspan=5, pady=5)

        self.log_text = tk.Text(self.window, height=10, width=70, state=tk.DISABLED, font=("Arial", 12))
        self.log_text.grid(row=6, column=0, columnspan=6, pady=10)

    def toggle_select(self, index):
        self.selected_dice[index] = not self.selected_dice[index]
        self.dice_frames[index].config(bg="yellow" if self.selected_dice[index] else "white")

    def roll_dice(self):
        if self.roll_count < self.max_rolls:
            for i in range(5):
                self.dice[i] = random.randint(1, 6)
            self.update_dice_labels()
            self.highlight_combinations()
            self.reroll_button.config(state=tk.NORMAL)
            self.roll_count += 1
            if self.roll_count == self.max_rolls:
                self.roll_button.config(state=tk.DISABLED)
            self.add_to_log(f"{self.current_player} rolled: {self.dice}")

    def reroll_selected(self):
        if self.roll_count < self.max_rolls:
            rerolled_dice = []
            for i in range(5):
                if self.selected_dice[i]:
                    self.dice[i] = random.randint(1, 6)
                    rerolled_dice.append(i+1)
            self.update_dice_labels()
            self.highlight_combinations()
            self.roll_count += 1
            if self.roll_count == self.max_rolls:
                self.reroll_button.config(state=tk.DISABLED)
                self.roll_button.config(state=tk.DISABLED)

            self.add_to_log(f"{self.current_player} rerolled dice: {rerolled_dice}")

    def update_dice_labels(self):
        for i, value in enumerate(self.dice):
            self.dice_labels[i].config(text=str(value))

    def highlight_combinations(self):
        counts = {i: self.dice.count(i) for i in range(1, 7)}
        self.available_combinations = []

        if len(set(self.dice)) == 1 and "General" not in self.used_combinations[self.current_player]:
            self.available_combinations.append("General")
        if 4 in counts.values() and "Four of a Kind" not in self.used_combinations[self.current_player]:
            self.available_combinations.append("Four of a Kind")
        if 3 in counts.values() and 2 in counts.values() and "Full House" not in self.used_combinations[self.current_player]:
            self.available_combinations.append("Full House")
        if sorted(self.dice) in [[1, 2, 3, 4, 5], [2, 3, 4, 5, 6]] and "Straight" not in self.used_combinations[self.current_player]:
            self.available_combinations.append("Straight")
        for i in range(1, 7):
            if f"{i}s" not in self.used_combinations[self.current_player]:
                self.available_combinations.append(f"{i}s")

        self.available_combinations.append("Other")
            
        for combo, btn in self.combination_buttons.items():
            if combo in self.available_combinations:
                btn.config(state=tk.NORMAL)
            else:
                btn.config(state=tk.DISABLED)

    def choose_combination(self, combination):
        if combination in self.used_combinations[self.current_player] and combination != "Other":
            return

        if combination != "Other":
            self.used_combinations[self.current_player].add(combination)

        score = self.calculate_score(combination)
        self.player_scores[self.current_player] += score
        self.update_scores()

        self.add_to_log(f"{self.current_player} chose {combination} and scored {score} points.")

        self.end_turn()

    def add_to_log(self, message):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.config(state=tk.DISABLED)
        self.log_text.yview(tk.END)

    def calculate_score(self, combination):
        if combination in ["1s", "2s", "3s", "4s", "5s", "6s"]:
            number = int(combination[0])
            return self.dice.count(number) * number
        return self.combinations.get(combination, 0)

    def update_scores(self):
        self.score_label.config(text=f"Scores: Player {self.player_scores['Player']} - {self.player_scores['Computer']} Computer")

    def end_turn(self):
        if self.current_player == "Player":
            self.current_player = "Computer"
            self.computer_turn()
        else:
            self.round += 1
            if self.round > self.max_rounds:
                self.end_game()
            else:
                self.current_player = "Player"
                self.status_label.config(text="Player's Turn")
                self.reset_turn()

    def reset_turn(self):
        self.roll_count = 0
        self.roll_button.config(state=tk.NORMAL)
        self.reroll_button.config(state=tk.DISABLED)

        for i in range(5):
            self.dice_frames[i].config(bg="white")
            self.selected_dice[i] = False
            self.select_buttons[i].deselect()

        for btn in self.combination_buttons.values():
            btn.config(state=tk.DISABLED)

    def computer_turn(self):
        self.status_label.config(text="Computer's Turn")
        self.window.update()
        
        self.roll_count = 0  # Обнулення лічильника перед першим ролом комп'ютера
        self.roll_dice()

        while self.roll_count < self.max_rolls:
            should_reroll, selected_dice = self.minimax_decision()

            self.add_to_log(f"Computer is deciding whether to reroll: {selected_dice}")

            if should_reroll:
                self.dice = [random.randint(1, 6) if selected else self.dice[i]
                            for i, selected in enumerate(selected_dice)]
                self.roll_count += 1
                self.update_dice_labels()
                self.highlight_combinations()
                self.add_to_log(f"Computer rerolled dice: {self.dice}")
            else:
                break

        best_combination, _ = self.minimax()
        if best_combination:
            self.choose_combination(best_combination)

    def minimax_decision(self):
        best_expected_value = -float('inf')
        best_reroll = [False] * 5

        for reroll_pattern in itertools.product([True, False], repeat=5):
            expected_value = self.simulate_reroll(reroll_pattern)
            if expected_value > best_expected_value:
                best_expected_value = expected_value
                best_reroll = reroll_pattern

        current_best_combination, current_best_score = self.minimax()
        if current_best_score >= best_expected_value:
            return False, [False] * 5

        return True, best_reroll

    def simulate_reroll(self, reroll_pattern):
        expected_score = 0
        total_possibilities = 0

        for reroll_values in itertools.product(range(1, 7), repeat=reroll_pattern.count(True)):
            simulated_dice = self.dice[:]
            index = 0
            for i, reroll in enumerate(reroll_pattern):
                if reroll:
                    simulated_dice[i] = reroll_values[index]
                    index += 1

            simulated_best_combination, simulated_best_score = self.minimax(simulated_dice)
            expected_score += simulated_best_score * (1 / 6 ** reroll_pattern.count(True))

        return expected_score

    def minimax(self, dice=None):
        if dice is None:
            dice = self.dice

        max_score = -float('inf')
        best_combination = None

        for combo in self.available_combinations:
            if combo in self.used_combinations[self.current_player]:
                continue
            temp_score = self.calculate_score(combo, dice)
            if temp_score > max_score:
                max_score = temp_score
                best_combination = combo

        return best_combination, max_score

    def calculate_score(self, combination, dice=None):
        if dice is None:
            dice = self.dice

        if combination in ["1s", "2s", "3s", "4s", "5s", "6s"]:
            number = int(combination[0])
            return dice.count(number) * number
        elif combination == "General" and len(set(dice)) == 1:
            return 60
        elif combination == "Four of a Kind" and max(dice.count(x) for x in set(dice)) >= 4:
            return 40
        elif combination == "Full House" and sorted(dice.count(x) for x in set(dice)) == [2, 3]:
            return 35
        elif combination == "Straight" and sorted(dice) in [[1, 2, 3, 4, 5], [2, 3, 4, 5, 6]]:
            return 25
        return 0

    def end_game(self):
        player_score = self.player_scores["Player"]
        computer_score = self.player_scores["Computer"]
        winner = "Player" if player_score > computer_score else "Computer" if computer_score > player_score else "Draw"
        messagebox.showinfo("Game Over", f"Final Scores:\nPlayer: {player_score}\nComputer: {computer_score}\nWinner: {winner}")
        self.window.quit()

    def start(self):
        self.window.mainloop()

if __name__ == "__main__":
    game = GeneralGameGUI()
    game.start()
