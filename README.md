i

```markdown
# Sensor Data Visualizer

Visualize IoT sensor data as time-based histograms with temperature color coding.

## Usage

```bash
python bf_sensor_visualiztion.py
```

Input: `data.csv` with columns `[entity_id, temperature, timestamp]`

Output: 4 PNG files (1min/5min/20min/60min intervals)

## Features

- **Auto-detection**: Flexible column naming
- **Color coding**: Red (hot) → Blue (cold)
- **Anti-overlap**: Max 8 x-axis labels
- **Wide bars**: 95% fill for clear visualization

## Requirements

```bash
pip install pandas matplotlib
```

## Input Format

```
sensor.te_0904  26.93  2026-01-19T13:52:10.882Z
sensor.te_0904  26.86  2026-01-19T13:52:

