from flask import Flask
from flask_migrate import Migrate
from dotenv import load_dotenv
from models import db
from routes import routes
import os


load_dotenv('.env')

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate = Migrate(app, db)

app.register_blueprint(routes)

if __name__ == "__main__":
    app.run(debug=True)
