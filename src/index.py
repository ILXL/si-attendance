from flask import Flask, request, jsonify, send_from_directory
from flask_restful import Resource, Api
import os
import sys

# Ensure src directory is in Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from attendance import Attendance
from flask_cors import CORS

# Configure Flask with static folder for frontend
# On Vercel: Flask runs from /var/task/index.py, frontend should be at /var/task/frontend/public
# Locally: Flask runs from src/index.py, frontend should be at src/frontend/public
current_dir = os.path.dirname(os.path.abspath(__file__))
current_file = os.path.abspath(__file__)

# Start with path relative to this file
frontend_path = os.path.join(current_dir, 'frontend', 'public')

# If we're at /var/task (Vercel), check /var/task/frontend/public
if current_dir == '/var/task' and not os.path.exists(frontend_path):
    frontend_path = '/var/task/frontend/public'

# Try parent directory
if not os.path.exists(frontend_path):
    parent = os.path.dirname(current_dir)
    alt_paths = [
        os.path.join(parent, 'frontend', 'public'),
        os.path.join(parent, 'src', 'frontend', 'public'),
    ]
    for path in alt_paths:
        if os.path.exists(path):
            frontend_path = path
            break

app = Flask(__name__, static_folder=frontend_path, static_url_path='')
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

CORS(app, resources={r"*": {"origins": "*"}})
api = Api(app)


class GetCourses(Resource):
    def get(self):
        args = request.args
        bot = Attendance()
        return bot.GetCourses(args["cwid"])


class SignIn(Resource):
    def get(self):
        args = request.args
        app.logger.info(f"/signin : {args}")
        response = {"message": "request made", "errmessage": ""}
        # response.headers.add("Access-Control-Allow-Origin", "*")
        if not len(args):
            response["errmessage"] = "Did not provide CWID or Course"
            return jsonify(response)
        bot = Attendance()
        try:
            (bot_response, student_name) = bot.signIn(
                cwid=args["cwid"], course=args["course"]
            )
        except:
            response["errmessage"] = "Could not find that CWID."
            return response, 404
        if type(bot_response) == dict:
            response["errmessage"] = bot_response["errmessage"]
        status = "200" if not len(response["errmessage"]) else "400"
        if status == "200":
            result = bot.logToSheet([args["course"], args["cwid"], student_name])
            if not result:
                response['message'] = "Sucessfully signed in but couldn't log to sheet."
        response = jsonify(response)
        response.status = status
        print(f"{response.status=}")
        return response


"""
Special route for logging students with No CWID to a Google Sheet. They will not
be signed into TitanNet
"""


class LogNonCWIDToSheet(Resource):
    def get(self):
        args = request.args
        app.logger.info(f"/noncwidsignin : {args}")
        bot = Attendance()
        bot.logToSheet([args["course"], args["nonCWIDStatus"], args["name"]])


api.add_resource(SignIn, "/signin")
api.add_resource(GetCourses, "/getcourses")
api.add_resource(LogNonCWIDToSheet, "/noncwidsignin")

# Debug endpoint
@app.route('/debug')
def debug():
    return {
        "static_folder": app.static_folder,
        "static_folder_exists": os.path.exists(app.static_folder),
        "index_html_exists": os.path.exists(os.path.join(app.static_folder, 'index.html')),
        "bundle_js_exists": os.path.exists(os.path.join(app.static_folder, 'build', 'bundle.js')),
        "current_file": __file__,
        "current_dir": os.path.dirname(os.path.abspath(__file__))
    }

# Frontend static file serving
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_spa(path):
    # Don't intercept API routes
    if path.startswith('signin') or path.startswith('getcourses') or path.startswith('noncwidsignin'):
        return {"error": "Not Found"}, 404
    
    # Try to serve files (CSS, JS, images, etc.) 
    if '.' in path:
        try:
            return send_from_directory(app.static_folder, path)
        except:
            pass
    
    # Serve index.html for all routes (SPA routing)
    try:
        return send_from_directory(app.static_folder, 'index.html')
    except Exception as e:
        return {"error": f"Could not find index.html: {str(e)}", "static_folder": app.static_folder}, 500
