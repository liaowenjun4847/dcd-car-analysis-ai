import pandas as pd
import matplotlib.pyplot as plt
import pymysql

# 1. 解决中文乱码
plt.rcParams['font.sans-serif'] = ['SimHei'] 

# 2. 从数据库取数
conn = pymysql.connect(host="localhost", user="root", password="123456", database="dcd_data")
df = pd.read_sql("SELECT series, min_price, monthly_sales FROM car_sales ORDER BY monthly_sales DESC LIMIT 10", conn)
conn.close()

# 3. 绘图：展示销量前10的车系及其起售价
fig, ax1 = plt.subplots(figsize=(10, 6))

# 画销量柱状图
ax1.bar(df['series'], df['monthly_sales'], color='g', alpha=0.6, label='月销量')
ax1.set_ylabel('销量 (台)')

# 画价格折线图（双坐标轴）
ax2 = ax1.twinx()
ax2.plot(df['series'], df['min_price'], color='r', marker='o', label='起售价(万)')
ax2.set_ylabel('起售价 (万元)')

plt.title("热销车系销量与价格关系图")
fig.tight_layout()
plt.show()