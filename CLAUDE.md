# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a comprehensive "Run in Lyon" race data analysis and visualization project with both web application and Python analysis tools. The project contains:
- **Web Application**: Interactive race results explorer (in `web/` directory)
- **Python Analysis**: Comprehensive data analysis and visualization scripts (in `analysis/` directory)
- **Race Data**: Multiple race datasets in JSON format (in `data/` directory)
- **Documentation**: Setup and usage instructions

## Development Environment

- **Python Version**: 3.12.3
- **Dependencies**: pandas, matplotlib, seaborn, numpy, openpyxl (see requirements.txt)

## Setup and Installation

### Install dependencies
```bash
pip install -r requirements.txt
```

## Common Commands

### Run the web application
```bash
# Start a local server from the project root
python -m http.server 8000
# Then open http://localhost:8000/web/
```

### Run comprehensive race analysis
```bash
python analysis/race_analysis.py
```

### Run summary example only
```bash
python analysis/summary_example.py
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
├── web/                          # Web application
│   ├── index.html               # Main HTML file with accessibility features
│   ├── app.js                   # JavaScript with toast notifications, URL params, etc.
│   └── styles.css               # Responsive styling with loading states
├── data/                        # Race data files
│   ├── 635.json                # Half Marathon (21K) results
│   ├── 636.json                # Marathon (42K) results
│   └── 639.json                # 10K results
├── analysis/                    # Python analysis scripts
│   ├── race_analysis.py        # Main analysis script
│   └── summary_example.py      # Example usage
├── requirements.txt            # Python dependencies
├── CLAUDE.md                   # This documentation file
├── README.md                   # Comprehensive project documentation
├── .gitignore                  # Git ignore rules
└── Generated files:
    ├── *.png                   # Visualization charts
    ├── run_in_lyon_summary.csv # Complete summary (CSV format)
    └── *.xlsx                  # Excel summaries (if openpyxl installed)
```

## Web Application Features

The web application (`web/index.html`) provides:

### Interactive Features
- **Search**: Search by bib number or participant name
- **Race Selection**: Switch between 10K, Half Marathon (21K), and Marathon (42K)
- **Detailed Results**: View comprehensive participant statistics with pace calculation
- **Share & Export**: Copy shareable URLs, print results
- **Toast Notifications**: User-friendly notifications instead of alerts
- **Loading States**: Spinner overlays during data loading
- **Keyboard Navigation**: ESC to clear, Enter to search
- **Accessibility**: ARIA labels and screen reader support

### Data Visualization
- Time distribution charts
- Performance by age category
- Gender distribution
- Top nationalities
- Filter by gender, category, and nationality

## Python Analysis Features

The `analysis/race_analysis.py` script provides:

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
from analysis.race_analysis import RaceAnalyzer

# Initialize analyzer
analyzer = RaceAnalyzer('data/639.json')

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