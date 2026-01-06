"""
Company Information Fetcher
Automatically populates company profile data from public web sources
"""
import requests
from bs4 import BeautifulSoup
import re
import json
from urllib.parse import quote_plus

def fetch_company_info(company_name, city=None, state=None):
    """
    Fetch company information from multiple sources
    Returns dict with available company data
    """
    info = {
        'company_name': company_name,
        'sources_checked': [],
        'data_found': {}
    }
    
    # Build search query
    search_query = company_name
    if city and state:
        search_query += f" {city} {state}"
    elif state:
        search_query += f" {state}"
    
    # Try SAM.gov entity search (for federal contractors)
    sam_data = fetch_from_sam_gov(company_name)
    if sam_data:
        info['sources_checked'].append('SAM.gov')
        info['data_found'].update(sam_data)
    
    # Try Google search for company website and basic info
    google_data = fetch_from_google(search_query)
    if google_data:
        info['sources_checked'].append('Google')
        info['data_found'].update(google_data)
    
    return info

def fetch_from_sam_gov(company_name):
    """
    Fetch company data from SAM.gov entity management API
    Returns EIN, CAGE Code, UEI, DUNS, certifications, NAICS codes
    """
    try:
        # SAM.gov Entity Management API endpoint
        api_key = os.environ.get('SAM_GOV_API_KEY')
        if not api_key:
            return None
        
        url = "https://api.sam.gov/entity-information/v3/entities"
        params = {
            'api_key': api_key,
            'legalBusinessName': company_name,
            'includeSections': 'entityRegistration,coreData,repsAndCerts'
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('entityData') and len(data['entityData']) > 0:
                entity = data['entityData'][0]
                
                result = {}
                
                # Core data
                core_data = entity.get('coreData', {})
                result['company_ein'] = core_data.get('taxIdentificationNumber')
                result['company_duns'] = core_data.get('dunsNumber')
                result['company_cage_code'] = core_data.get('cageCode')
                result['company_uei'] = core_data.get('ueiSAM')
                
                # Address
                physical_address = core_data.get('physicalAddress', {})
                result['address'] = physical_address.get('addressLine1')
                result['city'] = physical_address.get('city')
                result['state'] = physical_address.get('stateOrProvinceCode')
                result['zip_code'] = physical_address.get('zipCode')
                
                # Business info
                result['business_type'] = core_data.get('businessTypeCode')
                
                # Entity registration data
                entity_reg = entity.get('entityRegistration', {})
                result['years_in_business'] = entity_reg.get('activationDate')  # Can calculate from this
                
                # NAICS codes
                naics_list = entity_reg.get('naicsList', [])
                if naics_list:
                    primary_naics = [n.get('naicsCode') for n in naics_list if n.get('isPrimary')]
                    other_naics = [n.get('naicsCode') for n in naics_list if not n.get('isPrimary')]
                    result['naics_codes'] = ', '.join(primary_naics + other_naics)
                
                # Certifications (8(a), WOSB, SDVOSB, HUBZone, etc.)
                certifications = []
                reps_certs = entity.get('repsAndCerts', {})
                if reps_certs.get('isSmallBusiness'):
                    certifications.append('Small Business')
                if reps_certs.get('is8AProgram'):
                    certifications.append('8(a)')
                if reps_certs.get('isWomanOwned'):
                    certifications.append('WOSB')
                if reps_certs.get('isServiceDisabledVeteranOwned'):
                    certifications.append('SDVOSB')
                if reps_certs.get('isHUBZone'):
                    certifications.append('HUBZone')
                
                if certifications:
                    result['certifications'] = ', '.join(certifications)
                
                return result
                
    except Exception as e:
        print(f"SAM.gov fetch error: {e}")
        return None
    
    return None

def fetch_from_google(search_query):
    """
    Fetch basic company info from Google search results
    Returns website, phone, address if available
    """
    try:
        # Use Google Custom Search API or simple search
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        # Search for company website
        search_url = f"https://www.google.com/search?q={quote_plus(search_query)}"
        response = requests.get(search_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            result = {}
            
            # Extract website from search results
            for link in soup.find_all('a', href=True):
                href = link['href']
                if '/url?q=' in href:
                    url = href.split('/url?q=')[1].split('&')[0]
                    if url.startswith('http') and 'google.com' not in url:
                        # Validate it's likely a company website
                        if any(tld in url for tld in ['.com', '.net', '.org', '.biz']):
                            result['website'] = url
                            break
            
            # Look for phone numbers in results
            phone_pattern = r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
            phones = re.findall(phone_pattern, response.text)
            if phones:
                result['phone'] = phones[0]
            
            return result
            
    except Exception as e:
        print(f"Google fetch error: {e}")
        return None
    
    return None

def fetch_company_website_data(website_url):
    """
    Scrape company's own website for additional information
    Returns contact info, about data, services
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(website_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            result = {}
            
            # Look for phone numbers
            phone_pattern = r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
            phones = re.findall(phone_pattern, response.text)
            if phones:
                result['phone'] = phones[0]
            
            # Look for email addresses
            email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
            emails = re.findall(email_pattern, response.text)
            if emails:
                # Filter out common tracking emails
                valid_emails = [e for e in emails if 'noreply' not in e and 'tracking' not in e]
                if valid_emails:
                    result['primary_contact_email'] = valid_emails[0]
            
            # Look for address
            # Common patterns: "123 Main St, City, ST 12345"
            address_text = soup.get_text()
            
            # Look for certifications mentioned on website
            cert_keywords = ['8(a)', 'woman-owned', 'WOSB', 'SDVOSB', 'veteran', 'HUBZone', 'small business']
            found_certs = []
            for cert in cert_keywords:
                if cert.lower() in address_text.lower():
                    found_certs.append(cert)
            
            if found_certs:
                result['certifications'] = ', '.join(found_certs)
            
            # Look for "About" section for company description
            about_section = soup.find(['section', 'div'], class_=re.compile(r'about', re.I))
            if about_section:
                result['past_performance'] = about_section.get_text()[:500]  # First 500 chars
            
            return result
            
    except Exception as e:
        print(f"Website scrape error: {e}")
        return None
    
    return None

def enrich_company_profile(company_name, city=None, state=None, website=None):
    """
    Main function to enrich company profile data
    Combines data from multiple sources
    """
    enriched_data = {
        'success': False,
        'sources_used': [],
        'data': {}
    }
    
    # Fetch from SAM.gov (most reliable for federal contractors)
    print(f"🔍 Searching SAM.gov for {company_name}...")
    sam_data = fetch_from_sam_gov(company_name)
    if sam_data:
        enriched_data['data'].update(sam_data)
        enriched_data['sources_used'].append('SAM.gov')
        enriched_data['success'] = True
        print(f"✅ Found data on SAM.gov")
    
    # If we have a website, scrape it for additional info
    if website:
        print(f"🔍 Scraping company website {website}...")
        website_data = fetch_company_website_data(website)
        if website_data:
            # Only update fields that weren't found in SAM.gov
            for key, value in website_data.items():
                if key not in enriched_data['data'] or not enriched_data['data'][key]:
                    enriched_data['data'][key] = value
            enriched_data['sources_used'].append('Company Website')
            enriched_data['success'] = True
            print(f"✅ Found additional data on website")
    
    # Try Google search as fallback
    if not enriched_data['success']:
        print(f"🔍 Searching Google for {company_name}...")
        google_data = fetch_from_google(f"{company_name} {city or ''} {state or ''}")
        if google_data:
            enriched_data['data'].update(google_data)
            enriched_data['sources_used'].append('Google Search')
            enriched_data['success'] = True
            print(f"✅ Found data via Google search")
    
    return enriched_data

# Import os for environment variables
import os

if __name__ == "__main__":
    # Test the fetcher
    test_company = "ABC Cleaning Services"
    result = enrich_company_profile(test_company, city="Norfolk", state="VA")
    
    print("\n" + "="*60)
    print("Company Information Fetcher - Test Results")
    print("="*60)
    print(f"\nCompany: {test_company}")
    print(f"Success: {result['success']}")
    print(f"Sources Used: {', '.join(result['sources_used'])}")
    print(f"\nData Found:")
    for key, value in result['data'].items():
        print(f"  {key}: {value}")
