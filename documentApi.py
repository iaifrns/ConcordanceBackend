from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import os
import logging
import database  # Import the database module
DB_NAME = "textretrivalsystem"
app = Flask(__name__)
from flask_cors import CORS

UPLOAD_NEW_FOLDER = 'uploads'
app.config['UPLOAD_NEW_FOLDER'] = UPLOAD_NEW_FOLDER

CORS(app)


@app.route('/upload_document', methods=['POST'])
def upload_document():
    print("Received upload request")
    if 'file' not in request.files:
        logging.error("No file part in request")
        return jsonify({"message": "No file part"}), 400
    document = request.files['file']
    if document.filename == '':
        logging.error("No selected file in request")
        return jsonify({"message": "No selected file"}), 400

    meta_data = {
        'name': request.form.get('name', 'Unknown'),
        'location': request.form.get('location', 'Unknown'),
        'author': request.form.get('author', 'Unknown'),
        'date': request.form.get('date', 'Unknown'),
        'source': request.form.get('source', 'Unknown')
    }
    print(f"Metadata received: {meta_data}")

    if document:
        file_name = secure_filename(document.filename)
        file_path = os.path.join(app.config['UPLOAD_NEW_FOLDER'], file_name)
        document.save(file_path)
        print(f"File saved at {file_path}")

        # Connect to the database
        connection_to_db = database.create_server_connection("localhost", "root", "", DB_NAME)
        print("Connected to the database")

        # Save document metadata and get document ID
        document_id = database.save_document_and_metadata(connection_to_db,file_path, meta_data)
        print(f"Document ID received: {document_id}")

        # Process the document text and store word occurrences
        database.process_text(connection_to_db, document_id, file_path)
        print("Processed the document text and stored word occurrences")

        # Close the database connection
        connection_to_db.close()
        print("Closed the database connection")
        
        return jsonify({"message": "File uploaded successfully", "document_id": document_id}), 200

    logging.error("Unknown error occurred")
    return jsonify({"message": "Unknown error"}), 500

# Create the upload folder if it doesn't exist
if not os.path.exists(UPLOAD_NEW_FOLDER):
    os.makedirs(UPLOAD_NEW_FOLDER)
    print("Created upload folder")


# get all text from document
def read_document(file_path):
    array = []
    try:
        with open(file_path, 'r') as file:
            for line in file:
                words = line.split()
                array.extend(words)
            return array
    except FileNotFoundError:
        print(f"File '{file_path}' not found.")
        return None


# get all expressions
@app.route("/documents_list",methods=['GET'])
def get_all_documents():
    connection = database.create_server_connection("localhost", "root", "", DB_NAME)
    response = []
    filename = request.args.get('filename')
    if filename:
        file_path = "./uploads/"+filename+".txt"
        response = read_document(file_path)
    
    else:
        response = database.fetchAllDocuments(connection)
    
    return jsonify(response), 200

