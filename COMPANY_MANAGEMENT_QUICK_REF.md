# Multi-Company Management - Quick Reference

## 🚀 Quick Start (3 Steps)

### 1. Create Company Profile
```
Navigate to: /admin/manage-companies
Click: "Add New Company" button
Fill: Company Name (required) + other details
Save: Company created!
```

### 2. Upload Documents for Company
```
Navigate to: /ai-assistant
Select: Company from dropdown
Upload: Drag & drop RFP/documents
Done: Document linked to company
```

### 3. Manage Company
```
Edit: Click "Edit" button → Update fields → Save
Delete: Click "Delete" button → Confirm
Toggle: Click "Activate/Deactivate" button
```

---

## 📋 Required Fields

**Minimum to create company:**
- Company Name ✅

**Recommended for federal contracting:**
- Business Type
- EIN (Employer Identification Number)
- CAGE Code
- UEI Number
- Address (City, State)
- Primary NAICS Codes
- Certifications (8(a), WOSB, etc.)

---

## 🔗 Routes

| Route | Purpose |
|-------|---------|
| `/admin/manage-companies` | Main company management page |
| `/api/create-company` | POST - Create new company |
| `/api/get-company/<id>` | GET - Fetch company details |
| `/api/update-company/<id>` | PUT - Update company |
| `/api/delete-company/<id>` | DELETE - Remove company |
| `/api/toggle-company-status/<id>` | POST - Activate/Deactivate |

---

## 📊 Database Tables

### company_profiles (30 fields)
```
Basic: id, admin_email, company_name, business_type
Federal: ein, duns_number, cage_code, uei_number
Address: street_address, city, state, zip_code
Contact: phone, email, website
Industry: primary_naics_codes, certifications
Details: year_established, annual_revenue, employee_count
Capabilities: past_performance_summary, bonding_capacity
Status: is_active, created_at, updated_at
```

### user_bid_documents (enhanced)
```
Added: company_id INTEGER (foreign key)
```

### company_bid_documents (linking table)
```
Many-to-many: company_id, document_id, relationship, notes
```

---

## 🎨 UI Features

### Company Card Shows:
- ✅ Company name + business type badge
- ✅ EIN, CAGE Code, UEI Number
- ✅ Location (city, state, zip)
- ✅ Contact info (phone, email, website)
- ✅ Certifications
- ✅ NAICS codes
- ✅ Action buttons (Edit, Delete, Activate/Deactivate)

### Modal Form Sections:
1. Basic Information (name, business type)
2. Federal Registration (EIN, DUNS, CAGE, UEI)
3. Address (street, city, state, zip)
4. Contact Information (phone, email, website)
5. NAICS Codes & Certifications
6. Company Details (year, revenue, employees, service areas)
7. Capabilities & Performance (past performance, bonding, insurance)
8. Additional Information (capability statement URL, hours, notes)

---

## 🛡️ Security

- ✅ **Login Required**: All routes protected with `@login_required`
- ✅ **Ownership Verification**: Admin can only see/edit their own companies
- ✅ **SQL Injection Prevention**: Parameterized queries
- ✅ **Data Validation**: Required fields, type checking

```python
# All queries filtered by admin:
WHERE admin_email = :email
```

---

## 🧪 Testing Commands

### Check Tables Exist
```bash
sqlite3 leads.db "PRAGMA table_info(company_profiles);"
sqlite3 leads.db "PRAGMA table_info(company_bid_documents);"
sqlite3 leads.db "PRAGMA table_info(user_bid_documents);" | grep company_id
```

### Query Companies
```sql
SELECT id, company_name, business_type, is_active 
FROM company_profiles 
WHERE admin_email = 'admin@contractlink.ai';
```

### Query Documents with Companies
```sql
SELECT d.id, d.original_filename, d.file_type, c.company_name
FROM user_bid_documents d
LEFT JOIN company_profiles c ON d.company_id = c.id
WHERE d.user_email = 'admin@contractlink.ai';
```

---

## 💡 Common Use Cases

### Use Case 1: Proposal Writer with 3 Clients
```
Admin: proposal_writer@email.com
Companies:
  1. ABC Cleaning (Hampton, VA)
  2. XYZ Janitorial (Norfolk, VA)
  3. Elite Services (Virginia Beach, VA)

Workflow:
- Create 3 company profiles
- Upload RFP for ABC → Select "ABC Cleaning"
- Upload capability statement for XYZ → Select "XYZ Janitorial"
- Upload pricing schedule for Elite → Select "Elite Services"
- AI Assistant knows which company each document belongs to
```

### Use Case 2: Consultant Managing 10+ Companies
```
Admin: consultant@contractlink.ai
Companies: 10 cleaning contractors across VA

Workflow:
- Create profiles for all 10 companies (30 fields each)
- Upload documents organized by company
- Deactivate companies after project completion
- Filter documents by active/inactive status
```

### Use Case 3: Engineer Tracking Certifications
```
Admin: engineer@firm.com
Companies: 5 certified firms (8(a), WOSB, SDVOSB)

Workflow:
- Create profiles with certification details
- Upload capability statements
- Track past performance summaries
- Update bonding/insurance info as needed
```

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| Empty company dropdown | Create company at `/admin/manage-companies` |
| "Company not found" error | Verify `admin_email` matches session user |
| Modal doesn't open | Check Bootstrap 5 JS loaded, check console |
| Upload doesn't link to company | Verify `company_id` in FormData, check `company_id` column exists |
| 500 error on create | Check Flask logs for traceback, verify schema |

### Debug Commands
```python
# Flask logs show:
📊 Admin {email} managing {count} companies  # Route loaded
✅ Company created: {name} by {email}        # Create success
✅ Company updated: ID {id} by {email}       # Update success
✅ Company deleted: {name} (ID {id})         # Delete success
❌ Error loading company profiles: {error}  # Route error
```

---

## 📈 Next Steps

After creating companies:
1. Upload bid documents for each company
2. Use AI Assistant to analyze documents by company
3. Generate proposals with company-specific data
4. Track document expiration dates
5. Monitor activity per company

---

## 🔮 Future Features (Roadmap)

- [ ] Filter documents by company in sidebar
- [ ] Company name badge on each document
- [ ] Per-company statistics dashboard
- [ ] Multiple admins per company (team access)
- [ ] SAM.gov API auto-populate (from UEI)
- [ ] Capability statement generator
- [ ] Past performance tracker
- [ ] Contract award notifications

---

## 📞 Support

**Flask Logs:** Check terminal for emoji-prefixed messages (📊, ✅, ❌)  
**Database:** `sqlite3 leads.db` to query tables  
**API Testing:** Use curl/Postman to test endpoints  
**Browser Console:** Check for JavaScript errors  

**Contact:** admin@contractlink.ai

---

**Version:** 1.0.0  
**Last Updated:** January 5, 2026  
**Status:** ✅ PRODUCTION READY

**See Full Documentation:** `COMPANY_MANAGEMENT_GUIDE.md`
