"""
Create user_bid_documents table for storing uploaded bid documents
Run this once to set up the database table
"""
import sqlite3
from datetime import datetime

def create_bid_documents_table():
    """Create table for storing user bid documents"""
    try:
        conn = sqlite3.connect('leads.db')
        cursor = conn.cursor()
        
        # Create user_bid_documents table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_bid_documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_email TEXT NOT NULL,
                filename TEXT NOT NULL,
                original_filename TEXT NOT NULL,
                file_type TEXT NOT NULL,
                file_path TEXT NOT NULL,
                file_size INTEGER,
                extracted_text TEXT,
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_used TIMESTAMP,
                metadata TEXT,
                FOREIGN KEY (user_email) REFERENCES users(email)
            )
        ''')
        
        # Create index for faster lookups
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_bid_docs_user 
            ON user_bid_documents(user_email)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_bid_docs_type 
            ON user_bid_documents(file_type)
        ''')
        
        conn.commit()
        print("✅ user_bid_documents table created successfully")
        
        # Verify table creation
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='user_bid_documents'
        """)
        result = cursor.fetchone()
        
        if result:
            print(f"✅ Table verified: {result[0]}")
            
            # Show table schema
            cursor.execute("PRAGMA table_info(user_bid_documents)")
            columns = cursor.fetchall()
            print("\n📋 Table Schema:")
            for col in columns:
                print(f"  - {col[1]} ({col[2]})")
        else:
            print("❌ Table verification failed")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error creating table: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    create_bid_documents_table()
