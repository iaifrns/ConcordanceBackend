import mysql.connector
from mysql.connector import Error
import os
import re
import nltk
import logging
from collections import Counter
import re
import spacy
nltk.download('punkt')
from nltk.tokenize import word_tokenize, sent_tokenize
from itertools import combinations
nlp = spacy.load("en_core_web_sm")

# Global database name
DATABASE_NAME = "textretrivalsystem"
logging.basicConfig(filename='database.log', level=logging.DEBUG)

def establish_connection(host_name, user_name, user_password, db_name):
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host_name,
            user=user_name,
            passwd=user_password,
            database=db_name
        )
        print("MySQL Database connection successful")
        print("MySQL Database connection successful")
    except Error as err:
        print(f"Error: '{err}'")
        logging.error(f"Error: '{err}'")

    return connection

def create_db(connection, db_name):
    cursor = connection.cursor()
    try:
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
        print(f"Database '{db_name}' created successfully.")
        print(f"Database '{db_name}' created successfully")
        
        cursor.execute(f"USE {db_name}")  # Switch to the new database

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS document_list (
            doc_id INTEGER AUTO_INCREMENT PRIMARY KEY, 
            name TEXT,
            location TEXT,
            author TEXT,
            date DATE,
            source TEXT  
        );
        """)
        print("Table document_list created successfully")
        print("Table document_list created successfully")
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Words (
        word_id INTEGER AUTO_INCREMENT PRIMARY KEY,
        word VARCHAR(255) UNIQUE
        );
        """)
        print("Table Words created successfully")
        print("Table Words created successfully")
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS occurrences (
        doc_id INTEGER,
        word_id INTEGER,
        sentence_no INTEGER, 
        para_no INTEGER,
        word_position INTEGER,
        PRIMARY KEY (doc_id, word_id, sentence_no, word_position),
        FOREIGN KEY (doc_id) REFERENCES document_list(doc_id),
        FOREIGN KEY (word_id) REFERENCES Words(word_id)
        );
        """)
        print("Table occurrences created successfully")
        print("Table occurrences created successfully")
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS groups_of_words (
            group_id INTEGER PRIMARY KEY,
            name TEXT 
        );
        """)
        print("Table groups_of_words created successfully")
        print("Table groups_of_words created successfully")
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS word_associationed (
            word_id INTEGER,
            group_id INTEGER,
            PRIMARY KEY (word_id, group_id),
            FOREIGN KEY (word_id) REFERENCES Words(word_id),
            FOREIGN KEY (group_id) REFERENCES groups_of_words(group_id)
        );
        """)
        print("Table word_associationed created successfully")
        print("Table word_associationed created successfully")

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS declerations (
            decleration_id INTEGER PRIMARY KEY,
            decleration TEXT,
            words_decleration TEXT
        );
        """)
        print("Table declerations created successfully")
        print("Table declerations created successfully")
    except Error as err:
        print(f"Error: '{err}'")
        logging.error(f"Error: '{err}'")

def execute_query(connection, query, params=None):
    cursor = None
    try:
        cursor = connection.cursor()
        cursor.execute(query, params or ())
        connection.commit()
        print("Query successful")
        print("Query successful")
    except Error as err:
        print(f"Error: '{err}'")
        logging.error(f"Error: '{err}'")
    finally:
        if cursor:
            cursor.close()

def read_query(connection, query, params=None):
    result = None
    cursor = None
    try:
        cursor = connection.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        result = cursor.fetchall()
    except Error as err:
        print(f"Error: '{err}'")
        logging.error(f"Error: '{err}'")
    finally:
        if cursor:
            cursor.close()
    return result

def upload_document(connection, file_path, metadata):
    if not os.path.isfile(file_path):
        print("File not found.")
        logging.error("File not found.")
        return
    
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            text_content = file.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        logging.error(f"Error reading file: {e}")
        return
    
    name = metadata.get('name', 'Unknown')
    location = metadata.get('location', 'Unknown')
    author = metadata.get('author', 'Unknown')
    date = metadata.get('date', '0000-00-00')
    source = metadata.get('source', 'Unknown')

    insert_query = """
    INSERT INTO document_list (name, location, author, date, source)
    VALUES (%s, %s, %s, %s, %s);
    """
    
    execute_query(connection, insert_query, (name, location, author, date, source))

def save_document_and_metadata(connection,file_path, metadata):
    create_db(connection, DATABASE_NAME)
    try:
        upload_document(connection, file_path, metadata)
        doc_id_query = "SELECT LAST_INSERT_ID();"
        doc_id_result = read_query(connection,doc_id_query)
        doc_id = doc_id_result[0][0] if doc_id_result else None
    except Exception as e:
        print(f"Error saving document and metadata: {e}")
        logging.error(f"Error saving document and metadata: {e}")
        return None

    if doc_id:
        process_text(connection, doc_id, file_path)
    else:
        print("Error retrieving document ID.")
        logging.error("Error retrieving document ID.")

def process_text(connection, document_id, file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            text_content = file.read()
            sentences = sent_tokenize(text_content)
            for sentence_no, sentence in enumerate(sentences, 1):
                sentence = re.sub(r'[^A-Za-z0-9\s]', '', sentence)
                words = word_tokenize(sentence)
                words_pos = [(pos, word) for pos, word in enumerate(words, 1)]
                for word_pos, word in words_pos:
                    insert_occurrence_query = """
                    INSERT INTO occurrences (doc_id, word_id, sentence_no, word_position)
                    SELECT %s, word_id, %s, %s FROM Words WHERE word = %s;
                    """
                    execute_query(connection, insert_occurrence_query, (document_id, sentence_no, word_pos, word))
    except Exception as e:
        print(f"Error processing document: {e}")
        logging.error(f"Error processing document: {e}")

def find_word_occurrences(connection, word):
    return occurrences

def create_word_group(connection, group_name):
        logging.error(f"Error: '{err}'")

def add_word_to_group(connection, word, group_name):
        logging.error("Word or group not found.")

def create_expression(connection, expression):
    print(f"Expression '{expression}' created successfully.")

def get_document_statistics(connection, document_id):
        return None

def get_words(connection, doc_id=None):
        return read_query(connection, query)

def get_word_context(connection, word, doc_id=None):
    return read_query(connection, query, params)

def find_frequent_word_pairs(connection, document_id, min_frequency):
    return frequent_pairs

def get_filtered_words(connection, doc_id=None, starting_letter=None, paragraph=None, sentence=None, line_number=None, line_range=None):
    return read_query(connection, query, params)

def get_word_contexts(connection, word, doc_id=None, paragraph=None, sentence=None, line_number=None, line_range=None):
    return read_query(connection, query, params)

def get_surrounding_sentences(file_path, sentence_no, para_no):
    return context_paragraph

def save_group_to_db(connection,data):
    return result

def save_word_to_group_in_db(connection,data):
    return result

def fetchAllGroups(connection):
    return arr

def fetchAllWordInGroups(connection,group_id):
    return arr

def save_expression_to_db(connection,data):
    return result

def fetchAllExpressions(connection):
    return arr

def fetchAllDocuments(connection):
    return arr

def get_most_frequent_words(file_path,num):
        return []

def count_words_and_characters(file_path):
        return None

def data_mining(file_path):
    return entities

# Replace with your MySQL server information
host = "localhost"
user = "root"  # It's recommended to use a less privileged user in production
password = "password"  # Enter your MySQL root password here