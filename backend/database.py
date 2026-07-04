from flask_pymongo import PyMongo

mongo = PyMongo()

def init_db(app):
    mongo.init_app(app)

    try:
        # ❌ DO NOT use app_context here
        mongo.db.command("ping")
        print("✅ MongoDB connected successfully!")
    except Exception as e:
        print("❌ MongoDB error:", str(e))