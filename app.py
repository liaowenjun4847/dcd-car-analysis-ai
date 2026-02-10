import streamlit as st
import pandas as pd
import pymysql
import matplotlib.pyplot as plt
from openai import OpenAI
import re

# 1. 基础配置
st.set_page_config(page_title="懂车帝大数据看板", page_icon="🚗", layout="wide")
st.balloons()

# 解决 Linux 云端环境中文乱码：优先使用系统自带字体，并将标签改为英文/拼音以保万无一失
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Liberation Sans', 'Arial'] 
plt.rcParams['axes.unicode_minus'] = False

# 数据库配置 (从 Secrets 读取)
DB_CONFIG = {
    "host": st.secrets["database"]["host"],
    "user": st.secrets["database"]["user"],
    "password": st.secrets["database"]["password"],
    "database": st.secrets["database"]["database"],
    "charset": "utf8mb4"
}

# 初始化 DeepSeek 客户端
client = OpenAI(
    api_key=st.secrets["api"]["deepseek_key"], 
    base_url="https://api.deepseek.com"
)

# --- 核心功能函数：带容错的数据获取 ---

def get_data(min_p, max_p, car_type="全部", query_sql=None):
    """
    统一数据入口：优先连数据库，失败则解析 CSV 兜底。
    """
    try:
        # 尝试连接数据库
        conn = pymysql.connect(**DB_CONFIG)
        if query_sql:
            # 如果是 AI 模式，执行生成的 SQL
            df = pd.read_sql(query_sql, conn)
        else:
            # 正常筛选模式
            sql = f"SELECT * FROM car_sales WHERE min_price BETWEEN %s AND %s"
            params = [min_p, max_p]
            if car_type != "全部":
                sql += " AND category LIKE %s"
                params.append(f"%{car_type}%")
            df = pd.read_sql(sql, conn, params=params)
        conn.close()
        return df
    except Exception as e:
        # 数据库失败 -> 启动 CSV 模式
        st.warning("📡 正在从内置 CSV 数据源加载（云端数据库未就绪）")
        df_backup = pd.read_csv("dongchedi_sales.csv")
        
        # 1. 强制对齐列名
        df_backup.columns = ['rank', 'brand', 'series', 'price_range', 'monthly_sales', 'category']
        
        # 2. 解析价格数字 (例如从 "17.98-21.98万" 提取 17.98)
        df_backup['min_price'] = df_backup['price_range'].str.extract(r'(\d+\.?\d*)').astype(float)
        df_backup['monthly_sales'] = pd.to_numeric(df_backup['monthly_sales'], errors='coerce')

        # 3. 执行逻辑筛选
        if query_sql:
            # AI 模式下，CSV 无法执行 SQL，这里做个模糊搜索演示
            return df_backup.head(10)
        
        mask = (df_backup['min_price'] >= min_p) & (df_backup['min_price'] <= max_p)
        if car_type != "全部":
            mask &= df_backup['category'].str.contains(car_type)
        
        return df_backup[mask].sort_values("monthly_sales", ascending=False).head(15)

def ai_generate_sql(user_question):
    """Text-to-SQL：让 AI 把人话转成查询语句"""
    prompt = f"""
    你是一个汽车数据分析师。请根据用户问题生成一条 MySQL 查询语句。
    表名：car_sales
    字段：brand, series, monthly_sales, category, min_price
    要求：只输出 SQL，不要解释。
    问题：{user_question}
    """
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip().replace("```sql", "").replace("```", "")
    except:
        return "SELECT * FROM car_sales LIMIT 10"

# --- 网页界面布局 ---

st.title("🚗 懂车帝汽车销量智能分析系统")

# 侧边栏：结构化筛选
st.sidebar.header("📊 筛选条件")
price_range = st.sidebar.slider("选择预算范围 (万)", 0.0, 100.0, (10.0, 30.0))
car_kind = st.sidebar.selectbox("选择车型", ["全部", "轿车", "SUV", "MPV"])

if st.sidebar.button("开始分析"):
    df = get_data(price_range[0], price_range[1], car_kind)
    
    if not df.empty:
        st.subheader(f"✅ {price_range[0]}-{price_range[1]}万 销量排行")
        st.dataframe(df)

        # 图表部分
        st.subheader("📈 销量与价格分布图")
        fig, ax1 = plt.subplots(figsize=(10, 5))
        # 使用拼音或英文标签防止 Linux 乱码
        ax1.bar(df['series'], df['monthly_sales'], color='skyblue', label='Sales')
        ax1.set_ylabel('Sales')
        ax2 = ax1.twinx()
        ax2.plot(df['series'], df['min_price'], color='red', marker='o', label='Price')
        ax2.set_ylabel('Price (Wan)')
        plt.xticks(rotation=45)
        st.pyplot(fig)

        # AI 报告
        st.divider()
        st.subheader("📝 AI 市场深度洞察报告")
        with st.spinner("AI 专家分析中..."):
            summary_prompt = f"分析以下数据并给出建议：\n{df[['brand', 'series', 'monthly_sales', 'min_price']].to_string()}"
            res = client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": summary_prompt}]
            )
            st.info(res.choices[0].message.content)
    else:
        st.warning("没找到匹配的数据。")

# 底部：AI 智能对话助手
st.divider()
st.subheader("🤖 AI 智能购车助手")
user_input = st.chat_input("您可以问：帮我找找20万左右的小米或比亚迪")

if user_input:
    with st.chat_message("user"):
        st.write(user_input)
    
    with st.chat_message("assistant"):
        with st.spinner("思考中..."):
            # 1. 尝试生成 SQL 并查询
            gen_sql = ai_generate_sql(user_input)
            df_ai = get_data(0, 100, query_sql=gen_sql)
            
            # 2. 调用 AI 进行解读
            analysis_prompt = f"用户问：{user_input}。参考数据：{df_ai.to_string()}。请给出购车建议。"
            ans = client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": analysis_prompt}]
            )
            st.write(ans.choices[0].message.content)
            if not df_ai.empty:
                st.table(df_ai.head(5))

st.sidebar.markdown("---")
st.sidebar.caption("📅 数据最后更新：2026-02-10")
