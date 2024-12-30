# PCA降维分析
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
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

# 方差贡献分析——确定保留的主成分个数
pca = PCA()
pca.fit(X_scaled)
explained_variance_ratio = pca.explained_variance_ratio_
cumulative_explained_variance_ratio = []
total = 0
for ratio in explained_variance_ratio:
    total += ratio
    cumulative_explained_variance_ratio.append(total)

# 可视化主成分的解释方差贡献率
plt.figure(figsize=(10, 6))
bars = plt.bar(
    range(1, len(explained_variance_ratio) + 1),
    explained_variance_ratio,
    tick_label=[f"PC{i}" for i in range(1, len(explained_variance_ratio) + 1)],
    color='skyblue',
)

for bar, ratio in zip(bars, explained_variance_ratio):
    height = bar.get_height()
    plt.text(
        bar.get_x() + bar.get_width() / 2,
        height,
        f"{ratio:.2%}",
        ha='center',
        va='bottom',
        fontsize=10,
    )

plt.xlabel('主成分', fontsize=12)
plt.ylabel('解释方差贡献率', fontsize=12)
plt.title('主成分的解释方差贡献率', fontsize=14)
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.savefig('PCA主成分分析图.png')
plt.show()

# 主成分的加载矩阵
loading_matrix = pd.DataFrame(
    pca.components_,  # PCA分解后的权重矩阵
    columns=X.columns,  # 原始特征名称
    index=[f"PC{i}" for i in range(1, len(pca.components_) + 1)]  # 主成分编号
)
print("PCA主成分加载矩阵：")
print(loading_matrix)
# 保存加载矩阵为Excel文件，便于查看
loading_matrix.to_excel('PCA主成分加载矩阵.xlsx')

# 确定保留主成分个数
n_components = next(i for i, ratio in enumerate(cumulative_explained_variance_ratio) if ratio >= 0.85) + 1
print(f"选择的主成分个数：{n_components}")

# 降维
pca = PCA(n_components=n_components)
X_reduced = pca.fit_transform(X_scaled)

reduced_df = pd.DataFrame(X_reduced, columns=[f"PC{i + 1}" for i in range(n_components)])

# 可视化降维后的数据分布
if n_components == 2:
    plt.figure(figsize=(10, 6))
    plt.scatter(reduced_df['PC1'], reduced_df['PC2'], alpha=0.7, c='blue', edgecolor='k')
    plt.xlabel('主成分1', fontsize=12)
    plt.ylabel('主成分2', fontsize=12)
    plt.title('PCA降维后的数据分布 (二维)', fontsize=14)
    plt.grid(alpha=0.5)
    plt.savefig('PCA降维后数据分布_二维.png')
    plt.show()

elif n_components >= 3:
    from mpl_toolkits.mplot3d import Axes3D

    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(reduced_df['PC1'], reduced_df['PC2'], reduced_df['PC3'], alpha=0.7, c='blue', edgecolor='k')
    ax.set_xlabel('主成分1', fontsize=12)
    ax.set_ylabel('主成分2', fontsize=12)
    ax.set_zlabel('主成分3', fontsize=12)
    ax.set_title('PCA降维后的数据分布 (三维)', fontsize=14)
    plt.savefig('PCA降维后数据分布_三维.png')
    plt.show()