# CSV Publication Data Processing and Visualization

This project provides functionality for processing and visualizing CSV data related to publications, creating a series of diagrams, and handling duplicates. It processes multiple CSV files, filters the relevant columns, merges them, removes duplicates, and generates bar charts with grid lines for visualizing publication counts by year and source.

## Features

- **Pre-processing Diagrams**: Generates bar charts for publication counts by year and source for each individual CSV file.
- **Merging and Filtering**: Filters relevant columns from each CSV file, merges them, removes duplicates based on the 'Title' column, and exports both the cleaned data and duplicates.
- **Post-processing Diagrams**: Generates bar charts for the combined data showing the number of publications by year, source, and the number of duplicates.
- **Grid Lines**: Fine-granularity grid lines are added to the bar charts for improved readability.

## Requirements

- **Python 3.x**
- **pandas**: For handling CSV files and DataFrame operations.
- **matplotlib**: For creating bar charts.
- **glob**: For reading all CSV files in a directory.
- **re**: For regular expression filtering.

You can install the required Python libraries with the following command:

```bash
pip install pandas matplotlib

for Science Direct -> export -> bibtex -> convert bibtext to csv

## License

This project is licensed under the [Creative Commons Attribution-NonCommercial 4.0 International License (CC BY-NC 4.0)](https://creativecommons.org/licenses/by-nc/4.0/).

You are free to:
- Share — copy and redistribute the material in any medium or format
- Adapt — remix, transform, and build upon the material

Under the following terms:
- **Attribution** — You must give appropriate credit, provide a link to the license, and indicate if changes were made.
- **NonCommercial** — You may not use the material for commercial purposes.
