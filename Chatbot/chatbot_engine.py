import random
import json
import pickle
import numpy as np
import os
import datetime
import uuid
import re

# Import Sentence Transformers for Embeddings
from sentence_transformers import SentenceTransformer, util

# Import customized logging
from logging_utils import log_unanswered_query

# Import our custom preprocessing logic
from nlp_preprocessing import clean_up_sentence, bag_of_words
# Import document search functionality
from document_ingestion import search_documents

# ---------------------------------------------------------
# Step 1: Load Runtime Resources
# ---------------------------------------------------------
# A chatbot needs 4 things to function:
# 1. The 'definitions' (intents.json) to know what to say.
# 2. The 'brain' (model.pkl) to classify inputs.
# 3. The 'vocabulary' (words.pkl) to clean inputs exactly like during training.
# 4. The 'labels' (classes.pkl) to understand the output of the brain.

print("Loading chatbot engine resources...")

with open('intents.json') as file:
    intents = json.load(file)

words = pickle.load(open('words.pkl', 'rb'))
classes = pickle.load(open('classes.pkl', 'rb'))
model = pickle.load(open('model.pkl', 'rb'))

# Define a confidence threshold (e.g., 0.50).
# If the model isn't at least 50% sure, we shouldn't guess.
# Since we use softmax, these are probabilities summing to 1.
CONFIDENCE_THRESHOLD = 0.65

# Document search relevance threshold
# Only use document results if they have meaningful keyword overlap
DOCUMENT_RELEVANCE_THRESHOLD = 2

# Synonym dictionary for normalization
SYNONYMS = {
    "register": "apply",
    "registration": "apply",
    "pay": "fee",
    "payment": "fee",
    "semester": "term",
    "course": "program"
}

def normalize_synonyms(sentence):
    """
    Normalizes the input sentence by lowercasing and replacing synonyms.
    This ensures that variations of words map to the same token before vectorization.
    """
    sentence = sentence.lower()
    
    for word, replacement in SYNONYMS.items():
        # Replace whole words only to avoid partial matches (e.g. "lay" inside "play")
        sentence = re.sub(r'\b' + re.escape(word) + r'\b', replacement, sentence)
        
    return sentence

# ---------------------------------------------------------
# Step 1.2: Initialize Sentence Embedding System
# ---------------------------------------------------------
# Precompute Embeddings for all patterns to allow for semantic similarity fallback

print("Initializing Sentence Transformer model (all-MiniLM-L6-v2)...")
try:
    embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
    EMBEDDING_AVAILABLE = True
except Exception as e:
    print(f"Warning: Could not load SentenceTransformer ({e}). Embedding fallback will be disabled.")
    EMBEDDING_AVAILABLE = False

intent_embeddings = None
embedding_patterns = []
embedding_tags = []

if EMBEDDING_AVAILABLE:
    print("Precomputing intent embeddings...")

    for intent in intents['intents']:
        for pattern in intent['patterns']:
            # Store raw pattern strings for embedding (normalization is handled, but embeddings handle semantic meaning well)
            # We still normalize simple synonyms to align with user input preprocessing
            processed_pattern = normalize_synonyms(pattern)
            embedding_patterns.append(processed_pattern)
            embedding_tags.append(intent['tag'])

    # Compute matched embeddings
    # This matrix will be used for cosine similarity against user query
    intent_embeddings = embedding_model.encode(embedding_patterns, convert_to_tensor=True)

def get_embedding_response(user_query, min_score=0.5):
    """
    Finds the best matching intent using Sentence Embedding Cosine Similarity.
    This acts as a smart semantic fallback when the neural network is unsure.
    """
    if not EMBEDDING_AVAILABLE:
        return None
        
    # 1. Transform user query into embedding
    normalized_query = normalize_synonyms(user_query)
    user_embedding = embedding_model.encode(normalized_query, convert_to_tensor=True)
    
    # 2. Calculate cosine similarity against all stored pattern embeddings
    # util.cos_sim returns a tensor [[score1, score2, ...]]
    cosine_scores = util.cos_sim(user_embedding, intent_embeddings)[0]
    
    # 3. Find the best match
    best_match_idx = int(np.argmax(cosine_scores.cpu().numpy())) # Move to cpu for numpy conversion if needed
    best_similarity = float(cosine_scores[best_match_idx])
    
    # DEBUG: Print Embedding match info
    if best_similarity > 0.2: # Only debug log significant matches
        matched_pattern = embedding_patterns[best_match_idx]
        matched_tag = embedding_tags[best_match_idx]
        print(f"[DEBUG] Embedding Best Match: '{matched_pattern}' (Tag: {matched_tag}) Score: {best_similarity:.4f}")
    
    # 4. Check if similarity meets threshold
    if best_similarity >= min_score:
        matched_tag = embedding_tags[best_match_idx]
        
        # Return a response from the matched intent
        for intent in intents['intents']:
            if intent['tag'] == matched_tag:
                return random.choice(intent['responses'])
                
    return None

def predict_class(sentence):
    """
    Predicts the intent of the input sentence using the trained model.
    With DEBUG LOGGING ENABLED.
    
    Args:
        sentence (str): User input text.
        
    Returns:
        tuple: (list of dicts, float max_confidence)
               The list contains [{'intent': 'greeting', 'probability': '0.9'}] sorted by probability.
               The float is the raw maximum probability score encountered.
    """
    
    # 0. Apply Synonym Normalization Layer
    # This replaces words like "register" -> "apply" to standardize inputs
    sentence = normalize_synonyms(sentence)

    # DEBUG: Print normalized sentence
    # print(f"[DEBUG] Normalized Sentence: {sentence}")
    
    # 1. Preprocess the input into a bag-of-words array
    # This must match the 'input_shape' of our neural network
    bow = bag_of_words(sentence, words)
    
    # DEBUG: Print tokens
    # Note: clean_up_sentence is called inside bag_of_words, so we call it again just for printing
    print(f"[DEBUG] User Query Tokens: {clean_up_sentence(sentence)}")
    
    # 2. Predict using the neural network
    # model.predict_proba expects a batch of inputs, so we wrap our single bow in a list: np.array([bow])
    res = model.predict_proba(np.array([bow]))[0]
    
    # Capture the maximum confidence score before filtering
    max_confidence = np.max(res) if len(res) > 0 else 0.0
    
    # DEBUG: Print raw confidence
    print(f"[DEBUG] Raw Max Confidence: {max_confidence:.4f}")

    # 3. Filter out weak predictions
    # We enumerate to keep track of the index (which maps to the class name)
    results = [[i, r] for i, r in enumerate(res) if r > CONFIDENCE_THRESHOLD]
    
    # 4. Sort by strength of probability (highest first)
    results.sort(key=lambda x: x[1], reverse=True)
    
    return_list = []
    for r in results:
        intent_name = classes[r[0]]
        prob_val = str(r[1])
        return_list.append({'intent': intent_name, 'probability': prob_val})
        
    # DEBUG: Print final predicted intent(s)
    if return_list:
        print(f"[DEBUG] Predicted Intent: {return_list[0]['intent']} ({return_list[0]['probability']})")
    else:
        print(f"[DEBUG] No intent met threshold of {CONFIDENCE_THRESHOLD}")
        
    return return_list, max_confidence

# ---------------------------------------------------------
# Step 2: Hybrid Answering Engine
# ---------------------------------------------------------
# This is the core logic that decides between FAQ, Document, and Fallback

def get_faq_response(intents_list, intents_json):
    """
    Retrieves a response from the FAQ knowledge base (intents.json).
    
    Args:
        intents_list (list): Output from predict_class function.
        intents_json (dict): The loaded intents.json data.
        
    Returns:
        str or None: FAQ response if found, None otherwise.
    """
    if not intents_list:
        return None
    
    tag = intents_list[0]['intent']
    list_of_intents = intents_json['intents']
    
    for intent in list_of_intents:
        if intent['tag'] == tag:
            # Found the matching intent block. Pick a random response from its list.
            return random.choice(intent['responses'])
    
    return None

def get_dynamic_response(user_query):
    """
    Analyzes user query for time-sensitive topics and extracts relevant dates
    from documents to provide a dynamic answer.
    """
    user_query_lower = user_query.lower()
    
    # 1. Identify context
    target_category = None
    topic_keywords = {
        "Fees": ["fee", "payment", "deadline", "dues"],
        "Exams": ["exam", "timetable", "schedule", "date sheet"],
        "Events": ["event", "workshop", "seminar", "fest"],
        "Calendar": ["academic", "calendar", "term", "semester", "holiday"]
    }
    
    for category, keywords in topic_keywords.items():
        if any(keyword in user_query_lower for keyword in keywords):
            target_category = category
            break
            
    if not target_category:
        return None
        
    # 2. Search ONLY documents in this category
    # We use search_documents but filter results manually or rely on keyword relevance
    doc_results = search_documents(user_query, knowledge_file="data/document_index.json", top_k=5)
    
    if not doc_results:
        return None
        
    # Filter for category match if possible (our search_documents doesn't support category filter yet, 
    # but results include category metadata)
    relevant_chunks = [res['chunk'] for res in doc_results if res.get('category') == target_category]
    
    if not relevant_chunks:
        # Fallback to all chunks if strict category match fails 
        # (user might upload fee doc under 'General')
        relevant_chunks = [res['chunk'] for res in doc_results]

    # 3. Extract Dates
    date_pattern = r'(\d{1,2}(?:st|nd|rd|th)?\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?,?\s+\d{2,4})'
    # Valid formats: "20 February 2026", "20th Feb, 2026", "15 Jan 26"
    
    today = datetime.datetime.now()
    found_dates = []
    
    for chunk in relevant_chunks:
        matches = re.findall(date_pattern, chunk, re.IGNORECASE)
        for date_str in matches:
            try:
                # Normalize date string for parsing
                clean_date = re.sub(r'(st|nd|rd|th)', '', date_str) # Remove ordinal suffixes
                parse_formats = ["%d %B %Y", "%d %b %Y", "%d %B, %Y", "%d %b, %Y", "%d %b %y"]
                
                parsed_date = None
                for fmt in parse_formats:
                    try:
                        parsed_date = datetime.datetime.strptime(clean_date, fmt)
                        break
                    except ValueError:
                        continue
                        
                if parsed_date:
                    # Fix year if 2 digits (e.g. 26 -> 2026)
                    if parsed_date.year < 100:
                        parsed_date = parsed_date.replace(year=2000 + parsed_date.year)
                        
                    # Filter for UPCOMING dates (or recent past)
                    if parsed_date >= today - datetime.timedelta(days=7): 
                         found_dates.append(parsed_date)
            except Exception:
                continue
                
    if not found_dates:
        return None
        
    # 4. Generate Response
    # Sort to find the nearest upcoming date
    found_dates.sort()
    next_date = found_dates[0]
    date_str = next_date.strftime("%d %B %Y")
    
    responses = {
        "Fees": f"The upcoming fee payment deadline appears to be {date_str}.",
        "Exams": f"According to the schedule, the next major exam date is {date_str}.",
        "Events": f"The next scheduled event is on {date_str}.",
        "Calendar": f"Mark your calendar for {date_str} as a key academic date."
    }
    
    return responses.get(target_category, f"The relevant date found is {date_str}.")

def get_document_response(user_query, min_score=DOCUMENT_RELEVANCE_THRESHOLD):
    """
    Retrieves a response from uploaded documents.
    
    Args:
        user_query (str): User's question.
        min_score (int): Minimum relevance score to accept a document match.
        
    Returns:
        str or None: Document-based response if found, None otherwise.
    """
    # Search documents for relevant content
    doc_results = search_documents(user_query, knowledge_file="data/document_index.json", top_k=1)
    
    if doc_results and len(doc_results) > 0:
        best_match = doc_results[0]
        
        # Check if the match is relevant enough
        if best_match.get('score', 0) >= min_score:
            chunk = best_match['chunk']
            doc_name = best_match.get('document', 'our documents')
            
            # Format the response to indicate it's from documents
            return f"Based on {doc_name}: {chunk}"
    
    return None


# ---------------------------------------------------------
# Step 2: Two-Layer Static Knowledge Architecture
# ---------------------------------------------------------

def search_permanent_knowledge(user_msg):
    """
    LAYER 1: Permanent Knowledge Base (Intents)
    
    1. Uses ML Model (Bag of Words) to predict intent.
    2. If confidence >= threshold, returns intent response.
    3. Fallback: uses Sentence Embeddings (Semantic Similarity) if ML model is unsure.
    
    Returns:
        tuple: (response_string, confidence_score) or (None, confidence_score)
    """
    # 1. Neural Network Prediction
    intents_list, confidence = predict_class(user_msg)
    
    if intents_list and confidence >= CONFIDENCE_THRESHOLD:
        faq_response = get_faq_response(intents_list, intents)
        if faq_response:
            return faq_response, confidence
            
    # 2. Semantic Embedding (Fallback within Layer 1)
    # This helps catch matches that use different vocabulary but match an existing intent
    embedding_response = get_embedding_response(user_msg, min_score=0.5)
    if embedding_response:
        print("[DEBUG] Layer 1: Neural network unsure, but Embeddings found a match.")
        return embedding_response, confidence # Return confidence of NN even if embedding used (or could use embedding score)
        
    return None, confidence

def search_admin_static_knowledge(user_msg):
    """
    LAYER 2: Admin Static Knowledge Base (Uploaded Docs)
    
    Searches admin_static_knowledge.json using keyword matching.
    
    Returns:
        str or None: Response from documents.
    """
    # Use the document ingestion search module
    # Defaults are already updated in document_ingestion.py to point to admin_static_*.json
    doc_results = search_documents(user_msg, top_k=1)
    
    if doc_results and len(doc_results) > 0:
        best_match = doc_results[0]
        
        # Check relevance
        if best_match.get('score', 0) >= DOCUMENT_RELEVANCE_THRESHOLD:
            chunk = best_match['chunk']
            doc_name = best_match.get('document', 'documents')
            
            # Return clear source attribution
            return f"Based on {doc_name}: {chunk}"
            
    return None

def chatbot_response(msg):
    """
    Main Chatbot Interface - Two-Layer Architecture
    
    Flow:
    1. Check Stick Knowledge (Intents/ML)
    2. Check Admin Static Knowledge (Docs)
    3. Fallback
    """
    
    # STEP 1: Layer 1 - Permanent Knowledge Base
    response, confidence = search_permanent_knowledge(msg)
    if response:
        return response
        
    # STEP 2: Layer 2 - Admin Static Knowledge Base
    # Only search if Layer 1 failed (confidence < threshold or no intent found)
    doc_response = search_admin_static_knowledge(msg)
    if doc_response:
        # Log success from docs
        log_unanswered_query(msg, confidence, source="document")
        return doc_response
        
    # STEP 3: Fallback
    # Log failure
    log_unanswered_query(msg, confidence, source="none")
    
    return "I'm sorry, I'm not sure about that. I've noted your question for the administration to review. Please try rephrasing or ask something else."

# ---------------------------------------------------------
# Testing Block
# ---------------------------------------------------------
if __name__ == "__main__":
    print("\nTwo-Layer Chatbot Engine Loaded.")
    print("Priority: Intents (Layer 1) → Admin Docs (Layer 2) → Fallback\n")
    
    while True:
        message = input("You: ")
        if message.lower() == "quit":
            break
        
        response = chatbot_response(message)
        print("Bot:", response)
        print()
