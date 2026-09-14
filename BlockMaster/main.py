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
# FONT
# ============================================================

# Public Pixel must be installed in Windows.
# If it is not installed, Tkinter will automatically fall back
# to the fallback font defined below.
FONT = "Public Pixel"
FALLBACK_FONT = "Consolas"


# ============================================================
# NEON ARCADE PALETTE
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

# Leaderboard colors
LEADERBOARD_BG = "#19152A"
LEADERBOARD_ROW = "#25203B"
LEADERBOARD_ROW_ALT = "#2C2547"
LEADERBOARD_HEADER = "#41345F"

BLOCK_COLORS = [
    "#42DDF0",  # I
    "#FFE66D",  # O
    "#B98CFF",  # T
    "#FF9A62",  # L
    "#FF718B",  # J
    "#75F7A8",  # S
    "#FF67D9",  # Z
]


class BlockMaster:

    def __init__(self, root):

        self.root = root

        self.root.title("BlockMaster - Neon Arcade")
        self.root.geometry("1150x920")
        self.root.resizable(True, True)
        self.root.minsize(950, 760)
        self.root.configure(bg=BG)

        # ====================================================
        # SHAPES
        # ====================================================

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

        # ====================================================
        # PLAYER / SCORE STATE
        # ====================================================

        self.player_name = ""

        self.score = 0
        self.high_score = 0
        self.level = 1
        self.lines = 0
        self.combo = 0

        # ====================================================
        # TIMING
        # ====================================================

        self.fall_speed = START_SPEED
        self.game_start_time = None

        # ====================================================
        # GAME STATE
        # ====================================================

        self.game_over = False
        self.paused = False
        self.countdown_active = False
        self.countdown_hidden = False
        self.score_saved = False
        self.lock_in_progress = False

        # ====================================================
        # TKINTER JOBS
        # ====================================================

        self.menu_window = None
        self.menu_overlay = None
        self.game_over_overlay = None

        self.fall_job = None
        self.speed_job = None

        # ====================================================
        # SESSION SCORES
        # ====================================================

        self.session_scores = []

        # ====================================================
        # CURRENT BLOCK
        # ====================================================

        self.current_block = None
        self.current_shape_index = 0
        self.current_color = BLOCK_COLORS[0]

        self.next_block = random.choice(self.shapes)
        self.next_shape_index = self.shapes.index(self.next_block)
        self.next_color = BLOCK_COLORS[self.next_shape_index]

        self.block_row = 0
        self.block_col = 0

        # ====================================================
        # BOARD
        # ====================================================

        self.board = []
        self.board_colors = []

        self.CELL_SIZE = CELL_SIZE

        # ====================================================
        # CLEARING SYSTEM
        # ====================================================

        self.clearer = ClearingSystem(self)

        # ====================================================
        # DATABASE
        # ====================================================

        self.db = DatabaseManager()

        # Load database high score.
        self.high_score = self.db.get_high_score()

        # ====================================================
        # START HOME SCREEN
        # ====================================================

        self.create_home_screen()

    # ========================================================
    # FONT HELPERS
    # ========================================================

    def arcade_font(self, size, bold=False):

        """
        Returns Public Pixel font.

        If Public Pixel is unavailable, Consolas is used.
        """

        try:
            families = self.root.tk.call("font", "families")

            if FONT in families:
                return (FONT, size, "bold" if bold else "normal")

        except tk.TclError:
            pass

        return (
            FALLBACK_FONT,
            size,
            "bold" if bold else "normal"
        )

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
            font=self.arcade_font(9, True),
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

        # Destroy overlays BEFORE rebuilding home.
        self.close_menu()

        if getattr(self, "game_over_overlay", None):

            try:
                self.game_over_overlay.destroy()

            except tk.TclError:
                pass

            self.game_over_overlay = None

        # Refresh database high score.
        self.high_score = self.db.get_high_score()

        self.clear_root()

        root_box = tk.Frame(
            self.root,
            bg=BG
        )

        root_box.pack(
            fill="both",
            expand=True,
            padx=24,
            pady=20
        )

        # ====================================================
        # TITLE
        # ====================================================

        title = self.frame3d(
            root_box,
            BG2,
            25,
            16
        )

        title.pack(
            fill="x",
            pady=(0, 15)
        )

        tk.Label(
            title,
            text="B L O C K M A S T E R",
            font=self.arcade_font(25, True),
            bg=BG2,
            fg=NEON_CYAN,
        ).pack()

        tk.Label(
            title,
            text="N E O N   A R C A D E",
            font=self.arcade_font(9, True),
            bg=BG2,
            fg=NEON_PINK,
        ).pack(pady=(8, 0))

        # ====================================================
        # MAIN CONTENT
        # ====================================================

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
            padx=(0, 16)
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
            pady=6
        )

        tk.Label(
            player_box,
            text="ENTER PLAYER",
            font=self.arcade_font(9, True),
            bg=PANEL,
            fg=NEON_CYAN,
        ).pack()

        self.name_entry = tk.Entry(
            player_box,
            width=18,
            font=self.arcade_font(11, True),
            justify="center",
            bg=BOARD_BG,
            fg=WHITE,
            insertbackground=NEON_CYAN,
            relief="sunken",
            bd=5,
        )

        self.name_entry.insert(
            0,
            "PLAYER"
        )

        self.name_entry.pack(
            pady=12,
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
            pady=8
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
            pady=6
        )

        tk.Label(
            controls,
            text="CONTROLS",
            font=self.arcade_font(10, True),
            bg=BG2,
            fg=NEON_PINK,
        ).pack(
            pady=(0, 10)
        )

        tk.Label(
            controls,
            text=(
                "← →   MOVE\n"
                "↑ ↓   ROTATE\n"
                "SPACE   HARD DROP\n\n"
                "9+ FILLED CELLS = ROW CLEAR\n"
                "SPECIAL SHAPES = BLASTS"
            ),
            font=self.arcade_font(7, True),
            bg=BG2,
            fg=MUTED,
            justify="center",
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

        # ====================================================
        # LEADERBOARD BOX
        # ====================================================

        board_info = self.frame3d(
            right,
            LEADERBOARD_BG,
            12,
            12
        )

        board_info.pack(
            fill="both",
            expand=True
        )

        # ----------------------------------------------------
        # TITLE
        # ----------------------------------------------------

        tk.Label(
            board_info,
            text="★  HIGH SCORE TABLE  ★",
            font=self.arcade_font(14, True),
            bg=LEADERBOARD_BG,
            fg=NEON_YELLOW,
        ).pack(
            pady=(0, 10)
        )

        tk.Label(
            board_info,
            text="ALL RECORDED GAMES",
            font=self.arcade_font(7, True),
            bg=LEADERBOARD_BG,
            fg=MUTED,
        ).pack(
            pady=(0, 12)
        )

        # ----------------------------------------------------
        # HEADER
        # ----------------------------------------------------

        header = tk.Frame(
            board_info,
            bg=LEADERBOARD_HEADER,
            relief="raised",
            bd=3
        )

        header.pack(
            fill="x",
            padx=3
        )

        header_columns = [
            ("RANK", 9),
            ("PLAYER", 25),
            ("SCORE", 15),
        ]

        for text, width in header_columns:

            tk.Label(
                header,
                text=text,
                width=width,
                font=self.arcade_font(8, True),
                bg=LEADERBOARD_HEADER,
                fg=WHITE,
                anchor="center",
            ).pack(
                side="left",
                expand=True,
                fill="x"
            )

        # ----------------------------------------------------
        # SCROLLABLE LEADERBOARD
        # ----------------------------------------------------

        leaderboard_container = tk.Frame(
            board_info,
            bg=LEADERBOARD_BG
        )

        leaderboard_container.pack(
            fill="both",
            expand=True,
            pady=7
        )

        self.leaderboard_canvas = tk.Canvas(
            leaderboard_container,
            bg=LEADERBOARD_BG,
            highlightthickness=0
        )

        self.leaderboard_scrollbar = tk.Scrollbar(
            leaderboard_container,
            orient="vertical",
            command=self.leaderboard_canvas.yview
        )

        self.leaderboard_canvas.configure(
            yscrollcommand=self.leaderboard_scrollbar.set
        )

        self.leaderboard_scrollbar.pack(
            side="right",
            fill="y"
        )

        self.leaderboard_canvas.pack(
            side="left",
            fill="both",
            expand=True
        )

        self.leaderboard_frame = tk.Frame(
            self.leaderboard_canvas,
            bg=LEADERBOARD_BG
        )

        self.leaderboard_window = (
            self.leaderboard_canvas.create_window(
                (0, 0),
                window=self.leaderboard_frame,
                anchor="nw"
            )
        )

        self.leaderboard_frame.bind(
            "<Configure>",
            lambda event: self.leaderboard_canvas.configure(
                scrollregion=self.leaderboard_canvas.bbox("all")
            )
        )

        self.leaderboard_canvas.bind(
            "<Configure>",
            self.resize_leaderboard
        )

        # Mouse wheel
        self.leaderboard_canvas.bind_all(
            "<MouseWheel>",
            self.leaderboard_mousewheel
        )

        # ----------------------------------------------------
        # REFRESH DATABASE LEADERBOARD
        # ----------------------------------------------------

        self.refresh_leaderboard()

        # ====================================================
        # ALL TIME HIGH SCORE
        # ====================================================

        high = self.frame3d(
            right,
            BG2
        )

        high.pack(
            fill="x",
            pady=7
        )

        tk.Label(
            high,
            text="★  ALL-TIME HIGH SCORE  ★",
            font=self.arcade_font(8, True),
            bg=BG2,
            fg=MUTED,
        ).pack()

        self.home_high_label = tk.Label(
            high,
            text=str(self.high_score),
            font=self.arcade_font(23, True),
            bg=BG2,
            fg=NEON_CYAN,
        )

        self.home_high_label.pack(
            pady=5
        )

        # ====================================================
        # FOOTER
        # ====================================================

        tk.Label(
            root_box,
            text="NEON ARCADE EDITION  •  10 × 23 BOARD",
            font=self.arcade_font(7, True),
            bg=BG,
            fg=MUTED,
        ).pack(
            pady=6
        )

        self.name_entry.focus_set()

        self.root.bind(
            "<Return>",
            lambda event: self.start_game()
        )

    # ========================================================
    # LEADERBOARD RESIZE
    # ========================================================

    def resize_leaderboard(self, event):

        try:

            self.leaderboard_canvas.itemconfig(
                self.leaderboard_window,
                width=event.width
            )

        except tk.TclError:
            pass

    def leaderboard_mousewheel(self, event):

        try:

            self.leaderboard_canvas.yview_scroll(
                int(-1 * (event.delta / 120)),
                "units"
            )

        except tk.TclError:
            pass

    # ========================================================
    # START / RESET
    # ========================================================

    def reset_state(self):

        # Remove overlays FIRST.
        self.close_menu()

        if getattr(self, "game_over_overlay", None):

            try:
                self.game_over_overlay.destroy()

            except tk.TclError:
                pass

            self.game_over_overlay = None

        # Cancel all scheduled jobs.
        self.cancel_jobs()

        # ====================================================
        # RESET GAME DATA
        # ====================================================

        self.score = 0
        self.lines = 0
        self.level = 1
        self.combo = 0

        self.fall_speed = START_SPEED
        self.game_start_time = None

        # ====================================================
        # RESET FLAGS
        # ====================================================

        self.game_over = False
        self.paused = False
        self.countdown_active = False
        self.countdown_hidden = False
        self.score_saved = False
        self.lock_in_progress = False

        # ====================================================
        # RESET BOARD
        # ====================================================

        self.board = [
            [0 for _ in range(COLS)]
            for _ in range(ROWS)
        ]

        self.board_colors = [
            [None for _ in range(COLS)]
            for _ in range(ROWS)
        ]

        # ====================================================
        # RESET PIECES
        # ====================================================

        self.current_block = None

        self.next_block = random.choice(
            self.shapes
        )

        self.next_shape_index = (
            self.shapes.index(self.next_block)
        )

        self.next_color = (
            BLOCK_COLORS[self.next_shape_index]
        )

        self.block_row = 0
        self.block_col = 0

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

        # Hide current piece during countdown.
        self.countdown_hidden = True

        self.draw()

        self.start_countdown()

    def reset_current_game(self):

        # Preserve player name.
        if not self.player_name:

            if hasattr(self, "name_entry"):

                self.player_name = (
                    self.name_entry.get().strip().upper()
                    or "PLAYER"
                )

            else:

                self.player_name = "PLAYER"

        # ====================================================
        # IMPORTANT FIX:
        #
        # Completely destroy the old game screen and overlay.
        # This prevents old pieces from remaining visible when
        # restarting after GAME OVER.
        # ====================================================

        self.cancel_jobs()

        self.close_menu()

        if getattr(self, "game_over_overlay", None):

            try:
                self.game_over_overlay.destroy()

            except tk.TclError:
                pass

            self.game_over_overlay = None

        self.reset_state()

        self.create_game_screen()

        self.spawn_block()

        if self.game_over:

            self.draw()

            return

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
            font=self.arcade_font(11, True),
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

        # ====================================================
        # GAME AREA
        # ====================================================

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

        # ====================================================
        # LEFT SPACER
        # ====================================================

        spacer = tk.Frame(
            game_area,
            bg=BG,
            width=150
        )

        spacer.pack(
            side="left",
            fill="y"
        )

        spacer.pack_propagate(False)

        # ====================================================
        # BOARD
        # ====================================================

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

        # ====================================================
        # SIDE PANEL
        # ====================================================

        side = tk.Frame(
            game_area,
            bg=BG,
            width=260
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

        # ====================================================
        # NEXT BLOCK
        # ====================================================

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
            font=self.arcade_font(8, True),
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

        # ====================================================
        # COMBO
        # ====================================================

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
            font=self.arcade_font(8, True),
            bg=BG2,
            fg=MUTED,
        ).pack()

        self.combo_value = tk.Label(
            combo_box,
            text="x0",
            font=self.arcade_font(16, True),
            bg=BG2,
            fg=NEON_YELLOW,
        )

        self.combo_value.pack()

        # ====================================================
        # CONTROL FOOTER
        # ====================================================

        tk.Label(
            self.root,
            text=(
                "← → MOVE     "
                "↑ ↓ ROTATE     "
                "SPACE HARD DROP"
            ),
            font=self.arcade_font(7, True),
            bg=BG,
            fg=MUTED,
        ).pack(
            pady=7
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
    # STATS
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
            font=self.arcade_font(7, True),
            bg=PANEL,
            fg=MUTED,
        ).pack()

        value_label = tk.Label(
            box,
            text=value,
            font=self.arcade_font(16, True),
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
            font=self.arcade_font(
                42 if text != "GO!" else 30,
                True
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

        self.countdown_active = False
        self.countdown_hidden = False

        self.game_start_time = (
            time.monotonic()
        )

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
            and not self.lock_in_progress
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

        # Generate next block.
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

        # ====================================================
        # GAME OVER
        # ====================================================

        if not self.can_place(
            self.current_block,
            self.block_row,
            self.block_col
        ):

            self.game_over = True

            self.cancel_jobs()

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
            for row in zip(*block[::-1])
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
    # LOCK BLOCK - ACTUAL IMPLEMENTATION
    # ========================================================

    def lock_block(self):

        cells = 0

        for r, line in enumerate(
            self.current_block
        ):

            for c, value in enumerate(line):

                if value:

                    br = (
                        self.block_row + r
                    )

                    bc = (
                        self.block_col + c
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

        # Cancel fall callback.
        if self.fall_job:

            try:
                self.root.after_cancel(
                    self.fall_job
                )

            except tk.TclError:
                pass

            self.fall_job = None

        # Snapshot current piece.
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

        # Hide active piece.
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

        # Spawn exactly one block.
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

        if (
            self.blocked_input()
            or self.lock_in_progress
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
            font=self.arcade_font(
                13,
                True
            ),
            fill=NEON_YELLOW,
            tags="combo_fx",
        )

        self.canvas.create_text(
            cx,
            y + 30,
            text=f"+{points}",
            font=self.arcade_font(
                9,
                True
            ),
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

        try:

            self.canvas.delete("all")

        except tk.TclError:

            return

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

        # ----------------------------------------------------
        # NEXT PIECE
        # ----------------------------------------------------

        self.draw_next_shape()

        # ----------------------------------------------------
        # PAUSE
        # ----------------------------------------------------

        if (
            self.paused
            and not self.game_over
        ):

            self.draw_center_overlay(
                "PAUSED",
                NEON_YELLOW
            )

        # ----------------------------------------------------
        # GAME OVER
        # ----------------------------------------------------

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

        # Outer glow
        canvas.create_rectangle(
            x + 1,
            y + 1,
            x + size - 1,
            y + size - 1,
            outline=color,
            width=2,
        )

        # Main face
        canvas.create_rectangle(
            x + 4,
            y + 4,
            x + size - 4,
            y + size - 4,
            fill=color,
            outline="#0B0912",
            width=2,
        )

        # Bright top
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

        # Left bevel
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

        # Bottom bevel
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

        # Right bevel
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

        self.next_canvas.delete(
            "all"
        )

        block = self.next_block

        cell = 24

        rows = len(block)
        cols = len(block[0])

        start_x = (
            190 - cols * cell
        ) / 2

        start_y = (
            115 - rows * cell
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
            font=self.arcade_font(
                22,
                True
            ),
            fill=color,
        )

    # ========================================================
    # GAME OVER
    # ========================================================

    def draw_game_over(self):

        """
        Game-over window.

        The old overlay is destroyed before a new game starts,
        preventing old board pieces from remaining visible.
        """

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

        # Dim board.
        self.canvas.create_rectangle(
            0,
            0,
            BOARD_WIDTH,
            BOARD_HEIGHT,
            fill="#110E19",
            outline="",
            tags="gameover_dim"
        )

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
            font=self.arcade_font(
                22,
                True
            ),
            bg=PANEL,
            fg=NEON_PINK
        ).pack(
            pady=(8, 2)
        )

        tk.Label(
            outer,
            text=self.player_name,
            font=self.arcade_font(
                10,
                True
            ),
            bg=PANEL,
            fg=NEON_CYAN
        ).pack(
            pady=(0, 14)
        )

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
                pady=3
            )

            tk.Label(
                row,
                text=label,
                font=self.arcade_font(
                    7,
                    True
                ),
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
                font=self.arcade_font(
                    10,
                    True
                ),
                bg=BG2,
                fg=color,
                anchor="e"
            ).pack(
                side="right"
            )

        # New high score.
        if (
            self.score >= self.high_score
            and self.score > 0
        ):

            tk.Label(
                outer,
                text="★ NEW HIGH SCORE! ★",
                font=self.arcade_font(
                    11,
                    True
                ),
                bg=PANEL,
                fg=NEON_YELLOW
            ).pack(
                pady=6
            )

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
                or not hasattr(
                    self,
                    "canvas"
                )
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
                    font=self.arcade_font(
                        11,
                        True
                    ),
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
            font=self.arcade_font(
                16,
                True
            ),
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

        # Save current game if necessary.
        if (
            self.score > 0
            and not self.score_saved
        ):

            self.save_finished_game()

        # Cancel game jobs.
        self.cancel_jobs()

        self.close_menu()

        # IMPORTANT:
        # Remove game-over overlay before home.
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

        # Rebuild home screen.
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

            "name":
                self.player_name
                or "PLAYER",

            "score":
                self.score,

            "level":
                self.level,

            "lines":
                self.lines,
        }

        # ----------------------------------------------------
        # SESSION RECORD
        # ----------------------------------------------------

        self.session_scores.append(
            result
        )

        self.session_scores.sort(
            key=lambda item:
                item["score"],
            reverse=True
        )

        # ----------------------------------------------------
        # DATABASE RECORD
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

    # ========================================================
    # DATABASE LEADERBOARD
    # ========================================================

    def refresh_leaderboard(self):

        if not hasattr(
            self,
            "leaderboard_frame"
        ):

            return

        # ----------------------------------------------------
        # CLEAR OLD ROWS
        # ----------------------------------------------------

        for widget in (
            self.leaderboard_frame.winfo_children()
        ):

            widget.destroy()

        # ----------------------------------------------------
        # GET DATABASE SCORES
        # ----------------------------------------------------

        database_scores = []

        try:

            database_scores = (
                self.db.get_top_scores(
                    100
                )
            )

        except Exception as error:

            print(
                "[DATABASE] "
                f"Leaderboard error: {error}"
            )

        # ----------------------------------------------------
        # FALLBACK TO SESSION SCORES
        # ----------------------------------------------------

        if not database_scores:

            database_scores = []

            for item in self.session_scores:

                database_scores.append({

                    "player_name":
                        item["name"],

                    "score":
                        item["score"],

                    "level":
                        item["level"],

                    "line_count":
                        item["lines"],

                })

        # ----------------------------------------------------
        # EMPTY
        # ----------------------------------------------------

        if not database_scores:

            tk.Label(
                self.leaderboard_frame,
                text=(
                    "NO SCORES YET\n\n"
                    "START A GAME!"
                ),
                font=self.arcade_font(
                    9,
                    True
                ),
                bg=LEADERBOARD_BG,
                fg=MUTED,
                justify="center",
            ).pack(
                pady=70
            )

            return

        # ----------------------------------------------------
        # RANKED ROWS
        # ----------------------------------------------------

        for rank, result in enumerate(
            database_scores,
            1
        ):

            # Same styling for EVERY row.
            row_bg = (
                LEADERBOARD_ROW
                if rank % 2 == 0
                else LEADERBOARD_ROW_ALT
            )

            row = tk.Frame(
                self.leaderboard_frame,
                bg=row_bg,
                relief="raised",
                bd=3,
                height=62,
            )

            row.pack(
                fill="x",
                padx=3,
                pady=3
            )

            row.pack_propagate(False)

            # =================================================
            # RANK / MEDAL
            # =================================================

            rank_frame = tk.Frame(
                row,
                bg=row_bg,
                width=95
            )

            rank_frame.pack(
                side="left",
                fill="y"
            )

            rank_frame.pack_propagate(False)

            # -------------------------------------------------
            # MEDALS ONLY TOP 3
            # -------------------------------------------------

            if rank == 1:

                icon = "🥇"

            elif rank == 2:

                icon = "🥈"

            elif rank == 3:

                icon = "🥉"

            else:

                icon = ""

            if icon:

                # Slightly larger than player text.
                tk.Label(
                    rank_frame,
                    text=icon,
                    font=("Segoe UI Emoji", 21),
                    bg=row_bg,
                    fg=WHITE,
                ).pack(
                    side="left",
                    padx=(5, 2)
                )

            # -------------------------------------------------
            # RANK NUMBER
            # -------------------------------------------------

            tk.Label(
                rank_frame,
                text=str(rank),
                font=self.arcade_font(
                    10,
                    True
                ),
                bg=row_bg,
                fg=WHITE,
                anchor="center",
            ).pack(
                side="left",
                expand=True
            )

            # =================================================
            # PLAYER
            # =================================================

            player_name = str(
                result.get(
                    "player_name",
                    result.get(
                        "name",
                        "PLAYER"
                    )
                )
            )

            player_name = (
                player_name[:18]
            )

            player_frame = tk.Frame(
                row,
                bg=row_bg
            )

            player_frame.pack(
                side="left",
                fill="both",
                expand=True
            )

            tk.Label(
                player_frame,
                text=player_name,
                font=self.arcade_font(
                    10,
                    True
                ),
                bg=row_bg,
                fg=WHITE,
                anchor="w",
            ).pack(
                fill="both",
                expand=True,
                padx=12
            )

            # =================================================
            # SCORE
            # =================================================

            score = int(
                result.get(
                    "score",
                    0
                )
            )

            score_frame = tk.Frame(
                row,
                bg=row_bg,
                width=150
            )

            score_frame.pack(
                side="left",
                fill="y"
            )

            score_frame.pack_propagate(False)

            tk.Label(
                score_frame,
                text=f"{score:,}",
                font=self.arcade_font(
                    10,
                    True
                ),
                bg=row_bg,
                fg=NEON_CYAN,
                anchor="center",
            ).pack(
                fill="both",
                expand=True
            )

        # ----------------------------------------------------
        # UPDATE SCROLL REGION
        # ----------------------------------------------------

        self.leaderboard_frame.update_idletasks()

        self.leaderboard_canvas.configure(
            scrollregion=(
                self.leaderboard_canvas.bbox(
                    "all"
                )
            )
        )

        # ----------------------------------------------------
        # REFRESH HIGH SCORE
        # ----------------------------------------------------

        try:

            self.high_score = (
                self.db.get_high_score()
            )

        except Exception:

            pass

        if hasattr(
            self,
            "home_high_label"
        ):

            self.home_high_label.config(
                text=f"{self.high_score:,}"
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

    game = BlockMaster(
        root
    )

    root.mainloop()