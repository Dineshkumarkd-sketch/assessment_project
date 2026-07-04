from flask_pymongo import PyMongo

mongo = PyMongo()

def init_db(app):
    mongo.init_app(app)
    # Ping the database to ensure connection works (optional)
    try:
        if mongo.db is not None:
            mongo.db.command('ping')
            print("Successfully connected to MongoDB!")
    except Exception as e:
        print(f"Failed to connect to MongoDB: {e}")
