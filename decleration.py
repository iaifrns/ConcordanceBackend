from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import database  # Import the database module
DB_NAME = "textretrivalsystem"
app = Flask(__name__)
from flask_cors import CORS

UPLOAD_NEW_FOLDER = 'uploads'
app.config['UPLOAD_NEW_FOLDER'] = UPLOAD_NEW_FOLDER

CORS(app)


# get all expressions
@app.route("/declerations",methods=['GET'])
def get_all_declerations():
    connection = database.create_server_connection("localhost", "root", "", DB_NAME)
    response = database.fetchAllExpressions(connection)
    
    return jsonify(response), 200



# save expression to db
@app.route('/decleration', methods=['POST'])
def save_decleration():
    data = request.json
    connection = database.create_server_connection("localhost", "root", "", DB_NAME)
    result = database.save_expression_to_db(connection,(data['decleration'],data['words_decleration']))
    
    if result:
        return jsonify({"message": "Expression saved successfully !!!"}), 200
    else:
        return jsonify({"message": "An error occured while saving expression "}), 500

