# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python project for comprehensive "Run in Lyon" race data analysis and visualization. The project contains:
- `main.py`: Simple starter script
- `race_analysis.py`: Comprehensive race data analysis and visualization script
- `summary_example.py`: Example script showing how to use the summary features
- `635.json`: Large race results dataset (1.8MB) containing participant information including names, times, rankings, categories, and nationalities
- `requirements.txt`: Python dependencies

## Development Environment

- **Python Version**: 3.12.3
- **Dependencies**: pandas, matplotlib, seaborn, numpy, openpyxl (see requirements.txt)

## Setup and Installation

### Install dependencies
```bash
pip install -r requirements.txt
```

## Common Commands

### Run comprehensive race analysis
```bash
python race_analysis.py
```

### Run summary example only
```bash
python summary_example.py
```

### Install packages individually
```bash
pip install pandas matplotlib seaborn numpy openpyxl
```

### Data Analysis
The JSON file contains race results with the following structure:
- Header: CSV column mappings with French field names
- Data: Array of participant records with registration ID, bib number, name, gender, nationality, times, and rankings

## Project Structure

```
runinlyon/
├── main.py                    # Simple starter script
├── race_analysis.py           # Comprehensive race data analysis script  
├── summary_example.py         # Example usage of summary features
├── requirements.txt           # Python dependencies
├── 635.json                  # Race results data (1.8MB)
├── CLAUDE.md                 # This documentation file
└── Generated files:
    ├── *.png                 # Visualization charts
    ├── run_in_lyon_summary.csv    # Complete summary (CSV format)
    └── *.xlsx                # Excel summaries (if openpyxl installed)
```

## Race Analysis Features

The `race_analysis.py` script provides:

### General Statistics
- Total participants and finishers
- Gender distribution
- Average, median, fastest, and slowest times
- International participation (countries represented)

### Age-Based Analysis
- Performance breakdown by age categories (Senior, Master 0-5, Espoir, Junior, etc.)
- Average times per age group
- Participation counts by age category

### Individual Participant Search
- Find participant by bib number
- Show ranking, times, category, and percentile performance
- Context within overall field

### Comprehensive Summary Table
- Complete statistical overview with all key metrics
- Formatted console display with emojis
- CSV and Excel export capabilities
- Podium and top performers
- Performance quartiles and time range distributions

### Visualizations
- Real time distribution histograms and box plots
- Age category performance comparisons (using real times)
- Gender performance analysis (using real times)
- Nationality participation and performance charts
- Gun vs Chip time comparison analysis (showing start delays)

### Usage Examples
```python
from race_analysis import RaceAnalyzer

# Initialize analyzer
analyzer = RaceAnalyzer()

# Get general statistics
stats = analyzer.general_statistics()

# Find specific participant
participant = analyzer.find_participant_by_bib(12005)

# Generate all visualizations
analyzer.plot_time_distribution()        # Real time distributions
analyzer.plot_age_performance()          # Performance by age category
analyzer.plot_gender_comparison()        # Gender analysis
analyzer.plot_nationality_analysis()     # Nationality analysis
analyzer.plot_time_comparison()          # Gun vs Chip time analysis

# Generate comprehensive summary
analyzer.print_comprehensive_summary()   # Formatted console display
summary_df = analyzer.generate_comprehensive_summary()  # Get DataFrame
analyzer.save_summary_excel("summary.xlsx")  # Save to Excel
```

## Data Structure

The JSON file contains race results with:
- **Header**: CSV column mappings with French field names (Registration ID, Bib, Name, Gender, Times, Rankings, etc.)
- **Data**: Array of participant records with all race information

### Important: Two Different Time Measurements

The race data includes two different time measurements:

1. **Gun Result (Temps Officiel)**: Time from the official race start (gun shot) to finish
2. **Chip Result (Temps Réel)**: ACTUAL race time from when the participant crosses the start line to finish

**⚠️ CRITICAL**: The script prioritizes **Chip Result** for all performance analysis because:
- Participants don't all start simultaneously due to staggered/wave starts
- Gun Result includes waiting time before crossing the start line
- Chip Result represents the participant's true running performance
- Using Gun Result would unfairly penalize participants who started in later waves

## Development Notes

- Race data is from a French running event with French field names and age categories
- The script automatically processes time formats and extracts age categories
- Generates PNG visualization files when run
- Supports comprehensive statistical analysis of race performance