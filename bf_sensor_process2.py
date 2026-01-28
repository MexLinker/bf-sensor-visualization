import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
import os

file_path = 'data.csv'

if not os.path.exists(file_path):
    print(f"Error: {file_path} not found")
    exit()

# Read data
try:
    df = pd.read_csv(file_path, sep=None, engine='python')
except:
    df = pd.read_csv(file_path, sep='\t')

# Find time column
time_col = None
for col in df.columns:
    if any(k in col.lower() for k in ['time', 'changed', 'date']):
        time_col = col
        break
if time_col is None:
    time_col = df.columns[-1]

# Process time
df[time_col] = pd.to_datetime(df[time_col], errors='coerce')
df = df.dropna(subset=[time_col])
df.set_index(time_col, inplace=True)

def plot_distribution(data_df, interval, color, filename):
    counts = data_df.groupby(pd.Grouper(freq=interval)).size()
    counts = counts[counts > 0]
    
    if len(counts) == 0:
        return
        
    fig, ax = plt.subplots(figsize=(14, 6))
    
    # Plot bars
    width = 0.003 if len(counts) < 40 else 0.001
    bars = ax.bar(counts.index, counts.values, width=width, 
                  color=color, edgecolor='black', alpha=0.7)
    
    # === FIX: Limit x-axis ticks to prevent overlap ===
    ax.xaxis.set_major_locator(mticker.MaxNLocator(6))  # Max 6 labels
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    
    # Rotate labels
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
    ax.tick_params(axis='x', labelsize=9)
    
    # Add count labels on bars (only if few bars)
    if len(counts) <= 15:
        for bar, val in zip(bars, counts.values):
            ax.text(bar.get_x() + bar.get_width()/2., val,
                    f'{int(val)}', ha='center', va='bottom', fontsize=9)
    
    ax.set_xlabel(f'Time ({interval})', fontsize=11)
    ax.set_ylabel('Count', fontsize=11)
    ax.set_title(f'Distribution ({interval} intervals)', fontsize=13, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.subplots_adjust(bottom=0.2)
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    print(f"Saved: {filename} ({len(counts)} bins)")
    plt.show()

# Generate all 3
plot_distribution(df, '5min', 'steelblue', 'dist_5min.png')
plot_distribution(df, '20min', 'coral', 'dist_20min.png')
plot_distribution(df, '60min', 'mediumseagreen', 'dist_60min.png')