import os
import pandas as pd

from app import get_db_connection

# ==========================================================
# Database Connection
# ==========================================================

db = get_db_connection()
cursor = db.cursor()

# ==========================================================
# Dataset Folder
# ==========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATASET_FOLDER = os.path.join(BASE_DIR, "datasets")

FILES = [
    "OOP.csv",
    "DSA.csv",
    "DBMS.csv",
    "Computer_Networks.csv",
    "Operating_System.csv"
]

total_imported = 0

print("=" * 60)
print("IMPORTING QUESTIONS")
print("=" * 60)

# ==========================================================
# Import All CSV Files
# ==========================================================

for file in FILES:

    file_path = os.path.join(DATASET_FOLDER, file)

    if not os.path.exists(file_path):

        print(f"{file} not found.")
        continue

    print(f"\nReading : {file}")

    df = pd.read_csv(file_path)

    print(f"Questions Found : {len(df)}")

    for _, row in df.iterrows():

        cursor.execute("""

            INSERT INTO questions
            (
                subject_id,
                difficulty,
                question,
                option1,
                option2,
                option3,
                option4,
                correct_option,
                explanation,
                topic,
                marks
            )

            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s
            )

        """, (

            int(row["subject_id"]),
            row["difficulty"],
            row["question"],
            row["option1"],
            row["option2"],
            row["option3"],
            row["option4"],
            row["correct_option"],
            row["explanation"],
            row["topic"],
            int(row["marks"])

        ))

        total_imported += 1

    db.commit()

    print(f"{file} Imported Successfully.")

# ==========================================================
# Finish
# ==========================================================

cursor.close()
db.close()

print("\n" + "=" * 60)
print(f"Successfully Imported {total_imported} Questions")
print("=" * 60)