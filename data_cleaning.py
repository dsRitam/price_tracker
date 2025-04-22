import os
import pandas as pd 

# output_dir = "scrape_data"
# csv_files = [f for f in os.listdir(output_dir) if f.endswith(".csv")]
# latest_file = max(csv_files, key=lambda f: os.path.getmtime(os.path.join(output_dir, f)))
# print(f"Using latest file: {latest_file}")
# filename = os.path.join(output_dir, latest_file)

def data_cleaner(filename):
    df = pd.read_csv(filename)
    rows, columns = df.shape

    for row_no in range(rows):
        if pd.isna(df.iloc[row_no, 3]):
            df.iloc[row_no, 3] = df.iloc[row_no, 2]
            
    df = df.dropna(subset=['Name', 'Discounted_Price(₹)', 'Rating'])
    df["Reviews"] = df["Reviews"].str.replace("[", "").str.replace("]", "")
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    return df

# df = data_cleaner(filename)
# df.to_csv('final_data.csv', index=False)

def main():
    output_dir = "scrape_data"
    csv_files = [f for f in os.listdir(output_dir) if f.endswith(".csv")]

    latest_file = max(csv_files, key=lambda f: os.path.getmtime(os.path.join(output_dir, f)))
    print(f"Using latest file: {latest_file}")
    filename = os.path.join(output_dir, latest_file)

    df = data_cleaner(filename)
    df.to_csv('final_data.csv', index=False)

if __name__ == "__main__":
    main()