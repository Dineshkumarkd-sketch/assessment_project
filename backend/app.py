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

    mongo_uri = os.environ.get("MONGODB_URI")
    print("MONGO_URI =", mongo_uri)

    app.config["MONGO_URI"] = mongo_uri
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev")

    init_db(app)

    app.register_blueprint(api, url_prefix="/api")

    @app.route("/")
    def index():
        return "API Running"

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, use_reloader=False)