import requests
import re
import tkinter as tk
from tkinter import messagebox, ttk, scrolledtext
from urllib.parse import urlparse
import datetime
import time
import threading
from tkcalendar import DateEntry  # You'll need to install this package: pip install tkcalendar

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
        
        # Pattern to find the user's name in the specified squad
        if squad == "R":
            squad_id = "squad-r"
        else:
            squad_id = f"squad-{squad}"
        
        # First, find the squad section
        squad_pattern = f'<div[^>]*id="{squad_id}"[^>]*>.*?</div>'
        squad_matches = re.search(squad_pattern, content_html, re.DOTALL)
        
        if not squad_matches:
            # Try an alternative approach to find squad
            squad_alt_pattern = f'<label[^>]*for="{squad_id}"[^>]*>.*?Squad {squad}.*?</label>.*?<div class="w-full mt-2 text-sm gap-2 flex flex-row flex-wrap justify-center">(.*?)</div>'
            squad_matches = re.search(squad_alt_pattern, content_html, re.DOTALL)
            
        if squad_matches:
            squad_content = squad_matches.group(0)
            
            # Now look for the user's name in this squad section
            name_pattern = f'>{user_name}<'
            if re.search(name_pattern, squad_content, re.IGNORECASE):
                status_label.config(text=f"Registration verified! Found {user_name} in Squad {squad}")
                log_message(f"Registration verified! Found {user_name} in Squad {squad}")
                return True
            else:
                status_label.config(text=f"Could not find {user_name} in Squad {squad}")
                log_message(f"Could not find {user_name} in Squad {squad}")
                return False
        else:
            status_label.config(text=f"Could not find Squad {squad} in the response")
            log_message(f"Could not find Squad {squad} in the response")
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
    
    # Convert squad R to 0 for the API
    if selected_squad == "R":
        selected_squad = "0"
    
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
        "squad": selected_squad,
        "gdpr": "on"
    }
    
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
    
    # Try up to 10 times with 2-second intervals
    for attempt in range(1, 11):
        log_message(f"Registration attempt {attempt} with 2-second interval")
        status_label.config(text=f"Registration attempt {attempt} with 2-second interval")
        
        session, response = send_registration_request(values, selected_squad, selected_division, url)
        
        if response.status_code == 200 or response.status_code == 302:
            if verify_registration(session, url, name_entry.get(), selected_squad):
                messagebox.showinfo("Success", f"Registration successful on attempt {attempt}!")
                return True
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
        # Get scheduled date and time
        scheduled_date = cal_date.get_date()
        scheduled_time = time.strptime(time_entry.get(), "%H:%M")
        
        # Create a datetime object with the scheduled date and time
        scheduled_datetime = datetime.datetime.combine(
            scheduled_date,
            datetime.time(hour=scheduled_time.tm_hour, minute=scheduled_time.tm_min)
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
        
    except ValueError:
        messagebox.showerror("Error", "Invalid time format. Please use HH:MM (24-hour format)")

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
url_entry.insert(0, "https://www.loslex.cz/contest/362")

# User Full Name field
name_label = ttk.Label(main_frame, text="Your Full Name:")
name_label.grid(row=2, column=0, sticky=tk.W, pady=5)
name_entry = ttk.Entry(main_frame, width=50)
name_entry.grid(row=2, column=1, sticky=tk.W)
name_entry.insert(0, "Vladislav Bouška")

# Login Credentials
creds_frame = ttk.LabelFrame(main_frame, text="Login Credentials", padding="10")
creds_frame.grid(row=3, column=0, columnspan=2, pady=10, sticky=tk.W+tk.E)

email_label = ttk.Label(creds_frame, text="Email:")
email_label.grid(row=0, column=0, sticky=tk.W, pady=5)
email_entry = ttk.Entry(creds_frame, width=40)
email_entry.grid(row=0, column=1, sticky=tk.W)
email_entry.insert(0, "czhunternemesisoriginal@gmail.com")

password_label = ttk.Label(creds_frame, text="Password:")
password_label.grid(row=1, column=0, sticky=tk.W, pady=5)
password_entry = ttk.Entry(creds_frame, width=40, show="*")
password_entry.grid(row=1, column=1, sticky=tk.W)
password_entry.insert(0, "Prdelnikus123")

# Registration Details
reg_frame = ttk.LabelFrame(main_frame, text="Registration Details", padding="10")
reg_frame.grid(row=4, column=0, columnspan=2, pady=10, sticky=tk.W+tk.E)

license_label = ttk.Label(reg_frame, text="License Number:")
license_label.grid(row=0, column=0, sticky=tk.W, pady=5)
license_entry = ttk.Entry(reg_frame, width=20)
license_entry.grid(row=0, column=1, sticky=tk.W)
license_entry.insert(0, "ZP031187")

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

# Scheduling Frame
schedule_frame = ttk.LabelFrame(main_frame, text="Schedule Registration", padding="10")
schedule_frame.grid(row=5, column=0, columnspan=2, pady=10, sticky=tk.W+tk.E)

date_label = ttk.Label(schedule_frame, text="Date:")
date_label.grid(row=0, column=0, sticky=tk.W, pady=5)
cal_date = DateEntry(schedule_frame, width=12, background='darkblue', foreground='white', borderwidth=2)
cal_date.grid(row=0, column=1, sticky=tk.W, pady=5)

time_label = ttk.Label(schedule_frame, text="Time (24h):")
time_label.grid(row=1, column=0, sticky=tk.W, pady=5)
time_entry = ttk.Entry(schedule_frame, width=10)
time_entry.grid(row=1, column=1, sticky=tk.W, pady=5)
time_entry.insert(0, "12:00")  # Default to noon

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