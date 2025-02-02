import tensorflow as tf
import numpy as np
import json
from flask import Blueprint, request, jsonify
from PIL import Image
import io

predict_bp = Blueprint("predict", __name__)

# Load model and class labels
model = tf.keras.models.load_model("models/artifact_classifier.h5")
with open("models/class_labels.json", "r") as f:
    class_labels = json.load(f)

def preprocess_image(image_data):
    img = Image.open(io.BytesIO(image_data))
    img = img.resize((224, 224))
    img_array = np.array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)
    return img_array

@predict_bp.route("/predict", methods=["POST"])
def predict():
    if "file" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    file = request.files["file"]
    img_array = preprocess_image(file.read())

    predictions = model.predict(img_array)
    predicted_class = np.argmax(predictions)

    if predicted_class < len(class_labels):
        result = {"prediction": class_labels[predicted_class], "confidence": float(np.max(predictions))}
    else:
        result = {"error": "Invalid prediction index"}

    return jsonify(result)
