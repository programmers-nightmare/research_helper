import pandas as pd
import re
import matplotlib.pyplot as plt
import os
import logging
from typing import List, Tuple, Optional
from matplotlib.ticker import MaxNLocator
from wordcloud import WordCloud
import seaborn as sns
import numpy as np
from collections import Counter

class Visualization:
    """
    Handles the creation of various visualizations, including charts, word clouds, and heatmaps.
    """
    def __init__(self, output_png_folder: str, enable_heatmap: bool, top_n_keywords: int):
        """
        Initializes the Visualization class with output settings.

        Args:
            output_png_folder (str): Path to the folder for saving visualizations.
            enable_heatmap (bool): Flag to enable or disable heatmap generation.
            top_n_keywords (int): Number of top keywords to include in visualizations.
        """
        self.output_png_folder = output_png_folder
        self.enable_heatmap = enable_heatmap
        self.top_n_keywords = top_n_keywords

    def create_bar_chart(self, categories: List[str], counts: List[int], title: str, xlabel: str, ylabel: str, output_path: str) -> None:
        """
        Creates a bar chart for given categories and their respective counts.

        Args:
            categories (List[str]): List of category labels.
            counts (List[int]): List of corresponding counts for each category.
            title (str): Title of the chart.
            xlabel (str): Label for the X-axis.
            ylabel (str): Label for the Y-axis.
            output_path (str): The file path to save the generated bar chart.
        """
        try:
            plt.figure(figsize=(13, 6))
            plt.bar(categories, counts, color='green', edgecolor='black')
            plt.title(title)
            plt.xlabel(xlabel)
            plt.ylabel(ylabel)
            plt.ylim(0, max(counts) + 10)
            plt.grid(axis='both', linestyle='--', alpha=0.7)

            # Annotate the bars with their values
            for i, count in enumerate(counts):
                plt.text(i, count + 1, str(count), ha='center', va='bottom', fontsize=12)

            # Save the plot
            filename = os.path.join(self.output_png_folder, output_path)
            plt.savefig(filename)
            plt.close()
            logging.info(f"Bar chart '{title}' saved to {filename}")
        except Exception as e:
            logging.error(f"Error while creating the bar chart '{title}': {e}")

    def create_yearly_publications_chart(self, year_counts: pd.Series, title: str) -> None:
        """
        Creates a bar chart for the number of publications per year.

        Args:
            year_counts (pd.Series): Series with years as index and publication counts as values.
            title (str): Title of the chart.
        """
        plt.figure(figsize=(5, 6))
        plt.bar(year_counts.index, year_counts.values, color='skyblue', edgecolor='black')
        plt.title(title)
        plt.xlabel('Publication Year')
        plt.ylabel('Number of Publications')
        plt.xticks(year_counts.index, rotation=45)
        plt.gca().yaxis.set_major_locator(MaxNLocator(integer=True))
        plt.grid(True, which='both', axis='y', linestyle='--', linewidth=0.7)
        plt.tight_layout()
        filename = os.path.join(self.output_png_folder, 'publications_by_year.png')
        plt.savefig(filename)
        plt.close()
        logging.info(f"Yearly publications chart saved to {filename}")

    def create_keyword_visualizations(self, df_processed: pd.DataFrame) -> None:
        """
        Creates visualizations for keywords, including a word cloud, bar chart, and optionally a heatmap.

        Args:
            df_processed (pd.DataFrame): Processed DataFrame containing the 'Keywords' column.
        """
        if 'Keywords' not in df_processed.columns:
            logging.warning("No 'Keywords' column found in the processed DataFrame. Skipping keyword visualizations.")
            return

        keywords = df_processed['Keywords'].dropna().str.cat(sep=' ')
        keyword_list = keywords.split()

        # Word Cloud
        wordcloud = WordCloud(width=800, height=400, background_color='white').generate(keywords)
        plt.figure(figsize=(10, 5))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.title('Keyword Word Cloud')
        plt.tight_layout()
        filename = os.path.join(self.output_png_folder, 'keyword_wordcloud.png')
        plt.savefig(filename)
        plt.close()
        logging.info(f"Keyword word cloud saved to {filename}")

        # Bar Chart
        keyword_counts = Counter(keyword_list).most_common(self.top_n_keywords)
        keywords_df = pd.DataFrame(keyword_counts, columns=['Keyword', 'Count'])
        plt.figure(figsize=(10, 6))
        sns.barplot(data=keywords_df, x='Count', y='Keyword', palette='viridis')
        plt.title(f'Top {self.top_n_keywords} Keywords')
        plt.xlabel('Count')
        plt.ylabel('Keyword')
        plt.tight_layout()
        filename = os.path.join(self.output_png_folder, 'keyword_bar_chart.png')
        plt.savefig(filename)
        plt.close()
        logging.info(f"Keyword bar chart saved to {filename}")

        # Heatmap
        if self.enable_heatmap:
            from itertools import combinations
            from collections import defaultdict

            keyword_pairs = [kw.split() for kw in df_processed['Keywords'].dropna()]
            cooccurrence_dict = defaultdict(int)

            for keywords in keyword_pairs:
                for pair in combinations(sorted(set(keywords)), 2):
                    cooccurrence_dict[pair] += 1

            # Create the co-occurrence matrix
            unique_keywords = sorted(set([k for pair in cooccurrence_dict.keys() for k in pair]))[:self.top_n_keywords]
            cooccurrence_matrix = pd.DataFrame(
                np.zeros((len(unique_keywords), len(unique_keywords))),
                index=unique_keywords,
                columns=unique_keywords
            )

            for (kw1, kw2), count in cooccurrence_dict.items():
                if kw1 in unique_keywords and kw2 in unique_keywords:
                    cooccurrence_matrix.at[kw1, kw2] = count
                    cooccurrence_matrix.at[kw2, kw1] = count  # Symmetric matrix

            plt.figure(figsize=(12, 10))
            sns.heatmap(cooccurrence_matrix, cmap='YlGnBu', annot=False, cbar=True)
            plt.title(f'Keyword Co-occurrence Heatmap (Top {self.top_n_keywords})')
            plt.tight_layout()
            filename = os.path.join(self.output_png_folder, 'keyword_heatmap.png')
            plt.savefig(filename)
            plt.close()
            logging.info(f"Keyword heatmap saved to {filename}")

    def create_title_keyword_visualizations(self, df_processed: pd.DataFrame) -> None:
        """
        Creates visualizations for the most used keywords in the titles.

        Args:
            df_processed (pd.DataFrame): Processed DataFrame containing the 'Title' column.
        """
        if 'Title' not in df_processed.columns:
            logging.warning("No 'Title' column found in the processed DataFrame. Skipping title keyword visualizations.")
            return

        # Process Title column
        title_keywords = df_processed['Title'].dropna().str.cat(sep=' ')
        title_words = re.findall(r'\b\w{4,}\b', title_keywords.lower())
        title_word_counts = Counter(title_words).most_common(self.top_n_keywords)

        # Word Cloud for Title Keywords
        wordcloud = WordCloud(width=800, height=400, background_color='white').generate(' '.join(title_words))
        plt.figure(figsize=(10, 5))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.title('Title Keywords Word Cloud')
        plt.tight_layout()
        filename = os.path.join(self.output_png_folder, 'title_keywords_wordcloud.png')
        plt.savefig(filename)
        plt.close()
        logging.info(f"Title keywords word cloud saved to {filename}")

        # Bar Chart for Title Keywords
        title_keywords_df = pd.DataFrame(title_word_counts, columns=['Keyword', 'Count'])
        plt.figure(figsize=(10, 6))
        sns.barplot(data=title_keywords_df, x='Count', y='Keyword', palette='viridis')
        plt.title(f'Top {self.top_n_keywords} Title Keywords')
        plt.xlabel('Count')
        plt.ylabel('Keyword')
        plt.tight_layout()
        filename = os.path.join(self.output_png_folder, 'title_keywords_bar_chart.png')
        plt.savefig(filename)
        plt.close()
        logging.info(f"Title keywords bar chart saved to {filename}")

    def create_abstract_keyword_visualizations(self, df_processed: pd.DataFrame) -> None:
        """
        Creates visualizations for the most used keywords in the abstracts.

        Args:
            df_processed (pd.DataFrame): Processed DataFrame containing the 'Abstract' column.
        """
        if 'Abstract' not in df_processed.columns:
            logging.warning("No 'Abstract' column found in the processed DataFrame. Skipping abstract keyword visualizations.")
            return

        # Process Abstract column
        abstract_keywords = df_processed['Abstract'].dropna().str.cat(sep=' ')
        abstract_words = re.findall(r'\b\w{4,}\b', abstract_keywords.lower())
        abstract_word_counts = Counter(abstract_words).most_common(self.top_n_keywords)

        # Word Cloud for Abstract Keywords
        wordcloud = WordCloud(width=800, height=400, background_color='white').generate(' '.join(abstract_words))
        plt.figure(figsize=(10, 5))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.title('Abstract Keywords Word Cloud')
        plt.tight_layout()
        filename = os.path.join(self.output_png_folder, 'abstract_keywords_wordcloud.png')
        plt.savefig(filename)
        plt.close()
        logging.info(f"Abstract keywords word cloud saved to {filename}")

        # Bar Chart for Abstract Keywords
        abstract_keywords_df = pd.DataFrame(abstract_word_counts, columns=['Keyword', 'Count'])
        plt.figure(figsize=(10, 6))
        sns.barplot(data=abstract_keywords_df, x='Count', y='Keyword', palette='viridis')
        plt.title(f'Top {self.top_n_keywords} Abstract Keywords')
        plt.xlabel('Count')
        plt.ylabel('Keyword')
        plt.tight_layout()
        filename = os.path.join(self.output_png_folder, 'abstract_keywords_bar_chart.png')
        plt.savefig(filename)
        plt.close()
        logging.info(f"Abstract keywords bar chart saved to {filename}")