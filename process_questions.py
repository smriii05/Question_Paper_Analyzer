# questions_processor.py
import pandas as pd
import numpy as np
import string
import nltk
import re
import pickle
from sklearn.preprocessing import OneHotEncoder
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.stem import WordNetLemmatizer, PorterStemmer
from nltk.corpus import stopwords
from rake_nltk import Rake
import sqlite3

# Download necessary NLTK data
nltk.download('punkt')
nltk.download('wordnet')
nltk.download('stopwords')

# SQLite database connection
conn = sqlite3.connect('questions.db')
cursor = conn.cursor()

# Helper functions (same as before)
def preprocess_text(text):
    tokens = word_tokenize(text.lower())
    tokens = [word for word in tokens if word not in string.punctuation and word not in stop_words]
    lemmatized = [lemmatizer.lemmatize(word) for word in tokens]
    stemmed = [stemmer.stem(word) for word in lemmatized]
    return stemmed

def extract_qtype(question):
    rake.extract_keywords_from_text(question)
    keywords = rake.get_ranked_phrases()
    computational_keywords = {"perform", "generate", "database", "create", "design", "implement", "calculate", "determine", "solve", "compute", "evaluate", "simplify"}
    descriptive_keywords = {"justify", "method", "process", "procedure", "solution", "explain", "describe", "illustrate", "state", "discuss", "write", "why"}
    proof_keywords = {"prove", "verify", "demonstrate", "show"}
    statistical_keywords = {"test", "hypothesis", "mean", "variance", "confidence", "significance"}
    wh_keywords = {"what","why","which"}
    differentiate_keywords = {"differentiate", "contrast", "compare"}
    mathematical_keywords = {"solve", "convert", "find", "equation", "function", "integral", "derivative", "matrix"}
    discrete_keywords = {"graph", "logic", "combinatorics", "relation", "algorithm"}
    
    scores = {"Computational": 0, "Descriptive": 0, "Proof": 0, "Statistical": 0, "What": 0, "Differentiate": 0, "Mathematical": 0, "Discrete": 0, "Other": 0}

    for phrase in keywords:
        words = phrase.split()
        for word in words:
            if word in computational_keywords:
                scores["Computational"] += 1
            elif word in descriptive_keywords:
                scores["Descriptive"] += 1
            elif word in proof_keywords:
                scores["Proof"] += 1
            elif word in statistical_keywords:
                scores["Statistical"] += 1
            elif word in wh_keywords:
                scores["Wh"] += 1
            elif word in differentiate_keywords:
                scores["Differentiate"] += 1
            elif word in mathematical_keywords:
                scores["Mathematical"] += 1
            elif word in discrete_keywords:
                scores["Discrete"] += 1

    max_score_type = max(scores, key=scores.get)
    return "Other" if scores[max_score_type] == 0 else max_score_type

def keyword_count(question):
    rake.extract_keywords_from_text(question)
    keywords = rake.get_ranked_phrases()
    return len(keywords)

def compute_tf_idf(questions):
    tf = []
    idf = {}
    N = len(questions)
    vocabulary = set()
    processed_questions = [preprocess_text(q) for q in questions]
    for q in processed_questions:
        freq = {}
        for word in q:
            vocabulary.add(word)
            freq[word] = freq.get(word, 0) + 1
        tf.append(freq)

    for word in vocabulary:
        count = sum(1 for q in processed_questions if word in q)
        idf[word] = np.log(N / (1 + count))

    tf_idf_scores = []
    for q_tf in tf:
        scores = {word: tf_val * idf[word] for word, tf_val in q_tf.items()}
        tf_idf_scores.append(scores)
    return tf_idf_scores

def avg_word_length(text):
    question_tokens = preprocess_text(text)
    total_length = sum(len(word) for word in question_tokens)
    return 0 if not question_tokens else total_length / len(question_tokens)

def sentence_count(question):
    return len(re.split(r'[.!?]', question)) - 1

def readability_score(question):
    sentences = sent_tokenize(question)
    words = word_tokenize(question)
    complex_words = [word for word in words if len(word) > 2 and word not in string.punctuation]
    word_count = len(words)
    sentence_count = len(sentences)
    complex_word_count = len(complex_words)
    
    if sentence_count == 0 or word_count == 0:
        return 0
    gunning_fog = 0.4 * ((word_count / sentence_count) + 100 * (complex_word_count / word_count))
    return gunning_fog

# Initialize lemmatizer, stemmer, and stop words
lemmatizer = WordNetLemmatizer()
stemmer = PorterStemmer()
stop_words = set(stopwords.words('english'))

# RAKE initialization
rake = Rake(stopwords=stop_words)

features_data=[]

def process_questions(questions):
    for question in questions:
        features = []
        features.append(extract_qtype(question))  # qtype
        features.append(keyword_count(question))  # keyword count
        tf_idf_scores = compute_tf_idf([question])
        features.append(np.mean(list(tf_idf_scores[0].values())) if tf_idf_scores[0] else 0)  # TF-IDF score
        features.append(sentence_count(question))  # sentence count
        features.append(readability_score(question))  # readability score
        features.append(avg_word_length(question))  # average word length
        features_data.append(features)

        # Convert the feature list into a DataFrame                                     
        features_df = pd.DataFrame(features_data, columns=["qtype", "keyword_count", "keyword_tfidf", "sentence_count", "readability_scores", "avg_word_length"])                                       

        # One-hot encoding for qtype                                        
        encoder = OneHotEncoder(sparse_output=False)
        qtype_encoded = encoder.fit_transform(features_df[["qtype"]])
        qtype_encoded_df = pd.DataFrame(qtype_encoded, columns=encoder.get_feature_names_out(["qtype"]))
        features_df = pd.concat([features_df.reset_index(drop=True), qtype_encoded_df.reset_index(drop=True)], axis=1)      

        # Select numeric features only
        features_df_numeric = features_df.select_dtypes(include=['float64', 'int64'])       

        # Fill missing values in the numeric feature columns using the mean
        features_df_numeric = features_df_numeric.fillna(features_df_numeric.mean())

        # Load the pre-trained custom decision tree model from the .pkl file
        with open('custom_decision_tree_model.pkl', 'rb') as model_file:
            model = pickle.load(model_file)

        # Function to predict using the custom decision tree
        def predict(node, row):
            if row[node['index']] < node['value']:
                if isinstance(node['left'], dict):
                    return predict(node['left'], row)
                else:
                    return node['left']
            else:
                if isinstance(node['right'], dict):
                    return predict(node['right'], row)
                else:
                    return node['right']

        # Make predictions using the pre-trained custom decision tree model
        predictions = [predict(model, row) for row in features_df_numeric.values]

    print(features_df_numeric)
    # Print the predictions
    print(predictions)
    return predictions