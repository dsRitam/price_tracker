from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
import time
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import os
import sys


# options
chrome_options = Options()
chrome_options.add_argument("--disable-http2")
chrome_options.add_argument("--incognito")
#chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_argument("--ignore-certificate-errors")
chrome_options.add_argument("--enable-features=NetworkServiceInProcess")
#chrome_options.add_argument("--disable-features=NetworkService")
chrome_options.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36")
chrome_options.add_argument('--headless')  # Run without opening browser
chrome_options.add_argument('--no-sandbox')  # Required for Streamlit Cloud
chrome_options.add_argument('--disable-dev-shm-usage')  # Required for Streamlit Cloud



def wait_for_page_to_load(driver, wait):
    title=driver.title
    try:
        wait.until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        print(f"The Webpage {title} get fully loaded.\n")
    except:
        print(f"The Webpage {title} didn't get fully loaded.\n")
   
search_query = "smartphones"

# <---------------------------------- AMAZON ---------------------------------->

def amazon_web_scraper(chrome_options, search_query):
    service = Service('/usr/bin/chromium-chromedriver')  # Path for Streamlit Cloud
    driver = webdriver.Chrome(service=service, options=chrome_options)
    wait = WebDriverWait(driver,10)
    driver.maximize_window()

    url = f"https://www.amazon.in/s?k={search_query.replace(' ', '+')}"
    driver.get(url)
    wait_for_page_to_load(driver, wait)


    # WEB_SCRAPING ----->

    def scrape_product_data(driver, wait):
        original_window = driver.current_window_handle

        # Collecting all product links 
        try:
            product_links_per_page = wait.until(
                EC.presence_of_all_elements_located(
                    (By.CSS_SELECTOR, ".s-product-image-container a.a-link-normal.s-no-outline")
                )
            )
            urls = [link.get_attribute('href') for link in product_links_per_page]
        except:
            return []
        
        products=[]
        for url in urls:
            # Open new tab
            driver.switch_to.new_window('tab')
            #print(url)
            driver.get(url)
            #time.sleep(2)

            # SCARPING LOGIN HERE --->
            try:
                name = driver.find_element(By.CSS_SELECTOR, "span#productTitle.a-size-large.product-title-word-break").text # '#' since id
            except:
                name = None
                
            try:
                real_price = driver.find_element(By.CSS_SELECTOR, "span[class='a-price aok-align-center reinventPricePriceToPayMargin priceToPay'] span[class='a-price-whole']").text
            except:
                real_price = None


            try:
                mrp = driver.find_element(By.CSS_SELECTOR, "span[class='a-size-small a-color-secondary aok-align-center basisPrice'] span[class='a-price a-text-price']").text
            except:
                mrp = None

            try:
                rating = driver.find_element(By.CSS_SELECTOR, "span[data-hook='rating-out-of-text']").text   # [] since attribute
                rating = rating.split()[0] if rating else None
            except:
                rating = None
            
            try:
                review_element = driver.find_elements(By.XPATH, "//div[@data-hook='review-collapsed']/span")
                reviews = [review.text.strip() for review in review_element]
            except:
                reviews = None

            products.append({
                            'Platform': 'Amazon',
                            'Name': name,
                            'Discounted_Price(₹)': real_price.replace(',', '') if real_price else None,
                            'MRP(₹)': mrp.replace("₹", "").replace(",", "").strip() if mrp else None,
                            'Rating': rating,
                            'Reviews': reviews,
                            'Timestamp': pd.Timestamp.now()
                        })


            # Close tab and return to original window
            driver.close()
            driver.switch_to.window(original_window)
            #print("-" * 20)
        
        return products
        
    # PAGE EXPLORATION --->
    pg_count=2
    all_products=[]


    while True:
        products_on_page = scrape_product_data(driver, wait)
        if not products_on_page:  # Exit if no products found
            break
        all_products.extend(products_on_page)
        try:
            time.sleep(1)
            next_button = wait.until(
                EC.element_to_be_clickable((By.XPATH, f"//a[@aria-label='Go to next page, page {pg_count}']"))
            )
            
            driver.execute_script("window.scrollBy(0, arguments[0].getBoundingClientRect().top - 100);", next_button)
            time.sleep(1)
            next_button.click()
            pg_count += 1
            
        except:
            print("We have visited all the pages...")
            break

    # df = pd.DataFrame(all_products)
    driver.quit()
    return all_products








# <---------------------------------- FLIPKART ---------------------------------->

def flipkart_web_scraper(chrome_options, search_query, all_products):
    service = Service('/usr/bin/chromium-chromedriver')
    driver = webdriver.Chrome(service=service, options=chrome_options)
    wait = WebDriverWait(driver,10)
    driver.maximize_window()

    url = f"https://www.flipkart.com/search?q={search_query.replace(' ', '+')}"
    driver.get(url)
    wait_for_page_to_load(driver, wait)


    # WEB_SCRAPING ----->


    def scrape_product_data(driver, wait):
        original_window = driver.current_window_handle

        # Collect all product links 
        try:
            product_links_per_page = wait.until(
                EC.presence_of_all_elements_located(
                    (By.CSS_SELECTOR, ".CGtC98")
                )
            )
            urls = [link.get_attribute('href') for link in product_links_per_page]
        except:
            return []
        
        products=[]
        for url in urls:
            # Open new tab
            driver.switch_to.new_window('tab')
            #print(url)
            driver.get(url)
            #time.sleep(2)

            # SCARPING LOGIN HERE --->
            try:
                name = driver.find_element(By.CSS_SELECTOR, ".VU-ZEz").text 
            except:
                name = None
                
            try:
                real_price = driver.find_element(By.CSS_SELECTOR, "div.Nx9bqj.CxhGGd").text
            except:
                real_price = None


            try:
                mrp = driver.find_element(By.CSS_SELECTOR, "div[class='yRaY8j A6+E6v']").text
            except:
                mrp = None

            try:
                rating = driver.find_element(By.CSS_SELECTOR, ".ipqd2A").text
            except:
                rating = None
            
            try:
                review_element = driver.find_elements(By.CSS_SELECTOR, ".ZmyHeo")
                reviews = [review.text.strip() for review in review_element]
            except:
                reviews = None

            products.append({
                            'Platform': 'Flipkart',
                            'Name': name,
                            'Discounted_Price(₹)': real_price.replace("₹", "").replace(',', '') if real_price else None,
                            'MRP(₹)': mrp.replace("₹", "").replace(",", "").strip() if mrp else None,
                            'Rating': rating,
                            'Reviews': reviews,
                            'Timestamp': pd.Timestamp.now()
                        })


            # Close tab and return to original window
            driver.close()
            driver.switch_to.window(original_window)
            #print("-" * 20)
        
        return products


    # PAGE EXPLORATION --->

    while True:
        products_on_page = scrape_product_data(driver, wait)
        if not products_on_page:  
            break
        all_products.extend(products_on_page)
        try:
            time.sleep(1)
            current_url = driver.current_url  # Getting current URL before clicking
            
            next_button = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//span[normalize-space()='Next']"))
            )

            driver.execute_script("window.scrollBy(0, arguments[0].getBoundingClientRect().top - 100);", next_button)
            time.sleep(1)
            next_button.click()
            
            time.sleep(2) 
            new_url = driver.current_url  # Getting new URL after clicking
            
            # If clicking "Next" doesn't change the URL, we have reached the last page
            if current_url == new_url:
                print("We have visited all the pages...")
                break
            
        except:
            print("We have visited all the pages...")
            break
    
    driver.quit()
    return all_products


def main(search_query):
    print("Starting Amazon Scraper...\n")
    amazon_products = amazon_web_scraper(chrome_options, search_query)
    print(f"Total products scraped from Amazon: {len(amazon_products)}\n")

    print("Starting Flipkart Scraper...\n")
    all_products = flipkart_web_scraper(chrome_options, search_query, amazon_products)
    print(f"Total products scraped in total (Amazon + Flipkart): {len(all_products)}\n")

    
    output_dir = "scrape_data"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    df = pd.DataFrame(all_products)

    output_path = os.path.join(output_dir, f"{search_query.replace(' ', '_')}_product_data.csv")
    
    df.to_csv(output_path, index=False)
    print(f"Data saved to '{output_path}'\n")

if __name__ == "__main__":
    search_query = sys.argv[1] if len(sys.argv) > 1 else "smartphones"
    main(search_query)
