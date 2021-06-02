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


@app.route('/upload-file', methods=['POST'])
def upload_file():
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

@app.route('/print-file', methods=['POST'])
def print_file():
    f = request.files['0']
    response = {
        "success": True
    }
    try:
        labels.printCSV(f)
    except Exception as e:
        print("print-file Failed")
        print(str(e))
        response = {
            "success": False,
            "error_message": str(e)
        }
    
    return jsonify(response), 200    

@app.route('/print-single-label', methods=['POST'])
def print_single_label():
    try:
        customer = request.form.get('customer')
        cultivar = request.form.get('cultivar')
        tray = request.form.get('tray_number')
        lot = request.form.get('lot_number')

        lsg = labels.LabelSet(customer, cultivar, lot, tray)
        labels.printLabel([(lsg, tray)])

        response = { "success": True}

    except Exception as e:
        print("print-single-label failed")
        print(str(e))
        response = {
            "success": False,
            "error_message": str(e)
        }
    
    return jsonify(response)


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
