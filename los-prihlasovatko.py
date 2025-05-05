import requests
import re
import tkinter as tk
from tkinter import messagebox, ttk, scrolledtext
from urllib.parse import urlparse
import datetime
import time
import threading
import calendar  # Added for month names

def extract_competition_id(url):
    """Extract competition ID from URL"""
    # Parse the URL and extract the path
    parsed_url = urlparse(url)
    path = parsed_url.path
    
    # Use regex to find the competition ID in the path
    match = re.search(r'/contest/(\d+)', path)
    if match:
        return match.group(1)
    return None

def get_initial_values(url):
    """Get initial values required for registration"""
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
    
    status_label.config(text="Starting initial request...")
    
    # Create a session to maintain cookies between requests
    session = requests.Session()
    
    # Send the initial GET request
    initial_response = session.get(url, headers=initial_headers)
    
    # Check if the request was successful
    if initial_response.status_code == 200:
        status_label.config(text="Initial GET request successful")
    else:
        status_label.config(text=f"Failed to make initial GET request: {initial_response.status_code}")
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
        status_label.config(text="Found CSRF token in meta tag")
    else:
        status_label.config(text="Could not find CSRF token in meta tag")
        return None
    
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
        "Referer": url,
        "Priority": "u=0, i"
    }
    
    # Login credentials and CSRF token
    login_data = {
        "_token": csrf_token,
        "login": email_entry.get(),
        "password": password_entry.get()
    }
    
    status_label.config(text="Sending login request...")
    
    # Send the login POST request
    login_response = session.post(login_url, headers=login_headers, data=login_data)
    
    # Check if login was successful
    if login_response.status_code == 200 or login_response.status_code == 302:
        status_label.config(text="Login request successful")
    else:
        status_label.config(text=f"Login request failed with status code: {login_response.status_code}")
        return None
    
    # Step 3: Get the content from the competition page after logging in
    # Update the CSRF token and cookies after login
    xsrf_token = session.cookies.get('XSRF-TOKEN')
    session_cookie = session.cookies.get('los_lidova_obranna_strelba_session')
    
    status_label.config(text="Getting page content after login...")
    
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
    
    content_response = session.get(url, headers=content_headers)
    
    if content_response.status_code == 200:
        status_label.config(text="Content GET request successful")
        
        # Update CSRF token from the response content
        content_html = content_response.text
        csrf_token_pattern = r'<meta name="csrf-token" content="([^"]+)">'
        csrf_token_match = re.search(csrf_token_pattern, content_html)
        
        if csrf_token_match:
            csrf_token = csrf_token_match.group(1)
            status_label.config(text="Updated CSRF token")
        
        # Extract the hidden input values
        user_id_pattern = r'<input type="hidden" name="user_id" value="(\d+)" />'
        contest_id_pattern = r'<input type="hidden" name="contest_id" value="(\d+)" />'
        contest_level_id_pattern = r'<input type="hidden" name="contest_level_id" value="(\d+)" />'
        
        user_id_match = re.search(user_id_pattern, content_html)
        contest_id_match = re.search(contest_id_pattern, content_html)
        contest_level_id_match = re.search(contest_level_id_pattern, content_html)
        
        user_id = user_id_match.group(1) if user_id_match else None
        contest_id = contest_id_match.group(1) if contest_id_match else None
        contest_level_id = contest_level_id_match.group(1) if contest_level_id_match else None
        
        # Get available squads from the HTML
        available_squads = []
        squad_pattern = r'<input[^>]*id="squad-(\d+)" type="radio" name="squad"[^>]*>'
        squad_matches = re.finditer(squad_pattern, content_html)
        
        for match in squad_matches:
            available_squads.append(match.group(1))
        
        # Also check for Squad R
        squad_r_pattern = r'<input[^>]*id="squad-r" type="radio" name="squad" value="(\d+)"[^>]*>'
        squad_r_match = re.search(squad_r_pattern, content_html)
        if squad_r_match:
            available_squads.append("R")
        
        # Update squad dropdown based on available squads
        # If no squads found in the HTML, use the default 12+R squads
        if available_squads:
            squad_dropdown['values'] = available_squads
            squad_dropdown.current(0)  # Select first available squad
            status_label.config(text=f"Found {len(available_squads)} squads on the page")
        
        return {
            'session': session,
            'xsrf_token': xsrf_token,
            'session_cookie': session_cookie,
            'csrf_token': csrf_token,
            'user_id': user_id,
            'contest_id': contest_id,
            'contest_level_id': contest_level_id
        }
    else:
        status_label.config(text=f"Content GET request failed with status code: {content_response.status_code}")
        return None

def verify_registration(session, url, user_name, squad):
    """Verify registration by checking if the user's name appears in the specified squad"""
    status_label.config(text="Verifying registration...")
    
    # Send GET request to competition page
    verification_headers = {
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
        "Priority": "u=0, i"
    }
    
    verification_response = session.get(url, headers=verification_headers)
    
    if verification_response.status_code == 200:
        content_html = verification_response.text
        
        # First check if the user is registered anywhere on the page
        name_pattern = f'>{user_name}<'
        user_found = re.search(name_pattern, content_html, re.IGNORECASE)
        
        if not user_found:
            status_label.config(text=f"Could not find {user_name} registered on the page")
            log_message(f"Could not find {user_name} registered on the page")
            return False
            
        # Try to find which squad the user is actually in
        # Check each possible squad
        possible_squads = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "R"]
        assigned_squad = None
        
        for check_squad in possible_squads:
            if check_squad == "R":
                squad_id = "squad-r"
            else:
                squad_id = f"squad-{check_squad}"
                
            # Find the squad section
            squad_pattern = f'<div[^>]*id="{squad_id}"[^>]*>.*?</div>'
            squad_matches = re.search(squad_pattern, content_html, re.DOTALL)
            
            if not squad_matches:
                # Try an alternative approach to find squad
                squad_alt_pattern = f'<label[^>]*for="{squad_id}"[^>]*>.*?Squad {check_squad}.*?</label>.*?<div class="w-full mt-2 text-sm gap-2 flex flex-row flex-wrap justify-center">(.*?)</div>'
                squad_matches = re.search(squad_alt_pattern, content_html, re.DOTALL)
            
            if squad_matches:
                squad_content = squad_matches.group(0)
                
                # Look for the user's name in this squad section
                if re.search(name_pattern, squad_content, re.IGNORECASE):
                    assigned_squad = check_squad
                    break
        
        # Now verify if the user is in the requested squad
        if assigned_squad:
            if assigned_squad == squad:
                status_label.config(text=f"Registration verified! Found {user_name} in Squad {squad}")
                log_message(f"Registration verified! Found {user_name} in Squad {squad}")
                return True
            else:
                status_label.config(text=f"Warning: {user_name} was placed in Squad {assigned_squad} instead of requested Squad {squad}")
                log_message(f"Warning: {user_name} was placed in Squad {assigned_squad} instead of requested Squad {squad}")
                # Still return True because registration was successful, just in a different squad
                return True
        else:
            status_label.config(text=f"User {user_name} found, but could not determine which squad")
            log_message(f"User {user_name} found, but could not determine which squad")
            return False
    else:
        status_label.config(text=f"Verification request failed with status code: {verification_response.status_code}")
        log_message(f"Verification request failed with status code: {verification_response.status_code}")
        return False

def send_registration_request(values, selected_squad, selected_division, url):
    """Send registration request and return session and response"""
    registration_url = "https://www.loslex.cz/contest/registration"
    registration_headers = {
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
        "Referer": url,
        "Priority": "u=0, i"
    }
    
    # Add cookies to the session headers
    cookies = {
        "XSRF-TOKEN": values['xsrf_token'],
        "los_lidova_obranna_strelba_session": values['session_cookie']
    }
    
    # Process the squad value correctly - explicitly handle each case to ensure proper format
    squad_value = ""
    if selected_squad == "R":
        squad_value = "0"  # Squad R maps to value 0
    else:
        squad_value = selected_squad  # Use the numerical value directly
    
    # Log the squad being used
    log_message(f"Using squad value for registration request: {squad_value}")
    
    # Registration data
    registration_data = {
        "_token": values['csrf_token'],
        "user_id": values['user_id'],
        "contest_id": values['contest_id'],
        "contest_level_id": values['contest_level_id'],
        "licence_number": license_entry.get(),
        "lex_hash": "",
        "contest_division_id": selected_division,
        "note": note_entry.get(),
        "squad": squad_value,
        "gdpr": "on"
    }
    
    # Log the full registration data for debugging
    log_message(f"Sending registration data: {registration_data}")
    
    session = values['session']
    
    # Send registration request
    registration_response = session.post(
        registration_url, 
        headers=registration_headers, 
        data=registration_data,
        cookies=cookies
    )
    
    return session, registration_response

def attempt_registration_with_retries():
    """Attempt registration with multiple retries"""
    url = url_entry.get()
    if not url:
        messagebox.showerror("Error", "Please enter a competition URL")
        return
    
    # Get initial values
    values = get_initial_values(url)
    if not values:
        messagebox.showerror("Error", "Failed to get required values")
        return
    
    # Get selected division ID from the dropdown
    selected_division = division_dropdown.get().split(" - ID:")[1]
    
    # Get selected squad
    selected_squad = squad_dropdown.get()
    log_message(f"Selected squad: {selected_squad}")
    
    # Try up to 10 times with 2-second intervals
    for attempt in range(1, 11):
        log_message(f"Registration attempt {attempt} with 2-second interval")
        status_label.config(text=f"Registration attempt {attempt} with 2-second interval")
        
        session, response = send_registration_request(values, selected_squad, selected_division, url)
        
        if response.status_code == 200 or response.status_code == 302:
            # Check if registration was successful
            if verify_registration(session, url, name_entry.get(), selected_squad):
                messagebox.showinfo("Success", f"Registration successful on attempt {attempt}!")
                return True
            else:
                log_message(f"Registration verification failed on attempt {attempt}")
        else:
            log_message(f"Registration failed with status code: {response.status_code}")
        
        # Wait 2 seconds before next attempt
        time.sleep(2)
    
    # Try another 10 times with 10-second intervals
    for attempt in range(11, 21):
        log_message(f"Registration attempt {attempt} with 10-second interval")
        status_label.config(text=f"Registration attempt {attempt} with 10-second interval")
        
        session, response = send_registration_request(values, selected_squad, selected_division, url)
        
        if response.status_code == 200 or response.status_code == 302:
            if verify_registration(session, url, name_entry.get(), selected_squad):
                messagebox.showinfo("Success", f"Registration successful on attempt {attempt}!")
                return True
            else:
                log_message(f"Registration verification failed on attempt {attempt}")
        else:
            log_message(f"Registration failed with status code: {response.status_code}")
        
        # Wait 10 seconds before next attempt
        time.sleep(10)
    
    # Final attempt after 60 seconds
    log_message("Final registration attempt after 60-second wait")
    status_label.config(text="Final registration attempt after 60-second wait")
    time.sleep(60)
    
    session, response = send_registration_request(values, selected_squad, selected_division, url)
    
    if response.status_code == 200 or response.status_code == 302:
        if verify_registration(session, url, name_entry.get(), selected_squad):
            messagebox.showinfo("Success", "Registration successful on final attempt!")
            return True
        else:
            log_message("Registration verification failed on final attempt")
    
    # If all attempts failed
    messagebox.showerror("Registration Failed", "All registration attempts failed. Please try again later or register manually.")
    log_message("All registration attempts failed")
    return False

def register_for_competition():
    """Register user for the competition"""
    threading.Thread(target=attempt_registration_with_retries, daemon=True).start()

def schedule_registration():
    """Schedule registration for the specified date and time"""
    try:
        # Get current year
        current_year = datetime.datetime.now().year
        
        # Get selected values from dropdowns
        selected_month = month_dropdown.current() + 1  # +1 because month index starts at 0
        selected_day = int(day_dropdown.get())
        selected_hour = int(hour_dropdown.get())
        selected_minute = int(minute_dropdown.get())
        
        # Create a datetime object with the scheduled date and time
        scheduled_datetime = datetime.datetime(
            year=current_year,
            month=selected_month,
            day=selected_day,
            hour=selected_hour,
            minute=selected_minute
        )
        
        # Get current datetime
        now = datetime.datetime.now()
        
        # Calculate the time difference in seconds
        time_diff = (scheduled_datetime - now).total_seconds()
        
        if time_diff <= 0:
            messagebox.showerror("Error", "Scheduled time must be in the future")
            return
        
        # Update UI
        schedule_button.config(state=tk.DISABLED)
        register_button.config(state=tk.DISABLED)
        status_label.config(text=f"Registration scheduled for {scheduled_datetime.strftime('%Y-%m-%d %H:%M')}")
        log_message(f"Registration scheduled for {scheduled_datetime.strftime('%Y-%m-%d %H:%M')}")
        
        # Start a thread to wait until the scheduled time
        threading.Thread(target=run_at_scheduled_time, args=(scheduled_datetime,), daemon=True).start()
        
    except ValueError as e:
        messagebox.showerror("Error", f"Invalid date or time format: {str(e)}")

def run_at_scheduled_time(scheduled_datetime):
    """Run the registration at the scheduled time"""
    # Get current datetime
    now = datetime.datetime.now()
    
    # Calculate the time difference in seconds
    time_diff = (scheduled_datetime - now).total_seconds()
    
    if time_diff > 0:
        # Update status every minute
        minutes_to_wait = int(time_diff / 60)
        for minute in range(minutes_to_wait, 0, -1):
            status_label.config(text=f"Registration will start in {minute} minute(s)")
            log_message(f"Registration will start in {minute} minute(s)")
            time.sleep(60)  # Wait for one minute
        
        # For the last minute, update more frequently
        seconds_to_wait = int(time_diff % 60)
        for second in range(seconds_to_wait, 0, -1):
            if second % 10 == 0:  # Update every 10 seconds in the last minute
                status_label.config(text=f"Registration will start in {second} second(s)")
                log_message(f"Registration will start in {second} second(s)")
            time.sleep(1)
    
    # When the scheduled time is reached
    status_label.config(text="Scheduled time reached! Starting registration process...")
    log_message("Scheduled time reached! Starting registration process...")
    
    # Start the registration process
    attempt_registration_with_retries()
    
    # Re-enable buttons after completion
    schedule_button.config(state=tk.NORMAL)
    register_button.config(state=tk.NORMAL)

def update_days_dropdown(*args):
    """Update days in the dropdown based on selected month"""
    month_idx = month_dropdown.current() + 1  # +1 because month index starts at 0
    year = datetime.datetime.now().year
    
    # Get the last day of the selected month
    if month_idx == 2 and calendar.isleap(year):  # February in leap year
        last_day = 29
    else:
        last_day = calendar.monthrange(year, month_idx)[1]
    
    # Update days dropdown
    days = [str(i) for i in range(1, last_day + 1)]
    day_dropdown['values'] = days
    
    # Ensure selected day is valid for the new month
    current_day = day_dropdown.get()
    if current_day and int(current_day) > last_day:
        day_dropdown.set("1")

def log_message(message):
    """Add message to the log area"""
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_text.configure(state=tk.NORMAL)
    log_text.insert(tk.END, f"[{now}] {message}\n")
    log_text.see(tk.END)  # Scroll to the end
    log_text.configure(state=tk.DISABLED)

# Create the GUI
root = tk.Tk()
root.title("LOS Competition Registration")
root.geometry("800x750")  # Increased size to accommodate new elements
root.resizable(True, True)

# Main frame
main_frame = ttk.Frame(root, padding="20")
main_frame.pack(fill=tk.BOTH, expand=True)

# Title
title_label = ttk.Label(main_frame, text="LOS Competition Registration", font=("Helvetica", 16, "bold"))
title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))

# URL Entry
url_label = ttk.Label(main_frame, text="Competition URL:")
url_label.grid(row=1, column=0, sticky=tk.W, pady=5)
url_entry = ttk.Entry(main_frame, width=50)
url_entry.grid(row=1, column=1, sticky=tk.W)
url_entry.insert(0, "")

# User Full Name field
name_label = ttk.Label(main_frame, text="Your Full Name:")
name_label.grid(row=2, column=0, sticky=tk.W, pady=5)
name_entry = ttk.Entry(main_frame, width=50)
name_entry.grid(row=2, column=1, sticky=tk.W)
name_entry.insert(0, "")

# Login Credentials
creds_frame = ttk.LabelFrame(main_frame, text="Login Credentials", padding="10")
creds_frame.grid(row=3, column=0, columnspan=2, pady=10, sticky=tk.W+tk.E)

email_label = ttk.Label(creds_frame, text="Email:")
email_label.grid(row=0, column=0, sticky=tk.W, pady=5)
email_entry = ttk.Entry(creds_frame, width=40)
email_entry.grid(row=0, column=1, sticky=tk.W)
email_entry.insert(0, "")

password_label = ttk.Label(creds_frame, text="Password:")
password_label.grid(row=1, column=0, sticky=tk.W, pady=5)
password_entry = ttk.Entry(creds_frame, width=40)  # Removed show="*" to display plaintext
password_entry.grid(row=1, column=1, sticky=tk.W)
password_entry.insert(0, "")

# Registration Details
reg_frame = ttk.LabelFrame(main_frame, text="Registration Details", padding="10")
reg_frame.grid(row=4, column=0, columnspan=2, pady=10, sticky=tk.W+tk.E)

license_label = ttk.Label(reg_frame, text="License Number:")
license_label.grid(row=0, column=0, sticky=tk.W, pady=5)
license_entry = ttk.Entry(reg_frame, width=20)
license_entry.grid(row=0, column=1, sticky=tk.W)
license_entry.insert(0, "")

# Division dropdown with updated values
division_label = ttk.Label(reg_frame, text="Division:")
division_label.grid(row=1, column=0, sticky=tk.W, pady=5)
division_values = [
    "Pistole - ID:1",
    "Kompaktní pistole - ID:2",
    "Malá pistole - ID:3",
    "Revolver - ID:4",
    "Malý revolver - ID:5",
    "PDW/PCC - ID:6",
    "Optik/Pistole - ID:7",
    "Optik/Kompaktní pistole - ID:8",
    "Optik/Malá pistole - ID:9",
    "Optik/Revolver - ID:10",
    "Optik/Malý revolver - ID:11"
]
division_dropdown = ttk.Combobox(reg_frame, width=30, values=division_values)
division_dropdown.grid(row=1, column=1, sticky=tk.W)
division_dropdown.current(1)  # Default to Kompaktní pistole

# Squad dropdown with 12 numbered squads plus Squad R (13 total)
squad_label = ttk.Label(reg_frame, text="Squad:")
squad_label.grid(row=2, column=0, sticky=tk.W, pady=5)
squad_values = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "R"]
squad_dropdown = ttk.Combobox(reg_frame, width=10, values=squad_values)
squad_dropdown.grid(row=2, column=1, sticky=tk.W)
squad_dropdown.current(0)  # Default to squad 1

note_label = ttk.Label(reg_frame, text="Note:")
note_label.grid(row=3, column=0, sticky=tk.W, pady=5)
note_entry = ttk.Entry(reg_frame, width=40)
note_entry.grid(row=3, column=1, sticky=tk.W)

# Scheduling Frame - MODIFIED SECTION
schedule_frame = ttk.LabelFrame(main_frame, text="Schedule Registration", padding="10")
schedule_frame.grid(row=5, column=0, columnspan=2, pady=10, sticky=tk.W+tk.E)

# Add month dropdown
month_label = ttk.Label(schedule_frame, text="Month:")
month_label.grid(row=0, column=0, sticky=tk.W, pady=5)
# Czech-English month names
month_names = [
    "Leden - January",
    "Únor - February",
    "Březen - March",
    "Duben - April", 
    "Květen - May",
    "Červen - June",
    "Červenec - July",
    "Srpen - August",
    "Září - September",
    "Říjen - October",
    "Listopad - November",
    "Prosinec - December"
]
month_dropdown = ttk.Combobox(schedule_frame, width=10, values=month_names)
month_dropdown.grid(row=0, column=1, sticky=tk.W, padx=(0, 10))
month_dropdown.current(datetime.datetime.now().month - 1)  # Set to current month

# Add day dropdown
day_label = ttk.Label(schedule_frame, text="Day:")
day_label.grid(row=0, column=2, sticky=tk.W, pady=5)
# Initialize with days in current month
current_month = datetime.datetime.now().month
current_year = datetime.datetime.now().year
last_day = calendar.monthrange(current_year, current_month)[1]
days = [str(i) for i in range(1, last_day + 1)]
day_dropdown = ttk.Combobox(schedule_frame, width=5, values=days)
day_dropdown.grid(row=0, column=3, sticky=tk.W, padx=(0, 10))
day_dropdown.current(datetime.datetime.now().day - 1)  # Set to current day

# Add hour dropdown (24-hour format)
hour_label = ttk.Label(schedule_frame, text="Hour:")
hour_label.grid(row=1, column=0, sticky=tk.W, pady=5)
hours = [f"{i:02d}" for i in range(24)]  # 00-23 format
hour_dropdown = ttk.Combobox(schedule_frame, width=5, values=hours)
hour_dropdown.grid(row=1, column=1, sticky=tk.W, padx=(0, 10))
hour_dropdown.current(datetime.datetime.now().hour)  # Set to current hour

# Add minute dropdown
minute_label = ttk.Label(schedule_frame, text="Minute:")
minute_label.grid(row=1, column=2, sticky=tk.W, pady=5)
minutes = [f"{i:02d}" for i in range(60)]  # 00-59 format
minute_dropdown = ttk.Combobox(schedule_frame, width=5, values=minutes)
minute_dropdown.grid(row=1, column=3, sticky=tk.W, padx=(0, 10))
minute_dropdown.current(0)  # Default to 00 minutes

# Bind the month dropdown to update days when month changes
month_dropdown.bind("<<ComboboxSelected>>", update_days_dropdown)

# Button Frame
button_frame = ttk.Frame(main_frame)
button_frame.grid(row=6, column=0, columnspan=2, pady=10, sticky=tk.W+tk.E)

register_button = ttk.Button(button_frame, text="Register Now", command=register_for_competition)
register_button.pack(side=tk.LEFT, padx=10)

schedule_button = ttk.Button(button_frame, text="Schedule Registration", command=schedule_registration)
schedule_button.pack(side=tk.LEFT, padx=10)

# Status Label
status_label = ttk.Label(main_frame, text="Ready", font=("Helvetica", 10))
status_label.grid(row=7, column=0, columnspan=2, pady=5)

# Log Area
log_frame = ttk.LabelFrame(main_frame, text="Activity Log", padding="10")
log_frame.grid(row=8, column=0, columnspan=2, pady=10, sticky=tk.W+tk.E+tk.N+tk.S)
main_frame.rowconfigure(8, weight=1)  # Make log area expandable

# Add scrolled text widget for logging
log_text = scrolledtext.ScrolledText(log_frame, height=10, width=80, wrap=tk.WORD)
log_text.pack(fill=tk.BOTH, expand=True)
log_text.configure(state=tk.DISABLED)

# Initial log message
log_message("Application started. Ready for registration.")

# Start the GUI
root.mainloop()