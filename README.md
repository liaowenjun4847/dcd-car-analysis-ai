# 🚗 基于 DeepSeek + Streamlit 的汽车市场智能决策看板

本项目是一款集成数据爬取、结构化存储、BI可视化与大语言模型（LLM）分析的端到端数据分析系统。通过 Text-to-SQL 技术，用户可以使用自然语言直接对懂车帝汽车销量数据进行深度挖掘。

## 🌟 核心亮点

* **智能语义查询 (Text-to-SQL)**：利用 DeepSeek 大模型将用户口语化提问（如“推荐20万左右销量好的SUV”）实时转化为精准的 MySQL 查询语句。
* **RAG 容错机制**：设计了双层检索架构。当数据库无法精准匹配时，自动触发 AI 专家模式，结合模型内置知识库为用户提供购车建议。
* **动态可视化分析**：采用 Streamlit + Matplotlib 实时生成销量趋势与价格分布图表。
* **安全工程化设计**：通过 `secrets.toml` 实现 API 密钥与数据库凭证的解耦，符合企业级安全开发规范。

## 🛠️ 技术栈

* **前端展示**：Streamlit (Python 原生 Web 框架)
* **大模型后端**：DeepSeek API (OpenAI 兼容协议)
* **数据存储**：MySQL (8.0+)
* **数据处理**：Pandas, PyMySQL
* **可视化**：Matplotlib

## 📂 项目结构

├── .streamlit/          # 配置文件（存放 API Key 和数据库密码）
├── app.py               # 主程序：Streamlit 网页逻辑与 AI 交互
├── dcd_spider.py        # 爬虫脚本：负责懂车帝数据抓取
├── db_import.py         # 数据入库：将 CSV 清洗并导入 MySQL
└── README.md            # 项目说明文档