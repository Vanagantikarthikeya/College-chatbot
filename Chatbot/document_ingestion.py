
import os
import json
import uuid
import re
from datetime import datetime

# -------------------------------------------------------------
# Document Processing Module
# -------------------------------------------------------------
# This module handles document ingestion and text extraction
# for PDF, DOCX, and TXT files.
# -------------------------------------------------------------

def extract_text_from_txt(file_obj):
    """
    Extracts text from a TXT file stream.
    
    Args:
        file_obj: File-like object (BytesIO or FileStorage).
        
    Returns:
        str: Extracted text content.
    """
    try:
        # FileStorage or BytesIO
        content = file_obj.read()
        # If bytes, decode. If str (unlikely for upload), use as is.
        if isinstance(content, bytes):
            return content.decode('utf-8', errors='ignore')
        return str(content)
    except Exception as e:
        print(f"Error reading TXT file: {e}")
        return ""

def extract_text_from_pdf(file_obj):
    """
    Extracts text from a PDF file stream using PyPDF2.
    
    Args:
        file_obj: File-like object (BytesIO or FileStorage).
        
    Returns:
        str: Extracted text content.
    """
    try:
        import PyPDF2
        text = ""
        # PyPDF2 can read from a file-like object directly
        pdf_reader = PyPDF2.PdfReader(file_obj)
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text
    except ImportError:
        print("PyPDF2 not installed. Install using: pip install PyPDF2")
        return ""
    except Exception as e:
        print(f"Error reading PDF file: {e}")
        return ""

def extract_text_from_docx(file_obj):
    """
    Extracts text from a DOCX file stream using python-docx.
    
    Args:
        file_obj: File-like object (BytesIO or FileStorage).
        
    Returns:
        str: Extracted text content.
    """
    try:
        from docx import Document
        # python-docx can open a file-like object
        doc = Document(file_obj)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text
    except ImportError:
        print("python-docx not installed. Install using: pip install python-docx")
        return ""
    except Exception as e:
        print(f"Error reading DOCX file: {e}")
        return ""

def clean_text(text):
    """
    Cleans and normalizes extracted text.
    
    Args:
        text (str): Raw text to clean.
        
    Returns:
        str: Cleaned text.
    """
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove special characters but keep basic punctuation
    text = re.sub(r'[^\w\s.,!?;:()\-]', '', text)
    # Strip leading/trailing whitespace
    text = text.strip()
    return text

def chunk_text(text, chunk_size=500):
    """
    Splits text into smaller chunks for better retrieval.
    
    Args:
        text (str): Text to chunk.
        chunk_size (int): Approximate size of each chunk in characters.
        
    Returns:
        list: List of text chunks.
    """
    # Split by sentences (simple approach)
    sentences = re.split(r'(?<=[.!?])\s+', text)
    
    chunks = []
    current_chunk = ""
    
    for sentence in sentences:
        if len(current_chunk) + len(sentence) < chunk_size:
            current_chunk += sentence + " "
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = sentence + " "
    
    # Add the last chunk
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks

def process_document(file_obj, filename, category):
    """
    Main function to process an uploaded document from memory.
    
    Args:
        file_obj: File-like object (BytesIO or FileStorage).
        filename (str): Original filename.
        category (str): Document category.
        
    Returns:
        tuple: (index_entry, content_entry) or (None, None) if failed.
    """
    # Determine file type
    file_extension = filename.lower().split('.')[-1]
    
    # Extract text based on file type
    if file_extension == 'txt':
        raw_text = extract_text_from_txt(file_obj)
    elif file_extension == 'pdf':
        raw_text = extract_text_from_pdf(file_obj)
    elif file_extension == 'docx':
        raw_text = extract_text_from_docx(file_obj)
    else:
        print(f"Unsupported file type: {file_extension}")
        return None, None
    
    if not raw_text or len(raw_text.strip()) < 10:
        print("No text extracted from document")
        return None, None
    
    # Clean the text
    cleaned_text = clean_text(raw_text)
    
    # Chunk the text
    chunks = chunk_text(cleaned_text)
    
    doc_id = str(uuid.uuid4())
    upload_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Create document index entry (metadata + chunks)
    index_entry = {
        "id": doc_id,
        "filename": filename,
        "category": category,
        "upload_date": upload_time,
        "status": "active",
        "chunks": chunks,
        "total_chunks": len(chunks)
    }

    # Create content entry (full text + basic metadata)
    content_entry = {
        "id": doc_id,
        "filename": filename,
        "category": category,
        "upload_time": upload_time,
        "content": cleaned_text
    }
    
    return index_entry, content_entry

def save_document_data(index_entry, content_entry, index_file="data/admin_static_metadata.json", content_file="data/admin_static_knowledge.json"):
    """
    Saves document metadata to metadata file and text content to knowledge file.
    
    Args:
        index_entry (dict): Entry for the metadata file.
        content_entry (dict): Entry for the knowledge file.
        index_file (str): Path to the metadata file.
        content_file (str): Path to the knowledge file.
        
    Returns:
        bool: True if successful, False otherwise.
    """
    # Ensure data directory exists
    os.makedirs(os.path.dirname(index_file), exist_ok=True)
    
    # 1. Update Metadata File (Structure: list of metadata objects)
    if os.path.exists(index_file):
        try:
            with open(index_file, 'r', encoding='utf-8') as f:
                index_data = json.load(f)
        except (json.JSONDecodeError, IOError):
            index_data = [] # List based on requirement structure if simple list, but keeping dict container is safer for extensibility.
            # However, usually top level is a list or strict dict. I'll stick to a list of dicts if I can, OR a dict with a key.
            # Original code used {"documents": []}. The requirement doesn't specify top-level structure, just fields.
            # I will stick to {"documents": []} for compatibility with existing load functions if possible, 
            # or better yet, just a list. But search relies on loading it.
            # I will use {"documents": [...]} to be safe and consistent with previous code structure unless told otherwise.
            index_data = {"documents": []}
    else:
        index_data = {"documents": []}
    
    # Ensure index_entry has the required fields: doc_id, title, category, uploaded_at
    # We might need to map from the passed 'index_entry' which likely has 'filename' -> 'title', 'upload_date' -> 'uploaded_at'
    
    # Mapping to required schema
    metadata_entry = {
        "doc_id": index_entry.get("id"),
        "title": index_entry.get("filename"),
        "category": index_entry.get("category"),
        "uploaded_at": index_entry.get("upload_date"), # or upload_time
        "status": index_entry.get("status", "active"), # Keeping status for management
        "total_chunks": index_entry.get("total_chunks", 0) # Support analytics
    }
    
    index_data["documents"].append(metadata_entry)
    
    # 2. Update Knowledge File (Structure: list of content objects or dict by ID?)
    # Requirement: admin_static_knowledge.json Fields: doc_id, extracted_text_content
    if os.path.exists(content_file):
        try:
            with open(content_file, 'r', encoding='utf-8') as f:
                content_data = json.load(f)
        except (json.JSONDecodeError, IOError):
            content_data = []
    else:
        content_data = []
        
    # We need to append to list, or use dict for fast lookup?
    # "Search admin_static_knowledge.json" suggests iterating or searching.
    # Storing as a list of objects is most standard for "datasets".
    
    knowledge_entry = {
        "doc_id": content_entry.get("id"),
        "extracted_text_content": content_entry.get("content"),
        "chunks": index_entry.get("chunks", []) # Keeping chunks here for search granularity
    }
    
    content_data.append(knowledge_entry)
    
    # Save both
    try:
        with open(index_file, 'w', encoding='utf-8') as f:
            json.dump(index_data, f, indent=4, ensure_ascii=False)
            
        with open(content_file, 'w', encoding='utf-8') as f:
            json.dump(content_data, f, indent=4, ensure_ascii=False)
            
        return True
    except IOError as e:
        print(f"Error saving document data: {e}")
        return False

def load_knowledge_base(knowledge_file="data/admin_static_metadata.json"):
    """
    Loads the document metadata.
    
    Args:
        knowledge_file (str): Path to the metadata file.
        
    Returns:
        dict: Knowledge base data {"documents": [...]}.
    """
    if not os.path.exists(knowledge_file):
        return {"documents": []}
    
    try:
        with open(knowledge_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Ensure compatibility if it returns a list directly
            if isinstance(data, list):
                return {"documents": data}
            return data
    except (json.JSONDecodeError, IOError):
        return {"documents": []}

def update_document_status(doc_id, new_status, knowledge_file="data/admin_static_metadata.json"):
    """
    Updates the status of a document in the metadata file.
    """
    knowledge_base = load_knowledge_base(knowledge_file)
    
    found = False
    for doc in knowledge_base.get("documents", []):
        if doc.get("doc_id") == doc_id:
            doc["status"] = new_status
            found = True
            break
    
    if not found:
        return False
        
    try:
        with open(knowledge_file, 'w', encoding='utf-8') as f:
            json.dump(knowledge_base, f, indent=4, ensure_ascii=False)
        return True
    except IOError:
        return False

def delete_document(doc_id, index_file="data/admin_static_metadata.json", content_file="data/admin_static_knowledge.json"):
    """
    Deletes a document from the metadata and knowledge files.
    """
    # 1. Update Metadata
    index_data = load_knowledge_base(index_file)
    documents = index_data.get("documents", [])
    
    new_documents = [doc for doc in documents if doc.get("doc_id") != doc_id]
    
    index_data["documents"] = new_documents
    
    # 2. Update Knowledge
    if os.path.exists(content_file):
        try:
            with open(content_file, 'r', encoding='utf-8') as f:
                content_data = json.load(f)
                # Content data is a list of dicts now
                if isinstance(content_data, list):
                    content_data = [item for item in content_data if item.get("doc_id") != doc_id]
                else: 
                     # Fallback if somehow dict
                     pass
        except (json.JSONDecodeError, IOError):
            content_data = []
    else:
         content_data = []
    
    # Save both
    try:
        with open(index_file, 'w', encoding='utf-8') as f:
            json.dump(index_data, f, indent=4, ensure_ascii=False)
            
        with open(content_file, 'w', encoding='utf-8') as f:
            json.dump(content_data, f, indent=4, ensure_ascii=False)
            
        return True
    except IOError:
        return False


def search_documents(query, metadata_file="data/admin_static_metadata.json", knowledge_file="data/admin_static_knowledge.json", top_k=3):
    """
    Searches document chunks for relevant content using keyword matching.
    Join metadata (status) with knowledge (content).
    """
    # 1. Load Metadata to check status
    metadata = load_knowledge_base(metadata_file)
    active_doc_ids = {doc.get("doc_id"): doc for doc in metadata.get("documents", []) if doc.get("status") == "active"}
    
    if not active_doc_ids:
        return []

    # 2. Load Knowledge Content
    if not os.path.exists(knowledge_file):
        return []
        
    try:
        with open(knowledge_file, 'r', encoding='utf-8') as f:
            knowledge_data = json.load(f)
    except Exception:
        return []
        
    # Normalize query
    query_lower = query.lower()
    query_words = set(re.findall(r'\w+', query_lower))
    
    # Score each chunk
    scored_chunks = []
    
    # Iterate through knowledge entries
    # knowledge_data should be a list of dicts: {doc_id, extracted_text_content, chunks}
    for entry in knowledge_data:
        doc_id = entry.get("doc_id")
        
        # Only search active documents
        if doc_id not in active_doc_ids:
            continue
            
        # Get chunks (fallback to splitting extracted_text_content if chunks not present)
        chunks = entry.get("chunks", [])
        if not chunks:
            # Fallback chunking if not saved
            full_text = entry.get("extracted_text_content", "")
            chunks = chunk_text(full_text)
            
        doc_meta = active_doc_ids[doc_id]
        
        for chunk in chunks:
            chunk_lower = chunk.lower()
            chunk_words = set(re.findall(r'\w+', chunk_lower))
            
            # Calculate simple keyword overlap score
            overlap = len(query_words.intersection(chunk_words))
            
            if overlap > 0:
                scored_chunks.append({
                    "chunk": chunk,
                    "score": overlap,
                    "document": doc_meta.get("title", "Unknown Document"),
                    "category": doc_meta.get("category", "General")
                })
    
    # Sort by score (descending)
    scored_chunks.sort(key=lambda x: x["score"], reverse=True)
    
    # Return top K results
    return scored_chunks[:top_k]
