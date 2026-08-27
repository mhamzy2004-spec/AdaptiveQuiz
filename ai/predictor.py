import joblib
import pandas as pd

# ==========================================
# Load Model
# ==========================================

model = joblib.load("ai/model.pkl")

level_encoder = joblib.load("ai/level_encoder.pkl")

next_level_encoder = joblib.load("ai/next_level_encoder.pkl")


# ==========================================
# Predict Level
# ==========================================

def predict_level(
        assessment_score,
        subject_id,
        quiz_score,
        quiz_percentage,
        time_taken,
        current_level
):

    current_level_encoded = level_encoder.transform(
        [current_level]
    )[0]

    sample = pd.DataFrame([{

        "assessment_score": assessment_score,

        "subject_id": subject_id,

        "quiz_score": quiz_score,

        "quiz_percentage": quiz_percentage,

        "time_taken": time_taken,

        "current_level": current_level_encoded

    }])

    prediction = model.predict(sample)

    predicted_level = next_level_encoder.inverse_transform(
        prediction
    )[0]

    return predicted_level


# ==========================================
# Testing
# ==========================================

if __name__ == "__main__":

    level = predict_level(

        assessment_score=8,

        subject_id=2,

        quiz_score=9,

        quiz_percentage=90,

        time_taken=180,

        current_level="Intermediate"

    )

    print(level)