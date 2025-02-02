from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import os
import pandas as pd
import re
import matplotlib.pyplot as plt
import glob

app = Flask(__name__)

# Folder paths
csv_input_folder = 'csv_database'
output_csv_folder = 'output_csvs'
output_png_folder = 'output_pngs'

os.makedirs(output_csv_folder, exist_ok=True)
os.makedirs(output_png_folder, exist_ok=True)


# Function to create pre-processing diagrams
def create_pre_processing_diagrams(csv_files):
    for csv_file in csv_files:
        df = pd.read_csv(csv_file)
        df.rename(columns={"Document Title": "Title", "Year": "Publication Year"}, inplace=True)

        # Year vs Number of Publications
        year_counts = df['Publication Year'].value_counts().sort_index()
        plt.figure(figsize=(10, 6))
        year_counts.plot(kind='bar', color='skyblue', edgecolor='black')
        plt.title(f'Number of Publications by Year - {csv_file}')
        plt.xlabel('Publication Year')
        plt.ylabel('Number of Publications')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(os.path.join(output_png_folder, f'{os.path.basename(csv_file)}_publications_by_year.png'))
        plt.close()

        # Source vs Number of Publications
        df['Source'] = csv_file
        source_counts = df['Source'].value_counts()
        plt.figure(figsize=(10, 6))
        source_counts.plot(kind='bar', color='lightgreen', edgecolor='black')
        plt.title(f'Number of Publications by Source - {csv_file}')
        plt.xlabel('Source')
        plt.ylabel('Number of Publications')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(os.path.join(output_png_folder, f'{os.path.basename(csv_file)}_publications_by_source.png'))
        plt.close()


# Function to parse, filter, and merge CSVs
def parse_filter_and_merge_csvs(csv_files, export_file='post_processed.csv', duplicates_file='duplicates.csv'):
    merged_df = pd.DataFrame()

    for csv_file in csv_files:
        df = pd.read_csv(csv_file)
        df.rename(columns={"Document Title": "Title", "Year": "Publication Year"}, inplace=True)

        patterns = [r"(Document)*\bTitle.*", r".*Authors.*", r".*Year.*"]
        filtered_columns = [col for col in df.columns if any(re.match(pattern, col, re.IGNORECASE) for pattern in patterns)]
        df = df[filtered_columns]

        df['Source'] = csv_file
        merged_df = pd.concat([merged_df, df], ignore_index=True)

    duplicates = merged_df[merged_df.duplicated(subset=['Title'], keep=False)]
    duplicates.to_csv(os.path.join(output_csv_folder, duplicates_file), index=False)

    merged_df = merged_df.drop_duplicates(subset=['Title'])
    merged_df.to_csv(os.path.join(output_csv_folder, export_file), index=False)

    return merged_df, duplicates


# Route for uploading files
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        files = request.files.getlist("csv_files")

        # Save uploaded files to the csv_database folder
        for file in files:
            if file and file.filename.endswith('.csv'):
                file_path = os.path.join(csv_input_folder, file.filename)
                file.save(file_path)

        csv_files = glob.glob(os.path.join(csv_input_folder, "*.csv"))

        # Create pre-processing diagrams directly (without threading)
        create_pre_processing_diagrams(csv_files)

        # Parse and merge CSVs
        df_processed, df_duplicates = parse_filter_and_merge_csvs(csv_files)

        return render_template("index.html", files_uploaded=True, files=csv_files)

    return render_template("index.html", files_uploaded=False)


# Route to download the processed CSV or PNG files
@app.route("/download/<file_type>/<filename>")
def download(file_type, filename):
    if file_type == 'csv':
        return send_from_directory(output_csv_folder, filename)
    elif file_type == 'png':
        return send_from_directory(output_png_folder, filename)
    return "Invalid file type", 404


if __name__ == "__main__":
    # Ensure the app runs in single-threaded mode
    app.run(debug=True, threaded=False)
