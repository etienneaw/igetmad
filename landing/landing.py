from flask import jsonify, Response, Blueprint, current_app
import json

# Register app bp
landing = Blueprint('landing', __name__)

@landing.route('/')
def welcome():
    return "JJ, ton app run --> I GET MAD !!"
