import json
import os
import datetime
import uuid

def log_unanswered_query(user_query, confidence_score, source="none"):
    """
    Logs unanswered queries to a JSON file for future review.
    
    Args:
        user_query (str): The text the user entered.
        confidence_score (float or str): The confidence score of the model.
        source (str): Where the answer came from (faq/document/none).
    """
    # Define the directory and file path
    directory = "data"
    file_path = os.path.join(directory, "unanswered_queries.json")
    
    # Create the directory if it doesn't exist
    if not os.path.exists(directory):
        os.makedirs(directory)
        
    # Create the log entry
    log_entry = {
        "id": str(uuid.uuid4()),
        "query": user_query,
        "confidence": str(confidence_score),
        "source": source,
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": "unanswered"
    }
    
    # Load existing logs or initialize empty list
    current_logs = []
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r') as f:
                # Basic optimization: check file size before loading? 
                # For now, standard load is safest for JSON integrity.
                current_logs = json.load(f)
        except json.JSONDecodeError:
            current_logs = [] # Handle corrupted/empty file
            
    # Append new entry
    current_logs.append(log_entry)
    
    # Save back to file
    with open(file_path, 'w') as f:
        json.dump(current_logs, f, indent=4)
