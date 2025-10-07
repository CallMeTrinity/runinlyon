#!/usr/bin/env python3
"""
Run in Lyon Race Data Analysis Script

This script provides comprehensive analysis and visualization of race results data.
Features include general statistics, age-based analysis, placement visualizations,
and individual participant search functionality.
"""

import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from datetime import datetime, timedelta
import re
from typing import Optional, Dict, List, Tuple

class RaceAnalyzer:
    def __init__(self, json_file: str = "635.json"):
        """Initialize the race analyzer with data from JSON file."""
        self.data_file = json_file
        self.df = None
        self.load_data()
        
    def load_data(self):
        """Load and process race data from JSON file."""
        print("Loading race data...")
        
        with open(self.data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Extract headers
        headers = [h['csv_header'] for h in data['header']]
        
        # Create DataFrame
        self.df = pd.DataFrame(data['data'], columns=headers)
        
        # Clean and process data
        self._process_data()
        print(f"Data loaded successfully: {len(self.df)} participants")
    
    def _process_data(self):
        """Clean and process the loaded data."""
        # Convert numeric columns
        self.df['Bib'] = pd.to_numeric(self.df['Bib'], errors='coerce')
        self.df['Overall ranking'] = pd.to_numeric(self.df['Overall ranking'], errors='coerce')
        self.df['Gender Group Ranking'] = pd.to_numeric(self.df['Gender Group Ranking'], errors='coerce')
        self.df['Division Ranking'] = pd.to_numeric(self.df['Division Ranking'], errors='coerce')
        
        # Process time columns
        self.df['Gun Time Seconds'] = self.df['Gun Result'].apply(self._time_to_seconds)
        self.df['Chip Time Seconds'] = self.df['Chip Result'].apply(self._time_to_seconds)
        
        # Extract age categories from Division Name
        self.df['Age Category'] = self.df['Division Name'].apply(self._extract_age_category)
        self.df['Estimated Age'] = self.df['Division Name'].apply(self._estimate_age)
        
        # Clean names
        self.df['Full Name'] = self.df['First Name'] + ' ' + self.df['Last Name']
        
        print("Data processing completed.")
    
    def _time_to_seconds(self, time_str: str) -> Optional[int]:
        """Convert time string (HH:MM:SS) to seconds."""
        if not time_str or pd.isna(time_str):
            return None
        
        try:
            parts = time_str.split(':')
            if len(parts) == 3:
                hours, minutes, seconds = map(int, parts)
                return hours * 3600 + minutes * 60 + seconds
        except:
            pass
        return None
    
    def _seconds_to_time(self, seconds: int) -> str:
        """Convert seconds to HH:MM:SS format."""
        if pd.isna(seconds):
            return "N/A"
        
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    
    def _extract_age_category(self, division: str) -> str:
        """Extract age category from division name."""
        if pd.isna(division):
            return "Unknown"
        
        # Common French age categories
        categories = {
            'SE': 'Senior (23-39)',
            'M0': 'Master 0 (40-44)',
            'M1': 'Master 1 (45-49)',
            'M2': 'Master 2 (50-54)',
            'M3': 'Master 3 (55-59)',
            'M4': 'Master 4 (60-64)',
            'M5': 'Master 5 (65+)',
            'EH': 'Espoir/Junior (18-22)',
            'JH': 'Junior (16-19)',
            'U23': 'Under 23',
            'U20': 'Under 20'
        }
        
        for key, category in categories.items():
            if key in division:
                return category
        
        return division
    
    def _estimate_age(self, division: str) -> Optional[int]:
        """Estimate age from division name."""
        if pd.isna(division):
            return None
        
        # Age estimation based on category midpoints
        age_mapping = {
            'SE': 31,  # Senior midpoint
            'M0': 42,  # Master 0 midpoint
            'M1': 47,  # Master 1 midpoint
            'M2': 52,  # Master 2 midpoint
            'M3': 57,  # Master 3 midpoint
            'M4': 62,  # Master 4 midpoint
            'M5': 67,  # Master 5 estimated
            'EH': 20,  # Espoir midpoint
            'JH': 17,  # Junior midpoint
            'U23': 21, # Under 23
            'U20': 18  # Under 20
        }
        
        for key, age in age_mapping.items():
            if key in division:
                return age
        
        return None
    
    def general_statistics(self) -> Dict:
        """Calculate general race statistics."""
        stats = {}
        
        # Basic counts
        stats['total_participants'] = len(self.df)
        stats['total_finishers'] = len(self.df[self.df['Chip Time Seconds'].notna()])
        stats['male_participants'] = len(self.df[self.df['Gender'] == 'M'])
        stats['female_participants'] = len(self.df[self.df['Gender'] == 'F'])
        
        # Time statistics (using REAL times - Chip Result)
        # Real times are the actual race performance, excluding staggered start delays
        chip_times = self.df['Chip Time Seconds'].dropna()
        gun_times = self.df['Gun Time Seconds'].dropna()
        
        # Primary statistics use CHIP TIMES (real performance)
        if len(chip_times) > 0:
            stats['average_time'] = self._seconds_to_time(int(chip_times.mean()))
            stats['median_time'] = self._seconds_to_time(int(chip_times.median()))
            stats['fastest_time'] = self._seconds_to_time(int(chip_times.min()))
            stats['slowest_time'] = self._seconds_to_time(int(chip_times.max()))
        
        # Calculate average start delay (Gun - Chip)
        if len(chip_times) > 0 and len(gun_times) > 0:
            delays = gun_times - chip_times
            stats['average_start_delay'] = self._seconds_to_time(int(delays.mean()))
            stats['max_start_delay'] = self._seconds_to_time(int(delays.max()))
        
        # Nationality statistics
        stats['countries_represented'] = self.df['Nationality'].nunique()
        stats['top_nationalities'] = self.df['Nationality'].value_counts().head(5).to_dict()
        
        return stats
    
    def age_based_analysis(self) -> pd.DataFrame:
        """Analyze performance by age categories."""
        age_stats = []
        
        for category in self.df['Age Category'].unique():
            if pd.isna(category) or category == "Unknown":
                continue
                
            category_data = self.df[self.df['Age Category'] == category]
            
            if len(category_data) == 0:
                continue
            
            # Use CHIP TIMES (real performance) for age analysis
            chip_times = category_data['Chip Time Seconds'].dropna()
            
            if len(chip_times) > 0:
                age_stats.append({
                    'Age Category': category,
                    'Participants': len(category_data),
                    'Average Time': self._seconds_to_time(int(chip_times.mean())),
                    'Median Time': self._seconds_to_time(int(chip_times.median())),
                    'Best Time': self._seconds_to_time(int(chip_times.min())),
                    'Average Time (seconds)': int(chip_times.mean())
                })
        
        return pd.DataFrame(age_stats).sort_values('Average Time (seconds)')
    
    def gender_analysis(self) -> pd.DataFrame:
        """Analyze performance by gender."""
        gender_stats = []
        
        for gender in ['M', 'F']:
            gender_data = self.df[self.df['Gender'] == gender]
            # Use CHIP TIMES (real performance) for gender analysis
            chip_times = gender_data['Chip Time Seconds'].dropna()
            
            if len(chip_times) > 0:
                gender_stats.append({
                    'Gender': 'Male' if gender == 'M' else 'Female',
                    'Participants': len(gender_data),
                    'Average Time': self._seconds_to_time(int(chip_times.mean())),
                    'Median Time': self._seconds_to_time(int(chip_times.median())),
                    'Best Time': self._seconds_to_time(int(chip_times.min())),
                    'Average Time (seconds)': int(chip_times.mean())
                })
        
        return pd.DataFrame(gender_stats)
    
    def find_participant_by_bib(self, bib_number: int) -> Optional[Dict]:
        """Find participant by bib number and provide context."""
        participant = self.df[self.df['Bib'] == bib_number]
        
        if len(participant) == 0:
            return None
        
        p = participant.iloc[0]
        
        # Calculate percentile using CHIP TIMES (real performance)
        chip_time = p['Chip Time Seconds']
        if pd.notna(chip_time):
            better_times = len(self.df[self.df['Chip Time Seconds'] < chip_time])
            total_finishers = len(self.df[self.df['Chip Time Seconds'].notna()])
            percentile = (better_times / total_finishers) * 100
        else:
            percentile = None
        
        result = {
            'name': p['Full Name'],
            'bib': int(p['Bib']),
            'gender': p['Gender'],
            'nationality': p['Nationality'],
            'gun_time': p['Gun Result'],
            'chip_time': p['Chip Result'],
            'overall_ranking': int(p['Overall ranking']) if pd.notna(p['Overall ranking']) else None,
            'gender_ranking': int(p['Gender Group Ranking']) if pd.notna(p['Gender Group Ranking']) else None,
            'category': p['Division Name'],
            'category_ranking': int(p['Division Ranking']) if pd.notna(p['Division Ranking']) else None,
            'percentile': f"{percentile:.1f}%" if percentile is not None else None
        }
        
        return result
    
    def plot_time_distribution(self, save_fig: bool = True):
        """Plot distribution of finish times."""
        plt.figure(figsize=(12, 6))
        
        # Convert CHIP TIMES (real performance) to minutes for better readability
        chip_times_minutes = self.df['Chip Time Seconds'].dropna() / 60
        
        plt.subplot(1, 2, 1)
        plt.hist(chip_times_minutes, bins=50, alpha=0.7, edgecolor='black')
        plt.xlabel('Real Finish Time (minutes)')
        plt.ylabel('Number of Participants')
        plt.title('Distribution of Real Finish Times')
        plt.grid(True, alpha=0.3)
        
        plt.subplot(1, 2, 2)
        plt.boxplot(chip_times_minutes)
        plt.ylabel('Real Finish Time (minutes)')
        plt.title('Real Finish Time Box Plot')
        plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        if save_fig:
            plt.savefig('time_distribution.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    def plot_age_performance(self, save_fig: bool = True):
        """Plot performance by age category."""
        age_data = self.age_based_analysis()
        
        if len(age_data) == 0:
            print("No age data available for plotting.")
            return
        
        plt.figure(figsize=(12, 8))
        
        # Bar plot of average times by age category
        plt.subplot(2, 1, 1)
        bars = plt.bar(range(len(age_data)), age_data['Average Time (seconds)'] / 60)
        plt.xlabel('Age Category')
        plt.ylabel('Average Time (minutes)')
        plt.title('Average Finish Time by Age Category')
        plt.xticks(range(len(age_data)), age_data['Age Category'], rotation=45, ha='right')
        plt.grid(True, alpha=0.3)
        
        # Add value labels on bars
        for i, bar in enumerate(bars):
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height,
                    age_data.iloc[i]['Average Time'],
                    ha='center', va='bottom', fontsize=8)
        
        # Participants count by age category
        plt.subplot(2, 1, 2)
        plt.bar(range(len(age_data)), age_data['Participants'])
        plt.xlabel('Age Category')
        plt.ylabel('Number of Participants')
        plt.title('Participation by Age Category')
        plt.xticks(range(len(age_data)), age_data['Age Category'], rotation=45, ha='right')
        plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        if save_fig:
            plt.savefig('age_performance.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    def plot_gender_comparison(self, save_fig: bool = True):
        """Plot gender performance comparison."""
        plt.figure(figsize=(14, 6))
        
        # Box plot comparison using CHIP TIMES (real performance)
        plt.subplot(1, 2, 1)
        male_times = self.df[self.df['Gender'] == 'M']['Chip Time Seconds'].dropna() / 60
        female_times = self.df[self.df['Gender'] == 'F']['Chip Time Seconds'].dropna() / 60
        
        plt.boxplot([male_times, female_times], labels=['Male', 'Female'])
        plt.ylabel('Real Finish Time (minutes)')
        plt.title('Real Finish Time Comparison by Gender')
        plt.grid(True, alpha=0.3)
        
        # Histogram overlay
        plt.subplot(1, 2, 2)
        plt.hist(male_times, bins=30, alpha=0.7, label='Male', color='blue')
        plt.hist(female_times, bins=30, alpha=0.7, label='Female', color='red')
        plt.xlabel('Real Finish Time (minutes)')
        plt.ylabel('Number of Participants')
        plt.title('Real Time Distribution by Gender')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        if save_fig:
            plt.savefig('gender_comparison.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    def plot_nationality_analysis(self, save_fig: bool = True):
        """Plot nationality distribution and performance."""
        nationality_counts = self.df['Nationality'].value_counts().head(10)
        
        plt.figure(figsize=(14, 6))
        
        # Top nationalities participation
        plt.subplot(1, 2, 1)
        bars = plt.bar(range(len(nationality_counts)), nationality_counts.values)
        plt.xlabel('Nationality')
        plt.ylabel('Number of Participants')
        plt.title('Top 10 Nationalities by Participation')
        plt.xticks(range(len(nationality_counts)), nationality_counts.index, rotation=45)
        plt.grid(True, alpha=0.3)
        
        # Add value labels
        for i, bar in enumerate(bars):
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height,
                    str(int(height)), ha='center', va='bottom')
        
        # Average times by top nationalities
        plt.subplot(1, 2, 2)
        nationality_times = []
        top_nationalities = nationality_counts.head(5).index
        
        for nat in top_nationalities:
            # Use CHIP TIMES (real performance) for nationality analysis
            times = self.df[self.df['Nationality'] == nat]['Chip Time Seconds'].dropna()
            if len(times) > 0:
                nationality_times.append({
                    'Nationality': nat,
                    'Average Time (min)': times.mean() / 60,
                    'Count': len(times)
                })
        
        if nationality_times:
            nat_df = pd.DataFrame(nationality_times)
            bars = plt.bar(nat_df['Nationality'], nat_df['Average Time (min)'])
            plt.xlabel('Nationality')
            plt.ylabel('Average Real Time (minutes)')
            plt.title('Average Real Finish Time by Top 5 Nationalities')
            plt.xticks(rotation=45)
            plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        if save_fig:
            plt.savefig('nationality_analysis.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    def plot_time_comparison(self, save_fig: bool = True):
        """Plot comparison between Gun Time and Chip Time to show start delays."""
        plt.figure(figsize=(15, 10))
        
        # Filter out participants with both times
        both_times = self.df.dropna(subset=['Gun Time Seconds', 'Chip Time Seconds'])
        
        if len(both_times) == 0:
            print("No participants have both gun and chip times for comparison.")
            return
        
        # Calculate delays
        delays = both_times['Gun Time Seconds'] - both_times['Chip Time Seconds']
        
        # Plot 1: Scatter plot of Gun vs Chip times
        plt.subplot(2, 2, 1)
        plt.scatter(both_times['Chip Time Seconds'] / 60, both_times['Gun Time Seconds'] / 60, 
                   alpha=0.6, s=20)
        # Add perfect correlation line
        min_time = min(both_times['Chip Time Seconds'].min(), both_times['Gun Time Seconds'].min()) / 60
        max_time = max(both_times['Chip Time Seconds'].max(), both_times['Gun Time Seconds'].max()) / 60
        plt.plot([min_time, max_time], [min_time, max_time], 'r--', alpha=0.8, label='Perfect correlation')
        plt.xlabel('Temps Réel (minutes)')
        plt.ylabel('Temps Officiel (minutes)')
        plt.title('Temps Officiel vs Temps Réel')
        plt.grid(True, alpha=0.3)
        plt.legend()
        
        # Plot 2: Distribution of start delays
        plt.subplot(2, 2, 2)
        plt.hist(delays / 60, bins=50, alpha=0.7, edgecolor='black')
        plt.xlabel('Délai de départ (minutes)')
        plt.ylabel('Nombre de participants')
        plt.title('Distribution des délais de départ')
        plt.grid(True, alpha=0.3)
        
        # Plot 3: Delay vs finish position
        plt.subplot(2, 2, 3)
        valid_rankings = both_times.dropna(subset=['Overall ranking'])
        if len(valid_rankings) > 0:
            valid_delays = valid_rankings['Gun Time Seconds'] - valid_rankings['Chip Time Seconds']
            plt.scatter(valid_rankings['Overall ranking'], valid_delays / 60, alpha=0.6, s=20)
            plt.xlabel('Classement général')
            plt.ylabel('Délai de départ (minutes)')
            plt.title('Délai de départ selon le classement')
            plt.grid(True, alpha=0.3)
        
        # Plot 4: Box plot of delays by gender
        plt.subplot(2, 2, 4)
        male_delays = delays[both_times['Gender'] == 'M'] / 60
        female_delays = delays[both_times['Gender'] == 'F'] / 60
        
        plt.boxplot([male_delays, female_delays], labels=['Hommes', 'Femmes'])
        plt.ylabel('Délai de départ (minutes)')
        plt.title('Délais de départ par genre')
        plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        if save_fig:
            plt.savefig('time_comparison.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        # Print summary statistics
        print(f"\n📊 ANALYSE DES DÉLAIS DE DÉPART")
        print(f"Délai moyen: {self._seconds_to_time(int(delays.mean()))}")
        print(f"Délai médian: {self._seconds_to_time(int(delays.median()))}")
        print(f"Délai maximum: {self._seconds_to_time(int(delays.max()))}")
        print(f"Délai minimum: {self._seconds_to_time(int(delays.min()))}")
        print(f"Participants avec délai > 1 min: {len(delays[delays > 60]):,}")
        print(f"Participants avec délai > 5 min: {len(delays[delays > 300]):,}")
    
    def ranking_analysis(self, target_ranking: int) -> Dict:
        """Analyze performance around a specific ranking position."""
        if target_ranking < 1 or target_ranking > len(self.df):
            return {"error": "Invalid ranking position"}
        
        # Get participants around the target ranking
        window = 10
        start_rank = max(1, target_ranking - window)
        end_rank = min(len(self.df), target_ranking + window)
        
        ranking_window = self.df[
            (self.df['Overall ranking'] >= start_rank) & 
            (self.df['Overall ranking'] <= end_rank)
        ].sort_values('Overall ranking')
        
        result = {
            'target_ranking': target_ranking,
            'window_start': start_rank,
            'window_end': end_rank,
            'participants_in_window': []
        }
        
        for _, participant in ranking_window.iterrows():
            result['participants_in_window'].append({
                'ranking': int(participant['Overall ranking']),
                'name': participant['Full Name'],
                'bib': int(participant['Bib']),
                'time': participant['Gun Result'],
                'category': participant['Division Name'],
                'gender': participant['Gender']
            })
        
        return result
    
    def print_general_stats(self):
        """Print formatted general statistics."""
        stats = self.general_statistics()
        
        print("\n" + "="*60)
        print("         RUN IN LYON - RACE STATISTICS")
        print("="*60)
        
        print(f"\n📊 PARTICIPATION")
        print(f"Total Participants: {stats['total_participants']:,}")
        print(f"Total Finishers: {stats['total_finishers']:,}")
        print(f"Male Participants: {stats['male_participants']:,} ({stats['male_participants']/stats['total_participants']*100:.1f}%)")
        print(f"Female Participants: {stats['female_participants']:,} ({stats['female_participants']/stats['total_participants']*100:.1f}%)")
        
        print(f"\n⏱️  TIMING STATISTICS (Temps Réels)")
        print(f"Average Finish Time: {stats.get('average_time', 'N/A')}")
        print(f"Median Finish Time: {stats.get('median_time', 'N/A')}")
        print(f"Fastest Time: {stats.get('fastest_time', 'N/A')}")
        print(f"Slowest Time: {stats.get('slowest_time', 'N/A')}")
        
        print(f"\n🚀 START LINE ANALYSIS")
        print(f"Average Start Delay: {stats.get('average_start_delay', 'N/A')}")
        print(f"Maximum Start Delay: {stats.get('max_start_delay', 'N/A')}")
        print("(Délai = différence entre temps officiel et temps réel)")
        
        print(f"\n🌍 INTERNATIONAL PARTICIPATION")
        print(f"Countries Represented: {stats['countries_represented']}")
        print("Top 5 Nationalities:")
        for i, (country, count) in enumerate(stats['top_nationalities'].items(), 1):
            print(f"  {i}. {country}: {count} participants")
        
        print("\n" + "="*60)
    
    def generate_comprehensive_summary(self) -> pd.DataFrame:
        """Generate a comprehensive summary table with all key statistics."""
        summary_data = []
        
        # Get base statistics
        general_stats = self.general_statistics()
        age_stats = self.age_based_analysis()
        gender_stats = self.gender_analysis()
        
        # 1. OVERALL RACE STATISTICS
        summary_data.append(["=" * 50, "STATISTIQUES GÉNÉRALES DE LA COURSE", "=" * 50])
        summary_data.append(["Participants totaux", f"{general_stats['total_participants']:,}", ""])
        summary_data.append(["Arrivants", f"{general_stats['total_finishers']:,}", ""])
        summary_data.append(["Taux de finition", f"{(general_stats['total_finishers']/general_stats['total_participants']*100):.1f}%", ""])
        summary_data.append(["", "", ""])
        
        # 2. GENDER BREAKDOWN
        summary_data.append(["=" * 50, "RÉPARTITION PAR GENRE", "=" * 50])
        summary_data.append(["Hommes", f"{general_stats['male_participants']:,}", f"({general_stats['male_participants']/general_stats['total_participants']*100:.1f}%)"])
        summary_data.append(["Femmes", f"{general_stats['female_participants']:,}", f"({general_stats['female_participants']/general_stats['total_participants']*100:.1f}%)"])
        summary_data.append(["", "", ""])
        
        # 3. TIMING STATISTICS
        summary_data.append(["=" * 50, "PERFORMANCES TEMPORELLES", "=" * 50])
        summary_data.append(["Temps moyen", general_stats.get('average_time', 'N/A'), "(Temps réel)"])
        summary_data.append(["Temps médian", general_stats.get('median_time', 'N/A'), "(Temps réel)"])
        summary_data.append(["Meilleur temps", general_stats.get('fastest_time', 'N/A'), "(Temps réel)"])
        summary_data.append(["Temps le plus lent", general_stats.get('slowest_time', 'N/A'), "(Temps réel)"])
        summary_data.append(["", "", ""])
        
        # 4. START LINE DELAYS
        if 'average_start_delay' in general_stats:
            summary_data.append(["=" * 50, "ANALYSE DES DÉLAIS DE DÉPART", "=" * 50])
            summary_data.append(["Délai moyen de départ", general_stats.get('average_start_delay', 'N/A'), ""])
            summary_data.append(["Délai maximum", general_stats.get('max_start_delay', 'N/A'), ""])
            
            # Calculate additional delay statistics
            both_times = self.df.dropna(subset=['Gun Time Seconds', 'Chip Time Seconds'])
            if len(both_times) > 0:
                delays = both_times['Gun Time Seconds'] - both_times['Chip Time Seconds']
                delay_1min = len(delays[delays > 60])
                delay_5min = len(delays[delays > 300])
                summary_data.append(["Participants avec délai > 1min", f"{delay_1min:,}", f"({delay_1min/len(both_times)*100:.1f}%)"])
                summary_data.append(["Participants avec délai > 5min", f"{delay_5min:,}", f"({delay_5min/len(both_times)*100:.1f}%)"])
            summary_data.append(["", "", ""])
        
        # 5. GENDER PERFORMANCE COMPARISON
        if len(gender_stats) > 0:
            summary_data.append(["=" * 50, "COMPARAISON DES PERFORMANCES PAR GENRE", "=" * 50])
            for _, row in gender_stats.iterrows():
                summary_data.append([f"Temps moyen {row['Gender'].lower()}", row['Average Time'], f"({row['Participants']:,} participants)"])
                summary_data.append([f"Meilleur temps {row['Gender'].lower()}", row['Best Time'], ""])
            
            # Calculate gender time difference
            if len(gender_stats) == 2:
                male_avg = gender_stats[gender_stats['Gender'] == 'Male']['Average Time (seconds)'].iloc[0]
                female_avg = gender_stats[gender_stats['Gender'] == 'Female']['Average Time (seconds)'].iloc[0]
                diff_seconds = abs(male_avg - female_avg)
                diff_percentage = (diff_seconds / min(male_avg, female_avg)) * 100
                summary_data.append(["Écart moyen H/F", self._seconds_to_time(int(diff_seconds)), f"({diff_percentage:.1f}%)"])
            summary_data.append(["", "", ""])
        
        # 6. TOP 5 AGE CATEGORIES BY PERFORMANCE
        if len(age_stats) > 0:
            summary_data.append(["=" * 50, "TOP 5 CATÉGORIES D'ÂGE (PLUS RAPIDES)", "=" * 50])
            top_age_categories = age_stats.head(5)
            for i, (_, row) in enumerate(top_age_categories.iterrows(), 1):
                summary_data.append([f"{i}. {row['Age Category']}", row['Average Time'], f"({row['Participants']} participants)"])
            summary_data.append(["", "", ""])
        
        # 7. AGE CATEGORY PARTICIPATION
        if len(age_stats) > 0:
            summary_data.append(["=" * 50, "PARTICIPATION PAR CATÉGORIE D'ÂGE", "=" * 50])
            age_participation = age_stats.sort_values('Participants', ascending=False).head(5)
            for i, (_, row) in enumerate(age_participation.iterrows(), 1):
                total_participants = age_stats['Participants'].sum()
                percentage = (row['Participants'] / total_participants) * 100
                summary_data.append([f"{i}. {row['Age Category']}", f"{row['Participants']:,}", f"({percentage:.1f}%)"])
            summary_data.append(["", "", ""])
        
        # 8. INTERNATIONAL PARTICIPATION
        summary_data.append(["=" * 50, "PARTICIPATION INTERNATIONALE", "=" * 50])
        summary_data.append(["Pays représentés", f"{general_stats['countries_represented']}", ""])
        
        nationality_counts = self.df['Nationality'].value_counts().head(5)
        for i, (country, count) in enumerate(nationality_counts.items(), 1):
            percentage = (count / general_stats['total_participants']) * 100
            summary_data.append([f"{i}. {country}", f"{count:,}", f"({percentage:.1f}%)"])
        summary_data.append(["", "", ""])
        
        # 9. PERFORMANCE QUARTILES
        chip_times = self.df['Chip Time Seconds'].dropna()
        if len(chip_times) > 0:
            q1 = chip_times.quantile(0.25)
            q2 = chip_times.quantile(0.50)  # Median
            q3 = chip_times.quantile(0.75)
            
            summary_data.append(["=" * 50, "QUARTILES DE PERFORMANCE", "=" * 50])
            summary_data.append(["25% les plus rapides (Q1)", self._seconds_to_time(int(q1)), f"Moins de {self._seconds_to_time(int(q1))}"])
            summary_data.append(["50% (Médiane)", self._seconds_to_time(int(q2)), "Temps médian"])
            summary_data.append(["75% (Q3)", self._seconds_to_time(int(q3)), f"75% sous {self._seconds_to_time(int(q3))}"])
            summary_data.append(["", "", ""])
        
        # 10. FINISH TIME RANGES
        if len(chip_times) > 0:
            summary_data.append(["=" * 50, "RÉPARTITION DES TEMPS D'ARRIVÉE", "=" * 50])
            
            time_ranges = [
                ("Moins de 1h", 0, 3600),
                ("1h00 - 1h15", 3600, 4500),
                ("1h15 - 1h30", 4500, 5400),
                ("1h30 - 2h00", 5400, 7200),
                ("Plus de 2h", 7200, float('inf'))
            ]
            
            for range_name, min_time, max_time in time_ranges:
                if max_time == float('inf'):
                    count = len(chip_times[chip_times >= min_time])
                else:
                    count = len(chip_times[(chip_times >= min_time) & (chip_times < max_time)])
                percentage = (count / len(chip_times)) * 100
                summary_data.append([range_name, f"{count:,}", f"({percentage:.1f}%)"])
            summary_data.append(["", "", ""])
        
        # 11. PODIUM AND TOP PERFORMERS
        summary_data.append(["=" * 50, "PODIUM ET TOP PERFORMERS", "=" * 50])
        
        # Overall podium
        top_overall = self.df.nsmallest(3, 'Overall ranking')
        summary_data.append(["PODIUM GÉNÉRAL", "", ""])
        for i, (_, runner) in enumerate(top_overall.iterrows(), 1):
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉"
            summary_data.append([f"{medal} {i}e place", f"{runner['Full Name']}", f"{runner['Chip Result']} (Dossard {int(runner['Bib'])})"])
        
        # Top men and women
        top_men = self.df[self.df['Gender'] == 'M'].nsmallest(1, 'Chip Time Seconds')
        top_women = self.df[self.df['Gender'] == 'F'].nsmallest(1, 'Chip Time Seconds')
        
        if len(top_men) > 0:
            man = top_men.iloc[0]
            summary_data.append(["👨 Meilleur homme", f"{man['Full Name']}", f"{man['Chip Result']} (Dossard {int(man['Bib'])})"])
        
        if len(top_women) > 0:
            woman = top_women.iloc[0]
            summary_data.append(["👩 Meilleure femme", f"{woman['Full Name']}", f"{woman['Chip Result']} (Dossard {int(woman['Bib'])})"])
        
        # Create DataFrame
        summary_df = pd.DataFrame(summary_data, columns=['Métrique', 'Valeur', 'Détail'])
        return summary_df
    
    def print_comprehensive_summary(self):
        """Print a beautifully formatted comprehensive summary."""
        summary_df = self.generate_comprehensive_summary()
        
        print("\n" + "🏃‍♂️" * 30)
        print("🏃‍♂️" + " " * 26 + "RÉCAPITULATIF COMPLET - RUN IN LYON" + " " * 26 + "🏃‍♀️")
        print("🏃‍♀️" + "=" * 86 + "🏃‍♂️")
        
        for _, row in summary_df.iterrows():
            metric = row['Métrique']
            value = row['Valeur']
            detail = row['Détail']
            
            # Handle section headers
            if metric.startswith('='):
                print(f"\n🔥 {value}")
                print("─" * 88)
            elif metric == "":
                continue
            else:
                # Format the line nicely
                if detail:
                    print(f"{metric:<35} │ {value:<20} │ {detail}")
                else:
                    print(f"{metric:<35} │ {value:<20}")
        
        print("\n" + "🏃‍♀️" + "=" * 86 + "🏃‍♂️")
        print("🏃‍♂️" + " " * 30 + "FIN DU RÉCAPITULATIF" + " " * 30 + "🏃‍♀️")
        print("🏃‍♀️" * 30)
        
        # Save to CSV for Excel
        csv_filename = "run_in_lyon_summary.csv"
        summary_df.to_csv(csv_filename, index=False, encoding='utf-8')
        print(f"\n💾 Récapitulatif sauvegardé en: {csv_filename}")
    
    def save_summary_excel(self, filename: str = "run_in_lyon_summary.xlsx"):
        """Save comprehensive summary to Excel with better formatting."""
        try:
            summary_df = self.generate_comprehensive_summary()
            
            # Remove section separators for cleaner Excel export
            clean_df = summary_df[~summary_df['Métrique'].str.startswith('=')]
            clean_df = clean_df[clean_df['Métrique'] != '']
            
            clean_df.to_excel(filename, index=False, encoding='utf-8')
            print(f"\n📊 Récapitulatif Excel sauvegardé: {filename}")
            
        except ImportError:
            print("\n⚠️ Openpyxl non installé. Installation recommandée: pip install openpyxl")
            print("Sauvegarde CSV disponible à la place.")
        except Exception as e:
            print(f"\n❌ Erreur lors de la sauvegarde Excel: {e}")


def main():
    """Main function demonstrating the race analyzer capabilities."""
    # Initialize analyzer
    analyzer = RaceAnalyzer()
    
    # Print general statistics
    analyzer.print_general_stats()
    
    # Age-based analysis
    print("\n📈 AGE CATEGORY ANALYSIS")
    age_stats = analyzer.age_based_analysis()
    print(age_stats.to_string(index=False))
    
    # Gender analysis
    print("\n👥 GENDER ANALYSIS")
    gender_stats = analyzer.gender_analysis()
    print(gender_stats.to_string(index=False))
    
    # Example: Find participant by bib number
    print("\n🔍 PARTICIPANT SEARCH EXAMPLE (Bib #12005)")
    participant = analyzer.find_participant_by_bib(12005)
    if participant:
        print(f"Name: {participant['name']}")
        print(f"Overall Ranking: {participant['overall_ranking']}")
        print(f"Real Finish Time: {participant['chip_time']}")
        print(f"Official Time: {participant['gun_time']}")
        print(f"Percentile: {participant['percentile']}")
    
    # Generate visualizations
    print("\n📊 Generating visualizations...")
    analyzer.plot_time_distribution()
    analyzer.plot_age_performance() 
    analyzer.plot_gender_comparison()
    analyzer.plot_nationality_analysis()
    analyzer.plot_time_comparison()  # New: Gun vs Chip time analysis
    
    # Generate comprehensive summary
    print("\n" + "="*60)
    print("         GÉNÉRATION DU RÉCAPITULATIF COMPLET")
    print("="*60)
    analyzer.print_comprehensive_summary()
    
    print("\n✅ Analysis complete! Check the generated files:")
    print("📊 VISUALIZATIONS:")
    print("- time_distribution.png: Distribution des temps réels")
    print("- age_performance.png: Performance par catégorie d'âge")
    print("- gender_comparison.png: Comparaison hommes/femmes")
    print("- nationality_analysis.png: Analyse par nationalité")
    print("- time_comparison.png: Comparaison temps officiels vs réels")
    print("\n📋 DATA EXPORT:")
    print("- run_in_lyon_summary.csv: Récapitulatif complet (Excel compatible)")


if __name__ == "__main__":
    main()