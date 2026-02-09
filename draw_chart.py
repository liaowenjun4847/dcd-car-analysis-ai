import pandas as pd
import matplotlib.pyplot as plt

# 1. 解决图片中文乱码问题（固定写法，不用背）
plt.rcParams['font.sans-serif'] = ['SimHei'] 

# 2. 读取你那份完美的 Excel (CSV)
df = pd.read_csv("dongchedi_sales.csv")

# 3. 取前 10 名进行绘图
top10 = df.head(10)

# 4. 绘图：x轴是车系，y轴是销量，颜色是天蓝色
plt.bar(top10['车系'], top10['当月销量'], color='skyblue')

# 5. 装饰图片
plt.title("懂车帝热销榜 Top 10 销量分布")
plt.xlabel("车型")
plt.ylabel("月销量")
plt.xticks(rotation=45) # 文字倾斜，防止重叠

plt.show() # 见证奇迹的时刻