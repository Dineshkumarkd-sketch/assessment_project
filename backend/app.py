from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
import os
from database import init_db
from routes import api

# Load environment variables
load_dotenv()

def create_app():
    app = Flask(__name__)
    CORS(app)

    # Configuration
    app.config["MONGO_URI"] = os.environ.get("MONGODB_URI", "mongodb://localhost:27017/assessment_db")
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "super-secret-key-change-in-production")

    # Initialize MongoDB connection
    init_db(app)

    # Register blueprints
    app.register_blueprint(api, url_prefix='/api')

    @app.route('/')
    def index():
        return "Assessment API is running"

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
