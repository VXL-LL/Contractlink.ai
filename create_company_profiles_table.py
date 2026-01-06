"""
Create company_profiles table for admin users managing multiple client companies
Run this once to set up the database table
"""
import sqlite3
from datetime import datetime

def create_company_profiles_table():
    """Create table for storing client company profiles managed by admins"""
    try:
        conn = sqlite3.connect('leads.db')
        cursor = conn.cursor()
        
        # Create company_profiles table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS company_profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                admin_email TEXT NOT NULL,
                company_name TEXT NOT NULL,
                company_ein TEXT,
                company_duns TEXT,
                company_cage_code TEXT,
                company_uei TEXT,
                address TEXT,
                city TEXT,
                state TEXT,
                zip_code TEXT,
                phone TEXT,
                website TEXT,
                primary_contact_name TEXT,
                primary_contact_email TEXT,
                primary_contact_phone TEXT,
                business_type TEXT,
                certifications TEXT,
                naics_codes TEXT,
                years_in_business INTEGER,
                employee_count INTEGER,
                annual_revenue TEXT,
                bonding_capacity TEXT,
                insurance_info TEXT,
                past_performance TEXT,
                specialty_areas TEXT,
                service_regions TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1,
                FOREIGN KEY (admin_email) REFERENCES users(email)
            )
        ''')
        
        # Link bid documents to companies
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS company_bid_documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                document_id INTEGER NOT NULL,
                relationship TEXT DEFAULT 'general',
                notes TEXT,
                linked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (company_id) REFERENCES company_profiles(id) ON DELETE CASCADE,
                FOREIGN KEY (document_id) REFERENCES user_bid_documents(id) ON DELETE CASCADE,
                UNIQUE(company_id, document_id)
            )
        ''')
        
        # Add company_id to user_bid_documents if it doesn't exist
        try:
            cursor.execute('ALTER TABLE user_bid_documents ADD COLUMN company_id INTEGER')
            print("✅ Added company_id column to user_bid_documents")
        except sqlite3.OperationalError as e:
            if 'duplicate column' in str(e).lower():
                print("ℹ️ company_id column already exists")
            else:
                raise
        
        # Create indexes for faster lookups
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_company_profiles_admin 
            ON company_profiles(admin_email)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_company_profiles_active 
            ON company_profiles(is_active)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_company_bid_docs_company 
            ON company_bid_documents(company_id)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_bid_docs_company 
            ON user_bid_documents(company_id)
        ''')
        
        conn.commit()
        print("✅ company_profiles and company_bid_documents tables created successfully")
        
        # Verify table creation
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name IN ('company_profiles', 'company_bid_documents')
        """)
        tables = cursor.fetchall()
        
        if len(tables) == 2:
            print(f"✅ Tables verified: {[t[0] for t in tables]}")
            
            # Show table schemas
            for table_name in ['company_profiles', 'company_bid_documents']:
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = cursor.fetchall()
                print(f"\n📋 {table_name} Schema:")
                for col in columns:
                    print(f"  - {col[1]} ({col[2]})")
        else:
            print("❌ Table verification failed")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    create_company_profiles_table()
