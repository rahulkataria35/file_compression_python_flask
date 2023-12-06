"""main.py"""
import sys
import os
import requests
from flask import Flask, request, jsonify
from image_compressor import img_compressor_app



app = Flask(__name__)

app.register_blueprint(img_compressor_app)


env_not_found = "env not found"
code_update_time = os.getenv("code_update_time", env_not_found)
latest_commit_author = os.getenv("latest_commit_author", env_not_found)
latest_commit_time = os.getenv("latest_commit_time", env_not_found)

@app.route("/python_api/status", methods=['POST', 'GET'])
def hello():
    """
    :return: status api added
    """
    # return jsonify({"status":"UP"})

    ip = requests.get('https://api.ipify.org').text
    return jsonify({"status": 200,
                    "message": [
                        "Hello World from Flask in a uWSGI Nginx Docker container with  ",
                        "Python {}.{} (This is address-matching).".format(
                            sys.version_info.major,
                            sys.version_info.minor),
                        "Updated time: {}".format(code_update_time),
                        "Latest Commit Author: {}".format(latest_commit_author),
                        "Latest Commit Time: {}".format(latest_commit_time),
                        "Ip of deployment Server: {}".format(ip)]
                    })


if __name__ == "__main__":
    app.run(debug=False)
