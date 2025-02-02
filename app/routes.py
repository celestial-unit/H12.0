from flask import Blueprint, render_template, request, redirect, url_for
import os

main_bp = Blueprint("main", __name__)

# Route for the home page (index with buttons)
@main_bp.route("/")
def home():
    return render_template("index.html")

# Route for the artifact-related page (Prediction model)
@main_bp.route("/predict")
def artifact():
    return render_template("index_artifact.html")

# Route for the chatbot-related page
@main_bp.route("/chatbot")
def chatbot():
    return render_template("index_chatbot.html")


# Route for the upload functionality
@main_bp.route("/upload", methods=["POST"])
def upload():
    if "image" not in request.files:
        return redirect(url_for("main.home"))

    file = request.files["image"]
    if file.filename == "":
        return redirect(url_for("main.home"))

    filepath = os.path.join("static/images", file.filename)
    file.save(filepath)

    # Redirect to the process_3d_home route after upload
    return redirect(url_for("process_3d.process_3d_home"))
# Route for displaying uploaded     images
@main_bp.route("/results")
def results():
    images = os.listdir("static/images")
    return render_template("results.html", images=images)
