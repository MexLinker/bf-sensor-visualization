import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
import matplotlib.cm as cm
import matplotlib.colors as mcolors
import os

file_path = 'data.csv'

if not os.path.exists(file_path):
    print(f"Error: {file_path} not found")
    exit()

try:
    df = pd.read_csv(file_path, sep=None, engine='python')
except:
    df = pd.read_csv(file_path, sep='\t')

time_col = None
temp_col = None

for col in df.columns:
    if any(k in col.lower() for k in ['time', 'changed', 'date']):
        time_col = col
    if any(k in col.lower() for k in ['temp', 'state', 'value']):
        temp_col = col

if time_col is None:
    time_col = df.columns[-1]
if temp_col is None:
    temp_col = df.columns[1]

df[time_col] = pd.to_datetime(df[time_col], errors='coerce')
df[temp_col] = pd.to_numeric(df[temp_col], errors='coerce')
df = df.dropna(subset=[time_col, temp_col])
df.set_index(time_col, inplace=True)

def plot_distribution(data_df, interval, filename):
    grouped = data_df.groupby(pd.Grouper(freq=interval))
    counts = grouped.size()
    avg_temps = grouped[temp_col].mean()
    
    mask = counts > 0
    counts = counts[mask]
    avg_temps = avg_temps[mask]
    
    if len(counts) == 0:
        return
    
    # FIX: Calculate width as 95% of interval to make bars wider and touch each other
    if interval == '5min':
        interval_days = 5 / (24 * 60)
    elif interval == '20min':
        interval_days = 20 / (24 * 60)
    elif interval == '60min':
        interval_days = 60 / (24 * 60)
    else:
        interval_days = 5 / (24 * 60)
    
    width = interval_days * 0.95  # 95% width fills space nicely
    
    temp_min, temp_max = data_df[temp_col].min(), data_df[temp_col].max()
    norm = mcolors.Normalize(vmin=temp_min, vmax=temp_max)
    cmap = cm.RdYlBu_r
    
    fig, ax = plt.subplots(figsize=(14, 6))
    
    for timestamp, count in counts.items():
        temp = avg_temps.loc[timestamp]
        color = cmap(norm(temp))
        ax.bar(timestamp, count, width=width, color=color, 
               edgecolor='none', alpha=0.9)
        
        if len(counts) <= 15:
            ax.text(timestamp, count, f'{int(count)}', 
                   ha='center', va='bottom', fontsize=9)
    
    ax.xaxis.set_major_locator(mticker.MaxNLocator(6))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
    
    ax.set_xlabel(f'Time ({interval})', fontsize=11)
    ax.set_ylabel('Number of Data Points', fontsize=11)
    ax.set_title(f'Distribution ({interval})', fontsize=13, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='y')
    
    sm = cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=ax, pad=0.02)
    cbar.set_label(f'Temperature ({temp_min:.1f} ~ {temp_max:.1f})', fontsize=10)
    
    plt.tight_layout()
    plt.subplots_adjust(bottom=0.2)
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    print(f"Saved: {filename}")
    plt.show()

plot_distribution(df, '5min', 'dist_5min.png')
plot_distribution(df, '20min', 'dist_20min.png')
plot_distribution(df, '60min', 'dist_60min.png')