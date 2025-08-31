import re
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import os


# def start_driver(headless=False):
#     # ✅ Define a consistent user data directory
#     user_data_dir = os.path.join(os.getcwd(), "x_scraper_profile")
#
#     options = Options()
#
#     if headless:
#         options.add_argument("--headless=new")
#
#     # Chrome crash preventers
#     options.add_argument("--disable-gpu")
#     options.add_argument("--no-sandbox")
#     options.add_argument("--disable-dev-shm-usage")
#     options.add_argument("--disable-blink-features=AutomationControlled")
#     options.add_argument("--remote-debugging-port=9222")
#
#     # ✅ Persist profile directory so login is saved
#     options.add_argument(f"--user-data-dir={user_data_dir}")
#     options.add_argument("--profile-directory=Default")  # Can change if you want multiple
#
#     service = Service(ChromeDriverManager().install())
#     driver = webdriver.Chrome(service=service, options=options)
#
#     return driver
import json
import uuid
import time
import sqlite3
import shutil
import threading
profile_lock = threading.Lock()
import csv


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

    # Create unique profile directory for this user
    temp_profile_dir = os.path.join(os.getcwd(), "user_profiles", f"user_{user_session}")

    # Copy saved profile to user's unique directory
    with profile_lock:  # Prevent concurrent access issues
        copy_saved_profile_to_user_session(temp_profile_dir)

    # Create browser with copied profile
    driver = create_isolated_browser(temp_profile_dir, headless, user_session)

    return driver,session


def copy_saved_profile_to_user_session(user_profile_dir):
    """
    Copy the master saved profile to user's unique directory
    This ensures each user gets their own browser instance with same cookies
    """

    master_profile_folder = "x_scraper_profile"  # Your saved profile

    try:
        # Remove existing user profile if exists
        if os.path.exists(user_profile_dir):
            shutil.rmtree(user_profile_dir)

        # Create user profile directory
        os.makedirs(user_profile_dir, exist_ok=True)

        # Copy essential files for maintaining login state
        copy_essential_profile_files(master_profile_folder, user_profile_dir)

        print(f"✅ Profile copied to isolated user directory")

    except Exception as e:
        print(f"⚠️ Profile copy failed: {e}")
        # Create minimal profile structure
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

        except Exception as e:
            print(f"  ⚠️ Failed to copy {file_name}: {e}")

    # Copy Local State file (important for Chrome)
    try:
        source_local_state = os.path.join(source_folder, "Local State")
        dest_local_state = os.path.join(dest_folder, "Local State")

        if os.path.exists(source_local_state):
            shutil.copy2(source_local_state, dest_local_state)
            copied_count += 1
            print(f"  ✓ Copied: Local State")

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
        options.add_argument("--headless=new")
    
    # Essential Chrome options for Railway
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-plugins")
    options.add_argument("--disable-web-security")
    options.add_argument("--allow-running-insecure-content")
    options.add_argument("--disable-features=VizDisplayCompositor")
    
    # Use user's isolated profile
    options.add_argument(f"--user-data-dir={os.path.abspath(user_profile_dir)}")
    options.add_argument("--profile-directory=Default")
    
    # Set Chrome binary location for Railway
    options.binary_location = "/usr/bin/google-chrome-stable"
    
    try:
        # For Railway/Linux - use the installed ChromeDriver
        service = Service("/usr/bin/chromedriver")
        driver = webdriver.Chrome(service=service, options=options)
        
        print(f"🌐 Navigating to Instagram with session {session_id}...")
        driver.get("https://x.com/login")
        time.sleep(3)
        return driver
        
    except Exception as e:
        print(f"❌ Failed to create driver: {e}")
        # Fallback to webdriver_manager for local development
        try:
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
            driver.get("https://x.com/login")
            time.sleep(3)
            return driver
        except Exception as e2:
            print(f"❌ Fallback also failed: {e2}")
            raise e2


def check_login_status(driver):
    try:
        time.sleep(2)
        current_url = driver.current_url.lower()
        page_source = driver.page_source.lower()

        # X/Twitter login page indicators
        login_indicators = [
            'i/flow/login',
            'login',
            'signup',
            'enter your phone'
        ]

        # X/Twitter logged in indicators
        logged_in_indicators = [
            '"screen_name"',
            'compose/tweet',
            'home',
            'notifications'
        ]

        is_login_page = any(indicator in current_url for indicator in login_indicators)
        has_logged_in_data = any(indicator in page_source for indicator in logged_in_indicators)

        if has_logged_in_data and not is_login_page:
            print("Successfully logged in!")
            return True
        else:
            print("Not logged in - profile authentication failed")
            return False

    except Exception as e:
        print(f"Error checking login: {e}")
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


from urllib.parse import urljoin

def scroll_and_collect(driver, scroll_times=None, max_wait=3):
    collected = []
    tweet_ids_seen = set()
    scroll_count = 0
    stagnant_scrolls = 0
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        tweets = driver.find_elements(By.XPATH, '//article[@data-testid="tweet"]')

        for tweet in tweets:
            try:
                tweet_html = tweet.get_attribute('outerHTML')
                soup = BeautifulSoup(tweet_html, 'html.parser')

                # Extract tweet text
                tweet_text_tag = soup.find('div', {'data-testid': 'tweetText'})
                tweet_text = tweet_text_tag.get_text(separator=' ').strip() if tweet_text_tag else ""

                # Extract email
                emails = extract_emails(tweet_text)
                email = emails[0] if emails else "Not Available"

                # Extract author name
                name_tag = soup.find('div', {'dir': 'auto'})
                name = name_tag.text.strip() if name_tag else "Unknown"

                # Get tweet URL from "a" tag with "href" containing "/status/"
                tweet_link_tag = soup.find('a', href=re.compile(r'/status/\d+'))
                tweet_path = tweet_link_tag['href'] if tweet_link_tag else ""
                tweet_url = urljoin("https://x.com", tweet_path) if tweet_path else "Unavailable"

                tweet_id = tweet_path.split("/")[-1] if tweet_path else None
                if tweet_id and tweet_id not in tweet_ids_seen:
                    tweet_ids_seen.add(tweet_id)
                    collected.append({
                        "Name": name,
                        "Tweet URL": tweet_url,
                        "Email": email,
                        "Tweet Text": tweet_text
                    })

            except Exception as e:
                print("⚠️ Skipping tweet due to error:", e)

        # Scroll and wait
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3 + (scroll_count % 3))  # wait 3-5 sec
        time.sleep(15)

        # Scroll check
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            stagnant_scrolls += 1
            if stagnant_scrolls >= max_wait:
                break
        else:
            stagnant_scrolls = 0
            last_height = new_height

        scroll_count += 1
        if scroll_times is not None and scroll_count >= scroll_times:
            break

    return collected



def extract_emails(text):
    # Regular expression for matching email addresses
    email_regex = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    return re.findall(email_regex, text)




# Remove: import pandas as pd

def save_to_csv(data):
    filename = "emails.csv"
    file_counter = 1
    while os.path.exists(filename):
        filename = f"emails{file_counter}.csv"
        file_counter += 1

    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if data:
            writer.writerow(data[0].keys())  # Headers
            for row in data:
                writer.writerow(row.values())

    return filename




def scrape_tweet_replies(tweet_url):
    print(f"💬 Scraping replies from tweet: {tweet_url}")
    driver = start_driver(headless=False)
    driver.get(tweet_url)

    print("🔐 Please log in and scroll through replies...")
    input("👉 Press Enter here once you're done scrolling and ready to scrape:\n")

    emails = scroll_and_collect(driver)  # Fixed to match the new function
    driver.quit()
    return emails



def scrape_profile(username):
    print(f"📌 Scraping profile: @{username}")
    driver = start_driver(headless=False)
    driver.get(f"https://x.com/{username}")
    time.sleep(5)
    emails = scroll_and_collect(driver, scroll_times=20)
    driver.quit()
    return emails



def collect_tweet_urls(driver, scroll_times):
    print("🔁 Scrolling to collect tweet URLs...")
    tweet_urls = set()
    processed_tweet_ids = set()  # Track processed tweet IDs

    for _ in range(scroll_times):
        time.sleep(3)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(5)

        tweet_elements = driver.find_elements(By.XPATH, '//a[contains(@href, "/status/")]')
        for tweet in tweet_elements:
            try:
                href = tweet.get_attribute("href")
                if href and "/status/" in href:
                    # Clean the URL
                    href = href.split("?")[0].rstrip('/')
                    if href.endswith("/analytics"):
                        href = href.replace("/analytics", "")
                    if href.endswith("/media_tags"):
                        href = href.replace("/media_tags", "")

                    # Extract tweet ID for deduplication

                    # URL format: https://x.com/username/status/1234567890
                    tweet_id = href.split("/status/")[-1].split("/")[0]

                    # Only add if we haven't processed this tweet ID before
                    if tweet_id not in processed_tweet_ids:
                        tweet_urls.add(href)
                        processed_tweet_ids.add(tweet_id)

            except Exception:
                continue

    print(f"✅ Collected {len(tweet_urls)} unique tweet URLs.")
    print(f"📊 Processed {len(processed_tweet_ids)} unique tweet IDs.")
    return list(tweet_urls)


def extract_user_info_from_tweet(driver, tweet_url):
    from urllib.parse import urljoin
    data = {
        "Name": "Unknown",
        "Tweet URL": tweet_url,
        "Email": "Not Available",
        "Contact": "Not Available"
    }

    try:
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC

        # Remove /photo/1 if exists
        if "/photo/" in tweet_url:
            tweet_url = tweet_url.split("/photo/")[0]

        driver.get(tweet_url)
        time.sleep(10)

        # Close popup if visible
        try:
            close_btn = driver.find_element(By.XPATH, '//div[@aria-label="Dismiss"]')
            close_btn.click()
            print("🔕 Closed popup.")
        except:
            pass

        try:
            data["Name"] = driver.find_element(By.XPATH, '//div[@data-testid="User-Name"]//span').text.strip()
        except:
            data["Name"] = "Not Available"
        time.sleep(10)
        try:
            # 1. Try the standard test-id (most common)
            bio = driver.find_element(By.XPATH, '//div[@data-testid="UserDescription"]').text.strip()
        except:
            try:
                # 2. Try a common fallback: directly below the username (within a section)
                bio_section = driver.find_elements(By.XPATH, '//div[@data-testid="UserProfileHeader_Items"]//span')
                bio_texts = [span.text.strip() for span in bio_section if span.text.strip()]
                bio = " ".join(bio_texts) if bio_texts else "Not Available"
            except:
                try:
                    # 3. Try a more general approach from profile main container
                    all_spans = driver.find_elements(By.XPATH, '//section//span')
                    for span in all_spans:
                        text = span.text.strip()
                        if len(text.split()) > 3 and not text.startswith('@'):
                            bio = text
                            break
                    else:
                        bio = "Not Available"
                except:
                    bio = "Not Available"

        print(f"👤 Name: {data['Name']}")
        #print(f"📃 Bio: {bio}")

        # Extract bio
        try:
            #bio = driver.find_element(By.XPATH, '//div[@data-testid="UserDescription"]').text
                full_page_text = driver.find_element(By.TAG_NAME, "body").text

                # Extract email
                email_match = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", full_page_text)
                if email_match:
                    data["Email"] = email_match.group(0)

                time.sleep(10)
                # Extract contact (Pakistani/international formats)
                contact_match = re.search(r"((?:\+9\d{1,3}|\(?0\d{2,4}\)?) ?\d{3,4}(?: ?\d{3,4}){1,2})",full_page_text)
                if contact_match:
                    data["Contact"] = contact_match.group(1)

        except:
            pass
        print(data)

    except Exception as e:
        print(f"❌ Failed to process {tweet_url}: {e}")

    return data

import time
import os


def scrape_hashtag(hashtag,scroll):
    import time
    print(f"📌 Scraping hashtag: #{hashtag}")
    driver,session = start_driver(headless=True)
    #driver.get("https://x.com/login")
    if not check_login_status(driver):
        print("Authentication failed - profile didn't work on Railway")
        driver.quit()
        cleanup_user_session(session)
        raise Exception("Authentication required - please log in manually")
    
    time.sleep(10)
    import time
    import os

    driver.get(f"https://x.com/search?q=%23{hashtag}&src=typed_query")
    time.sleep(5)

    print("🔁 Collecting tweet URLs...")
    tweet_urls = collect_tweet_urls(driver, scroll_times=scroll)
    print(f"✅ Found {len(tweet_urls)} tweet URLs.")

    results = []
    for url in tweet_urls:

        print(f"🔍 Extracting from: {url}")
        info = extract_user_info_from_tweet(driver, url)
        results.append(info)
        time.sleep(15)

    driver.quit()
    cleanup_user_session(session)
    return results
def run_x_scraper(tag,scroll):
    print(f"Environment check:")
    print(f"- Chrome binary exists: {os.path.exists('/usr/bin/google-chrome')}")
    print(f"- ChromeDriver exists: {os.path.exists('/usr/bin/chromedriver')}")
    print(f"- Master profile exists: {os.path.exists('x_scraper_profile')}")
    print(f"- Current directory: {os.getcwd()}")
    print(f"- Directory contents: {os.listdir('.')}")
    emails = scrape_hashtag(tag,scroll)

    print("\n📧 Emails Found:")
    for email in emails:
        print(" -", email)

    filename=save_to_csv(emails)
    print("✅ Done.")
    return filename
