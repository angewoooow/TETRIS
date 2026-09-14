# BLOCKMASTER — PROJECT PROGRESS DOCUMENT

## Project Title

**BlockMaster: A Tetris-Inspired Puzzle Game with Player Progress Tracking System**

---

# 1. PROJECT PURPOSE

BlockMaster is a simplified Tetris-inspired desktop game being developed as a student project.

The goal is to create a functional, understandable, and presentable game using:

* Python
* Tkinter
* MySQL
* XAMPP
* VS Code

This is intentionally NOT a full Tetris clone.

The project should remain simple and beginner-friendly.

---

# 2. FINAL PLANNED FEATURES

The final project is planned to have:

## Gameplay

* 5 × 10 game board
* 3–4 block shapes
* Automatic falling
* Left Arrow = move left
* Right Arrow = move right
* Down Arrow = move down faster
* No block rotation
* Fixed falling speed
* Collision detection
* Block locking and stacking
* Row clearing
* Score system
* Game Over
* Restart

## Player System

* Player enters their name before playing
* Player name is associated with the game
* Final score is saved

## Database

MySQL database through XAMPP.

Database:

`blockmaster`

Table:

`scores`

Planned fields:

* id
* player_name
* score
* date_played

## High Scores

Display the top 10 scores ordered from highest to lowest.

---

# 3. DEVELOPMENT RULE

The project is being developed incrementally.

DO NOT build the entire project at once.

Each phase should be completed and tested before moving to the next.

Development order:

1. Environment Setup
2. Basic Tkinter Window
3. 5×10 Game Board
4. Block Spawning
5. Automatic Falling
6. Player Movement
7. Collision Detection
8. Block Locking & Stacking
9. Row Clearing
10. Score System
11. Game Over
12. Restart
13. Player Name
14. MySQL Connection
15. Save Scores
16. High Scores
17. UI Polish
18. Testing
19. Final Packaging

---

# 4. CURRENT PROGRESS

## PHASE 1 — Environment Setup

STATUS: ✅ COMPLETED

Python, VS Code, XAMPP, and the required development environment have been prepared.

---

## PHASE 2 — Basic Tkinter Window

STATUS: ✅ COMPLETED

A Tkinter application window was created for BlockMaster.

---

## PHASE 3 — 5×10 Game Board

STATUS: ✅ COMPLETED

The game has:

* 10 rows
* 5 columns
* 40px cells

Current constants:

```python
ROWS = 10
COLS = 5
CELL_SIZE = 40
```

---

## PHASE 4 — Block Spawning

STATUS: ✅ COMPLETED

The game randomly selects a block from the available shapes.

Current shapes:

### Square

```text
XX
XX
```

### I Block

```text
XXXX
```

### L Block

```text
X
X
XX
```

### T Block

```text
XXX
 X
```

---

## PHASE 5 — Automatic Falling

STATUS: ✅ COMPLETED

Blocks automatically move downward using Tkinter's `after()` method.

Current speed:

```python
FALL_SPEED = 500
```

This means the block attempts to move down every 500 milliseconds.

---

# PHASE 6 — Movement

STATUS: ✅ COMPLETED

Keyboard controls have been implemented.

Controls:

```text
← Left Arrow  = move left
→ Right Arrow = move right
↓ Down Arrow  = move down
```

Tkinter key bindings:

```python
self.root.bind("<Left>", self.move_left)
self.root.bind("<Right>", self.move_right)
self.root.bind("<Down>", self.move_down)
```

---

# PHASE 7 — Collision Detection

STATUS: ✅ COMPLETED

Collision detection now prevents the current falling block from:

* Leaving the left side
* Leaving the right side
* Falling below the board

A `can_move()` method was introduced.

It checks whether the current block can move to a proposed row/column position.

---

# PHASE 8 — BLOCK LOCKING & STACKING

STATUS: ✅ COMPLETED / CURRENTLY IMPLEMENTED

The game now has a permanent board that stores blocks after they can no longer move downward.

A permanent board was added:

```python
self.board = [
    [0 for _ in range(COLS)]
    for _ in range(ROWS)
]
```

A `lock_block()` method was added.

When the current block can no longer move downward:

1. The block is added to `self.board`
2. A new random block is generated
3. The new block starts at the top

Collision detection also checks against existing locked blocks.

---

# 5. CURRENT GAME STATE

At the current stage:

```text
              NEW BLOCK
                  ↓
             FALLING BLOCK
                  ↓
          ┌──────────────┐
          │ CAN MOVE?    │
          └──────┬───────┘
             YES │ NO
                 │
                 ↓
              LOCK
                 ↓
          NEW BLOCK SPAWNS
```

The board can now contain multiple locked blocks.

---

# 6. CURRENT LIMITATIONS

These are intentionally NOT implemented yet:

* ❌ Row clearing
* ❌ Score
* ❌ Game Over
* ❌ Restart
* ❌ Player name
* ❌ MySQL
* ❌ High scores
* ❌ Advanced UI
* ❌ Block rotation
* ❌ Levels
* ❌ Increasing difficulty

These will be implemented in later phases.

---

# 7. IMPORTANT CURRENT CODE

This is the CURRENT working `main.py`.

DO NOT replace or redesign this code unnecessarily.

Use this exact code as the baseline for future development.

```python
import tkinter as tk
import random

# Board settings
ROWS = 10
COLS = 5
CELL_SIZE = 40
FALL_SPEED = 500  # milliseconds


class BlockMaster:
    def __init__(self, root):
        self.root = root
        self.root.title("BlockMaster")

        self.frame = tk.Frame(root)
        self.frame.pack(padx=20, pady=20)

        self.title_label = tk.Label(
            self.frame,
            text="BLOCKMASTER",
            font=("Arial", 18, "bold")
        )
        self.title_label.pack(pady=10)

        self.canvas = tk.Canvas(
            self.frame,
            width=COLS * CELL_SIZE,
            height=ROWS * CELL_SIZE,
            bg="white"
        )
        self.canvas.pack()

        # Shapes
        self.shapes = [
            # Square
            [
                [1, 1],
                [1, 1]
            ],

            # I Block
            [
                [1, 1, 1, 1]
            ],

            # L Block
            [
                [1, 0],
                [1, 0],
                [1, 1]
            ],

            # T Block
            [
                [1, 1, 1],
                [0, 1, 0]
            ]
        ]

        # Permanent board
        self.board = [
            [0 for _ in range(COLS)]
            for _ in range(ROWS)
        ]

        # Spawn block
        self.current_block = random.choice(self.shapes)
        self.block_row = 0
        self.block_col = 1

        # Keyboard controls
        self.root.bind("<Left>", self.move_left)
        self.root.bind("<Right>", self.move_right)
        self.root.bind("<Down>", self.move_down)

        self.draw()

        # Start automatic falling
        self.fall()

    def draw(self):
        self.canvas.delete("all")

        # Draw board grid
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
                    outline="black"
                )

        # Draw locked blocks
        for row in range(ROWS):
            for col in range(COLS):

                if self.board[row][col] == 1:

                    x1 = col * CELL_SIZE
                    y1 = row * CELL_SIZE
                    x2 = x1 + CELL_SIZE
                    y2 = y1 + CELL_SIZE

                    self.canvas.create_rectangle(
                        x1,
                        y1,
                        x2,
                        y2,
                        fill="gray",
                        outline="black"
                    )

        # Draw current block
        for r in range(len(self.current_block)):
            for c in range(len(self.current_block[r])):

                if self.current_block[r][c] == 1:

                    x1 = (self.block_col + c) * CELL_SIZE
                    y1 = (self.block_row + r) * CELL_SIZE

                    x2 = x1 + CELL_SIZE
                    y2 = y1 + CELL_SIZE

                    self.canvas.create_rectangle(
                        x1,
                        y1,
                        x2,
                        y2,
                        fill="blue",
                        outline="black"
                    )

    def can_move(self, row_change, col_change):
        """
        Check if the current block can move
        to a new position.
        """

        new_row = self.block_row + row_change
        new_col = self.block_col + col_change

        for r in range(len(self.current_block)):
            for c in range(len(self.current_block[r])):

                if self.current_block[r][c] == 1:

                    board_row = new_row + r
                    board_col = new_col + c

                    # Check left and right boundaries
                    if board_col < 0 or board_col >= COLS:
                        return False

                    # Check top and bottom boundaries
                    if board_row < 0 or board_row >= ROWS:
                        return False

                    # Check collision with locked blocks
                    if self.board[board_row][board_col] == 1:
                        return False

        return True

    def move_left(self, event):
        if self.can_move(0, -1):
            self.block_col -= 1

        self.draw()

    def move_right(self, event):
        if self.can_move(0, 1):
            self.block_col += 1

        self.draw()

    def move_down(self, event):
        if self.can_move(1, 0):
            self.block_row += 1

        self.draw()

    def lock_block(self):
        """
        Place the current block permanently
        onto the board.
        """

        for r in range(len(self.current_block)):
            for c in range(len(self.current_block[r])):

                if self.current_block[r][c] == 1:

                    board_row = self.block_row + r
                    board_col = self.block_col + c

                    self.board[board_row][board_col] = 1

    def fall(self):
        """
        Move block down automatically.
        """

        if self.can_move(1, 0):
            self.block_row += 1

        else:
            # Block can no longer move down
            self.lock_block()

            # Create a new block
            self.current_block = random.choice(self.shapes)

            # Reset block position
            self.block_row = 0
            self.block_col = 1

        self.draw()

        self.root.after(FALL_SPEED, self.fall)


root = tk.Tk()

game = BlockMaster(root)

root.mainloop()
```

---

# 8. CRITICAL RULE FOR FUTURE DEVELOPMENT

When modifying the project:

**Preserve all currently working functionality.**

Do not rewrite the entire program unless there is a strong technical reason.

When adding a new phase:

1. Start from the current working code above.
2. Explain what will change.
3. Add only the code necessary for the new feature.
4. Explain where each change goes.
5. Provide the updated complete code when appropriate.
6. Explain how to test it.
7. Wait for confirmation before proceeding to the next major phase.

If a bug occurs, debug the existing implementation instead of replacing the entire architecture.

---

# 9. CURRENT NEXT TASK

The next phase is:

## PHASE 9 — ROW CLEARING

Goal:

Detect when an entire row is filled.

Example:

```text
Before:

00000
00100
11111  ← COMPLETE ROW
01100
```

After clearing:

```text
00000
00000
00100
01100
```

The completed row should disappear and the blocks above it should move downward.

Do NOT implement the score system yet unless it is necessary for testing.

First make row clearing work correctly.

---

# 10. TEACHING STYLE

Explain programming concepts while building.

For every new feature:

* Explain the purpose
* Explain the logic
* Show where the code goes
* Explain important lines
* Give the complete updated code if needed
* Explain how to run it
* Give a testing checklist

Keep explanations beginner-friendly.

Avoid unnecessary advanced Python concepts.

The goal is not just to make the game work.

The goal is for me to understand **why the code works**.
