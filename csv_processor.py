import logging
import pandas as pd
import os
from typing import List
from file_handler import FileHandler
from visualisation import Visualization
class CSVProcessor:
    """
    Orchestrates the processing of CSV files, including parsing, deduplication, and visualization.
    """
    def __init__(self, csv_input_folder: str, output_csv_folder: str, output_png_folder: str, enable_heatmap: bool, top_n_keywords: int):
        """
        Initializes the CSVProcessor with file handling and visualization settings.

        Args:
            csv_input_folder (str): Path to the folder containing input CSV files.
            output_csv_folder (str): Path to the folder for saving processed CSV files.
            output_png_folder (str): Path to the folder for saving visualizations.
            enable_heatmap (bool): Flag to enable or disable heatmap generation.
            top_n_keywords (int): Number of top keywords to include in visualizations.
        """
        logging.debug(f"Initializing CSVProcessor with input folder: {csv_input_folder}, output CSV folder: {output_csv_folder}, "
                      f"output PNG folder: {output_png_folder}, enable_heatmap: {enable_heatmap}, top_n_keywords: {top_n_keywords}")
        self.file_handler = FileHandler(csv_input_folder, output_csv_folder, output_png_folder)
        self.visualization = Visualization(output_png_folder, enable_heatmap, top_n_keywords)

    def parse_and_visualize(self, export_file: str = 'post_processed', duplicates_file: str = 'duplicates.xlsx') -> None:
        """
        Parses CSV files, removes duplicates, and generates visualizations.

        Args:
            export_file (str): Name of the file to save the processed DataFrame.
            duplicates_file (str): Name of the file to save the duplicate records.
        """
        logging.info("Starting the parse and visualize process.")
        csv_files = self.file_handler.load_csv_files()
        logging.debug(f"Loaded {len(csv_files)} CSV files: {csv_files}")
        export_file_csv = export_file+".csv"
        export_file_xlsx = export_file+".xlsx"
        v_list_s = list()
        v_list_i = list()
        file_lengths = {}  # Dictionary to store file lengths
        merged_df = pd.DataFrame()

        for csv_file in csv_files:
            logging.debug(f"Processing file: {csv_file}")

            # Read the CSV into a DataFrame
            df = pd.read_csv(csv_file)

            # Get the base name of the file without extension
            file_name = os.path.splitext(os.path.basename(csv_file))[0]
            v_list_s.append(file_name)

            # Store the length of the DataFrame
            file_lengths[file_name] = len(df)
            logging.debug(f"Loaded DataFrame with {len(df)} rows from {csv_file}")
            v_list_i.append(len(df))

            # Rename and add a source column
            df.rename(columns={"Document Title": "Title", "Year": "Publication Year"}, inplace=True)
            df['Source'] = file_name

            # Merge the DataFrame
            merged_df = pd.concat([merged_df, df], ignore_index=True)

        # Log the lengths of all files
        logging.info(f"File lengths: {file_lengths}")

        total_publications_before = len(merged_df)
        logging.info(f"Total publications before removing duplicates: {total_publications_before}")

        self.file_handler.export_to_excel(merged_df, "before_duplication_"+export_file_xlsx)
        self.file_handler.export_to_csv(merged_df, "before_duplication_"+export_file_csv)
        logging.info(f"Processed data saved to {export_file_csv}")

        duplicates = merged_df[merged_df.duplicated(subset=['DOI'], keep=False)]
        logging.debug(f"Found {len(duplicates)} duplicate entries.")
        self.file_handler.export_to_excel(duplicates, duplicates_file)
        logging.info(f"Saved duplicates to {duplicates_file}")

        duplicate_droped_merged_df = merged_df.drop_duplicates(subset=['DOI'])
        total_publications_after = len(duplicate_droped_merged_df)
        logging.info(f"Total publications after removing duplicates: {total_publications_after}")

        logging.info(f"Summary: Total publications before duplicates: {total_publications_before}, after duplicates: {total_publications_after}")

        self.file_handler.export_to_excel(duplicate_droped_merged_df, export_file_xlsx)
        self.file_handler.export_to_csv(duplicate_droped_merged_df, export_file_csv)
        logging.info(f"Processed data saved to {export_file_csv}")

        # Visualizations
        logging.debug("Generating visualizations.")
        year_counts = duplicate_droped_merged_df['Publication Year'].value_counts().sort_index()
        self.visualization.create_yearly_publications_chart(year_counts, 'Number of Publications by Year')
        logging.debug("Yearly publications chart generated.")
        self.visualization.create_keyword_visualizations(merged_df)
        logging.debug("Keyword visualizations generated.")
        self.visualization.create_title_keyword_visualizations(merged_df)
        logging.debug("Title keyword visualizations generated.")
        self.visualization.create_abstract_keyword_visualizations(merged_df)
        logging.debug("Abstract keyword visualizations generated.")
        duplicates_1= total_publications_before-total_publications_after
        v_list_s = v_list_s + ["Before\n Duplicate Removal", "After\n Duplicate Removal", "Duplicates"]
        v_list_i = v_list_i + [total_publications_before, total_publications_after, total_publications_before-total_publications_after]
        print(v_list_s)
        print(v_list_i)
        self.visualization.create_bar_chart(v_list_s, v_list_i,"","","Count (Publications)","stats.png")

    def filter_papers_by_field(self, keywords: List[str], field: str, post_processed_file: str = 'post_processed.csv', filter_contains: bool = True) -> pd.DataFrame:
        """
        Filters research papers based on the presence or absence of keywords in the specified field.

        Args:
            keywords (List[str]): List of keywords to filter the specified field by.
            field (str): The field (e.g., 'Title', 'Abstract') to check for the keywords.
            post_processed_file (str): The file containing the processed CSV data.
            filter_contains (bool): If True, filters rows where the field contains any keyword.
                                    If False, filters rows where the field does not contain any keyword.

        Returns:
            pd.DataFrame: Filtered DataFrame based on the specified condition.
        """
        filepath = os.path.join(self.file_handler.output_csv_folder, post_processed_file)
        logging.debug(f"Looking for post-processed file at: {filepath}")
        if not os.path.exists(filepath):
            logging.error(f"Post-processed file not found: {filepath}")
            return pd.DataFrame()

        df = pd.read_csv(filepath)
        logging.debug(f"Loaded DataFrame with {len(df)} rows from {filepath}")
        if field not in df.columns:
            logging.error(f"The post-processed file does not contain the field: {field}.")
            return pd.DataFrame()

        logging.debug(f"Filtering papers in field '{field}' using keywords: {keywords} and filter_contains={filter_contains}")

        # Create the filter mask
        if filter_contains:
            # Filter rows where the field contains any keyword
            mask = df[field].str.contains('|'.join(keywords), case=False, na=False)
        else:
            # Filter rows where the field does not contain any keyword
            mask = ~df[field].str.contains('|'.join(keywords), case=False, na=False)

        filtered_df = df[mask]
        condition_type = 'contains' if filter_contains else 'does_not_contain'
        logging.info(f"Filtered {len(filtered_df)} papers where the field '{field}' {condition_type} the keywords: {keywords}")

        output_file = f"filtered_{condition_type}_{field.lower()}_{'_'.join(keywords)}.csv"
        self.file_handler.export_to_csv(filtered_df, output_file)
        logging.info(f"Filtered data saved to {output_file}")
        return filtered_df

