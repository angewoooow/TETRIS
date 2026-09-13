
import tkinter as tk
import random


# ============================================================
# BLOCKMASTER
# ARCADE UI VERSION
# ============================================================
#
# BOARD:
# 8 columns x 16 rows
#
# CONTROLS:
# LEFT       = Move left
# RIGHT      = Move right
# UP         = Rotate
# DOWN       = Rotate
# SPACE      = Hard drop / lock
#
# FEATURES:
# - Player name
# - 3 second countdown
# - Score
# - High score
# - Level
# - Next block preview
# - 6+ filled cells can clear a row
# - Combo system
# - Blast clearing
# - Session leaderboard
# - Recent 10 scores
# - Same-window menu
# - Restart button
# - Home screen
# - Dark arcade theme
# - 3D UI
# - 3D blocks
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
# GAME SPEED
# ============================================================

# Level 1 starts slower
START_FALL_SPEED = 1500

# Every level gets faster
SPEED_STEP = 75

# Never become impossibly fast
MIN_FALL_SPEED = 300


# ============================================================
# LEVEL
# ============================================================

LEVEL_SCORE = 75


# ============================================================
# DARK ARCADE COLORS
# ============================================================

BG = "#111318"
BG_DARK = "#0A0C10"

PANEL = "#1C2029"
PANEL_DARK = "#151820"
PANEL_LIGHT = "#252B36"

BORDER = "#454D5A"

TEXT = "#E8EAF0"
TEXT_DIM = "#9CA3AF"

ACCENT = "#B9A7D9"
ACCENT_DARK = "#75658F"

BUTTON = "#292F3A"
BUTTON_LIGHT = "#353C49"
BUTTON_PRESS = "#454D5A"

SUCCESS = "#A8D5BA"
WARNING = "#E7C98A"

# Game board
BOARD_BG = "#181B22"
GRID = "#2A303A"

# Pastel-ish but darker arcade block colors
BLOCK_COLORS = [
    "#7BA7B8",
    "#B68CA8",
    "#8FA6C9",
    "#8FB39A",
    "#C7A77B",
    "#A995C9",
    "#B98585"
]


# ============================================================
# ARCADE FONT
# ============================================================

FONT = "Courier New"


class BlockMaster:

    def __init__(self, root):

        self.root = root

        self.root.title("BLOCKMASTER")

        self.root.geometry("1080x850")

        self.root.resizable(False, False)

        self.root.configure(
            bg=BG
        )

        # ====================================================
        # PLAYER DATA
        # ====================================================

        self.player_name = ""

        # ====================================================
        # SCORE DATA
        # ====================================================

        self.score = 0
        self.high_score = 0
        self.level = 1
        self.lines = 0
        self.combo = 0

        # ====================================================
        # GAME DATA
        # ====================================================

        self.fall_speed = START_FALL_SPEED

        self.game_over = False
        self.paused = False
        self.countdown_active = False

        # ====================================================
        # SESSION SCORE HISTORY
        # ====================================================

        # Every completed game is stored here.
        #
        # Example:
        # [
        #   {"name": "ANGELO", "score": 450},
        #   {"name": "JUAN", "score": 300}
        # ]
        #
        self.session_scores = []

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
        # CURRENT / NEXT BLOCK
        # ====================================================

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

        # ====================================================
        # BOARD
        # ====================================================

        self.board = []

        self.board_colors = []

        # ====================================================
        # HOME SCREEN
        # ====================================================

        self.create_home_screen()

    # ========================================================
    # UTILITY
    # ========================================================

    def clear_root(self):

        for widget in self.root.winfo_children():

            widget.destroy()

    # ========================================================
    # 3D FRAME
    # ========================================================

    def create_3d_frame(
        self,
        parent,
        bg=PANEL,
        padx=10,
        pady=10
    ):

        frame = tk.Frame(
            parent,
            bg=bg,
            padx=padx,
            pady=pady,
            relief="raised",
            bd=3,
            highlightthickness=1,
            highlightbackground=BORDER
        )

        return frame

    # ========================================================
    # 3D BUTTON
    # ========================================================

    def create_arcade_button(
        self,
        parent,
        text,
        command,
        width=18
    ):

        button = tk.Button(
            parent,
            text=text,
            command=command,
            width=width,
            height=2,
            font=(
                FONT,
                11,
                "bold"
            ),
            bg=BUTTON,
            fg=TEXT,
            activebackground=BUTTON_PRESS,
            activeforeground=TEXT,
            relief="raised",
            bd=4,
            padx=8,
            pady=4,
            cursor="hand2"
        )

        return button

    # ========================================================
    # HOME SCREEN
    # ========================================================

    def create_home_screen(self):

        self.clear_root()

        self.home_container = tk.Frame(
            self.root,
            bg=BG
        )

        self.home_container.pack(
            fill="both",
            expand=True,
            padx=35,
            pady=30
        )

        # ====================================================
        # TITLE
        # ====================================================

        title_frame = self.create_3d_frame(
            self.home_container,
            bg=PANEL_DARK,
            padx=30,
            pady=18
        )

        title_frame.pack(
            fill="x",
            pady=(0, 20)
        )

        title = tk.Label(
            title_frame,
            text="B L O C K M A S T E R",
            font=(
                FONT,
                27,
                "bold"
            ),
            bg=PANEL_DARK,
            fg=ACCENT
        )

        title.pack()

        subtitle = tk.Label(
            title_frame,
            text="A R C A D E   B L O C K   P U Z Z L E",
            font=(
                FONT,
                9,
                "bold"
            ),
            bg=PANEL_DARK,
            fg=TEXT_DIM
        )

        subtitle.pack(
            pady=(6, 0)
        )

        # ====================================================
        # MAIN HOME AREA
        # ====================================================

        home_area = tk.Frame(
            self.home_container,
            bg=BG
        )

        home_area.pack(
            fill="both",
            expand=True
        )

        # ====================================================
        # LEFT SIDE
        # ====================================================

        left = tk.Frame(
            home_area,
            bg=BG
        )

        left.pack(
            side="left",
            fill="y",
            padx=(0, 15)
        )

        # ====================================================
        # PLAYER BOX
        # ====================================================

        player_box = self.create_3d_frame(
            left,
            bg=PANEL
        )

        player_box.pack(
            fill="x",
            pady=8
        )

        player_title = tk.Label(
            player_box,
            text="PLAYER",
            font=(
                FONT,
                10,
                "bold"
            ),
            bg=PANEL,
            fg=TEXT_DIM
        )

        player_title.pack()

        self.name_entry = tk.Entry(
            player_box,
            width=22,
            font=(
                FONT,
                12,
                "bold"
            ),
            justify="center",
            bg=BG_DARK,
            fg=TEXT,
            insertbackground=TEXT,
            relief="sunken",
            bd=3
        )

        self.name_entry.insert(
            0,
            "PLAYER"
        )

        self.name_entry.pack(
            pady=10,
            ipady=7
        )

        # ====================================================
        # START BUTTON
        # ====================================================

        start_button = self.create_arcade_button(
            left,
            "▶  START GAME",
            self.start_game,
            width=22
        )

        start_button.pack(
            pady=10
        )

        # ====================================================
        # INSTRUCTIONS
        # ====================================================

        instruction_box = self.create_3d_frame(
            left,
            bg=PANEL_DARK
        )

        instruction_box.pack(
            fill="x",
            pady=10
        )

        instruction_title = tk.Label(
            instruction_box,
            text="CONTROLS",
            font=(
                FONT,
                10,
                "bold"
            ),
            bg=PANEL_DARK,
            fg=ACCENT
        )

        instruction_title.pack(
            pady=(0, 10)
        )

        instruction_text = (
            "← →   MOVE\n"
            "↑ ↓   ROTATE\n"
            "SPACE   DROP\n"
            "\n"
            "CLEAR 6+ CELLS\n"
            "BUILD COMBOS"
        )

        instruction = tk.Label(
            instruction_box,
            text=instruction_text,
            font=(
                FONT,
                9,
                "bold"
            ),
            bg=PANEL_DARK,
            fg=TEXT_DIM,
            justify="center"
        )

        instruction.pack()

        # ====================================================
        # RIGHT SIDE — LEADERBOARD
        # ====================================================

        right = tk.Frame(
            home_area,
            bg=BG
        )

        right.pack(
            side="left",
            fill="both",
            expand=True
        )

        # ====================================================
        # SESSION LEADERBOARD
        # ====================================================

        leaderboard_box = self.create_3d_frame(
            right,
            bg=PANEL
        )

        leaderboard_box.pack(
            fill="both",
            expand=True,
            pady=8
        )

        leaderboard_title = tk.Label(
            leaderboard_box,
            text="🏆  SESSION LEADERBOARD",
            font=(
                FONT,
                12,
                "bold"
            ),
            bg=PANEL,
            fg=ACCENT
        )

        leaderboard_title.pack(
            pady=(0, 12)
        )

        # ----------------------------------------------------
        # Header
        # ----------------------------------------------------

        header = tk.Frame(
            leaderboard_box,
            bg=PANEL_LIGHT,
            relief="raised",
            bd=2
        )

        header.pack(
            fill="x"
        )

        tk.Label(
            header,
            text="RANK",
            width=6,
            font=(
                FONT,
                9,
                "bold"
            ),
            bg=PANEL_LIGHT,
            fg=TEXT_DIM
        ).pack(
            side="left"
        )

        tk.Label(
            header,
            text="PLAYER",
            width=16,
            font=(
                FONT,
                9,
                "bold"
            ),
            bg=PANEL_LIGHT,
            fg=TEXT_DIM
        ).pack(
            side="left"
        )

        tk.Label(
            header,
            text="SCORE",
            width=10,
            font=(
                FONT,
                9,
                "bold"
            ),
            bg=PANEL_LIGHT,
            fg=TEXT_DIM
        ).pack(
            side="left"
        )

        # ----------------------------------------------------
        # Leaderboard rows
        # ----------------------------------------------------

        self.leaderboard_frame = tk.Frame(
            leaderboard_box,
            bg=PANEL
        )

        self.leaderboard_frame.pack(
            fill="both",
            expand=True
        )

        self.refresh_leaderboard()

        # ====================================================
        # ALL-TIME SCORE
        # ====================================================

        high_box = self.create_3d_frame(
            right,
            bg=PANEL_DARK
        )

        high_box.pack(
            fill="x",
            pady=10
        )

        high_title = tk.Label(
            high_box,
            text="👑  HIGHEST SCORE THIS SESSION",
            font=(
                FONT,
                10,
                "bold"
            ),
            bg=PANEL_DARK,
            fg=TEXT_DIM
        )

        high_title.pack()

        self.home_high_score_label = tk.Label(
            high_box,
            text=str(
                self.high_score
            ),
            font=(
                FONT,
                25,
                "bold"
            ),
            bg=PANEL_DARK,
            fg=ACCENT
        )

        self.home_high_score_label.pack(
            pady=5
        )

        # ====================================================
        # FOOTER
        # ====================================================

        footer = tk.Label(
            self.home_container,
            text="BLOCKMASTER  •  ARCADE MODE",
            font=(
                FONT,
                8,
                "bold"
            ),
            bg=BG,
            fg=TEXT_DIM
        )

        footer.pack(
            pady=10
        )

        self.name_entry.focus()

        self.root.bind(
            "<Return>",
            lambda event: self.start_game()
        )

    # ========================================================
    # START GAME
    # ========================================================

    def start_game(self):

        name = self.name_entry.get().strip()

        if name == "":

            name = "PLAYER"

        self.player_name = name.upper()

        self.score = 0

        self.lines = 0

        self.level = 1

        self.combo = 0

        self.fall_speed = START_FALL_SPEED

        self.game_over = False

        self.paused = False

        self.countdown_active = False

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
            bg=BG
        )

        self.game_container.pack(
            fill="both",
            expand=True,
            padx=25,
            pady=20
        )

        # ====================================================
        # TOP PLAYER BOX
        # ====================================================

        player_box = self.create_3d_frame(
            self.game_container,
            bg=PANEL_DARK,
            padx=20,
            pady=10
        )

        player_box.pack(
            fill="x",
            pady=(0, 15)
        )

        self.player_label = tk.Label(
            player_box,
            text=f"PLAYER  //  {self.player_name}",
            font=(
                FONT,
                15,
                "bold"
            ),
            bg=PANEL_DARK,
            fg=ACCENT
        )

        self.player_label.pack()

        # ====================================================
        # GAME AREA
        # ====================================================

        self.main_game_area = tk.Frame(
            self.game_container,
            bg=BG
        )

        self.main_game_area.pack()

        # ====================================================
        # BOARD CONTAINER
        # ====================================================

        board_outer = self.create_3d_frame(
            self.main_game_area,
            bg=PANEL_DARK,
            padx=12,
            pady=12
        )

        board_outer.pack(
            side="left",
            padx=12
        )

        self.canvas = tk.Canvas(
            board_outer,
            width=BOARD_WIDTH,
            height=BOARD_HEIGHT,
            bg=BOARD_BG,
            highlightthickness=3,
            highlightbackground=BORDER
        )

        self.canvas.pack()

        # ====================================================
        # SIDE PANEL
        # ====================================================

        self.side_panel = tk.Frame(
            self.main_game_area,
            bg=BG,
            width=260
        )

        self.side_panel.pack(
            side="left",
            padx=15,
            anchor="n"
        )

        # ====================================================
        # SCORE
        # ====================================================

        score_box = self.create_stat_box(
            self.side_panel,
            "SCORE",
            "0"
        )

        score_box.pack(
            fill="x",
            pady=6
        )

        self.score_value = score_box.value_label

        # ====================================================
        # HIGH SCORE
        # ====================================================

        high_box = self.create_stat_box(
            self.side_panel,
            "HIGH SCORE",
            str(self.high_score)
        )

        high_box.pack(
            fill="x",
            pady=6
        )

        self.high_score_value = high_box.value_label

        # ====================================================
        # LEVEL
        # ====================================================

        level_box = self.create_stat_box(
            self.side_panel,
            "LEVEL",
            "1"
        )

        level_box.pack(
            fill="x",
            pady=6
        )

        self.level_value = level_box.value_label

        # ====================================================
        # NEXT BLOCK
        # ====================================================

        next_box = self.create_3d_frame(
            self.side_panel,
            bg=PANEL
        )

        next_box.pack(
            fill="x",
            pady=10
        )

        tk.Label(
            next_box,
            text="NEXT BLOCK",
            font=(
                FONT,
                10,
                "bold"
            ),
            bg=PANEL,
            fg=TEXT_DIM
        ).pack(
            pady=(0, 8)
        )

        self.next_canvas = tk.Canvas(
            next_box,
            width=180,
            height=125,
            bg=BG_DARK,
            highlightthickness=2,
            highlightbackground=BORDER
        )

        self.next_canvas.pack()

        # ====================================================
        # MENU BUTTON
        # ====================================================

        self.menu_button = self.create_arcade_button(
            self.side_panel,
            "☰  MENU",
            self.toggle_menu,
            width=18
        )

        self.menu_button.pack(
            pady=10
        )

        # ====================================================
        # MENU PANEL
        # ====================================================

        self.menu_panel = self.create_3d_frame(
            self.side_panel,
            bg=PANEL_DARK,
            padx=15,
            pady=15
        )

        self.menu_visible = False

        # Menu title
        menu_title = tk.Label(
            self.menu_panel,
            text="GAME MENU",
            font=(
                FONT,
                11,
                "bold"
            ),
            bg=PANEL_DARK,
            fg=ACCENT
        )

        menu_title.pack(
            pady=(0, 10)
        )

        # Resume
        self.resume_button = self.create_arcade_button(
            self.menu_panel,
            "▶  RESUME",
            self.resume_game,
            width=16
        )

        self.resume_button.pack(
            pady=4
        )

        # Pause
        self.pause_button = self.create_arcade_button(
            self.menu_panel,
            "Ⅱ  PAUSE",
            self.pause_game,
            width=16
        )

        self.pause_button.pack(
            pady=4
        )

        # Reset
        reset_button = self.create_arcade_button(
            self.menu_panel,
            "↻  RESET",
            self.reset_game,
            width=16
        )

        reset_button.pack(
            pady=4
        )

        # Home
        home_button = self.create_arcade_button(
            self.menu_panel,
            "⌂  HOME",
            self.go_home,
            width=16
        )

        home_button.pack(
            pady=4
        )

        # Quit
        quit_button = self.create_arcade_button(
            self.menu_panel,
            "✕  QUIT",
            self.quit_game,
            width=16
        )

        quit_button.pack(
            pady=4
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

        box = self.create_3d_frame(
            parent,
            bg=PANEL,
            padx=15,
            pady=10
        )

        title_label = tk.Label(
            box,
            text=title,
            font=(
                FONT,
                9,
                "bold"
            ),
            bg=PANEL,
            fg=TEXT_DIM
        )

        title_label.pack()

        value_label = tk.Label(
            box,
            text=value,
            font=(
                FONT,
                18,
                "bold"
            ),
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

    def show_countdown(self):

        if not self.countdown_active:

            return

        self.draw()

        center_x = BOARD_WIDTH / 2
        center_y = BOARD_HEIGHT / 2

        self.canvas.create_rectangle(
            center_x - 120,
            center_y - 100,
            center_x + 120,
            center_y + 100,
            fill=PANEL_DARK,
            outline=ACCENT,
            width=3
        )

        if self.countdown_value > 0:

            self.canvas.create_text(
                center_x,
                center_y,
                text=str(
                    self.countdown_value
                ),
                font=(
                    FONT,
                    65,
                    "bold"
                ),
                fill=ACCENT
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
                font=(
                    FONT,
                    40,
                    "bold"
                ),
                fill=SUCCESS
            )

            self.root.after(
                500,
                self.finish_countdown
            )

    # ========================================================

    def finish_countdown(self):

        self.countdown_active = False

        self.draw()

        self.fall()

    # ========================================================
    # SPAWN
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

        width = len(
            self.current_block[0]
        )

        self.block_col = (
            COLS - width
        ) // 2

        if not self.can_place(
            self.current_block,
            self.block_row,
            self.block_col
        ):

            self.game_over = True

            self.save_finished_game()

    # ========================================================
    # DRAW
    # ========================================================

    def draw(self):

        if not hasattr(
            self,
            "canvas"
        ):

            return

        self.canvas.delete("all")

        # ====================================================
        # GRID
        # ====================================================

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
                    outline=GRID
                )

        # ====================================================
        # LOCKED BLOCKS
        # ====================================================

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

        # ====================================================
        # CURRENT BLOCK
        # ====================================================

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

        # ====================================================
        # NEXT
        # ====================================================

        if hasattr(
            self,
            "next_canvas"
        ):

            self.draw_next_shape()

        # ====================================================
        # PAUSE
        # ====================================================

        if self.paused:

            center_x = BOARD_WIDTH / 2
            center_y = BOARD_HEIGHT / 2

            self.canvas.create_rectangle(
                center_x - 120,
                center_y - 70,
                center_x + 120,
                center_y + 70,
                fill=PANEL_DARK,
                outline=ACCENT,
                width=3
            )

            self.canvas.create_text(
                center_x,
                center_y,
                text="PAUSED",
                font=(
                    FONT,
                    25,
                    "bold"
                ),
                fill=ACCENT
            )

        # ====================================================
        # GAME OVER
        # ====================================================

        if self.game_over:

            center_x = BOARD_WIDTH / 2
            center_y = BOARD_HEIGHT / 2

            self.canvas.create_rectangle(
                center_x - 140,
                center_y - 115,
                center_x + 140,
                center_y + 115,
                fill=PANEL_DARK,
                outline=ACCENT,
                width=3
            )

            self.canvas.create_text(
                center_x,
                center_y - 65,
                text="GAME OVER",
                font=(
                    FONT,
                    23,
                    "bold"
                ),
                fill=TEXT
            )

            self.canvas.create_text(
                center_x,
                center_y - 20,
                text=f"SCORE: {self.score}",
                font=(
                    FONT,
                    12,
                    "bold"
                ),
                fill=ACCENT
            )

            # Restart icon/button
            self.canvas.create_rectangle(
                center_x - 95,
                center_y + 15,
                center_x + 95,
                center_y + 65,
                fill=BUTTON,
                outline=BORDER,
                width=3,
                tags="restart_button"
            )

            self.canvas.create_text(
                center_x,
                center_y + 40,
                text="↻  RESTART",
                font=(
                    FONT,
                    11,
                    "bold"
                ),
                fill=TEXT,
                tags="restart_button"
            )

            self.canvas.tag_bind(
                "restart_button",
                "<Button-1>",
                lambda event: self.reset_game()
            )

        # ====================================================
        # UPDATE STATS
        # ====================================================

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
            outline=BG_DARK,
            width=2
        )

        # Top highlight
        self.canvas.create_polygon(
            x + 4,
            y + 4,
            x + CELL_SIZE - 4,
            y + 4,
            x + CELL_SIZE - 8,
            y + 8,
            x + 8,
            y + 8,
            fill="#D8DEE5",
            outline=""
        )

        # Left highlight
        self.canvas.create_polygon(
            x + 4,
            y + 4,
            x + 8,
            y + 8,
            x + 8,
            y + CELL_SIZE - 8,
            x + 4,
            y + CELL_SIZE - 4,
            fill="#C5CDD5",
            outline=""
        )

        # Bottom shadow
        self.canvas.create_polygon(
            x + 4,
            y + CELL_SIZE - 4,
            x + CELL_SIZE - 4,
            y + CELL_SIZE - 4,
            x + CELL_SIZE - 8,
            y + CELL_SIZE - 8,
            x + 8,
            y + CELL_SIZE - 8,
            fill="#59616D",
            outline=""
        )

        # Right shadow
        self.canvas.create_polygon(
            x + CELL_SIZE - 4,
            y + 4,
            x + CELL_SIZE - 8,
            y + 8,
            x + CELL_SIZE - 8,
            y + CELL_SIZE - 8,
            x + CELL_SIZE - 4,
            y + CELL_SIZE - 4,
            fill="#68717D",
            outline=""
        )

    # ========================================================
    # NEXT BLOCK
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
            180 - width
        ) / 2

        start_y = (
            125 - height
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

                    self.next_canvas.create_rectangle(
                        x + 2,
                        y + 2,
                        x + cell - 2,
                        y + cell - 2,
                        fill=self.next_color,
                        outline=BG_DARK,
                        width=2
                    )

                    # Highlight
                    self.next_canvas.create_line(
                        x + 4,
                        y + 4,
                        x + cell - 5,
                        y + 4,
                        fill="#D8DEE5",
                        width=2
                    )

    # ========================================================
    # COLLISION
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
    # MOVE LEFT
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
    # MOVE RIGHT
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
    # ROTATION
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
    # LOCK
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
                        0 <= board_row < ROWS
                        and 0 <= board_col < COLS
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

        # Basic placement score
        self.score += cells

        self.update_level()

    # ========================================================
    # ARCADE CLEAR SYSTEM
    # ========================================================

    def arcade_clear(self):

        qualifying_rows = []

        # ----------------------------------------------------
        # 6+ CELLS = CLEAR
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
        # Nothing cleared
        # ----------------------------------------------------

        if not qualifying_rows:

            self.combo = 0

            return

        # ----------------------------------------------------
        # COMBO
        # ----------------------------------------------------

        self.combo += 1

        self.lines += len(
            qualifying_rows
        )

        # ----------------------------------------------------
        # Strongest row
        # ----------------------------------------------------

        strongest = 0

        for row in qualifying_rows:

            filled = sum(
                self.board[row]
            )

            strongest = max(
                strongest,
                filled
            )

        # ----------------------------------------------------
        # Neighbor rows
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
        # Clear main rows
        # ----------------------------------------------------

        for row in qualifying_rows:

            self.board[row] = [
                0 for _ in range(COLS)
            ]

            self.board_colors[row] = [
                None for _ in range(COLS)
            ]

        # ----------------------------------------------------
        # 6 cells
        # ----------------------------------------------------

        if strongest == 6:

            damage_ratio = 0.25

        # ----------------------------------------------------
        # 7 cells
        # ----------------------------------------------------

        elif strongest == 7:

            damage_ratio = 0.50

        # ----------------------------------------------------
        # 8 cells
        # ----------------------------------------------------

        else:

            damage_ratio = 0.75

        # ----------------------------------------------------
        # DAMAGE NEIGHBORS
        # ----------------------------------------------------

        for row in neighbor_rows:

            occupied = []

            for col in range(COLS):

                if self.board[row][col] == 1:

                    occupied.append(col)

            random.shuffle(
                occupied
            )

            if occupied:

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
        # ----------------------------------------------------

        if self.combo >= 2:

            extra_rows = set()

            for row in qualifying_rows:

                for offset in [-2, 2]:

                    target = row + offset

                    if (
                        0 <= target < ROWS
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

        row_bonus = (
            len(qualifying_rows)
            * 10
        )

        combo_bonus = (
            self.combo
            * 25
        )

        strong_bonus = (
            strongest
            * 5
        )

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

        self.update_level()

    # ========================================================
    # LEVEL
    # ========================================================

    def update_level(self):

        self.level = (
            self.score // LEVEL_SCORE
        ) + 1

        self.fall_speed = max(
            MIN_FALL_SPEED,
            START_FALL_SPEED
            - (
                (self.level - 1)
                * SPEED_STEP
            )
        )

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

        # Drop bonus
        self.score += dropped

        self.lock_block()

        self.arcade_clear()

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
        # Move down
        # ----------------------------------------------------

        if self.can_place(
            self.current_block,
            self.block_row + 1,
            self.block_col
        ):

            self.block_row += 1

        else:

            self.lock_block()

            self.arcade_clear()

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

    def toggle_menu(self):

        if self.menu_visible:

            self.menu_panel.pack_forget()

            self.menu_visible = False

        else:

            self.menu_panel.pack(
                fill="x",
                pady=8
            )

            self.menu_visible = True

    # ========================================================
    # PAUSE
    # ========================================================

    def pause_game(self):

        if not self.game_over:

            self.paused = True

            self.draw()

    # ========================================================
    # RESUME
    # ========================================================

    def resume_game(self):

        if not self.game_over:

            self.paused = False

            self.draw()

    # ========================================================
    # RESET
    # ========================================================

    def reset_game(self):

        # Save current game only if it has started
        if self.player_name:

            if self.score > 0:

                self.save_finished_game()

        # Go back to player screen
        self.create_home_screen()

    # ========================================================
    # SAVE FINISHED GAME
    # ========================================================

    def save_finished_game(self):

        # Prevent accidental duplicate saves
        if getattr(
            self,
            "score_saved",
            False
        ):

            return

        self.score_saved = True

        result = {
            "name": self.player_name,
            "score": self.score
        }

        self.session_scores.append(
            result
        )

        # Sort highest score first
        self.session_scores.sort(
            key=lambda x: x["score"],
            reverse=True
        )

        # Keep only 10 recent score entries
        # for the visible history.
        #
        # NOTE:
        # The complete session data remains
        # available in session_scores.
        #
        self.refresh_leaderboard()

    # ========================================================
    # QUIT
    # ========================================================

    def quit_game(self):

        self.root.destroy()

    # ========================================================
    # HOME
    # ========================================================

    def go_home(self):

        if self.player_name:

            if self.score > 0 and not self.game_over:

                self.save_finished_game()

        self.create_home_screen()

    # ========================================================
    # REFRESH LEADERBOARD
    # ========================================================

    def refresh_leaderboard(self):

        if not hasattr(
            self,
            "leaderboard_frame"
        ):

            return

        for widget in self.leaderboard_frame.winfo_children():

            widget.destroy()

        # ----------------------------------------------------
        # Last 10 score records
        # ----------------------------------------------------

        recent = self.session_scores[-10:]

        # Display newest first
        recent = list(
            reversed(recent)
        )

        if not recent:

            empty = tk.Label(
                self.leaderboard_frame,
                text="NO SCORES YET\n\nSTART A GAME!",
                font=(
                    FONT,
                    10,
                    "bold"
                ),
                bg=PANEL,
                fg=TEXT_DIM,
                justify="center"
            )

            empty.pack(
                pady=50
            )

            return

        for index, result in enumerate(
            recent,
            start=1
        ):

            row = tk.Frame(
                self.leaderboard_frame,
                bg=(
                    PANEL_LIGHT
                    if index % 2 == 0
                    else PANEL
                ),
                relief="raised",
                bd=1
            )

            row.pack(
                fill="x",
                pady=2
            )

            # Rank
            rank_text = str(index)

            tk.Label(
                row,
                text=rank_text,
                width=6,
                font=(
                    FONT,
                    9,
                    "bold"
                ),
                bg=row["bg"],
                fg=TEXT_DIM
            ).pack(
                side="left"
            )

            # Name
            tk.Label(
                row,
                text=result["name"][:14],
                width=16,
                font=(
                    FONT,
                    9,
                    "bold"
                ),
                bg=row["bg"],
                fg=TEXT
            ).pack(
                side="left"
            )

            # Score
            tk.Label(
                row,
                text=str(
                    result["score"]
                ),
                width=10,
                font=(
                    FONT,
                    9,
                    "bold"
                ),
                bg=row["bg"],
                fg=ACCENT
            ).pack(
                side="left"
            )

        # Update home high score
        if hasattr(
            self,
            "home_high_score_label"
        ):

            self.home_high_score_label.config(
                text=str(
                    self.high_score
                )
            )

    # ========================================================
    # RESTART AFTER GAME OVER
    # ========================================================

    def restart_game(self):

        # Reset game but keep player name
        self.score = 0

        self.lines = 0

        self.level = 1

        self.combo = 0

        self.fall_speed = START_FALL_SPEED

        self.game_over = False

        self.paused = False

        self.countdown_active = False

        self.score_saved = False

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


# ============================================================
# PROGRAM START
# ============================================================

root = tk.Tk()

game = BlockMaster(
    root
)

root.mainloop()
