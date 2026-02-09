import pymysql

def get_db_connection():
    """统一管理数据库连接"""
    return pymysql.connect(
        host="localhost",
        user="root",
        password="123456", # <--- 记得改成你的 DataGrip 登录密码
        database="dcd_data",
        charset="utf8mb4"
    )

def ai_query_engine(budget_min, budget_max, category=None):
    """
    模拟 AI 的查询引擎
    """
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    # 基础 SQL 逻辑
    sql = """
        SELECT brand, series, min_price, monthly_sales, category 
        FROM car_sales 
        WHERE min_price >= %s AND min_price <= %s
    """
    params = [budget_min, budget_max]
    
    # 如果用户指定了车型（比如 SUV），增加过滤条件
    if category:
        sql += " AND category LIKE %s"
        params.append(f"%{category}%")
    
    # 按销量排序，只给用户看最火的 5 款
    sql += " ORDER BY monthly_sales DESC LIMIT 5"
    
    try:
        cursor.execute(sql, params)
        data = cursor.fetchall()
        return data
    except Exception as e:
        print(f"查询出错: {e}")
        return []
    finally:
        conn.close()

def main():
    print("="*40)
    print("🤖 懂车帝 AI 购车助手 (数据驱动版) 启动")
    print("="*40)
    
    try:
        b_min = float(input("💰 您的最低预算是多少万？ "))
        b_max = float(input("💰 您的最高预算是多少万？ "))
        cat = input("🚗 您有心仪的车型吗？(如: SUV, 轿车, 或直接按回车跳过): ")
        
        print("\n正在从数据库检索最新销量数据...\n")
        results = ai_query_engine(b_min, b_max, cat if cat else None)
        
        if not results:
            print("😅 抱歉，当前数据库中没有符合您要求的车型。")
        else:
            print(f"✨ 为您找到以下 {len(results)} 款高人气推荐：")
            print("-" * 50)
            for i, car in enumerate(results, 1):
                print(f"{i}. 【{car['brand']} {car['series']}】")
                print(f"   价格区间起步: {car['min_price']}万")
                print(f"   上月全国销量: {car['monthly_sales']}台")
                print(f"   车辆定位: {car['category']}")
                print("-" * 50)
            
            # 模拟 AI 的总结建议
            top_car = results[0]
            print(f"\n💡 AI 建议：在这个预算范围内，{top_car['series']} 的销量最高，市场认可度最强，建议优先试驾。")

    except ValueError:
        print("❌ 输入错误，请输入数字。")

if __name__ == "__main__":
    main()