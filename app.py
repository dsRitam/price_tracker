import streamlit as st
import pandas as pd
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from textblob import TextBlob
import plotly.express as px
import io
import time

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Streamlit UI
st.title("E-Commerce Price Tracker Dashboard")
query = st.text_input("What are you looking for?", value="smartphones")

# Web scraping functions (from web_scraping.py)
def wait_for_page_to_load(driver, wait):
    title = driver.title
    try:
        wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
        logger.info(f"The Webpage {title} get fully loaded.")
    except:
        logger.error(f"The Webpage {title} didn't get fully loaded.")

def amazon_web_scraper(chrome_options, search_query):
    all_products = []
    try:
        logger.info("Starting Amazon scraper...")
        driver = webdriver.Chrome(options=chrome_options)
        wait = WebDriverWait(driver, 10)
        driver.maximize_window()
        url = f"https://www.amazon.in/s?k={search_query.replace(' ', '+')}"
        driver.get(url)
        wait_for_page_to_load(driver, wait)

        def scrape_product_data(driver, wait):
            original_window = driver.current_window_handle
            try:
                product_links_per_page = wait.until(
                    EC.presence_of_all_elements_located(
                        (By.CSS_SELECTOR, ".s-product-image-container a.a-link-normal.s-no-outline")
                    )
                )
                urls = [link.get_attribute('href') for link in product_links_per_page]
            except:
                return []

            products = []
            for url in urls:
                driver.switch_to.new_window('tab')
                driver.get(url)
                try:
                    name = driver.find_element(By.CSS_SELECTOR, "span#productTitle.a-size-large.product-title-word-break").text
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
                    rating = driver.find_element(By.CSS_SELECTOR, "span[data-hook='rating-out-of-text']").text.split()[0]
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
                driver.close()
                driver.switch_to.window(original_window)

            return products

        pg_count = 2
        while True:
            products_on_page = scrape_product_data(driver, wait)
            if not products_on_page:
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
                logger.info("Visited all Amazon pages")
                break
        driver.quit()
    except Exception as e:
        logger.error(f"Amazon scraping failed: {str(e)}")
    return all_products

def flipkart_web_scraper(chrome_options, search_query, all_products):
    try:
        logger.info("Starting Flipkart scraper...")
        driver = webdriver.Chrome(options=chrome_options)
        wait = WebDriverWait(driver, 10)
        driver.maximize_window()
        url = f"https://www.flipkart.com/search?q={search_query.replace(' ', '+')}"
        driver.get(url)
        wait_for_page_to_load(driver, wait)

        def scrape_product_data(driver, wait):
            original_window = driver.current_window_handle
            try:
                product_links_per_page = wait.until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".CGtC98"))
                )
                urls = [link.get_attribute('href') for link in product_links_per_page]
            except:
                return []

            products = []
            for url in urls:
                driver.switch_to.new_window('tab')
                driver.get(url)
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
                driver.close()
                driver.switch_to.window(original_window)

            return products

        while True:
            products_on_page = scrape_product_data(driver, wait)
            if not products_on_page:
                break
            all_products.extend(products_on_page)
            try:
                time.sleep(1)
                current_url = driver.current_url
                next_button = wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//span[normalize-space()='Next']"))
                )
                driver.execute_script("window.scrollBy(0, arguments[0].getBoundingClientRect().top - 100);", next_button)
                time.sleep(1)
                next_button.click()
                time.sleep(2)
                new_url = driver.current_url
                if current_url == new_url:
                    logger.info("Visited all Flipkart pages")
                    break
            except:
                logger.info("Visited all Flipkart pages")
                break
        driver.quit()
    except Exception as e:
        logger.error(f"Flipkart scraping failed: {str(e)}")
    return all_products

# Data cleaning function (from data_cleaning.py)
def data_cleaner(df):
    try:
        logger.info("Starting data cleaning...")
        if df.empty:
            logger.warning("Empty DataFrame received")
            return None
        rows, columns = df.shape
        for row_no in range(rows):
            if pd.isna(df.iloc[row_no, df.columns.get_loc("MRP(₹)")]):
                df.iloc[row_no, df.columns.get_loc("MRP(₹)")] = df.iloc[row_no, df.columns.get_loc("Discounted_Price(₹)")]
        df = df.dropna(subset=['Name', 'Discounted_Price(₹)', 'Rating'])
        df["Reviews"] = df["Reviews"].apply(lambda x: str(x).replace("[", "").replace("]", ""))
        df['Timestamp'] = pd.to_datetime(df['Timestamp'])
        logger.info("Data cleaning completed")
        return df
    except Exception as e:
        logger.error(f"Data cleaning failed: {str(e)}")
        return None

# Sentiment analysis function (from sentiment.py)
def get_sentiment(review):
    if pd.isna(review) or str(review).strip() == "":
        return 0.0
    analysis = TextBlob(str(review))
    return analysis.sentiment.polarity

def sentiment_analysis(df):
    try:
        logger.info("Starting sentiment analysis...")
        df['Sentiment_Score'] = df['Reviews'].apply(get_sentiment)
        df['Sentiment_Label'] = df['Sentiment_Score'].apply(lambda x: 'Positive' if x > 0 else 'Negative' if x < 0 else 'Neutral')
        logger.info("Sentiment analysis completed")
        return df
    except Exception as e:
        logger.error(f"Sentiment analysis failed: {str(e)}")
        return None

# Main processing
if st.button("Run Scraping & Analysis"):
    with st.spinner("Running web scraping, cleaning, and sentiment analysis..."):
        try:
            # Chrome options
            chrome_options = Options()
            chrome_options.add_argument("--disable-http2")
            chrome_options.add_argument("--incognito")
            chrome_options.add_argument("--ignore-certificate-errors")
            chrome_options.add_argument("--enable-features=NetworkServiceInProcess")
            chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36")
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.binary_location = '/usr/bin/chromium'

            # Scraping
            st.write("Fetching data... This may take some time.")
            logger.info(f"Scraping for {query}...")
            amazon_products = amazon_web_scraper(chrome_options, query)
            all_products = flipkart_web_scraper(chrome_options, query, amazon_products)
            df = pd.DataFrame(all_products)
            if df.empty:
                st.error("No data scraped. Please try again.")
                logger.warning("No data scraped")
                st.stop()

            # Data cleaning
            df = data_cleaner(df)
            if df is None:
                st.error("Data cleaning failed.")
                logger.warning("Data cleaning failed")
                st.stop()

            # Sentiment analysis
            df = sentiment_analysis(df)
            if df is None:
                st.error("Sentiment analysis failed.")
                logger.warning("Sentiment analysis failed")
                st.stop()

            # Save to in-memory CSV
            csv_buffer = io.StringIO()
            df.to_csv(csv_buffer, index=False)
            csv_data = csv_buffer.getvalue().encode('utf-8')

            # Display results
            st.success("Data processing complete! Datasheet generated.")
            st.write("Preview of Datasheet:")
            st.dataframe(df.head())

            # Download button
            st.download_button(
                label="Download Datasheet",
                data=csv_data,
                file_name="final_data.csv",
                mime="text/csv"
            )

            # Visualizations
            st.subheader("Dashboard")

            # Price Comparison Bar Chart
            st.write("Price Comparison Across Platforms")
            fig_price = px.bar(
                df.nlargest(10, "Discounted_Price(₹)"),
                x="Name",
                y="Discounted_Price(₹)",
                color="Platform",
                barmode="group",
                title="Top 10 Products by Price"
            )
            st.plotly_chart(fig_price, use_container_width=True)

            # Sentiment Distribution Pie Chart
            if "Sentiment_Label" in df.columns:
                st.write("Sentiment Distribution")
                sentiment_counts = df["Sentiment_Label"].value_counts().reset_index()
                sentiment_counts.columns = ["Sentiment_Label", "Count"]
                fig_sentiment = px.pie(
                    sentiment_counts,
                    names="Sentiment_Label",
                    values="Count",
                    title="Sentiment Distribution"
                )
                st.plotly_chart(fig_sentiment, use_container_width=True)
            else:
                st.warning("Sentiment analysis may have failed.")

            # Brand Distribution Pie Chart
            st.write("Brand Distribution")
            df["Brand_Name"] = df["Name"].apply(
                lambda x: x.split()[0] if isinstance(x, str) and len(x.split()) > 0 else "Unknown"
            )
            brand_counts = df["Brand_Name"].value_counts().reset_index()
            brand_counts.columns = ["Brand_Name", "Count"]
            fig_brand = px.pie(
                brand_counts,
                names="Brand_Name",
                values="Count",
                title="Brand Distribution"
            )
            st.plotly_chart(fig_brand, use_container_width=True)

            # Top Products Table
            st.write("Top Products")
            top_products = df[["Name", "Discounted_Price(₹)", "Rating", "Platform", "Brand_Name"]]
            if "Sentiment_Label" in df.columns:
                top_products["Sentiment_Label"] = df["Sentiment_Label"]
            st.dataframe(top_products.sort_values(by="Rating", ascending=False).head(10))

        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            logger.error(f"Processing error: {str(e)}")
            st.stop()