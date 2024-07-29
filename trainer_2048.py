from neural_net import *
from deep_q import *
import tkinter as tk
import numpy as np

class Game:
    def __init__(self):
        self.reset()

    def show_game(self):
        print(self.score)
        print(self.board)
        print()

    def reset(self):
        self.board = np.zeros((4, 4))
        self.score = 0
        self.add_random_tile()
        self.add_random_tile()

    def add_random_tile(self):
        empty_tiles = np.argwhere(self.board == 0)
        if len(empty_tiles) > 0:
            i, j = empty_tiles[np.random.choice(len(empty_tiles))]
            self.board[i, j] = 2 if np.random.rand() < 0.9 else 4
            self.score += 2 if self.board[i, j] == 2 else 4

    ## Slide left does actual movement
    # Other slides manipulate/rotate board so that slide code doesnt have to be repeated
    def slide_left(self):
        moved = False
        for row in self.board:
            new_row = self.merge(row)
            if not np.array_equal(row, new_row):
                moved = True
            row[:] = new_row
        self.add_random_tile()
        return moved

    def slide_right(self):
        self.board = np.fliplr(self.board)
        moved = self.slide_left()
        self.board = np.fliplr(self.board)
        return moved

    def slide_up(self):
        self.board = self.board.T
        moved = self.slide_left()
        self.board = self.board.T
        return moved

    def slide_down(self):
        self.board = np.flipud(self.board).T
        moved = self.slide_left()
        self.board = self.board.T
        self.board = np.flipud(self.board)
        return moved
    
    def merge(self, line):
        non_zero = line[line != 0]
        new_line = np.zeros_like(line)
        index = 0
        i = 0

        while i < len(non_zero):
            current = non_zero[i]
            if i + 1 < len(non_zero) and non_zero[i + 1] == current:
                new_line[index] = current * 2
                self.score += current * 2  # Update score
                i += 1
            else:
                new_line[index] = current
            index += 1
            i += 1

        return new_line

    def is_game_over(self):
        if np.any(self.board == 0):
            return False
        for row in self.board:
            if self.can_merge(row):
                return False
        for col in self.board.T:
            if self.can_merge(col):
                return False
        return True

    def can_merge(self, line):
        return any(line[i] == line[i + 1] for i in range(len(line) - 1))
    
class GUI:
    def __init__(self, root):
        self.game = Game()
        self.root = root
        self.root.title("2048")
        
        # Create the main frame
        self.main_frame = tk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create the game canvas
        self.canvas = tk.Canvas(self.main_frame, width=400, height=400, bg='lightgray')
        self.canvas.pack(side=tk.LEFT, padx=10, pady=10)
        
        # Create the control panel frame
        self.control_panel = tk.Frame(self.main_frame)
        self.control_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)
        
        # Create a label to display the score
        self.score_label = tk.Label(self.control_panel, text=f"Score: {self.game.score}", font=('Arial', 24))
        self.score_label.pack(side=tk.TOP, pady=10)

        # Create buttons in the control panel
        self.train_button = tk.Button(self.control_panel, text="Train Agent", command=self.train_agent)
        self.train_button.pack(side=tk.TOP, pady=10)
        
        self.play_button = tk.Button(self.control_panel, text="Play with Agent", command=self.play_with_agent)
        self.play_button.pack(side=tk.TOP, pady=10)

         # Placeholder button at the top of the right frame
        self.placeholder_button = tk.Button(self.control_panel, text="Play with expectimax")
        self.placeholder_button.pack(side=tk.TOP, pady=5)

        # Button to reset the game
        self.reset_button = tk.Button(self.control_panel, text="Reset Game", command=self.reset)
        self.reset_button.pack(side=tk.BOTTOM, pady=5)

        # Button to quit the game
        self.quit_button = tk.Button(self.control_panel, text="Quit", command=self.root.quit)
        self.quit_button.pack(side=tk.BOTTOM, pady=5)

        # Color mapping for tiles
        self.tile_colours = {
            0: 'lightgray',
            2: '#eee4da',
            4: '#ede0c8',
            8: '#f2b179',
            16: '#f59563',
            32: '#f67c5f',
            64: '#f65e3b',
            128: '#edcf72',
            256: '#edcc61',
            512: '#edc850',
            1024: '#edc53f',
            2048: '#edc22e',
        }
        self.draw_board()
        self.root.bind("<Left>", self.move_left)
        self.root.bind("<Right>", self.move_right)
        self.root.bind("<Up>", self.move_up)
        self.root.bind("<Down>", self.move_down)
        self.agent = None

    def reset(self):
        self.game.reset()
        self.draw_board()

    def draw_board(self):
        self.canvas.delete("all")
        for i in range(4):
            for j in range(4):
                x = j * 100 + 10
                y = i * 100 + 10
                value = self.game.board[i, j]
                colour = self.tile_colours.get(value, 'black')  # Default to 'black' if the value is not in the mapping
                self.canvas.create_rectangle(x, y, x + 80, y + 80, fill=colour, outline='gray')
                if value != 0:
                    self.canvas.create_text(x + 40, y + 40, text=str(value), font=('Arial', 24))
        self.score_label.config(text=f"Score: {self.game.score}")

    def move_left(self, event):
        if self.game.slide_left():
            self.draw_board()
            if self.game.is_game_over():
                self.show_game_over()

    def move_right(self, event):
        if self.game.slide_right():
            self.draw_board()
            if self.game.is_game_over():
                self.show_game_over()

    def move_up(self, event):
        if self.game.slide_up():
            self.draw_board()
            if self.game.is_game_over():
                self.show_game_over()

    def move_down(self, event):
        if self.game.slide_down():
            self.draw_board()
            if self.game.is_game_over():
                self.show_game_over()

    def show_game_over(self):
        self.canvas.create_text(200, 200, text="Game Over", font=('Arial', 36), fill='red')

    def train_agent(self, episodes=1000, name=None):
        if name == None:
            input_neurons = 16
            num_actions = 4
            loss = Mean_Squared_Error_Loss
            self.agent = Q_Network(Game, input_neurons, loss, num_actions)
            self.agent.add_layer(16, 32, ReLU)
            self.agent.add_layer(32, 32, ReLU)
            self.agent.add_layer(32, 4, Linear)
            self.agent.train(episodes, gui_callback=self.update_gui_during_training)
            self.agent.save_model("2048_agent.pkl")
        else:
            self.load_agent(name)
            self.agent.train(episodes, gui_callback=self.update_gui_during_training)
            self.agent.save_model(name)
        print("Agent trained and model saved as 2048_agent.pkl")

    def update_gui_during_training(self):
        self.game = self.agent.game  # Update the game state in the GUI
        self.draw_board()
        self.root.update_idletasks()  # Update the GUI

    def load_agent(self, name=None):
        if name == None:
            self.agent = Q_Network(lambda: None, 16, Mean_Squared_Error_Loss, 4).load_model('2048_agent.pkl')
        else:
            self.agent = Q_Network(lambda: None, 16, Mean_Squared_Error_Loss, 4).load_model(name)
        print("Agent model loaded from 2048_agent.pkl")

    def agent_move(self):
        if self.agent is not None:
            state = self.game.board
            action = self.agent.choose_action(state)
            if action == 0:
                moved = self.game.slide_left()
            elif action == 1:
                moved = self.game.slide_right()
            elif action == 2:
                moved = self.game.slide_up()
            elif action == 3:
                moved = self.game.slide_down()
            self.draw_board()
            if self.game.is_game_over():
                self.show_game_over()
            else:
                self.root.after(500, self.agent_move)

    def play_with_agent(self):
        self.load_agent()
        self.root.after(50, self.agent_move)
