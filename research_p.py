import logging
import argparse
from csv_processor import CSVProcessor

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process CSV files and generate diagrams.")
    parser.add_argument('--csv_input_folder', type=str, default='csv_database', help='Folder containing input CSV files')
    parser.add_argument('--output_csv_folder', type=str, default='output_csvs', help='Folder to store processed CSV files')
    parser.add_argument('--output_png_folder', type=str, default='output_pngs', help='Folder to store generated PNG files')
    parser.add_argument('--enable_heatmap', action='store_true', help='Enable heatmap generation for keyword co-occurrences')
    parser.add_argument('--top_n_keywords', type=int, default=20, help='Number of top keywords to include in visualizations')
    parser.add_argument('--filter_keywords', type=str, nargs='+', help='Keywords to filter research papers by')
    parser.add_argument('--filter_field', type=str, default='Title', help='Field to filter by (e.g., Title, Abstract)')

    args = parser.parse_args()

    processor = CSVProcessor(
        csv_input_folder=args.csv_input_folder,
        output_csv_folder=args.output_csv_folder,
        output_png_folder=args.output_png_folder,
        enable_heatmap=args.enable_heatmap,
        top_n_keywords=args.top_n_keywords
    )

    processor.parse_and_visualize()

    if args.filter_keywords:
        processor.filter_papers_by_field(args.filter_keywords, args.filter_field)
