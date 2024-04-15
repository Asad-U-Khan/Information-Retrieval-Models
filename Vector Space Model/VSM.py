import os
import pandas as pd
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
from collections import Counter
import math

# Initialize inverted index
inverted_index = {}
N = 20
docs = [1,2,3,7,8,9,11,12,13,14,15,16,17,18,21,22,23,24,25,26]
# Read stopwords from Stopword-List.txt
stop_words = {}
with open("Stopword-List.txt", "r") as stopword_file:
    stop_words = set(stopword_file.read().splitlines())

# Initialize single alpha characters, and target characters
single_alpha = set('abcdefghijklmnopqrstuvwxyz')
target_chars = ['%', '$', '*', "'", '’', '¨', '=', '+', '`', '/', '.', '·', ',', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '|', ':', '(', ')', '>', ';', '&', '“', '”', '[', ']', '@', '?', '}', '{']

# Function to preprocess text
def preprocess_text(text):
    for char in text:
        if char in target_chars:
            text = text.replace(char, ' ')
        elif char == '-' or char == '_':
            text = text.replace(char, '')
        elif char == '\n':
            text = text.replace(char, ' ')
    return text

# Function to tokenize and stem text
def tokenize_and_stem(text):
    porter_stemmer = PorterStemmer()
    tokens = word_tokenize(text)
    stemmed_tokens = [porter_stemmer.stem(token) for token in tokens if token.lower() not in stop_words and token not in single_alpha]
    return stemmed_tokens

# Function to calculate term frequency
def calculate_term_frequency(tokens):
    return dict(Counter(tokens))

def cal_tf_idf_and_making_DataFrame():

    directory = r'E:\Documents (E)\6TH SEMESTER\K214945 VSM\ResearchPapers' 
    #initializing DataFrame
    columns = ["words"]
    columns_ = [filename.split('.')[0] for filename in sorted(os.listdir(directory), key=lambda x: int(x[:-4]))]
    columns.extend(columns_)
    df = pd.DataFrame(columns = columns)

    for filename in sorted(os.listdir(directory),key=lambda x: int(x[:-4]) ):
        filepath = os.path.join(directory, filename)
        if os.path.isfile(filepath):
            # Preprocess text
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as file:
                content = file.read()
            print(f"Preprocessed : {filepath}")    
            preprocessed_content = preprocess_text(content)
    
            # Tokenize and stem
            print(f"Tokenize and stem : {filepath}") 
            stemmed_tokens = tokenize_and_stem(preprocessed_content)
    
            # Calculate term frequency
            print(f"Calculate term frequency : {filepath}") 
            term_freq = calculate_term_frequency(stemmed_tokens)
    
    
            for word , freq in term_freq.items():
                if word not in df['words'].values:
                    df = df._append({'words': word}, ignore_index=True)
                    df.loc[df['words'] == word, filename.split('.')[0]] = freq
                else:
                    df.loc[df['words'] == word, filename.split('.')[0]] = freq
    df = df.fillna(0)
    # calculating df
    df['df'] = (df.iloc[:, 1:22] != 0).sum(axis=1)
    # calculating idf
    df['idf'] = df['df'].apply(lambda x: math.log(N/x))
    # calculating tf-idf
    for doc in docs:
        df['tf_idf' + str(doc)] = df[str(doc)] * df['idf']
    # normalizing vectors 
    for doc in docs:
        df['Normalized tf_idf' + str(doc)] = df['tf_idf' + str(doc)]/math.sqrt((df['tf_idf' + str(doc)] ** 2).sum())
    print(df)
    df.to_csv(r'E:\Documents (E)\6TH SEMESTER\K214945 VSM\output.csv', index=False)

#cal_tf_idf_and_making_DataFrame()

def query_processing(query):
    path = r'E:\Documents (E)\6TH SEMESTER\K214945 VSM\output.csv'
    df = pd.read_csv(path)

    pp_query = preprocess_text(query)
    stem_query = tokenize_and_stem(pp_query)
    term_freq = calculate_term_frequency(stem_query)

    for word , freq in term_freq.items():
        if word not in df['words'].values:   
            df = df._append({'words': word}, ignore_index=True)
            df.loc[df['words'] == word, filename.split('.')[0]] = freq
        else:
            df.loc[df['words'] == word, 'query'] = freq
             
    df = df.fillna(0)
    df['tf_idf_query'] = df['query'] * df['idf']
    # normalizing query
    df['Normalized tf_idf_query' ] = df['tf_idf_query']/math.sqrt((df['tf_idf_query'] ** 2).sum())
    
    rank = []
    # ranking documents finding cosine similarity
    for doc in docs:
        rank.append(((df['Normalized tf_idf_query' ] * df['Normalized tf_idf' + str(doc)]).sum() , str(doc))) 

    print("")
    rank = sorted(rank, key=lambda x: x[0], reverse=True)
    return rank