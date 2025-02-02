from gradio_client import Client, handle_file
import shutil
import os

# Get Hugging Face token from environment variable
hf_token = os.getenv('HF_TOKEN')
if not hf_token:
    raise ValueError("HF_TOKEN environment variable is not set. Please set your Hugging Face token as HF_TOKEN.")

# Initialize Gradio client
client = Client("JeffreyXiang/TRELLIS", hf_token=hf_token)

# Output folder
OUTPUT_FOLDER = "outputs"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def sanitize_filename(image_name):
    """ Ensure file name is used correctly without duplicate extensions """
    return os.path.splitext(image_name)[0]  # Removes extra extensions like `.png.png`

def generate_3d(image_name):
    """
    Generate a 3D model from an image, but skip processing if cached results exist.
    """
    image_name = sanitize_filename(image_name)  # Ensure correct filename handling

    # Define input/output paths
    input_image = os.path.join("static/images", f"{image_name}.png")  # Image from uploads
    processed_image = os.path.join(OUTPUT_FOLDER, f"{image_name}_processed.png")  # Preprocessed image
    output_video = os.path.join(OUTPUT_FOLDER, f"{image_name}_video.mp4")  # 3D generated video
    output_glb = os.path.join(OUTPUT_FOLDER, f"{image_name}.glb")  # GLB model

    # ✅ **Check if cached files exist (Skip generation if available)**
    if os.path.exists(output_video) and os.path.exists(output_glb) and os.path.exists(processed_image):
        print(f"✅ Cached results found for {image_name}. Skipping generation.")
        return processed_image, output_video, output_glb

    # ❌ **Check if input image exists before processing**
    if not os.path.exists(input_image):
        print(f"❌ Error: Input image {input_image} does not exist.")
        return None, None, None

    try:
        print(f"🚀 Generating 3D model for {image_name}...")

        # Start session
        client.predict(api_name="/start_session")

        # Call lambda API
        client.predict(api_name="/lambda")

        # Preprocess the image
        result = client.predict(image=handle_file(input_image), api_name="/preprocess_image")
        shutil.copy(result, processed_image)
        print(f"✅ Preprocessed image saved: {processed_image}")

        # Get seed for 3D generation
        client.predict(randomize_seed=True, seed=0, api_name="/get_seed")

        # Convert the image to 3D video
        result = client.predict(
            image=handle_file(input_image),
            multiimages=[],
            seed=0,
            ss_guidance_strength=7.5,
            ss_sampling_steps=12,
            slat_guidance_strength=3,
            slat_sampling_steps=12,
            multiimage_algo="stochastic",
            api_name="/image_to_3d"
        )
        shutil.copy(result['video'], output_video)
        print(f"✅ 3D video saved: {output_video}")

        # Extract the 3D model as a GLB file
        result = client.predict(mesh_simplify=0.95, texture_size=1024, api_name="/extract_glb")
        shutil.copy(result[1], output_glb)
        print(f"✅ GLB file saved: {output_glb}")

        return processed_image, output_video, output_glb

    except Exception as e:
        print(f"❌ Error in 3D generation: {e}")
        return None, None, None

# ✅ **Run only when script is executed**
if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("❌ Error: No image name provided.")
    else:
        image_name = sys.argv[1]
        generate_3d(image_name)
