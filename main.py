from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import time
import csv
import os

url_1 = "https://www.google.com/maps/place/Pera+Turkcell+%C4%B0leti%C5%9Fim+Merkezi/@41.0359664,28.975326,16z/data=!4m12!1m2!2m1!1sturkcell+taksim!3m8!1s0x14cab9e00b444573:0xae4d363847ab0b6b!8m2!3d41.0310797!4d28.9757005!9m1!1b1!15sCg90dXJrY2VsbCB0YWtzaW0iA4gBAVoRIg90dXJrY2VsbCB0YWtzaW2SASN0ZWxlY29tbXVuaWNhdGlvbnNfc2VydmljZV9wcm92aWRlcqoBYAoNL2cvMTFjMmtjaG5oMQoJL20vMDcybHhnEAEqDCIIdHVya2NlbGwoITIfEAEiG-52ldX8Y5PJfAxuqT3Vo3BGHt1tpp9_55l__DITEAIiD3R1cmtjZWxsIHRha3NpbeABAA!16s%2Fg%2F11b6_x5ql6?entry=ttu&g_ep=EgoyMDI1MDYyNi4wIKXMDSoASAFQAw%3D%3D"

def setup_driver():
    """Set up Chrome WebDriver with basic options"""
    chrome_options = Options()
    
    # Add some useful options
    chrome_options.add_argument("--start-maximized")  # Start maximized
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # Optional: Add headless mode (uncomment if you want to run without GUI)
    # chrome_options.add_argument("--headless")
    
    # Set up the service with WebDriverManager
    service = Service(ChromeDriverManager().install())
    
    # Create and return the driver
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # Execute script to remove webdriver property
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    return driver

def load_existing_reviewers(filename):
    """Load existing reviewer names from CSV file"""
    existing_reviewers = set()
    if os.path.exists(filename):
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    existing_reviewers.add(row['reviewer_name'])
        except Exception as e:
            print(f"Error reading existing CSV: {e}")
    return existing_reviewers

def save_reviews_to_csv(reviews_data, filename):
    """Save reviews to CSV file"""
    file_exists = os.path.exists(filename)
    
    with open(filename, 'a', newline='', encoding='utf-8') as file:
        fieldnames = ['reviewer_name', 'star_count', 'review_text']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        
        # Write header only if file doesn't exist
        if not file_exists:
            writer.writeheader()
        
        # Write all reviews
        for review_data in reviews_data:
            writer.writerow(review_data)

def get_reviews():
    """Print all reviewer names from the CSV file"""
    csv_filename = "turkcell_reviews.csv"
    
    if not os.path.exists(csv_filename):
        print(f"CSV file '{csv_filename}' not found!")
        return
    
    try:
        with open(csv_filename, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            reviewer_names = []
            
            for row in reader:
                reviewer_names.append(row['reviewer_name'])
            
            if reviewer_names:
                print(f"Found {len(reviewer_names)} reviewers in CSV:")
                print("-" * 50)
                for i, name in enumerate(reviewer_names, 1):
                    print(f"{i}. {name}")
                print("-" * 50)
            else:
                print("No reviewers found in CSV file.")
                
    except Exception as e:
        print(f"Error reading CSV file: {e}")

def main():
    """Main function to run the Selenium script"""
    driver = None
    csv_filename = "turkcell_reviews.csv"
    
    # Load existing reviewers to avoid duplicates
    existing_reviewers = load_existing_reviewers(csv_filename)
    print(f"Found {len(existing_reviewers)} existing reviewers in CSV")
    
    # List to store new review data
    new_reviews = []
    
    try:
        print("Setting up Chrome WebDriver...")
        driver = setup_driver()
        
        print("Navigating to Google.com...")
        driver.get(url_1)
        
        print("Successfully opened Google.com!")
        print("You can now continue with your automation...")
        
        # Wait for 5 seconds so you can see the browser 
        
        # You can add your code here
        # For example:
        # search_box = driver.find_element(By.ID, "searchboxinput")
        # search_box.click()
        # search_box.send_keys("turkcell")
        # search_box.send_keys(Keys.ENTER)
        
        # Wait for page to load
        time.sleep(3)
        
        # Click the "En yeni" button
        en_yeni_button = driver.find_element(By.CSS_SELECTOR, 'button[aria-label="En alakalı"]')
        en_yeni_button.click()
        
        # Wait for dropdown to appear
        time.sleep(2)
        
        # Select the div element with data-index="1"
        dropdown_option = driver.find_element(By.CSS_SELECTOR, 'div[data-index="1"]')
        dropdown_option.click()
        
        # Wait for reviews to load
        time.sleep(5)
        
        # Scrape reviews that are 2 months or newer
        print("Extracting reviews that are 2 months or newer...")
        
        reviews = driver.find_elements(By.CSS_SELECTOR, 'div.jftiEf.fontBodyMedium')
        
        for review in reviews:
            try:
                # Get the time element
                time_element = review.find_element(By.CSS_SELECTOR, 'span.rsqaWe')
                time_text = time_element.text.strip()
                
                # Check if review is 3 months or older and stop
                if "ay önce" in time_text:
                    if "bir ay" in time_text:
                        months = 1
                    else:
                        # Extract number before "ay önce"
                        try:
                            months = int(time_text.split()[0])
                        except:
                            months = 1
                    
                    # Stop if 3 months or older
                    if months >= 3:
                        print(f"Reached {months} month old review, stopping...")
                        break
                
                # Get reviewer name
                try:
                    name_element = review.find_element(By.CSS_SELECTOR, 'div.d4r55')
                    reviewer_name = name_element.text.strip()
                except:
                    reviewer_name = "Unknown"
                
                # Skip if reviewer already exists in CSV
                if reviewer_name in existing_reviewers:
                    print(f"Skipping {reviewer_name} - already in CSV")
                    continue
                
                # Get star rating and check if less than 3 stars
                try:
                    star_element = review.find_element(By.CSS_SELECTOR, 'span.kvMYJc')
                    star_label = star_element.get_attribute('aria-label')
                    
                    # Extract number of stars from aria-label (e.g., "1 yıldız" -> 1)
                    if "yıldız" in star_label:
                        star_count = int(star_label.split()[0])
                        
                        # Only process if less than 3 stars
                        if star_count >= 4:
                            continue
                    else:
                        continue
                        
                except:
                    # Skip if can't find star rating
                    continue
                
                # Get review text
                try:
                    review_text_element = review.find_element(By.CSS_SELECTOR, 'div.MyEned span.wiI7pd')
                    review_text = review_text_element.text.strip()
                    
                    # Add to new reviews list
                    review_data = {
                        'reviewer_name': reviewer_name,
                        'star_count': star_count,
                        'review_text': review_text
                    }
                    new_reviews.append(review_data)
                    
                    # Print the review info
                    print(f"\n--- Review from {time_text} ({star_count} stars) ---")
                    print(f"Reviewer: {reviewer_name}")
                    print(f"Comment: {review_text}")
                    
                except:
                    # Skip reviews without text
                    continue
                    
            except Exception as e:
                continue
        
        # Save new reviews to CSV
        if new_reviews:
            save_reviews_to_csv(new_reviews, csv_filename)
            print(f"\nSaved {len(new_reviews)} new reviews to {csv_filename}")
        else:
            print("\nNo new reviews found to save")
        
        print("Searching for turkcell...")
        time.sleep(5)
        
    except Exception as e:
        print(f"An error occurred: {e}")
        
    finally:
        # Clean up: close the browser
        if driver:
            print("Closing browser...")
            time.sleep(5)
            driver.quit()

    get_reviews()


if __name__ == "__main__":
    main()
