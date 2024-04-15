# K214945 ASAD ULLAH KHAN 

import os
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
import re
import string
import csv

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
    tokens_without_special_chars = [token for token in tokens if not special_char_pattern.match(token)]

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

# Implement inverted index
inverted_index = {}
document_frequency = {}

for filename, data in document_data.items():
    tokens = data['tokens']
    unique_tokens_in_doc = set(tokens)
    for token in unique_tokens_in_doc:
        if token not in inverted_index:
            inverted_index[token] = LinkedList()
            document_frequency[token] = 1
        else:
            document_frequency[token] += 1
        inverted_index[token].append(filename)

# Function to save inverted index to a CSV file
def save_inverted_index(inverted_index, output_file):
    with open(output_file, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Term', 'DocID'])
        for term, doc_id in inverted_index.items():
                terms_str = str(doc_id) 
                writer.writerow([term, terms_str])

# Save inverted index
output_file = "inverted_index.csv"
save_inverted_index(inverted_index, output_file)

# Process the query
def process_boolean_query(query):
    query_terms = query.split()
    result_documents = None
    current_op = None  # Default to None operation if no operator is provided
    
    for term in query_terms:
        term = term.lower()

        if term in ["and", "or", "not"]:
            current_op = term  # Update the current operation based on the query term
            continue  # Skip to the next term in the query

        term_documents = set()

        if term in inverted_index:
            posting_list = inverted_index[term]
            current = posting_list.head

            while current:
                term_documents.add(current.data)
                current = current.next

        if current_op == "and":
            result_documents = result_documents.intersection(term_documents)
        elif current_op == "or":
            result_documents = result_documents.union(term_documents)
        elif current_op == "not":
            result_documents = set(document_data.keys()).difference(term_documents)
        else:
            result_documents = term_documents    

    return result_documents,len(inverted_index.keys())
