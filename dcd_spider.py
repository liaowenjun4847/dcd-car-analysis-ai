import requests
import pandas as pd
import time

def get_dcd_rank(pages=3):
    url = "https://www.dongchedi.com/motor/pc/car/rank_data"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://www.dongchedi.com/sales"
    }
    
    all_cars = []

    for page in range(pages):
        params = {"type": "1", "month": "", "page": str(page)}
        print(f"正在抓取第 {page + 1} 页数据...")
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                car_list = data.get('data', {}).get('list', [])
                
                for car in car_list:
                    # 1. 价格处理
                    price = car.get('price_range') or car.get('price') or "暂无价格"
                    
                    # 2. 车型分类终极增强版：尝试懂车帝所有可能的分类字段
                    car_type = car.get('sub_board_name') or \
                               car.get('series_type_name') or \
                               car.get('upper_name') or \
                               car.get('brand_name') + "系列" # 如果实在没有，用品牌名凑一下
                    
                    all_cars.append({
                        "排名": car.get('rank'),
                        "品牌": car.get('brand_name'),
                        "车系": car.get('series_name'),
                        "价格区间": price,
                        "当月销量": car.get('count'),
                        "车型分类": car_type
                    })
            time.sleep(1.5)
        except Exception as e:
            print(f"错误: {e}")

    # --- 数据处理环节：解决重复和保存问题 ---
    if all_cars:
        df = pd.DataFrame(all_cars)
        
        # 【去重核心】根据“车系”去重，保留第一次出现的，防止排名重复
        df = df.drop_duplicates(subset=['车系'], keep='first')
        
        # 重新整理一下排名（可选）
        df = df.sort_values(by="当月销量", ascending=False)
        
        df.to_csv("dongchedi_sales.csv", index=False, encoding="utf_8_sig")
        print(f"🎉 清洗完成！实际抓取去重后共 {len(df)} 款车型。")
    else:
        print("未抓取到数据。")

if __name__ == "__main__":
    get_dcd_rank(pages=3)