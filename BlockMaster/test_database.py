from database import DatabaseManager


db = DatabaseManager()

if db.connect():

    print("DATABASE CONNECTED SUCCESSFULLY!")

    success = db.save_game(
        "PYTHON TEST",
        2500,
        5,
        20
    )

    if success:
        print("GAME SCORE SAVED SUCCESSFULLY!")
    else:
        print("GAME SCORE FAILED TO SAVE!")

    print("Highest score:", db.get_high_score())

    print("\nTOP SCORES:")

    scores = db.get_top_scores(10)

    for row in scores:
        print(row)

db.close()