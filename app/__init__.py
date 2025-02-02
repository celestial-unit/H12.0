from flask import Flask
import os

def create_app():
    app = Flask(__name__)

    # Configurations
    app.config["UPLOAD_FOLDER"] = "static/images"
    app.config["OUTPUT_FOLDER"] = "static/outputs"

    # Ensure directories exist
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    os.makedirs(app.config["OUTPUT_FOLDER"], exist_ok=True)

    # Register Blueprints (modular routing)
    from app.routes import main_bp
    from app.predict import predict_bp
    from app.process_3d import process_3d_bp
    from app.chatbot import chatbot_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(predict_bp)
    app.register_blueprint(process_3d_bp)
    app.register_blueprint(chatbot_bp)

    return app
