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
            # Use this for Railway instead:
           # options.add_argument("--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.7258.154 Safari/537.36")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_argument("--disable-extensions")
            options.add_argument("--disable-plugins")
            options.add_argument("--disable-web-security")
            options.add_argument("--allow-running-insecure-content")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
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
                
                print(f"🌐 Navigating to facebook with session {session_id}...")
                driver.get("https://www.facebook.com")
                time.sleep(3)
                sys.stdout.flush() 
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
    def get_facebook_post_count(driver, selectors):
        """Count total posts using multiple selectors"""
        max_count = 0
        for selector in selectors:
            try:
                posts = driver.find_elements(By.CSS_SELECTOR, selector)
                current_count = len(posts)
                max_count = max(max_count, current_count)
            except:
                continue
        return max_count

    def gentle_scroll_facebook(driver):
        """Gentle scrolling that mimics human behavior"""
        try:
            # Method 1: Multiple small scrolls
            viewport_height = driver.execute_script("return window.innerHeight")
            scroll_amount = viewport_height // 3
            
            for i in range(4):
                driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
                time.sleep(random.uniform(1, 3))
            
            # Method 2: Scroll to bottom with smooth behavior
            driver.execute_script("""
                window.scrollTo({
                    top: document.body.scrollHeight,
                    behavior: 'smooth'
                });
            """)
            time.sleep(3)
            
            # Method 3: Trigger focus on feed elements
            try:
                feed_elements = driver.find_elements(By.CSS_SELECTOR, 'div[role="main"], div[role="feed"]')
                if feed_elements:
                    feed_elements[0].click()
            except:
                pass
            
        except Exception as e:
            print(f"   ❌ Error in gentle scroll: {e}")
            # Fallback to basic scroll
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    
    def wait_for_facebook_loading(driver, loading_selectors, timeout=15):
        """Wait for loading indicators to appear"""
        try:
            for selector in loading_selectors:
                try:
                    WebDriverWait(driver, timeout).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    return True
                except TimeoutException:
                    continue
            return False
        except:
            return False
    
    def wait_for_facebook_loading_complete(driver, loading_selectors, timeout=120):
        """Wait for all loading indicators to disappear"""
        print(f"     ⌛ Waiting up to {timeout}s for loading to complete...")
        start_time = time.time()
        last_check_time = start_time
        
        while time.time() - start_time < timeout:
            loading_found = False
            
            # Check for loading indicators
            for selector in loading_selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        loading_found = True
                        break
                except:
                    continue
            
            # Also check for network activity
            try:
                # Check if page is still making requests
                network_active = driver.execute_script("""
                    return window.performance.getEntriesByType('resource')
                        .some(entry => entry.responseEnd === 0);
                """)
                if network_active:
                    loading_found = True
            except:
                pass
            
            if not loading_found:
                # Wait a bit more to ensure stability
                time.sleep(5)
                elapsed = int(time.time() - start_time)
                print(f"     ✅ Loading completed in {elapsed}s")
                return True
            
            # Print status every 30 seconds
            if time.time() - last_check_time > 30:
                elapsed = int(time.time() - start_time)
                print(f"     ⏳ Still loading... ({elapsed}s elapsed)")
                last_check_time = time.time()
                
            time.sleep(3)
        
        print(f"     ⚠️ Loading timeout after {timeout}s")
        return False
    
    def wait_for_new_facebook_posts(driver, post_selectors, current_count, timeout=120):
        """Wait for new posts to appear"""
        print(f"     🔍 Waiting up to {timeout}s for new posts...")
        start_time = time.time()
        last_check_time = start_time
        
        while time.time() - start_time < timeout:
            new_count = get_facebook_post_count(driver, post_selectors)
            
            if new_count > current_count:
                elapsed = int(time.time() - start_time)
                print(f"     ✅ New posts appeared in {elapsed}s")
                return new_count
            
            # Print status every 30 seconds
            if time.time() - last_check_time > 30:
                elapsed = int(time.time() - start_time)
                print(f"     ⏳ Still waiting for posts... ({elapsed}s elapsed, count: {new_count})")
                last_check_time = time.time()
            
            # Check every 5 seconds
            time.sleep(5)
        
        elapsed = int(time.time() - start_time)
        final_count = get_facebook_post_count(driver, post_selectors)
        print(f"     ⏰ No new posts after {elapsed}s (final count: {final_count})")
        return final_count
    
    def try_facebook_alternatives(driver, post_selectors, current_count):
        """Try alternative methods to trigger content loading"""
        print("     🔄 Trying alternative methods...")
        
        try:
            # Method 1: Interact with feed area
            try:
                feed = driver.find_element(By.CSS_SELECTOR, 'div[role="main"], div[role="feed"], #mainContent')
                ActionChains(driver).move_to_element(feed).click().perform()
                time.sleep(3)
            except:
                pass
            
            # Method 2: Multiple scroll techniques
            techniques = [
                "window.scrollTo(0, document.body.scrollHeight - 1000);",
                "window.scrollTo(0, document.body.scrollHeight);",
                "window.scrollBy(0, 500);",
                "window.scrollTo(0, document.documentElement.scrollHeight);"
            ]
            
            for technique in techniques:
                driver.execute_script(technique)
                time.sleep(2)
            
            # Method 3: Trigger events
            driver.execute_script("""
                ['scroll', 'resize', 'focus', 'click'].forEach(eventType => {
                    window.dispatchEvent(new Event(eventType));
                });
            """)
            time.sleep(5)
            
            # Method 4: Focus on last visible posts
            try:
                posts = driver.find_elements(By.CSS_SELECTOR, 'div[role="article"], div[data-pagelet*="FeedUnit"]')
                if len(posts) >= 3:
                    for post in posts[-3:]:
                        try:
                            ActionChains(driver).move_to_element(post).perform()
                            time.sleep(1)
                        except:
                            continue
            except:
                pass
            
            # Method 5: Page Down keys
            try:
                ActionChains(driver).send_keys(Keys.END).perform()
                time.sleep(2)
                for _ in range(3):
                    ActionChains(driver).send_keys(Keys.PAGE_DOWN).perform()
                    time.sleep(1)
            except:
                pass
            
            # Check if any method worked
            time.sleep(10)  # Give time for changes
            new_count = get_facebook_post_count(driver, post_selectors)
            success = new_count > current_count
            
            if success:
                print(f"     ✅ Alternative methods added {new_count - current_count} posts")
            else:
                print("     ❌ Alternative methods didn't help")
                
            return success
            
        except Exception as e:
            print(f"     ❌ Alternative methods failed: {e}")
            return False
    
    def normalize_facebook_url(url: str) -> str:
        """Add the _rdr parameter if needed"""
        if "pfbid" in url and "_rdr" not in url:
            if "?" in url:
                return url + "&_rdr"
            else:
                return url + "?_rdr"
        return url
    
    def scroll_page_facebook_enhanced(driver, scroll_count, timeout_per_scroll=120):
        """
        Enhanced Facebook scrolling optimized for cloud environments like Railway
        """
        print(f"🔵 Starting Facebook-optimized scrolling (max {scroll_count} scrolls)")
        print(f"⏰ Timeout per scroll: {timeout_per_scroll}s")
        sys.stdout.flush()
        
        # Facebook-specific selectors for posts and loading indicators
        POST_SELECTORS = [
            'div[data-pagelet*="FeedUnit"]',  # Main feed posts
            'div[role="article"]',           # Article posts
            'div[data-testid*="story"]',     # Story posts  
            'div[aria-label*="post"]',       # Accessible posts
            '.x1yztbdb',                     # Facebook's dynamic class for posts
            '[data-visualcompletion="ignore-dynamic"]',  # Facebook posts
            'div[data-ft]',                  # Posts with data-ft attribute
            'div[data-testid="fbfeed_story"]' # Feed stories
        ]
        
        LOADING_SELECTORS = [
            'div[aria-label="Loading..."]',
            'div[data-testid="react-loading-skeleton"]',
            '.async_spinner',
            '[role="progressbar"]',
            'div[aria-busy="true"]',
            '.spinner',
            '[data-testid*="loading"]'
        ]
        
        # Initial setup
        print("⏳ Waiting for Facebook page to stabilize...")
        time.sleep(15)  # Let Facebook fully load initially
        
        initial_posts = get_facebook_post_count(driver, POST_SELECTORS)
        print(f"📊 Initial posts detected: {initial_posts}")
        
        successful_scrolls = 0
        consecutive_failures = 0
        last_post_count = initial_posts
        
        for scroll_num in range(scroll_count):
            print(f"\n🌀 Facebook scroll {scroll_num + 1}/{scroll_count}")
            sys.stdout.flush()
            
            try:
                # Step 1: Gentle scroll to trigger loading
                print("   📱 Performing gentle scroll...")
                gentle_scroll_facebook(driver)
                
                # Step 2: Wait for loading indicators
                print("   🔍 Checking for loading indicators...")
                loading_detected = wait_for_facebook_loading(driver, LOADING_SELECTORS, timeout=15)
                
                if loading_detected:
                    print("   ⏳ Loading detected, waiting for completion...")
                    wait_for_facebook_loading_complete(driver, LOADING_SELECTORS, timeout=timeout_per_scroll)
                else:
                    print("   ⚠️ No loading indicators found, using time-based wait...")
                    time.sleep(30)  # Fallback wait
                
                # Step 3: Wait for new posts to appear
                print("   🔍 Checking for new posts...")
                new_post_count = wait_for_new_facebook_posts(
                    driver, POST_SELECTORS, last_post_count, timeout=timeout_per_scroll
                )
                
                if new_post_count > last_post_count:
                    posts_added = new_post_count - last_post_count
                    print(f"   ✅ Success! Added {posts_added} posts ({last_post_count} → {new_post_count})")
                    successful_scrolls += 1
                    consecutive_failures = 0
                    last_post_count = new_post_count
                    
                    # Small pause to let Facebook settle
                    time.sleep(random.uniform(5, 10))
                    
                else:
                    consecutive_failures += 1
                    print(f"   ⚠️ No new posts loaded (failure {consecutive_failures}/3)")
                    
                    if consecutive_failures >= 2:
                        print("   🔧 Trying alternative loading methods...")
                        alternative_success = try_facebook_alternatives(driver, POST_SELECTORS, last_post_count)
                        
                        if alternative_success:
                            new_count = get_facebook_post_count(driver, POST_SELECTORS)
                            if new_count > last_post_count:
                                print(f"   ✅ Alternative method worked! {last_post_count} → {new_count}")
                                successful_scrolls += 1
                                consecutive_failures = 0
                                last_post_count = new_count
                    
                    if consecutive_failures >= 3:
                        print("   ⏹️ Stopping: No new content after multiple attempts")
                        break
                    
                    # Progressive backoff
                    backoff_time = min(20 + (consecutive_failures * 10), 60)
                    print(f"   ⏸️ Backing off for {backoff_time}s...")
                    time.sleep(backoff_time)
            
            except Exception as e:
                print(f"   ❌ Error in scroll {scroll_num + 1}: {str(e)}")
                consecutive_failures += 1
                if consecutive_failures >= 3:
                    break
                time.sleep(15)
        
        final_posts = get_facebook_post_count(driver, POST_SELECTORS)
        total_loaded = final_posts - initial_posts
        
        print(f"\n🏁 Facebook scrolling completed!")
        print(f"📈 Total posts loaded: {total_loaded} ({initial_posts} → {final_posts})")
        print(f"✅ Successful scrolls: {successful_scrolls}/{scroll_count}")
        sys.stdout.flush()
        
        
    
    
            
            # last_height = driver.execute_script("return document.body.scrollHeight")
            # for i in range(SCROLL_COUNT):
            #     driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            #     print(f"🌀 Scrolling... ({i + 1}/{SCROLL_COUNT})")
            #     time.sleep(50)
            #     new_height = driver.execute_script("return document.body.scrollHeight")
            #     time.sleep(10)
            #     if new_height == last_height:
            #         print("⏹️ No more content to load.")
            #         sys.stdout.flush() 
            #         #break
            #     last_height = new_height
            
        #     """
        #     Enhanced scrolling function optimized for cloud environments
            
        #     Args:
        #         driver: Selenium WebDriver instance
        #         scroll_count: Maximum number of scrolls to perform
        #         base_wait: Base wait time between scrolls
        #         max_wait: Maximum wait time for content to load
        #     """
        #     base_wait=15
        #     max_wait=45
        #     print(f"🚀 Starting enhanced scrolling (max {SCROLL_COUNT} scrolls)")
        #     sys.stdout.flush()
            
        #     last_height = driver.execute_script("return document.body.scrollHeight")
        #     successful_scrolls = 0
        #     consecutive_no_change = 0
            
        #     for i in range(SCROLL_COUNT):
        #         try:
        #             print(f"🌀 Scroll attempt {i + 1}/{SCROLL_COUNT}")
        #             sys.stdout.flush()
                    
        #             # Scroll to bottom with smooth behavior
        #             driver.execute_script("""
        #                 window.scrollTo({
        #                     top: document.body.scrollHeight,
        #                     behavior: 'smooth'
        #                 });
        #             """)
                    
        #             # Wait for initial scroll to complete
        #             time.sleep(2)
                    
        #             # Check for loading indicators and wait for them to disappear
        #             loading_selectors = [
        #                 '[data-testid*="loading"]',
        #                 '.loading',
        #                 '.spinner',
        #                 '[aria-label*="Loading"]',
        #                 '.skeleton',
        #                 '[class*="loading"]',
        #                 '[class*="spinner"]'
        #             ]
                    
        #             wait_time = base_wait
        #             content_loaded = False
                    
        #             # Dynamic waiting with multiple strategies
        #             for attempt in range(3):
        #                 print(f"   ⏳ Waiting for content... (attempt {attempt + 1}/3)")
        #                 sys.stdout.flush()
                        
        #                 # Strategy 1: Wait for loading indicators to disappear
        #                 try:
        #                     for selector in loading_selectors:
        #                         WebDriverWait(driver, 2).until_not(
        #                             EC.presence_of_element_located((By.CSS_SELECTOR, selector))
        #                         )
        #                 except TimeoutException:
        #                     pass  # No loading indicators found or they didn't disappear
                        
        #                 # Strategy 2: Wait for network idle (no new requests for 2 seconds)
        #                 try:
        #                     driver.execute_script("""
        #                         return new Promise((resolve) => {
        #                             let requestCount = 0;
        #                             let lastRequestTime = Date.now();
                                    
        #                             const observer = new PerformanceObserver((list) => {
        #                                 requestCount++;
        #                                 lastRequestTime = Date.now();
        #                             });
        #                             observer.observe({entryTypes: ['resource']});
                                    
        #                             const checkIdle = () => {
        #                                 if (Date.now() - lastRequestTime > 2000) {
        #                                     observer.disconnect();
        #                                     resolve(true);
        #                                 } else {
        #                                     setTimeout(checkIdle, 500);
        #                                 }
        #                             };
                                    
        #                             setTimeout(() => {
        #                                 observer.disconnect();
        #                                 resolve(false);
        #                             }, 10000);
                                    
        #                             checkIdle();
        #                         });
        #                     """)
        #                     time.sleep(2)
        #                 except:
        #                     pass
                        
        #                 # Strategy 3: Check if page height changed
        #                 current_height = driver.execute_script("return document.body.scrollHeight")
        #                 if current_height > last_height:
        #                     content_loaded = True
        #                     break
                        
        #                 # Progressive wait time increase
        #                 time.sleep(min(wait_time + (attempt * 5), max_wait))
                    
        #             # Final height check
        #             new_height = driver.execute_script("return document.body.scrollHeight")
                    
        #             if new_height > last_height:
        #                 print(f"   ✅ New content loaded! Height: {last_height} → {new_height}")
        #                 successful_scrolls += 1
        #                 consecutive_no_change = 0
        #                 last_height = new_height
        #             else:
        #                 consecutive_no_change += 1
        #                 print(f"   ⚠️ No new content detected (attempt {consecutive_no_change}/3)")
                        
        #                 # Try alternative scroll methods if no content is loading
        #                 if consecutive_no_change >= 2:
        #                     print("   🔄 Trying alternative scroll methods...")
                            
        #                     # Method 1: Scroll by viewport height increments
        #                     viewport_height = driver.execute_script("return window.innerHeight")
        #                     for scroll_step in range(3):
        #                         driver.execute_script(f"window.scrollBy(0, {viewport_height});")
        #                         time.sleep(2)
                            
        #                     # Method 2: Trigger scroll events manually
        #                     driver.execute_script("""
        #                         window.dispatchEvent(new Event('scroll'));
        #                         window.dispatchEvent(new Event('resize'));
        #                     """)
        #                     time.sleep(3)
                            
        #                     # Method 3: Focus on different elements to trigger lazy loading
        #                     try:
        #                         elements = driver.find_elements(By.CSS_SELECTOR, "div, article, section")
        #                         if elements:
        #                             random.choice(elements[-10:]).click()
        #                             time.sleep(2)
        #                     except:
        #                         pass
                            
        #                     # Check again after alternative methods
        #                     final_height = driver.execute_script("return document.body.scrollHeight")
        #                     if final_height > new_height:
        #                         print(f"   ✅ Alternative method worked! Height: {new_height} → {final_height}")
        #                         successful_scrolls += 1
        #                         consecutive_no_change = 0
        #                         last_height = final_height
                            
        #                 # Break if no content for 3 consecutive attempts
        #                 if consecutive_no_change >= 3:
        #                     print("   ⏹️ No more content to load after multiple attempts.")
        #                     break
                    
        #             sys.stdout.flush()
                    
        #         except Exception as e:
        #             print(f"   ❌ Error during scroll {i + 1}: {str(e)}")
        #             consecutive_no_change += 1
        #             if consecutive_no_change >= 3:
        #                 break
        #             time.sleep(5)
            
        #     print(f"🏁 Scrolling completed! Successful scrolls: {successful_scrolls}/{scroll_count}")
        #     sys.stdout.flush()
    
        # def normalize_facebook_url(url: str) -> str:
        #     if "pfbid" in url and "_rdr" not in url:
        #         if "?" in url:
        #             return url + "&_rdr"
        #         else:
        #             return url + "?_rdr"
        #     return url
    
    



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
        scroll_page_facebook_enhanced(driver, SCROLL_COUNT)
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
