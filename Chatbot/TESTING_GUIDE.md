# COLLEGE HELPDESK CHATBOT - TESTING GUIDE

## ✅ APPLICATION STATUS: RUNNING

The Flask server is currently running on: **http://localhost:5000/**

---

## 🧪 COMPREHENSIVE TEST CASES

### TEST 1: Chatbot Interface (Public User)
**URL:** http://localhost:5000/

**Test Cases:**
1. **Basic Greeting**
   - Input: "Hello"
   - Expected: Greeting response from FAQ

2. **Admission Queries**
   - Input: "How can I apply for admission?"
   - Expected: Admission information from FAQ

3. **Placement Queries**
   - Input: "Which companies visit for placements?"
   - Expected: Placement information from FAQ

4. **Fee Structure**
   - Input: "What is the fee structure?"
   - Expected: Fee details from FAQ

5. **Low Confidence Query (Document Fallback)**
   - Input: "Tell me about hostel facilities"
   - Expected: If FAQ exists, return FAQ. Otherwise, search documents or fallback

6. **Unknown Query (Fallback Logging)**
   - Input: "What is the weather today?"
   - Expected: Fallback message + query logged for admin review

---

### TEST 2: Admin Login
**URL:** http://localhost:5000/admin/login

**Credentials:**
- Username: `admin`
- Password: `password123`

**Test Cases:**
1. **Valid Login**
   - Enter correct credentials
   - Expected: Redirect to Admin Dashboard

2. **Invalid Login**
   - Enter wrong password
   - Expected: Error message displayed

---

### TEST 3: Admin Dashboard
**URL:** http://localhost:5000/admin/dashboard

**Test Cases:**
1. **Navigation Menu**
   - Verify all links present:
     - Home
     - Unanswered Queries
     - Manage FAQs
     - Upload Documents
     - Analytics
     - Logout

2. **Quick Access Buttons**
   - Click "View Unanswered Queries"
   - Click "Manage FAQs"
   - Expected: Navigate to respective pages

---

### TEST 4: Unanswered Queries Management
**URL:** http://localhost:5000/admin/queries

**Test Cases:**
1. **View Unanswered Queries**
   - Expected: Table showing all logged queries with:
     - Timestamp
     - User Query
     - Confidence Score
     - Status
     - ID

2. **Check Query Details**
   - Verify queries are sorted (newest first)
   - Check if fallback queries are logged

---

### TEST 5: FAQ Management
**URL:** http://localhost:5000/admin/manage-faq

**Test Cases:**
1. **Add New FAQ**
   - Intent Tag: `test_scholarship`
   - Patterns (one per line):
     ```
     How to apply for scholarship?
     Scholarship eligibility criteria
     Types of scholarships available
     ```
   - Responses (one per line):
     ```
     Scholarships are available for meritorious students. Please contact the administration.
     You can apply for scholarships through the official portal during admission.
     ```
   - Expected: Success message + FAQ added to list

2. **Edit Existing FAQ**
   - Select an intent from dropdown
   - Add new patterns or responses
   - Expected: FAQ updated successfully

3. **Delete FAQ**
   - Select an intent
   - Confirm deletion
   - Expected: FAQ removed from list

4. **View All FAQs**
   - Expected: Table showing all intents with pattern and response counts

---

### TEST 6: Document Upload & Management
**URL:** http://localhost:5000/admin/upload-documents

**Test Cases:**
1. **Upload TXT Document**
   - Create a test file: `test_document.txt` with content:
     ```
     The college library is open from 8 AM to 8 PM on weekdays.
     Students can borrow up to 5 books at a time.
     Digital resources are available 24/7 through the online portal.
     ```
   - Category: "Library"
   - Expected: Document uploaded, processed, and chunks created

2. **Upload PDF Document** (if available)
   - Upload a PDF file
   - Category: "Admissions"
   - Expected: Text extracted and stored

3. **Upload DOCX Document** (if available)
   - Upload a DOCX file
   - Category: "Exams"
   - Expected: Text extracted and stored

4. **Toggle Document Status**
   - Click "Deactivate" on an active document
   - Expected: Status changes to "inactive"
   - Click "Activate" again
   - Expected: Status changes to "active"

5. **View Document List**
   - Expected: Table showing:
     - Filename
     - Category
     - Upload Date
     - Chunks Count
     - Status
     - Action buttons

---

### TEST 7: Analytics & Insights
**URL:** http://localhost:5000/admin/analytics

**Test Cases:**
1. **Key Performance Metrics**
   - Verify all 8 metric cards display:
     - Total Queries
     - Answered (FAQ)
     - Answered (Documents)
     - Unanswered
     - Resolved Queries
     - Total FAQs
     - Active Documents
     - Success Rate

2. **Most Frequent Unanswered Queries**
   - Expected: Table showing repeated queries with frequency count

3. **Recent Query Activity**
   - Expected: Last 10 queries with timestamp, confidence, source, status

4. **Knowledge Base Growth**
   - Expected: Table showing:
     - Total FAQ Intents
     - Total Uploaded Documents
     - Total Document Chunks
     - Queries Resolved by Admin

5. **Improvement Suggestions**
   - Expected: Automated recommendations based on performance

---

### TEST 8: Hybrid Answering System (Integration Test)

**Scenario 1: FAQ Priority**
1. Ask chatbot: "Hello"
2. Expected: FAQ response (high confidence)
3. Check: No query logged (successful FAQ match)

**Scenario 2: Document Fallback**
1. Upload a document about "Sports Facilities"
2. Ask chatbot: "Tell me about sports facilities"
3. Expected: 
   - If FAQ exists: FAQ response
   - If no FAQ: Document-based response with "Based on [document]:"
   - Query logged with source="document"

**Scenario 3: Complete Fallback**
1. Ask chatbot: "What is quantum physics?"
2. Expected:
   - Fallback message
   - Query logged with source="none" and status="unanswered"
3. Verify in Admin → Unanswered Queries

**Scenario 4: FAQ Addition After Fallback**
1. Check unanswered queries for a repeated question
2. Add FAQ for that question
3. Ask the same question again
4. Expected: FAQ response (no longer fallback)

---

### TEST 9: End-to-End Workflow

**Complete Admin Workflow:**
1. Login as admin
2. Check analytics (baseline metrics)
3. View unanswered queries
4. Add FAQ for most frequent query
5. Upload a document
6. Check analytics again (verify improvement)
7. Test chatbot with new FAQ
8. Verify query is now answered
9. Logout

---

## 🎯 EXPECTED RESULTS SUMMARY

### ✅ All Tests Should Pass If:
- Flask server is running without errors
- All templates render correctly
- Admin authentication works
- FAQ CRUD operations function
- Document upload and processing work
- Analytics compute correctly
- Chatbot responds using FAQ → Document → Fallback priority
- Queries are logged appropriately

### 📊 Success Metrics:
- **Chatbot Response Rate:** >70% (FAQ + Documents)
- **Admin Dashboard:** All pages accessible
- **FAQ Management:** Add/Edit/Delete functional
- **Document Processing:** TXT/PDF/DOCX supported
- **Analytics:** Real-time metrics display
- **Hybrid System:** Correct priority routing

---

## 🚀 HOW TO RUN THE APPLICATION

1. **Start the Server:**
   ```bash
   python app.py
   ```

2. **Access the Application:**
   - Chatbot: http://localhost:5000/
   - Admin Login: http://localhost:5000/admin/login

3. **Admin Credentials:**
   - Username: `admin`
   - Password: `password123`

4. **Stop the Server:**
   - Press `Ctrl+C` in the terminal

---

## 📝 TESTING NOTES

- All tests have been verified in the test suite (`test_suite.py`)
- Flask server is currently running and ready for manual testing
- Dependencies installed: Flask, PyPDF2, python-docx, scikit-learn, NLTK
- All templates created and verified
- Hybrid answering system implemented and tested

---

## 🔧 TROUBLESHOOTING

**Issue:** Server won't start
- **Solution:** Check if port 5000 is already in use
- **Command:** `netstat -ano | findstr :5000`

**Issue:** Document upload fails
- **Solution:** Verify PyPDF2 and python-docx are installed
- **Command:** `pip install PyPDF2 python-docx`

**Issue:** Analytics shows 0 queries
- **Solution:** Use the chatbot first to generate query logs

**Issue:** FAQ not working
- **Solution:** Verify intents.json is valid JSON and model files exist

---

## ✨ FEATURES IMPLEMENTED

1. ✅ ML-based Intent Classification
2. ✅ Intelligent Fallback Logging
3. ✅ Admin Dashboard with Authentication
4. ✅ Dynamic FAQ Management (Add/Edit/Delete)
5. ✅ Document Upload & Processing (PDF/DOCX/TXT)
6. ✅ Hybrid Retrieval Engine (FAQ → Documents → Fallback)
7. ✅ Analytics & Insights Dashboard
8. ✅ Query Frequency Analysis
9. ✅ Knowledge Base Growth Tracking
10. ✅ Automated Improvement Suggestions

---

**STATUS: ALL SYSTEMS OPERATIONAL ✅**
**SERVER: RUNNING ON http://localhost:5000/ 🚀**
