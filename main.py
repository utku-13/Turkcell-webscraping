import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.keys import Keys

class TurkcellReviewScraper:
    def __init__(self):
        self.driver = None
        self.wait = None
        self.setup_driver()
    
    def setup_driver(self):
        """Setup Chrome driver with optimal settings"""
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        self.wait = WebDriverWait(self.driver, 15)
    
    def search_turkcell_locations(self):
        """Search for Turkcell on Google Maps and get first 3 locations"""
        print("🔍 Searching for Turkcell locations on Google Maps...")
        
        # Go to Google Maps
        self.driver.get("https://www.google.com/maps")
        time.sleep(random.uniform(2, 4))
        
        # Search for Turkcell
        search_box = self.wait.until(EC.element_to_be_clickable((By.ID, "searchboxinput")))
        search_box.clear()
        search_box.send_keys("turkcell")
        search_box.send_keys(Keys.RETURN)
        
        # Wait for results to load
        time.sleep(random.uniform(3, 5))
        
        # Get the first 3 location links
        locations = []
        try:
            # Wait for search results
            self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "[role='article']")))
            
            # Find location elements
            location_elements = self.driver.find_elements(By.CSS_SELECTOR, "[role='article'] a[href*='/maps/place/']")[:3]
            
            for i, element in enumerate(location_elements):
                try:
                    location_name = element.find_element(By.CSS_SELECTOR, "[role='heading']").text
                    location_url = element.get_attribute('href')
                    locations.append({
                        'name': location_name,
                        'url': location_url,
                        'index': i + 1
                    })
                    print(f"✅ Found location {i+1}: {location_name}")
                except Exception as e:
                    print(f"❌ Error getting location {i+1}: {e}")
                    
        except TimeoutException:
            print("❌ Timeout waiting for search results")
            
        return locations
    
    def get_location_reviews(self, location):
        """Get reviews for a specific location"""
        print(f"\n📍 Getting reviews for: {location['name']}")
        
        try:
            # Navigate to location
            self.driver.get(location['url'])
            time.sleep(random.uniform(3, 5))
            
            # Click on reviews tab
            try:
                reviews_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(@data-tab-index, '1')]")))
                reviews_button.click()
                time.sleep(random.uniform(2, 4))
            except:
                # Try alternative selector for reviews
                try:
                    reviews_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Yorumlar') or contains(@aria-label, 'Yorumlar')]")))
                    reviews_button.click()
                    time.sleep(random.uniform(2, 4))
                except:
                    print("❌ Could not find reviews button")
                    return []
            
            # Sort by newest (if available)
            try:
                sort_button = self.driver.find_element(By.XPATH, "//button[contains(@data-value, 'Sort')]")
                sort_button.click()
                time.sleep(1)
                newest_option = self.driver.find_element(By.XPATH, "//div[contains(text(), 'En yeni') or contains(text(), 'Newest')]")
                newest_option.click()
                time.sleep(random.uniform(2, 3))
            except:
                print("⚠️  Could not sort by newest, using default order")
            
            # Scroll to load more reviews
            self.scroll_to_load_reviews()
            
            # Extract reviews
            reviews = self.extract_reviews()
            
            return reviews[:10]  # Return top 10
            
        except Exception as e:
            print(f"❌ Error getting reviews for {location['name']}: {e}")
            return []
    
    def scroll_to_load_reviews(self):
        """Scroll down to load more reviews"""
        print("📜 Loading reviews...")
        
        try:
            # Find scrollable reviews container
            scrollable_div = self.driver.find_element(By.CSS_SELECTOR, "[role='main']")
            
            last_height = self.driver.execute_script("return arguments[0].scrollHeight", scrollable_div)
            scroll_attempts = 0
            max_scrolls = 5  # Limit scrolling to prevent infinite loops
            
            while scroll_attempts < max_scrolls:
                # Scroll down
                self.driver.execute_script("arguments[0].scrollTo(0, arguments[0].scrollHeight);", scrollable_div)
                time.sleep(random.uniform(2, 3))
                
                # Calculate new scroll height
                new_height = self.driver.execute_script("return arguments[0].scrollHeight", scrollable_div)
                
                if new_height == last_height:
                    break
                    
                last_height = new_height
                scroll_attempts += 1
                
        except Exception as e:
            print(f"⚠️  Error while scrolling: {e}")
    
    def extract_reviews(self):
        """Extract review data from the page"""
        reviews = []
        
        try:
            # Find all review elements
            review_elements = self.driver.find_elements(By.CSS_SELECTOR, "[data-review-id]")
            
            for review_element in review_elements:
                try:
                    # Extract reviewer name
                    name_element = review_element.find_element(By.CSS_SELECTOR, "[role='button']")
                    reviewer_name = name_element.get_attribute('aria-label') or name_element.text
                    
                    # Extract rating
                    try:
                        rating_element = review_element.find_element(By.CSS_SELECTOR, "[role='img'][aria-label*='star']")
                        rating_text = rating_element.get_attribute('aria-label')
                        rating = rating_text.split()[0] if rating_text else "No rating"
                    except:
                        rating = "No rating"
                    
                    # Extract review text
                    try:
                        # Try to click "more" button if it exists
                        more_button = review_element.find_element(By.CSS_SELECTOR, "button[aria-label*='daha fazla']")
                        more_button.click()
                        time.sleep(0.5)
                    except:
                        pass
                    
                    try:
                        text_element = review_element.find_element(By.CSS_SELECTOR, "[data-expandable-text]")
                        review_text = text_element.text
                    except:
                        try:
                            text_element = review_element.find_element(By.CSS_SELECTOR, "span[role='text']")
                            review_text = text_element.text
                        except:
                            review_text = "No text available"
                    
                    if reviewer_name and reviewer_name.strip():
                        reviews.append({
                            'reviewer_name': reviewer_name,
                            'rating': rating,
                            'text': review_text
                        })
                        
                except Exception as e:
                    print(f"⚠️  Error extracting individual review: {e}")
                    continue
                    
        except Exception as e:
            print(f"❌ Error finding review elements: {e}")
            
        return reviews
    
    def print_reviews(self, location, reviews):
        """Print reviews in a formatted way"""
        print(f"\n{'='*60}")
        print(f"📍 LOCATION: {location['name']}")
        print(f"{'='*60}")
        
        if not reviews:
            print("❌ No reviews found for this location")
            return
            
        for i, review in enumerate(reviews, 1):
            print(f"\n--- Review {i} ---")
            print(f"👤 Reviewer: {review['reviewer_name']}")
            print(f"⭐ Rating: {review['rating']}")
            print(f"💬 Text: {review['text'][:200]}{'...' if len(review['text']) > 200 else ''}")
            print("-" * 40)
    
    def run(self):
        """Main execution method"""
        try:
            print("🚀 Starting Turkcell Google Maps Review Scraper")
            
            # Search for locations
            locations = self.search_turkcell_locations()
            
            if not locations:
                print("❌ No locations found")
                return
                
            print(f"\n✅ Found {len(locations)} locations")
            
            # Get reviews for each location
            for location in locations:
                reviews = self.get_location_reviews(location)
                self.print_reviews(location, reviews)
                
                # Add delay between locations
                time.sleep(random.uniform(3, 5))
                
        except Exception as e:
            print(f"❌ Fatal error: {e}")
        finally:
            if self.driver:
                print("\n🔄 Closing browser...")
                self.driver.quit()

if __name__ == "__main__":
    scraper = TurkcellReviewScraper()
    scraper.run()
