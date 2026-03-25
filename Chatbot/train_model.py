
import random
import json
import pickle
import numpy as np
from sklearn.neural_network import MLPClassifier

import traceback

if __name__ == "__main__":
    try:
        # Import the preprocessing function from our custom module
        from nlp_preprocessing import clean_up_sentence

        # ---------------------------------------------------------
        # Step 1: Initialization and Data Loading
        # ---------------------------------------------------------
        print("Loading intents file...")
        with open('intents.json') as file:
            intents = json.load(file)

        words = []        # Vocabulary list
        classes = []      # Intent tags list
        documents = []    # List of (pattern_tokens, tag) tuples
        ignore_letters = ['?', '!', '.', ','] # Characters to ignore

        # ---------------------------------------------------------
        # Step 2: Data Preprocessing
        # ---------------------------------------------------------
        print("Preprocessing data and building vocabulary...")

        for intent in intents['intents']:
            for pattern in intent['patterns']:
                # Tokenize and lemmatize each pattern using our helper function
                # clean_up_sentence returns a list of lemmatized tokens
                word_list = clean_up_sentence(pattern)
                
                # Add tokens to our vocabulary list
                words.extend(word_list)
                
                # Add the 'tokenized pattern' and 'associated tag' to documents
                documents.append((word_list, intent['tag']))
                
                # Add the tag to classes if it's not already there
                if intent['tag'] not in classes:
                    classes.append(intent['tag'])

        # Finalize the vocabulary:
        # 1. Remove duplicates (set)
        # 2. Sort the lists for consistency
        words = sorted(list(set(words))) 
        classes = sorted(list(set(classes)))

        print(f"Data statistics: {len(documents)} documents, {len(classes)} classes, {len(words)} unique lemmatized words")

        # ---------------------------------------------------------
        # Step 3: SAVE Data Structures
        # ---------------------------------------------------------
        # We need to save 'words' and 'classes' to pickle files.
        # The prediction script (main app) will need these to process user input consistently.
        print("Saving data structures (words.pkl, classes.pkl)...")
        pickle.dump(words, open('words.pkl', 'wb'))
        pickle.dump(classes, open('classes.pkl', 'wb'))

        # ---------------------------------------------------------
        # Step 4: Create Training Data
        # ---------------------------------------------------------
        print("Creating training data...")

        training = []
        output_empty = [0] * len(classes)

        # Create a Bag of Words for each document
        for document in documents:
            bag = []
            word_patterns = document[0] # List of tokens
            
            # Create the bag of words array: 1 if word match found in current pattern, otherwise 0
            # Note: We rely on the exact words list we just built
            for word in words:
                bag.append(1) if word in word_patterns else bag.append(0)
                
            # Output is a '0' for each tag and '1' for current tag (One Hot Encoding)
            output_row = list(output_empty)
            output_row[classes.index(document[1])] = 1
            
            training.append([bag, output_row])

        # Shuffle the data to ensure the model doesn't learn order-dependencies
        random.shuffle(training)

        # Convert to numpy array
        # Note: explicit conversion to list first avoids typical numpy warnings with ragged arrays
        training = np.array(training, dtype=object)

        # Split into attributes (X - Bag of Words) and labels (Y - Tags)
        train_x = list(training[:, 0]) # Features
        train_y = list(training[:, 1]) # Labels

        # ---------------------------------------------------------
        # Step 5: Build the Neural Network Model (sklearn)
        # ---------------------------------------------------------
        print("Building the Neural Network model (MLPClassifier)...")

        # MLPClassifier is a Multi-Layer Perceptron (Neural Network)
        # hidden_layer_sizes=(128, 64): matches our previous architecture
        # max_iter=200: number of epochs
        # activation='relu': same as Keras
        # solver='adam': same as Keras optimizer
        model = MLPClassifier(hidden_layer_sizes=(128, 64), 
                            max_iter=300, 
                            activation='relu', 
                            solver='adam', 
                            random_state=1)

        # ---------------------------------------------------------
        # Step 6: Train the Model
        # ---------------------------------------------------------
        print("Training the model...")

        # fit() trains the model on the data
        model.fit(np.array(train_x), np.array(train_y))

        # ---------------------------------------------------------
        # Step 7: Save the Trained Model
        # ---------------------------------------------------------
        print("Saving the trained model...")

        # We use pickle to save the sklearn model
        pickle.dump(model, open('model.pkl', 'wb'))

        print("Training complete. Model saved as 'model.pkl'.")

    except Exception as e:
        print("An error occurred:")
        print(e)
        traceback.print_exc()
