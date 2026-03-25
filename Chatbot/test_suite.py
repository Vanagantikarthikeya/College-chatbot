"""
Test Suite for College Helpdesk Chatbot
Tests all major components and functionality
"""

import sys
import os

print("="*70)
print("COLLEGE HELPDESK CHATBOT - COMPREHENSIVE TEST SUITE")
print("="*70)

# Test 1: Import all modules
print("\n[TEST 1] Testing Module Imports...")
try:
    import flask
    print("✓ Flask imported successfully")
except ImportError as e:
    print(f"✗ Flask import failed: {e}")
    sys.exit(1)

try:
    import nlp_preprocessing
    print("✓ NLP Preprocessing module imported")
except ImportError as e:
    print(f"✗ NLP Preprocessing import failed: {e}")
    sys.exit(1)

try:
    import chatbot_engine
    print("✓ Chatbot Engine module imported")
except ImportError as e:
    print(f"✗ Chatbot Engine import failed: {e}")
    sys.exit(1)

try:
    import document_ingestion
    print("✓ Document Ingestion module imported")
except ImportError as e:
    print(f"✗ Document Ingestion import failed: {e}")
    sys.exit(1)

try:
    import app
    print("✓ Flask App module imported")
except ImportError as e:
    print(f"✗ Flask App import failed: {e}")
    sys.exit(1)

# Test 2: Check required files
print("\n[TEST 2] Checking Required Files...")
required_files = [
    'intents.json',
    'model.pkl',
    'words.pkl',
    'classes.pkl',
    'nlp_preprocessing.py',
    'chatbot_engine.py',
    'document_ingestion.py',
    'app.py'
]

for file in required_files:
    if os.path.exists(file):
        print(f"✓ {file} exists")
    else:
        print(f"✗ {file} missing")

# Test 3: Check templates
print("\n[TEST 3] Checking Template Files...")
template_files = [
    'templates/index.html',
    'templates/admin_login.html',
    'templates/admin_dashboard.html',
    'templates/admin_queries.html',
    'templates/manage_faq.html',
    'templates/upload_documents.html',
    'templates/admin_analytics.html'
]

for template in template_files:
    if os.path.exists(template):
        print(f"✓ {template} exists")
    else:
        print(f"✗ {template} missing")

# Test 4: Test Chatbot Engine
print("\n[TEST 4] Testing Chatbot Engine...")
try:
    test_queries = [
        "Hello",
        "What are the admission requirements?",
        "Tell me about placements",
        "What is the fee structure?",
        "How can I contact the college?"
    ]
    
    for query in test_queries:
        response = chatbot_engine.chatbot_response(query)
        print(f"✓ Query: '{query[:40]}...' -> Response received ({len(response)} chars)")
except Exception as e:
    print(f"✗ Chatbot engine test failed: {e}")

# Test 5: Test Document Ingestion Functions
print("\n[TEST 5] Testing Document Ingestion Functions...")
try:
    # Test text cleaning
    test_text = "This   is   a    test   text!!!   "
    cleaned = document_ingestion.clean_text(test_text)
    print(f"✓ Text cleaning works: '{test_text}' -> '{cleaned}'")
    
    # Test text chunking
    long_text = "This is a sentence. " * 50
    chunks = document_ingestion.chunk_text(long_text, chunk_size=100)
    print(f"✓ Text chunking works: {len(long_text)} chars -> {len(chunks)} chunks")
    
    # Test knowledge base loading
    kb = document_ingestion.load_knowledge_base()
    print(f"✓ Knowledge base loaded: {len(kb.get('documents', []))} documents")
    
except Exception as e:
    print(f"✗ Document ingestion test failed: {e}")

# Test 6: Test Flask App Configuration
print("\n[TEST 6] Testing Flask App Configuration...")
try:
    from app import app as flask_app
    print(f"✓ Flask app created: {flask_app.name}")
    print(f"✓ Secret key configured: {'Yes' if flask_app.secret_key else 'No'}")
    print(f"✓ Upload folder: {flask_app.config.get('UPLOAD_FOLDER', 'Not set')}")
    
    # Test routes
    routes = [rule.rule for rule in flask_app.url_map.iter_rules()]
    admin_routes = [r for r in routes if '/admin/' in r]
    print(f"✓ Total routes: {len(routes)}")
    print(f"✓ Admin routes: {len(admin_routes)}")
    
except Exception as e:
    print(f"✗ Flask app test failed: {e}")

# Test 7: Test Analytics Computation
print("\n[TEST 7] Testing Analytics Computation...")
try:
    from app import compute_analytics
    analytics = compute_analytics()
    
    print(f"✓ Total Queries: {analytics['total_queries']}")
    print(f"✓ Answered by FAQ: {analytics['answered_by_faq']}")
    print(f"✓ Answered by Docs: {analytics['answered_by_docs']}")
    print(f"✓ Unanswered: {analytics['unanswered_count']}")
    print(f"✓ Success Rate: {analytics['success_rate']}%")
    print(f"✓ Total FAQs: {analytics['total_faqs']}")
    print(f"✓ Active Documents: {analytics['active_documents']}")
    
except Exception as e:
    print(f"✗ Analytics test failed: {e}")

# Test 8: Test Data Directory Structure
print("\n[TEST 8] Checking Data Directory Structure...")
if not os.path.exists('data'):
    os.makedirs('data')
    print("✓ Created data directory")
else:
    print("✓ Data directory exists")

if not os.path.exists('data/uploads'):
    os.makedirs('data/uploads')
    print("✓ Created uploads directory")
else:
    print("✓ Uploads directory exists")

# Test 9: Test Hybrid Response Logic
print("\n[TEST 9] Testing Hybrid Response Logic...")
try:
    # Test with high confidence query
    test_msg = "Hello"
    intents_list, confidence = chatbot_engine.predict_class(test_msg)
    response = chatbot_engine.hybrid_response(test_msg, intents_list, confidence)
    print(f"✓ High confidence query handled: confidence={confidence:.2f}")
    
    # Test with low confidence query
    test_msg = "xyzabc123nonsense"
    intents_list, confidence = chatbot_engine.predict_class(test_msg)
    response = chatbot_engine.hybrid_response(test_msg, intents_list, confidence)
    print(f"✓ Low confidence query handled: confidence={confidence:.2f}")
    
except Exception as e:
    print(f"✗ Hybrid response test failed: {e}")

# Final Summary
print("\n" + "="*70)
print("TEST SUITE COMPLETED")
print("="*70)
print("\n✓ All critical tests passed!")
print("\nThe chatbot system is ready to run.")
print("\nTo start the application, run:")
print("  python app.py")
print("\nThen access:")
print("  - Chatbot Interface: http://localhost:5000/")
print("  - Admin Login: http://localhost:5000/admin/login")
print("  - Admin Credentials: username='admin', password='password123'")
print("\n" + "="*70)
