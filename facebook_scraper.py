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
    import sys
    import json
    import random

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



    # --- Setup Chrome --
    
    from selenium.common.exceptions import NoSuchElementException

    import json
    import uuid
    import time
    import sqlite3
    import shutil
    import threading
    profile_lock = threading.Lock()
    import time

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
            sys.stdout.flush() 
            return True
    
        except Exception as e:
            print(f"❌ Error loading {platform} cookies: {e}")
            return False
    
    
    
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
        #with profile_lock:  # Prevent concurrent access issues
          #  copy_saved_profile_to_user_session(temp_profile_dir)
    
        # Create browser with copied profile
        driver = create_isolated_browser(temp_profile_dir, headless, user_session)
    
        return driver,session
    
    def create_isolated_browser(user_profile_dir, headless, session_id):
        options = Options()
        if headless:
            options.add_argument("--headless=new")
        
        # Essential Chrome options for Railway
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        
        # CRITICAL: Remove these lines that break JavaScript execution
        # options.add_argument("--disable-extensions")  # REMOVED - can break JS
        # options.add_argument("--disable-plugins")     # REMOVED - can break JS
        # options.add_argument("--disable-web-security") # REMOVED - breaks modern web apps
        # options.add_argument("--disable-features=VizDisplayCompositor") # REMOVED
        
        # Keep these for anti-detection
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # CRITICAL: Enable JavaScript properly
        options.add_argument("--enable-javascript")
        options.add_argument("--enable-automation")  # Needed for proper JS execution
        
        # Allow Facebook's features to work
        options.add_argument("--allow-running-insecure-content")
        
        # Better performance for JavaScript-heavy sites
        options.add_argument("--max_old_space_size=4096")
        options.add_argument("--disable-background-timer-throttling")
        options.add_argument("--disable-backgrounding-occluded-windows")
        options.add_argument("--disable-renderer-backgrounding")
        
        # Set proper user agent
       # options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebDriver/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        # Use user's isolated profile
        options.add_argument(f"--user-data-dir={os.path.abspath(user_profile_dir)}")
        options.add_argument("--profile-directory=Default")
        
        # Set Chrome binary location for Railway
        options.binary_location = "/usr/bin/google-chrome-stable"
        
        try:
            # For Railway/Linux - use the installed ChromeDriver
            service = Service("/usr/bin/chromedriver")
            driver = webdriver.Chrome(service=service, options=options)
            
            # CRITICAL: Set proper timeouts for JavaScript execution
            driver.set_page_load_timeout(120)  # 2 minutes for initial load
            driver.implicitly_wait(10)         # 10 seconds for element finding
            
            # Set window size (helps with lazy loading detection)
            driver.set_window_size(1920, 1080)
            
            print(f"🌐 Navigating to facebook with session {session_id}...")
            driver.get("https://www.facebook.com")
            
            # Wait for Facebook's JavaScript to initialize
            time.sleep(10)
            
            # Test if JavaScript is working
            try:
                js_test = driver.execute_script("return typeof window.jQuery !== 'undefined' || typeof window.React !== 'undefined' || document.readyState === 'complete';")
                print(f"✅ JavaScript execution test: {js_test}")
            except Exception as e:
                print(f"⚠️ JavaScript test failed: {e}")
            
            sys.stdout.flush() 
            return driver
            
        except Exception as e:
            print(f"❌ Failed to create driver: {e}")
            # Fallback to webdriver_manager for local development
            try:
                service = Service(ChromeDriverManager().install())
                driver = webdriver.Chrome(service=service, options=options)
                driver.set_page_load_timeout(120)
                driver.implicitly_wait(10)
                driver.set_window_size(1920, 1080)
                driver.get("https://www.facebook.com")
                time.sleep(10)
                return driver
            except Exception as e2:
                print(f"❌ Fallback also failed: {e2}")
                raise e2
    

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
                email_element = driver.find_element(By.NAME, "itsghufranqayyum@gmail.com")
                pass_element = driver.find_element(By.NAME, "ghufran786")

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
        """
        Simple Facebook scrolling with verification
        """
        print(f"Starting Facebook scrolling ({SCROLL_COUNT} scrolls)")
        
        # Check initial state
        initial_height = driver.execute_script("return document.body.scrollHeight")
        initial_posts = len(driver.find_elements(By.CSS_SELECTOR, 'div[role="article"], div[data-pagelet*="FeedUnit"]'))
        print(f"Initial: height={initial_height}, posts={initial_posts}")
        
        # Wait for page to stabilize
        time.sleep(8)
        
        for i in range(SCROLL_COUNT):
            try:
                print(f"Scroll {i+1}/{SCROLL_COUNT}")
                
                # Get current state
                current_height = driver.execute_script("return document.body.scrollHeight")
                
                # Scroll using multiple methods
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                
                # Alternative scroll method
                driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
                time.sleep(2)
                
                # Trigger scroll events to activate lazy loading
                driver.execute_script("""
                    window.dispatchEvent(new Event('scroll'));
                    window.dispatchEvent(new Event('resize'));
                """)
                
                # Wait for content to load
                time.sleep(10)
                
                # Check if height changed
                new_height = driver.execute_script("return document.body.scrollHeight")
                new_posts = len(driver.find_elements(By.CSS_SELECTOR, 'div[role="article"], div[data-pagelet*="FeedUnit"]'))
                
                if new_height > current_height:
                    print(f"  ✅ Height increased: {current_height} → {new_height}, Posts: {new_posts}")
                else:
                    print(f"  ⚠️ Height unchanged: {current_height}, Posts: {new_posts}")
                
                sys.stdout.flush()
                    
            except Exception as e:
                print(f"Scroll {i+1} failed: {str(e)}")
                time.sleep(5)  # Brief pause before continuing
        
        final_height = driver.execute_script("return document.body.scrollHeight")
        final_posts = len(driver.find_elements(By.CSS_SELECTOR, 'div[role="article"], div[data-pagelet*="FeedUnit"]'))
        
        print(f"Scrolling completed!")
        print(f"Final: height={final_height} (+{final_height-initial_height}), posts={final_posts} (+{final_posts-initial_posts})")
        sys.stdout.flush()
        
        return SCROLL_COUNT
        
    def normalize_facebook_url(url: str) -> str:
        """Add the _rdr parameter if needed"""
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

        for a in anchors:
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
    sys.stdout.flush() 
    driver.get("https://www.facebook.com")
    load_cookies_into_browser(driver,"facebook")
    sys.stdout.flush() 
    # check_login_status(driver)
    # sys.stdout.flush() 

    time.sleep(10)
    driver.get(TARGET_URL)
    sys.stdout.flush() 

    check_and_handle_login_popup(driver, EMAIL, PASSWORD)

    #time.sleep(10)
    #check_and_handle_login_popup(driver, EMAIL, PASSWORD)
    time.sleep(10)
    print("🔵 Waiting for Facebook page to fully stabilize...")
    time.sleep(20)  # Let Facebook completely load
    sys.stdout.flush() 
    try:
        time.sleep(10)
        initial_posts = len(driver.find_elements(By.CSS_SELECTOR, 'div[role="article"]'))
        print(f"📊 After additional wait: {initial_posts} posts")
        scroll_page()
        sys.stdout.flush() 
    except Exception as e:
        print(f"❌ Error during scrolling: {e}")
        print("🔄 Continuing with available posts...")
    
    # try:
    #     cookie_btn = driver.find_element(By.XPATH, '//button[contains(text(), "Allow essential and optional cookies")]')
    #     cookie_btn.click()
    #     print("✅ Cookie banner dismissed")
    # except:
    #     pass



    time.sleep(5)
    post_urls = get_post_urls(driver)
    sys.stdout.flush() 

    results = []

    for url in post_urls:
        try:
            print(f"🔗 Opening post: {url}")
            driver.get(normalize_facebook_url(url))
            sys.stdout.flush() 
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
                sys.stdout.flush() 
                
                time.sleep(10)
                driver.execute_script("document.body.style.zoom='50%'")
                time.sleep(10)
    

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
            sys.stdout.flush() 
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
