from flask import Flask, render_template, request
from supabase import create_client
from dotenv import load_dotenv
import os
import uuid

# Load .env
load_dotenv()

app = Flask(__name__)

# -----------------------------
# Supabase Configuration
# -----------------------------

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError(
        "SUPABASE_URL and SUPABASE_KEY must be set in the .env file"
    )

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)

# Your Supabase Storage bucket
BUCKET_NAME = "Zen"


# -----------------------------
# Home Page
# -----------------------------

@app.route("/")
def index():
    return render_template("index.html")


# -----------------------------
# Image Upload
# -----------------------------

@app.route("/upload", methods=["POST"])
def upload():

    # Check whether image exists
    if "image" not in request.files:
        return "No image selected", 400

    image = request.files["image"]

    # Check filename
    if image.filename == "":
        return "Please select an image", 400

    try:
        # -----------------------------
        # Get file extension
        # -----------------------------
        file_extension = os.path.splitext(image.filename)[1].lower()

        # -----------------------------
        # Create unique filename
        # Example:
        # 89ffe638-e756-42d9-a29f-903048c8630e.jpg
        # -----------------------------
        file_name = f"{uuid.uuid4()}{file_extension}"

        # -----------------------------
        # Read image
        # -----------------------------
        image_data = image.read()

        print("Uploading:", file_name)
        print("Content Type:", image.content_type)
        print("Bucket:", BUCKET_NAME)

        # -----------------------------
        # Upload to Supabase Storage
        # -----------------------------
        response = supabase.storage.from_(BUCKET_NAME).upload(
            file_name,
            image_data,
            file_options={
                "content-type": image.content_type
            }
        )

        print("Supabase upload response:", response)

        # -----------------------------
        # Get public URL
        # -----------------------------
        public_url = supabase.storage.from_(
            BUCKET_NAME
        ).get_public_url(file_name)

        print("Public URL:", public_url)

        # -----------------------------
        # Show uploaded image
        # -----------------------------
        return render_template(
            "image.html",
            image_url=public_url,
            file_name=file_name
        )

    except Exception as e:

        print("UPLOAD ERROR:", repr(e))

        return f"Upload failed: {str(e)}", 500


# -----------------------------
# Run Flask
# -----------------------------

if __name__ == "__main__":
    app.run(
        debug=True
    )