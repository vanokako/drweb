from dotenv import load_dotenv
from flask import Flask

from filemanager import routers

load_dotenv()
ui_api = Flask(__name__)

ui_api.register_blueprint(routers.filemanager_bp, url_prefix="/files")


