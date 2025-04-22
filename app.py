import streamlit as st
import pandas as pd
import os
import subprocess
import sys
import plotly.express as px
import plotly.graph_objects as go

st.title("E-Commerce Price Tracker Dashboard")
query = st.text_input("What are you looking for?", value="smartphones")


if st.button("Run Scraping & Analysis"):
    with st.spinner("Running web scraping, cleaning, and sentiment analysis..."):
        
        python_exec = sys.executable

        # Step 1: Running web_scraping.py
        st.write("We are fetching data... This may take some time (30mins - 1hour)")
        result = subprocess.run([python_exec, "web_scraping.py", query], capture_output=True, text=True)
        # st.write(f"Web scraping output: {result.stdout}")
        if result.stderr:
            st.error(f"Web scraping error: {result.stderr}")

        # Step 2: Running data_cleaning.py
        # st.write("Cleaning data...")
        result = subprocess.run([python_exec, "data_cleaning.py"], capture_output=True, text=True)
        # st.write(f"Data cleaning output: {result.stdout}")
        if result.stderr:
            st.error(f"Data cleaning error: {result.stderr}")

        # Step 3: Running sentiment.py
        # st.write("Performing sentiment analysis...")
        result = subprocess.run([python_exec, "sentiment.py"], capture_output=True, text=True)
        # st.write(f"Sentiment analysis output: {result.stdout}")
        if result.stderr:
            st.error(f"Sentiment analysis error: {result.stderr}")

        # Checking if final_data.csv exists
        file_path = "final_data.csv"
        if os.path.exists(file_path):
            st.success("Data processing complete! Datasheet generated.")
            df = pd.read_csv(file_path)
            st.write("Preview of Datasheet:")
            st.dataframe(df.head())

            # Download button
            with open(file_path, "rb") as file:
                st.download_button(
                    label="Download Datasheet",
                    data=file,
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

        else:
            st.error("Error: final_data.csv not found.")