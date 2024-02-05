from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import os
import logging
import database  # Import the database module
DB_NAME = "concordance"
app = Flask(__name__)
from flask_cors import CORS

UPLOAD_NEW_FOLDER = 'uploads'
app.config['UPLOAD_NEW_FOLDER'] = UPLOAD_NEW_FOLDER

CORS(app)

# Create the upload folder if it doesn't exist
if not os.path.exists(UPLOAD_NEW_FOLDER):
    os.makedirs(UPLOAD_NEW_FOLDER)
    logging.info("Created upload folder")

# get all text from document
def read_file(file_path):
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
@app.route("/documents",methods=['GET'])
def getAllDocuments():
    connection = database.create_server_connection("localhost", "root", "", DB_NAME)
    response = []
    filename = request.args.get('filename')
    if filename:
        file_path = "./uploads/"+filename+".txt"
        response = read_file(file_path)
    
    else:
        response = database.fetchAllDocuments(connection)
    
    return jsonify(response), 200

@app.route('/upload', methods=['POST'])
def upload_file():
    logging.info("Received upload request")
    if 'file' not in request.files:
        logging.error("No file part in request")
        return jsonify({"message": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        logging.error("No selected file in request")
        return jsonify({"message": "No selected file"}), 400

    meta_data = {
        'name': request.form.get('name', 'Unknown'),
        'location': request.form.get('location', 'Unknown'),
        'author': request.form.get('author', 'Unknown'),
        'date': request.form.get('date', 'Unknown'),
        'source': request.form.get('source', 'Unknown')
    }
    logging.info(f"Metadata received: {meta_data}")

    if file:
        file_name = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_NEW_FOLDER'], file_name)
        file.save(file_path)
        logging.info(f"File saved at {file_path}")

        # Connect to the database
        connection_to_db = database.create_server_connection("localhost", "root", "", DB_NAME)
        logging.info("Connected to the database")

        # Save document metadata and get document ID
        document_id = database.save_document_and_metadata(connection_to_db,file_path, meta_data)
        logging.info(f"Document ID received: {document_id}")

        # Process the document text and store word occurrences
        database.process_text(connection_to_db, document_id, file_path)
        logging.info("Processed the document text and stored word occurrences")

        # Close the database connection
        connection_to_db.close()
        logging.info("Closed the database connection")
        
        return jsonify({"message": "File uploaded successfully", "document_id": document_id}), 200

    logging.error("Unknown error occurred")
    return jsonify({"message": "Unknown error"}), 500



@app.route('/word-context', methods=['GET'])
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



@app.route('/words', methods=['GET'])
def get_words():
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



# 
@app.route('/group', methods=['POST'])
def saveGroup():
    data = request.json
    
    connection = database.create_server_connection("localhost", "root", "", DB_NAME)
    result = database.save_group_to_db(connection,(data['name'],))
    
    if result:
        return jsonify({"message": "Group saved successfully !!!"}), 200
    else:
        return jsonify({"message": "An error occured while saving group "}), 500
    

    
@app.route('/group/add-word', methods=['POST'])
def saveWordToGroup():
    data = request.json
    
    connection = database.create_server_connection("localhost", "root", "", DB_NAME)
    result = database.save_word_to_group_in_db(connection,(data['group_id'],data['word']))
    
    if result:
        return jsonify({"message": "Word saved to group successfully !!!"}), 200
    else:
        return jsonify({"message": "An error occured while saving word to  group "}), 500
    

@app.route("/group",methods=['GET'])
def getAllGroups():
    connection = database.create_server_connection("localhost", "root", "", DB_NAME)
    response = database.fetchAllGroups(connection)
    
    return jsonify(response), 200

# get all words of a particular group_id
@app.route("/group/words",methods=['GET'])
def getAllWordsGroups():
    connection = database.create_server_connection("localhost", "root", "", DB_NAME)
    groupe_id = request.args.get('group_id')
    response = database.fetchAllWordInGroups(connection,groupe_id)
    
    return jsonify(response), 200


# save expression to db
@app.route('/expression', methods=['POST'])
def saveExpression():
    data = request.json
    connection = database.create_server_connection("localhost", "root", "", DB_NAME)
    result = database.save_expression_to_db(connection,(data['expression'],data['words_expression']))
    
    if result:
        return jsonify({"message": "Expression saved successfully !!!"}), 200
    else:
        return jsonify({"message": "An error occured while saving expression "}), 500


# get all expressions
@app.route("/expression",methods=['GET'])
def getAllExpressions():
    connection = database.create_server_connection("localhost", "root", "", DB_NAME)
    response = database.fetchAllExpressions(connection)
    
    return jsonify(response), 200


# endpoint to generate statistics
@app.route("/statistics",methods=['GET'])
def stats():
    file_path = request.args.get('filename')
    frequency = request.args.get('frequency')
    
    if not frequency:
        frequency = 10
    else:
        frequency = int(frequency)
    
    if not file_path:
        return jsonify({'message': 'no file received'}),400
    
    file_path = "./uploads/"+file_path+'.txt'
    
    try:
        with open(file_path, 'r') as file:
            # Read the entire content of the file
            content = file.read()

            # Count the number of paragraphs (assumed to be separated by empty lines)
            paragraphs = content.split('\n\n')
            num_paragraphs = len(paragraphs)

            # Count the number of sentences (assumed to be separated by '.', '!', or '?')
            sentences = [sentence.strip() for sentence in content.split('.') if sentence.strip()]
            sentences += [sentence.strip() for sentence in content.split('!') if sentence.strip()]
            sentences += [sentence.strip() for sentence in content.split('?') if sentence.strip()]
            num_sentences = len(sentences)

            # Count the number of words
            words = content.split()
            num_words = len(words)
            
            # get 10 most frequent words
            get_most_frequent_words = database.get_most_frequent_words(file_path,frequency)
            
            sentence_results, paragraph_results,total_letter_stats = database.count_words_and_characters(file_path)
            

            # Count the number of letters
            num_letters = sum(len(word) for word in words)
            
             # stats response
            statistics_data = {
                'paragraphs': num_paragraphs,
                'sentences': num_sentences,
                'words': num_words,
                'letters': num_letters
            }
            
            response = {
                'stats': statistics_data,
                'frequency': get_most_frequent_words,
                'sentence': sentence_results,
                'paragraph': paragraph_results,
                'total_letters_counts': total_letter_stats
            }

            # Print the results
            return jsonify(response), 200

    except FileNotFoundError:
        print(f"File '{file_path}' not found.")
        return jsonify({'message': 'Error processing file'}),400


# data mining
@app.route("/data-mining",methods=['GET'])
def data_mining():
    file_path = request.args.get('filename')
    if not file_path:
        return jsonify({'message': 'no file received'}),400
    
    file_path = "./uploads/"+file_path+'.txt'
    array = database.data_mining(file_path)
    
    return jsonify(array), 200
        


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    app.run(debug=True)
