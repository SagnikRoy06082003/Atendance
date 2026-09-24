import cv2
import numpy as np
import os
import csv
from datetime import datetime

# Paths
MODEL_FILE = "face_model.yml"
LABELS_FILE = "labels.npy"
ATTENDANCE_FILE = "attendance.csv"

# Load trained recognizer and labels
recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read(MODEL_FILE)
labels = np.load(LABELS_FILE, allow_pickle=True).item()

# Load Haar cascade for face detection
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

# Attendance tracking
attendance_data = {}

# For evaluation
true_positives = 0
false_positives = 0
false_negatives = 0
predicted_present = set()

# Ground truth — list of students who were actually present (manually provide)
ground_truth_present = {"Alice", "Bob", "Charlie"}  # Example names

# Open webcam
cap = cv2.VideoCapture(0)
print("Press 'q' to stop and save attendance.")

while True:
    ret, frame = cap.read()
    if not ret:
        continue

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=5, minSize=(30, 30))

    for (x, y, w, h) in faces:
        face_roi = gray[y:y+h, x:x+w]
        label_id, confidence = recognizer.predict(face_roi)

        if confidence < 65:
            name = labels.get(label_id, "Unknown")
        else:
            name = "Unknown"

        # Record attendance
        if name != "Unknown":
            predicted_present.add(name)

            if name not in attendance_data:
                attendance_data[name] = {"entry_time": datetime.now(), "exit_time": None}
            attendance_data[name]["exit_time"] = datetime.now()

        # Draw rectangle and label
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.putText(frame, name, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

    cv2.imshow("Face Recognition Attendance", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# Close camera
cap.release()
cv2.destroyAllWindows()

# Save attendance to CSV
file_exists = os.path.isfile(ATTENDANCE_FILE)
with open(ATTENDANCE_FILE, "a", newline="") as file:
    writer = csv.writer(file)
    if not file_exists:
        writer.writerow(["Student Name", "Entry Time", "Exit Time", "Duration (minutes)", "Status"])

    for name, times in attendance_data.items():
        entry_time = times["entry_time"]
        exit_time = times["exit_time"]
        duration = (exit_time - entry_time).total_seconds()
        status = "Present" if duration > 10 else "Absent"

        writer.writerow([name, entry_time.strftime("%Y-%m-%d %H:%M:%S"), exit_time.strftime("%Y-%m-%d %H:%M:%S"), round(duration, 2), status])

# === Evaluation ===
for name in ground_truth_present:
    if name in predicted_present:
        true_positives += 1
    else:
        false_negatives += 1

for name in predicted_present:
    if name not in ground_truth_present:
        false_positives += 1

precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0

print("\n📊 Evaluation Metrics:")
print(f"✔ True Positives: {true_positives}")
print(f"❌ False Positives: {false_positives}")
print(f"⚠ False Negatives: {false_negatives}")
print(f"🎯 Precision: {precision:.2f}")
print(f"📈 Recall (Sensitivity): {recall:.2f}")
print("✅ Attendance saved successfully!")
