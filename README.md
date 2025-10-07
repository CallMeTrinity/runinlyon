# 🏃 Run in Lyon - Race Results Explorer

A comprehensive web application and Python analysis toolkit for exploring and analyzing "Run in Lyon" race results data.

![Python](https://img.shields.io/badge/Python-3.12.3-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## 📋 Table of Contents

- [Features](#features)
- [Project Structure](#project-structure)
- [Quick Start](#quick-start)
- [Web Application](#web-application)
- [Python Analysis](#python-analysis)
- [Data Structure](#data-structure)
- [Usage Examples](#usage-examples)
- [Technologies](#technologies)
- [Contributing](#contributing)

## ✨ Features

### Web Application
- **Interactive Search**: Search by bib number or participant name
- **Detailed Results**: View comprehensive participant statistics including:
  - Chip time (real time) and gun time (official time)
  - Pace per kilometer
  - Overall, gender, and category rankings
  - Performance percentiles
- **Data Visualization**: Interactive charts powered by Chart.js
  - Time distribution histograms
  - Performance by age category
  - Gender distribution
  - International participation
- **Filtering**: Filter results by gender, category, and nationality
- **Leaderboard**: View top 50 participants overall, by gender
- **Share & Export**:
  - Copy shareable links to specific results
  - Print individual results
  - URL parameter support for direct access
- **Accessibility**:
  - ARIA labels for screen readers
  - Keyboard navigation (ESC to clear)
  - Toast notifications instead of alerts
- **Responsive Design**: Works on desktop, tablet, and mobile devices

### Python Analysis Tools
- **Statistical Analysis**: Calculate comprehensive race statistics
- **Visualizations**: Generate publication-quality charts with matplotlib and seaborn
- **Age Category Analysis**: Performance breakdown by French age categories
- **Data Export**: Save summaries to CSV and Excel formats
- **Participant Lookup**: Find and analyze individual participant performance

## 📁 Project Structure

```
runinlyon/
├── web/                          # Web application
│   ├── index.html               # Main HTML file
│   ├── app.js                   # JavaScript application logic
│   └── styles.css               # Styling and responsive design
├── data/                        # Race data files
│   ├── 635.json                # Half Marathon (21K) results
│   ├── 636.json                # Marathon (42K) results
│   └── 639.json                # 10K results
├── analysis/                    # Python analysis scripts
│   ├── race_analysis.py        # Main analysis script
│   └── summary_example.py      # Example usage
├── start_server.py             # Quick start server script
├── requirements.txt            # Python dependencies
├── CLAUDE.md                   # Development documentation
├── .gitignore                  # Git ignore rules
└── README.md                   # This file
```

## 🚀 Quick Start

### Web Application

**Option 1: Quick Start Script** (Recommended)
```bash
python start_server.py
# Automatically starts server and opens browser
```

**Option 2: Manual Server Start**
```bash
python -m http.server 8000
# Then open http://localhost:8000/web/
```

**Option 3: Direct File Open** (Limited functionality due to CORS)
```bash
# Navigate to the web directory and open index.html in a browser
cd web
# On Windows: start index.html
# On Mac: open index.html
# On Linux: xdg-open index.html
```

### Python Analysis

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the analysis**:
   ```bash
   python analysis/race_analysis.py
   ```

3. **View the example**:
   ```bash
   python analysis/summary_example.py
   ```

## 🌐 Web Application

### Features

#### Search Functionality
- **By Bib Number**: Direct lookup using race bib number
- **By Name**: Search by first or last name (supports partial matches)
- **Multiple Matches**: If multiple participants match, select from a list

#### Race Selection
Switch between three race distances:
- **10K** (default)
- **Half Marathon (21K)**
- **Marathon (42K)**

#### Participant Results Display
When viewing a participant's results, you'll see:
- **Personal Information**: Name, bib number, gender, category, nationality
- **Times**:
  - Chip time (actual running time)
  - Gun time (official time from race start)
  - Pace per kilometer
  - Start delay calculation
- **Rankings**:
  - Overall ranking and percentile
  - Gender ranking and percentile
  - Category ranking and percentile
- **Actions**:
  - Print results
  - Share link (copy to clipboard)
  - Clear search

#### Keyboard Shortcuts
- **Enter**: Execute search
- **ESC**: Clear search results

#### URL Sharing
Share results using URL parameters:
```
https://yoursite.com/web/?bib=12005
```

## 🐍 Python Analysis

### RaceAnalyzer Class

```python
from analysis.race_analysis import RaceAnalyzer

# Initialize analyzer
analyzer = RaceAnalyzer('data/635.json')

# Get statistics
stats = analyzer.general_statistics()
print(f"Total participants: {stats['total_participants']}")
print(f"Average time: {stats['avg_time']}")

# Find participant
participant = analyzer.find_participant_by_bib(12005)
print(f"{participant['name']}: {participant['chipResult']}")

# Generate visualizations
analyzer.plot_time_distribution()
analyzer.plot_age_performance()
analyzer.plot_gender_comparison()
analyzer.plot_nationality_analysis()
analyzer.plot_time_comparison()

# Export comprehensive summary
analyzer.print_comprehensive_summary()
summary_df = analyzer.generate_comprehensive_summary()
analyzer.save_summary_excel('race_summary.xlsx')
```

### Analysis Features

- **General Statistics**: Total participants, gender distribution, time statistics
- **Age Category Analysis**: Performance by French age categories (Senior, Master 0-5, Espoir, Junior)
- **Time Analysis**: Chip vs Gun time comparison, start delay analysis
- **International Analysis**: Participation by nationality
- **Performance Quartiles**: Distribution of finish times
- **Podium Results**: Top 3 finishers

## 📊 Data Structure

Race data is stored in JSON format with the following structure:

```json
{
  "header": {
    "0": "Registration ID",
    "1": "Bib",
    "2": "Last Name",
    "3": "First Name",
    "4": "Gender",
    "5": "Nationality",
    "6": "Gun Result",
    "7": "Chip Result",
    "8": "Overall Rank",
    "9": "Gender Rank",
    "10": "Category",
    "11": "Category Rank"
  },
  "data": [
    [/* participant data arrays */]
  ]
}
```

### Important Time Measurements

- **Gun Result (Temps Officiel)**: Time from official race start to finish
- **Chip Result (Temps Réel)**: ACTUAL race time from crossing start line to finish

**Note**: All analysis prioritizes Chip Result as it represents true running performance, accounting for wave starts and start line delays.

## 🛠 Technologies

### Web Application
- **HTML5**: Semantic markup with accessibility features
- **CSS3**: Modern styling with CSS Grid and Flexbox
- **Vanilla JavaScript**: No frameworks, pure JS
- **Chart.js**: Interactive data visualizations
- **Responsive Design**: Mobile-first approach

### Python Analysis
- **Python 3.12.3**
- **pandas**: Data manipulation and analysis
- **matplotlib**: Data visualization
- **seaborn**: Statistical visualizations
- **numpy**: Numerical computing
- **openpyxl**: Excel file export

## 📝 Usage Examples

### Web Application Examples

1. **Search for your results**:
   - Enter your bib number and click "Search"
   - Or enter your name and click "Search by Name"

2. **Share your results**:
   - Search for your results
   - Click "Share Link" button
   - Send the copied link to friends

3. **Compare different races**:
   - Click on different race buttons (10K, 21K, 42K)
   - View how participation and performance differ

4. **Explore statistics**:
   - Scroll down to view overall race statistics
   - Use filters to narrow down by gender, category, or nationality
   - View interactive charts showing data distributions

### Python Analysis Examples

```python
# Example 1: Quick statistics
from analysis.race_analysis import RaceAnalyzer

analyzer = RaceAnalyzer('data/639.json')
stats = analyzer.general_statistics()
print(f"Fastest time: {stats['fastest_time']}")

# Example 2: Age category analysis
age_stats = analyzer.age_category_analysis()
for category, data in age_stats.items():
    print(f"{category}: {data['count']} participants, avg {data['avg_time']}")

# Example 3: Export to Excel
analyzer.save_summary_excel('10k_summary.xlsx')
```

## 🤝 Contributing

Contributions are welcome! Here are some ways you can contribute:

1. **Report bugs**: Open an issue describing the bug
2. **Suggest features**: Open an issue with feature requests
3. **Submit pull requests**: Fix bugs or add new features

## 📄 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- Race data provided by Run in Lyon organizers
- Built with modern web technologies and Python data science tools
- Designed for runners, by runners

## 📧 Support

For questions or support, please open an issue on the project repository.

---

**Happy Running! 🏃‍♂️🏃‍♀️**
