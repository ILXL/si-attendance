from flask import Flask, request, jsonify, send_from_directory
from flask_restful import Resource, Api
import os
import sys

# Ensure src directory is in Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from attendance import Attendance
from flask_cors import CORS

# Configure Flask
# Serve static files from static/ subdirectory
current_dir = os.path.dirname(os.path.abspath(__file__))
static_dir = os.path.join(current_dir, 'static')

app = Flask(__name__, static_folder=static_dir, static_url_path='/')
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
    import os
    index_path = os.path.join(os.getcwd(), 'public', 'index.html')
    bundle_path = os.path.join(os.getcwd(), 'public', 'build', 'bundle.js')
    
    return {
        "app_root": app.root_path,
        "cwd": os.getcwd(),
        "index_html_exists": os.path.exists(index_path),
        "index_html_path": index_path,
        "bundle_js_exists": os.path.exists(bundle_path),
        "bundle_js_path": bundle_path,
        "public_dir_contents": os.listdir(os.path.join(os.getcwd(), 'public')) if os.path.exists(os.path.join(os.getcwd(), 'public')) else "NOT FOUND",
        "message": "Frontend should be served by Vercel's catch-all route (/(.*) -> /index.html)"
    }

# Minimal SPA fallback - Vercel handles static files, we just return JSON for API errors
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_spa(path):
    # Don't intercept API routes
    if path.startswith('signin') or path.startswith('getcourses') or path.startswith('noncwidsignin') or path.startswith('debug'):
        return {"error": "Not Found"}, 404
    
    # Try to serve static files (images, CSS, JS)
    if '.' in path:
        try:
            return send_from_directory(app.static_folder, path)
        except:
            pass
    
    # For SPA, serve index.html for all non-API routes
    try:
        return send_from_directory(app.static_folder, 'index.html')
    except Exception as e:
        return {"error": f"Could not find index.html: {str(e)}", "public_folder": app.static_folder, "public_exists": os.path.exists(app.static_folder)}, 500
