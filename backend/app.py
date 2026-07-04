from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
import os
from database import init_db
from routes import api

# 🔥 FORCE LOAD .env
load_dotenv(dotenv_path=".env")

def create_app():
    app = Flask(__name__)
    CORS(app)

    mongo_uri = os.environ.get("MONGODB_URI")
    print("MONGO_URI =", mongo_uri)

    # ❌ STOP CRASH
    if not mongo_uri:
        raise Exception("MONGODB_URI not found in environment")

    app.config["MONGO_URI"] = mongo_uri
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")

    init_db(app)

    app.register_blueprint(api, url_prefix="/api")

    @app.route("/")
    def index():
        return "API Running"

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, use_reloader=False)