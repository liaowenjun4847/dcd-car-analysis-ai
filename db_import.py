import pandas as pd
import pymysql

# 1. 加载你那份没有问题的 CSV
df = pd.read_csv("dongchedi_sales.csv")

# 2. 数据库配置
db_config = {
    "host": "localhost",
    "user": "root", 
    "password": "123456", # <--- 这里填你在 DataGrip 里用的那个密码
    "database": "dcd_data",
    "charset": "utf8mb4"
}

try:
    # 建立连接
    conn = pymysql.connect(**db_config)
    cursor = conn.cursor()
    
    # 3. 逐行插入
    for _, row in df.iterrows():
        sql = """INSERT INTO car_sales (rank_num, brand, series, price_range, monthly_sales, category) 
                 VALUES (%s, %s, %s, %s, %s, %s)"""
        
        # 将数据转为正确的 Python 类型
        values = (
            int(row['排名']), 
            str(row['品牌']), 
            str(row['车系']), 
            str(row['价格区间']), 
            int(row['当月销量']), 
            str(row['车型分类'])
        )
        cursor.execute(sql, values)
    
    # 4. 提交更改
    conn.commit()
    print(f"✅ 成功！已将 {len(df)} 条汽车数据导入 MySQL 数据库。")

except Exception as e:
    print(f"❌ 导入失败: {e}")
finally:
    if 'conn' in locals():
        conn.close()