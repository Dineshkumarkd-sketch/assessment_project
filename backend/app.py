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

    # MongoDB
    app.config["MONGO_URI"] = os.environ.get("MONGODB_URI")

    # Secret Key
    app.config["SECRET_KEY"] = os.environ.get(
        "SECRET_KEY",
        "change-this-to-a-random"
    )

    print("MONGO_URI =", app.config["MONGO_URI"])
    print("SECRET_KEY Loaded =", app.config["SECRET_KEY"])

    if not app.config["MONGO_URI"]:
        raise Exception("MONGODB_URI not found")

    init_db(app)

    app.register_blueprint(api, url_prefix="/api")

    @app.route("/")
    def home():
        return "API Running"

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, use_reloader=False)