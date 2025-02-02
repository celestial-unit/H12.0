import subprocess
import os
from flask import Blueprint, url_for, redirect, send_file, render_template

process_3d_bp = Blueprint("process_3d", __name__)

# Use absolute path for the output folder
UPLOAD_FOLDER = "app/static/images"
OUTPUT_FOLDER = os.path.abspath("app/outputs")
PROCESS_SCRIPT = "app/generate_3d.py"

# Define the route for the 3D processing page
@process_3d_bp.route("/process_3d")
def process_3d_home():
    # List all images in the "static/images" directory
    images = os.listdir(UPLOAD_FOLDER)
    images = [image for image in images if image.endswith(('.png', '.jpg', '.jpeg', '.gif'))]  # Optionally filter image types
    return render_template("process_3d_home.html", images=images)

def sanitize_filename(image_name):
    # Remove file extension and sanitize filename
    return os.path.splitext(image_name)[0]

@process_3d_bp.route("/process/<image_name>")
def process_image(image_name):
    image_name = sanitize_filename(image_name)

    video_file = os.path.join(OUTPUT_FOLDER, f"{image_name}_video.mp4")
    glb_file = os.path.join(OUTPUT_FOLDER, f"{image_name}.glb")
    processed_image = os.path.join(OUTPUT_FOLDER, f"{image_name}_processed.png")

    if os.path.exists(video_file) and os.path.exists(glb_file) and os.path.exists(processed_image):
        return redirect(url_for("process_3d.view_results", image_name=image_name))

    try:
        # Run the 3D generation script and capture stdout/stderr
        result = subprocess.run(
            ["python", PROCESS_SCRIPT, image_name],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        # Log any output or error from the script
        print("Standard Output:", result.stdout.decode())
        print("Standard Error:", result.stderr.decode())

        # Check if files were created
        if os.path.exists(video_file) and os.path.exists(glb_file) and os.path.exists(processed_image):
            return redirect(url_for("process_3d.view_results", image_name=image_name))
        else:
            return f"Files not generated: {video_file}, {glb_file}, {processed_image}", 500

    except subprocess.CalledProcessError as e:
        # Print error details
        print("Error while processing the image:", e.stderr.decode())
        return f"Error processing image: {e.stderr.decode()}", 500


@process_3d_bp.route("/results/<image_name>")
def view_results(image_name):
    image_name = sanitize_filename(image_name)  
    video_file = f"{image_name}_video.mp4"
    glb_file = f"{image_name}.glb"
    processed_image = f"{image_name}_processed.png"

    return render_template("results.html",
                           image_name=image_name,
                           video_path=video_file,
                           glb_path=glb_file,
                           processed_image=processed_image)

@process_3d_bp.route("/output/<filename>")
def get_output(filename):
    file_path = os.path.join(OUTPUT_FOLDER, filename)
    if not os.path.exists(file_path):
        return "File not found", 404
    return send_file(file_path)
