import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.manifold import TSNE  # 导入 t-SNE
import matplotlib
import matplotlib.pyplot as plt
from matplotlib import rcParams
from sklearn.cluster import KMeans

# 设置支持中文的字体
rcParams['font.sans-serif'] = ['SimHei']
rcParams['axes.unicode_minus'] = False
matplotlib.use('TkAgg')

# 读取数据
data = pd.read_excel('data/data.xlsx')

# 对成交日期列进行处理（转换为年月形式）
def convert_to_month(year_decimal):
    year = int(year_decimal)  # 获取年份
    decimal = year_decimal - year  # 获取小数部分
    month = round(decimal * 12) + 1  # 小数部分乘以12，得到月份（1到12月）
    return f"{year}.{month:02d}"  # 返回YYYY.MM格式

# 对成交日期进行转换处理
data['成交日期'] = data['成交日期'].apply(convert_to_month)
data['成交日期'] = pd.to_datetime(data['成交日期'], format='%Y.%m')
# a.生成新列（增长率-成交量）：相邻月份，后一月相较前一月的成交量增长率
grouped = data.groupby(data['成交日期'].dt.to_period('M'))  # 按年月分组

# 增长率计算函数（增加异常处理）
def calculate_growth_rate(current, previous):
    if previous is None or previous == 0 or pd.isnull(previous) or pd.isnull(current):
        return 0.0  # 如果前一月数据为空或为0，则增长率置为0.0
    return (current - previous) / previous

# 计算成交量增长率
data['成交量'] = grouped.size()
prev_vol = data['成交量'].shift(1)
data['成交量增长率'] = [
    calculate_growth_rate(curr, prev)
    for curr, prev in zip(data['成交量'], prev_vol)
]

data['成交量增长率'] = data['成交量增长率'].fillna(0.0)

# b. 将成交日期转换成数值（时间戳）
data['成交日期数值'] = (data['成交日期'].astype('int64') // 10**9)

X = data.drop(['No', '房价', '成交日期'], axis=1)  # 除标签外的所有列
X.fillna(0.0, inplace=True) # 检查是否有 NaN 或空值，填充为 0.0
y = data['房价']  # 标签列

# 数据清洗：缺失值（无）、标准化（最大最小）
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# # t-SNE降维分析 (三维)
# tsne = TSNE(n_components=3, random_state=42)  # 使用3维空间进行可视化
# X_tsne = tsne.fit_transform(X_scaled)
#
# # 可视化降维后的数据分布 (三维)
# fig = plt.figure(figsize=(10, 8))
# ax = fig.add_subplot(111, projection='3d')
# ax.scatter(X_tsne[:, 0], X_tsne[:, 1], X_tsne[:, 2], alpha=0.7, c='blue', edgecolor='k')
# ax.set_xlabel('t-SNE维度1', fontsize=12)
# ax.set_ylabel('t-SNE维度2', fontsize=12)
# ax.set_zlabel('t-SNE维度3', fontsize=12)
# ax.set_title('t-SNE降维后的数据分布 (三维)', fontsize=14)
# plt.savefig('t-SNE降维后数据分布_三维.png')
# plt.show()

# t-SNE降维分析 (二维)
tsne = TSNE(n_components=2, random_state=42)  # 使用2维空间进行可视化
X_tsne = tsne.fit_transform(X_scaled)

# 可视化降维后的数据分布 (二维)
plt.figure(figsize=(10, 6))
plt.scatter(X_tsne[:, 0], X_tsne[:, 1], alpha=0.7, c='blue', edgecolor='k')
plt.xlabel('t-SNE维度1', fontsize=12)
plt.ylabel('t-SNE维度2', fontsize=12)
plt.title('t-SNE降维后的数据分布 (二维)', fontsize=14)
plt.grid(alpha=0.5)
plt.savefig('t-SNE降维后数据分布_二维.png')
plt.show()
