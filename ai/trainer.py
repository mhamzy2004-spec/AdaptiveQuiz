import os
import joblib
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix
)

# ==========================================
# Create Graph Folder
# ==========================================

os.makedirs("ai/graph_output", exist_ok=True)

# ==========================================
# Load Dataset
# ==========================================

df = pd.read_csv("datasets/student_history.csv")

print("Dataset Loaded Successfully")
print(df.head())

# ==========================================
# Encode Labels
# ==========================================

level_encoder = LabelEncoder()
next_level_encoder = LabelEncoder()

df["current_level"] = level_encoder.fit_transform(df["current_level"])
df["next_level"] = next_level_encoder.fit_transform(df["next_level"])

# ==========================================
# Features
# ==========================================

X = df[
    [
        "assessment_score",
        "subject_id",
        "quiz_score",
        "quiz_percentage",
        "time_taken",
        "current_level"
    ]
]

y = df["next_level"]

# ==========================================
# Train Test Split
# ==========================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42
)

# ==========================================
# Random Forest Model
# ==========================================

model = RandomForestClassifier(
    n_estimators=300,
    random_state=42
)

model.fit(X_train, y_train)

# ==========================================
# Prediction
# ==========================================

prediction = model.predict(X_test)

accuracy = accuracy_score(y_test, prediction)

print("\nAccuracy :", accuracy)

print("\nClassification Report\n")
print(classification_report(y_test, prediction))

print("\nConfusion Matrix\n")

cm = confusion_matrix(y_test, prediction)

print(cm)  
# ==========================================
# GRAPH 1 : Confusion Matrix
# ==========================================

plt.figure(figsize=(8,6))

sns.heatmap(
    cm,
    annot=True,
    fmt="d",
    cmap="Blues",
    linewidths=1,
    linecolor="white",
    xticklabels=next_level_encoder.classes_,
    yticklabels=next_level_encoder.classes_
)

plt.title("Confusion Matrix", fontsize=18, fontweight="bold")
plt.xlabel("Predicted Level", fontsize=12)
plt.ylabel("Actual Level", fontsize=12)

plt.tight_layout()

plt.savefig(
    "ai/graph_output/confusion_matrix.png",
    dpi=300
)

plt.close()

# ==========================================
# GRAPH 2 : Accuracy
# ==========================================

plt.figure(figsize=(6,5))

bars = plt.bar(
    ["Random Forest"],
    [accuracy * 100],
    color="#1976D2",
    width=0.4
)

plt.ylim(0,100)

plt.ylabel("Accuracy (%)", fontsize=12)

plt.title(
    "Model Accuracy",
    fontsize=16,
    fontweight="bold"
)

for bar in bars:

    yval = bar.get_height()

    plt.text(
        bar.get_x()+bar.get_width()/2,
        yval+1,
        f"{yval:.2f}%",
        ha='center',
        fontsize=11,
        fontweight='bold'
    )

plt.tight_layout()

plt.savefig(
    "ai/graph_output/accuracy.png",
    dpi=300
)

plt.close()

# ==========================================
# GRAPH 3 : Feature Importance
# ==========================================

importance = model.feature_importances_

features = X.columns

plt.figure(figsize=(9,6))

plt.barh(
    features,
    importance,
    color="#42A5F5"
)

plt.title(
    "Feature Importance",
    fontsize=16,
    fontweight="bold"
)

plt.xlabel("Importance Score")

plt.grid(axis="x", linestyle="--", alpha=0.4)

plt.tight_layout()

plt.savefig(
    "ai/graph_output/feature_importance.png",
    dpi=300
)

plt.close() 
# ==========================================
# GRAPH 4 : Student Level Distribution
# ==========================================

plt.figure(figsize=(8,5))

labels = next_level_encoder.classes_

counts = df["next_level"].value_counts().sort_index()

colors = ["#BBDEFB", "#64B5F6", "#1976D2"]

plt.bar(labels, counts, color=colors)

plt.title(
    "Student Level Distribution",
    fontsize=16,
    fontweight="bold"
)

plt.xlabel("Learning Level")
plt.ylabel("Number of Students")

for i, value in enumerate(counts):

    plt.text(
        i,
        value + 5,
        str(value),
        ha="center",
        fontsize=10,
        fontweight="bold"
    )

plt.tight_layout()

plt.savefig(
    "ai/graph_output/class_distribution.png",
    dpi=300
)

plt.close()

# ==========================================
# GRAPH 5 : Quiz Percentage Distribution
# ==========================================

plt.figure(figsize=(8,5))

plt.hist(
    df["quiz_percentage"],
    bins=10,
    color="#42A5F5",
    edgecolor="black"
)

plt.title(
    "Quiz Percentage Distribution",
    fontsize=16,
    fontweight="bold"
)

plt.xlabel("Quiz Percentage")
plt.ylabel("Students")

plt.grid(alpha=0.3)

plt.tight_layout()

plt.savefig(
    "ai/graph_output/quiz_distribution.png",
    dpi=300
)

plt.close()

# ==========================================
# GRAPH 6 : Time Taken Distribution
# ==========================================

plt.figure(figsize=(8,5))

plt.hist(
    df["time_taken"],
    bins=10,
    color="#1976D2",
    edgecolor="black"
)

plt.title(
    "Time Taken Distribution",
    fontsize=16,
    fontweight="bold"
)

plt.xlabel("Time Taken (Seconds)")
plt.ylabel("Students")

plt.grid(alpha=0.3)

plt.tight_layout()

plt.savefig(
    "ai/graph_output/time_distribution.png",
    dpi=300
)

plt.close()

print("\nGraphs Saved Successfully")

# ==========================================
# Save Model & Encoders
# ==========================================

joblib.dump(model, "ai/model.pkl")
joblib.dump(level_encoder, "ai/level_encoder.pkl")
joblib.dump(next_level_encoder, "ai/next_level_encoder.pkl")

print("\nModel Saved Successfully")