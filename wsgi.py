from src import create_app
from flask_cors import CORS

app = create_app()
CORS(app, resources={r"/*": {"origins": "*"}})
