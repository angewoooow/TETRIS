
import tkinter as tk
import random


# ============================================================
# BLOCKMASTER
# PHASE 14
#
# Features:
# - 8 x 16 board
# - Start/Home screen
# - Player name selection
# - 3, 2, 1 countdown
# - Arcade-style pastel UI
# - 3D-looking blocks
# - Score
# - High score
# - Level
# - Next shape preview
# - Progressive speed
# - 6+ filled cells can trigger clearing
# - Combo blast
# - Pause / Resume
# - Reset
# - Home
# - Quit
#
# CONTROLS:
# LEFT      = Move left
# RIGHT     = Move right
# UP        = Rotate
# DOWN      = Rotate
# SPACE     = Hard drop / Lock
# ============================================================


# ============================================================
# BOARD SETTINGS
# ============================================================

ROWS = 16
COLS = 8

CELL_SIZE = 40

BOARD_WIDTH = COLS * CELL_SIZE
BOARD_HEIGHT = ROWS * CELL_SIZE


# ============================================================
# SPEED SETTINGS
# ============================================================

# You said 1000 works well, so we start here.
START_FALL_SPEED = 1000

# Speed becomes faster by this amount each level.
SPEED_STEP = 50

# The lowest possible delay.
MIN_FALL_SPEED = 150


# ============================================================
# LEVEL SETTINGS
# ============================================================

LEVEL_SCORE = 75


# ============================================================
# COLORS
# ============================================================

BACKGROUND = "#F4F1EA"
PANEL = "#E8E1D5"
PANEL_LIGHT = "#F8F5EF"

TEXT = "#4E4A45"

BOARD_BG = "#DDD8CF"
GRID_COLOR = "#C8C2B8"

BUTTON_BG = "#D7C7E8"
BUTTON_ACTIVE = "#C7B2DE"

HOME_BG = "#EFE8DF"

# Pastel block colors
BLOCK_COLORS = [
    "#A8DADC",   # pastel cyan
    "#F6BDCC",   # pastel pink
    "#CDB4DB",   # pastel purple
    "#BDE0FE",   # pastel blue
    "#CDE8B5",   # pastel green
    "#F8D6A0",   # pastel orange
    "#D8C3A5"    # pastel brown
]


class BlockMaster:

    def __init__(self, root):

        self.root = root

        self.root.title("BlockMaster")

        self.root.geometry("1000x850")

        self.root.resizable(False, False)

        self.root.configure(
            bg=BACKGROUND
        )

        # ====================================================
        # GAME VARIABLES
        # ====================================================

        self.player_name = ""

        self.score = 0

        self.high_score = 0

        self.level = 1

        self.lines = 0

        self.combo = 0

        self.fall_speed = START_FALL_SPEED

        self.game_over = False

        self.paused = False

        self.countdown_active = False

        self.countdown_value = 0

        # ====================================================
        # SHAPES
        # ====================================================

        self.shapes = [

            # I
            [
                [1, 1, 1, 1]
            ],

            # O
            [
                [1, 1],
                [1, 1]
            ],

            # T
            [
                [1, 1, 1],
                [0, 1, 0]
            ],

            # L
            [
                [1, 0],
                [1, 0],
                [1, 1]
            ],

            # J
            [
                [0, 1],
                [0, 1],
                [1, 1]
            ],

            # S
            [
                [0, 1, 1],
                [1, 1, 0]
            ],

            # Z
            [
                [1, 1, 0],
                [0, 1, 1]
            ]
        ]

        # ====================================================
        # BLOCK COLORS
        # ====================================================

        self.current_color = random.choice(
            BLOCK_COLORS
        )

        self.next_color = random.choice(
            BLOCK_COLORS
        )

        # ====================================================
        # CURRENT / NEXT BLOCK
        # ====================================================

        self.current_block = None

        self.next_block = random.choice(
            self.shapes
        )

        # ====================================================
        # BOARD
        # ====================================================

        self.board = []

        self.board_colors = []

        # ====================================================
        # CREATE HOME SCREEN
        # ====================================================

        self.create_home_screen()

    # ========================================================
    # HOME SCREEN
    # ========================================================

    def create_home_screen(self):

        self.clear_root()

        self.home_frame = tk.Frame(
            self.root,
            bg=HOME_BG,
            padx=50,
            pady=40
        )

        self.home_frame.pack(
            expand=True
        )

        # ----------------------------------------------------
        # TITLE
        # ----------------------------------------------------

        title_box = tk.Frame(
            self.home_frame,
            bg=PANEL,
            padx=50,
            pady=25
        )

        title_box.pack(
            pady=20
        )

        title = tk.Label(
            title_box,
            text="BLOCKMASTER",
            font=("Arial", 30, "bold"),
            bg=PANEL,
            fg=TEXT
        )

        title.pack()

        subtitle = tk.Label(
            title_box,
            text="ARCADE BLOCK PUZZLE",
            font=("Arial", 11, "bold"),
            bg=PANEL,
            fg=TEXT
        )

        subtitle.pack(
            pady=(5, 0)
        )

        # ----------------------------------------------------
        # NAME BOX
        # ----------------------------------------------------

        name_box = tk.Frame(
            self.home_frame,
            bg=PANEL,
            padx=30,
            pady=25
        )

        name_box.pack(
            pady=15
        )

        name_label = tk.Label(
            name_box,
            text="PLAYER NAME",
            font=("Arial", 12, "bold"),
            bg=PANEL,
            fg=TEXT
        )

        name_label.pack(
            pady=(0, 10)
        )

        self.name_entry = tk.Entry(
            name_box,
            width=25,
            font=("Arial", 13),
            justify="center"
        )

        self.name_entry.insert(
            0,
            "PLAYER"
        )

        self.name_entry.pack()

        # ----------------------------------------------------
        # START BUTTON
        # ----------------------------------------------------

        start_button = tk.Button(
            self.home_frame,
            text="START GAME",
            font=("Arial", 13, "bold"),
            width=18,
            height=2,
            bg=BUTTON_BG,
            activebackground=BUTTON_ACTIVE,
            fg=TEXT,
            relief="flat",
            command=self.start_game
        )

        start_button.pack(
            pady=15
        )

        # ----------------------------------------------------
        # QUIT BUTTON
        # ----------------------------------------------------

        quit_button = tk.Button(
            self.home_frame,
            text="QUIT",
            font=("Arial", 11, "bold"),
            width=18,
            bg=PANEL,
            activebackground=BUTTON_ACTIVE,
            fg=TEXT,
            relief="flat",
            command=self.root.destroy
        )

        quit_button.pack(
            pady=5
        )

        # ----------------------------------------------------
        # INSTRUCTIONS
        # ----------------------------------------------------

        instruction_box = tk.Frame(
            self.home_frame,
            bg=PANEL_LIGHT,
            padx=25,
            pady=15
        )

        instruction_box.pack(
            pady=20
        )

        instruction = tk.Label(
            instruction_box,
            text=(
                "← →  MOVE\n"
                "↑ ↓  ROTATE\n"
                "SPACE  DROP"
            ),
            font=("Arial", 10),
            bg=PANEL_LIGHT,
            fg=TEXT,
            justify="center"
        )

        instruction.pack()

        self.name_entry.focus()

        self.root.bind(
            "<Return>",
            lambda event: self.start_game()
        )

    # ========================================================
    # CLEAR ROOT
    # ========================================================

    def clear_root(self):

        for widget in self.root.winfo_children():

            widget.destroy()

    # ========================================================
    # START GAME
    # ========================================================

    def start_game(self):

        name = self.name_entry.get().strip()

        if name == "":

            name = "PLAYER"

        self.player_name = name

        self.score = 0

        self.lines = 0

        self.level = 1

        self.combo = 0

        self.fall_speed = START_FALL_SPEED

        self.game_over = False

        self.paused = False

        self.board = [
            [0 for _ in range(COLS)]
            for _ in range(ROWS)
        ]

        self.board_colors = [
            [None for _ in range(COLS)]
            for _ in range(ROWS)
        ]

        self.current_block = None

        self.next_block = random.choice(
            self.shapes
        )

        self.current_color = random.choice(
            BLOCK_COLORS
        )

        self.next_color = random.choice(
            BLOCK_COLORS
        )

        self.create_game_screen()

        self.spawn_block()

        self.draw()

        self.start_countdown()

    # ========================================================
    # GAME SCREEN
    # ========================================================

    def create_game_screen(self):

        self.clear_root()

        self.game_container = tk.Frame(
            self.root,
            bg=BACKGROUND,
            padx=25,
            pady=20
        )

        self.game_container.pack(
            expand=True
        )

        # ====================================================
        # TOP PLAYER DISPLAY
        # ====================================================

        self.player_box = tk.Frame(
            self.game_container,
            bg=PANEL,
            padx=25,
            pady=10
        )

        self.player_box.pack(
            pady=(0, 15)
        )

        self.player_label = tk.Label(
            self.player_box,
            text=f"PLAYER: {self.player_name}",
            font=("Arial", 17, "bold"),
            bg=PANEL,
            fg=TEXT
        )

        self.player_label.pack()

        # ====================================================
        # MAIN GAME AREA
        # ====================================================

        self.main_game_area = tk.Frame(
            self.game_container,
            bg=BACKGROUND
        )

        self.main_game_area.pack()

        # ====================================================
        # BOARD BOX
        # ====================================================

        self.board_box = tk.Frame(
            self.main_game_area,
            bg=PANEL,
            padx=15,
            pady=15
        )

        self.board_box.pack(
            side="left",
            padx=15
        )

        # ====================================================
        # CANVAS
        # ====================================================

        self.canvas = tk.Canvas(
            self.board_box,
            width=BOARD_WIDTH,
            height=BOARD_HEIGHT,
            bg=BOARD_BG,
            highlightthickness=2,
            highlightbackground=GRID_COLOR
        )

        self.canvas.pack()

        # ====================================================
        # SIDE PANEL
        # ====================================================

        self.side_panel = tk.Frame(
            self.main_game_area,
            bg=BACKGROUND,
            width=230
        )

        self.side_panel.pack(
            side="left",
            padx=15,
            anchor="n"
        )

        # ====================================================
        # SCORE BOX
        # ====================================================

        self.score_box = self.create_stat_box(
            self.side_panel,
            "SCORE",
            "0"
        )

        self.score_box.pack(
            pady=7
        )

        self.score_value = self.score_box.value_label

        # ====================================================
        # HIGH SCORE BOX
        # ====================================================

        self.high_score_box = self.create_stat_box(
            self.side_panel,
            "HIGH SCORE",
            "0"
        )

        self.high_score_box.pack(
            pady=7
        )

        self.high_score_value = (
            self.high_score_box.value_label
        )

        # ====================================================
        # LEVEL BOX
        # ====================================================

        self.level_box = self.create_stat_box(
            self.side_panel,
            "LEVEL",
            "1"
        )

        self.level_box.pack(
            pady=7
        )

        self.level_value = (
            self.level_box.value_label
        )

        # ====================================================
        # NEXT BOX
        # ====================================================

        self.next_box = tk.Frame(
            self.side_panel,
            bg=PANEL,
            padx=15,
            pady=15
        )

        self.next_box.pack(
            pady=15
        )

        next_title = tk.Label(
            self.next_box,
            text="NEXT",
            font=("Arial", 12, "bold"),
            bg=PANEL,
            fg=TEXT
        )

        next_title.pack(
            pady=(0, 8)
        )

        self.next_canvas = tk.Canvas(
            self.next_box,
            width=150,
            height=120,
            bg=PANEL_LIGHT,
            highlightthickness=1,
            highlightbackground=GRID_COLOR
        )

        self.next_canvas.pack()

        # ====================================================
        # MENU BUTTON
        # ====================================================

        self.menu_button = tk.Button(
            self.side_panel,
            text="MENU",
            font=("Arial", 11, "bold"),
            width=16,
            height=2,
            bg=BUTTON_BG,
            activebackground=BUTTON_ACTIVE,
            fg=TEXT,
            relief="flat",
            command=self.open_menu
        )

        self.menu_button.pack(
            pady=15
        )

        # ====================================================
        # KEYBOARD
        # ====================================================

        self.root.bind(
            "<Left>",
            self.move_left
        )

        self.root.bind(
            "<Right>",
            self.move_right
        )

        self.root.bind(
            "<Up>",
            self.rotate_block
        )

        self.root.bind(
            "<Down>",
            self.rotate_block
        )

        self.root.bind(
            "<space>",
            self.hard_drop
        )

    # ========================================================
    # STAT BOX
    # ========================================================

    def create_stat_box(
        self,
        parent,
        title,
        value
    ):

        box = tk.Frame(
            parent,
            bg=PANEL,
            width=210,
            padx=20,
            pady=12
        )

        title_label = tk.Label(
            box,
            text=title,
            font=("Arial", 10, "bold"),
            bg=PANEL,
            fg=TEXT
        )

        title_label.pack()

        value_label = tk.Label(
            box,
            text=value,
            font=("Arial", 18, "bold"),
            bg=PANEL,
            fg=TEXT
        )

        value_label.pack(
            pady=(3, 0)
        )

        box.value_label = value_label

        return box

    # ========================================================
    # COUNTDOWN
    # ========================================================

    def start_countdown(self):

        self.countdown_active = True

        self.countdown_value = 3

        self.show_countdown()

    # ========================================================
    # SHOW COUNTDOWN
    # ========================================================

    def show_countdown(self):

        if not self.countdown_active:

            return

        self.draw()

        center_x = BOARD_WIDTH / 2

        center_y = BOARD_HEIGHT / 2

        # Background box
        self.canvas.create_rectangle(
            center_x - 100,
            center_y - 80,
            center_x + 100,
            center_y + 80,
            fill=PANEL,
            outline=GRID_COLOR,
            width=2
        )

        if self.countdown_value > 0:

            self.canvas.create_text(
                center_x,
                center_y,
                text=str(
                    self.countdown_value
                ),
                font=("Arial", 60, "bold"),
                fill=TEXT
            )

            self.countdown_value -= 1

            self.root.after(
                700,
                self.show_countdown
            )

        else:

            self.canvas.create_text(
                center_x,
                center_y,
                text="GO!",
                font=("Arial", 42, "bold"),
                fill=TEXT
            )

            self.root.after(
                500,
                self.finish_countdown
            )

    # ========================================================
    # FINISH COUNTDOWN
    # ========================================================

    def finish_countdown(self):

        self.countdown_active = False

        self.draw()

        self.fall()

    # ========================================================
    # SPAWN BLOCK
    # ========================================================

    def spawn_block(self):

        if self.current_block is None:

            self.current_block = random.choice(
                self.shapes
            )

            self.current_color = random.choice(
                BLOCK_COLORS
            )

        else:

            self.current_block = self.next_block

            self.current_color = self.next_color

        self.next_block = random.choice(
            self.shapes
        )

        self.next_color = random.choice(
            BLOCK_COLORS
        )

        self.block_row = 0

        block_width = len(
            self.current_block[0]
        )

        self.block_col = (
            COLS - block_width
        ) // 2

        if not self.can_place(
            self.current_block,
            self.block_row,
            self.block_col
        ):

            self.game_over = True

    # ========================================================
    # DRAW BOARD
    # ========================================================

    def draw(self):

        self.canvas.delete("all")

        # ----------------------------------------------------
        # GRID
        # ----------------------------------------------------

        for row in range(ROWS):

            for col in range(COLS):

                x1 = col * CELL_SIZE
                y1 = row * CELL_SIZE

                x2 = x1 + CELL_SIZE
                y2 = y1 + CELL_SIZE

                self.canvas.create_rectangle(
                    x1,
                    y1,
                    x2,
                    y2,
                    fill=BOARD_BG,
                    outline=GRID_COLOR
                )

        # ----------------------------------------------------
        # LOCKED BLOCKS
        # ----------------------------------------------------

        for row in range(ROWS):

            for col in range(COLS):

                if self.board[row][col] == 1:

                    color = self.board_colors[
                        row
                    ][
                        col
                    ]

                    self.draw_3d_block(
                        col * CELL_SIZE,
                        row * CELL_SIZE,
                        color
                    )

        # ----------------------------------------------------
        # CURRENT BLOCK
        # ----------------------------------------------------

        if (
            self.current_block is not None
            and not self.game_over
            and not self.paused
            and not self.countdown_active
        ):

            for r in range(
                len(self.current_block)
            ):

                for c in range(
                    len(self.current_block[r])
                ):

                    if self.current_block[r][c] == 1:

                        x = (
                            self.block_col + c
                        ) * CELL_SIZE

                        y = (
                            self.block_row + r
                        ) * CELL_SIZE

                        self.draw_3d_block(
                            x,
                            y,
                            self.current_color
                        )

        # ----------------------------------------------------
        # NEXT
        # ----------------------------------------------------

        if hasattr(
            self,
            "next_canvas"
        ):

            self.draw_next_shape()

        # ----------------------------------------------------
        # GAME OVER
        # ----------------------------------------------------

        if self.game_over:

            center_x = BOARD_WIDTH / 2
            center_y = BOARD_HEIGHT / 2

            self.canvas.create_rectangle(
                center_x - 130,
                center_y - 90,
                center_x + 130,
                center_y + 90,
                fill=PANEL,
                outline=GRID_COLOR,
                width=2
            )

            self.canvas.create_text(
                center_x,
                center_y - 30,
                text="GAME OVER",
                font=("Arial", 25, "bold"),
                fill=TEXT
            )

            self.canvas.create_text(
                center_x,
                center_y + 20,
                text="Press R to Restart",
                font=("Arial", 11),
                fill=TEXT
            )

        # ----------------------------------------------------
        # PAUSED
        # ----------------------------------------------------

        if self.paused:

            center_x = BOARD_WIDTH / 2
            center_y = BOARD_HEIGHT / 2

            self.canvas.create_rectangle(
                center_x - 110,
                center_y - 65,
                center_x + 110,
                center_y + 65,
                fill=PANEL,
                outline=GRID_COLOR,
                width=2
            )

            self.canvas.create_text(
                center_x,
                center_y,
                text="PAUSED",
                font=("Arial", 25, "bold"),
                fill=TEXT
            )

        # ----------------------------------------------------
        # UPDATE SIDE PANEL
        # ----------------------------------------------------

        if hasattr(
            self,
            "score_value"
        ):

            self.score_value.config(
                text=str(self.score)
            )

            self.high_score_value.config(
                text=str(self.high_score)
            )

            self.level_value.config(
                text=str(self.level)
            )

    # ========================================================
    # 3D BLOCK
    # ========================================================

    def draw_3d_block(
        self,
        x,
        y,
        color
    ):

        # Main body
        self.canvas.create_rectangle(
            x + 2,
            y + 2,
            x + CELL_SIZE - 2,
            y + CELL_SIZE - 2,
            fill=color,
            outline=TEXT
        )

        # Top highlight
        self.canvas.create_polygon(
            x + 3,
            y + 3,
            x + CELL_SIZE - 3,
            y + 3,
            x + CELL_SIZE - 7,
            y + 7,
            x + 7,
            y + 7,
            fill="#FFFFFF",
            outline=""
        )

        # Left highlight
        self.canvas.create_polygon(
            x + 3,
            y + 3,
            x + 7,
            y + 7,
            x + 7,
            y + CELL_SIZE - 7,
            x + 3,
            y + CELL_SIZE - 3,
            fill="#FFFFFF",
            outline=""
        )

        # Bottom shadow
        self.canvas.create_polygon(
            x + 3,
            y + CELL_SIZE - 3,
            x + CELL_SIZE - 3,
            y + CELL_SIZE - 3,
            x + CELL_SIZE - 7,
            y + CELL_SIZE - 7,
            x + 7,
            y + CELL_SIZE - 7,
            fill="#B8B1A8",
            outline=""
        )

    # ========================================================
    # NEXT SHAPE
    # ========================================================

    def draw_next_shape(self):

        self.next_canvas.delete("all")

        block = self.next_block

        cell = 25

        rows = len(block)
        cols = len(block[0])

        width = cols * cell
        height = rows * cell

        start_x = (
            150 - width
        ) / 2

        start_y = (
            120 - height
        ) / 2

        for r in range(rows):

            for c in range(cols):

                if block[r][c] == 1:

                    x = (
                        start_x
                        + c * cell
                    )

                    y = (
                        start_y
                        + r * cell
                    )

                    # Simple 3D preview
                    self.next_canvas.create_rectangle(
                        x + 2,
                        y + 2,
                        x + cell - 2,
                        y + cell - 2,
                        fill=self.next_color,
                        outline=TEXT
                    )

                    self.next_canvas.create_line(
                        x + 4,
                        y + 4,
                        x + cell - 5,
                        y + 4,
                        fill="white",
                        width=2
                    )

    # ========================================================
    # CAN PLACE
    # ========================================================

    def can_place(
        self,
        block,
        row,
        col
    ):

        for r in range(
            len(block)
        ):

            for c in range(
                len(block[r])
            ):

                if block[r][c] == 1:

                    board_row = row + r
                    board_col = col + c

                    if board_row < 0:
                        return False

                    if board_row >= ROWS:
                        return False

                    if board_col < 0:
                        return False

                    if board_col >= COLS:
                        return False

                    if self.board[
                        board_row
                    ][
                        board_col
                    ] == 1:

                        return False

        return True

    # ========================================================
    # MOVE
    # ========================================================

    def move_left(
        self,
        event=None
    ):

        if (
            self.game_over
            or self.paused
            or self.countdown_active
        ):
            return

        if self.can_place(
            self.current_block,
            self.block_row,
            self.block_col - 1
        ):

            self.block_col -= 1

        self.draw()

    # ========================================================

    def move_right(
        self,
        event=None
    ):

        if (
            self.game_over
            or self.paused
            or self.countdown_active
        ):
            return

        if self.can_place(
            self.current_block,
            self.block_row,
            self.block_col + 1
        ):

            self.block_col += 1

        self.draw()

    # ========================================================
    # ROTATE
    # ========================================================

    def rotate_matrix(
        self,
        block
    ):

        return [
            list(row)
            for row in zip(
                *block[::-1]
            )
        ]

    def rotate_block(
        self,
        event=None
    ):

        if (
            self.game_over
            or self.paused
            or self.countdown_active
        ):
            return

        rotated = self.rotate_matrix(
            self.current_block
        )

        if self.can_place(
            rotated,
            self.block_row,
            self.block_col
        ):

            self.current_block = rotated

        self.draw()

    # ========================================================
    # LOCK BLOCK
    # ========================================================

    def lock_block(self):

        cells = 0

        for r in range(
            len(self.current_block)
        ):

            for c in range(
                len(self.current_block[r])
            ):

                if self.current_block[r][c] == 1:

                    board_row = (
                        self.block_row + r
                    )

                    board_col = (
                        self.block_col + c
                    )

                    if (
                        board_row >= 0
                        and board_row < ROWS
                        and board_col >= 0
                        and board_col < COLS
                    ):

                        self.board[
                            board_row
                        ][
                            board_col
                        ] = 1

                        self.board_colors[
                            board_row
                        ][
                            board_col
                        ] = self.current_color

                        cells += 1

        # Placement score
        self.score += cells

        self.update_level()

    # ========================================================
    # ARCADE CLEAR
    # ========================================================

    def arcade_clear(self):

        qualifying_rows = []

        # ----------------------------------------------------
        # NEW REQUIREMENT:
        #
        # 6 OR MORE OCCUPIED CELLS = CLEAR
        # ----------------------------------------------------

        for row in range(ROWS):

            filled = sum(
                self.board[row]
            )

            if filled >= 6:

                qualifying_rows.append(
                    row
                )

        # ----------------------------------------------------
        # No qualifying rows
        # ----------------------------------------------------

        if not qualifying_rows:

            self.combo = 0

            return

        # ----------------------------------------------------
        # Combo
        # ----------------------------------------------------

        self.combo += 1

        self.lines += len(
            qualifying_rows
        )

        # ----------------------------------------------------
        # Determine strongest row
        # ----------------------------------------------------

        strongest = 0

        for row in qualifying_rows:

            filled = sum(
                self.board[row]
            )

            if filled > strongest:

                strongest = filled

        # ----------------------------------------------------
        # Determine neighboring rows
        # ----------------------------------------------------

        neighbor_rows = set()

        for row in qualifying_rows:

            if row - 1 >= 0:

                neighbor_rows.add(
                    row - 1
                )

            if row + 1 < ROWS:

                neighbor_rows.add(
                    row + 1
                )

        # ----------------------------------------------------
        # CLEAR QUALIFYING ROWS
        # ----------------------------------------------------

        for row in qualifying_rows:

            self.board[row] = [
                0 for _ in range(COLS)
            ]

            self.board_colors[row] = [
                None for _ in range(COLS)
            ]

        # ----------------------------------------------------
        # 6 CELLS
        #
        # Small neighboring damage
        # ----------------------------------------------------

        if strongest == 6:

            damage_ratio = 0.25

        # ----------------------------------------------------
        # 7 CELLS
        #
        # Medium neighboring damage
        # ----------------------------------------------------

        elif strongest == 7:

            damage_ratio = 0.50

        # ----------------------------------------------------
        # 8 CELLS
        #
        # Major 3-row clear
        # ----------------------------------------------------

        else:

            damage_ratio = 0.75

        # ----------------------------------------------------
        # DAMAGE NEIGHBOR ROWS
        # ----------------------------------------------------

        for row in neighbor_rows:

            occupied = []

            for col in range(COLS):

                if self.board[row][col] == 1:

                    occupied.append(col)

            random.shuffle(
                occupied
            )

            if len(occupied) > 0:

                damage = max(
                    1,
                    int(
                        len(occupied)
                        * damage_ratio
                    )
                )

                for col in occupied[
                    :damage
                ]:

                    self.board[
                        row
                    ][
                        col
                    ] = 0

                    self.board_colors[
                        row
                    ][
                        col
                    ] = None

        # ----------------------------------------------------
        # COMBO BLAST
        #
        # If the player clears successfully
        # multiple times in a row, damage
        # additional surrounding rows.
        # ----------------------------------------------------

        if self.combo >= 2:

            extra_rows = set()

            for row in qualifying_rows:

                for offset in [-2, 2]:

                    target = row + offset

                    if (
                        target >= 0
                        and target < ROWS
                    ):

                        extra_rows.add(
                            target
                        )

            for row in extra_rows:

                occupied = []

                for col in range(COLS):

                    if self.board[row][col] == 1:

                        occupied.append(col)

                random.shuffle(
                    occupied
                )

                damage = max(
                    1,
                    len(occupied) // 2
                )

                for col in occupied[
                    :damage
                ]:

                    self.board[
                        row
                    ][
                        col
                    ] = 0

                    self.board_colors[
                        row
                    ][
                        col
                    ] = None

        # ----------------------------------------------------
        # SCORE
        # ----------------------------------------------------

        if strongest == 6:

            base_score = 30

        elif strongest == 7:

            base_score = 50

        else:

            base_score = 100

        # Multiple qualifying rows
        row_bonus = (
            len(qualifying_rows)
            * 10
        )

        # Combo bonus
        combo_bonus = (
            self.combo
            * 25
        )

        # Strong clear bonus
        strong_bonus = (
            strongest
            * 5
        )

        # ----------------------------------------------------
        # BIG BLAST BONUS
        # ----------------------------------------------------

        blast_bonus = 0

        if (
            strongest == 8
            and self.combo >= 2
        ):

            blast_bonus = 100

        self.score += (
            base_score
            + row_bonus
            + combo_bonus
            + strong_bonus
            + blast_bonus
        )

        # ----------------------------------------------------
        # Level
        # ----------------------------------------------------

        self.update_level()

    # ========================================================
    # LEVEL
    # ========================================================

    def update_level(self):

        self.level = (
            self.score // LEVEL_SCORE
        ) + 1

        # Faster every level
        self.fall_speed = max(
            MIN_FALL_SPEED,
            START_FALL_SPEED
            - (
                (self.level - 1)
                * SPEED_STEP
            )
        )

        # High score
        if self.score > self.high_score:

            self.high_score = self.score

    # ========================================================
    # HARD DROP
    # ========================================================

    def hard_drop(
        self,
        event=None
    ):

        if (
            self.game_over
            or self.paused
            or self.countdown_active
        ):
            return

        dropped = 0

        while self.can_place(
            self.current_block,
            self.block_row + 1,
            self.block_col
        ):

            self.block_row += 1

            dropped += 1

        # Drop score
        self.score += dropped

        # Lock
        self.lock_block()

        # Clear
        self.arcade_clear()

        # New block
        self.spawn_block()

        self.draw()

    # ========================================================
    # AUTOMATIC FALL
    # ========================================================

    def fall(self):

        if self.game_over:

            self.draw()

            return

        if self.paused:

            self.root.after(
                self.fall_speed,
                self.fall
            )

            return

        if self.countdown_active:

            return

        # ----------------------------------------------------
        # Try moving down
        # ----------------------------------------------------

        if self.can_place(
            self.current_block,
            self.block_row + 1,
            self.block_col
        ):

            self.block_row += 1

        else:

            # Lock
            self.lock_block()

            # Clear
            self.arcade_clear()

            # Spawn
            self.spawn_block()

        self.draw()

        if not self.game_over:

            self.root.after(
                self.fall_speed,
                self.fall
            )

    # ========================================================
    # MENU
    # ========================================================

    def open_menu(self):

        menu = tk.Toplevel(
            self.root
        )

        menu.title(
            "BlockMaster Menu"
        )

        menu.geometry(
            "300x390"
        )

        menu.resizable(
            False,
            False
        )

        menu.configure(
            bg=BACKGROUND
        )

        title = tk.Label(
            menu,
            text="MENU",
            font=("Arial", 20, "bold"),
            bg=BACKGROUND,
            fg=TEXT
        )

        title.pack(
            pady=20
        )

        # ----------------------------------------------------
        # RESUME
        # ----------------------------------------------------

        resume = tk.Button(
            menu,
            text="RESUME",
            width=18,
            height=2,
            bg=BUTTON_BG,
            activebackground=BUTTON_ACTIVE,
            fg=TEXT,
            relief="flat",
            command=lambda: self.resume_game(menu)
        )

        resume.pack(
            pady=6
        )

        # ----------------------------------------------------
        # PAUSE
        # ----------------------------------------------------

        pause = tk.Button(
            menu,
            text="PAUSE",
            width=18,
            height=2,
            bg=PANEL,
            activebackground=BUTTON_ACTIVE,
            fg=TEXT,
            relief="flat",
            command=lambda: self.pause_game(menu)
        )

        pause.pack(
            pady=6
        )

        # ----------------------------------------------------
        # RESET
        # ----------------------------------------------------

        reset = tk.Button(
            menu,
            text="RESET",
            width=18,
            height=2,
            bg=PANEL,
            activebackground=BUTTON_ACTIVE,
            fg=TEXT,
            relief="flat",
            command=lambda: self.reset_game(menu)
        )

        reset.pack(
            pady=6
        )

        # ----------------------------------------------------
        # HOME
        # ----------------------------------------------------

        home = tk.Button(
            menu,
            text="HOME",
            width=18,
            height=2,
            bg=PANEL,
            activebackground=BUTTON_ACTIVE,
            fg=TEXT,
            relief="flat",
            command=lambda: self.go_home(menu)
        )

        home.pack(
            pady=6
        )

        # ----------------------------------------------------
        # QUIT
        # ----------------------------------------------------

        quit_button = tk.Button(
            menu,
            text="QUIT",
            width=18,
            height=2,
            bg=PANEL,
            activebackground=BUTTON_ACTIVE,
            fg=TEXT,
            relief="flat",
            command=self.root.destroy
        )

        quit_button.pack(
            pady=6
        )

    # ========================================================
    # PAUSE
    # ========================================================

    def pause_game(
        self,
        menu=None
    ):

        if not self.game_over:

            self.paused = True

            self.draw()

        if menu:

            menu.destroy()

    # ========================================================
    # RESUME
    # ========================================================

    def resume_game(
        self,
        menu=None
    ):

        if not self.game_over:

            self.paused = False

            self.draw()

        if menu:

            menu.destroy()

    # ========================================================
    # RESET
    # ========================================================

    def reset_game(
        self,
        menu=None
    ):

        if menu:

            menu.destroy()

        self.start_game()

    # ========================================================
    # HOME
    # ========================================================

    def go_home(
        self,
        menu=None
    ):

        if menu:

            menu.destroy()

        self.create_home_screen()

    # ========================================================
    # RESTART KEY
    # ========================================================

    def restart_key(
        self,
        event=None
    ):

        if self.game_over:

            self.start_game()


# ============================================================
# START PROGRAM
# ============================================================

root = tk.Tk()

game = BlockMaster(
    root
)

root.mainloop()
