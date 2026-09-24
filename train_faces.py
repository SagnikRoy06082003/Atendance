import cv2
import os
import numpy as np

# Paths
DATASET_DIR = "faces"
MODEL_FILE = "face_model.yml"
LABELS_FILE = "labels.npy"

# Create LBPH Face Recognizer
recognizer = cv2.face.LBPHFaceRecognizer_create()
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

# Prepare training data
labels = {}
faces = []
ids = []
current_id = 0

for filename in os.listdir(DATASET_DIR):
    if filename.endswith(".jpg") or filename.endswith(".png"):
        img_path = os.path.join(DATASET_DIR, filename)
        img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
        face = face_cascade.detectMultiScale(img, scaleFactor=1.2, minNeighbors=5, minSize=(30, 30))

        if len(face) > 0:
            (x, y, w, h) = face[0]  # Take the first detected face
            face_roi = img[y:y+h, x:x+w]

            labels[current_id] = os.path.splitext(filename)[0]  # Filename as label (without extension)
            faces.append(face_roi)
            ids.append(current_id)
            current_id += 1

# Train the recognizer
if len(faces) > 0:
    recognizer.train(faces, np.array(ids))
    recognizer.save(MODEL_FILE)
    np.save(LABELS_FILE, labels)

    print("✅ Model trained successfully!")
else:
    print("⚠️ No faces found in dataset!") 