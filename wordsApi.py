from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import os
import database  # Import the database module
DB_NAME = "textretrivalsystem"
app = Flask(__name__)
from flask_cors import CORS

UPLOAD_NEW_FOLDER = 'uploads'
app.config['UPLOAD_NEW_FOLDER'] = UPLOAD_NEW_FOLDER

CORS(app)


@app.route('/word_list', methods=['GET'])
def get_word_list():
    print("Received words request")
    connection_to_db = database.create_server_connection("localhost", "root", "", DB_NAME)
    # Fetch filters from request arguments
    doc_id = request.args.get('doc_id')
    starting_letter = request.args.get('startingLetter')
    paragraph = request.args.get('paragraph')
    sentence = request.args.get('sentence')
    line_number = request.args.get('lineNumber')
    line_range = request.args.get('lineRange')
    print(f"Filters received: doc_id={doc_id}, starting_letter={starting_letter}, paragraph={paragraph}, sentence={sentence}, line_number={line_number}, line_range={line_range}")
    # Call a new function to get filtered words
    words = database.get_filtered_words(connection_to_db, doc_id, starting_letter, paragraph, sentence, line_number, line_range)
    print(f"Received words: {words}")
    response = []
    for word in words:
        response.append(word[0])
    return jsonify(response)


@app.route('/word_context', methods=['GET'])
def get_word_context():
    print("Received word context request")
    word = request.args.get('word')
    print(f"Request Params: {request.args}")
    if not word:
        print("Word parameter is missing in request")
        return jsonify({"error": "Word parameter is required"}), 400
    # Replace this line in your Flask endpoints
    connection_to_db = database.create_server_connection("localhost", "root", "", DB_NAME)
    document_id = request.args.get('doc_id')
    paragraph_content = request.args.get('paragraph')
    sentence_content = request.args.get('sentence')
    line_number = request.args.get('lineNumber')
    line_range = request.args.get('lineRange')
    print(f"Filters received: word={word}, doc_id={document_id}, paragraph={paragraph_content}, sentence={sentence_content}, line_number={line_number}, line_range={line_range}")
    # Call a new function to get word context with filters
    contexts = database.get_word_contexts(connection_to_db, word, document_id, paragraph_content, sentence_content, line_number, line_range)
    response = []
    for context in contexts:
        word, sentence_no, para_no, doc_name = context
        file_path = os.path.join(app.config['UPLOAD_NEW_FOLDER'], doc_name + '.txt')
        context_paragraph = database.get_surrounding_sentences(file_path, sentence_no, para_no)
        context_dict = {
            'word': word,
            'sentence_no': int(sentence_no),
            'paragraph_no': int(para_no),
            'doc_name': doc_name,
            'context_paragraph': context_paragraph
        }
        
        response.append(context_dict)
        
    response.sort(key=lambda x: (x['paragraph_no'], x['sentence_no']))
    print(f"Received contexts: {response}")
    return jsonify(response)


# 
@app.route('/word_group', methods=['POST'])
def save_word_group():
    data = request.json
    
    connection = database.create_server_connection("localhost", "root", "", DB_NAME)
    result = database.save_group_to_db(connection,(data['name'],))
    
    if result:
        return jsonify({"message": "Group saved successfully !!!"}), 200
    else:
        return jsonify({"message": "An error occured while saving group "}), 500
    

@app.route('/word_group/add_word', methods=['POST'])
def save_word_to_group():
    data = request.json
    
    connection = database.create_server_connection("localhost", "root", "", DB_NAME)
    result = database.save_word_to_group_in_db(connection,(data['group_id'],data['word']))
    
    if result:
        return jsonify({"message": "Word added to group successfully !!!"}), 200
    else:
        return jsonify({"message": "An error occured while saving the word in the group "}), 500
    

# get all words of a particular group_id
@app.route("/word_group/word_list",methods=['GET'])
def get_all_words_groups():
    connection = database.create_server_connection("localhost", "root", "", DB_NAME)
    groupe_id = request.args.get('group_id')
    response = database.fetchAllWordInGroups(connection,groupe_id)
    
    return jsonify(response), 200


@app.route("/word_group",methods=['GET'])
def get_all_groups():
    connection = database.create_server_connection("localhost", "root", "", DB_NAME)
    response = database.fetchAllGroups(connection)
    
    return jsonify(response), 200
