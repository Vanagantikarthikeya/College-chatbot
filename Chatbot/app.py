
from flask import Flask, render_template, request, session, redirect, url_for, flash, jsonify
from chatbot_engine import chatbot_response
from document_ingestion import process_document, save_document_data, load_knowledge_base, update_document_status, search_documents, delete_document

from werkzeug.utils import secure_filename
import os
import traceback

import json
import functools

# Initialize Flask application
app = Flask(__name__)
app.static_folder = 'static'

# Secret key for session management
app.secret_key = 'academic_demo_secret_key_123'

# Admin Credentials (Hardcoded for Demo)
ADMIN_USERNAME = "Pallavi"
ADMIN_PASSWORD = "Pallavi@2026"

# Data File Configuration
DATA_DIR = "data"
LOG_FILE = "unanswered_queries.json"
INTENTS_FILE = "intents.json"
KNOWLEDGE_FILE = "data/admin_static_metadata.json"
CONTENT_FILE = "data/admin_static_knowledge.json"
UPLOAD_FOLDER = "data/uploads"
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

# Configure upload folder
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)

# -------------------------------------------------------------
# Helper Functions/Decorators
# -------------------------------------------------------------

def login_required(f):
    """
    Decorator to ensure user is logged in as admin.
    """
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_logged_in' not in session:
            flash("Please log in to access this page.", "error")
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

def get_unanswered_queries():
    """
    Reads the unanswered queries from the JSON file.
    Returns list reversed (newest first).
    """
    file_path = os.path.join(DATA_DIR, LOG_FILE)
    if not os.path.exists(file_path):
        return []
    
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
            return data[::-1]
    except (json.JSONDecodeError, IOError):
        return []

def load_intents():
    """
    Loads the intents.json file.
    Returns the intents data structure.
    """
    try:
        with open(INTENTS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data
    except (json.JSONDecodeError, IOError, FileNotFoundError):
        return {"intents": []}

def save_intents(intents_data):
    """
    Saves the intents data back to intents.json.
    """
    try:
        with open(INTENTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(intents_data, f, indent=4, ensure_ascii=False)
        return True
    except IOError:
        return False

def compute_analytics():
    """
    Computes analytics and insights from stored data.
    
    Returns:
        dict: Analytics data including metrics and insights.
    """
    analytics = {
        'total_queries': 0,
        'answered_by_faq': 0,
        'answered_by_docs': 0,
        'unanswered_count': 0,
        'resolved_count': 0,
        'total_faqs': 0,
        'total_documents': 0,
        'active_documents': 0,
        'total_chunks': 0,
        'success_rate': 0,
        'frequent_unanswered': [],
        'recent_queries': []
    }
    
    # Load unanswered queries log
    queries_file = os.path.join(DATA_DIR, LOG_FILE)
    all_queries = []
    
    if os.path.exists(queries_file):
        try:
            with open(queries_file, 'r') as f:
                all_queries = json.load(f)
        except (json.JSONDecodeError, IOError):
            all_queries = []
    
    # Total queries logged
    analytics['total_queries'] = len(all_queries)
    
    # Count by source and status
    query_frequency = {}
    
    for query in all_queries:
        source = query.get('source', 'none')
        status = query.get('status', 'unanswered')
        query_text = query.get('query', '').lower().strip()
        
        # Count by source
        if source == 'document':
            analytics['answered_by_docs'] += 1
        elif source == 'none':
            analytics['unanswered_count'] += 1
        
        # Count resolved
        if status == 'resolved':
            analytics['resolved_count'] += 1
        
        # Track query frequency for unanswered
        if status == 'unanswered' and query_text:
            if query_text not in query_frequency:
                query_frequency[query_text] = {
                    'query': query.get('query', ''),
                    'count': 0,
                    'status': status,
                    'source': source
                }
            query_frequency[query_text]['count'] += 1
    
    # FAQ count (queries answered by FAQ are not logged)
    analytics['answered_by_faq'] = max(0, analytics['total_queries'] - analytics['answered_by_docs'] - analytics['unanswered_count'])
    
    # Success rate calculation
    if analytics['total_queries'] > 0:
        successful = analytics['answered_by_faq'] + analytics['answered_by_docs']
        analytics['success_rate'] = round((successful / analytics['total_queries']) * 100, 1)
    
    # Sort frequent unanswered queries
    frequent_list = sorted(query_frequency.values(), key=lambda x: x['count'], reverse=True)
    analytics['frequent_unanswered'] = frequent_list[:10]
    
    # Recent queries (last 10)
    analytics['recent_queries'] = all_queries[-10:][::-1]
    
    # Load FAQ count
    intents_data = load_intents()
    analytics['total_faqs'] = len(intents_data.get('intents', []))
    
    # Load document stats
    knowledge_base = load_knowledge_base(KNOWLEDGE_FILE)
    documents = knowledge_base.get('documents', [])
    analytics['total_documents'] = len(documents)
    
    active_docs = 0
    total_chunks = 0
    
    for doc in documents:
        if doc.get('status') == 'active':
            active_docs += 1
        total_chunks += doc.get('total_chunks', 0)
    
    analytics['active_documents'] = active_docs
    analytics['total_chunks'] = total_chunks
    
    return analytics

def allowed_file(filename):
    """
    Checks if the uploaded file has an allowed extension.
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# -------------------------------------------------------------
# Public Routes
# -------------------------------------------------------------

@app.route("/")
def home():
    """
    Main college homepage.
    """
    return render_template("main.html")

@app.route("/helpdesk")
def helpdesk():
    """
    Student helpdesk chatbot page.
    """
    return render_template("chatbot.html")

@app.route("/get-response", methods=["POST"])
def get_bot_response():
    """
    API endpoint for chatbot responses.
    """
    user_message = request.json.get("message", "")
    if not user_message:
        return jsonify({"response": "Please enter a message."})
    
    bot_response = chatbot_response(user_message)
    return jsonify({"response": bot_response})

# -------------------------------------------------------------
# Admin Routes
# -------------------------------------------------------------

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    """
    Admin login page.
    """
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            flash("Login successful!", "success")
            return redirect(url_for('admin_dashboard'))
        else:
            flash("Invalid credentials. Please try again.", "error")
    
    return render_template("admin/login.html")

@app.route("/admin/logout")
def admin_logout():
    """
    Admin logout.
    """
    session.pop('admin_logged_in', None)
    flash("You have been logged out.", "success")
    return redirect(url_for('home'))

@app.route("/admin/dashboard")
@login_required
def admin_dashboard():
    """
    Admin dashboard - main admin page.
    """
    return render_template("admin/dashboard.html")

@app.route("/admin/analytics")
@login_required
def admin_analytics():
    """
    Analytics and insights page.
    """
    analytics_data = compute_analytics()
    return render_template("admin/analytics.html", analytics=analytics_data)

@app.route("/admin/knowledge")
@login_required
def admin_knowledge():
    """
    Knowledge management page (FAQs + Documents).
    """
    # Load FAQs
    intents_data = load_intents()
    intents_list = intents_data.get('intents', [])
    
    # Load Documents
    knowledge_base = load_knowledge_base(KNOWLEDGE_FILE)
    documents = knowledge_base.get('documents', [])
    
    return render_template("admin/knowledge.html", intents=intents_list, documents=documents)

@app.route("/admin/add-faq", methods=["POST"])
@login_required
def admin_add_faq():
    """
    Add new FAQ.
    """
    tag = request.form.get('tag', '').strip()
    patterns = request.form.get('patterns', '').strip()
    responses = request.form.get('responses', '').strip()
    
    if not tag or not patterns or not responses:
        flash("All fields are required.", "error")
        return redirect(url_for('admin_knowledge'))
    
    # Parse patterns and responses
    patterns_list = [p.strip() for p in patterns.split('\n') if p.strip()]
    responses_list = [r.strip() for r in responses.split('\n') if r.strip()]
    
    if not patterns_list or not responses_list:
        flash("Please provide at least one pattern and one response.", "error")
        return redirect(url_for('admin_knowledge'))
    
    # Load current intents
    intents_data = load_intents()
    intents_list = intents_data.get('intents', [])
    
    # Check if tag already exists
    for intent in intents_list:
        if intent['tag'] == tag:
            flash(f"FAQ with tag '{tag}' already exists. Use edit instead.", "error")
            return redirect(url_for('admin_knowledge'))
    
    # Create new intent
    new_intent = {
        "tag": tag,
        "patterns": patterns_list,
        "responses": responses_list
    }
    
    intents_list.append(new_intent)
    intents_data['intents'] = intents_list
    
    # Save to file
    if save_intents(intents_data):
        flash(f"FAQ '{tag}' added successfully!", "success")
    else:
        flash("Error saving FAQ. Please try again.", "error")
    
    return redirect(url_for('admin_knowledge'))

@app.route("/admin/delete-faq", methods=["POST"])
@login_required
def admin_delete_faq():
    """
    Delete FAQ.
    """
    tag = request.form.get('tag', '').strip()
    
    if not tag:
        flash("Please select an intent to delete.", "error")
        return redirect(url_for('admin_knowledge'))
    
    # Load current intents
    intents_data = load_intents()
    intents_list = intents_data.get('intents', [])
    
    # Filter out the intent to delete
    original_count = len(intents_list)
    intents_list = [intent for intent in intents_list if intent['tag'] != tag]
    
    if len(intents_list) == original_count:
        flash(f"Intent '{tag}' not found.", "error")
        return redirect(url_for('admin_knowledge'))
    
    intents_data['intents'] = intents_list
    
    # Save to file
    if save_intents(intents_data):
        flash(f"FAQ '{tag}' deleted successfully!", "success")
    else:
        flash("Error deleting FAQ. Please try again.", "error")
    
    return redirect(url_for('admin_knowledge'))

@app.route("/upload_document", methods=["POST"])
@login_required
def upload_document():
    """
    Safe in-memory document upload and processing.
    """
    import sys
    import uuid
    from datetime import datetime
    
    print("UPLOAD ROUTE HIT")
    sys.stdout.flush()

    # Helper to get fresh data for rendering
    def get_render_data():
        try:
            intents_data = load_intents()
            knowledge_base = load_knowledge_base(KNOWLEDGE_FILE)
            return intents_data.get('intents', []), knowledge_base.get('documents', [])
        except Exception:
            return [], []

    # Initialize default context
    category = ""
    try:
        # Get form data safely
        category = request.form.get('category', '').strip()
        
        # Check file presence
        file = request.files.get('document')
        if not file or file.filename == '':
            flash("No file selected.", "error")
            intents_list, documents = get_render_data()
            return render_template("admin/knowledge.html", intents=intents_list, documents=documents, selected_category=category)
        
        filename = secure_filename(file.filename)
        content = ""
        
        # 1. READ CONTENT (In-Memory)
        try:
            if filename.lower().endswith(".txt"):
                content = file.read().decode("utf-8", errors="ignore")

            elif filename.lower().endswith(".pdf"):
                import pdfplumber
                try:
                    with pdfplumber.open(file) as pdf:
                        content = "\n".join(page.extract_text() or "" for page in pdf.pages)
                    
                    # Check for scanned PDF (image-based)
                    if not content or not content.strip():
                        flash("This PDF appears to be a scanned image and contains no extractable text. Please upload a text-based PDF.", "error")
                        intents_list, documents = get_render_data()
                        return render_template("admin/knowledge.html", intents=intents_list, documents=documents, selected_category=category)
                        
                except ImportError:
                    flash("server error: pdfplumber not installed", "error")
                    intents_list, documents = get_render_data()
                    return render_template("admin/knowledge.html", intents=intents_list, documents=documents, selected_category=category)

            elif filename.lower().endswith(".docx"):
                from docx import Document
                try:
                   doc = Document(file)
                   content = "\n".join([p.text for p in doc.paragraphs])
                except ImportError:
                   flash("server error: python-docx not installed", "error")
                   intents_list, documents = get_render_data()
                   return render_template("admin/knowledge.html", intents=intents_list, documents=documents, selected_category=category)

            else:
                flash("Unsupported file type. Allowed: .txt, .pdf, .docx", "error")
                intents_list, documents = get_render_data()
                return render_template("admin/knowledge.html", intents=intents_list, documents=documents, selected_category=category)

        except Exception as e:
            traceback.print_exc()
            flash(f"Error reading file: {str(e)}", "error")
            intents_list, documents = get_render_data()
            return render_template("admin/knowledge.html", intents=intents_list, documents=documents, selected_category=category)

        # 2. VALIDATE CONTENT
        if not content or len(content.strip()) < 10:
             flash("Extracted content is too short or empty.", "error")
             intents_list, documents = get_render_data()
             return render_template("admin/knowledge.html", intents=intents_list, documents=documents, selected_category=category)

        # 3. PREPARE DATA
        # We misuse query chunking logic from document_ingestion for consistency but skip processing logic
        # Ideally, we should replicate chunking here or call a helper, I'll call a helper from extraction
        from document_ingestion import clean_text, chunk_text
        
        cleaned_text = clean_text(content)
        chunks = chunk_text(cleaned_text)
        
        doc_id = str(uuid.uuid4())
        upload_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        index_entry = {
            "id": doc_id,
            "filename": filename,
            "category": category,
            "upload_date": upload_time,
            "status": "active",
            "chunks": chunks,
            "total_chunks": len(chunks)
        }

        content_entry = {
            "id": doc_id,
            "filename": filename,
            "category": category,
            "upload_time": upload_time,
            "content": cleaned_text
        }

        # 4. SAVE DATA
        if save_document_data(index_entry, content_entry, KNOWLEDGE_FILE, CONTENT_FILE):
            flash(f"Success! '{filename}' processed and indexed.", "success")
        else:
            flash("Database save failed.", "error")
            
    except Exception as e:
        traceback.print_exc()
        flash(f"Critical System Error: {str(e)}", "error")
    
    # Always reload data and render page
    intents_list, documents = get_render_data()
    return render_template("admin/knowledge.html", intents=intents_list, documents=documents, selected_category=category)

@app.route("/admin/toggle-document", methods=["POST"])
@login_required
def admin_toggle_document():
    """
    Toggle document status.
    """
    doc_id = request.form.get('doc_id', '').strip()
    current_status = request.form.get('current_status', '').strip()
    
    if not doc_id:
        flash("Invalid document ID.", "error")
        return redirect(url_for('admin_knowledge'))
    
    # Toggle status
    new_status = 'inactive' if current_status == 'active' else 'active'
    
    if update_document_status(doc_id, new_status, KNOWLEDGE_FILE):
        flash(f"Document status updated to {new_status}.", "success")
    else:
        flash("Error updating document status.", "error")
    
    return redirect(url_for('admin_knowledge'))

@app.route("/admin/delete-document", methods=["POST"])
@login_required
def admin_delete_document():
    """
    Delete document.
    """
    doc_id = request.form.get('doc_id', '').strip()
    
    if not doc_id:
        flash("Invalid document ID.", "error")
        return redirect(url_for('admin_knowledge'))
    
    # Pass both files to delete_document
    if delete_document(doc_id, KNOWLEDGE_FILE, CONTENT_FILE):
        flash("Document deleted successfully.", "success")
    else:
        flash("Error deleting document.", "error")
    
    return redirect(url_for('admin_knowledge'))


if __name__ == "__main__":
    print("Starting College Website Server...")
    app.run(host='0.0.0.0', port=5000, debug=True)
