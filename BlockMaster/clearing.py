import time


class ClearingSystem:
    """
    BlockMaster clearing engine.

    Normal clear:
      - 10 x 23 board
      - a row clears when 9/10 cells are occupied
      - removed rows use normal Tetris gravity

    Special clear:
      - special opportunities are checked no more than once every 25 seconds
      - 10-filled-row event is also rate-limited to 25 seconds
      - two consecutive qualifying rows can trigger the special event
      - special effects only remove cells explicitly selected by the effect
      - no special effect modifies the active/next piece

    Animation is performed BEFORE the board is mutated.
    """

    SPECIAL_INTERVAL = 25.0
    ANIMATION_MS = 850

    def __init__(self, game):
        self.game = game
        self.last_special_time = None
        self.special_armed = False

    def can_special(self):
        # No special combination is permitted during the first
        # 30 seconds of a game. After the first special occurs,
        # another special window opens every 25 seconds.
        start = getattr(self.game, "game_start_time", None)
        if not start:
            return False

        elapsed = time.monotonic() - start

        if self.last_special_time is None:
            return elapsed >= 30.0

        return (time.monotonic() - self.last_special_time) >= self.SPECIAL_INTERVAL

    def resolve(self, shape_index, block_row, block_col, block):
        board = self.game.board
        rows = len(board)
        cols = len(board[0])

        # Snapshot the board before doing anything. This prevents
        # an animation callback from accidentally operating on a
        # subsequently spawned piece.
        snapshot = [row[:] for row in board]

        qualifying_rows = [
            r for r in range(rows)
            if sum(snapshot[r]) >= 9
        ]

        # Consecutive qualifying rows are a special combination.
        consecutive_pair = any(
            qualifying_rows[i + 1] == qualifying_rows[i] + 1
            for i in range(len(qualifying_rows) - 1)
        )

        special_cells = set()
        special_message = ""
        special_points = 0

        if self.can_special():
            # A 10/10 row is a timed special event.
            full_rows = [
                r for r in qualifying_rows
                if sum(snapshot[r]) == cols
            ]

            if full_rows:
                special_cells = {
                    (r, c)
                    for r in full_rows
                    for c in range(cols)
                }
                special_message = "PERFECT LINE BLAST!"
                special_points = 300
                self.last_special_time = time.monotonic()

            elif consecutive_pair:
                # Clear only the two qualifying rows and their
                # directly adjacent occupied cells. Nothing above
                # this controlled area is randomly removed.
                pair = None
                for i in range(len(qualifying_rows) - 1):
                    if qualifying_rows[i + 1] == qualifying_rows[i] + 1:
                        pair = (
                            qualifying_rows[i],
                            qualifying_rows[i + 1],
                        )
                        break

                if pair:
                    for r in pair:
                        for c in range(cols):
                            if snapshot[r][c]:
                                special_cells.add((r, c))

                    for r in (
                        max(0, pair[0] - 1),
                        min(rows - 1, pair[1] + 1),
                    ):
                        for c in range(cols):
                            if snapshot[r][c]:
                                special_cells.add((r, c))

                    special_message = "DOUBLE ROW COMBO!"
                    special_points = 250
                    self.last_special_time = time.monotonic()

            else:
                # First priority: a shape that fits tightly into an
                # existing pocket can trigger a massive neighboring
                # blast. This is intentionally rare and only works
                # during a special window.
                (
                    special_cells,
                    special_message,
                    special_points,
                ) = self.perfect_fit_blast(
                    shape_index,
                    block_row,
                    block_col,
                    block,
                    snapshot,
                )

                # Otherwise use the shape's normal special pattern.
                if not special_cells:
                    (
                        special_cells,
                        special_message,
                        special_points,
                    ) = self.detect_shape_blast(
                        shape_index,
                        block_row,
                        block_col,
                        block,
                        snapshot,
                    )

                if special_cells:
                    self.last_special_time = time.monotonic()

        # Normal row clear is always allowed at 9/10.
        # However, if a special event already contains those rows,
        # don't run a second conflicting clear.
        all_cells = set(special_cells)

        normal_rows = []
        for r in qualifying_rows:
            if not any((r, c) in all_cells for c in range(cols)):
                normal_rows.append(r)

        for r in normal_rows:
            for c in range(cols):
                if snapshot[r][c]:
                    all_cells.add((r, c))

        if not all_cells:
            return {
                "cleared": False,
                "rows": 0,
                "special_cells": 0,
                "score": 0,
                "message": "",
            }

        # Visible animation is blocking for this short duration.
        self.animate_cells(all_cells)

        # Mutate the board ONLY after animation.
        special_removed = self.remove_cells(special_cells)

        # Recalculate qualifying rows on the current board.
        # This prevents stale coordinates from removing unintended
        # rows after a special effect.
        current_qualifying = [
            r for r in range(rows)
            if sum(self.game.board[r]) >= 9
        ]

        row_count = len(current_qualifying)

        if current_qualifying:
            self.remove_rows(current_qualifying)

        row_scores = {
            1: 100,
            2: 225,
            3: 400,
            4: 650,
        }

        score = row_scores.get(
            row_count,
            650 + max(0, row_count - 4) * 150,
        ) if row_count else 0

        score += special_points

        if special_message and row_count:
            message = f"{special_message} + ROW CLEAR!"
        elif special_message:
            message = special_message
        elif row_count == 4:
            message = "TETRIS!"
        elif row_count == 3:
            message = "TRIPLE CLEAR!"
        elif row_count == 2:
            message = "DOUBLE CLEAR!"
        elif row_count == 1:
            message = "ROW CLEAR!"
        else:
            message = "CLEAR!"

        return {
            "cleared": True,
            "rows": row_count,
            "special_cells": special_removed,
            "score": score,
            "message": message,
        }

    def remove_rows(self, rows):
        board = self.game.board
        colors = self.game.board_colors
        removed = set(rows)

        remaining_board = []
        remaining_colors = []

        for r in range(len(board)):
            if r not in removed:
                remaining_board.append(board[r][:])
                remaining_colors.append(colors[r][:])

        empty_count = len(board) - len(remaining_board)

        self.game.board = (
            [[0] * len(board[0]) for _ in range(empty_count)]
            + remaining_board
        )
        self.game.board_colors = (
            [[None] * len(board[0]) for _ in range(empty_count)]
            + remaining_colors
        )

    def remove_cells(self, cells):
        removed = 0

        for r, c in cells:
            if (
                0 <= r < len(self.game.board)
                and 0 <= c < len(self.game.board[0])
                and self.game.board[r][c]
            ):
                self.game.board[r][c] = 0
                self.game.board_colors[r][c] = None
                removed += 1

        return removed

    def perfect_fit_blast(self, row_shape_index, row, col, block, board):
        rows = len(board)
        cols = len(board[0])

        occupied_shape = []
        for r, line in enumerate(block):
            for c, value in enumerate(line):
                if value:
                    occupied_shape.append((row + r, col + c))

        if not occupied_shape:
            return set(), "", 0

        # Count the occupied cells immediately surrounding the
        # shape's bounding box. A high perimeter fill means the
        # piece has landed in a tight pocket.
        min_r = min(r for r, c in occupied_shape)
        max_r = max(r for r, c in occupied_shape)
        min_c = min(c for r, c in occupied_shape)
        max_c = max(c for r, c in occupied_shape)

        perimeter = set()
        for c in range(min_c - 1, max_c + 2):
            perimeter.add((min_r - 1, c))
            perimeter.add((max_r + 1, c))
        for r in range(min_r, max_r + 1):
            perimeter.add((r, min_c - 1))
            perimeter.add((r, max_c + 1))

        valid_perimeter = {
            (r, c) for r, c in perimeter
            if 0 <= r < rows and 0 <= c < cols
        }
        filled = sum(
            1 for r, c in valid_perimeter if board[r][c]
        )

        # Require a genuinely tight fit, not just one neighboring block.
        if len(valid_perimeter) < 4 or filled / len(valid_perimeter) < 0.70:
            return set(), "", 0

        # Massive but controlled neighboring blast: up to a 5x5 area
        # centered on the shape. It does NOT affect unrelated distant rows.
        blast = set()
        center_r = (min_r + max_r) // 2
        center_c = (min_c + max_c) // 2

        for r in range(max(0, center_r - 2), min(rows, center_r + 3)):
            for c in range(max(0, center_c - 2), min(cols, center_c + 3)):
                if board[r][c]:
                    blast.add((r, c))

        if len(blast) >= 7:
            return blast, "PERFECT FIT MEGA BLAST!", 350

        return set(), "", 0

    def detect_shape_blast(
        self, shape_index, row, col, block, board
    ):
        if shape_index == 0:
            return self.i_blast(row, col, block, board)

        if shape_index == 1:
            return self.o_blast(row, col, board)

        if shape_index == 2:
            return self.t_blast(row, col, board)

        if shape_index in (3, 4):
            return self.corner_blast(row, col, block, board)

        if shape_index in (5, 6):
            return self.chain_blast(row, col, board)

        return set(), "", 0

    def i_blast(self, row, col, block, board):
        height = len(block)
        width = len(block[0])
        cols = len(board[0])

        if width == 4 and height == 1 and 0 <= row < len(board):
            if sum(board[row]) >= 6:
                return {
                    (row, c) for c in range(cols) if board[row][c]
                }, "I-LINE BLAST!", 180

        if height == 4 and width == 1 and 0 <= col < cols:
            if sum(board[r][col] for r in range(len(board))) >= 6:
                return {
                    (r, col)
                    for r in range(len(board))
                    if board[r][col]
                }, "I-COLUMN BLAST!", 180

        return set(), "", 0

    def o_blast(self, row, col, board):
        cells = set()

        for r in range(max(0, row - 1), min(len(board), row + 3)):
            for c in range(
                max(0, col - 1),
                min(len(board[0]), col + 3),
            ):
                if board[r][c]:
                    cells.add((r, c))

        if len(cells) >= 6:
            return set(list(cells)[:9]), "SQUARE BLAST!", 140

        return set(), "", 0

    def t_blast(self, row, col, board):
        center_r = row + 1
        center_c = col + 1

        cross = {
            (center_r, center_c),
            (center_r - 1, center_c),
            (center_r + 1, center_c),
            (center_r, center_c - 1),
            (center_r, center_c + 1),
        }

        occupied = {
            p for p in cross
            if 0 <= p[0] < len(board)
            and 0 <= p[1] < len(board[0])
            and board[p[0]][p[1]]
        }

        if len(occupied) >= 4:
            return occupied, "T-CROSS BLAST!", 160

        return set(), "", 0

    def corner_blast(self, row, col, block, board):
        cells = set()

        for r in range(
            max(0, row - 1),
            min(len(board), row + len(block)),
        ):
            for c in range(
                max(0, col - 1),
                min(len(board[0]), col + len(block[0])),
            ):
                if board[r][c]:
                    cells.add((r, c))

        if len(cells) >= 5:
            return set(list(cells)[:7]), "CORNER BLAST!", 130

        return set(), "", 0

    def chain_blast(self, row, col, board):
        cells = set()

        for r in range(
            max(0, row - 1),
            min(len(board), row + 4),
        ):
            for c in range(
                max(0, col - 1),
                min(len(board[0]), col + 4),
            ):
                if board[r][c]:
                    cells.add((r, c))

        if len(cells) >= 5:
            return set(list(cells)[:6]), "CHAIN BLAST!", 150

        return set(), "", 0

    def animate_cells(self, cells):
        canvas = getattr(self.game, "canvas", None)

        if canvas is None:
            return

        cell_size = getattr(self.game, "CELL_SIZE", 32)

        # Use a synchronous sequence so the game cannot spawn the
        # next piece while the current clear is still being shown.
        try:
            for phase in range(6):
                canvas.delete("clear_fx")

                if phase % 2 == 0:
                    fill = "#FFFFFF"
                    outline = "#66FFFF"
                else:
                    fill = "#FF66CC"
                    outline = "#FFFFFF"

                for r, c in cells:
                    x1 = c * cell_size + 2
                    y1 = r * cell_size + 2
                    x2 = (c + 1) * cell_size - 2
                    y2 = (r + 1) * cell_size - 2

                    canvas.create_rectangle(
                        x1, y1, x2, y2,
                        fill=fill,
                        outline=outline,
                        width=4,
                        tags="clear_fx",
                    )

                canvas.update()
                canvas.after(140)

            canvas.delete("clear_fx")
            canvas.update()

        except Exception:
            canvas.delete("clear_fx")
