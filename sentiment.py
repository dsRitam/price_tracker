import pandas as pd
from textblob import TextBlob

# df = pd.read_csv('final_data.csv')

def get_sentiment(review):
    if pd.isna(review) or review.strip() == "":
        return 0.0  # Neutral for no reviews
    analysis = TextBlob(str(review))
    return analysis.sentiment.polarity

# # Sentiment analysis logic
# df['Sentiment_Score'] = df['Reviews'].apply(get_sentiment)
# df['Sentiment_Label'] = df['Sentiment_Score'].apply( lambda x: 'Positive' if x>0 else 'Negative' if x<0 else 'Neutral' )

# df.to_csv('final_data.csv', index=False)
# print("Sentiment analysis completed....")

def main():
    try:
        df = pd.read_csv('final_data.csv')
        df['Sentiment_Score'] = df['Reviews'].apply(get_sentiment)
        df['Sentiment_Label'] = df['Sentiment_Score'].apply( lambda x: 'Positive' if x > 0 else 'Negative' if x < 0 else 'Neutral' )
        
        df.to_csv('final_data.csv', index=False)
        print("Sentiment analysis completed....")
    except FileNotFoundError:
        print("Error: final_data.csv not found.")

if __name__ == "__main__":
    main()