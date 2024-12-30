import pandas as pd
import seaborn as sns
import math
import matplotlib
from matplotlib import rcParams
from matplotlib import pyplot as plt

# 设置支持中文的字体
rcParams['font.sans-serif'] = ['SimHei']
rcParams['axes.unicode_minus'] = False
matplotlib.use('TkAgg')


# 1. 读取数据并查看前几行
data = pd.read_excel('data/data.xlsx')
print("数据集的前几行：")
print(data.head())

# 2. 计算房价的统计信息
mean_price = data['房价'].mean()
median_price = data['房价'].median()
std_price = data['房价'].std()

print("\n房价的平均值：", mean_price)
print("房价的中位数：", median_price)
print("房价的标准差：", std_price)

# 将成交日期列转换为年月形式
def convert_to_month(year_decimal):
    year = int(year_decimal)  # 获取年份
    decimal = year_decimal - year  # 获取小数部分
    month = round(decimal * 12) + 1  # 小数部分乘以12，得到月份（1到12月）
    return f"{year}.{month:02d}"  # 返回YYYY.MM格式

# 对成交日期进行转换处理
data['成交日期'] = data['成交日期'].apply(convert_to_month)

# 3. 创建直方图并展示价格与不同要素的关系
# 筛选特征列
features = [col for col in data.columns if col not in ['No', '房价']]

# 动态计算子图的行数和列数
num_features = len(features)
cols = 3  # 每行显示的子图数
rows = math.ceil(num_features / cols)

# 创建图表
plt.figure(figsize=(5 * cols, 4 * rows))
for i, feature in enumerate(features, 1):
    plt.subplot(rows, cols, i)
    if "成交日期" in feature:
        # 成交日期列转换为日期时间类型
        data[feature] = pd.to_datetime(data[feature], format='%Y.%m')
        # 按照日期时间排序
        data = data.sort_values(by=feature)
        sns.histplot(data=data, x=feature, kde=True, bins=30)
        tick_locs, tick_labels = plt.xticks()
        plt.xticks(tick_locs, tick_labels, rotation=45, fontsize='small', ha='right', rotation_mode='anchor')

    else:
        sns.histplot(data=data, x=feature, kde=True, bins=30)
    plt.title(f'{feature} 分布直方图')
    plt.xlabel(feature)
    plt.ylabel('频率')

# 调整布局并保存图像
plt.tight_layout()
plt.savefig('房价关联图.png')
plt.show()
