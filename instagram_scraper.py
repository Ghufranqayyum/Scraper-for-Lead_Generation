#############################################################################

import re
import time
from selenium.webdriver.support import expected_conditions as EC

import os
import json
import uuid
import time
import sqlite3
import shutil
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
import csv
import sys
# def start_driver(headless=False):
#     user_data_dir = os.path.join(os.getcwd(), "instagram_profile_data")
#     options = Options()
#
#     if headless:
#         options.add_argument("--headless=new")
#
#     options.add_argument("--disable-gpu")
#     options.add_argument("--no-sandbox")
#     options.add_argument("--disable-dev-shm-usage")
#     options.add_argument("--disable-blink-features=AutomationControlled")
#     options.add_argument("--remote-debugging-port=9222")
#     options.add_argument(f"--user-data-dir={user_data_dir}")
#     options.add_argument("--profile-directory=Default")
#
#     service = Service(ChromeDriverManager().install())
#     driver = webdriver.Chrome(service=service, options=options)
#     return driver
import threading
profile_lock = threading.Lock()


def start_driver(headless=True, user_session=None):
    """
    Creates a new browser instance by copying the saved profile
    Perfect for multi-user deployment (Railway, etc.)
    Each user gets their own isolated browser with copied cookies
    """

    # Generate unique session ID for this user
    if user_session is None:
        user_session = str(uuid.uuid4())[:8]
    session=user_session
    print(f"🚀 Creating new browser instance for session: {user_session}")
    sys.stdout.flush() 

    # Create unique profile directory for this user
    temp_profile_dir = os.path.join(os.getcwd(), "user_profiles", f"user_{user_session}")

    # Copy saved profile to user's unique directory
    # with profile_lock:  # Prevent concurrent access issues
    #     copy_saved_profile_to_user_session(temp_profile_dir)

    # Create browser with copied profile
    driver = create_isolated_browser(temp_profile_dir, headless, user_session)

    return driver,session


def copy_saved_profile_to_user_session(user_profile_dir):
    """
    Copy the master saved profile to user's unique directory
    This ensures each user gets their own browser instance with same cookies
    """

    master_profile_folder = "instagram_profile_data"  # Your saved profile

    try:
        # Remove existing user profile if exists
        if os.path.exists(user_profile_dir):
            shutil.rmtree(user_profile_dir)

        # Create user profile directory
        os.makedirs(user_profile_dir, exist_ok=True)

        # Copy essential files for maintaining login state
        copy_essential_profile_files(master_profile_folder, user_profile_dir)

        print(f"✅ Profile copied to isolated user directory")
        sys.stdout.flush() 

    except Exception as e:
        print(f"⚠️ Profile copy failed: {e}")
        # Create minimal profile structure
        sys.stdout.flush() 
        create_minimal_profile(user_profile_dir)


def copy_essential_profile_files(source_folder, dest_folder):
    """
    Copy only essential files needed for login state
    Keeps the profile lightweight for cloud deployment
    """

    source_default = os.path.join(source_folder, "Default")
    dest_default = os.path.join(dest_folder, "Default")

    if not os.path.exists(source_default):
        raise Exception("Source Default folder not found")

    # Create destination Default folder
    os.makedirs(dest_default, exist_ok=True)

    # Essential files to copy for login state
    essential_files = [
        "Cookies",  # Main cookies file
        "Local Storage",  # Local storage data
        "Session Storage",  # Session storage
        "Web Data",  # Saved passwords, autofill
        "Login Data",  # Login information
        "Preferences",  # Browser preferences
        "Secure Preferences",  # Secure preferences
        "Network/Cookies"  # Network cookies (if exists)
    ]

    copied_count = 0
    for file_name in essential_files:
        source_file = os.path.join(source_default, file_name)
        dest_file = os.path.join(dest_default, file_name)

        try:
            if os.path.exists(source_file):
                if os.path.isdir(source_file):
                    # Create directory structure and copy
                    os.makedirs(os.path.dirname(dest_file), exist_ok=True)
                    shutil.copytree(source_file, dest_file, dirs_exist_ok=True)
                else:
                    # Copy file
                    os.makedirs(os.path.dirname(dest_file), exist_ok=True)
                    shutil.copy2(source_file, dest_file)

                copied_count += 1
                print(f"  ✓ Copied: {file_name}")
                sys.stdout.flush() 

        except Exception as e:
            print(f"  ⚠️ Failed to copy {file_name}: {e}")
            sys.stdout.flush() 

    # Copy Local State file (important for Chrome)
    try:
        source_local_state = os.path.join(source_folder, "Local State")
        dest_local_state = os.path.join(dest_folder, "Local State")

        if os.path.exists(source_local_state):
            shutil.copy2(source_local_state, dest_local_state)
            copied_count += 1
            print(f"  ✓ Copied: Local State")
            sys.stdout.flush() 

    except Exception as e:
        print(f"  ⚠️ Failed to copy Local State: {e}")

    print(f"📁 Copied {copied_count} essential files")


def create_minimal_profile(user_profile_dir):
    """
    Create minimal profile structure if copying fails
    Will require manual login but prevents crashes
    """
    try:
        default_dir = os.path.join(user_profile_dir, "Default")
        os.makedirs(default_dir, exist_ok=True)

        # Create minimal preferences
        preferences = {
            "profile": {
                "default_content_setting_values": {
                    "notifications": 2
                },
                "managed_user_id": "",
                "name": "Person 1"
            }
        }

        with open(os.path.join(default_dir, "Preferences"), 'w') as f:
            json.dump(preferences, f)

        print("📝 Created minimal profile structure")

    except Exception as e:
        print(f"❌ Failed to create minimal profile: {e}")


def create_isolated_browser(user_profile_dir, headless, session_id):
    options = Options()

    if headless:
        options.add_argument("--headless=new")  # Correct headless syntax

    # Essential Chrome options for stability
    
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-plugins")
    options.add_argument("--disable-web-security")
    options.add_argument("--allow-running-insecure-content")
    options.add_argument("--disable-features=VizDisplayCompositor")
    
    # Additional stealth measures
    options.add_argument("--disable-automation")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-dev-tools")
    options.add_argument("--no-first-run")
    options.add_argument("--disable-default-apps")
    

    # Memory and process options
    # options.add_argument("--single-process")  # Add this back
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-plugins")
    # options.add_argument("--disable-images")  # Faster loading

    # Profile and security options
    options.add_argument("--disable-web-security")
    options.add_argument("--allow-running-insecure-content")
    options.add_argument("--disable-features=VizDisplayCompositor")

    # Use user's isolated profile
    options.add_argument(f"--user-data-dir={os.path.abspath(user_profile_dir)}")
    options.add_argument("--profile-directory=Default")

    # Add unique remote debugging port to avoid conflicts
    debug_port = 9222 + hash(session_id) % 1000
    options.add_argument(f"--remote-debugging-port={debug_port}")

    try:
        # Try different Chrome paths (Windows for local, Linux for Railway)
        # chrome_binary_paths = [
        #     "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",  # Windows
        #     "/usr/bin/google-chrome",  # Railway Linux
        #     "/usr/local/bin/chromedriver",
        #     "/usr/bin/chromium-browser",
        #     "/opt/google/chrome/chrome"
        # ]

        # for chrome_path in chrome_binary_paths:
        #     if os.path.exists(chrome_path):
        #         options.binary_location = chrome_path
        #         break

        # # Use environment variable for chromedriver path
        # chromedriver_path = os.environ.get('CHROMEDRIVER_PATH', '/usr/bin/chromedriver')

        # if os.path.exists(chromedriver_path):
        #     service = Service(chromedriver_path)
        # else:
        #     # Fallback to webdriver_manager (works locally)
        #service = Service(ChromeDriverManager().install())
        service = Service("/usr/bin/chromedriver")

        driver = webdriver.Chrome(service=service, options=options)
        # Execute script to hide webdriver property
        time.sleep(10)
       # driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        # Navigate to Instagram
        print(f"🌐 Navigating to Instagram with session {session_id}...")
        sys.stdout.flush() 
        driver.get("https://www.instagram.com")
        time.sleep(3)

        return driver

    except Exception as e:
        print(f"❌ Failed to create browser: {e}")
        raise


def check_login_status(driver):

    """
    Check if successfully logged into Instagram
    """
    try:
        time.sleep(2)
        current_url = driver.current_url.lower()
        page_source = driver.page_source.lower()

        # Login page indicators
        login_indicators = [
            'accounts/login',
            'accounts/signup',
            'login/?source',
            'sign up',
            'log in',
            'loginform'
        ]

        # Logged in indicators
        logged_in_indicators = [
            '{"config":',  # Instagram's config object (logged in)
            'window._shareddata',  # Shared data (logged in)
            '"viewer":{"id":"',  # User ID in page data
            'direct/inbox',
            'explore/people'
        ]

        is_login_page = any(indicator in current_url for indicator in login_indicators)
        has_logged_in_data = any(indicator in page_source for indicator in logged_in_indicators)

        if has_logged_in_data and not is_login_page:
            print("🎉 Successfully logged in using copied profile!")
            sys.stdout.flush()
            return True
        elif is_login_page:
            print("❌ Redirected to login page - cookies may have expired")
            sys.stdout.flush()
            return False
        else:
            print("⚠️ Login status unclear - checking page elements...")
            # Additional check for navigation elements
            nav_elements = ['search & explore', 'create', 'reels', 'messages']
            if any(element in page_source for element in nav_elements):
                print("✅ Detected navigation elements - likely logged in")
                sys.stdout.flush()
                return True

            return False

    except Exception as e:
        print(f"❌ Error checking login: {e}")
        return False


def cleanup_user_session(session_id):
    """
    Clean up specific user's profile directory
    Call this when user session ends
    """
    try:
        time.sleep(20)  # Brief wait for processes to close

        user_profile_dir = os.path.join(os.getcwd(), "user_profiles", f"user_{session_id}")
        if os.path.exists(user_profile_dir):
            shutil.rmtree(user_profile_dir)
            print(f"🧹 Cleaned up session: {session_id}")
    except Exception as e:
        print(f"⚠️ Cleanup failed for {session_id}: {e}")


def cleanup_all_user_sessions():
    """
    Clean up all user profile directories
    Call this on application shutdown
    """
    try:
        user_profiles_dir = os.path.join(os.getcwd(), "user_profiles")
        if os.path.exists(user_profiles_dir):
            shutil.rmtree(user_profiles_dir)
            print("🧹 Cleaned up all user sessions")
    except Exception as e:
        print(f"⚠️ Full cleanup failed: {e}")


def get_session_info(driver, session_id):
    """
    Get information about current session
    Useful for debugging multi-user scenarios
    """
    try:
        return {
            'session_id': session_id,
            'current_url': driver.current_url,
            'window_handles': len(driver.window_handles),
            'logged_in': check_login_status(driver)
        }
    except:
        return {'session_id': session_id, 'status': 'error'}
def scroll_on_hashtag(driver, scroll_times):
    post_urls = set()
    print("⏳ Waiting for hashtag page to load...")
    time.sleep(10)
    page_source = driver.page_source
    if "challenge" in page_source.lower() or "suspended" in page_source.lower():
        print("❌ Instagram challenge or suspension detected!")
        return list(post_urls)
    sys.stdout.flush()
    
    last_height = driver.execute_script("return document.body.scrollHeight")
    time.sleep(5)
    for i in range(scroll_times):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(15)

        # ⛔ Don't use old elements — fetch fresh links every time
        fresh_links = driver.find_elements(By.XPATH, '//a[contains(@href, "/p/")]')
        for link in fresh_links:
            try:
                href = link.get_attribute("href")
                if href and "/p/" in href:
                    post_urls.add(href.split("?")[0])
                    print(href)
                    sys.stdout.flush()
                    
            except:
                continue

        print(f"🔁 Scroll {i+1}/{scroll_times} — Posts found: {len(post_urls)}")
        sys.stdout.flush()

        # Optional: break if no new scroll happened
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            print("🛑 No more scroll possible.")
            break
        last_height = new_height

    return list(post_urls)

def extract_profile_info(driver):
    data = {
        "Name": "Not Available",
        "Email": "Not Available",
        "Contact": "Not Available",
        "Profile URL": driver.current_url
    }
    time.sleep(10)
    # try:
    #     name = driver.find_element(By.XPATH, '//a[contains(@href, "/")]').text
    #     print(name)
    # except Exception as e:
    #     print(f"❌ Could not extract username: {e}")
    #     name = None

    try:
        time.sleep(5)
        bio_elem = driver.find_element(By.XPATH, '//section//div[contains(text(), "")]')
        bio = bio_elem.text.strip()
        #print(bio)
    except:
        bio = ""

    try:
        username = bio.strip().split()[0]  # first word from first line
        data["Name"]=username
        print(username)
        profile_url = f"https://www.instagram.com/{username}/"
        driver.get(profile_url)
        time.sleep(10)
        print(f"👤 Profile: {profile_url}")
        sys.stdout.flush()
        data["Profile URL"]=profile_url
        # try:
        #     elements = driver.find_elements(By.XPATH, '//a[.//span[text()="more"]]')
        #     print(f"Found {len(elements)} more elements")
        #
        #     more_btn = WebDriverWait(driver, 5).until(
        #         EC.presence_of_element_located((By.XPATH, '//a[.//span[contains(text(),"more")]]'))
        #     )
        #     from selenium.webdriver.common.action_chains import ActionChains
        #
        #     # Reliable scroll to element using ActionChains
        #     actions = ActionChains(driver)
        #     actions.move_to_element(more_btn).perform()
        #     time.sleep(1)
        #
        #     # Safer click via JS
        #     driver.execute_script("arguments[0].click();", more_btn)
        #     print("✅ Clicked on more button.")
        # except:
        #    print("Error on more")



        profile_page = driver.page_source
        email_matches = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', profile_page)
        if email_matches:
            data["Email"] = email_matches[0]


        # Search in all elements that might contain the number
        elements = driver.find_elements(By.XPATH,
                                        '//body//*[contains(text(), "+9") or contains(text(), "03") or contains(text(), "(04")]')

        contact = "Not Available"
        for el in elements:
            try:
                text = el.text.strip()
                match = re.search(r'(\+92|03)[0-9()\s-]{7,}', text)
                if match:
                    data["Contact"] = match.group(0)
                    break
            except:
                continue
        print(" From profile page")
        print(data)
        sys.stdout.flush()


    except:
        print("❌ Could not extract profile username or more button from bio and profile.")

    full_text = username + "\n" + bio

    email_match = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", full_text)
    if email_match:
        data["Email"] = email_match.group(0)

    contact_match = re.search(r"((?:\+9\d{1,3}|\(?0\d{2,4}\)?) ?\d{3,4}(?: ?\d{3,4}){1,2})", full_text)
    if contact_match:
        data["Contact"] = contact_match.group(1)
    print(" From Post Text")
    print(data)
    sys.stdout.flush()
    return data


def extract_info_from_post(driver, post_url):
 try:
    driver.get(post_url)
    time.sleep(5)

    # try:
    #     profile_link = WebDriverWait(driver, 10).until(
    #         EC.element_to_be_clickable((By.XPATH, '//article//header//a[contains(@href, "/")]'))
    #     )
    #     name = profile_link.text.strip()
    #     profile_link.click()
    #     time.sleep(2)
    # except Exception as e:
    #     print("❌ Could not click on username:", e)
    #     return {"name": "Not Available", "email": "Not Available", "contact": "Not Available"}

    info = extract_profile_info(driver)
    info["Post URL"] = post_url
    return info
 except Exception as e:
    print(f"⚠️ Error with {post_url}: {e}")
    return {
        "Name": "Error",
        "Profile URL": "Error",
        "Post URL": post_url,
        "Email": "Error",
        "Contact": "Error"
    }


# Remove: import pandas as pd

def save_to_csv(data):
    filename = "insta_leads.csv"
    counter = 1
    while os.path.exists(filename):
        filename = f"insta_leads_{counter}.csv"
        counter += 1
    
    # Replace pandas with standard CSV
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if data:
            writer.writerow(data[0].keys())  # Headers
            for row in data:
                writer.writerow(row.values())
    
    return filename

def load_cookies_into_browser(driver, platform):
    """
    Load saved cookies into isolated browser
    platform: 'instagram', 'facebook', or 'x'
    """
    print(f"🔄 Loading {platform} cookies into browser...")

    platform_configs = {
        'instagram': {
            'url': 'https://www.instagram.com',
            'cookies_file': 'instagram_cookies.json',
            'storage_file': 'instagram_local_storage.json'
        },
        'facebook': {
            'url': 'https://www.facebook.com',
            'cookies_file': 'facebook_cookies.json',
            'storage_file': 'facebook_local_storage.json'
        },
        'x': {
            'url': 'https://www.x.com',
            'cookies_file': 'x_cookies.json',
            'storage_file': 'x_local_storage.json'
        }
    }

    if platform not in platform_configs:
        print(f"❌ Unknown platform: {platform}")
        return False

    config = platform_configs[platform]

    try:
        # Check if cookie file exists
        if not os.path.exists(config['cookies_file']):
            print(f"❌ Cookie file not found: {config['cookies_file']}")
            return False

        # Navigate to platform first
        driver.get(config['url'])
        time.sleep(3)

        # Clear existing cookies
        driver.delete_all_cookies()

        # Load cookies from JSON
        with open(config['cookies_file'], 'r') as f:
            cookies = json.load(f)

        # Add cookies to browser
        cookies_added = 0
        for cookie in cookies:
            try:
                # Clean cookie format for Selenium
                cookie_clean = {
                    'name': cookie['name'],
                    'value': cookie['value'],
                    'domain': cookie['domain'],
                    'path': cookie.get('path', '/'),
                }

                # Add optional fields
                if 'secure' in cookie:
                    cookie_clean['secure'] = cookie['secure']
                if 'httpOnly' in cookie:
                    cookie_clean['httpOnly'] = cookie['httpOnly']
                if 'sameSite' in cookie and cookie['sameSite']:
                    cookie_clean['sameSite'] = cookie['sameSite']

                driver.add_cookie(cookie_clean)
                cookies_added += 1

            except Exception as e:
                print(f"⚠️ Failed to add cookie {cookie['name']}: {e}")
                continue

        print(f"✅ Added {cookies_added}/{len(cookies)} cookies")

        # Load local storage if available
        if os.path.exists(config['storage_file']):
            try:
                with open(config['storage_file'], 'r') as f:
                    local_storage = json.load(f)

                # Set local storage items
                for key, value in local_storage.items():
                    try:
                        # Escape quotes in the value
                        escaped_value = str(value).replace("'", "\\'").replace('"', '\\"')
                        driver.execute_script(f"localStorage.setItem('{key}', '{escaped_value}');")
                    except Exception as e:
                        print(f"⚠️ Failed to set local storage {key}: {e}")

                print(f"✅ Loaded {len(local_storage)} local storage items")

            except Exception as e:
                print(f"⚠️ Could not load local storage: {e}")

        # Refresh page to apply cookies
        driver.refresh()
        time.sleep(5)

        print(f"🎉 Successfully loaded {platform} session!")
        return True

    except Exception as e:
        print(f"❌ Error loading {platform} cookies: {e}")
        return False


def scrape_from_hashtag(hashtag, scrolls):
    print("STEP A: Starting scrape_hashtag")
    sys.stdout.flush()
    
    print("STEP B: About to start_driver")
    sys.stdout.flush()
    print(f"🔍 Scraping Instagram for #{hashtag} with {scrolls} scrolls")
    sys.stdout.flush() 
    driver,session = start_driver(headless=True)
    #driver.get("https://www.instagram.com/accounts/login/")
    time.sleep(20)
    print("Checking for login")
    sys.stdout.flush()
    #check_login_status(driver)
    load_cookies_into_browser(driver,"instagram")
    time.sleep(5)
    time.sleep(5)
    driver.get(f"https://www.instagram.com/explore/tags/{hashtag}/")
    time.sleep(5)
    print("Hashtag cross")
    sys.stdout.flush()
    time.sleep(10)
    print("Checking for login after hashtag")
    #check_login_status(driver)
    sys.stdout.flush()

    post_urls = scroll_on_hashtag(driver, scroll_times=scrolls)
    print(f"✅ Total posts collected: {len(post_urls)}")

    results = []
    for idx, post_url in enumerate(post_urls):
        print(f"🔍 [{idx + 1}/{len(post_urls)}] Processing: {post_url}")
        data = extract_info_from_post(driver, post_url)
        results.append(data)
        time.sleep(5)

    driver.quit()
    filename=save_to_csv(results)
    cleanup_user_session(session)
    return filename

# ---------- RUN ----------
def run_instagram_scraper(tag,scroll):
    print(f"Environment check:")
    print(f"- Chrome binary exists: {os.path.exists('/usr/bin/google-chrome')}")
    print(f"- ChromeDriver exists: {os.path.exists('/usr/bin/chromedriver')}")
    print(f"- Master profile exists: {os.path.exists('instagram_profile_data')}")
    print(f"- Current directory: {os.getcwd()}")
    print(f"- Directory contents: {os.listdir('.')}")
    print("STEP 1: Starting Insta_scraper")
    sys.stdout.flush()  # Force immediate output
    
    print(f"STEP 2: Environment check complete")
    sys.stdout.flush()
    
    file=scrape_from_hashtag(tag, scroll)
     
    print("STEP 4: scrape_hashtag completed")
    sys.stdout.flush()
    return file
