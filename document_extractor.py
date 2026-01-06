"""
Document text extraction utility for bid documents
Supports PDF, DOCX, TXT files
"""
import os
import re
from pathlib import Path

def extract_text_from_pdf(file_path):
    """Extract text from PDF file"""
    try:
        import PyPDF2
        text = ""
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += page.extract_text() + "\n"
        return text.strip()
    except ImportError:
        # PyPDF2 not installed, try alternative
        try:
            import pdfplumber
            text = ""
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() + "\n"
            return text.strip()
        except ImportError:
            return "PDF extraction libraries not available. Install PyPDF2 or pdfplumber."
    except Exception as e:
        print(f"Error extracting PDF: {e}")
        return f"Error extracting PDF: {str(e)}"

def extract_text_from_docx(file_path):
    """Extract text from DOCX file"""
    try:
        from docx import Document
        doc = Document(file_path)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        return text.strip()
    except ImportError:
        return "python-docx library not available. Install python-docx."
    except Exception as e:
        print(f"Error extracting DOCX: {e}")
        return f"Error extracting DOCX: {str(e)}"

def extract_text_from_txt(file_path):
    """Extract text from TXT file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read().strip()
    except UnicodeDecodeError:
        # Try with different encoding
        try:
            with open(file_path, 'r', encoding='latin-1') as file:
                return file.read().strip()
        except Exception as e:
            return f"Error reading text file: {str(e)}"
    except Exception as e:
        print(f"Error extracting TXT: {e}")
        return f"Error extracting TXT: {str(e)}"

def extract_text_from_file(file_path):
    """
    Extract text from supported file formats
    Returns: (success: bool, text: str, error: str)
    """
    if not os.path.exists(file_path):
        return False, "", "File not found"
    
    file_ext = Path(file_path).suffix.lower()
    
    try:
        if file_ext == '.pdf':
            text = extract_text_from_pdf(file_path)
        elif file_ext in ['.docx', '.doc']:
            text = extract_text_from_docx(file_path)
        elif file_ext == '.txt':
            text = extract_text_from_txt(file_path)
        else:
            return False, "", f"Unsupported file format: {file_ext}"
        
        if text and len(text) > 10:  # Minimum text threshold
            return True, text, None
        else:
            return False, "", "No text could be extracted from file"
            
    except Exception as e:
        return False, "", f"Extraction error: {str(e)}"

def clean_extracted_text(text, max_length=50000):
    """
    Clean and normalize extracted text
    - Remove excessive whitespace
    - Limit length for AI processing
    - Remove special characters that might cause issues
    """
    if not text:
        return ""
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove null bytes and control characters
    text = ''.join(char for char in text if ord(char) >= 32 or char in '\n\t')
    
    # Truncate if too long (keep first portion for context)
    if len(text) > max_length:
        text = text[:max_length] + "\n\n[Document truncated for processing...]"
    
    return text.strip()

def get_document_summary(text, max_lines=20):
    """Get a preview/summary of document content"""
    if not text:
        return "No content available"
    
    lines = text.split('\n')
    preview_lines = [line.strip() for line in lines if line.strip()][:max_lines]
    preview = '\n'.join(preview_lines)
    
    if len(lines) > max_lines:
        preview += f"\n\n[... {len(lines) - max_lines} more lines]"
    
    return preview

# Test function
def test_extraction():
    """Test document extraction with sample file"""
    test_file = "test_document.txt"
    
    # Create test file
    with open(test_file, 'w') as f:
        f.write("This is a test document for bid document extraction.\n")
        f.write("RFP Number: 2026-001\n")
        f.write("Deadline: January 15, 2026\n")
    
    success, text, error = extract_text_from_file(test_file)
    
    if success:
        print("✅ Extraction successful!")
        print(f"Extracted text: {text}")
        print(f"\nCleaned text: {clean_extracted_text(text)}")
        print(f"\nSummary: {get_document_summary(text)}")
    else:
        print(f"❌ Extraction failed: {error}")
    
    # Cleanup
    os.remove(test_file)

if __name__ == '__main__':
    test_extraction()
