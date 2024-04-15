# K214945 ASAD ULLAH KHAN 

import os
from collections import defaultdict
import csv
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
import re
import string

# Define the directory containing your files
directory = "ResearchPapers"
tokens = {}
No_stop_word_tokens = {}  # Dictionary to store processed tokens from all files

# Read stopwords from Stopword-List.txt
stop_words = set()
with open("Stopword-List.txt", "r") as stopword_file:
    stop_words = set(stopword_file.read().splitlines())

# Function to remove URLs from tokens
def remove_urls(tokens):
    url_pattern = re.compile(r'https?://\S+|www\.\S+')
    # Iterate through the tokens and filter out URLs
    tokens_without_urls = [token for token in tokens if not url_pattern.match(token)]
    return tokens_without_urls

# Function to remove special characters from tokens
def remove_special_characters(tokens):
    # Define the pattern to match special characters
    special_char_pattern = re.compile(r'[^\w\s]')  # Matches any character that is not a word character or whitespace

    # Iterate through the tokens and remove special characters
    tokens_without_special_chars = [special_char_pattern.sub('', token) for token in tokens]

    # Remove empty tokens after removing special characters
    tokens_without_special_chars = [token for token in tokens_without_special_chars if token]

    return tokens_without_special_chars

# Function to remove numbers from tokens
def remove_numbers(tokens):
    # Define the pattern to match numbers
    number_pattern = re.compile(r'\b\d+\b')

    # Iterate through the tokens and remove tokens containing numbers
    tokens_without_numbers = [token for token in tokens if not number_pattern.match(token)]

    return tokens_without_numbers

document_data = {}
# Loop through each file in the directory
for filename in os.listdir(directory):
    # Construct the full path to the file
    file_path = os.path.join(directory, filename)

    with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
        # Read the content of the file
        file_content = file.read()

        # Tokenize the content
        tokens = word_tokenize(file_content)

        # Stemming and other processing
        ps = PorterStemmer()
        token_case_fold = [ps.stem(word) for word in tokens]

        punctuation = set(string.punctuation)

        # Remove punctuation and stop words
        No_punctuation_tokens = [word for word in token_case_fold if word not in punctuation]
        No_stop_word_tokens = [word for word in No_punctuation_tokens if word.lower() not in stop_words]

        No_url_tokens= remove_urls(No_stop_word_tokens)

        No_special_char_tokens = remove_special_characters(No_url_tokens)

        No_number_tokens = remove_numbers(No_special_char_tokens)

        # Further tokenize to reduce terms
        No_number_tokens = [token for token in No_number_tokens if len(token) > 1]  # Remove single-character tokens

        # Store document data
        document_data[filename] = {
            'tokens': No_number_tokens,  # Store processed tokens
            'term_count': len(set(No_number_tokens)),
            'total_terms': len(No_number_tokens)
        }

# Define the Node class for linked list
class Node:
    def __init__(self, data=None):
        self.data = data
        self.next = None

# Define the LinkedList class
class LinkedList:
    def __init__(self):
        self.head = None

    def append(self, data):
        new_node = Node(data)
        if not self.head:
            self.head = new_node
            return
        current = self.head
        while current.next:
            current = current.next
        current.next = new_node

    def __str__(self):
        result = []
        current = self.head
        while current:
            result.append(str(current.data))
            current = current.next
        return ' -> '.join(result)

# Function to build positional index
def build_positional_index(docs_dir):
    positional_index = defaultdict(lambda: defaultdict(list))
    for filename in os.listdir(docs_dir):
        if filename.endswith('.txt'):
            doc_id = filename[:-4]
            doc_path = os.path.join(docs_dir, filename)
            tokens = document_data[filename]['tokens']
            for position, term in enumerate(tokens):
                positional_index[term][doc_id].append(position)
    return positional_index

# Function to save positional index to a CSV file
def save_positional_index(positional_index, output_file):
    with open(output_file, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Term', 'DocID', 'Positions'])
        for term, postings in positional_index.items():
            for doc_id, positions in postings.items():
                positions_str = '[' + ', '.join(map(str, positions)) + ']'
                writer.writerow([term, doc_id, positions_str])

# Build positional index
positional_index = build_positional_index(directory)
output_file = "positional_index.csv"
save_positional_index(positional_index, output_file)

# Function to execute proximity query
def execute_proximity_query(positional_index, term1, term2, distance):
    matching_documents = []

    if term1 not in positional_index or term2 not in positional_index:
        return matching_documents

    # Iterate over documents containing term1
    for document in positional_index[term1].keys():
        if document in positional_index[term2]:
            positions1 = positional_index[term1][document]
            positions2 = positional_index[term2][document]

            # Check positional proximity
            for pos1 in positions1:
                for pos2 in positions2:
                    if abs(pos1 - pos2) <= distance:
                        matching_documents.append(document)
                        break  # Break if a match is found within proximity

    return matching_documents

# Function to process query with proximity
def process_proximity_query(query, positional_index):
    query_terms = query.split('/')
    proximity_query = query_terms[0].split()
    distance = int(query_terms[1])

    term1, term2 = proximity_query

    result_documents = execute_proximity_query(positional_index, term1, term2, distance)
    return set(result_documents), term1, term2, distance, len(positional_index.keys())
