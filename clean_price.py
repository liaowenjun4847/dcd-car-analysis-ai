import pymysql
import re

# 数据库配置 (填入你的密码)
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "123456", 
    "database": "dcd_data",
    "charset": "utf8mb4"
}

def clean_price_string(price_str):
    """
    专门处理 '17.98-21.98万' 这种格式
    """
    if not price_str or "暂无" in price_str:
        return None, None
    
    # 使用正则表达式提取所有的数字（包括小数点）
    prices = re.findall(r"\d+\.?\d*", price_str)
    
    if len(prices) == 2:
        return float(prices[0]), float(prices[1])
    elif len(prices) == 1:
        # 如果只有1个价格（比如“20万起”），则最低最高都设为它
        return float(prices[0]), float(prices[0])
    return None, None

try:
    conn = pymysql.connect(**db_config)
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    # 1. 查出所有带价格的记录
    cursor.execute("SELECT id, price_range FROM car_sales")
    rows = cursor.fetchall()
    
    print(f"正在清洗 {len(rows)} 条数据...")
    
    # 2. 逐行处理并更新
    for row in rows:
        p_min, p_max = clean_price_string(row['price_range'])
        
        if p_min is not None:
            update_sql = "UPDATE car_sales SET min_price=%s, max_price=%s WHERE id=%s"
            cursor.execute(update_sql, (p_min, p_max, row['id']))
            
    conn.commit()
    print("✅ 价格数据清洗完成！数字已存入 min_price 和 max_price 列。")

except Exception as e:
    print(f"❌ 出错: {e}")
finally:
    conn.close()