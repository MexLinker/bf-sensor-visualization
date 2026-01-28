import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os

# ============== 1. 读取当前文件夹下的 data.csv ==============
file_path = 'data.csv'

# 检查文件是否存在
if not os.path.exists(file_path):
    print(f"❌ 错误：在当前文件夹下找不到 {file_path}")
    print(f"当前工作目录: {os.getcwd()}")
    print("请确保 data.csv 文件与此脚本在同一目录下")
    exit()

try:
    # 尝试读取CSV，自动检测分隔符（支持逗号、 Tab、空格等）
    df = pd.read_csv(file_path, sep=None, engine='python')
    print(f"✅ 成功读取数据，共 {len(df)} 行")
    
except Exception as e:
    print(f"❌ 读取文件失败: {e}")
    exit()

# ============== 2. 识别时间列 ==============
# 自动寻找可能的时间列（last_changed、timestamp、time、date等）
time_col = None
possible_names = ['last_changed', 'timestamp', 'time', 'date', 'datetime', '时间']

for col in df.columns:
    if col.lower() in possible_names or 'time' in col.lower() or 'date' in col.lower():
        time_col = col
        break

if time_col is None:
    print("可用的列:", df.columns.tolist())
    # 如果没有识别到，默认使用第3列（索引2）或最后一列
    time_col = df.columns[-1]
    print(f"⚠️ 未识别到标准时间列，将使用最后一列: {time_col}")

print(f"使用 '{time_col}' 作为时间列")

# ============== 3. 数据处理 ==============
try:
    # 转换时间为datetime格式
    df[time_col] = pd.to_datetime(df[time_col], errors='coerce')
    
    # 删除无法解析的时间行
    invalid_rows = df[time_col].isna().sum()
    if invalid_rows > 0:
        print(f"⚠️ 警告: 有 {invalid_rows} 行时间格式无法解析，将被忽略")
        df = df.dropna(subset=[time_col])
    
    # 设置为索引
    df.set_index(time_col, inplace=True)
    
    # 按5分钟分箱统计
    counts = df.groupby(pd.Grouper(freq='5min')).size()
    
    print(f"\n📊 时间分布统计:")
    for timestamp, count in counts.items():
        if count > 0:
            print(f"   {timestamp.strftime('%m-%d %H:%M')}: {count} 个数据点")
    
except Exception as e:
    print(f"❌ 数据处理失败: {e}")
    exit()

# ============== 4. 可视化 ==============
if len(counts) == 0 or counts.sum() == 0:
    print("❌ 没有有效数据可供可视化")
    exit()

fig, ax = plt.subplots(figsize=(14, 6))

# 绘制柱状图 - 使用更合适的宽度
# 如果是时间数据，宽度需要根据时间间隔调整
bars = ax.bar(counts.index, counts.values, width=0.003, 
              color='steelblue', edgecolor='black', alpha=0.7, align='center')

# 设置x轴格式为时间
ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H:%M'))
ax.xaxis.set_major_locator(mdates.MinuteLocator(interval=5))

# 自动旋转标签以防重叠
plt.xticks(rotation=45)

# 在柱子上方添加数值标签（仅当柱子数量不多于30个时，避免拥挤）
if len(counts[counts > 0]) <= 30:
    for bar, value in zip(bars, counts.values):
        if value > 0:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(value)}', ha='center', va='bottom', fontsize=9)

ax.set_xlabel('时间 (每5分钟一格)', fontsize=12)
ax.set_ylabel('传感器数据点数量', fontsize=12)
ax.set_title('传感器数据时间分布统计 (5分钟间隔)', fontsize=14, fontweight='bold')

# 添加网格线，仅在y轴
ax.grid(True, alpha=0.3, linestyle='--', axis='y')
ax.set_axisbelow(True)

# 自动调整布局
plt.tight_layout()

# 保存图表
output_file = 'sensor_distribution.png'
plt.savefig(output_file, dpi=150, bbox_inches='tight')
print(f"\n✅ 图表已保存为: {output_file}")

# 显示图表
plt.show()

# ============== 5. 输出统计摘要 ==============
print(f"\n📈 统计摘要:")
print(f"   总数据点数: {len(df)}")
print(f"   时间跨度: {df.index.min().strftime('%Y-%m-%d %H:%M')} 至 {df.index.max().strftime('%Y-%m-%d %H:%M')}")
print(f"   5分钟区间数: {len(counts)}")
print(f"   平均每区间点数: {len(df)/len(counts):.1f}")
print(f"   最大点数区间: {counts.idxmax().strftime('%H:%M')} ({counts.max()}个)")