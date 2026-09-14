import tkinter as tk
import random
import time
from clearing import ClearingSystem


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

# Speed decreases by 200 ms every 20 seconds.
# It bottoms out at a playable 300 ms.
THREE_MINUTES = 180_000

LEVEL_SCORE = 500  # Score required per level; deliberately slower progression

# Neon arcade palette
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

BLOCK_COLORS = [
    "#42DDF0",  # I
    "#FFE66D",  # O
    "#B98CFF",  # T
    "#FF9A62",  # L
    "#FF718B",  # J
    "#75F7A8",  # S
    "#FF67D9",  # Z
]

FONT = "Consolas"


class BlockMaster:
    def __init__(self, root):
        self.root = root
        self.root.title("BlockMaster - Neon Arcade")
        self.root.geometry("1100x920")
        self.root.resizable(True, True)
        self.root.minsize(900, 760)
        self.root.configure(bg=BG)

        self.shapes = [
            [[1, 1, 1, 1]],                         # I
            [[1, 1], [1, 1]],                       # O
            [[1, 1, 1], [0, 1, 0]],                 # T
            [[1, 0], [1, 0], [1, 1]],               # L
            [[0, 1], [0, 1], [1, 1]],               # J
            [[0, 1, 1], [1, 1, 0]],                 # S
            [[1, 1, 0], [0, 1, 1]],                 # Z
        ]

        self.shape_names = ["I", "O", "T", "L", "J", "S", "Z"]

        self.player_name = ""
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

        self.menu_window = None
        self.menu_overlay = None
        self.fall_job = None
        self.speed_job = None

        self.session_scores = []

        self.current_block = None
        self.current_shape_index = 0
        self.current_color = BLOCK_COLORS[0]

        self.next_block = random.choice(self.shapes)
        self.next_shape_index = self.shapes.index(self.next_block)
        self.next_color = BLOCK_COLORS[self.next_shape_index]

        self.block_row = 0
        self.block_col = 0

        self.board = []
        self.board_colors = []

        self.CELL_SIZE = CELL_SIZE
        self.clearer = ClearingSystem(self)

        self.create_home_screen()

    # --------------------------------------------------------
    # GENERAL UI
    # --------------------------------------------------------

    def clear_root(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def frame3d(self, parent, bg=PANEL, padx=12, pady=12):
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

    def button3d(self, parent, text, command, width=18):
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

    # --------------------------------------------------------
    # HOME
    # --------------------------------------------------------

    def create_home_screen(self):
        self.cancel_jobs()
        self.close_menu()
        self.clear_root()

        root_box = tk.Frame(self.root, bg=BG)
        root_box.pack(fill="both", expand=True, padx=28, pady=24)

        title = self.frame3d(root_box, BG2, 25, 18)
        title.pack(fill="x", pady=(0, 18))

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
        ).pack(pady=(5, 0))

        content = tk.Frame(root_box, bg=BG)
        content.pack(fill="both", expand=True)

        # LEFT
        left = tk.Frame(content, bg=BG)
        left.pack(side="left", fill="y", padx=(0, 16))

        player_box = self.frame3d(left, PANEL)
        player_box.pack(fill="x", pady=6)

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
        self.name_entry.insert(0, "PLAYER")
        self.name_entry.pack(pady=12, ipady=8)

        start = self.button3d(left, "▶  START GAME", self.start_game, 22)
        start.pack(fill="x", pady=8)

        controls = self.frame3d(left, BG2)
        controls.pack(fill="x", pady=6)

        tk.Label(
            controls,
            text="CONTROLS",
            font=(FONT, 11, "bold"),
            bg=BG2,
            fg=NEON_PINK,
        ).pack(pady=(0, 8))

        tk.Label(
            controls,
            text="← →   MOVE\n↑ ↓   ROTATE\nSPACE   HARD DROP\n\n9+ FILLED CELLS = ROW CLEAR\nSPECIAL SHAPES = BLASTS",
            font=(FONT, 9, "bold"),
            bg=BG2,
            fg=MUTED,
            justify="center",
        ).pack()

        # RIGHT
        right = tk.Frame(content, bg=BG)
        right.pack(side="left", fill="both", expand=True)

        board_info = self.frame3d(right, PANEL)
        board_info.pack(fill="both", expand=True)

        tk.Label(
            board_info,
            text="🏆  SESSION LEADERBOARD",
            font=(FONT, 13, "bold"),
            bg=PANEL,
            fg=NEON_YELLOW,
        ).pack(pady=(0, 10))

        header = tk.Frame(board_info, bg=PANEL3, relief="raised", bd=3)
        header.pack(fill="x")

        for text, width in [("RANK", 7), ("PLAYER", 18), ("SCORE", 10)]:
            tk.Label(
                header,
                text=text,
                width=width,
                font=(FONT, 9, "bold"),
                bg=PANEL3,
                fg=WHITE,
            ).pack(side="left")

        self.leaderboard_frame = tk.Frame(board_info, bg=PANEL)
        self.leaderboard_frame.pack(fill="both", expand=True, pady=6)

        self.refresh_leaderboard()

        high = self.frame3d(right, BG2)
        high.pack(fill="x", pady=6)

        tk.Label(
            high,
            text="👑 ALL-TIME SESSION HIGH SCORE",
            font=(FONT, 9, "bold"),
            bg=BG2,
            fg=MUTED,
        ).pack()

        self.home_high_label = tk.Label(
            high,
            text=str(self.high_score),
            font=(FONT, 25, "bold"),
            bg=BG2,
            fg=NEON_CYAN,
        )
        self.home_high_label.pack(pady=4)

        tk.Label(
            root_box,
            text="NEON ARCADE EDITION  •  10 × 23 BOARD",
            font=(FONT, 8, "bold"),
            bg=BG,
            fg=MUTED,
        ).pack(pady=7)

        self.name_entry.focus_set()
        self.root.bind("<Return>", lambda e: self.start_game())

    # --------------------------------------------------------
    # START / RESET
    # --------------------------------------------------------

    def reset_state(self):
        self.close_menu()
        self.cancel_jobs()
        if getattr(self, "game_over_window", None):
            try:
                if self.game_over_window.winfo_exists():
                    self.game_over_window.grab_release()
                    self.game_over_window.destroy()
            except tk.TclError:
                pass
            self.game_over_window = None

        self.score = 0
        self.lines = 0
        self.level = 1
        self.combo = 0
        self.fall_speed = START_SPEED

        self.game_over = False
        self.paused = False
        self.countdown_active = False
        self.countdown_hidden = False
        self.score_saved = False
        self.lock_in_progress = False

        self.board = [[0 for _ in range(COLS)] for _ in range(ROWS)]
        self.board_colors = [[None for _ in range(COLS)] for _ in range(ROWS)]

        self.current_block = None
        self.next_block = random.choice(self.shapes)
        self.next_shape_index = self.shapes.index(self.next_block)
        self.next_color = BLOCK_COLORS[self.next_shape_index]

    def start_game(self):
        name = self.name_entry.get().strip()
        self.player_name = name.upper() if name else "PLAYER"

        self.reset_state()
        self.create_game_screen()

        self.spawn_block()
        if self.game_over:
            self.draw()
            return

        # Hide the active piece during the countdown.
        self.countdown_hidden = True
        self.draw()
        self.start_countdown()

    def reset_current_game(self):
        if not hasattr(self, "name_entry"):
            self.player_name = self.player_name or "PLAYER"

        self.reset_state()
        self.create_game_screen()
        self.spawn_block()
        self.draw()

        if not self.game_over:
            self.start_countdown()

    # --------------------------------------------------------
    # GAME SCREEN
    # --------------------------------------------------------

    def create_game_screen(self):
        self.close_menu()
        self.clear_root()

        top = tk.Frame(self.root, bg=BG)
        top.pack(fill="x", padx=18, pady=(12, 8))

        player = self.frame3d(top, BG2, 14, 8)
        player.pack(side="left", fill="x", expand=True, padx=(0, 8))

        tk.Label(
            player,
            text=self.player_name,
            font=(FONT, 13, "bold"),
            bg=BG2,
            fg=NEON_CYAN,
        ).pack()

        self.menu_button = self.button3d(top, "☰  MENU", self.toggle_menu, 12)
        self.menu_button.pack(side="left")

        game_area = tk.Frame(self.root, bg=BG)
        game_area.pack(fill="both", expand=True, padx=18, pady=4)

        # Center the board by using a fixed left spacer.
        spacer = tk.Frame(game_area, bg=BG, width=180)
        spacer.pack(side="left", fill="y")
        spacer.pack_propagate(False)

        board_box = self.frame3d(game_area, BG2, 9, 9)
        board_box.pack(side="left", anchor="n")

        self.canvas = tk.Canvas(
            board_box,
            width=BOARD_WIDTH,
            height=BOARD_HEIGHT,
            bg=BOARD_BG,
            highlightthickness=3,
            highlightbackground=NEON_PURPLE,
        )
        self.canvas.pack()

        side = tk.Frame(game_area, bg=BG, width=250)
        side.pack(side="left", fill="y", padx=(18, 0))
        side.pack_propagate(False)

        self.score_value = self.make_stat(side, "SCORE", "0")
        self.high_value = self.make_stat(side, "HIGH SCORE", str(self.high_score))
        self.level_value = self.make_stat(side, "LEVEL", "1")

        next_box = self.frame3d(side, PANEL)
        next_box.pack(fill="x", pady=6)

        tk.Label(
            next_box,
            text="NEXT BLOCK",
            font=(FONT, 10, "bold"),
            bg=PANEL,
            fg=NEON_PINK,
        ).pack(pady=(0, 7))

        self.next_canvas = tk.Canvas(
            next_box,
            width=190,
            height=115,
            bg=BOARD_BG,
            highlightthickness=2,
            highlightbackground=PANEL3,
        )
        self.next_canvas.pack()

        combo_box = self.frame3d(side, BG2)
        combo_box.pack(fill="x", pady=6)

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
            text="← → MOVE     ↑ ↓ ROTATE     SPACE HARD DROP",
            font=(FONT, 9, "bold"),
            bg=BG,
            fg=MUTED,
        ).pack(pady=7)

        self.root.bind("<Left>", self.move_left)
        self.root.bind("<Right>", self.move_right)
        self.root.bind("<Up>", self.rotate_block)
        self.root.bind("<Down>", self.rotate_block)
        self.root.bind("<space>", self.hard_drop)

    def make_stat(self, parent, title, value):
        box = self.frame3d(parent, PANEL)
        box.pack(fill="x", pady=5)

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
        value_label.pack(pady=3)

        return value_label

    # --------------------------------------------------------
    # COUNTDOWN
    # --------------------------------------------------------

    def start_countdown(self):
        self.countdown_active = True
        self.countdown_value = 3
        self.show_countdown()

    def show_countdown(self):
        if not self.countdown_active or self.game_over:
            return

        self.draw()

        cx = BOARD_WIDTH / 2
        cy = BOARD_HEIGHT / 2

        self.canvas.create_rectangle(
            cx - 125, cy - 90,
            cx + 125, cy + 90,
            fill=BG2,
            outline=NEON_CYAN,
            width=5,
        )

        if self.countdown_value > 0:
            text = str(self.countdown_value)
            self.countdown_value -= 1
            delay = 700
        else:
            text = "GO!"
            delay = 450

        self.canvas.create_text(
            cx,
            cy,
            text=text,
            font=(FONT, 58 if text != "GO!" else 38, "bold"),
            fill=NEON_PINK if text != "GO!" else NEON_GREEN,
        )

        if text == "GO!":
            self.root.after(delay, self.finish_countdown)
        else:
            self.root.after(delay, self.show_countdown)

    def finish_countdown(self):
        self.countdown_active = False
        self.countdown_hidden = False
        self.game_start_time = time.monotonic()
        self.start_speed_timer()
        self.draw()
        self.schedule_fall()

    # --------------------------------------------------------
    # SPEED
    # --------------------------------------------------------

    def start_speed_timer(self):
        if self.speed_job:
            self.root.after_cancel(self.speed_job)
        self.speed_job = self.root.after(250, self.update_time_speed)

    def update_time_speed(self):
        if self.game_over:
            return

        if not self.paused and not self.countdown_active and self.game_start_time:
            elapsed_ms = int((time.monotonic() - self.game_start_time) * 1000)

            steps = elapsed_ms // SPEED_INTERVAL
            self.fall_speed = max(
                MIN_SPEED,
                START_SPEED - steps * SPEED_STEP
            )

        self.speed_job = self.root.after(250, self.update_time_speed)

    def schedule_fall(self):
        if self.fall_job:
            self.root.after_cancel(self.fall_job)

        if not self.game_over and not self.paused and not self.countdown_active:
            self.fall_job = self.root.after(self.fall_speed, self.fall)

    # --------------------------------------------------------
    # SPAWN
    # --------------------------------------------------------

    def spawn_block(self):
        if self.current_block is None:
            self.current_block = random.choice(self.shapes)
            self.current_shape_index = self.shapes.index(self.current_block)
            self.current_color = BLOCK_COLORS[self.current_shape_index]
        else:
            self.current_block = [row[:] for row in self.next_block]
            self.current_shape_index = self.next_shape_index
            self.current_color = self.next_color

        self.next_block = random.choice(self.shapes)
        self.next_shape_index = self.shapes.index(self.next_block)
        self.next_color = BLOCK_COLORS[self.next_shape_index]

        self.block_row = 0
        self.block_col = (COLS - len(self.current_block[0])) // 2

        if not self.can_place(
            self.current_block,
            self.block_row,
            self.block_col
        ):
            self.game_over = True
            self.save_finished_game()

    # --------------------------------------------------------
    # COLLISION / MOVEMENT
    # --------------------------------------------------------

    def can_place(self, block, row, col):
        for r, line in enumerate(block):
            for c, value in enumerate(line):
                if not value:
                    continue

                br = row + r
                bc = col + c

                if br < 0 or br >= ROWS or bc < 0 or bc >= COLS:
                    return False

                if self.board[br][bc]:
                    return False

        return True

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

    # --------------------------------------------------------
    # ROTATION
    # --------------------------------------------------------

    def rotate_matrix(self, block):
        return [list(row) for row in zip(*block[::-1])]

    def rotate_block(self, event=None):
        if self.blocked_input():
            return

        rotated = self.rotate_matrix(self.current_block)

        # Simple wall-kick attempts.
        for offset in (0, -1, 1, -2, 2):
            if self.can_place(
                rotated,
                self.block_row,
                self.block_col + offset
            ):
                self.current_block = rotated
                self.block_col += offset
                break

        self.draw()

    # --------------------------------------------------------
    # LOCK / CLEAR
    # --------------------------------------------------------

    def lock_block(self):
        cells = 0

        for r, line in enumerate(self.current_block):
            for c, value in enumerate(line):
                if value:
                    br = self.block_row + r
                    bc = self.block_col + c

                    if 0 <= br < ROWS and 0 <= bc < COLS:
                        self.board[br][bc] = 1
                        self.board_colors[br][bc] = self.current_color
                        cells += 1

        # Small placement reward; the main score comes from
        # clears, combos, and special combinations.
        self.score += cells
        self.update_level()

    def process_lock(self):
        # HARD GUARD: only one lock may be processed at a time.
        # This prevents an animation/fall callback from spawning
        # two pieces and apparently skipping the next shape.
        if self.lock_in_progress or self.game_over:
            return

        self.lock_in_progress = True

        # Cancel any already scheduled fall callback. Hard-drop and
        # automatic fall must never be allowed to call process_lock
        # again while the current clear animation is running.
        if self.fall_job:
            try:
                self.root.after_cancel(self.fall_job)
            except tk.TclError:
                pass
            self.fall_job = None

        # Snapshot the current piece BEFORE any board effect.
        locked_shape_index = self.current_shape_index
        locked_row = self.block_row
        locked_col = self.block_col
        locked_block = [row[:] for row in self.current_block]

        self.lock_block()

        # Hide the old active piece while the clearing system resolves.
        self.current_block = None
        self.draw()

        result = self.clearer.resolve(
            locked_shape_index,
            locked_row,
            locked_col,
            locked_block,
        )

        if result["cleared"]:
            self.lines += result.get("rows", 0)
            self.combo += 1

            combo_bonus = self.combo * 35
            earned = result["score"] + combo_bonus
            self.score += earned

            self.show_combo(result["message"], earned)
        else:
            self.combo = 0

        self.update_level()

        # IMPORTANT: exactly one spawn, after the clear is completely
        # finished. The next-block queue is therefore advanced once.
        if not self.game_over:
            self.spawn_block()

        self.lock_in_progress = False
        self.draw()


    # --------------------------------------------------------
    # FALL / HARD DROP
    # --------------------------------------------------------

    def fall(self):
        self.fall_job = None

        if self.game_over or self.paused or self.countdown_active or self.lock_in_progress:
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

    def hard_drop(self, event=None):
        if self.blocked_input() or self.lock_in_progress:
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

    # --------------------------------------------------------
    # SCORE / LEVEL
    # --------------------------------------------------------

    def update_level(self):
        self.level = (self.score // LEVEL_SCORE) + 1

        if self.score > self.high_score:
            self.high_score = self.score

        if hasattr(self, "score_value"):
            self.score_value.config(text=str(self.score))
            self.high_value.config(text=str(self.high_score))
            self.level_value.config(text=str(self.level))
            self.combo_value.config(text=f"x{self.combo}")

    # --------------------------------------------------------
    # COMBO INDICATOR
    # --------------------------------------------------------

    def show_combo(self, message, points):
        if not hasattr(self, "canvas"):
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
            lambda: self.canvas.delete("combo_fx")
            if hasattr(self, "canvas") else None
        )

    # --------------------------------------------------------
    # DRAW
    # --------------------------------------------------------

    def draw(self):
        if not hasattr(self, "canvas"):
            return

        self.canvas.delete("all")

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

        # Locked blocks
        for r in range(ROWS):
            for c in range(COLS):
                if self.board[r][c]:
                    self.draw_3d_block(
                        self.canvas,
                        c * CELL_SIZE,
                        r * CELL_SIZE,
                        self.board_colors[r][c],
                    )

        # Current block
        if (
            self.current_block is not None
            and not self.game_over
            and not self.countdown_hidden
        ):
            for r, line in enumerate(self.current_block):
                for c, value in enumerate(line):
                    if value:
                        self.draw_3d_block(
                            self.canvas,
                            (self.block_col + c) * CELL_SIZE,
                            (self.block_row + r) * CELL_SIZE,
                            self.current_color,
                        )

        self.draw_next_shape()

        if self.paused and not self.game_over:
            self.draw_center_overlay("PAUSED", NEON_YELLOW)

        if self.game_over:
            self.draw_game_over()

        self.update_level()

    def draw_3d_block(self, canvas, x, y, color, size=CELL_SIZE):
        # Outer glow
        canvas.create_rectangle(
            x + 1, y + 1,
            x + size - 1, y + size - 1,
            outline=color,
            width=2,
        )

        # Main face
        canvas.create_rectangle(
            x + 4, y + 4,
            x + size - 4, y + size - 4,
            fill=color,
            outline="#0B0912",
            width=2,
        )

        # Bright top
        canvas.create_polygon(
            x + 5, y + 5,
            x + size - 5, y + 5,
            x + size - 9, y + 9,
            x + 9, y + 9,
            fill="#FFFFFF",
            outline="",
        )

        # Left bevel
        canvas.create_polygon(
            x + 5, y + 5,
            x + 9, y + 9,
            x + 9, y + size - 9,
            x + 5, y + size - 5,
            fill="#D8D5E6",
            outline="",
        )

        # Bottom bevel
        canvas.create_polygon(
            x + 5, y + size - 5,
            x + size - 5, y + size - 5,
            x + size - 9, y + size - 9,
            x + 9, y + size - 9,
            fill="#5D5870",
            outline="",
        )

        # Right bevel
        canvas.create_polygon(
            x + size - 5, y + 5,
            x + size - 9, y + 9,
            x + size - 9, y + size - 9,
            x + size - 5, y + size - 5,
            fill="#716B85",
            outline="",
        )

    def draw_next_shape(self):
        if not hasattr(self, "next_canvas"):
            return

        self.next_canvas.delete("all")

        block = self.next_block
        cell = 24

        rows = len(block)
        cols = len(block[0])

        start_x = (190 - cols * cell) / 2
        start_y = (115 - rows * cell) / 2

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

    # --------------------------------------------------------
    # OVERLAYS
    # --------------------------------------------------------

    def draw_center_overlay(self, title, color):
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

    def draw_game_over(self):
        # Keep the board clean and show a proper arcade-style popup.
        self.canvas.create_rectangle(
            0, 0, BOARD_WIDTH, BOARD_HEIGHT,
            fill="#110E19", outline="", tags="gameover_dim"
        )

        if getattr(self, "game_over_window", None):
            try:
                if self.game_over_window.winfo_exists():
                    return
            except tk.TclError:
                pass

        self.game_over_window = tk.Toplevel(self.root)
        self.game_over_window.title("BlockMaster - Game Over")
        self.game_over_window.configure(bg=BG)
        self.game_over_window.resizable(False, False)
        self.game_over_window.transient(self.root)
        self.game_over_window.grab_set()

        width, height = 500, 470
        self.root.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() - width) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - height) // 2
        self.game_over_window.geometry(f"{width}x{height}+{x}+{y}")

        outer = self.frame3d(self.game_over_window, BG2, 24, 24)
        outer.pack(fill="both", expand=True, padx=14, pady=14)

        tk.Label(
            outer, text="GAME OVER",
            font=(FONT, 28, "bold"), bg=BG2, fg=NEON_PINK
        ).pack(pady=(8, 3))

        tk.Label(
            outer, text=self.player_name,
            font=(FONT, 13, "bold"), bg=BG2, fg=NEON_CYAN
        ).pack(pady=(0, 18))

        summary = self.frame3d(outer, PANEL, 15, 12)
        summary.pack(fill="x", pady=6)

        for label, value, color in [
            ("FINAL SCORE", self.score, NEON_CYAN),
            ("HIGH SCORE", self.high_score, NEON_YELLOW),
            ("LEVEL", self.level, NEON_PURPLE),
            ("LINES", self.lines, NEON_GREEN),
        ]:
            row = tk.Frame(summary, bg=PANEL)
            row.pack(fill="x", pady=3)
            tk.Label(row, text=label, font=(FONT, 10, "bold"),
                     bg=PANEL, fg=MUTED, width=16, anchor="w").pack(side="left")
            tk.Label(row, text=str(value), font=(FONT, 13, "bold"),
                     bg=PANEL, fg=color, anchor="e").pack(side="right")

        if self.score >= self.high_score and self.score > 0:
            tk.Label(
                outer, text="★ NEW HIGH SCORE! ★",
                font=(FONT, 15, "bold"), bg=BG2, fg=NEON_YELLOW
            ).pack(pady=8)

        restart = self.button3d(
            outer, "↻  RESTART GAME", self.reset_current_game, 24
        )
        restart.pack(fill="x", pady=(12, 5))

        home = self.button3d(
            outer, "⌂  HOME", self.go_home, 24
        )
        home.pack(fill="x", pady=5)

        self.game_over_window.protocol(
            "WM_DELETE_WINDOW", self.reset_current_game
        )

        self.celebrate_high_score()

    def celebrate_high_score(self):
        if self.score <= 0 or self.score < self.high_score:
            return

        if not hasattr(self, "canvas"):
            return

        # Lightweight neon celebration around the board.
        colors = [NEON_CYAN, NEON_PINK, NEON_YELLOW, NEON_PURPLE, NEON_GREEN]

        def pulse(i=0):
            if not hasattr(self, "canvas"):
                return
            if i >= 8:
                self.canvas.delete("highscore_fx")
                return
            self.canvas.delete("highscore_fx")
            color = colors[i % len(colors)]
            self.canvas.create_rectangle(
                3, 3, BOARD_WIDTH - 3, BOARD_HEIGHT - 3,
                outline=color, width=6, tags="highscore_fx"
            )
            self.canvas.create_text(
                BOARD_WIDTH / 2, 42,
                text="★ NEW HIGH SCORE! ★",
                font=(FONT, 16, "bold"),
                fill=color, tags="highscore_fx"
            )
            self.canvas.update()
            self.root.after(180, lambda: pulse(i + 1))

        pulse()

    # --------------------------------------------------------
    # MENU POPUP
    # --------------------------------------------------------

    def toggle_menu(self):
        if getattr(self, "menu_overlay", None) is not None:
            self.close_menu()
        else:
            self.open_menu()

    def open_menu(self):
        if self.game_over:
            return

        # Menu opens as an overlay INSIDE the game window.
        self.paused = True
        if self.fall_job:
            try:
                self.root.after_cancel(self.fall_job)
            except tk.TclError:
                pass
            self.fall_job = None

        if getattr(self, "menu_overlay", None) is not None:
            return

        self.menu_overlay = tk.Frame(
            self.root,
            bg=BG2,
            relief="raised",
            bd=7,
            highlightthickness=3,
            highlightbackground=NEON_CYAN,
        )
        self.menu_overlay.place(relx=0.5, rely=0.5, anchor="center",
                                relwidth=0.38, relheight=0.55)

        inner = self.frame3d(self.menu_overlay, PANEL, 18, 18)
        inner.pack(fill="both", expand=True, padx=8, pady=8)

        tk.Label(
            inner, text="GAME MENU", font=(FONT, 20, "bold"),
            bg=PANEL, fg=NEON_CYAN
        ).pack(pady=(10, 18))

        for text, command in [
            ("▶  RESUME", self.resume_game),
            ("↻  RESTART", self.reset_current_game),
            ("⌂  HOME", self.go_home),
            ("✕  QUIT", self.quit_game),
        ]:
            btn = self.button3d(inner, text, command, 18)
            btn.pack(fill="x", pady=6, padx=12)

    def close_menu(self):
        overlay = getattr(self, "menu_overlay", None)
        if overlay is not None:
            try:
                overlay.destroy()
            except tk.TclError:
                pass
        self.menu_overlay = None

    def pause_game(self):
        # Kept for compatibility with any existing callback, but the
        # visible menu no longer exposes a Pause button.
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


    # --------------------------------------------------------
    # HOME / QUIT
    # --------------------------------------------------------

    def go_home(self):
        if self.score > 0 and not self.score_saved:
            self.save_finished_game()

        self.close_menu()
        self.create_home_screen()

    def quit_game(self):
        self.save_finished_game()
        self.cancel_jobs()
        self.close_menu()
        self.root.destroy()

    # --------------------------------------------------------
    # LEADERBOARD
    # --------------------------------------------------------

    def save_finished_game(self):
        if self.score_saved:
            return

        self.score_saved = True

        if self.score <= 0:
            return

        self.session_scores.append({
            "name": self.player_name or "PLAYER",
            "score": self.score,
        })

        self.session_scores.sort(
            key=lambda item: item["score"],
            reverse=True,
        )

    def refresh_leaderboard(self):
        if not hasattr(self, "leaderboard_frame"):
            return

        for widget in self.leaderboard_frame.winfo_children():
            widget.destroy()

        if not self.session_scores:
            tk.Label(
                self.leaderboard_frame,
                text="NO SCORES YET\n\nSTART A GAME!",
                font=(FONT, 11, "bold"),
                bg=PANEL,
                fg=MUTED,
                justify="center",
            ).pack(pady=65)
            return

        for rank, result in enumerate(self.session_scores[:10], 1):
            bg = PANEL2 if rank % 2 == 0 else PANEL

            row = tk.Frame(
                self.leaderboard_frame,
                bg=bg,
                relief="raised",
                bd=2,
            )
            row.pack(fill="x", pady=2)

            tk.Label(
                row,
                text=str(rank),
                width=7,
                font=(FONT, 9, "bold"),
                bg=bg,
                fg=MUTED,
            ).pack(side="left")

            tk.Label(
                row,
                text=result["name"][:16],
                width=18,
                font=(FONT, 9, "bold"),
                bg=bg,
                fg=WHITE,
            ).pack(side="left")

            tk.Label(
                row,
                text=str(result["score"]),
                width=10,
                font=(FONT, 9, "bold"),
                bg=bg,
                fg=NEON_CYAN,
            ).pack(side="left")

        if hasattr(self, "home_high_label"):
            self.home_high_label.config(text=str(self.high_score))

    # --------------------------------------------------------
    # CLEANUP
    # --------------------------------------------------------

    def cancel_jobs(self):
        if self.fall_job:
            try:
                self.root.after_cancel(self.fall_job)
            except tk.TclError:
                pass
            self.fall_job = None

        if self.speed_job:
            try:
                self.root.after_cancel(self.speed_job)
            except tk.TclError:
                pass
            self.speed_job = None


if __name__ == "__main__":
    root = tk.Tk()
    game = BlockMaster(root)
    root.mainloop()
