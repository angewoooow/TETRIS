# BLOCKMASTER — FULL UPDATE / DATABASE INTEGRATION PROMPT

I am developing a Python/Tkinter Tetris-style arcade game called **BlockMaster**.

The game itself is currently working well. **DO NOT redesign or remove the existing gameplay unless necessary.** The immediate priority is to correctly connect the game to **MySQL/MariaDB through XAMPP/phpMyAdmin**, make the leaderboard persistent, and then prepare the project for the next database-related features.

---

# 1. CURRENT PROJECT STRUCTURE

The project is located approximately at:

```text
TETRIS/
│
├── .venv/
│
└── BlockMaster/
    ├── main.py
    ├── database.py
    ├── clearing.py
    └── test_database.py
```

The main game is in:

```text
BlockMaster/main.py
```

Database connection code is in:

```text
BlockMaster/database.py
```

Special clearing/combo mechanics are in:

```text
BlockMaster/clearing.py
```

Database testing is performed using:

```text
BlockMaster/test_database.py
```

The project uses:

* Python
* Tkinter
* MySQL Connector/Python
* XAMPP
* MySQL/MariaDB
* phpMyAdmin

---

# 2. CURRENT GAME DESIGN

The game is a Tetris-inspired arcade game.

Current board:

```text
10 columns × 23 rows
```

Cell size:

```text
32 px
```

The game has the standard seven Tetris-like shapes:

```text
I
O
T
L
J
S
Z
```

Shapes can:

* Move left
* Move right
* Rotate
* Hard drop using SPACE
* Fall automatically
* Lock into the board

Controls:

```text
← / → = Move
↑ / ↓ = Rotate
SPACE = Hard Drop
```

---

# 3. CURRENT VISUAL DESIGN

The game currently uses a:

**Neon 3D Arcade theme**

The interface contains:

* 3D-looking panels
* Neon arcade colors
* Dark arcade background
* 3D-looking blocks
* Score box
* High score box
* Level box
* Combo indicator
* Next-block preview
* Menu button
* Game-over popup
* Restart button
* Home button
* Leaderboard

The design should remain intact.

Do NOT replace the existing Tkinter interface with another framework.

---

# 4. HOME SCREEN

The home screen allows the player to enter a name.

Example:

```text
ENTER PLAYER

[ PLAYER ]

[ ▶ START GAME ]
```

The home screen also displays leaderboard information.

The player name should be stored when a game starts.

The game should use the player's name when saving the score.

---

# 5. GAME SCREEN

The game screen contains:

### Main board

```text
10 × 23
```

### Side information

Currently includes:

```text
SCORE
HIGH SCORE
LEVEL
NEXT BLOCK
COMBO
```

The player's name appears at the top.

The menu button is located in the upper-left/top area.

---

# 6. MENU

When the MENU button is clicked:

**The game automatically pauses.**

The menu appears as a popup/overlay **inside the same game window**.

It must NOT create another Tkinter window.

Menu options:

```text
▶ RESUME
↻ RESTART
⌂ HOME
✕ QUIT
```

There should NOT be a separate visible PAUSE button.

When MENU is opened:

```text
game pauses automatically
```

When RESUME is clicked:

```text
game resumes
```

RESTART:

```text
current game resets
```

HOME:

```text
returns to home screen
```

QUIT:

```text
saves the game if necessary
closes database connection
closes application
```

---

# 7. GAME OVER

When the blocks reach the top and a new piece cannot spawn:

```text
GAME OVER
```

must appear.

The game-over popup should remain **inside the same main window**.

It should be larger than the game board and display:

```text
GAME OVER

PLAYER NAME

FINAL SCORE
HIGH SCORE
LEVEL
LINES

[ ↻ RESTART GAME ]

[ ⌂ HOME ]
```

If the player achieved a new high score, display:

```text
★ NEW HIGH SCORE! ★
```

There should also be a celebration animation/effect.

---

# 8. COUNTDOWN

Before gameplay begins:

```text
3
2
1
GO!
```

The active falling piece must NOT be visible during the countdown.

The actual piece should become visible only after:

```text
GO!
```

The game timer and falling timer should begin after the countdown finishes.

---

# 9. CURRENT SPEED SYSTEM

Current starting speed:

```text
1600 ms
```

The game becomes faster as time passes.

Current intended behavior:

```text
START = 1600 ms
```

The speed decreases by:

```text
200 ms
```

every:

```text
20 seconds
```

until reaching:

```text
300 ms
```

After the later time thresholds, the intended design was to make the game even faster while remaining playable.

Important:

Do not accidentally make Level 1 extremely fast.

The current starting speed should remain:

```text
1600 ms
```

---

# 10. CURRENT SCORING

The current game gives points for:

* Placing blocks
* Hard drop distance
* Clearing rows
* Combos
* Special clearing combinations

The current level system is based on score.

However, the level progression should remain balanced.

A previous implementation used:

```python
LEVEL_SCORE = 500
```

but this caused levels to increase too quickly.

The final implementation should prevent situations such as:

```text
Level 100+
after approximately one minute
```

The game should feel like an arcade game where progression is meaningful.

---

# 11. CURRENT CLEARING SYSTEM

The clearing system is handled separately in:

```text
clearing.py
```

This is intentional.

Do NOT move all clearing logic into main.py unless necessary.

The project has special clearing mechanics beyond standard Tetris.

The current system includes:

### Normal row clearing

A row does not necessarily need to be completely filled.

The current requirement is approximately:

```text
9 filled cells
```

to trigger the normal row-clear behavior.

This is intentionally different from traditional Tetris.

---

# 12. SPECIAL COMBINATIONS

The game also contains special shape combinations.

Special combinations can:

* Clear rows
* Clear columns
* Clear neighboring blocks
* Create blast effects
* Produce combo scores
* Produce visual effects

Each shape can have its own possible combination behavior.

However, special combinations must NOT happen constantly.

Current intended special-combination timing:

```text
Every 30 seconds
```

There should be:

```text
NO special combination during the first 30 seconds.
```

After 30 seconds, the special combination system may activate.

The special combination should not interfere with the normal next-piece queue.

---

# 13. IMPORTANT BUG THAT WAS FIXED

Previously, when a special combination happened:

```text
current piece
↓
combination animation
↓
board clearing
```

the next piece sometimes appeared to be skipped.

This happened because the combination/clearing process could accidentally spawn or advance the next piece more than once.

The current code contains a guard:

```python
self.lock_in_progress
```

The purpose is to guarantee:

```text
ONE PIECE
→ ONE LOCK
→ ONE CLEAR PROCESS
→ ONE SPAWN
```

Do NOT remove this protection.

Do NOT introduce any code that causes:

```text
piece A
→ combination
→ piece C
```

while piece B is accidentally skipped.

The next-piece queue must remain deterministic.

---

# 14. CURRENT ANIMATION

The game has combo and clearing animations.

The player specifically needs to SEE the clearing animation.

Do not make the animation so fast that it becomes invisible.

Animations should be visually noticeable but not freeze the game.

The game should show:

* Clearing flash
* Combo indicator
* Special blast effect
* New-high-score celebration

---

# 15. DATABASE REQUIREMENT

This is now the MOST IMPORTANT PART.

The game must save completed games permanently into MySQL/MariaDB.

The database is:

```text
blockmaster
```

The table is:

```text
game_scores
```

The current table structure is:

```sql
CREATE TABLE IF NOT EXISTS game_scores (
    id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    player_name VARCHAR(50) NOT NULL,
    score INT UNSIGNED NOT NULL DEFAULT 0,
    level INT UNSIGNED NOT NULL DEFAULT 1,
    line_count INT UNSIGNED NOT NULL DEFAULT 0,
    played_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    INDEX idx_score (score),
    INDEX idx_played_at (played_at)
);
```

IMPORTANT:

The column is:

```text
line_count
```

NOT:

```text
lines
```

This caused a previous problem.

All Python database queries MUST use:

```text
line_count
```

---

# 16. DATABASE CURRENT TEST RESULT

The database itself has already been successfully created.

I successfully inserted test data manually:

```text
TEST PLAYER
Score: 1000
Level: 3
Lines: 10
```

I also successfully tested Python database communication.

The test program previously produced:

```text
DATABASE CONNECTED SUCCESSFULLY!
[DATABASE] Game saved successfully!
GAME SCORE SAVED SUCCESSFULLY!
Highest score: 2500

TOP SCORES:
{'player_name': 'PYTHON TEST', 'score': 2500, 'level': 5, 'line_count': 20, ...}
{'player_name': 'TEST PLAYER', 'score': 1000, 'level': 3, 'line_count': 10, ...}
```

Therefore:

**The database and Python MySQL connector CAN work.**

---

# 17. CURRENT DATABASE ERROR

The current problem is:

```text
[DATABASE] Connection failed:
2003 (HY000): Can't connect to MySQL server on 'localhost:3306' (10061)
```

This is the current priority.

The application starts, but it cannot connect to MySQL.

The error occurs from:

```text
database.py
```

using:

```text
localhost
port 3306
user root
password ""
database blockmaster
```

Current connection configuration:

```python
HOST = "localhost"
PORT = 3306
USER = "root"
PASSWORD = ""
DATABASE = "blockmaster"
```

---

# 18. IMPORTANT: DO NOT ASSUME THE DATABASE IS BROKEN

The database was previously confirmed to work.

Therefore investigate the connection problem before changing the schema.

Possible causes to check:

1. XAMPP Apache is running.
2. XAMPP MySQL is running.
3. MySQL/MariaDB is actually listening on port 3306.
4. The MySQL port may have changed.
5. Another MySQL installation may be using the port.
6. XAMPP may be configured for another port.
7. The Python connector may be connecting to the wrong port.
8. MySQL may have stopped after the previous test.
9. The application may be using a different Python environment.
10. The database name/user/password may not match the current XAMPP configuration.

The first thing I want you to help me diagnose is:

```text
2003 (HY000)
Can't connect to MySQL server on localhost:3306
(10061)
```

Do NOT immediately rewrite the entire game.

---

# 19. DATABASE.PY REQUIREMENTS

The final `database.py` should provide:

```python
DatabaseManager
```

with at least:

```text
connect()
ensure_connection()
save_game()
get_high_score()
get_top_scores()
get_recent_scores()
close()
```

The SQL must use:

```text
line_count
```

everywhere.

It must NOT use:

```text
lines
```

---

# 20. ERROR HANDLING

The game should NOT crash if MySQL is temporarily unavailable.

If MySQL is offline:

```text
Game can still start and play.
```

The database manager should report:

```text
[DATABASE] Connection failed: ...
```

but the game should remain usable.

However, when MySQL becomes available again, the application should be able to reconnect.

---

# 21. DATABASE SAVE BEHAVIOR

A game should be saved when the game ends.

The saved information should include:

```text
player_name
score
level
line_count
played_at
```

Example:

```text
PLAYER: ANGELO
SCORE: 3250
LEVEL: 8
LINES: 25
DATE/TIME: automatic
```

Each completed game should create a NEW database row.

Do NOT overwrite previous scores.

---

# 22. ALL-TIME HIGH SCORE

The home screen should retrieve:

```sql
MAX(score)
```

from:

```text
game_scores
```

This means the high score survives:

```text
closing the application
reopening the application
restarting Windows
starting another game
```

The highest score should remain permanently stored.

---

# 23. SESSION LEADERBOARD

There should be a session leaderboard.

The purpose is:

```text
Players can play one after another.
The current session can compare their scores.
```

For example:

```text
RANK    PLAYER          SCORE

1       ANGELO          8500
2       MARK            6200
3       JOHN            5100
4       PAUL            3000
```

The session leaderboard can remain in memory.

The database is for permanent historical records.

---

# 24. DATABASE LEADERBOARD

The permanent database should also allow the application to retrieve the highest scores.

For example:

```text
TOP 10 ALL-TIME
```

ordered by:

```text
score DESC
```

The database should also support recent games:

```text
10 MOST RECENT GAMES
```

ordered by:

```text
played_at DESC
```

---

# 25. IMPORTANT DATABASE ISSUE TO FIX

The current `main.py` and `database.py` must use the same column name.

Correct:

```python
INSERT INTO game_scores
(player_name, score, level, line_count)
VALUES (%s, %s, %s, %s)
```

Incorrect:

```python
INSERT INTO game_scores
(player_name, score, level, lines)
```

Also correct:

```sql
SELECT player_name, score, level, line_count, played_at
FROM game_scores
```

NOT:

```sql
SELECT player_name, score, level, lines, played_at
```

---

# 26. CURRENT MAIN.PY

The existing `main.py` already contains the major game systems.

Do NOT remove:

```text
ClearingSystem
DatabaseManager
countdown
spawn system
next block
rotation
hard drop
game over
menu
home screen
leaderboard
3D blocks
combo indicator
animations
high-score celebration
```

The current import structure is approximately:

```python
import tkinter as tk
import random
import time

from clearing import ClearingSystem
from database import DatabaseManager
```

---

# 27. IMPORTANT GAME SAFETY RULE

When saving a game:

```python
self.score_saved
```

is used to prevent duplicate database records.

This protection must remain.

A single game should NOT produce:

```text
3 duplicate database rows
```

because the player clicked:

```text
HOME
RESTART
QUIT
```

multiple times.

Each completed game should be saved exactly once.

---

# 28. HOME SCREEN DATABASE REFRESH

When returning to the home screen:

```text
create_home_screen()
```

should retrieve the latest database high score.

It should also retrieve the permanent leaderboard if that feature is enabled.

This means:

```text
Game 1
→ score 5000
→ save

HOME

Game 2
→ home screen should show 5000
```

even if the application was not restarted.

---

# 29. APPLICATION RESTART REQUIREMENT

This is very important.

Test this sequence:

```text
1. Start XAMPP.
2. Start BlockMaster.
3. Enter player name.
4. Start game.
5. Play.
6. Reach game over.
7. Score is saved.
8. Close BlockMaster.
9. Open BlockMaster again.
10. Home screen loads.
11. Previous score should still exist.
12. All-time high score should still be visible.
```

The database is the permanent source of truth.

---

# 30. DATABASE CONNECTION DIAGNOSTIC

Before changing the code, help me verify:

### XAMPP

Check:

```text
MySQL = Running
```

### Port

Verify whether XAMPP MySQL is actually using:

```text
3306
```

If it is using another port, update:

```python
PORT = ...
```

accordingly.

### phpMyAdmin

Verify:

```text
blockmaster
```

exists.

Verify:

```text
game_scores
```

exists.

Verify columns:

```text
id
player_name
score
level
line_count
played_at
```

---

# 31. DO NOT CHANGE THE DATABASE SCHEMA UNNECESSARILY

The current database already works.

Do NOT:

```text
DROP DATABASE
DROP TABLE
DELETE ALL DATA
```

unless I explicitly ask.

Do not destroy existing test scores.

If a migration is necessary, explain it first.

---

# 32. EXPECTED FINAL RESULT

After the database connection is fixed:

```text
BlockMaster
       ↓
Python/Tkinter
       ↓
database.py
       ↓
mysql.connector
       ↓
XAMPP MySQL/MariaDB
       ↓
blockmaster
       ↓
game_scores
```

The game should be able to:

```text
START GAME
↓
PLAYER PLAYS
↓
GAME OVER
↓
SAVE SCORE
↓
MYSQL DATABASE
↓
RETURN HOME
↓
LOAD HIGH SCORE
↓
SHOW LEADERBOARD
```

---

# 33. DEVELOPMENT PRIORITY

Work in this order.

## PHASE A — DATABASE CONNECTION

Fix:

```text
2003 (HY000)
Can't connect to MySQL server on localhost:3306
```

Do not change gameplay.

---

## PHASE B — DATABASE MANAGER

Verify:

```text
connect()
save_game()
get_high_score()
get_top_scores()
get_recent_scores()
close()
```

Use:

```text
line_count
```

consistently.

---

## PHASE C — MAIN.PY INTEGRATION

Make sure:

```text
GAME OVER
```

calls:

```python
save_finished_game()
```

and the data reaches MySQL.

---

## PHASE D — PERSISTENT LEADERBOARD

When the application starts:

```text
retrieve database high score
retrieve top scores
```

When a game ends:

```text
save score
refresh leaderboard
```

---

## PHASE E — TEST

Perform this exact test:

```text
PLAYER NAME = TEST PLAYER

Play game.

Game over.

Check phpMyAdmin.

Expected:

new row in game_scores
```

Then:

```text
close app
reopen app
```

Expected:

```text
previous score still visible
```

---

# 34. CODING STYLE

Keep the project beginner-friendly.

I am an engineering student learning programming, so:

* Do not over-engineer.
* Keep functions readable.
* Add comments for important database logic.
* Avoid unnecessary frameworks.
* Keep Tkinter.
* Keep clearing.py separate.
* Keep database.py separate.
* Explain important changes.
* Do not silently change unrelated gameplay.

When providing code, provide the **whole file**, not only fragments, when a file needs to be replaced.

---

# 35. VERY IMPORTANT RESPONSE FORMAT

First diagnose the current error:

```text
2003 (HY000): Can't connect to MySQL server on localhost:3306
```

Explain what it means in simple terms.

Then tell me exactly what to check in XAMPP/phpMyAdmin.

If the problem is confirmed to be the MySQL port/service, show me exactly what to change.

After diagnosis, provide the corrected complete:

```text
database.py
```

and, only if necessary, the corrected complete:

```text
main.py
```

Do not break the current working game mechanics.

The immediate objective is:

**MAKE BLOCKMASTER CONNECT TO THE EXISTING XAMPP MYSQL DATABASE AND SAVE/LOAD SCORES PERSISTENTLY.**


