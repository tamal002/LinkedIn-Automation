from playwright.sync_api import sync_playwright, TimeoutError
import time
import random
import re
import json

def run_linkedin_login_and_search(email, password, domain):
    """
    Logs into LinkedIn and searches for people in a domain.
    Returns list of unique profile URLs.
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        try:
            print("Opening LinkedIn login page...")
            page.goto("https://www.linkedin.com/login",  wait_until="networkidle")

            print("Filling email and password...")
            page.fill("input#username", email)
            page.fill("input#password", password)
            page.click("button[type='submit']")
            print("Waiting for login to complete or manual OTP")
            # Wait for either feed or search page
            try:
                page.wait_for_url("https://www.linkedin.com/feed/",  timeout=15000)
                print("✅ Login successful - redirected to feed")
            except:
                try:
                    page.wait_for_url("**/search/**", timeout=5000)
                    print("✅ Already on search results page")
                except:
                    print("⚠️ Manual verification may be required - waiting 10 seconds...")
                    page.wait_for_timeout(10000)

            # Navigate to search results
            search_url = f"https://www.linkedin.com/search/results/people/?keywords={domain}"
            print(f"Searching for '{domain}' at {search_url}...")
            page.goto(search_url, wait_until="networkidle")
            page.wait_for_timeout(3000)

            if "search/results/people" not in page.url:
                print("🔄 Trying alternative navigation...")
                page.goto(f"https://www.linkedin.com/search/results/all/?keywords={domain}")
                page.wait_for_timeout(2000)

                # Try clicking the People filter 
                try:
                    people_filter = page.query_selector("button[aria-label*='People']")
                    if people_filter:
                        people_filter.click()
                        page.wait_for_timeout(3000)
                        print("✅ Clicked 'People' filter")
                    else:
                        people_filter = page.query_selector("//button[contains(text(), 'People')]")
                        if people_filter:
                            people_filter.click()
                            page.wait_for_timeout(3000)
                            print("✅ Clicked 'People' filter (fallback selector)")
                except Exception as e:
                    print("⚠️ Could not click 'People' filter:", e)

            # Take screenshot for debugging
            try:
                page.screenshot(path="debug_search_page.png", full_page=True)
                print("📸 Screenshot saved as debug_search_page.png")
            except Exception as e:
                print("📷 Failed to take screenshot:", e)

            # Wait for results container
            search_result_selectors = [
                ".search-results-container",
                ".search-results",
                "[data-chameleon-result-urn]",
                ".entity-result",
                ".search-result",
                ".reusable-search-simple-insight"
            ]
            results_found = False
            for selector in search_result_selectors:
                try:
                    page.wait_for_selector(selector, timeout=5000)
                    print(f"✅ Found results using selector: {selector}")
                    results_found = True
                    break
                except:
                    continue

            if not results_found:
                print("❌ No results found on this page")
                try:
                    page_html = page.content()
                    with open("debug_no_results.html", "w", encoding="utf-8") as f:
                        f.write(page_html)
                    print("💾 Page HTML saved for inspection")
                except Exception as e:
                    print("📄 Failed to save page HTML:", e)

            # Scroll to load more results
            print("Scrolling to load more results...")
            for i in range(3):
                print(f"Scroll {i+1}/3...")
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                page.wait_for_timeout(2000)

            # Extract profile links
            all_links = page.query_selector_all("a[href]")
            profile_links = set()

            for link in all_links:
                try:
                    href = link.get_attribute('href')
                    if not href:
                        continue
                    if href.startswith('/'):
                        href = f"https://www.linkedin.com{href}" 
                    clean_url = href.split('?')[0].split('#')[0]

                    # Validate it's a proper profile URL
                    if re.match(r'https://[^/]*linkedin\.com/in/[^/]+/?$', clean_url):
                        if not any(exclude in clean_url.lower() for exclude in ['company', 'school', 'showcase']):
                            profile_links.add(clean_url)
                except:
                    continue

            profile_list = list(profile_links)
            print(f"✅ Found {len(profile_list)} unique profile(s)")

            return profile_list

        except Exception as e:
            print(f"❌ Unexpected error during search: {e}")
            try:
                page.screenshot(path="debug_error_screenshot.png")
                print("📸 Saved error screenshot")
            except:
                pass
            return []
        finally:
            context.close()
            browser.close()


def send_linkedin_invites(email, password, profile_list, domain="AI", message_template=None):
    if message_template is None:
        message_template = "Hi there! I noticed your work in {{domain}} and wanted to connect."

    personalized_message = message_template.replace("{{domain}}", domain)
    sent_profiles = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 720}
        )
        page = context.new_page()

        try:
            print("Logging in to LinkedIn...")
            page.goto("https://www.linkedin.com/login", wait_until="networkidle")
            page.fill("input#username", email)
            page.fill("input#password", password)
            page.click("button[type='submit']")
            page.wait_for_timeout(10000)

            if "login" in page.url:
                raise Exception("Login failed or redirected back to login.")

            for idx, profile_url in enumerate(profile_list, start=1):
                profile_url = profile_url['url'] if isinstance(profile_url, dict) else profile_url

                print(f"[{idx}/{len(profile_list)}] Visiting {profile_url}")
                page.goto(profile_url, wait_until="networkidle")
                time.sleep(random.uniform(3, 6))
                page.screenshot(path=f"debug_profile_{idx}.png")

                try:
                    connect_button = page.locator("button[aria-label='Connect']")
                    if not connect_button.is_visible():
                        more_button = page.locator("button:has-text('More')")
                        if more_button.is_visible():
                            more_button.click()
                            time.sleep(1)
                            connect_button = page.locator("div[role='menu'] button:has-text('Connect')")

                    if connect_button.is_visible():
                        connect_button.click()
                        time.sleep(random.uniform(2, 4))

                        try:
                            add_note_button = page.locator("button[aria-label='Add a note']")
                            if add_note_button.is_visible():
                                add_note_button.click()
                                time.sleep(2)
                                page.fill("textarea[name='message']", personalized_message)
                                print("📝 Note added")
                        except:
                            print("⚠️ Could not add note (may not be available)")

                        send_button = page.locator("button:has-text('Send')")
                        if send_button.is_visible():
                            send_button.click()
                            print("🚀 Invite sent")
                            sent_profiles.append({'url': profile_url, 'status': 'Sent'})
                        else:
                            print("❌ Send button not found")
                            sent_profiles.append({'url': profile_url, 'status': 'Failed - Send Button Missing'})
                    else:
                        print("❌ Connect button not visible")
                        sent_profiles.append({'url': profile_url, 'status': 'Failed - No Connect Button'})

                except TimeoutError:
                    print(f"⏰ Timeout while sending invite to {profile_url}")
                    sent_profiles.append({'url': profile_url, 'status': 'Failed - Timeout'})
                except Exception as e:
                    print(f"❌ Error sending invite to {profile_url}: {e}")
                    sent_profiles.append({'url': profile_url, 'status': 'Failed - General Error'})

                time.sleep(random.uniform(5, 8))

        except Exception as e:
            print(f"❌ Critical error in automation: {e}")
            sent_profiles.append({'url': 'System Error', 'status': str(e)})
        finally:
            context.close()
            browser.close()

    return sent_profiles


# def send_linkedin_invites(email, password, profile_list, domain="AI", message_template=None):
#     """
#     Log into LinkedIn and send invites to list of profile URLs
#     Returns list of sent profiles with status
#     """
#     if message_template is None:
#         message_template = "Hi there! I noticed your work in {{domain}} and wanted to connect."

#     personalized_message = message_template.replace("{{domain}}", domain)

#     sent_profiles = []

#     with sync_playwright() as p:
#         browser = p.chromium.launch(headless=False)
#         context = browser.new_context(
#             user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
#         )
#         page = context.new_page()

#         try:
#             print("Logging in to LinkedIn...")
#             page.goto("https://www.linkedin.com/feed/", wait_until="networkidle")
#             page.wait_for_timeout(3000)

#             # Check if already logged in 
#             if "login" in page.url:
#                 print("🔄 Need to log in again...")
#                 page.fill("input#username", email)
#                 page.fill("input#password", password)
#                 page.click("button[type='submit']")
#                 print("✅ Logging in with provided credentials")
#                 page.wait_for_timeout(10000)  # Wait for OTP or login

#             # Loop through each profile and send invite
#             for idx, profile in enumerate(profile_list, start=1):
#                 profile_url = profile['url'] if isinstance(profile, dict) else profile

#                 print(f"[{idx}/{len(profile_list)}] Visiting {profile_url}")
#                 page.goto(profile_url, wait_until="networkidle")
#                 time.sleep(random.uniform(3, 6))

#                 try:
#                     # Find and click Connect button
#                     connect_button = page.locator("button[aria-label='Connect']")
#                     if connect_button.is_visible(timeout=5000):
#                         connect_button.click()
#                         print("✅ Connect button clicked")
#                         time.sleep(random.uniform(2, 4))

#                         # Add custom note
#                         add_note_button = page.locator("button[aria-label='Add a note']")
#                         if add_note_button.is_visible():
#                             add_note_button.click()
#                             time.sleep(2)
#                             page.fill(".send-invite__custom-message", personalized_message)
#                             print("📝 Note added")

#                         # Send invite
#                         send_button = page.locator("button[aria-label='Send without a note']")
#                         if send_button.is_visible():
#                             send_button.click()
#                             print("🚀 Invite sent")
#                             sent_profiles.append({'url': profile_url, 'status': 'Sent'})
#                         else:
#                             print("❌ Send button not found")
#                             sent_profiles.append({'url': profile_url, 'status': 'Failed - Send Button Missing'})

#                     else:
#                         print("❌ Connect button not found")
#                         sent_profiles.append({'url': profile_url, 'status': 'Failed - No Connect Button'})

#                 except TimeoutError:
#                     print(f"⏰ Timeout while sending invite to {profile_url}")
#                     sent_profiles.append({'url': profile_url, 'status': 'Failed - Timeout'})
#                 except Exception as e:
#                     print(f"❌ Error sending invite to {profile_url}: {e}")
#                     sent_profiles.append({'url': profile_url, 'status': 'Failed - General Error'})

#                 # Random delay between invites
#                 time.sleep(random.uniform(5, 8))

#         except Exception as e:
#             print(f"❌ Critical error in automation: {e}")
#             sent_profiles.append({'url': 'System Error', 'status': str(e)})
#         finally:
#             context.close()
#             browser.close()

#     return sent_profiles