# E-Commerce Real Time Price Tracker

A dynamic e-commerce price tracker that scrapes product data from Amazon and Flipkart, performs data cleaning and sentiment analysis, and visualizes insights through an interactive Streamlit dashboard. The processed data is exported as a CSV for advanced analytics in Power BI, with a published dashboard exported as PPT/PDF for reporting.

## Features

- **User Input**: Search for products (e.g., smartphones, watches) via a Streamlit app.
- **Web Scraping**: Fetches product details (name, price, MRP, rating, reviews) from Amazon and Flipkart using Selenium.
- **Data Cleaning**: Handles missing values, formats prices, and standardizes data.
- **Sentiment Analysis**: Analyzes review sentiments using TextBlob, categorizing them as Positive, Negative, or Neutral.
- **Interactive Dashboard**: Displays price comparisons, sentiment distribution, and brand distribution using Plotly.
- **Data Export**: Downloads processed `final_data.csv` for external use (e.g., Power BI).
- **Power BI Integration**: Manual data loading into Power BI for advanced visualizations, exported as PPT/PDF.

## Project Structure

```
price_tracker/
├── app.py                    # Streamlit app
├── web_scraping.py           # Scrapes data from Amazon/Flipkart
├── data_cleaning.py          # Cleans scraped data
├── sentiment.py              # Performs sentiment analysis
├── requirements.txt          # Python dependencies
├── README.md                 # Project documentation
```

## Setup (Local)

1. **Clone Repository**:

   ```bash
   git clone https://github.com/dsRitam/price_tracker.git
   cd price_tracker
   ```

2. **Create Virtual Environment**:

   ```bash
   python -m venv venv
   .\venv\Scripts\activate  # Windows
   ```

3. **Install Dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Run Streamlit App**:

   ```bash
   streamlit run app.py
   ```

5. **Access App**: Open `http://localhost:8501` in browser.


## Demo

- **Power BI Outputs**: Available in `price_tracker.pdf` and `price_tracker_report_power_bi.pptx`. Please ensure you use an official or work account to open the PowerPoint presentation.


## Technologies

- **Python**: Streamlit, Pandas, Selenium, TextBlob, Plotly
- **Web Scraping**: Selenium with ChromeDriver
- **Visualization**: Plotly, Power BI

---

