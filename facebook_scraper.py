def run_facebook_scraper(value,scroll):
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager
    from bs4 import BeautifulSoup
    import time
    import csv
    import re
    import os

    # --- Configuration ---
    EMAIL =""
    PASSWORD = ''
    TARGET_URL = value
    SCROLL_COUNT = scroll
    CSV_FILE = 'Facebook'
    print(f"Environment check:")
    print(f"- Chrome binary exists: {os.path.exists('/usr/bin/google-chrome')}")
    print(f"- ChromeDriver exists: {os.path.exists('/usr/bin/chromedriver')}")
    print(f"- Master profile exists: {os.path.exists('facebook_scraper_profile')}")
    print(f"- Current directory: {os.getcwd()}")
    print(f"- Directory contents: {os.listdir('.')}")

    #https://www.facebook.com/dawndotcom/mentions



    # --- Setup Chrome ---

    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options

    options = Options()
     # ⛔ Block notifications popup

    # driver = webdriver.Chrome(options=options)
    # wait = WebDriverWait(driver, 15)
    # import os
    # from webdriver_manager.chrome import ChromeDriverManager
    # user_data_dir = os.path.join(os.getcwd(), "facebook_scraper_profile")
    # # ✅ Persist profile directory so login is saved
    # options.add_argument(f"--user-data-dir={user_data_dir}")
    # options.add_argument("--profile-directory=Default")  # Can change if you want multiple
    # options.add_argument("--disable-notifications")
    # #options.add_argument("--headless=True")
    # options.add_argument("--headless=new")
    #
    # service = Service(ChromeDriverManager().install())
    # driver = webdriver.Chrome(service=service, options=options)

    from selenium.common.exceptions import NoSuchElementException
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    import json
    import uuid
    import time
    import sqlite3
    import shutil
    import threading
    profile_lock = threading.Lock()
    import time

    def start_driver(headless=True, user_session=None):
        """
        Creates a new browser instance by copying the saved profile
        Perfect for multi-user deployment (Railway, etc.)
        Each user gets their own isolated browser with copied cookies
        """

        # Generate unique session ID for this user
        if user_session is None:
            user_session = str(uuid.uuid4())[:8]
        sessionid=user_session
        print(f"Session jo urre ga{sessionid}")
        print(f"🚀 Creating new browser instance for session: {user_session}")

        # Create unique profile directory for this user
        temp_profile_dir = os.path.join(os.getcwd(), "user_profiles", f"user_{user_session}")

        # Copy saved profile to user's unique directory
        with profile_lock:  # Prevent concurrent access issues
            copy_saved_profile_to_user_session(temp_profile_dir)

        # Create browser with copied profile
        driver = create_isolated_browser(temp_profile_dir, headless, user_session)

        return driver,sessionid

    def copy_saved_profile_to_user_session(user_profile_dir):
        """
        Copy the master saved profile to user's unique directory
        This ensures each user gets their own browser instance with same cookies
        """

        master_profile_folder = "facebook_scraper_profile"  # Your saved profile

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
        """
        Create browser instance using user's isolated profile directory
        """

        """
            Create browser instance using user's isolated profile directory
            """
        options = Options()

        if headless:
            options.add_argument("--headless=new")  # Correct headless syntax

        # Essential Chrome options for stability
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-blink-features=AutomationControlled")

        # Memory and process options
        #options.add_argument("--single-process")  # Add this back
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-plugins")
        #options.add_argument("--disable-images")  # Faster loading

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
            chrome_binary_paths = [
                "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",  # Windows
                "/usr/bin/google-chrome",  # Railway Linux
                "/usr/bin/chromium-browser",
                "/opt/google/chrome/chrome"
            ]

            for chrome_path in chrome_binary_paths:
                if os.path.exists(chrome_path):
                    options.binary_location = chrome_path
                    break

            # Use environment variable for chromedriver path
            chromedriver_path = os.environ.get('CHROMEDRIVER_PATH', '/usr/bin/chromedriver')

            if os.path.exists(chromedriver_path):
                service = Service(chromedriver_path)
            else:
                # Fallback to webdriver_manager (works locally)
                service = Service(ChromeDriverManager().install())

            driver = webdriver.Chrome(service=service, options=options)

            # Navigate to Instagram
            print(f"🌐 Navigating to facebook with session {session_id}...")
            driver.get("https://www.facebook.com")
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
                return True
            elif is_login_page:
                print("❌ Redirected to login page - cookies may have expired")
                return False
            else:
                print("⚠️ Login status unclear - checking page elements...")
                # Additional check for navigation elements
                nav_elements = ['search & explore', 'create', 'reels', 'messages']
                if any(element in page_source for element in nav_elements):
                    print("✅ Detected navigation elements - likely logged in")
                    return True

                return False

        except Exception as e:
            print(f"❌ Error checking login: {e}")
            return False

    def cleanup_user_session(session_id):
        try:
           # Kill any browser processes for this session first
           try:
               import psutil
               for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                   if f"user_{session_id}" in str(proc.info.get('cmdline', [])):
                       proc.terminate()
           except ImportError:
               print("psutil not available - skipping process cleanup")


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

    def wait_for_manual_captcha_solution():
        print("⚠️ CAPTCHA detected. Please solve it manually in the browser...")
        input("🔒 Press Enter once you’ve solved the CAPTCHA and the page has loaded.")



    def check_and_handle_login_popup(driver, email, password):
        login_popup_detected = False

        try:
            # Look for email & password input fields (in case of popup or redirect)
            driver.find_element(By.NAME, "email")
            driver.find_element(By.NAME, "pass")
            login_popup_detected = True
        except:
            pass

        if login_popup_detected:
            print("⚠️ Login popup detected after redirect. Attempting to re-login...")

            try:
                email_element = driver.find_element(By.NAME, "email")
                pass_element = driver.find_element(By.NAME, "pass")

                email_element.clear()
                email_element.send_keys(email)

                pass_element.clear()
                pass_element.send_keys(password)
                pass_element.send_keys(Keys.RETURN)

                print("🔁 Re-submitted login credentials...")
                time.sleep(5)  # allow page to reload
            except Exception as e:
                print("❌ Failed to re-login:", e)



    # def facebook_login(email, password):
    #     driver.get("https://www.facebook.com")
    #     wait.until(EC.presence_of_element_located((By.ID, "email"))).send_keys(email)
    #     driver.find_element(By.ID, "pass").send_keys(password)
    #     driver.find_element(By.NAME, "login").click()
    #     time.sleep(5)
    def scroll_page():
        last_height = driver.execute_script("return document.body.scrollHeight")
        for i in range(SCROLL_COUNT):
            time.sleep(10)
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            print(f"🌀 Scrolling... ({i + 1}/{SCROLL_COUNT})")
            time.sleep(3)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                print("⏹️ No more content to load.")
                break
            last_height = new_height

    def normalize_facebook_url(url: str) -> str:
        if "pfbid" in url and "_rdr" not in url:
            if "?" in url:
                return url + "&_rdr"
            else:
                return url + "?_rdr"
        return url





    from selenium.common.exceptions import StaleElementReferenceException
    from selenium.webdriver.common.by import By
    import time
    from selenium.webdriver.common.by import By
    from selenium.common.exceptions import StaleElementReferenceException

    # Alternative approach - Get one representative URL per post collection
    def get_post_urls(driver):
        print("🔍 Collecting unique post URLs (one per post)...")
        time.sleep(5)

        anchors = driver.find_elements(By.XPATH,
                                       '//a[contains(@href, "/videos/") or contains(@href, "/posts/") or contains(@href, "/photo/")]')

        post_urls = []
        seen_post_ids = set()  # Track unique post IDs to avoid duplicates
        i=1

        for a in anchors:
            if(i==1):
                print(i)
                i=i+1
                continue
            try:
                href = a.get_attribute("href")
                if not href:
                    continue

                # Skip unwanted URLs
                if any(s in href for s in
                       ["/groups/", "/watch/", "/live/", "/stories/"]) or "privacy_mutation_token" in href:
                    continue

                post_id = None

                # For URLs with pcb (post collection) - MOST IMPORTANT CASE
                if "pcb." in href:
                    import re
                    pcb_match = re.search(r'pcb\.(\d+)', href)
                    if pcb_match:
                        post_id = f"pcb.{pcb_match.group(1)}"

                # For regular posts
                elif "/posts/" in href:
                    post_id = f"post_{href.split('/posts/')[1].split('?')[0]}"

                # For standalone videos (not part of collections)
                elif "/videos/" in href and "pcb." not in href:
                    post_id = f"video_{href.split('/videos/')[1].split('?')[0]}"

                # For standalone photos (not in collections)
                elif "/photo/" in href and "pcb." not in href:
                    if "fbid=" in href:
                        fbid = href.split("fbid=")[1].split("&")[0]
                        post_id = f"photo_{fbid}"

                # Only add if we haven't seen this post ID before
                if post_id and post_id not in seen_post_ids:
                    seen_post_ids.add(post_id)
                    post_urls.append(href)
                    print(f"📌 Added unique post: {post_id}")
                elif post_id:
                    print(f"🔄 Skipped duplicate: {post_id}")

            except Exception as e:
                print(f"⚠️ Error processing URL: {e}")
                continue

        print(f"✅ Found {len(post_urls)} unique posts from {len(seen_post_ids)} post IDs.")
        return post_urls

    def extract_poster_info():
        name = "Not Available"
        profile_url = "Not Available"
        email = "Not Available"
        contact = "Not Available"
        time.sleep(10)
        try:
            # Try to get name from post header
            name_el = driver.find_element(By.XPATH, '//h2//span//span')
            name = name_el.text.strip()
        except:
            pass

        try:
            profile_link_el = driver.find_element(By.XPATH, '//h2//a[contains(@href,"facebook.com/")]')
            profile_url = profile_link_el.get_attribute('href').split('?')[0]
        except:
            pass

        if "facebook.com" in profile_url:
            try:
                time.sleep(10)
                about_url = profile_url + "/about_contact_and_basic_info"
                driver.get(about_url)
                time.sleep(5)
                driver.execute_script("document.body.style.zoom='67%'")
                time.sleep(5)
                # Now restrict to visible elements only
                import re

                # Search in all elements that might contain the number
                elements = driver.find_elements(By.XPATH,
                                                '//body//*[contains(text(), "+92") or contains(text(), "03") or contains(text(), "(")]')

                contact = "Not Available"
                for el in elements:
                    try:
                        text = el.text.strip()
                        match = re.search(r'(\+92|03)[0-9()\s-]{7,}', text)
                        if match:
                            contact = match.group(0)
                            break
                    except:
                        continue

                # Same for email
                # about_url = profile_url + "/about_contact_and_basic_info"
                # driver.get(about_url)
                # time.sleep(5)
                time.sleep(5)
                page = driver.page_source
                time.sleep(5)
                time.sleep(5)
                email_matches = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', page)
                if email_matches:
                     time.sleep(5)
                     email = email_matches[0]
                time.sleep(5)

            except Exception as e:
                print("⚠️ Error in about section:", e)

        return name, profile_url, email, contact


    def save_to_csv(data):
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        CSV_FILE1 = f"{CSV_FILE}_{timestamp}.csv"

        with open(CSV_FILE1, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Name", "Post URL", "Contact", "Email"])
            for row in data:
                writer.writerow(row)

        return CSV_FILE1

    # --- Main Execution ---
    #facebook_login(EMAIL, PASSWORD)
    time.sleep(3)
    import time
    import os
    driver,session=start_driver(headless=True)
    #driver.get("https://www.facebook.com")


    time.sleep(10)
    driver.get(TARGET_URL)
    time.sleep(10)
    #check_and_handle_login_popup(driver, EMAIL, PASSWORD)

    #time.sleep(10)
    #check_and_handle_login_popup(driver, EMAIL, PASSWORD)
    #time.sleep(10)
    driver.execute_script("document.body.style.zoom='67%'")

    scroll_page()
    try:
        cookie_btn = driver.find_element(By.XPATH, '//button[contains(text(), "Allow essential and optional cookies")]')
        cookie_btn.click()
        print("✅ Cookie banner dismissed")
    except:
        pass



    time.sleep(5)
    post_urls = get_post_urls(driver)


    results = []

    for url in post_urls:
        try:
            print(f"🔗 Opening post: {url}")
            driver.get(normalize_facebook_url(url))
            time.sleep(10)
            try:
                # Try multiple patterns until one works
                name_xpaths = [
                    '//h2//a/span/span',  # Common profile name link
                    '//h2//span//span',  # Older structure
                    '//div[@role="article"]//h2//span//span',  # Scoped to post
                    '//strong//span//span',  # Bolded names
                    '//a[contains(@href, "profile.php") or contains(@href, "/")]//span/span'  # Fallback
                ]

                name = "Not Available"
                for path in name_xpaths:
                    try:
                        name_el = WebDriverWait(driver, 5).until(
                            EC.presence_of_element_located((By.XPATH, path))
                        )
                        name = name_el.text.strip()
                        break  # Stop at first match
                    except:
                        continue

                # Try to click on the post creator's profile
                print("🔎 Attempting to click on poster's name to visit profile...")

                # This XPath usually matches the poster name (can vary — adjust if needed)
                poster_link = driver.find_element(By.XPATH, '//h2//span//a | //strong//a | //h3//a')
                driver.execute_script("arguments[0].click();", poster_link)


                time.sleep(10)  # Wait for profile to load
                driver.execute_script("document.body.style.zoom='60%'")
                time.sleep(10)

                elements = driver.find_elements(By.XPATH, '//a[.//span[text()="About"]]')
                print(f"Found {len(elements)} About elements")

                about_btn = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, '//a[.//span[contains(text(),"About")]]'))
                )
                from selenium.webdriver.common.action_chains import ActionChains

                # Reliable scroll to element using ActionChains
                actions = ActionChains(driver)
                actions.move_to_element(about_btn).perform()
                time.sleep(10)

                # Safer click via JS
                driver.execute_script("arguments[0].click();", about_btn)
                print("✅ Clicked on About tab.")

                time.sleep(5)
                driver.execute_script("document.body.style.zoom='50%'")

                # Now extract email/contact as usual
                about_page = driver.page_source
                email_matches = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',about_page)
                if email_matches:
                    time.sleep(5)
                    email = email_matches[0]
                import re

                # Search in all elements that might contain the number
                elements = driver.find_elements(By.XPATH,
                                                '//body//*[contains(text(), "+9") or contains(text(), "03") or contains(text(), "(04")]')

                contact = "Not Available"
                for el in elements:
                    try:
                        text = el.text.strip()
                        match = re.search(r'(\+92|03)[0-9()\s-]{7,}', text)
                        if match:
                            contact = match.group(0)
                            break
                    except:
                        continue

                email = email_matches[0] if email_matches else "Not Available"
               # contact = contact_matches[0] if contact_matches else "Not Available"
                #print(f"✅ {name} | {email} | {contact}")


            except Exception as e:
                print(f"❌ Couldn't open profile or extract info: {e}")
                email = "Not Available"
                contact = "Not Available"

            time.sleep(3)
           # name, profile_url, email, contact = extract_poster_info()
            time.sleep(5)
            print(f"✅ {name} | {email} | {contact}")
            results.append([name, url, contact, email])
            driver.get("https://web.facebook.com/")
            time.sleep(8)  # Let homepage load
        except Exception as e:
            print(f"❌ Failed on post {url}: {e}")
            results.append(["Not Available", url, "Not Available", "Not Available"])
            driver.get("https://web.facebook.com/")
            time.sleep(8)  # Let homepage load

    CSV_FILE1=save_to_csv(results)
    print(f"💾 Saved {len(results)} records to {CSV_FILE1}")
    cleanup_user_session(session)

    driver.quit()
    return CSV_FILE1


    ###################################################################################
