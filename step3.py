import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime
import matplotlib.font_manager as fm

# Specify a font that supports the required glyphs
plt.rcParams['font.family'] = 'Arial Unicode MS'

def generate_timeline_charts(timeline_data, timeline_file):
    # Read timestamps from the TXT file
    with open(timeline_data, 'r') as file:
        timestamps = [line.strip() for line in file if line.strip()]

    # Convert timestamps to datetime objects
    timestamps = [datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ") for ts in timestamps]

    # Create a DataFrame with timestamps
    df = pd.DataFrame({'Timestamp': timestamps})

    # Count occurrences in each month
    df['Month'] = df['Timestamp'].dt.to_period('M')
    monthly_counts = df['Month'].value_counts().sort_index()

    # Create a bar chart
    plt.figure(figsize=(10, 6))
    monthly_counts.plot(kind='bar', color='skyblue')
    plt.xlabel('Month')
    plt.ylabel('Event Count')
    plt.title(f'Monthly Comment Counts for "{search_query}"')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(timeline_file)
    plt.show()

if __name__ == "__main__":
    # Input search query and output file name
    search_query = "動物救援"
    theme = search_query.replace(' ', '_')

    # Initialize file paths
    timeline_data = f"Tempfile/{theme}_timeline.txt"
    timeline_file = f"OUTPUT/{theme}_timeline.png"

    generate_timeline_charts(timeline_data, timeline_file)
