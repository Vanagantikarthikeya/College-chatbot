
import string
import json
import pickle
import numpy as np
import os

# Try to import nltk and use it. If it fails (missing resource), fallback to simple processing.
try:
    import nltk
    from nltk.stem import WordNetLemmatizer
    
    # Ensure NLTK can find data in current directory
    nltk.data.path.append(os.getcwd())
    
    # Check if resources exist
    try:
        nltk.data.find('tokenizers/punkt')
        nltk.data.find('corpora/wordnet')
    except LookupError:
        # If resources are missing and we can't download/find them, we set a flag to force fallback
        # However, for now we will try to proceed and let the inner except catch if actual function calls fail
        pass

    lemmatizer = WordNetLemmatizer()
    USE_NLTK = True
except (ImportError, LookupError, Exception):
    USE_NLTK = False
    print("Warning: NLTK resources not working. Switching to basic string processing.")

def clean_up_sentence(sentence):
    """
    Takes a raw sentence and returns a list of processed word tokens.
    Uses NLTK if available, otherwise simple whitespace splitting.
    """
    global USE_NLTK
    
    # Fallback logic if NLTK breaks during runtime (e.g. data missing)
    try:
        if USE_NLTK:
            # Step 1: Tokenize
            sentence_words = nltk.word_tokenize(sentence)
            # Step 2: Lemmatize
            processed_words = [lemmatizer.lemmatize(word.lower()) for word in sentence_words]
            return processed_words
    except Exception as e:
        print(f"NLTK Error ({e}), falling back to simple processing.")
        USE_NLTK = False # Disable for future calls
        
    # BACKUP / SIMPLE MODE
    # Just lowercase and split by space, removing punctuation
    sentence = sentence.lower()
    for char in string.punctuation:
        sentence = sentence.replace(char, "")
    return sentence.split()

def bag_of_words(sentence, words):
    """
    Converts a sentence into a bag-of-words array (numpy array).
    """
    # Preprocess the user sentence using the function defined above
    sentence_words = clean_up_sentence(sentence)
    
    # Initialize a bag with 0 for each word in the vocabulary
    bag = [0] * len(words)
    
    for s in sentence_words:
        for i, w in enumerate(words):
            if w == s:
                bag[i] = 1
                
    return np.array(bag)
