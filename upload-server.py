import os
import uuid
import csv

from flask import (Flask,
                   request,
                   render_template,
                   jsonify,
                   send_from_directory)

# Local imports
import labels


app = Flask(__name__)


@app.route('/parse-file', methods=['POST'])
def parse_file():
    f = request.files['0']
    response = {
        "success": True
    }
    try:
        labels.saveLabelDataFile(f)
    except Exception as e:
        print("Failed")
        print(str(e))
        response = {
            "success": False,
            "error_message": str(e)
        }
    
    return jsonify(response), 200


@app.route('/', methods=['GET'])
def main():
    return render_template("index.html")


@app.errorhandler(404)
def not_found(e):
    message = "404 We couldn't find the page"
    return render_template("index.html", error_message=message)


if __name__ == "__main__":
    IS_PROD = os.environ.get("PRODUCTION", False)
    app.run(debug=not IS_PROD, host="0.0.0.0", threaded=True)
