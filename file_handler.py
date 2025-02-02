import pandas as pd
import os
import glob
import logging
from typing import List, Tuple, Optional

class FileHandler:
    """
    Handles file-related operations such as loading CSV files and saving DataFrames.
    """
    def __init__(self, csv_input_folder: str, output_csv_folder: str, output_png_folder: str):
        """
        Initializes the FileHandler with input and output folder paths.

        Args:
            csv_input_folder (str): Path to the folder containing input CSV files.
            output_csv_folder (str): Path to the folder for saving processed CSV files.
            output_png_folder (str): Path to the folder for saving generated visualizations.
        """
        self.csv_input_folder = csv_input_folder
        self.output_csv_folder = output_csv_folder
        self.output_png_folder = output_png_folder

        os.makedirs(self.output_csv_folder, exist_ok=True)
        os.makedirs(self.output_png_folder, exist_ok=True)

    def load_csv_files(self) -> List[str]:
        """
        Loads all CSV files from the input folder.

        Returns:
            List[str]: List of file paths for the CSV files.
        """
        return glob.glob(os.path.join(self.csv_input_folder, '*.csv'))

    def export_to_csv(self, df: pd.DataFrame, filename: str) -> None:
        """
        Saves a DataFrame to a CSV file.

        Args:
            df (pd.DataFrame): DataFrame to save.
            filename (str): Name of the file to save the DataFrame as.
        """
        filepath = os.path.join(self.output_csv_folder, filename)
        df.to_csv(filepath, index=False)
        logging.info(f"DataFrame saved to {filepath}")

    def export_to_excel(self, df: pd.DataFrame, filename: str, sheet_name: str = 'Sheet1') -> None:
        """
        Exports a DataFrame to an Excel file.

        Args:
            df (pd.DataFrame): DataFrame to export.
            filename (str): Name of the Excel file to save the DataFrame as.
            sheet_name (str): Name of the sheet in the Excel file. Defaults to 'Sheet1'.
        """
        filepath = os.path.join(self.output_csv_folder, filename)
        try:
            df.to_excel(filepath, index=False, sheet_name=sheet_name, engine='openpyxl')
            logging.info(f"DataFrame exported to Excel at {filepath}")
        except Exception as e:
            logging.error(f"Failed to export DataFrame to Excel: {e}")
            raise
