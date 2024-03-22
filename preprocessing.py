# pip install langdetect
import nltk
nltk.download('punkt')
nltk.download('stopwords')
import os
import json
import string
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from langdetect import detect
nltk.download('wordnet')
nltk.download('omw-1.4')
import re

stop_words = set(stopwords.words('english'))
lemmatizer = WordNetLemmatizer()

input_directory = './data/raw-txt'
output_directory = './data/tokenized-txt'

if not os.path.exists(output_directory):
    os.makedirs(output_directory)

def preprocess_text(text):
    text = text.lower()
    text = "".join(re.findall("[a-z0-9\s]*", text))  
    tokens = word_tokenize(text)
    filtered_text = []
    for word in tokens:
        if word not in stop_words:
            try:
                if detect(word) == 'en':
                    filtered_text.append(word)
            except:
                pass
    tokens = [lemmatizer.lemmatize(l) for l in filtered_text]
    return tokens

def process_file(input_file_path, output_file_path):
    with open(input_file_path, 'r', encoding='utf-8') as file:
        text = file.read()
        preprocessed_text = preprocess_text(text)
    with open(output_file_path, 'w', encoding='utf-8') as file:
        json.dump(preprocessed_text, file)

for filename in os.listdir(input_directory):
    if filename.endswith('.txt'):
        input_path = os.path.join(input_directory, filename)
        output_path = os.path.join(output_directory, filename)
        process_file(input_path, output_path)
