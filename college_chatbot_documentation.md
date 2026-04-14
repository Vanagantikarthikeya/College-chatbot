# College Chatbot – AI-Powered Student Helpdesk System
### Comprehensive Project Documentation

---

## 1. Project Basic Details

| Field | Details |
|---|---|
| **Project Title** | AI-Powered College Helpdesk Chatbot System |
| **Institution** | Pallavi Engineering College, Hyderabad |
| **Domain** | Artificial Intelligence / Natural Language Processing / Web Application |
| **Academic Year** | 2025–2026 |

### Problem Statement
Students at engineering colleges frequently face difficulties in obtaining timely and accurate information regarding admissions, exam schedules, fee structures, library details, placements, and other institutional services. Manual helpdesk systems are slow, inconsistent, and unavailable outside office hours, leading to student frustration and administrative overhead.

### Objective of the Project
To design and deploy an intelligent, web-based chatbot system that can:
- Automatically respond to student queries using a trained NLP model
- Search and retrieve information from admin-uploaded documents as a secondary source
- Log unanswered queries to identify knowledge gaps
- Provide an admin panel for managing FAQs, documents, and viewing analytics

### Motivation Behind the Project
- **24/7 Availability**: Students need answers outside of office hours
- **Reduce Admin Burden**: Free staff from repetitive query handling
- **Continuous Learning**: The system can be improved by admins based on logged unanswered questions
- **Digital Transformation**: Bridge the gap between traditional helpdesks and modern student expectations
- **AI-in-Education**: Practical application of AI/ML for real-world institutional problems

---

## 2. Abstract

The AI-Powered College Helpdesk Chatbot is an intelligent web application developed for Pallavi Engineering College to facilitate automated student assistance. The system employs a two-layer hybrid architecture combining a trained Multi-Layer Perceptron (MLP) neural network for intent classification with a semantic sentence embedding fallback using the `all-MiniLM-L6-v2` Sentence Transformer model. This allows the chatbot to handle a wide variety of natural language queries with both speed and semantic awareness.

When neither the static knowledge base (FAQ intents) nor the semantic embeddings produce a confident response, the system seamlessly transitions to a dynamic document search layer, querying admin-uploaded institutional documents (PDFs, DOCX, TXT) through keyword-based chunk retrieval. All unanswered queries are logged to a structured JSON file, enabling administrators to identify knowledge gaps and continuously improve system coverage.

The administrative backend, secured behind session-based authentication, offers a comprehensive dashboard for managing FAQ intents, uploading and toggling documents, and viewing performance analytics including success rates, query distribution by source, and frequent knowledge gaps.

Built using Flask (Python), the system follows RESTful routing conventions, Jinja2-based HTML templating, and a file-based JSON data store — making it lightweight, portable, and easy to deploy without requiring a full database server. The project demonstrates the practical integration of NLP, machine learning, document processing, and web development into a cohesive institutional tool.

---

## 3. Introduction

### Background of the Problem
Engineering colleges manage thousands of students who continuously generate queries about:
- Admission procedures and eligibility criteria
- Exam schedules and fee payment deadlines
- Library timings and borrowing rules
- Placement drives and internship opportunities
- Hostel regulations and contact information

Traditionally, this information is dispersed across notice boards, websites, and administrative offices — creating an inconsistent and time-consuming experience for students.

### Importance of the Project
An AI chatbot tailored to the college environment:
- Provides **instant, consistent responses** across all channels
- **Scales effortlessly** — one chatbot serves thousands of students simultaneously
- Creates a **learning feedback loop** via unanswered query logging
- Reduces the **cognitive load** on administrative staff
- Can be **updated dynamically** by admins without any coding knowledge

### Overview of the Solution
The system provides:
1. A **student-facing chatbot page** accessible at `/helpdesk`
2. A **trained intent classifier** (MLP neural network) fine-tuned on college-specific Q&A patterns
3. A **semantic similarity fallback** (Sentence Transformers) for paraphrased or novel queries
4. A **document search layer** for admin-uploaded institutional knowledge
5. An **admin panel** with FAQ management, document ingestion, and analytics

---

## 4. Existing System

### Current Systems Available

| System Type | Description |
|---|---|
| **Manual Help Desks** | Staff-operated inquiry counters in administrative offices |
| **College Websites** | Static pages with FAQs and notice boards |
| **Rule-Based Chatbots** | Simple keyword-match bots with no semantic understanding |
| **General AI Assistants** | Generic tools like ChatGPT not tuned for institution-specific data |

### Limitations / Drawbacks

- **Not available 24/7**: Manual helpdesks operate only during office hours
- **Inconsistent Answers**: Different staff may give different responses to the same query
- **No Institutional Tuning**: Generic AI tools lack college-specific knowledge
- **Information Silos**: Important documents are not searchable in real-time
- **No Analytics**: No mechanism to track what students are asking or where the system fails
- **Static FAQs**: Websites cannot understand natural language or paraphrased questions
- **Rule-Based Limitations**: Keyword chatbots break down when students rephrase questions

---

## 5. Proposed System

### What is the New System
An AI-powered, two-layer hybrid chatbot system that:
1. Uses a trained **MLP neural network** to classify student intent from natural language input
2. Applies **cosine similarity via Sentence Transformers** as a semantic fallback
3. Searches **admin-uploaded documents** (PDF/DOCX/TXT) via chunked keyword retrieval
4. Logs all **unresolved queries** for admin review
5. Provides an **admin dashboard** for live FAQ editing, document management, and analytics

### Advantages Over Existing System

| Feature | Old System | Proposed System |
|---|---|---|
| Availability | Office hours only | 24/7 |
| Response consistency | Variable | Uniform |
| Natural language understanding | No | Yes (NLP + ML) |
| Document search | No | Yes |
| Admin analytics | No | Yes |
| Knowledge updates | Manual, technical | Admin-friendly panel |
| Unanswered query tracking | No | Yes (JSON logging) |

### Key Innovations
- **Two-Layer Hybrid Architecture**: ML model + Document fallback ensures maximum coverage
- **Semantic Embedding Fallback**: Uses sentence vector similarity to handle paraphrasing
- **Admin-Driven Dynamic Knowledge**: Admins can upload PDFs and toggle documents without code
- **Intelligent Query Logging**: System learns what it doesn't know and surfaces gaps to admins
- **Synonym Normalization**: Pre-processing layer maps synonyms (e.g., "register" → "apply") for stability

---

## 6. System Architecture

### Detailed Explanation

The system follows a **layered, request-response architecture** hosted on a Flask web server:

```
Student Browser
    │
    ▼
Flask Web Server (app.py)
    │
    ├── Route: /helpdesk → chatbot.html (UI)
    ├── Route: /get-response → chatbot_engine.chatbot_response()
    │       │
    │       ├── LAYER 1: Permanent Knowledge Base
    │       │       ├── NLP Preprocessing (nlp_preprocessing.py)
    │       │       │       └── Tokenization + Lemmatization (NLTK)
    │       │       ├── Bag-of-Words Vectorization
    │       │       ├── MLP Neural Network Prediction (model.pkl)
    │       │       └── Sentence Embedding Fallback (SentenceTransformer)
    │       │
    │       └── LAYER 2: Admin Static Knowledge Base
    │               └── Keyword Chunk Search (document_ingestion.py)
    │                       └── admin_static_knowledge.json
    │
    └── Admin Routes (/admin/*)
            ├── Login (session auth)
            ├── Dashboard
            ├── FAQ Management (intents.json)
            ├── Document Upload & Management
            └── Analytics (unanswered_queries.json)
```

### Components Involved

| Component | File | Role |
|---|---|---|
| Web Server | `app.py` | Routing, session management, admin logic |
| Chatbot Engine | `chatbot_engine.py` | Hybrid NLP response engine |
| NLP Preprocessing | `nlp_preprocessing.py` | Tokenization and lemmatization |
| Document Ingestion | `document_ingestion.py` | File parsing, chunking, search |
| Model Training | `train_model.py` | One-time offline model training |
| Intent Database | `intents.json` | FAQ patterns and responses |
| Trained Model | `model.pkl` | Serialized MLP classifier |
| Vocabulary | `words.pkl` | Lemmatized word list for BoW |
| Class Labels | `classes.pkl` | Intent tag list |
| Document Index | `data/admin_static_metadata.json` | Document metadata and status |
| Document Content | `data/admin_static_knowledge.json` | Chunked text content |
| Query Log | `data/unanswered_queries.json` | Failed/partial responses log |

### Data Flow Explanation

1. Student types a query → AJAX POST to `/get-response`
2. `chatbot_engine.chatbot_response()` is called
3. **Layer 1**: Query is normalized, tokenized, vectorized → MLP predicts intent
   - If confidence ≥ 0.65: return FAQ response
   - Else: try Sentence Embedding cosine similarity (threshold 0.5)
4. **Layer 2**: If both fail, search admin-uploaded document chunks (keyword overlap)
   - Minimum relevance score = 2 keyword matches
5. **Fallback**: If all layers fail, log the query and return a default message
6. Admin reviews logs, adds FAQs or uploads documents to improve coverage over time

---

## 7. Technologies Used

| # | Name | Purpose | Why Chosen |
|---|---|---|---|
| 1 | **Python 3.x** | Core backend language | Extensive AI/ML ecosystem, Flask compatibility |
| 2 | **Flask** | Web framework | Lightweight, easy routing, Jinja2 templating |
| 3 | **scikit-learn (MLPClassifier)** | Neural network for intent classification | Simple, portable, no GPU required |
| 4 | **NLTK** | Tokenization and lemmatization | Standard NLP preprocessing library |
| 5 | **Sentence Transformers** | Semantic similarity fallback | Pre-trained embeddings for paraphrase handling |
| 6 | **NumPy** | Bag-of-words array processing | Fast vectorized operations |
| 7 | **pdfplumber** | PDF text extraction | Reliable text extraction from PDFs |
| 8 | **python-docx** | DOCX text extraction | Standard library for Word documents |
| 9 | **HTML5 + CSS3** | Frontend UI | Native, no framework dependency |
| 10 | **JavaScript (Vanilla)** | AJAX chatbot message handling | Lightweight, no framework needed |
| 11 | **Jinja2** | HTML templating | Built into Flask, dynamic page rendering |
| 12 | **JSON** | Data storage (intents, docs, logs) | Portable flat-file storage, no DB server |
| 13 | **Werkzeug** | Secure file handling | Part of Flask ecosystem |
| 14 | **Pickle** | Model serialization | Standard Python object persistence |
| 15 | **UUID** | Unique document IDs | Collision-free identifier generation |
| 16 | **Regex (re)** | Text cleaning and synonym normalization | Flexible pattern matching |

---

## 8. Modules Description

### Module 1: Student Chatbot Interface
- **Name**: Student Helpdesk Chatbot
- **Description**: The public-facing chat page where students interact with the bot
- **Functionality**: Displays a chat window; sends user messages via AJAX; renders bot responses in real-time
- **Input**: Student's natural language text message
- **Output**: Bot-generated response displayed in the chat window

### Module 2: Chatbot Engine (NLP Core)
- **Name**: Hybrid Chatbot Engine (`chatbot_engine.py`)
- **Description**: Central intelligence of the system orchestrating the two-layer response strategy
- **Functionality**:
  - Synonym normalization
  - BoW vectorization and MLP prediction (Layer 1)
  - Sentence embedding cosine similarity (Layer 1 fallback)
  - Document chunk search (Layer 2)
  - Query logging on failure
- **Input**: Raw user message string
- **Output**: Response string (from FAQ, documents, or fallback message)

### Module 3: Model Training
- **Name**: NLP Model Trainer (`train_model.py`)
- **Description**: Offline script used to train the MLP classifier on the intents dataset
- **Functionality**: Reads `intents.json` → tokenizes → creates BoW training data → trains MLP → saves `model.pkl`, `words.pkl`, `classes.pkl`
- **Input**: `intents.json` (FAQ patterns and tags)
- **Output**: `model.pkl`, `words.pkl`, `classes.pkl`

### Module 4: NLP Preprocessing
- **Name**: Text Preprocessor (`nlp_preprocessing.py`)
- **Description**: Converts raw text into standardized tokens using NLTK or fallback string processing
- **Functionality**: Tokenizes sentences, lemmatizes words, creates Bag-of-Words arrays
- **Input**: Raw sentence string + vocabulary list
- **Output**: Bag-of-Words NumPy array

### Module 5: Document Ingestion & Search
- **Name**: Document Processor (`document_ingestion.py`)
- **Description**: Handles extraction, cleaning, chunking, saving, and searching of admin-uploaded documents
- **Functionality**:
  - Extract text from TXT, PDF, DOCX files
  - Clean and normalize text
  - Split into 500-character chunks
  - Save metadata to `admin_static_metadata.json` and content to `admin_static_knowledge.json`
  - Search active document chunks via keyword overlap scoring
- **Input**: Uploaded file object, filename, category
- **Output**: Indexed document with chunks; search results with relevance scores

### Module 6: Admin Authentication & Dashboard
- **Name**: Admin Authentication Module
- **Description**: Session-based login system protecting all admin routes
- **Functionality**: Validates hardcoded credentials, sets session flag, decorates protected routes with `@login_required`
- **Input**: Username and password from login form
- **Output**: Authenticated session or error flash message

### Module 7: FAQ Management
- **Name**: Knowledge Base Manager (Part of `app.py`)
- **Description**: Allows admins to add/delete FAQ intent entries in `intents.json`
- **Functionality**: Lists intents, parses multi-line patterns/responses, adds new tags, deletes by tag
- **Input**: Intent tag, patterns (one per line), responses (one per line)
- **Output**: Updated `intents.json` file

### Module 8: Analytics Engine
- **Name**: Analytics Module (Part of `app.py`)
- **Description**: Computes performance metrics from stored query logs and knowledge base
- **Functionality**: Calculates total queries, success rate, FAQ vs. document vs. unanswered counts, identifies frequent knowledge gaps
- **Input**: `unanswered_queries.json`, `intents.json`, `admin_static_metadata.json`
- **Output**: Analytics dictionary rendered on the admin analytics page

---

## 9. Working of the System

### Step-by-Step Working Process

**Step 1: Startup**  
The admin runs `python app.py`. Flask loads the chatbot engine, which reads `intents.json`, loads `model.pkl`, `words.pkl`, `classes.pkl`, and pre-computes Sentence Transformer embeddings for all FAQ patterns.

**Step 2: Student Visits the Site**  
Student navigates to `http://localhost:5000/`. The homepage (`main.html`) is shown with a "Student Helpdesk" navigation link.

**Step 3: Student Opens the Chatbot**  
Student clicks "Student Helpdesk" → navigates to `/helpdesk` → `chatbot.html` is rendered showing a clean chat interface.

**Step 4: Student Sends a Message**  
Student types a question and presses Send. JavaScript captures the input and sends an AJAX POST request to `/get-response` with the message in JSON format.

**Step 5: Layer 1 Processing (FAQ + Embedding)**  
- The message is synonym-normalized (e.g., "register" → "apply")
- Tokenized and lemmatized via NLTK
- Converted to a Bag-of-Words vector
- The MLP classifier predicts probabilities for all intent classes
- If the top prediction confidence ≥ 0.65, the matching FAQ response is returned

**Step 6: Semantic Embedding Fallback**  
- If MLP confidence is low, the user query is encoded using Sentence Transformer
- Cosine similarity is computed against all pre-encoded FAQ patterns
- If the best similarity ≥ 0.5, the response for the matched intent is returned

**Step 7: Layer 2 Processing (Document Search)**  
- If both Layer 1 attempts fail, the system searches admin-uploaded documents
- Query words are compared against chunks from active documents using keyword overlap
- If a chunk's score ≥ 2, it is returned with source attribution (e.g., "Based on fee_structure.pdf: ...")

**Step 8: Fallback**  
- If no layer produces a confident answer, a default fallback message is returned
- The query is logged to `data/unanswered_queries.json` with timestamp and confidence score

**Step 9: Admin Reviews and Improves**  
- Admin logs into `/admin/login` with credentials
- Reviews the Analytics page to see knowledge gaps
- Adds new FAQ intents or uploads new documents
- Re-trains the model if new FAQs are added (optional manual step)

### User Flow

```
Student → Opens /helpdesk → Types query → Receives response
                                                │
                                                ▼
         ┌──────────────────────────────────────────────────────┐
         │           Response Priority                          │
         │  1. MLP FAQ match (confidence ≥ 65%)                │
         │  2. Sentence Embedding match (similarity ≥ 50%)     │
         │  3. Document keyword search (overlap ≥ 2)           │
         │  4. Fallback + query logged                         │
         └──────────────────────────────────────────────────────┘
```

---

## 10. Algorithms / Logic Used

### Algorithm 1: Bag-of-Words (BoW) Vectorization
- **Purpose**: Convert text to numerical format for the MLP
- **Steps**:
  1. Tokenize input sentence using NLTK `word_tokenize`
  2. Lemmatize all tokens using `WordNetLemmatizer`
  3. Create a binary array of length = vocabulary size
  4. Set index to `1` if the lemmatized word exists in the vocabulary

### Algorithm 2: MLP Intent Classification
- **Model**: `MLPClassifier` (scikit-learn) with hidden layers `(128, 64)`, ReLU activation, Adam optimizer
- **Input**: BoW vector
- **Output**: Probability distribution over all intent classes (softmax)
- **Decision**: If `max(probabilities) ≥ 0.65`, accept the top predicted class

### Algorithm 3: Sentence Embedding Cosine Similarity
- **Model**: `all-MiniLM-L6-v2` (Sentence Transformers)
- **Pre-computation**: All FAQ patterns are encoded into embedding vectors at startup
- **At query time**:
  1. Encode user query into embedding vector
  2. Compute cosine similarity against all stored pattern embeddings
  3. If `max(similarity) ≥ 0.5`, return response from matched intent

**Cosine Similarity Formula**:
```
similarity(A, B) = (A · B) / (||A|| × ||B||)
```
Where A = query embedding, B = pattern embedding.

### Algorithm 4: Document Keyword Search
- **Strategy**: Keyword overlap scoring
- **Steps**:
  1. Extract vocabulary from user query (set of unique words)
  2. For each chunk of each active document, extract its vocabulary
  3. Compute intersection size: `score = |query_words ∩ chunk_words|`
  4. Return the top-K chunks sorted by score (descending)
  5. Accept if `score ≥ DOCUMENT_RELEVANCE_THRESHOLD (= 2)`

### Algorithm 5: Synonym Normalization
- **Purpose**: Handle common synonym variants before ML processing
- **Method**: Regex whole-word replacement using a predefined dictionary:
  ```python
  SYNONYMS = {"register": "apply", "pay": "fee", "semester": "term", ...}
  ```

### Algorithm 6: Text Chunking
- **Purpose**: Split large document texts into searchable pieces
- **Method**: Sentence-boundary splitting; accumulate sentences until chunk reaches ~500 characters

---

## 11. Database Design

> The project uses **JSON flat-files** as a lightweight database (no SQL/NoSQL server required).

### File 1: `intents.json` — FAQ Knowledge Base
| Field | Type | Description |
|---|---|---|
| `intents` | Array | Top-level container |
| `tag` | String | Unique intent identifier (e.g., "admissions") |
| `patterns` | Array[String] | Sample user questions for this intent |
| `responses` | Array[String] | Possible chatbot responses (randomly selected) |

### File 2: `data/admin_static_metadata.json` — Document Index
| Field | Type | Description |
|---|---|---|
| `documents` | Array | List of all uploaded documents |
| `doc_id` | String (UUID) | Unique document identifier |
| `title` | String | Original filename |
| `category` | String | Admin-assigned category (e.g., "Fees", "Exams") |
| `uploaded_at` | String (datetime) | Upload timestamp |
| `status` | String | "active" or "inactive" |
| `total_chunks` | Integer | Number of text chunks extracted |

### File 3: `data/admin_static_knowledge.json` — Document Content
| Field | Type | Description |
|---|---|---|
| `doc_id` | String (UUID) | Links to metadata file |
| `extracted_text_content` | String | Full cleaned text from document |
| `chunks` | Array[String] | Pre-split text chunks for search |

### File 4: `data/unanswered_queries.json` — Query Log
| Field | Type | Description |
|---|---|---|
| `query` | String | The original user query text |
| `confidence` | Float | Max probability from MLP output |
| `source` | String | "document" (partial success) or "none" (full failure) |
| `status` | String | "unanswered" or "resolved" |
| `timestamp` | String | When the query was logged |

### Relationships
```
intents.json   ──[tag]──→  model.pkl (trained on patterns)
admin_static_metadata.json  ──[doc_id]──→  admin_static_knowledge.json
unanswered_queries.json  ──[reviewed by]──→  Admin adds to intents.json
```

---

## 12. UML Diagrams (Explained in Text)

### Use Case Diagram

**Actors**: Student, Admin

**Student Use Cases**:
- View College Homepage
- Open Student Helpdesk
- Send Query to Chatbot
- Receive Chatbot Response

**Admin Use Cases**:
- Login to Admin Panel
- View Dashboard
- Manage FAQs (Add / Delete Intent)
- Upload Document
- Toggle Document Status (Active/Inactive)
- Delete Document
- View Analytics & Knowledge Gaps
- Logout

**Relationships**:
- Student → "Send Query" → extends → "Receive Response"
- Admin → "Manage FAQs" → includes → "Login"
- Admin → "View Analytics" → includes → "Login"

---

### Class Diagram

**Class: ChatbotEngine**
- Attributes: `words`, `classes`, `model`, `intents`, `embedding_model`, `intent_embeddings`, `CONFIDENCE_THRESHOLD`
- Methods: `normalize_synonyms()`, `predict_class()`, `get_faq_response()`, `get_embedding_response()`, `search_admin_static_knowledge()`, `chatbot_response()`

**Class: DocumentIngestion**
- Attributes: None (stateless module)
- Methods: `extract_text_from_txt()`, `extract_text_from_pdf()`, `extract_text_from_docx()`, `clean_text()`, `chunk_text()`, `process_document()`, `save_document_data()`, `load_knowledge_base()`, `search_documents()`, `update_document_status()`, `delete_document()`

**Class: NLPPreprocessor**
- Attributes: `lemmatizer`, `USE_NLTK`
- Methods: `clean_up_sentence()`, `bag_of_words()`

**Class: FlaskApp**
- Attributes: `app`, `ADMIN_USERNAME`, `ADMIN_PASSWORD`, `DATA_DIR`
- Methods: `home()`, `helpdesk()`, `get_bot_response()`, `admin_login()`, `admin_logout()`, `admin_dashboard()`, `admin_analytics()`, `admin_knowledge()`, `admin_add_faq()`, `admin_delete_faq()`, `upload_document()`, `compute_analytics()`

**Relationships**:
- `FlaskApp` uses `ChatbotEngine` (calls `chatbot_response()`)
- `ChatbotEngine` uses `NLPPreprocessor` (calls `bag_of_words()`, `clean_up_sentence()`)
- `ChatbotEngine` uses `DocumentIngestion` (calls `search_documents()`)
- `FlaskApp` uses `DocumentIngestion` (calls `process_document()`, `save_document_data()`)

---

### Sequence Diagram: Student Query Flow

```
Student → Browser: Types and sends query
Browser → Flask (/get-response): POST {message: "..."}
Flask → ChatbotEngine: chatbot_response(msg)
ChatbotEngine → NLPPreprocessor: bag_of_words(msg, words)
NLPPreprocessor → ChatbotEngine: BoW vector
ChatbotEngine → MLPModel: predict_proba([bow])
MLPModel → ChatbotEngine: probability array
ChatbotEngine → [if confidence >= 0.65]: return FAQ response
ChatbotEngine → [else] SentenceTransformer: encode(msg)
SentenceTransformer → ChatbotEngine: cosine similarities
ChatbotEngine → [if similarity >= 0.5]: return embedding response
ChatbotEngine → [else] DocumentIngestion: search_documents(msg)
DocumentIngestion → ChatbotEngine: scored chunks
ChatbotEngine → [if score >= 2]: return document response
ChatbotEngine → [else] LoggingUtils: log_unanswered_query()
ChatbotEngine → Flask: fallback response string
Flask → Browser: JSON {response: "..."}
Browser → Student: Displays response
```

---

### Activity Diagram: Admin Document Upload

```
[Start]
    ↓
Admin clicks "Upload Document"
    ↓
Selects file + category
    ↓
POST to /upload_document
    ↓
[Is file present?]
   No ↓           Yes ↓
Flash error    Read file content (PDF/DOCX/TXT)
   ↓                   ↓
[End]       [Is content extractable?]
              No ↓           Yes ↓
           Flash error    Clean Text (remove extra whitespace)
              ↓                   ↓
           [End]          Chunk Text (~500 chars per chunk)
                                  ↓
                          Generate UUID + Timestamp
                                  ↓
                          Save metadata to admin_static_metadata.json
                                  ↓
                          Save chunks to admin_static_knowledge.json
                                  ↓
                          Flash success message
                                  ↓
                               [End]
```

---

## 13. User Interface Description

### Page 1: College Homepage (`/`)
- **Template**: `main.html`
- **Description**: The public landing page of Pallavi Engineering College
- **Sections**:
  - Navigation bar with logo, Home, Student Helpdesk, Admin Login
  - Hero section with college tagline
  - About the College section
  - Stats grid: Affiliation, Accreditations, Location
  - Campus Facilities image gallery (Auditorium, Digital Library, Robotics Lab)
  - Footer with address and copyright

### Page 2: Student Helpdesk (`/helpdesk`)
- **Template**: `chatbot.html`
- **Description**: The student-facing chatbot interface
- **Elements**:
  - Chat message window showing conversation history
  - Color-coded bubbles: student (right, primary color), bot (left, neutral)
  - Text input field + Send button
  - JavaScript handles input → AJAX → response display without page reload

### Page 3: Admin Login (`/admin/login`)
- **Template**: `admin/login.html`
- **Description**: Secure login form for admin access
- **Elements**: Username and password fields, Login button, error flash messages

### Page 4: Admin Dashboard (`/admin/dashboard`)
- **Template**: `admin/dashboard.html`
- **Description**: Admin home screen with quick navigation cards
- **Links to**: FAQ Management, Document Upload, Analytics, Logout

### Page 5: Knowledge Management (`/admin/knowledge`)
- **Template**: `admin/knowledge.html`
- **Sections**:
  - **FAQ Tab**: Table of all intent tags with patterns preview; Add FAQ form (tag, patterns, responses)
  - **Document Tab**: Upload form (file chooser + category dropdown); Table of uploaded docs with status, chunks count, toggle/delete actions

### Page 6: Analytics Dashboard (`/admin/analytics`)
- **Template**: `admin/analytics.html`
- **Sections**:
  - **Stat Banner**: Total Queries, Success Rate, FAQ Answers, Unresolved (4-column grid)
  - **Knowledge Gaps Table**: Frequent unanswered queries with frequency count
  - **Improvement Insights**: Conditional alerts if success rate < 80% or unanswered queries exist
  - **Source Distribution**: Counts by FAQ / Document / Fallback

---

## 14. Features of the Project

1. ✅ **Two-Layer Hybrid Chatbot**: MLP + Document fallback for maximum coverage
2. ✅ **Semantic Search**: Sentence Transformer cosine similarity handles paraphrased queries
3. ✅ **Synonym Normalization**: Preprocessing layer maps vocabulary variants
4. ✅ **Natural Language Understanding**: NLTK tokenization + lemmatization
5. ✅ **Multi-Format Document Upload**: Supports PDF, DOCX, and TXT upload
6. ✅ **Dynamic Document Management**: Admin can activate/deactivate documents without deletion
7. ✅ **FAQ CRUD**: Admin can add and delete FAQ intents through the web UI
8. ✅ **Unanswered Query Logging**: All failed queries are timestamped and stored
9. ✅ **Analytics Dashboard**: Success rate, source distribution, knowledge gap identification
10. ✅ **Session-Based Admin Authentication**: Protected admin routes with login/logout
11. ✅ **Document Category Classification**: Documents tagged by topic (Fees, Exams, etc.)
12. ✅ **Text Chunking**: Smart sentence-boundary splitting for retrieval quality
13. ✅ **Scanned PDF Detection**: Warns admin if uploaded PDF has no extractable text
14. ✅ **Responsive Web UI**: Desktop-friendly layout with shared navigation and footer
15. ✅ **Real-Time Chat**: JavaScript AJAX for instant response without page reload

---

## 15. Advantages

### Technical Advantages
- **No GPU Required**: MLPClassifier runs on CPU, making it deployable on any standard server
- **Modular Architecture**: Each component (NLP, document search, analytics) is independently replaceable
- **No External Database Server**: JSON file-based storage makes setup trivial
- **Graceful Degradation**: System falls back gracefully across three layers rather than failing
- **Semantic Robustness**: Sentence Transformers handle vocabulary variation not covered by BoW

### Practical Advantages
- **Zero Training Required from Admin**: Admins improve the bot through simple web forms
- **Instant Deployment**: Runs with `python app.py`; no cloud infra required
- **Scalable Knowledge Base**: More FAQs and documents can be added without redeployment
- **Transparent Performance**: Analytics show exactly where the system succeeds and fails
- **Student-Friendly Interface**: Clean, minimal chat UI reduces friction

---

## 16. Limitations

1. **Static Model**: Adding new FAQs to `intents.json` does NOT automatically retrain the model — the admin must manually run `train_model.py` after adding new intents
2. **Scanned PDFs Not Supported**: Image-based PDFs cannot be parsed (no OCR integration)
3. **Keyword-Based Document Search**: Layer 2 uses keyword overlap, not semantic search; it may miss relevant chunks with different vocabulary
4. **Hardcoded Admin Credentials**: Credentials are currently stored in `app.py` — not suitable for production without a user database
5. **Single Admin User**: No multi-user admin system; all admins share one account
6. **No Conversation History Persistence**: Chat sessions are lost on page refresh (in-browser memory only)
7. **File-Based Storage Limits**: JSON files are not optimized for large-scale query logs (no indexing)
8. **English Only**: The NLP pipeline is optimized for English queries only
9. **5MB File Size Limit**: Large institutional documents may need to be split before upload

---

## 17. Future Enhancements

### Short-Term Improvements
- **Automatic Model Retraining**: Trigger model training automatically when new FAQs are added via admin panel
- **Password Hashing**: Store admin credentials using bcrypt/Argon2 in a proper user table
- **Multi-Admin Support**: Role-based access with separate admin accounts
- **OCR Integration**: Use `tesseract-ocr` or `EasyOCR` to extract text from scanned PDFs
- **Document Semantic Search**: Replace keyword search with vector embeddings for Layer 2 as well

### Medium-Term Improvements
- **Persistent Chat History**: Store per-session conversations in a database (SQLite/PostgreSQL)
- **Multi-Language Support**: Add Telugu/Hindi intent sets for regional accessibility
- **WhatsApp/Telegram Integration**: Deploy chatbot on messaging platforms
- **Email/SMS Alerts**: Notify admin when unanswered query count crosses a threshold
- **REST API Layer**: Expose chatbot as a REST API for integration with college mobile apps

### Long-Term Scalability
- **Vector Database (Pinecone / ChromaDB)**: Replace JSON search with a proper vector store for thousands of document chunks
- **LLM Integration**: Use a hosted LLM (e.g., Gemini, GPT-4) for free-form generation when FAQ and document search fail
- **Real-Time Model Fine-Tuning**: Allow the system to learn from admin-resolved queries automatically
- **Multi-College Deployment**: Containerize with Docker and deploy across multiple institutions on a shared cloud platform
- **Voice Interface**: Add speech-to-text for accessibility support

---

## 18. Testing

### Types of Testing Used

| Type | Description |
|---|---|
| **Unit Testing** | Individual functions tested in isolation (`test_suite.py`) |
| **Integration Testing** | Flask routes tested with HTTP requests |
| **Functional Testing** | End-to-end chatbot response flow validated |
| **Manual Testing** | UI interaction tested in the browser |

### Test Cases (Examples)

| # | Test Case | Input | Expected Output | Pass/Fail |
|---|---|---|---|---|
| 1 | Greeting intent | "Hello" | "Greetings! I am the College Helpdesk Assistant..." | Pass |
| 2 | Admissions query | "How do I apply for admission?" | Admission process details | Pass |
| 3 | Library timing | "When does the library close?" | "8:00 AM to 6:00 PM on working days..." | Pass |
| 4 | Synonym normalization | "How do I register?" | Admission response (register → apply) | Pass |
| 5 | Low confidence fallback | "Blah blah blah" | Default fallback message | Pass |
| 6 | Document search | "fee deadline" (doc uploaded) | "Based on fee_doc.pdf: ..." | Pass |
| 7 | Admin login valid | Username: Pallavi, Password: Pallavi@2026 | Redirect to dashboard | Pass |
| 8 | Admin login invalid | Wrong credentials | "Invalid credentials" flash error | Pass |
| 9 | FAQ add | Valid tag + patterns + responses | Intent added to intents.json | Pass |
| 10 | Document upload PDF | Valid PDF upload | "Success! Processed and indexed." | Pass |
| 11 | Document upload scanned PDF | Scanned image PDF | Error: "No extractable text" | Pass |
| 12 | Analytics computation | Query log with 10 entries | Correct counts displayed | Pass |

---

## 19. Results

### What the System Produces

**For Students**:
- Instant, natural language responses to over 40+ college-specific FAQ categories
- Contextual answers drawn from admin-uploaded institutional documents
- A graceful fallback message with a promise of admin review if knowledge is unavailable

**For Admins**:
- A real-time analytics dashboard showing:
  - Total queries handled since deployment
  - Success rate percentage (FAQ + document answers / total queries)
  - Breakdown: FAQ-answered, Document-answered, Unanswered
  - Top 10 knowledge gaps (most frequently unanswered queries)
  - Recent 10 queries log

**System Performance**:
- MLP confidence threshold of 0.65 ensures high-precision FAQ responses
- Sentence Transformer semantic similarity at 0.5 catches paraphrased queries
- Document search with min-score 2 keyword matches ensures relevance filtering

---

## 20. Conclusion

The AI-Powered College Helpdesk Chatbot successfully addresses the critical need for an intelligent, always-available student assistance system at Pallavi Engineering College. By combining a trained neural network classifier with semantic sentence embeddings and a dynamic document retrieval layer, the project achieves robust natural language understanding without requiring enterprise infrastructure or cloud services.

The admin-facing management panel empowers non-technical college staff to continuously expand the system's knowledge through a simple, intuitive interface — ensuring the chatbot improves organically over time as new FAQs are added and documents are uploaded. The integrated analytics engine creates a data-driven feedback loop, transforming every failed query into an actionable improvement opportunity.

This project demonstrates the practical power of combining classical machine learning (MLP classifiers, Bag-of-Words), modern NLP (Sentence Transformers, lemmatization), and traditional web development (Flask, REST APIs) to solve a real institutional problem. It lays a strong foundation for future enhancements such as LLM integration, voice interfaces, and multi-college scalability — making it both an academically rigorous and practically impactful contribution to the institution.

---

## 21. References

### Libraries and Frameworks
1. Flask Documentation — https://flask.palletsprojects.com/
2. scikit-learn MLPClassifier — https://scikit-learn.org/stable/modules/generated/sklearn.neural_network.MLPClassifier.html
3. NLTK (Natural Language Toolkit) — https://www.nltk.org/
4. Sentence Transformers (all-MiniLM-L6-v2) — https://www.sbert.net/
5. pdfplumber — https://github.com/jsvine/pdfplumber
6. python-docx — https://python-docx.readthedocs.io/
7. NumPy — https://numpy.org/
8. Werkzeug — https://werkzeug.palletsprojects.com/

### Concepts and Methods
9. Bag-of-Words Model — Manning, C., Schütze, H. (1999). *Foundations of Statistical Natural Language Processing*. MIT Press.
10. Multi-Layer Perceptron — Rumelhart, D. E., Hinton, G. E., & Williams, R. J. (1986). *Learning representations by back-propagating errors*. Nature, 323, 533–536.
11. Sentence-BERT — Reimers, N., & Gurevych, I. (2019). *Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks*. EMNLP 2019. https://arxiv.org/abs/1908.10084
12. WordNet Lemmatizer — Miller, G. A. (1995). *WordNet: A lexical database for English*. Communications of the ACM, 38(11), 39–41.

### Tools and APIs
13. Python 3.x — https://www.python.org/
14. Jinja2 Template Engine — https://jinja.palletsprojects.com/
15. TMDB API *(referenced in related project)* — https://www.themoviedb.org/documentation/api

### Institutional References
16. Pallavi Engineering College Official Website — https://www.pallaviengineeringcollege.ac.in
17. JNTUH Academic Regulations — https://jntuh.ac.in
18. AICTE Regulations — https://www.aicte-india.org

---
*Documentation generated for: AI-Powered College Helpdesk Chatbot | Pallavi Engineering College | Academic Year 2025–2026*
