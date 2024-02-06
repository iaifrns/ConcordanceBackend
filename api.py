import logging
from flask import Flask
from werkzeug.utils import secure_filename
DB_NAME = "textretrivalsystem"
app = Flask(__name__)
from flask_cors import CORS

import analyticsApi
import decleration
import documentApi
import wordsApi

documentApi.read_document()

documentApi.upload_document()

documentApi.get_all_documents()

wordsApi.get_all_groups()

wordsApi.get_all_words_groups()

wordsApi.get_word_context()

wordsApi.get_word_list()

wordsApi.save_word_group()

wordsApi.save_word_to_group()

decleration.get_all_declerations()

decleration.save_decleration()

analyticsApi.stats()

analyticsApi.data_mining()

UPLOAD_NEW_FOLDER = 'uploads'
app.config['UPLOAD_NEW_FOLDER'] = UPLOAD_NEW_FOLDER

CORS(app)




if __name__ == "__main__":
    logging.basicConfig(level=print)
    app.run(debug=True)
