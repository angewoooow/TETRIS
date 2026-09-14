import tkinter as tk
import random
import time

from clearing import ClearingSystem
from database import DatabaseManager


# ============================================================
# BLOCKMASTER - NEON 3D ARCADE
# ============================================================

ROWS = 23
COLS = 10
CELL_SIZE = 32

BOARD_WIDTH = COLS * CELL_SIZE
BOARD_HEIGHT = ROWS * CELL_SIZE

START_SPEED = 1600
SPEED_STEP = 200
SPEED_INTERVAL = 20_000
MIN_SPEED = 300

LEVEL_SCORE = 500


# ============================================================
# NEON ARCADE COLORS
# ============================================================

BG = "#171525"
BG2 = "#211B35"
PANEL = "#2B2444"
PANEL2 = "#382E58"
PANEL3 = "#49386A"

NEON_CYAN = "#69F6FF"
NEON_PINK = "#FF67D9"
NEON_PURPLE = "#B98CFF"
NEON_GREEN = "#75F7A8"
NEON_YELLOW = "#FFE66D"
NEON_RED = "#FF718B"

WHITE = "#F5F4FF"
MUTED = "#BDB7D6"
GRID = "#493F63"
BOARD_BG = "#12101D"

GOLD = "#FFD700"
SILVER = "#D9E0E8"
BRONZE = "#CD7F32"

FONT = "Consolas"


BLOCK_COLORS = [
    "#42DDF0",
    "#FFE66D",
    "#B98CFF",
    "#FF9A62",
    "#FF718B",
    "#75F7A8",
    "#FF67D9",
]


class BlockMaster:

    # ========================================================
    # INITIALIZATION
    # ========================================================

    def __init__(self, root):

        self.root = root

        self.root.title("BlockMaster - Neon Arcade")

        self.root.geometry("1200x920")
        self.root.minsize(1000, 760)
        self.root.resizable(True, True)

        self.root.configure(bg=BG)

        # ----------------------------------------------------
        # SHAPES
        # ----------------------------------------------------

        self.shapes = [

            [[1, 1, 1, 1]],

            [[1, 1],
             [1, 1]],

            [[1, 1, 1],
             [0, 1, 0]],

            [[1, 0],
             [1, 0],
             [1, 1]],

            [[0, 1],
             [0, 1],
             [1, 1]],

            [[0, 1, 1],
             [1, 1, 0]],

            [[1, 1, 0],
             [0, 1, 1]],
        ]

        self.shape_names = [
            "I",
            "O",
            "T",
            "L",
            "J",
            "S",
            "Z"
        ]

        # ----------------------------------------------------
        # GAME STATE
        # ----------------------------------------------------

        self.player_name = "PLAYER"

        self.score = 0
        self.high_score = 0
        self.level = 1
        self.lines = 0
        self.combo = 0

        self.fall_speed = START_SPEED

        self.game_start_time = None

        self.game_over = False
        self.paused = False

        self.countdown_active = False
        self.countdown_hidden = False

        self.score_saved = False
        self.lock_in_progress = False

        # ----------------------------------------------------
        # TKINTER JOBS
        # ----------------------------------------------------

        self.menu_window = None
        self.menu_overlay = None

        self.game_over_overlay = None

        self.fall_job = None
        self.speed_job = None

        # ----------------------------------------------------
        # SESSION
        # ----------------------------------------------------

        self.session_scores = []

        # ----------------------------------------------------
        # CURRENT BLOCK
        # ----------------------------------------------------

        self.current_block = None
        self.current_shape_index = 0
        self.current_color = BLOCK_COLORS[0]

        self.next_block = random.choice(self.shapes)

        self.next_shape_index = self.shapes.index(
            self.next_block
        )

        self.next_color = BLOCK_COLORS[
            self.next_shape_index
        ]

        self.block_row = 0
        self.block_col = 0

        # ----------------------------------------------------
        # BOARD
        # ----------------------------------------------------

        self.board = []
        self.board_colors = []

        self.CELL_SIZE = CELL_SIZE

        # ----------------------------------------------------
        # CLEARING SYSTEM
        # ----------------------------------------------------

        self.clearer = ClearingSystem(self)

        # ----------------------------------------------------
        # DATABASE
        # ----------------------------------------------------

        self.db = DatabaseManager()

        print("[DATABASE] Testing connection...")

        if self.db.connect():
            print("[DATABASE] Database connection is READY.")

            self.high_score = self.db.get_high_score()

        else:
            print(
                "[DATABASE] Database unavailable. "
                "Game will continue without permanent storage."
            )

        # ----------------------------------------------------
        # HOME
        # ----------------------------------------------------

        self.create_home_screen()

    # ========================================================
    # GENERAL UI
    # ========================================================

    def clear_root(self):

        for widget in self.root.winfo_children():

            try:
                widget.destroy()
            except tk.TclError:
                pass

    def frame3d(
        self,
        parent,
        bg=PANEL,
        padx=12,
        pady=12
    ):

        return tk.Frame(
            parent,
            bg=bg,
            padx=padx,
            pady=pady,
            relief="raised",
            bd=5,
            highlightthickness=2,
            highlightbackground=PANEL3,
        )

    def button3d(
        self,
        parent,
        text,
        command,
        width=18
    ):

        return tk.Button(
            parent,
            text=text,
            command=command,
            width=width,
            height=2,
            font=(FONT, 10, "bold"),
            bg=PANEL2,
            fg=WHITE,
            activebackground=NEON_PURPLE,
            activeforeground=BG,
            relief="raised",
            bd=5,
            cursor="hand2",
        )

    # ========================================================
    # HOME SCREEN
    # ========================================================

    def create_home_screen(self):

        self.cancel_jobs()

        self.close_menu()

        self.game_over_overlay = None

        # ----------------------------------------------------
        # Reload database information
        # ----------------------------------------------------

        if hasattr(self, "db"):

            self.high_score = self.db.get_high_score()

        self.clear_root()

        # ----------------------------------------------------
        # ROOT CONTAINER
        # ----------------------------------------------------

        root_box = tk.Frame(
            self.root,
            bg=BG
        )

        root_box.pack(
            fill="both",
            expand=True,
            padx=22,
            pady=18
        )

        # ----------------------------------------------------
        # TITLE
        # ----------------------------------------------------

        title = self.frame3d(
            root_box,
            BG2,
            20,
            14
        )

        title.pack(
            fill="x",
            pady=(0, 12)
        )

        tk.Label(
            title,
            text="B L O C K M A S T E R",
            font=(FONT, 28, "bold"),
            bg=BG2,
            fg=NEON_CYAN,
        ).pack()

        tk.Label(
            title,
            text="N E O N   A R C A D E",
            font=(FONT, 10, "bold"),
            bg=BG2,
            fg=NEON_PINK,
        ).pack(pady=(4, 0))

        # ----------------------------------------------------
        # MAIN CONTENT
        # ----------------------------------------------------

        content = tk.Frame(
            root_box,
            bg=BG
        )

        content.pack(
            fill="both",
            expand=True
        )

        # ====================================================
        # LEFT SIDE
        # ====================================================

        left = tk.Frame(
            content,
            bg=BG,
            width=300
        )

        left.pack(
            side="left",
            fill="y",
            padx=(0, 14)
        )

        left.pack_propagate(False)

        # ----------------------------------------------------
        # PLAYER
        # ----------------------------------------------------

        player_box = self.frame3d(
            left,
            PANEL
        )

        player_box.pack(
            fill="x",
            pady=5
        )

        tk.Label(
            player_box,
            text="ENTER PLAYER",
            font=(FONT, 10, "bold"),
            bg=PANEL,
            fg=NEON_CYAN,
        ).pack()

        self.name_entry = tk.Entry(
            player_box,
            width=22,
            font=(FONT, 13, "bold"),
            justify="center",
            bg=BOARD_BG,
            fg=WHITE,
            insertbackground=NEON_CYAN,
            relief="sunken",
            bd=5,
        )

        self.name_entry.insert(
            0,
            self.player_name or "PLAYER"
        )

        self.name_entry.pack(
            pady=10,
            ipady=8
        )

        # ----------------------------------------------------
        # START
        # ----------------------------------------------------

        start = self.button3d(
            left,
            "▶  START GAME",
            self.start_game,
            22
        )

        start.pack(
            fill="x",
            pady=7
        )

        # ----------------------------------------------------
        # CONTROLS
        # ----------------------------------------------------

        controls = self.frame3d(
            left,
            BG2
        )

        controls.pack(
            fill="x",
            pady=5
        )

        tk.Label(
            controls,
            text="CONTROLS",
            font=(FONT, 11, "bold"),
            bg=BG2,
            fg=NEON_PINK,
        ).pack(
            pady=(0, 8)
        )

        tk.Label(
            controls,
            text=(
                "← →   MOVE\n"
                "↑ ↓   ROTATE\n"
                "SPACE   HARD DROP\n\n"
                "ROW CLEAR = SCORE\n"
                "COMBOS = BONUS\n"
                "SPEED INCREASES"
            ),
            font=(FONT, 9, "bold"),
            bg=BG2,
            fg=MUTED,
            justify="center",
        ).pack()

        # ----------------------------------------------------
        # CURRENT HIGH SCORE CARD
        # ----------------------------------------------------

        high_box = self.frame3d(
            left,
            BG2,
            14,
            12
        )

        high_box.pack(
            fill="x",
            pady=7
        )

        tk.Label(
            high_box,
            text="👑 CURRENT CHAMPION",
            font=(FONT, 10, "bold"),
            bg=BG2,
            fg=NEON_YELLOW,
        ).pack()

        high_record = None

        if hasattr(self, "db"):
            high_record = self.db.get_high_score_record()

        if high_record:

            champion_name = (
                high_record.get(
                    "player_name",
                    "PLAYER"
                )
                or "PLAYER"
            )

            champion_score = high_record.get(
                "score",
                self.high_score
            )

        else:

            champion_name = "NO CHAMPION"

            champion_score = self.high_score

        tk.Label(
            high_box,
            text=champion_name[:18],
            font=(FONT, 16, "bold"),
            bg=BG2,
            fg=NEON_CYAN,
        ).pack(pady=(5, 0))

        tk.Label(
            high_box,
            text=f"{champion_score:,}",
            font=(FONT, 28, "bold"),
            bg=BG2,
            fg=NEON_YELLOW,
        ).pack()

        tk.Label(
            high_box,
            text="ALL-TIME HIGH SCORE",
            font=(FONT, 8, "bold"),
            bg=BG2,
            fg=MUTED,
        ).pack()

        # ====================================================
        # RIGHT SIDE - LEADERBOARD
        # ====================================================

        right = tk.Frame(
            content,
            bg=BG
        )

        right.pack(
            side="left",
            fill="both",
            expand=True
        )

        leaderboard_box = self.frame3d(
            right,
            PANEL,
            12,
            12
        )

        leaderboard_box.pack(
            fill="both",
            expand=True
        )

        # ----------------------------------------------------
        # HEADER
        # ----------------------------------------------------

        tk.Label(
            leaderboard_box,
            text="🏆  ALL-TIME ARCADE LEADERBOARD",
            font=(FONT, 18, "bold"),
            bg=PANEL,
            fg=NEON_YELLOW,
        ).pack(
            pady=(0, 3)
        )

        tk.Label(
            leaderboard_box,
            text="HIGHEST SCORES • ALL PLAYERS • ALL GAMES",
            font=(FONT, 8, "bold"),
            bg=PANEL,
            fg=MUTED,
        ).pack(
            pady=(0, 10)
        )

        # ----------------------------------------------------
        # TABLE HEADER
        # ----------------------------------------------------

        header = tk.Frame(
            leaderboard_box,
            bg=PANEL3,
            relief="raised",
            bd=4
        )

        header.pack(
            fill="x"
        )

        tk.Label(
            header,
            text="RANK",
            width=8,
            font=(FONT, 10, "bold"),
            bg=PANEL3,
            fg=WHITE,
        ).pack(side="left", padx=3, pady=7)

        tk.Label(
            header,
            text="PLAYER",
            width=20,
            font=(FONT, 10, "bold"),
            bg=PANEL3,
            fg=WHITE,
        ).pack(side="left", padx=3, pady=7)

        tk.Label(
            header,
            text="SCORE",
            width=14,
            font=(FONT, 10, "bold"),
            bg=PANEL3,
            fg=WHITE,
        ).pack(side="left", padx=3, pady=7)

        tk.Label(
            header,
            text="LEVEL",
            width=9,
            font=(FONT, 10, "bold"),
            bg=PANEL3,
            fg=WHITE,
        ).pack(side="left", padx=3, pady=7)

        tk.Label(
            header,
            text="LINES",
            width=9,
            font=(FONT, 10, "bold"),
            bg=PANEL3,
            fg=WHITE,
        ).pack(side="left", padx=3, pady=7)

        # ----------------------------------------------------
        # LEADERBOARD SCROLL AREA
        # ----------------------------------------------------

        table_container = tk.Frame(
            leaderboard_box,
            bg=PANEL
        )

        table_container.pack(
            fill="both",
            expand=True,
            pady=(5, 0)
        )

        self.leaderboard_canvas = tk.Canvas(
            table_container,
            bg=PANEL,
            highlightthickness=0
        )

        self.leaderboard_scrollbar = tk.Scrollbar(
            table_container,
            orient="vertical",
            command=self.leaderboard_canvas.yview
        )

        self.leaderboard_frame = tk.Frame(
            self.leaderboard_canvas,
            bg=PANEL
        )

        self.leaderboard_window = (
            self.leaderboard_canvas.create_window(
                (0, 0),
                window=self.leaderboard_frame,
                anchor="nw"
            )
        )

        self.leaderboard_canvas.configure(
            yscrollcommand=self.leaderboard_scrollbar.set
        )

        self.leaderboard_canvas.pack(
            side="left",
            fill="both",
            expand=True
        )

        self.leaderboard_scrollbar.pack(
            side="right",
            fill="y"
        )

        self.leaderboard_frame.bind(
            "<Configure>",
            self.update_leaderboard_scrollregion
        )

        self.leaderboard_canvas.bind(
            "<Configure>",
            self.resize_leaderboard_frame
        )

        self.leaderboard_canvas.bind_all(
            "<MouseWheel>",
            self.scroll_leaderboard
        )

        # ----------------------------------------------------
        # LOAD DATABASE LEADERBOARD
        # ----------------------------------------------------

        self.refresh_leaderboard()

        # ----------------------------------------------------
        # FOOTER
        # ----------------------------------------------------

        tk.Label(
            root_box,
            text=(
                "NEON ARCADE EDITION   •   "
                "10 × 23 BOARD   •   "
                "DATABASE HIGH SCORES"
            ),
            font=(FONT, 8, "bold"),
            bg=BG,
            fg=MUTED,
        ).pack(
            pady=5
        )

        self.name_entry.focus_set()

        self.root.bind(
            "<Return>",
            lambda e: self.start_game()
        )

    # ========================================================
    # LEADERBOARD SCROLL
    # ========================================================

    def update_leaderboard_scrollregion(self, event=None):

        if hasattr(
            self,
            "leaderboard_canvas"
        ):

            self.leaderboard_canvas.configure(
                scrollregion=self.leaderboard_canvas.bbox(
                    "all"
                )
            )

    def resize_leaderboard_frame(self, event):

        if hasattr(
            self,
            "leaderboard_canvas"
        ):

            self.leaderboard_canvas.itemconfig(
                self.leaderboard_window,
                width=event.width
            )

    def scroll_leaderboard(self, event):

        if hasattr(
            self,
            "leaderboard_canvas"
        ):

            self.leaderboard_canvas.yview_scroll(
                int(-1 * (event.delta / 120)),
                "units"
            )

    # ========================================================
    # START / RESET
    # ========================================================

    def reset_state(self):

        self.close_menu()

        self.cancel_jobs()

        # ----------------------------------------------------
        # DESTROY OLD GAME OVER POPUP
        # ----------------------------------------------------

        if getattr(
            self,
            "game_over_overlay",
            None
        ):

            try:
                self.game_over_overlay.destroy()
            except tk.TclError:
                pass

            self.game_over_overlay = None

        # ----------------------------------------------------
        # RESET SCORE
        # ----------------------------------------------------

        self.score = 0
        self.lines = 0
        self.level = 1
        self.combo = 0

        self.fall_speed = START_SPEED

        self.game_over = False
        self.paused = False

        self.countdown_active = False

        # IMPORTANT:
        # New piece must remain invisible during countdown.
        self.countdown_hidden = True

        self.score_saved = False
        self.lock_in_progress = False

        self.game_start_time = None

        # ----------------------------------------------------
        # RESET BOARD
        # ----------------------------------------------------

        self.board = [
            [0 for _ in range(COLS)]
            for _ in range(ROWS)
        ]

        self.board_colors = [
            [None for _ in range(COLS)]
            for _ in range(ROWS)
        ]

        # ----------------------------------------------------
        # RESET BLOCKS
        # ----------------------------------------------------

        self.current_block = None

        self.next_block = random.choice(
            self.shapes
        )

        self.next_shape_index = self.shapes.index(
            self.next_block
        )

        self.next_color = BLOCK_COLORS[
            self.next_shape_index
        ]

    def start_game(self):

        name = self.name_entry.get().strip()

        self.player_name = (
            name.upper()
            if name
            else "PLAYER"
        )

        self.reset_state()

        self.create_game_screen()

        self.spawn_block()

        if self.game_over:

            self.draw()

            return

        # Keep the piece invisible during countdown.
        self.countdown_hidden = True

        self.draw()

        self.start_countdown()

    def reset_current_game(self):

        # ----------------------------------------------------
        # IMPORTANT:
        # Destroy old game-over screen FIRST
        # ----------------------------------------------------

        if getattr(
            self,
            "game_over_overlay",
            None
        ):

            try:
                self.game_over_overlay.destroy()
            except tk.TclError:
                pass

            self.game_over_overlay = None

        # ----------------------------------------------------
        # Make sure player name survives restart
        # ----------------------------------------------------

        if not self.player_name:
            self.player_name = "PLAYER"

        # ----------------------------------------------------
        # COMPLETE GAME RESET
        # ----------------------------------------------------

        self.reset_state()

        self.create_game_screen()

        self.spawn_block()

        if self.game_over:

            self.draw()

            return

        # ----------------------------------------------------
        # IMPORTANT FIX:
        # Do NOT show the new piece until countdown finishes.
        # ----------------------------------------------------

        self.countdown_hidden = True

        self.draw()

        self.start_countdown()

    # ========================================================
    # GAME SCREEN
    # ========================================================

    def create_game_screen(self):

        self.close_menu()

        self.clear_root()

        top = tk.Frame(
            self.root,
            bg=BG
        )

        top.pack(
            fill="x",
            padx=18,
            pady=(12, 8)
        )

        player = self.frame3d(
            top,
            BG2,
            14,
            8
        )

        player.pack(
            side="left",
            fill="x",
            expand=True,
            padx=(0, 8)
        )

        tk.Label(
            player,
            text=self.player_name,
            font=(FONT, 13, "bold"),
            bg=BG2,
            fg=NEON_CYAN,
        ).pack()

        self.menu_button = self.button3d(
            top,
            "☰  MENU",
            self.toggle_menu,
            12
        )

        self.menu_button.pack(
            side="left"
        )

        # ----------------------------------------------------
        # GAME AREA
        # ----------------------------------------------------

        game_area = tk.Frame(
            self.root,
            bg=BG
        )

        game_area.pack(
            fill="both",
            expand=True,
            padx=18,
            pady=4
        )

        spacer = tk.Frame(
            game_area,
            bg=BG,
            width=180
        )

        spacer.pack(
            side="left",
            fill="y"
        )

        spacer.pack_propagate(False)

        board_box = self.frame3d(
            game_area,
            BG2,
            9,
            9
        )

        board_box.pack(
            side="left",
            anchor="n"
        )

        self.canvas = tk.Canvas(
            board_box,
            width=BOARD_WIDTH,
            height=BOARD_HEIGHT,
            bg=BOARD_BG,
            highlightthickness=3,
            highlightbackground=NEON_PURPLE,
        )

        self.canvas.pack()

        # ----------------------------------------------------
        # RIGHT GAME PANEL
        # ----------------------------------------------------

        side = tk.Frame(
            game_area,
            bg=BG,
            width=250
        )

        side.pack(
            side="left",
            fill="y",
            padx=(18, 0)
        )

        side.pack_propagate(False)

        self.score_value = self.make_stat(
            side,
            "SCORE",
            "0"
        )

        self.high_value = self.make_stat(
            side,
            "HIGH SCORE",
            str(self.high_score)
        )

        self.level_value = self.make_stat(
            side,
            "LEVEL",
            "1"
        )

        # ----------------------------------------------------
        # NEXT BLOCK
        # ----------------------------------------------------

        next_box = self.frame3d(
            side,
            PANEL
        )

        next_box.pack(
            fill="x",
            pady=6
        )

        tk.Label(
            next_box,
            text="NEXT BLOCK",
            font=(FONT, 10, "bold"),
            bg=PANEL,
            fg=NEON_PINK,
        ).pack(
            pady=(0, 7)
        )

        self.next_canvas = tk.Canvas(
            next_box,
            width=190,
            height=115,
            bg=BOARD_BG,
            highlightthickness=2,
            highlightbackground=PANEL3,
        )

        self.next_canvas.pack()

        # ----------------------------------------------------
        # COMBO
        # ----------------------------------------------------

        combo_box = self.frame3d(
            side,
            BG2
        )

        combo_box.pack(
            fill="x",
            pady=6
        )

        tk.Label(
            combo_box,
            text="COMBO",
            font=(FONT, 9, "bold"),
            bg=BG2,
            fg=MUTED,
        ).pack()

        self.combo_value = tk.Label(
            combo_box,
            text="x0",
            font=(FONT, 20, "bold"),
            bg=BG2,
            fg=NEON_YELLOW,
        )

        self.combo_value.pack()

        tk.Label(
            self.root,
            text=(
                "← → MOVE     "
                "↑ ↓ ROTATE     "
                "SPACE HARD DROP"
            ),
            font=(FONT, 9, "bold"),
            bg=BG,
            fg=MUTED,
        ).pack(
            pady=7
        )

        # ----------------------------------------------------
        # KEYBOARD
        # ----------------------------------------------------

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

    def make_stat(
        self,
        parent,
        title,
        value
    ):

        box = self.frame3d(
            parent,
            PANEL
        )

        box.pack(
            fill="x",
            pady=5
        )

        tk.Label(
            box,
            text=title,
            font=(FONT, 8, "bold"),
            bg=PANEL,
            fg=MUTED,
        ).pack()

        value_label = tk.Label(
            box,
            text=value,
            font=(FONT, 19, "bold"),
            bg=PANEL,
            fg=NEON_CYAN,
        )

        value_label.pack(
            pady=3
        )

        return value_label

    # ========================================================
    # COUNTDOWN
    # ========================================================

    def start_countdown(self):

        self.countdown_active = True

        self.countdown_value = 3

        self.show_countdown()

    def show_countdown(self):

        if (
            not self.countdown_active
            or self.game_over
        ):
            return

        self.draw()

        cx = BOARD_WIDTH / 2
        cy = BOARD_HEIGHT / 2

        self.canvas.create_rectangle(
            cx - 125,
            cy - 90,
            cx + 125,
            cy + 90,
            fill=BG2,
            outline=NEON_CYAN,
            width=5,
        )

        if self.countdown_value > 0:

            text = str(
                self.countdown_value
            )

            self.countdown_value -= 1

            delay = 700

        else:

            text = "GO!"

            delay = 450

        self.canvas.create_text(
            cx,
            cy,
            text=text,
            font=(
                FONT,
                58 if text != "GO!" else 38,
                "bold"
            ),
            fill=(
                NEON_PINK
                if text != "GO!"
                else NEON_GREEN
            ),
        )

        if text == "GO!":

            self.root.after(
                delay,
                self.finish_countdown
            )

        else:

            self.root.after(
                delay,
                self.show_countdown
            )

    def finish_countdown(self):

        if self.game_over:
            return

        self.countdown_active = False

        self.countdown_hidden = False

        self.game_start_time = time.monotonic()

        self.start_speed_timer()

        self.draw()

        self.schedule_fall()

    # ========================================================
    # SPEED
    # ========================================================

    def start_speed_timer(self):

        if self.speed_job:

            try:
                self.root.after_cancel(
                    self.speed_job
                )
            except tk.TclError:
                pass

        self.speed_job = self.root.after(
            250,
            self.update_time_speed
        )

    def update_time_speed(self):

        if self.game_over:
            return

        if (
            not self.paused
            and not self.countdown_active
            and self.game_start_time
        ):

            elapsed_ms = int(
                (
                    time.monotonic()
                    - self.game_start_time
                ) * 1000
            )

            steps = (
                elapsed_ms
                // SPEED_INTERVAL
            )

            self.fall_speed = max(
                MIN_SPEED,
                START_SPEED
                - steps * SPEED_STEP
            )

        self.speed_job = self.root.after(
            250,
            self.update_time_speed
        )

    def schedule_fall(self):

        if self.fall_job:

            try:
                self.root.after_cancel(
                    self.fall_job
                )
            except tk.TclError:
                pass

        if (
            not self.game_over
            and not self.paused
            and not self.countdown_active
        ):

            self.fall_job = self.root.after(
                self.fall_speed,
                self.fall
            )

    # ========================================================
    # SPAWN
    # ========================================================

    def spawn_block(self):

        if self.current_block is None:

            self.current_block = random.choice(
                self.shapes
            )

            self.current_shape_index = (
                self.shapes.index(
                    self.current_block
                )
            )

            self.current_color = (
                BLOCK_COLORS[
                    self.current_shape_index
                ]
            )

        else:

            self.current_block = [
                row[:]
                for row in self.next_block
            ]

            self.current_shape_index = (
                self.next_shape_index
            )

            self.current_color = (
                self.next_color
            )

        # ----------------------------------------------------
        # Generate next piece
        # ----------------------------------------------------

        self.next_block = random.choice(
            self.shapes
        )

        self.next_shape_index = (
            self.shapes.index(
                self.next_block
            )
        )

        self.next_color = (
            BLOCK_COLORS[
                self.next_shape_index
            ]
        )

        self.block_row = 0

        self.block_col = (
            COLS
            - len(self.current_block[0])
        ) // 2

        # ----------------------------------------------------
        # GAME OVER
        # ----------------------------------------------------

        if not self.can_place(
            self.current_block,
            self.block_row,
            self.block_col
        ):

            self.game_over = True

            self.save_finished_game()

    # ========================================================
    # COLLISION
    # ========================================================

    def can_place(
        self,
        block,
        row,
        col
    ):

        for r, line in enumerate(block):

            for c, value in enumerate(line):

                if not value:
                    continue

                br = row + r
                bc = col + c

                if (
                    br < 0
                    or br >= ROWS
                    or bc < 0
                    or bc >= COLS
                ):
                    return False

                if self.board[br][bc]:
                    return False

        return True

    # ========================================================
    # MOVEMENT
    # ========================================================

    def move_left(self, event=None):

        if self.blocked_input():
            return

        if self.can_place(
            self.current_block,
            self.block_row,
            self.block_col - 1
        ):

            self.block_col -= 1

        self.draw()

    def move_right(self, event=None):

        if self.blocked_input():
            return

        if self.can_place(
            self.current_block,
            self.block_row,
            self.block_col + 1
        ):

            self.block_col += 1

        self.draw()

    def blocked_input(self):

        return (
            self.game_over
            or self.paused
            or self.countdown_active
            or self.lock_in_progress
            or self.current_block is None
        )

    # ========================================================
    # ROTATION
    # ========================================================

    def rotate_matrix(self, block):

        return [
            list(row)
            for row in zip(
                *block[::-1]
            )
        ]

    def rotate_block(self, event=None):

        if self.blocked_input():
            return

        rotated = self.rotate_matrix(
            self.current_block
        )

        for offset in (
            0,
            -1,
            1,
            -2,
            2
        ):

            if self.can_place(
                rotated,
                self.block_row,
                self.block_col + offset
            ):

                self.current_block = rotated

                self.block_col += offset

                break

        self.draw()

    # ========================================================
    # LOCK BLOCK
    # ========================================================

    def lock_block(self):

        cells = 0

        for r, line in enumerate(
            self.current_block
        ):

            for c, value in enumerate(line):

                if value:

                    br = (
                        self.block_row
                        + r
                    )

                    bc = (
                        self.block_col
                        + c
                    )

                    if (
                        0 <= br < ROWS
                        and 0 <= bc < COLS
                    ):

                        self.board[br][bc] = 1

                        self.board_colors[
                            br
                        ][bc] = self.current_color

                        cells += 1

        self.score += cells

        self.update_level()

    # ========================================================
    # PROCESS LOCK
    # ========================================================

    def process_lock(self):

        if (
            self.lock_in_progress
            or self.game_over
        ):
            return

        self.lock_in_progress = True

        if self.fall_job:

            try:
                self.root.after_cancel(
                    self.fall_job
                )
            except tk.TclError:
                pass

            self.fall_job = None

        locked_shape_index = (
            self.current_shape_index
        )

        locked_row = self.block_row

        locked_col = self.block_col

        locked_block = [
            row[:]
            for row in self.current_block
        ]

        self.lock_block()

        self.current_block = None

        self.draw()

        result = self.clearer.resolve(
            locked_shape_index,
            locked_row,
            locked_col,
            locked_block,
        )

        if result["cleared"]:

            self.lines += result.get(
                "rows",
                0
            )

            self.combo += 1

            combo_bonus = (
                self.combo * 35
            )

            earned = (
                result["score"]
                + combo_bonus
            )

            self.score += earned

            self.show_combo(
                result["message"],
                earned
            )

        else:

            self.combo = 0

        self.update_level()

        # ----------------------------------------------------
        # Exactly one new block
        # ----------------------------------------------------

        if not self.game_over:

            self.spawn_block()

        self.lock_in_progress = False

        self.draw()

    # ========================================================
    # FALL
    # ========================================================

    def fall(self):

        self.fall_job = None

        if (
            self.game_over
            or self.paused
            or self.countdown_active
            or self.lock_in_progress
        ):

            self.schedule_fall()

            return

        if self.can_place(
            self.current_block,
            self.block_row + 1,
            self.block_col
        ):

            self.block_row += 1

        else:

            self.process_lock()

        self.draw()

        if not self.game_over:

            self.schedule_fall()

    # ========================================================
    # HARD DROP
    # ========================================================

    def hard_drop(self, event=None):

        if self.blocked_input():
            return

        if self.lock_in_progress:
            return

        dropped = 0

        while self.can_place(
            self.current_block,
            self.block_row + 1,
            self.block_col
        ):

            self.block_row += 1

            dropped += 1

        self.score += dropped

        self.process_lock()

        self.draw()

        if not self.game_over:

            self.schedule_fall()

    # ========================================================
    # SCORE / LEVEL
    # ========================================================

    def update_level(self):

        self.level = (
            self.score
            // LEVEL_SCORE
        ) + 1

        if self.score > self.high_score:

            self.high_score = self.score

        if hasattr(
            self,
            "score_value"
        ):

            self.score_value.config(
                text=str(self.score)
            )

            self.high_value.config(
                text=str(self.high_score)
            )

            self.level_value.config(
                text=str(self.level)
            )

            self.combo_value.config(
                text=f"x{self.combo}"
            )

    # ========================================================
    # COMBO
    # ========================================================

    def show_combo(
        self,
        message,
        points
    ):

        if not hasattr(
            self,
            "canvas"
        ):
            return

        cx = BOARD_WIDTH / 2

        y = BOARD_HEIGHT * 0.38

        self.canvas.create_text(
            cx,
            y,
            text=message,
            font=(FONT, 18, "bold"),
            fill=NEON_YELLOW,
            tags="combo_fx",
        )

        self.canvas.create_text(
            cx,
            y + 30,
            text=f"+{points}",
            font=(FONT, 12, "bold"),
            fill=NEON_GREEN,
            tags="combo_fx",
        )

        self.root.after(
            650,
            lambda: (
                self.canvas.delete(
                    "combo_fx"
                )
                if hasattr(
                    self,
                    "canvas"
                )
                else None
            )
        )

    # ========================================================
    # DRAW BOARD
    # ========================================================

    def draw(self):

        if not hasattr(
            self,
            "canvas"
        ):
            return

        self.canvas.delete("all")

        # ----------------------------------------------------
        # GRID
        # ----------------------------------------------------

        for r in range(ROWS):

            for c in range(COLS):

                x = c * CELL_SIZE

                y = r * CELL_SIZE

                self.canvas.create_rectangle(
                    x,
                    y,
                    x + CELL_SIZE,
                    y + CELL_SIZE,
                    fill=BOARD_BG,
                    outline=GRID,
                )

        # ----------------------------------------------------
        # LOCKED BLOCKS
        # ----------------------------------------------------

        for r in range(ROWS):

            for c in range(COLS):

                if self.board[r][c]:

                    self.draw_3d_block(
                        self.canvas,
                        c * CELL_SIZE,
                        r * CELL_SIZE,
                        self.board_colors[r][c],
                    )

        # ----------------------------------------------------
        # CURRENT BLOCK
        # ----------------------------------------------------

        if (
            self.current_block is not None
            and not self.game_over
            and not self.countdown_hidden
        ):

            for r, line in enumerate(
                self.current_block
            ):

                for c, value in enumerate(line):

                    if value:

                        self.draw_3d_block(
                            self.canvas,
                            (
                                self.block_col + c
                            ) * CELL_SIZE,
                            (
                                self.block_row + r
                            ) * CELL_SIZE,
                            self.current_color,
                        )

        self.draw_next_shape()

        if (
            self.paused
            and not self.game_over
        ):

            self.draw_center_overlay(
                "PAUSED",
                NEON_YELLOW
            )

        if self.game_over:

            self.draw_game_over()

        self.update_level()

    # ========================================================
    # 3D BLOCK
    # ========================================================

    def draw_3d_block(
        self,
        canvas,
        x,
        y,
        color,
        size=CELL_SIZE
    ):

        canvas.create_rectangle(
            x + 1,
            y + 1,
            x + size - 1,
            y + size - 1,
            outline=color,
            width=2,
        )

        canvas.create_rectangle(
            x + 4,
            y + 4,
            x + size - 4,
            y + size - 4,
            fill=color,
            outline="#0B0912",
            width=2,
        )

        canvas.create_polygon(
            x + 5,
            y + 5,
            x + size - 5,
            y + 5,
            x + size - 9,
            y + 9,
            x + 9,
            y + 9,
            fill="#FFFFFF",
            outline="",
        )

        canvas.create_polygon(
            x + 5,
            y + 5,
            x + 9,
            y + 9,
            x + 9,
            y + size - 9,
            x + 5,
            y + size - 5,
            fill="#D8D5E6",
            outline="",
        )

        canvas.create_polygon(
            x + 5,
            y + size - 5,
            x + size - 5,
            y + size - 5,
            x + size - 9,
            y + size - 9,
            x + 9,
            y + size - 9,
            fill="#5D5870",
            outline="",
        )

        canvas.create_polygon(
            x + size - 5,
            y + 5,
            x + size - 9,
            y + 9,
            x + size - 9,
            y + size - 9,
            x + size - 5,
            y + size - 5,
            fill="#716B85",
            outline="",
        )

    # ========================================================
    # NEXT SHAPE
    # ========================================================

    def draw_next_shape(self):

        if not hasattr(
            self,
            "next_canvas"
        ):
            return

        self.next_canvas.delete("all")

        block = self.next_block

        cell = 24

        rows = len(block)

        cols = len(block[0])

        start_x = (
            190
            - cols * cell
        ) / 2

        start_y = (
            115
            - rows * cell
        ) / 2

        for r, line in enumerate(block):

            for c, value in enumerate(line):

                if value:

                    self.draw_3d_block(
                        self.next_canvas,
                        start_x + c * cell,
                        start_y + r * cell,
                        self.next_color,
                        cell,
                    )

    # ========================================================
    # CENTER OVERLAY
    # ========================================================

    def draw_center_overlay(
        self,
        title,
        color
    ):

        cx = BOARD_WIDTH / 2

        cy = BOARD_HEIGHT / 2

        self.canvas.create_rectangle(
            cx - 145,
            cy - 75,
            cx + 145,
            cy + 75,
            fill=BG2,
            outline=color,
            width=5,
        )

        self.canvas.create_text(
            cx,
            cy,
            text=title,
            font=(FONT, 28, "bold"),
            fill=color,
        )

    # ========================================================
    # GAME OVER
    # ========================================================

    def draw_game_over(self):

        if getattr(
            self,
            "game_over_overlay",
            None
        ) is not None:

            try:

                if self.game_over_overlay.winfo_exists():
                    return

            except tk.TclError:
                pass

        # ----------------------------------------------------
        # Darken board
        # ----------------------------------------------------

        self.canvas.create_rectangle(
            0,
            0,
            BOARD_WIDTH,
            BOARD_HEIGHT,
            fill="#110E19",
            outline="",
            tags="gameover_dim"
        )

        # ----------------------------------------------------
        # Game over popup
        # ----------------------------------------------------

        self.game_over_overlay = tk.Frame(
            self.root,
            bg=BG2,
            relief="raised",
            bd=8,
            highlightthickness=3,
            highlightbackground=NEON_PINK,
        )

        self.game_over_overlay.place(
            relx=0.5,
            rely=0.5,
            anchor="center",
            relwidth=0.58,
            relheight=0.70
        )

        outer = self.frame3d(
            self.game_over_overlay,
            PANEL,
            22,
            18
        )

        outer.pack(
            fill="both",
            expand=True,
            padx=8,
            pady=8
        )

        tk.Label(
            outer,
            text="GAME OVER",
            font=(FONT, 28, "bold"),
            bg=PANEL,
            fg=NEON_PINK
        ).pack(
            pady=(8, 2)
        )

        tk.Label(
            outer,
            text=self.player_name,
            font=(FONT, 13, "bold"),
            bg=PANEL,
            fg=NEON_CYAN
        ).pack(
            pady=(0, 14)
        )

        # ----------------------------------------------------
        # Summary
        # ----------------------------------------------------

        summary = self.frame3d(
            outer,
            BG2,
            14,
            10
        )

        summary.pack(
            fill="x",
            pady=5
        )

        for label, value, color in [

            (
                "FINAL SCORE",
                self.score,
                NEON_CYAN
            ),

            (
                "HIGH SCORE",
                self.high_score,
                NEON_YELLOW
            ),

            (
                "LEVEL",
                self.level,
                NEON_PURPLE
            ),

            (
                "LINES",
                self.lines,
                NEON_GREEN
            ),
        ]:

            row = tk.Frame(
                summary,
                bg=BG2
            )

            row.pack(
                fill="x",
                pady=2
            )

            tk.Label(
                row,
                text=label,
                font=(FONT, 10, "bold"),
                bg=BG2,
                fg=MUTED,
                width=16,
                anchor="w"
            ).pack(
                side="left"
            )

            tk.Label(
                row,
                text=str(value),
                font=(FONT, 13, "bold"),
                bg=BG2,
                fg=color,
                anchor="e"
            ).pack(
                side="right"
            )

        # ----------------------------------------------------
        # High Score Message
        # ----------------------------------------------------

        if (
            self.score >= self.high_score
            and self.score > 0
        ):

            tk.Label(
                outer,
                text="★ NEW HIGH SCORE! ★",
                font=(FONT, 15, "bold"),
                bg=PANEL,
                fg=NEON_YELLOW
            ).pack(
                pady=6
            )

        # ----------------------------------------------------
        # Buttons
        # ----------------------------------------------------

        self.button3d(
            outer,
            "↻  RESTART GAME",
            self.reset_current_game,
            24
        ).pack(
            fill="x",
            pady=(8, 4)
        )

        self.button3d(
            outer,
            "⌂  HOME",
            self.go_home,
            24
        ).pack(
            fill="x",
            pady=4
        )

        self.celebrate_high_score()

    # ========================================================
    # HIGH SCORE ANIMATION
    # ========================================================

    def celebrate_high_score(self):

        if (
            self.score <= 0
            or self.score < self.high_score
        ):
            return

        if not hasattr(
            self,
            "canvas"
        ):
            return

        colors = [
            NEON_CYAN,
            NEON_PINK,
            NEON_YELLOW,
            NEON_PURPLE,
            NEON_GREEN
        ]

        def pulse(i=0):

            if (
                i >= 10
                or self.game_over is False
            ):

                try:
                    self.canvas.delete(
                        "highscore_fx"
                    )
                except tk.TclError:
                    pass

                return

            try:

                self.canvas.delete(
                    "highscore_fx"
                )

                color = colors[
                    i % len(colors)
                ]

                self.canvas.create_rectangle(
                    3,
                    3,
                    BOARD_WIDTH - 3,
                    BOARD_HEIGHT - 3,
                    outline=color,
                    width=6,
                    tags="highscore_fx"
                )

                self.canvas.create_text(
                    BOARD_WIDTH / 2,
                    42,
                    text="★ NEW HIGH SCORE! ★",
                    font=(FONT, 16, "bold"),
                    fill=color,
                    tags="highscore_fx"
                )

                self.canvas.update()

                self.root.after(
                    180,
                    lambda: pulse(i + 1)
                )

            except tk.TclError:
                return

        pulse()

    # ========================================================
    # MENU
    # ========================================================

    def toggle_menu(self):

        if getattr(
            self,
            "menu_overlay",
            None
        ) is not None:

            self.close_menu()

        else:

            self.open_menu()

    def open_menu(self):

        if self.game_over:
            return

        self.paused = True

        if self.fall_job:

            try:
                self.root.after_cancel(
                    self.fall_job
                )
            except tk.TclError:
                pass

            self.fall_job = None

        if getattr(
            self,
            "menu_overlay",
            None
        ) is not None:

            return

        self.menu_overlay = tk.Frame(
            self.root,
            bg=BG2,
            relief="raised",
            bd=7,
            highlightthickness=3,
            highlightbackground=NEON_CYAN,
        )

        self.menu_overlay.place(
            relx=0.5,
            rely=0.5,
            anchor="center",
            relwidth=0.38,
            relheight=0.55
        )

        inner = self.frame3d(
            self.menu_overlay,
            PANEL,
            18,
            18
        )

        inner.pack(
            fill="both",
            expand=True,
            padx=8,
            pady=8
        )

        tk.Label(
            inner,
            text="GAME MENU",
            font=(FONT, 20, "bold"),
            bg=PANEL,
            fg=NEON_CYAN
        ).pack(
            pady=(10, 18)
        )

        for text, command in [

            (
                "▶  RESUME",
                self.resume_game
            ),

            (
                "↻  RESTART",
                self.reset_current_game
            ),

            (
                "⌂  HOME",
                self.go_home
            ),

            (
                "✕  QUIT",
                self.quit_game
            ),
        ]:

            btn = self.button3d(
                inner,
                text,
                command,
                18
            )

            btn.pack(
                fill="x",
                pady=6,
                padx=12
            )

    def close_menu(self):

        overlay = getattr(
            self,
            "menu_overlay",
            None
        )

        if overlay is not None:

            try:
                overlay.destroy()
            except tk.TclError:
                pass

        self.menu_overlay = None

    def pause_game(self):

        if not self.game_over:

            self.paused = True

            self.close_menu()

            self.draw()

    def resume_game(self):

        if not self.game_over:

            self.paused = False

            self.close_menu()

            self.draw()

            self.schedule_fall()

    # ========================================================
    # HOME / QUIT
    # ========================================================

    def go_home(self):

        # ----------------------------------------------------
        # Save current game
        # ----------------------------------------------------

        if (
            self.score > 0
            and not self.score_saved
        ):

            self.save_finished_game()

        # ----------------------------------------------------
        # Stop all timers BEFORE destroying screen
        # ----------------------------------------------------

        self.cancel_jobs()

        self.close_menu()

        # ----------------------------------------------------
        # IMPORTANT:
        # Reload database leaderboard.
        # ----------------------------------------------------

        if hasattr(self, "db"):

            self.high_score = (
                self.db.get_high_score()
            )

        self.create_home_screen()

    def quit_game(self):

        self.save_finished_game()

        self.cancel_jobs()

        self.close_menu()

        if hasattr(
            self,
            "db"
        ):

            self.db.close()

        self.root.destroy()

    # ========================================================
    # SAVE GAME
    # ========================================================

    def save_finished_game(self):

        if self.score_saved:
            return

        self.score_saved = True

        if self.score <= 0:
            return

        result = {

            "name": (
                self.player_name
                or "PLAYER"
            ),

            "score": self.score,

            "level": self.level,

            "lines": self.lines,
        }

        # ----------------------------------------------------
        # Session history
        # ----------------------------------------------------

        self.session_scores.append(
            result
        )

        self.session_scores.sort(
            key=lambda item: item["score"],
            reverse=True
        )

        # ----------------------------------------------------
        # MySQL permanent history
        # ----------------------------------------------------

        if hasattr(
            self,
            "db"
        ):

            saved = self.db.save_game(
                result["name"],
                result["score"],
                result["level"],
                result["lines"]
            )

            if saved:

                self.high_score = max(
                    self.high_score,
                    result["score"]
                )

                print(
                    "[DATABASE] "
                    "Permanent leaderboard updated."
                )

    # ========================================================
    # LEADERBOARD
    # ========================================================

    def refresh_leaderboard(self):

        if not hasattr(
            self,
            "leaderboard_frame"
        ):
            return

        # ----------------------------------------------------
        # CLEAR CURRENT ROWS
        # ----------------------------------------------------

        for widget in (
            self.leaderboard_frame
            .winfo_children()
        ):

            widget.destroy()

        # ----------------------------------------------------
        # READ DATABASE
        # ----------------------------------------------------

        database_scores = []

        if hasattr(
            self,
            "db"
        ):

            database_scores = (
                self.db.get_all_scores()
            )

        # ----------------------------------------------------
        # DATABASE EMPTY
        # ----------------------------------------------------

        if not database_scores:

            tk.Label(
                self.leaderboard_frame,
                text=(
                    "🏆\n\n"
                    "NO SCORES YET\n\n"
                    "BE THE FIRST CHAMPION!"
                ),
                font=(FONT, 14, "bold"),
                bg=PANEL,
                fg=MUTED,
                justify="center"
            ).pack(
                pady=100
            )

            return

        # ----------------------------------------------------
        # DISPLAY DATABASE RECORDS
        # ----------------------------------------------------

        for rank, result in enumerate(
            database_scores,
            1
        ):

            player = (
                result.get(
                    "player_name",
                    "PLAYER"
                )
                or "PLAYER"
            )

            score = result.get(
                "score",
                0
            )

            level = result.get(
                "level",
                1
            )

            lines = result.get(
                "line_count",
                0
            )

            # ------------------------------------------------
            # TOP 3 ICON
            # ------------------------------------------------

            if rank == 1:

                medal = "🥇"
                row_bg = "#4A3A16"
                rank_color = GOLD
                score_color = GOLD
                row_font = 12

            elif rank == 2:

                medal = "🥈"
                row_bg = "#343840"
                rank_color = SILVER
                score_color = SILVER
                row_font = 11

            elif rank == 3:

                medal = "🥉"
                row_bg = "#49301E"
                rank_color = BRONZE
                score_color = BRONZE
                row_font = 11

            else:

                medal = ""
                row_bg = (
                    PANEL2
                    if rank % 2 == 0
                    else PANEL
                )

                rank_color = MUTED
                score_color = NEON_CYAN
                row_font = 10

            # ------------------------------------------------
            # ROW
            # ------------------------------------------------

            row = tk.Frame(
                self.leaderboard_frame,
                bg=row_bg,
                relief="raised",
                bd=3
            )

            row.pack(
                fill="x",
                pady=2,
                padx=2
            )

            # ------------------------------------------------
            # RANK
            # ------------------------------------------------

            rank_text = (
                f"{medal} {rank}"
                if rank <= 3
                else str(rank)
            )

            tk.Label(
                row,
                text=rank_text,
                width=8,
                font=(
                    FONT,
                    row_font,
                    "bold"
                ),
                bg=row_bg,
                fg=rank_color
            ).pack(
                side="left",
                padx=3,
                pady=7
            )

            # ------------------------------------------------
            # PLAYER
            # ------------------------------------------------

            tk.Label(
                row,
                text=player[:20],
                width=20,
                font=(
                    FONT,
                    row_font,
                    "bold"
                ),
                bg=row_bg,
                fg=(
                    NEON_YELLOW
                    if rank == 1
                    else WHITE
                ),
                anchor="w"
            ).pack(
                side="left",
                padx=3,
                pady=7
            )

            # ------------------------------------------------
            # SCORE
            # ------------------------------------------------

            tk.Label(
                row,
                text=f"{score:,}",
                width=14,
                font=(
                    FONT,
                    row_font + (
                        4 if rank == 1
                        else 1
                    ),
                    "bold"
                ),
                bg=row_bg,
                fg=score_color
            ).pack(
                side="left",
                padx=3,
                pady=7
            )

            # ------------------------------------------------
            # LEVEL
            # ------------------------------------------------

            tk.Label(
                row,
                text=str(level),
                width=9,
                font=(
                    FONT,
                    row_font,
                    "bold"
                ),
                bg=row_bg,
                fg=NEON_PURPLE
            ).pack(
                side="left",
                padx=3,
                pady=7
            )

            # ------------------------------------------------
            # LINES
            # ------------------------------------------------

            tk.Label(
                row,
                text=str(lines),
                width=9,
                font=(
                    FONT,
                    row_font,
                    "bold"
                ),
                bg=row_bg,
                fg=NEON_GREEN
            ).pack(
                side="left",
                padx=3,
                pady=7
            )

            # ------------------------------------------------
            # SPECIAL CHAMPION LABEL
            # ------------------------------------------------

            if rank == 1:

                tk.Label(
                    row,
                    text="  CHAMPION",
                    font=(
                        FONT,
                        9,
                        "bold"
                    ),
                    bg=row_bg,
                    fg=NEON_YELLOW
                ).pack(
                    side="right",
                    padx=8
                )

        # ----------------------------------------------------
        # UPDATE SCROLL
        # ----------------------------------------------------

        self.leaderboard_frame.update_idletasks()

        self.leaderboard_canvas.configure(
            scrollregion=(
                self.leaderboard_canvas
                .bbox("all")
            )
        )

        self.leaderboard_canvas.yview_moveto(
            0
        )

        # ----------------------------------------------------
        # UPDATE HIGH SCORE
        # ----------------------------------------------------

        if database_scores:

            highest = database_scores[0]

            self.high_score = int(
                highest.get(
                    "score",
                    0
                )
            )

        if hasattr(
            self,
            "home_high_label"
        ):

            self.home_high_label.config(
                text=str(self.high_score)
            )

    # ========================================================
    # CLEANUP
    # ========================================================

    def cancel_jobs(self):

        if self.fall_job:

            try:

                self.root.after_cancel(
                    self.fall_job
                )

            except tk.TclError:
                pass

            self.fall_job = None

        if self.speed_job:

            try:

                self.root.after_cancel(
                    self.speed_job
                )

            except tk.TclError:
                pass

            self.speed_job = None


# ============================================================
# RUN GAME
# ============================================================

if __name__ == "__main__":

    root = tk.Tk()

    game = BlockMaster(root)

    root.mainloop()