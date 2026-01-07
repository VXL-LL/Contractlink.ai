#!/usr/bin/env python3
"""
Fix company_profiles table in production PostgreSQL database
This script removes the problematic foreign key constraint and ensures the table exists
"""

import os
import sys
from sqlalchemy import create_engine, text

def fix_company_profiles_table():
    """Create or fix company_profiles table in production"""
    
    # Get database URL from environment
    database_url = os.environ.get('DATABASE_URL')
    
    if not database_url:
        print("❌ DATABASE_URL environment variable not set")
        print("   This script is for production database only")
        return False
    
    # Handle Render.com PostgreSQL URL format
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    
    print(f"🔗 Connecting to production database...")
    
    try:
        engine = create_engine(database_url)
        
        with engine.connect() as conn:
            # Check if table exists
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'company_profiles'
                )
            """))
            table_exists = result.scalar()
            
            if table_exists:
                print("✅ company_profiles table exists")
                
                # Check if problematic foreign key exists
                result = conn.execute(text("""
                    SELECT constraint_name 
                    FROM information_schema.table_constraints 
                    WHERE table_name = 'company_profiles' 
                    AND constraint_type = 'FOREIGN KEY'
                    AND constraint_name LIKE '%admin_email%'
                """))
                fk_constraint = result.fetchone()
                
                if fk_constraint:
                    print(f"🔧 Removing problematic foreign key: {fk_constraint[0]}")
                    conn.execute(text(f"ALTER TABLE company_profiles DROP CONSTRAINT IF EXISTS {fk_constraint[0]}"))
                    conn.commit()
                    print("✅ Foreign key constraint removed")
                else:
                    print("✅ No problematic foreign key found")
                    
            else:
                print("📝 Creating company_profiles table...")
                
                # Create table without foreign key constraint
                conn.execute(text('''
                    CREATE TABLE company_profiles (
                        id SERIAL PRIMARY KEY,
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
                        is_active BOOLEAN DEFAULT TRUE
                    )
                '''))
                conn.commit()
                print("✅ company_profiles table created")
                
                # Create indexes
                print("📝 Creating indexes...")
                conn.execute(text('CREATE INDEX IF NOT EXISTS idx_company_profiles_admin ON company_profiles(admin_email)'))
                conn.execute(text('CREATE INDEX IF NOT EXISTS idx_company_profiles_active ON company_profiles(is_active)'))
                conn.execute(text('CREATE INDEX IF NOT EXISTS idx_company_profiles_name ON company_profiles(company_name)'))
                conn.commit()
                print("✅ Indexes created")
            
            # Verify table structure
            print("\n📋 Verifying table structure...")
            result = conn.execute(text("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'company_profiles'
                ORDER BY ordinal_position
            """))
            
            columns = result.fetchall()
            print(f"✅ Table has {len(columns)} columns:")
            for col_name, col_type in columns:
                print(f"   - {col_name} ({col_type})")
            
            print("\n✅ Production database fix complete!")
            return True
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("Company Profiles Table Production Fix")
    print("=" * 60)
    print()
    
    success = fix_company_profiles_table()
    
    if success:
        print("\n✅ SUCCESS - Production database is ready")
        sys.exit(0)
    else:
        print("\n❌ FAILED - Please check error messages above")
        sys.exit(1)
