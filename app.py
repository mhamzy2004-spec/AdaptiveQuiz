from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
    jsonify
)
import os
import mysql.connector
import random
import re

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from ai.predictor import predict_level


# ==========================================================
# Flask App Configuration
# ==========================================================

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "adaptive_quiz_secret_key_2026")


def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "M_Hamza"),
        password=os.getenv("DB_PASSWORD", "Hamza@22"),
        database=os.getenv("DB_NAME", "adaptive_quiz"),
        port=int(os.getenv("DB_PORT", 3306))
    )

# ==========================================================
# Home
# ==========================================================

@app.route("/")
def home():

    if "user_id" in session:

        return redirect(url_for("dashboard"))

    return render_template("Login.html")


# ==========================================================
# Signup Page
# ==========================================================

@app.route("/signup")
def signup():

    if "user_id" in session:

        return redirect(url_for("dashboard"))

    return render_template("signup.html")
# ==========================================================
# Register User
# ==========================================================

@app.route("/register", methods=["POST"])
def register():

    fullname = request.form.get("fullname", "").strip()
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")
    confirm_password = request.form.get("confirm_password", "")

    # ----------------------------
    # Validation
    # ----------------------------

    if not fullname:
        flash("Full Name is required.", "danger")
        return redirect(url_for("signup"))

    if len(fullname) < 3:
        flash("Full Name must be at least 3 characters.", "danger")
        return redirect(url_for("signup"))

    if not email:
        flash("Email is required.", "danger")
        return redirect(url_for("signup"))

    email_pattern = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'

    if not re.match(email_pattern, email):
        flash("Please enter a valid email address.", "danger")
        return redirect(url_for("signup"))

    if not password:
        flash("Password is required.", "danger")
        return redirect(url_for("signup"))

    if len(password) < 8:
        flash("Password must be at least 8 characters.", "danger")
        return redirect(url_for("signup"))

    if password != confirm_password:
        flash("Passwords do not match.", "danger")
        return redirect(url_for("signup"))

    db = get_db_connection()
    cursor = db.cursor(dictionary=True, buffered=True)

    try:

        # Check duplicate email

        cursor.execute(
            "SELECT id FROM users WHERE email=%s",
            (email,)
        )

        existing = cursor.fetchone()

        if existing:
            flash("Email already registered.", "warning")
            return redirect(url_for("signup"))

        # Hash Password

        hashed_password = generate_password_hash(password)

        cursor.execute("""

            INSERT INTO users
            (
                full_name,
                email,
                password
            )

            VALUES
            (
                %s,
                %s,
                %s
            )

        """,

        (
            fullname,
            email,
            hashed_password
        ))

        db.commit()

        flash("Registration Successful. Please Login.", "success")

        return redirect(url_for("home"))

    except Exception as e:

        db.rollback()

        print("Register Error :", e)

        flash("Registration failed.", "danger")

        return redirect(url_for("signup"))

    finally:

        cursor.close()
        db.close()


# ==========================================================
# Login
# ==========================================================

@app.route("/login", methods=["POST"])
def login():

    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")

    if not email or not password:

        flash("Email and Password are required.", "danger")

        return redirect(url_for("home"))

    db = get_db_connection()
    cursor = db.cursor(dictionary=True, buffered=True)

    try:

        cursor.execute("""

            SELECT *

            FROM users

            WHERE email=%s

        """, (email,))

        user = cursor.fetchone()

        if not user:

            flash("Account does not exist.", "danger")

            return redirect(url_for("home"))

        # Password Verification

        if not check_password_hash(user["password"], password):

            flash("Incorrect Password.", "danger")

            return redirect(url_for("home"))

        # Session

        session["user_id"] = user["id"]
        session["name"] = user["full_name"]
        session["email"] = user["email"]
        session["level"] = user["level"]

        flash(f"Welcome {user['full_name']}!", "success")

        return redirect(url_for("dashboard"))

    except Exception as e:

        print("Login Error :", e)

        flash("Unable to login.", "danger")

        return redirect(url_for("home"))

    finally:

        cursor.close()
        db.close()


# ==========================================================
# Logout
# ==========================================================

@app.route("/logout")
def logout():

    session.clear()

    flash("Logged out successfully.", "success")

    return redirect(url_for("home"))
# ==========================================================
# Dashboard
# ==========================================================

@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        flash("Please login first.", "warning")
        return redirect(url_for("home"))

    user_id = session["user_id"]

    db = get_db_connection()
    cursor = db.cursor(dictionary=True, buffered=True)

    try:
        pass

        # =====================================
        # User Information
        # =====================================

        cursor.execute("""
            SELECT
                id,
                full_name,
                email,
                assessment_completed,
                assessment_score,
                quizzes_completed
            FROM users
            WHERE id=%s
        """,(user_id,))

        user = cursor.fetchone()

        if not user:
            session.clear()
            flash("User not found.")
            return redirect(url_for("home"))

        # =====================================
        # Quiz Statistics
        # =====================================

        cursor.execute("""
            SELECT

                COUNT(*) AS total_quizzes,

                IFNULL(SUM(score),0) AS total_score,

                IFNULL(SUM(total_questions),0) AS total_questions,

                IFNULL(AVG(time_taken),0) AS avg_time

            FROM quiz_attempts

            WHERE user_id=%s

        """,(user_id,))

        stats = cursor.fetchone()

        total_quizzes = stats["total_quizzes"]

        if stats["total_questions"] > 0:

            average = round(

                (stats["total_score"] /
                 stats["total_questions"]) * 100,

                2

            )

        else:

            average = 0

        # =====================================
        # Subject Levels
        # =====================================

        cursor.execute("""

            SELECT

                s.subject_name,

                us.current_level,

                us.average_score,

                us.quizzes_completed

            FROM user_subject_level us

            INNER JOIN subjects s

            ON us.subject_id=s.subject_id

            WHERE us.user_id=%s

            ORDER BY s.subject_name

        """,(user_id,))

        subject_levels = cursor.fetchall()

        # =====================================
        # Overall AI Level
        # =====================================

        level_points = {

            "Beginner":1,

            "Intermediate":2,

            "Advanced":3

        }

        if subject_levels:

            total = sum(

                level_points.get(x["current_level"],1)

                for x in subject_levels

            )

            avg = total / len(subject_levels)

            if avg >= 2.5:

                overall_level = "Advanced"

            elif avg >= 1.5:

                overall_level = "Intermediate"

            else:

                overall_level = "Beginner"

        else:

            overall_level = "Beginner"

        # =====================================
        # Recent Quizzes
        # =====================================

        cursor.execute("""

            SELECT

                s.subject_name,

                q.score,

                q.total_questions,

                q.difficulty,

                q.attempt_date

            FROM quiz_attempts q

            INNER JOIN subjects s

            ON q.subject_id=s.subject_id

            WHERE q.user_id=%s

            ORDER BY q.attempt_date DESC

            LIMIT 5

        """,(user_id,))

        recent_quizzes = cursor.fetchall()

        # =====================================
        # Subjects
        # =====================================

        cursor.execute("""

            SELECT

                subject_id,

                subject_name,

                description

            FROM subjects

            ORDER BY subject_name

        """)

        subjects = cursor.fetchall()
        
        cursor.execute("""
            SELECT
                attempt_date,
                score,
                total_questions
            FROM quiz_attempts
            WHERE user_id=%s
            ORDER BY attempt_date
        """, (user_id,))

        quiz_history = cursor.fetchall()

        chart_labels = []
        chart_scores = []

        for row in quiz_history:

            chart_labels.append(row["attempt_date"].strftime("%d %b"))

            if row["total_questions"] > 0:
                percentage = round(
                    (row["score"] / row["total_questions"]) * 100,
                    2
                )
            else:
                percentage = 0

            chart_scores.append(percentage)

        # =====================================
        # Dynamic Rank
        # =====================================

        cursor.execute("""

            SELECT

                u.id,

                IFNULL(SUM(q.score),0) total_score,

                IFNULL(SUM(q.total_questions),0) total_questions

            FROM users u

            LEFT JOIN quiz_attempts q

            ON u.id=q.user_id

            GROUP BY u.id

        """)

        students = cursor.fetchall()

        ranking = []

        for s in students:

            if s["total_questions"] > 0:

                avg = round(

                    (s["total_score"] /
                     s["total_questions"]) * 100,

                    2

                )

            else:

                avg = 0

            ranking.append({

                "user_id":s["id"],

                "average":avg

            })

        ranking.sort(

            key=lambda x:x["average"],

            reverse=True

        )

        user_rank = "-"

        for index,row in enumerate(ranking,start=1):

            if row["user_id"] == user_id:

                user_rank = index

                break

        # =====================================
        # Update Session
        # =====================================

        session["name"] = user["full_name"]

        session["email"] = user["email"]

        session["level"] = overall_level

        # =====================================
        # Render Dashboard
        # =====================================

        return render_template(

            "dashboard.html",

            name=user["full_name"],

            email=user["email"],

            level=overall_level,

            assessment_completed=user["assessment_completed"],

            assessment_score=user["assessment_score"],

            quizzes=total_quizzes,

            average=average,

            avg_time=round(stats["avg_time"],2),

            rank=user_rank,

            recent_quizzes=recent_quizzes,

            subject_levels=subject_levels,

            subjects=subjects,
            chart_labels=chart_labels,
chart_scores=chart_scores

        )

    except Exception as e:

        print("Dashboard Error :", e)

        flash("Unable to load dashboard.")

        return redirect(url_for("home"))

    finally:

        cursor.close()

        db.close()
        
 # ==========================================================
# Subjects Page
# ==========================================================

@app.route("/subjects")
def subjects():

    # --------------------------------------
    # Login Check
    # --------------------------------------

    if "user_id" not in session:

        flash("Please login first.", "warning")

        return redirect(url_for("home"))

    user_id = session["user_id"]

    db = get_db_connection()

    cursor = db.cursor(dictionary=True, buffered=True)

    try:

        # --------------------------------------
        # Get User
        # --------------------------------------

        cursor.execute("""

            SELECT

                full_name,
                email,
                level,
                assessment_completed

            FROM users

            WHERE id=%s

        """, (user_id,))

        user = cursor.fetchone()

        if not user:

            session.clear()

            flash("User not found.", "danger")

            return redirect(url_for("home"))

        # --------------------------------------
        # Load Subjects
        # --------------------------------------

        cursor.execute("""

            SELECT

                subject_id,

                subject_name,

                description

            FROM subjects

            ORDER BY subject_name

        """)

        subjects = cursor.fetchall()

        # --------------------------------------
        # Update Session
        # --------------------------------------

        session["name"] = user["full_name"]

        session["level"] = user["level"]

        # --------------------------------------
        # Open Subject Page
        # --------------------------------------

        return render_template(

            "subject_selection.html",

            name=user["full_name"],

            email=user["email"],

            level=user["level"],

            assessment_completed=user["assessment_completed"],

            subjects=subjects

        )

    except Exception as e:

        print("Subjects Error :", e)

        flash("Unable to load subjects.", "danger")

        return redirect(url_for("dashboard"))

    finally:

        cursor.close()

        db.close()
        
 # ========================================================
# Assessment Route (AI Ready)
# ========================================================

@app.route("/assessment", methods=["GET", "POST"])
def assessment():

    if "user_id" not in session:
        return redirect(url_for("home"))

    user_id = session["user_id"]

    # ==========================================
    # POST REQUEST
    # ==========================================

    if request.method == "POST":

        data = request.get_json()

        answers = data.get("answers", {})

        db = get_db_connection()
        cursor = db.cursor(dictionary=True, buffered=True)

        score = 0
        total_questions = len(answers)

        # ------------------------------------------
        # Calculate Assessment Score
        # ------------------------------------------

        for q_id, selected in answers.items():

            cursor.execute("""
                SELECT correct_option
                FROM assessment_questions
                WHERE id=%s
            """, (q_id,))

            row = cursor.fetchone()

            if row:

                if row["correct_option"].lower() == selected.lower():
                    score += 1

        # ------------------------------------------
        # Decide Initial Level
        # ------------------------------------------

        if score <= 4:
            level = "Beginner"

        elif score <= 7:
            level = "Intermediate"

        else:
            level = "Advanced"

        # ------------------------------------------
        # Update Users Table
        # ------------------------------------------

        cursor.execute("""
            UPDATE users
            SET
                level=%s,
                assessment_score=%s,
                assessment_completed=1
            WHERE id=%s
        """, (
            level,
            score,
            user_id
        ))

        # ------------------------------------------
        # Save Assessment History
        # ------------------------------------------

        cursor.execute("""
            INSERT INTO assessment
            (
                user_id,
                score,
                level_assigned
            )
            VALUES
            (
                %s,
                %s,
                %s
            )
        """, (
            user_id,
            score,
            level
        ))

        # ------------------------------------------
        # Initialize Subject Levels
        # ------------------------------------------

        cursor.execute("""
            DELETE FROM user_subject_level
            WHERE user_id=%s
        """, (user_id,))

        cursor.execute("""
            SELECT subject_id
            FROM subjects
        """)

        subjects = cursor.fetchall()

        for subject in subjects:

            cursor.execute("""
                INSERT INTO user_subject_level
                (
                    user_id,
                    subject_id,
                    current_level,
                    quizzes_completed,
                    average_score
                )
                VALUES
                (
                    %s,
                    %s,
                    %s,
                    %s,
                    %s
                )
            """, (
                user_id,
                subject["subject_id"],
                level,
                0,
                0
            ))

        db.commit()

        percentage = 0

        if total_questions > 0:

            percentage = round(
                (score / total_questions) * 100,
                2
            )

        session["level"] = level
        session["assessment_score"] = score

        cursor.close()
        db.close()

        return jsonify({

            "status": "success",

            "score": score,

            "total": total_questions,

            "percentage": percentage,

            "level": level,

            "redirect": url_for("dashboard")

        })

    # ==========================================
    # GET REQUEST
    # ==========================================

    db = get_db_connection()
    cursor = db.cursor(dictionary=True, buffered=True)

    cursor.execute("""
        SELECT
            id,
            subject,
            question,
            option1,
            option2,
            option3,
            option4
        FROM assessment_questions
    """)

    questions = cursor.fetchall()

    random.shuffle(questions)

    questions = questions[:10]

    cursor.close()
    db.close()

    return render_template(
        "assessment.html",
        questions=questions,
        name=session.get("name")
    )
        
# ========================================================
# Quiz Route (Subject-wise AI Level)
# ========================================================

@app.route("/quiz/<int:subject_id>")
def quiz(subject_id):

    print("\n==============================")
    print("QUIZ ROUTE HIT")
    print("Subject ID:", subject_id)
    print("Session:", dict(session))
    print("==============================\n")

    if "user_id" not in session:
        print("ERROR: user_id not found in session")
        return redirect(url_for("home"))

    user_id = session["user_id"]

    db = get_db_connection()
    cursor = db.cursor(dictionary=True, buffered=True)

    try:

        # ==========================================
        # Subject Information
        # ==========================================

        cursor.execute("""
            SELECT subject_name
            FROM subjects
            WHERE subject_id=%s
        """, (subject_id,))

        subject = cursor.fetchone()

        print("Subject Query Result:", subject)

        if subject is None:
            print("ERROR: Subject not found")
            flash("Subject not found.", "danger")
            return redirect(url_for("subjects"))

        subject_name = subject["subject_name"]

        # ==========================================
        # Student Current Level
        # ==========================================

        cursor.execute("""
            SELECT current_level
            FROM user_subject_level
            WHERE user_id=%s
            AND subject_id=%s
        """, (user_id, subject_id))

        level_data = cursor.fetchone()

        print("Level Data:", level_data)

        if level_data:

            difficulty = level_data["current_level"]

        else:

            print("No level found -> Creating Beginner")

            difficulty = "Beginner"

            cursor.execute("""
                INSERT INTO user_subject_level
                (
                    user_id,
                    subject_id,
                    current_level,
                    quizzes_completed,
                    average_score
                )
                VALUES
                (%s,%s,%s,%s,%s)
            """, (
                user_id,
                subject_id,
                "Beginner",
                0,
                0
            ))

            db.commit()

        print("Difficulty:", difficulty)

        # ==========================================
        # Load Questions
        # ==========================================

        cursor.execute("""
            SELECT
                question_id,
                question,
                option1,
                option2,
                option3,
                option4,
                difficulty
            FROM questions
            WHERE subject_id=%s
            AND difficulty=%s
            ORDER BY RAND()
            LIMIT 10
        """, (
            subject_id,
            difficulty
        ))

        questions = cursor.fetchall()

        print("Questions Loaded:", len(questions))

        # ==========================================
        # Fallback
        # ==========================================

        if len(questions) < 10:

            print("Using Fallback Questions")

            cursor.execute("""
                SELECT
                    question_id,
                    question,
                    option1,
                    option2,
                    option3,
                    option4,
                    difficulty
                FROM questions
                WHERE subject_id=%s
                ORDER BY RAND()
                LIMIT 10
            """, (subject_id,))

            questions = cursor.fetchall()

            print("Fallback Loaded:", len(questions))

        if len(questions) == 0:

            print("ERROR: No questions found")

            flash("No questions available.", "warning")

            return redirect(url_for("subjects"))

        print("Rendering quiz.html")

        return render_template(
            "quiz.html",
            questions=questions,
            subject_id=subject_id,
            subject_name=subject_name,
            difficulty=difficulty,
            student_level=difficulty,
            total_questions=len(questions)
        )

    except Exception as e:

        import traceback
        traceback.print_exc()

        return f"<h2>{e}</h2>"

    finally:

        cursor.close()
        db.close()
# ========================================================
# Submit Quiz (Part 1)
# ========================================================

@app.route("/submit_quiz", methods=["POST"])
def submit_quiz():

    if "user_id" not in session:
        return redirect(url_for("home"))

    user_id = session["user_id"]

    subject_id = int(request.form.get("subject_id"))

    time_taken = int(request.form.get("time_taken", 0))

    db = get_db_connection()

    cursor = db.cursor(dictionary=True, buffered=True)

    try:

        # ==========================================
        # Subject Information
        # ==========================================

        cursor.execute("""
            SELECT subject_name
            FROM subjects
            WHERE subject_id=%s
        """, (subject_id,))

        subject = cursor.fetchone()

        if not subject:

            flash("Subject not found.")

            return redirect(url_for("subjects"))

        subject_name = subject["subject_name"]

        # ==========================================
        # Get Subject-wise Current Level
        # ==========================================

        cursor.execute("""
            SELECT
                current_level
            FROM user_subject_level
            WHERE
                user_id=%s
                AND subject_id=%s
        """, (
            user_id,
            subject_id
        ))

        level_data = cursor.fetchone()

        if level_data:

            current_level = level_data["current_level"]

        else:

            current_level = "Beginner"

            cursor.execute("""
                INSERT INTO user_subject_level
                (
                    user_id,
                    subject_id,
                    current_level,
                    quizzes_completed,
                    average_score
                )
                VALUES
                (
                    %s,
                    %s,
                    %s,
                    %s,
                    %s
                )
            """, (
                user_id,
                subject_id,
                "Beginner",
                0,
                0
            ))

            db.commit()

        # ==========================================
        # Assessment Score
        # ==========================================

        cursor.execute("""
            SELECT
                assessment_score
            FROM users
            WHERE id=%s
        """, (user_id,))

        user = cursor.fetchone()

        assessment_score = user["assessment_score"] if user else 0

        # ==========================================
        # Load Quiz Questions
        # ==========================================

        cursor.execute("""
            SELECT
                question_id,
                correct_option
            FROM questions
            WHERE
                subject_id=%s
                AND difficulty=%s
            ORDER BY RAND()
            LIMIT 10
        """, (
            subject_id,
            current_level
        ))

        questions = cursor.fetchall()

        # ==========================================
        # Fallback
        # ==========================================

        if len(questions) < 10:

            cursor.execute("""
                SELECT
                    question_id,
                    correct_option
                FROM questions
                WHERE subject_id=%s
                ORDER BY RAND()
                LIMIT 10
            """, (
                subject_id,
            ))

            questions = cursor.fetchall()

        total_questions = len(questions)

        score = 0

        # ==========================================
        # Option Mapping
        # ==========================================

        option_map = {

            "a": "option1",

            "b": "option2",

            "c": "option3",

            "d": "option4"

        }

        # ==========================================
        # Calculate Quiz Score
        # ==========================================

        for question in questions:

            qid = str(question["question_id"])

            answer = request.form.get(f"q_{qid}")

            if answer is None:

                answer = request.form.get(qid)

            if answer:

                answer = answer.lower().strip()

                mapped_answer = option_map.get(
                    answer,
                    answer
                )

                correct_answer = question["correct_option"].lower().strip()

                if mapped_answer == correct_answer:

                    score += 1

        # ==========================================
        # Percentage
        # ==========================================

        if total_questions > 0:

            percentage = round(
                (score / total_questions) * 100,
                2
            )

        else:

            percentage = 0
       
              # ==========================================
        # AI Prediction
        # ==========================================

        try:

            new_level = predict_level(

                assessment_score=float(assessment_score or 0),

                subject_id=int(subject_id),

                quiz_score=score,

                quiz_percentage=float(percentage),

                time_taken=time_taken,

                current_level=current_level

            )

        except Exception as e:

            print("AI Prediction Error :", e)

            new_level = current_level

        # ==========================================
        # Save Quiz Attempt
        # ==========================================

        cursor.execute("""

            INSERT INTO quiz_attempts(

                user_id,

                subject_id,

                difficulty,

                score,

                total_questions,

                time_taken

            )

            VALUES(

                %s,

                %s,

                %s,

                %s,

                %s,

                %s

            )

        """,(

            user_id,

            subject_id,

            current_level,

            score,

            total_questions,

            time_taken

        ))

        # ==========================================
        # Calculate Subject Average
        # ==========================================

        cursor.execute("""

            SELECT

                COUNT(*) AS total_attempts,

                AVG((score/total_questions)*100) AS avg_score

            FROM quiz_attempts

            WHERE

                user_id=%s

                AND subject_id=%s

        """,(

            user_id,

            subject_id

        ))

        stats = cursor.fetchone()

        if stats and stats["avg_score"] is not None:

            average_score = round(stats["avg_score"],2)

        else:

            average_score = percentage

        # ==========================================
        # Update Subject Level
        # ==========================================

        cursor.execute("""

            UPDATE user_subject_level

            SET

                current_level=%s,

                quizzes_completed=quizzes_completed+1,

                average_score=%s

            WHERE

                user_id=%s

                AND subject_id=%s

        """,(

            new_level,

            average_score,

            user_id,

            subject_id

        ))

        # ==========================================
        # Update User Quiz Count
        # ==========================================

        cursor.execute("""

            UPDATE users

            SET

                quizzes_completed=quizzes_completed+1

            WHERE id=%s

        """,(

            user_id,

        ))

        db.commit()
        
              # ==========================================
        # Save Result in Session
        # ==========================================

        session["level"] = new_level

        session["last_quiz_result"] = {

            "score": score,

            "total": total_questions,

            "percentage": percentage,

            "subject_id": subject_id,

            "subject_name": subject_name,

            "difficulty": current_level,

            "time_taken": time_taken,

            "assessment_score": assessment_score,

            "average_percentage": average_score,

            "old_level": current_level,

            "new_level": new_level

        }

        # ==========================================
        # Redirect to Result Page
        # ==========================================

        return redirect(url_for("result"))

    # ==========================================
    # Exception
    # ==========================================

    except Exception as e:

        print("Submit Quiz Error :", e)

        flash("Something went wrong while submitting the quiz.")

        return redirect(url_for("subjects"))

    # ==========================================
    # Close Connection
    # ==========================================

    finally:

        cursor.close()

        db.close()
        
# ========================================================
# Result Route
# ========================================================

@app.route("/result")
def result():

    if "user_id" not in session:
        return redirect(url_for("home"))

    quiz_data = session.get("last_quiz_result")

    if not quiz_data:

        flash("No quiz result found.")

        return redirect(url_for("dashboard"))

    return render_template(

        "result.html",

        # ======================================
        # Quiz Information
        # ======================================

        score=quiz_data["score"],

        total=quiz_data["total"],

        percentage=quiz_data["percentage"],

        subject_id=quiz_data["subject_id"],

        subject_name=quiz_data["subject_name"],

        difficulty=quiz_data["difficulty"],

        time_taken=quiz_data["time_taken"],

        # ======================================
        # AI Information
        # ======================================

        assessment_score=quiz_data["assessment_score"],

        average_percentage=quiz_data["average_percentage"],

        old_level=quiz_data["old_level"],

        new_level=quiz_data["new_level"],

        # ======================================
        # User Information
        # ======================================

        name=session.get("name"),

        email=session.get("email"),

        overall_level=session.get("level")

    )
    
# ==========================================================
# Profile
# ==========================================================

@app.route("/profile")
def profile():

    if "user_id" not in session:
        return redirect(url_for("home"))

    user_id = session["user_id"]

    db = get_db_connection()
    cursor = db.cursor(dictionary=True, buffered=True)

    try:

        # =====================================
        # User Basic Information
        # =====================================

        cursor.execute("""
            SELECT
                full_name,
                email,
                assessment_score,
                quizzes_completed
            FROM users
            WHERE id=%s
        """,(user_id,))

        user = cursor.fetchone()

        # =====================================
        # Quiz Statistics
        # =====================================

        cursor.execute("""
            SELECT
                COUNT(*) AS quizzes,
                IFNULL(SUM(score),0) AS total_score,
                IFNULL(SUM(total_questions),0) AS total_questions,
                IFNULL(SUM(time_taken),0) AS total_time
            FROM quiz_attempts
            WHERE user_id=%s
        """,(user_id,))

        stats = cursor.fetchone()

        quizzes = stats["quizzes"] or 0
        total_score = stats["total_score"] or 0
        total_questions = stats["total_questions"] or 0
        total_time = stats["total_time"] or 0

        if total_questions > 0:
            average = round((total_score / total_questions) * 100,2)
        else:
            average = 0

        correct = total_score
        wrong = total_questions - total_score

        # =====================================
        # Subject Levels
        # =====================================

        cursor.execute("""
            SELECT
                s.subject_name,
                us.current_level,
                us.average_score,
                us.quizzes_completed
            FROM user_subject_level us
            INNER JOIN subjects s
            ON us.subject_id=s.subject_id
            WHERE us.user_id=%s
            ORDER BY s.subject_name
        """,(user_id,))

        subject_levels = cursor.fetchall()

        # =====================================
        # Overall Level
        # =====================================

        level_points = {
            "Beginner":1,
            "Intermediate":2,
            "Advanced":3
        }

        if subject_levels:

            total_points = 0

            for row in subject_levels:
                total_points += level_points.get(
                    row["current_level"],
                    1
                )

            avg_level = total_points / len(subject_levels)

            if avg_level >= 2.5:
                overall_level = "Advanced"

            elif avg_level >= 1.5:
                overall_level = "Intermediate"

            else:
                overall_level = "Beginner"

        else:

            overall_level = "Beginner"

        # =====================================
        # Badge
        # =====================================

        if average >= 90:
            badge="Quiz Champion"

        elif average>=80:
            badge="Gold Performer"

        elif average>=70:
            badge="Silver Performer"

        elif average>=60:
            badge="Bronze Performer"

        else:
            badge="Beginner"

        # =====================================
        # Recent Quizzes
        # =====================================

        cursor.execute("""

            SELECT

                s.subject_name,

                q.score,

                q.total_questions,

                q.difficulty,

                q.attempt_date

            FROM quiz_attempts q

            INNER JOIN subjects s

            ON q.subject_id=s.subject_id

            WHERE q.user_id=%s

            ORDER BY q.attempt_date DESC

            LIMIT 5

        """,(user_id,))

        recent_quizzes = cursor.fetchall()

        # =====================================
        # Dynamic Rank
        # =====================================

        cursor.execute("""

            SELECT

                u.id,

                ROUND(
                    IFNULL(
                        (SUM(q.score)/NULLIF(SUM(q.total_questions),0))*100,
                        0
                    ),
                    2
                ) AS avg_score

            FROM users u

            LEFT JOIN quiz_attempts q

            ON u.id=q.user_id

            GROUP BY u.id

            ORDER BY avg_score DESC

        """)

        ranking = cursor.fetchall()

        rank="-"

        for i,row in enumerate(ranking,start=1):

            if row["id"]==user_id:

                rank=i

                break

    finally:

        cursor.close()
        db.close()

    return render_template(

        "profile.html",

        name=user["full_name"] if user else session["name"],

        email=user["email"] if user else session.get("email",""),

        assessment_score=user["assessment_score"] if user else 0,

        overall_level=overall_level,

        quizzes=quizzes,

        average=average,

        correct=correct,

        wrong=wrong,

        percentage=average,

        time_taken=f"{total_time} sec",

        badge=badge,

        rank=rank,

        subject_levels=subject_levels,

        recent_quizzes=recent_quizzes

    )
# ==========================================================
# Leaderboard
# ==========================================================

@app.route("/leaderboard")
def leaderboard():

    if "user_id" not in session:
        return redirect(url_for("home"))

    user_id = session["user_id"]

    db = get_db_connection()
    cursor = db.cursor(dictionary=True, buffered=True)

    try:

        cursor.execute("""

            SELECT

                u.id AS user_id,

                u.full_name,

                COUNT(q.attempt_id) AS total_quizzes,

                IFNULL(SUM(q.score),0) AS total_score,

                IFNULL(SUM(q.total_questions),0) AS total_questions,

                IFNULL(ROUND(AVG(q.time_taken),2),0) AS avg_time,

                MAX(q.attempt_date) AS last_attempt

            FROM users u

            LEFT JOIN quiz_attempts q

            ON u.id=q.user_id

            GROUP BY u.id

        """)

        data = cursor.fetchall()

        # ======================================
        # Calculate Average %
        # ======================================

        leaderboard = []

        level_points = {
            "Beginner":1,
            "Intermediate":2,
            "Advanced":3
        }

        for student in data:

            if student["total_questions"] > 0:

                average_score = round(

                    (student["total_score"] /
                     student["total_questions"]) * 100,

                    2

                )

            else:

                average_score = 0

            # ---------------------------------
            # Subject-wise Overall Level
            # ---------------------------------

            cursor.execute("""

                SELECT current_level

                FROM user_subject_level

                WHERE user_id=%s

            """,(student["user_id"],))

            levels = cursor.fetchall()

            if levels:

                total = sum(

                    level_points.get(x["current_level"],1)

                    for x in levels

                )

                avg = total / len(levels)

                if avg >= 2.5:
                    overall_level = "Advanced"

                elif avg >= 1.5:
                    overall_level = "Intermediate"

                else:
                    overall_level = "Beginner"

            else:

                overall_level = "Beginner"

            leaderboard.append({

                "user_id":student["user_id"],

                "full_name":student["full_name"],

                "level":overall_level,

                "average_score":average_score,

                "total_quizzes":student["total_quizzes"],

                "avg_time":student["avg_time"],

                "last_attempt":student["last_attempt"]

            })

        # ======================================
        # Sort Leaderboard
        # ======================================

        leaderboard.sort(

            key=lambda x: (

                x["average_score"],

                x["total_quizzes"]

            ),

            reverse=True

        )

        # ======================================
        # User Rank
        # ======================================

        my_rank = "-"

        for i,row in enumerate(leaderboard,start=1):

            if row["user_id"] == user_id:

                my_rank = i

                break

        # ======================================
        # Top 3
        # ======================================

        first = leaderboard[0] if len(leaderboard) > 0 else None

        second = leaderboard[1] if len(leaderboard) > 1 else None

        third = leaderboard[2] if len(leaderboard) > 2 else None

        total_attempts = sum(

            x["total_quizzes"]

            for x in leaderboard

        )

        highest_score = first["average_score"] if first else 0

    finally:

        cursor.close()

        db.close()

    return render_template(

        "leaderboard.html",

        name=session["name"],

        leaderboard=leaderboard,

        my_rank=my_rank,

        total_students=len(leaderboard),

        total_attempts=total_attempts,

        highest_score=highest_score,

        first_name=first["full_name"] if first else "-",

        first_score=first["average_score"] if first else 0,

        second_name=second["full_name"] if second else "-",

        second_score=second["average_score"] if second else 0,

        third_name=third["full_name"] if third else "-",

        third_score=third["average_score"] if third else 0

    )
if __name__ == "__main__":
    app.run(debug=True)