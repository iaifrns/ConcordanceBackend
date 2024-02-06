from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import database  # Import the database module
DB_NAME = "textretrivalsystem"
app = Flask(__name__)
from flask_cors import CORS

UPLOAD_NEW_FOLDER = 'uploads'
app.config['UPLOAD_NEW_FOLDER'] = UPLOAD_NEW_FOLDER

CORS(app)


# endpoint to generate statistics
@app.route("/word_analytics",methods=['GET'])
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
@app.route("/data_mining",methods=['GET'])
def data_mining():
    file_path = request.args.get('filename')
    if not file_path:
        return jsonify({'message': 'no file received'}),400
    
    file_path = "./uploads/"+file_path+'.txt'
    array = database.data_mining(file_path)
    
    return jsonify(array), 200
        
