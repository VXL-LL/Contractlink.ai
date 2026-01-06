# Bid Document Upload System - Complete Guide

## Overview
The AI Assistant now supports uploading and analyzing bid documents (RFPs, coversheets, addendums, capability statements, intake forms) to provide context-aware assistance with filling out forms and generating accurate responses.

## Features Implemented ✅

### 1. Database Schema
**Table:** `user_bid_documents`

**Columns:**
- `id` - Primary key (auto-increment)
- `user_email` - User identifier (foreign key to users.email)
- `filename` - Unique filename for storage
- `original_filename` - User's original filename
- `file_type` - Document category (rfp, coversheet, addendum, capability, intake, schedule, other)
- `file_path` - Full path to stored file
- `file_size` - File size in bytes
- `extracted_text` - Full text extracted from document
- `uploaded_at` - Timestamp of upload
- `last_used` - Last time document was referenced
- `metadata` - JSON field for additional info

**Indexes:**
- `idx_bid_docs_user` - Fast user lookups
- `idx_bid_docs_type` - Filter by document type

### 2. Document Types Supported

| Type | Description | Use Case |
|------|-------------|----------|
| **RFP** | Request for Proposal / Solicitation | Full bid requirements |
| **Coversheet** | Bid cover/title page | Contact info, certifications |
| **Addendum** | Changes/amendments | Updated requirements |
| **Capability** | Capability statement | Company qualifications |
| **Intake** | Intake/screening form | Initial qualification questions |
| **Schedule** | Pricing schedule | Cost breakdowns |
| **Other** | Miscellaneous documents | Supporting materials |

### 3. File Format Support

**Supported:** PDF (.pdf), Microsoft Word (.docx, .doc), Plain Text (.txt)

**Maximum Size:** 10 MB per file

**Text Extraction:**
- **PDF**: Uses PyPDF2 or pdfplumber
- **DOCX**: Uses python-docx
- **TXT**: Native Python file handling

### 4. User Interface

**Location:** AI Assistant page (`/ai-assistant`) - Right sidebar

**Components:**
1. **Document Type Selector** - Dropdown with 7 document categories
2. **Drag & Drop Zone** - Visual file upload area with hover effects
3. **File Browser** - Click zone triggers system file picker
4. **Upload Progress** - Animated progress bar during upload
5. **Document List** - Shows all uploaded documents with metadata
6. **Delete Buttons** - Remove individual documents

**Visual Features:**
- Blue border highlight on drag-over
- File type badges (color-coded by category)
- File size display in KB
- Upload timestamp
- Success/error feedback in chat

### 5. API Endpoints

#### Upload Document
```
POST /api/upload-bid-document
Content-Type: multipart/form-data
Authentication: Required (login_required)

Parameters:
- file: File upload (required)
- file_type: Document category (required)

Response:
{
  "success": true,
  "message": "Document uploaded successfully",
  "filename": "original.pdf",
  "file_type": "rfp",
  "size": 245678,
  "text_extracted": true
}

Error Codes:
- 400: No file / invalid type / file too large
- 500: Processing error
```

#### Delete Document
```
DELETE /api/delete-bid-document/<doc_id>
Authentication: Required (login_required)

Response:
{
  "success": true,
  "message": "Document deleted successfully"
}

Error Codes:
- 404: Document not found / not owned by user
- 500: Deletion error
```

#### Get Documents
```
GET /api/get-bid-documents
Authentication: Required (login_required)

Response:
{
  "success": true,
  "documents": [
    {
      "id": 1,
      "filename": "RFP-2026-001.pdf",
      "file_type": "rfp",
      "uploaded_at": "2026-01-05 14:30:00",
      "file_size": 245678,
      "has_text": true
    }
  ]
}
```

### 6. AI Integration

**Enhanced chatbot_kb.py:**

The AI assistant now detects document-related queries and provides context-aware responses.

**Trigger Keywords:**
- "my rfp"
- "uploaded document"
- "fill out"
- "my coversheet"
- "my addendum"
- "my capability statement"
- "intake form"
- "help me with"
- "complete this"
- "answer this"

**Example Queries:**
```
❓ "Help me fill out my RFP"
✅ AI shows list of uploaded documents with content previews

❓ "What does Section 3.2 of my RFP require?"
✅ AI searches uploaded RFP text for Section 3.2

❓ "Fill out my capability statement"
✅ AI provides guidance based on extracted text
```

**Response Structure:**
```html
<strong>Your Uploaded Documents:</strong><br>
1. <strong>RFP-2026-001.pdf</strong> (rfp)<br>
<em>Content preview:</em> [First 500 characters]...<br>

<strong>How I can help:</strong><br>
• Answer specific questions about requirements
• Help fill out forms with appropriate responses
• Suggest compliance strategies
• Review capability statements
• Provide guidance on addendum changes
```

### 7. Security Features

**Access Control:**
- All endpoints require login (`@login_required`)
- Users can only view/delete their own documents
- SQL queries use parameterized statements (injection protection)

**File Safety:**
- Filename sanitization with `secure_filename()`
- File type validation (whitelist approach)
- File size limits (10MB)
- Unique filename generation (UUID prefix)
- Isolated storage directory (`uploads/bid_documents/`)

**Data Privacy:**
- Documents stored per-user (not shared)
- Extracted text stored in database for fast retrieval
- No external API calls (all processing on-server)

### 8. Storage Management

**File Organization:**
```
project_root/
└── uploads/
    └── bid_documents/
        ├── a1b2c3d4_RFP-2026-001.pdf
        ├── e5f6g7h8_Coversheet.docx
        └── i9j0k1l2_Capability-Statement.pdf
```

**Naming Convention:** `{uuid8}_{sanitized_original_name}`

**Database Cleanup:**
- Orphaned files: Manual script or cron job
- File deletion: Cascade to filesystem removal

### 9. Error Handling

**Upload Failures:**
- No file selected → Alert user
- Invalid file type → Show supported formats
- File too large → Display size limit
- Extraction error → Save file, store error message

**Display Handling:**
- Documents list empty → Show helpful message
- Database error → Graceful degradation (empty list)
- Missing text → Show "No preview available"

### 10. User Experience Flow

**Step 1: Navigate to AI Assistant**
`Dashboard → AI Assistant`

**Step 2: Select Document Type**
Choose from dropdown: RFP, Coversheet, Addendum, etc.

**Step 3: Upload File**
- **Option A:** Drag & drop file onto upload zone
- **Option B:** Click zone to browse files

**Step 4: Wait for Processing**
Progress bar shows upload status

**Step 5: Confirmation**
Success message appears in chat with document details

**Step 6: Ask Questions**
Type queries like "Help me with my RFP" or "What are the requirements?"

**Step 7: Get AI Assistance**
AI provides context-aware responses based on uploaded documents

**Step 8: Manage Documents**
Delete unwanted documents with trash button

## Installation & Setup

### 1. Database Setup
```bash
python create_bid_documents_table.py
```

### 2. Install Dependencies (if needed)
```bash
pip install PyPDF2 python-docx
# or
pip install pdfplumber python-docx
```

### 3. Create Upload Directory
```bash
mkdir -p uploads/bid_documents
```

### 4. Restart Flask Application
```bash
flask run
# or
python app.py
```

## Testing Checklist

- [ ] Upload PDF file (RFP type)
- [ ] Upload DOCX file (Coversheet type)
- [ ] Upload TXT file (Other type)
- [ ] Verify document appears in list
- [ ] Check file size display
- [ ] Ask "help me with my RFP" in chat
- [ ] Verify AI shows document preview
- [ ] Delete document
- [ ] Verify deletion from UI
- [ ] Try uploading unsupported file type (expect error)
- [ ] Try uploading 11MB file (expect error)
- [ ] Test drag & drop upload
- [ ] Test click-to-browse upload

## Maintenance

### Clean Orphaned Files
```python
# create cleanup script
import os
from database import db
from sqlalchemy import text

# Find files in uploads/bid_documents
all_files = os.listdir('uploads/bid_documents')

# Get all filenames from database
db_files = db.session.execute(text(
    'SELECT filename FROM user_bid_documents'
)).fetchall()
db_filenames = {row[0] for row in db_files}

# Delete orphaned files
for file in all_files:
    if file not in db_filenames:
        os.remove(f'uploads/bid_documents/{file}')
        print(f'Deleted orphaned file: {file}')
```

### Monitor Storage Usage
```bash
du -sh uploads/bid_documents/
```

### Backup User Documents
```bash
tar -czf bid_documents_backup_$(date +%Y%m%d).tar.gz uploads/bid_documents/
```

## Future Enhancements (Optional)

1. **Advanced Text Extraction**
   - OCR for scanned PDFs (Tesseract)
   - Table extraction for pricing schedules
   - Form field detection

2. **Document Analysis**
   - Automatic requirement extraction
   - Compliance checklist generation
   - Deadline detection

3. **AI Improvements**
   - Section-specific responses (e.g., "What's in Section 3?")
   - Automatic form pre-fill suggestions
   - Comparison between RFP and capability statement

4. **Collaboration**
   - Share documents with team members
   - Comment/annotation system
   - Version tracking

5. **Templates**
   - Pre-built capability statement templates
   - Coversheet generators
   - Pricing schedule calculators

## Troubleshooting

### Issue: Text extraction fails for PDF
**Solution:** Install alternative library
```bash
pip install pdfplumber
```

### Issue: DOCX extraction fails
**Solution:** Install python-docx
```bash
pip install python-docx
```

### Issue: Files not appearing after upload
**Solution:** Check:
1. Database connection
2. Uploads directory permissions
3. Browser console for JavaScript errors

### Issue: AI not using uploaded documents
**Solution:** Verify:
1. Query contains trigger keywords
2. User is logged in
3. chatbot_kb.py updated with user_email parameter

## Technical Notes

**Text Extraction Limits:**
- Maximum 50,000 characters stored (prevents database bloat)
- Longer documents truncated with marker
- Full file always preserved for re-extraction

**Performance:**
- Document list cached in template render
- Text extraction runs async during upload
- No impact on chat response time

**Browser Compatibility:**
- Drag & drop: Chrome/Firefox/Safari/Edge (modern versions)
- File picker: All browsers
- Progress bar: CSS3 animations

## Support

For issues or questions:
1. Check browser console for JavaScript errors
2. Check terminal for Python errors
3. Verify database table exists
4. Test API endpoints with curl/Postman
5. Review extraction logs in terminal

## Credits

**Implementation Date:** January 5, 2026

**Features:**
- Database schema
- File upload/storage system
- Text extraction utility
- UI components (drag & drop, document list)
- API endpoints (upload, delete, list)
- AI integration with context awareness
- Security & validation

**Files Modified/Created:**
- `create_bid_documents_table.py` - Database setup
- `document_extractor.py` - Text extraction utility
- `app.py` - API routes & document handling
- `templates/ai_assistant.html` - UI components & JavaScript
- `chatbot_kb.py` - Enhanced KB with document context
- `BID_DOCUMENT_UPLOAD_GUIDE.md` - This documentation
