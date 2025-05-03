import requests
import re

def perform_login_and_get_content():
    # Step 1: Initial GET request to obtain cookies and CSRF token
    initial_url = "https://www.loslex.cz/contest/289"
    initial_headers = {
        "Host": "www.loslex.cz",
        "Sec-Ch-Ua": "\"Chromium\";v=\"135\", \"Not-A.Brand\";v=\"8\"",
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": "\"Windows\"",
        "Accept-Language": "en-US,en;q=0.9",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-User": "?1",
        "Sec-Fetch-Dest": "document",
        "Priority": "u=0, i",
        "Connection": "keep-alive"
    }
    
    # Create a session to maintain cookies between requests
    session = requests.Session()
    
    # Send the initial GET request
    initial_response = session.get(initial_url, headers=initial_headers)
    
    # Check if the request was successful
    if initial_response.status_code == 200:
        print(f"Initial GET request successful: {initial_response.status_code}")
    else:
        print(f"Failed to make initial GET request: {initial_response.status_code}")
        return None
    
    # Get cookies directly from the session
    xsrf_token = session.cookies.get('XSRF-TOKEN')
    session_cookie = session.cookies.get('los_lidova_obranna_strelba_session')
    
    # Extract CSRF token from the meta tag
    content = initial_response.text
    csrf_token_pattern = r'<meta name="csrf-token" content="([^"]+)">'
    csrf_token_match = re.search(csrf_token_pattern, content)
    
    csrf_token = None
    if csrf_token_match:
        csrf_token = csrf_token_match.group(1)
        print("Found CSRF token in meta tag")
    else:
        print("Could not find CSRF token in meta tag")
        return None
    
    print(f"XSRF-TOKEN: {xsrf_token}")
    print(f"los_lidova_obranna_strelba_session: {session_cookie}")
    print(f"CSRF-Token: {csrf_token}")
    
    # Step 2: Login POST request
    login_url = "https://www.loslex.cz/login"
    login_headers = {
        "Host": "www.loslex.cz",
        "Cache-Control": "max-age=0",
        "Sec-Ch-Ua": "\"Chromium\";v=\"135\", \"Not-A.Brand\";v=\"8\"",
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": "\"Windows\"",
        "Accept-Language": "en-US,en;q=0.9",
        "Origin": "https://www.loslex.cz",
        "Content-Type": "application/x-www-form-urlencoded",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-User": "?1",
        "Sec-Fetch-Dest": "document",
        "Referer": "https://www.loslex.cz/contest/289",
        "Priority": "u=0, i"
    }
    
    # Login credentials and CSRF token
    login_data = {
        "_token": csrf_token,
        "login": "czhunternemesisoriginal@gmail.com",
        "password": "Prdelnikus123"
    }
    
    # Send the login POST request
    login_response = session.post(login_url, headers=login_headers, data=login_data)
    
    # Check if login was successful
    if login_response.status_code == 200 or login_response.status_code == 302:
        print(f"Login request successful: {login_response.status_code}")
        
        # Check if we're redirected to a page that indicates successful login
        if "dashboard" in login_response.url or "home" in login_response.url:
            print("Login successful! Redirected to dashboard/home.")
        else:
            # Check for any error messages in the response
            error_pattern = r'<div class="alert alert-danger[^>]*>(.*?)</div>'
            error_match = re.search(error_pattern, login_response.text, re.DOTALL)
            if error_match:
                print(f"Login failed with error: {error_match.group(1).strip()}")
            else:
                print("Login possibly successful, proceeding to next step.")
    else:
        print(f"Login request failed with status code: {login_response.status_code}")
        return None
    
    # Step 3: Get the content from the original endpoint after logging in
    content_url = "https://www.loslex.cz/contest/289"
    content_headers = {
        "Host": "www.loslex.cz",
        "Sec-Ch-Ua": "\"Chromium\";v=\"135\", \"Not-A.Brand\";v=\"8\"",
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": "\"Windows\"",
        "Accept-Language": "en-US,en;q=0.9",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-User": "?1",
        "Sec-Fetch-Dest": "document",
        "Referer": "https://www.loslex.cz/login",
        "Priority": "u=0, i"
    }
    
    content_response = session.get(content_url, headers=content_headers)
    
    if content_response.status_code == 200:
        print(f"Content GET request successful: {content_response.status_code}")
        
        # Look for the specific div and extract the content
        content_html = content_response.text
        start_pattern = r'<div class="border rounded p-2">\s*<div class="flex flex-row flex-wrap gap-2 justify-around">'
        
        # Find the start position of the target content
        start_match = re.search(start_pattern, content_html)
        if start_match:
            start_pos = start_match.start()
            extracted_content = content_html[start_pos:]
            
            print("\n--- EXTRACTED CONTENT ---")
            print(extracted_content)
            print("--- END OF EXTRACTED CONTENT ---\n")
        else:
            print("Could not find the target content in the response")
    else:
        print(f"Content GET request failed with status code: {content_response.status_code}")
    
    return session

if __name__ == "__main__":
    session = perform_login_and_get_content()
    if session:
        print("Script completed successfully")
    else:
        print("Script failed")