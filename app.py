import streamlit as st
import pandas as pd
import pymysql
import matplotlib.pyplot as plt
from openai import OpenAI

# 1. 基础配置
st.set_page_config(page_title="懂车帝大数据看板", page_icon="🚗", layout="wide")
plt.rcParams['font.sans-serif'] = ['SimHei']  # 解决中文乱码

# 数据库配置 
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

# --- 核心功能函数 ---

def get_data(min_p, max_p, car_type=None):
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    # 基础 SQL
    sql = "SELECT brand, series, min_price, monthly_sales, category FROM car_sales WHERE min_price BETWEEN %s AND %s"
    params = [min_p, max_p]
    
    # 优化车型筛选逻辑
    if car_type and car_type != "全部":
        # 如果选择 SUV，不仅匹配 category，还匹配 series 或 brand 里的关键词
        # 增加 OR 逻辑，确保只要包含这个词就能搜出来
        sql += " AND (category LIKE %s OR series LIKE %s)"
        params.append(f"%{car_type}%")
        params.append(f"%{car_type}%")
        
    sql += " ORDER BY monthly_sales DESC LIMIT 15"
    cursor.execute(sql, params)
    data = cursor.fetchall()
    conn.close()
    return pd.DataFrame(data)

def ai_generate_sql(user_question):
    """Text-to-SQL：让 AI 把人话转成查询语句"""
    prompt = f"""
    你是一个精通汽车数据的高级分析师。请根据用户的问题生成一条 MySQL 查询语句。
    【数据库表：car_sales】字段：brand, series, monthly_sales, category, min_price, max_price
    【要求】
    1. 搜索词：使用 LIKE '%关键词%' 模糊匹配。
    2. 多字段：对 brand、series 和 category 进行 OR 联合搜索。
    3. 排序：默认按 monthly_sales DESC，LIMIT 10。
    只输出 SQL 语句，不要解释。
    用户问题：{user_question}
    """
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip().replace(";", "").replace("```sql", "").replace("```", "")

# --- 网页界面布局 ---

st.title("🚗 懂车帝汽车销量智能分析系统")

# 侧边栏：结构化筛选
st.sidebar.header("📊 筛选条件")
price_range = st.sidebar.slider("选择预算范围 (万)", 0.0, 100.0, (10.0, 30.0))
car_kind = st.sidebar.selectbox("选择车型", ["全部", "轿车", "SUV", "MPV"])

if st.sidebar.button("开始分析"):
    df = get_data(price_range[0], price_range[1], car_kind)
    
    if not df.empty:
        # 第一部分：展示数据表格
        st.subheader(f"✅ {price_range[0]}-{price_range[1]}万 销量 Top 15")
        st.dataframe(df.style.highlight_max(axis=0, subset=['monthly_sales'], color='lightgreen'))

        # 第二部分：展示图表
        st.subheader("📈 销量与价格分布图")
        fig, ax1 = plt.subplots(figsize=(10, 5))
        ax1.bar(df['series'], df['monthly_sales'], color='skyblue', label='月销量')
        ax1.set_ylabel('销量')
        ax2 = ax1.twinx()
        ax2.plot(df['series'], df['min_price'], color='red', marker='o', label='价格')
        ax2.set_ylabel('价格(万)')
        plt.xticks(rotation=45)
        st.pyplot(fig)

        # 第三部分：AI 自动生成分析报告 (修复了之前的缩进错误)
        st.divider()
        st.subheader("📝 AI 市场深度洞察报告")
        with st.spinner("AI 专家正在分析数据..."):
            summary_prompt = f"请根据这份汽车销量表进行深度分析，指出销量冠军、性价比之王，并给购买建议：\n{df.to_string()}"
            summary_res = client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": summary_prompt}]
            )
            st.info(summary_res.choices[0].message.content)
    else:
        st.warning("没找到匹配的数据，换个条件试试吧！")

st.sidebar.markdown("---")
st.sidebar.caption("📅 数据最后更新：2026-02-09")
st.sidebar.caption("💾 数据来源：懂车帝真实销量")

# 底部：AI 智能对话助手
st.divider()
st.subheader("🤖 AI 智能购车助手 (对话模式)")
user_input = st.chat_input("您可以问：帮我找找小米和比亚迪20万左右的车")

if user_input:
    with st.chat_message("user"):
        st.write(user_input)
    
    generated_sql = ai_generate_sql(user_input)
    
    conn = pymysql.connect(**DB_CONFIG)
    df_ai = pd.read_sql(generated_sql, conn)
    conn.close()
    
    with st.chat_message("assistant"):
        if not df_ai.empty:
            st.write("✨ 实时检索结果：")
            st.table(df_ai)
            # AI 深度解读
            analysis_prompt = f"用户问：{user_input}。查询到的数据是：{df_ai.to_string()}。请简要分析这些车的优缺点。"
            analysis_res = client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": analysis_prompt}]
            )
            st.write(analysis_res.choices[0].message.content)
        else:
            # 兜底：数据库查不到时直接用 AI 知识储备回答
            st.warning("🔍 数据库中暂无精准匹配，AI 专家为您提供以下参考：")
            backup_res = client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": f"用户问：{user_input}。请基于你的知识给出购车建议。"}]
            )
            st.write(backup_res.choices[0].message.content)