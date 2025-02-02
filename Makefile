# Define file names for the output
EXPORT_FILE = post_processed.csv
DUPLICATES_FILE = duplicates.csv
PRE_PROC_FILES = scopus_publications_by_year.png scopus_publications_by_source.png \
                 ieeexplore_publications_by_year.png ieeexplore_publications_by_source.png
POST_PROC_FILES = publications_by_year.png publications_by_source.png duplicates_count.png

# Define the Python script to run
PYTHON_SCRIPT = research_p.py

# Default target: process the CSV files
all: process

create_venv:
	python3 -m venv myenv
	source myenv/bin/activate
	pip install -r requirements.txt
# Process CSV files and generate diagrams
process:
	@echo "Processing CSV files and generating diagrams..."
	python3 $(PYTHON_SCRIPT)

# Clean up generated files (CSV outputs and diagram images)
clean:
	@echo "Cleaning up generated files..."
	rm -f $(EXPORT_FILE) $(DUPLICATES_FILE) $(PRE_PROC_FILES) $(POST_PROC_FILES)
	rm *png

# Add a help target for easy reference
help:
	@echo "Makefile targets:"
	@echo "  process  - Process CSV files and generate diagrams"
	@echo "  clean    - Remove generated files (CSV and images)"
	@echo "  help     - Display this help message"
