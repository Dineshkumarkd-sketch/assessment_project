from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
import os
from database import init_db
from routes import api

load_dotenv()

def create_app():
    app = Flask(__name__)
    CORS(app)

    app.config["MONGO_URI"] = os.environ.get(
        "MONGODB_URI",
        "mongodb://localhost:27017/assessment_db"
    )

    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")

    # ✅ FIX HERE
    with app.app_context():
        init_db(app)

    app.register_blueprint(api, url_prefix='/api')

    @app.route('/')
    def index():
        return "Assessment API is running"

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, use_reloader=False)