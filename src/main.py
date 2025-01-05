import akshare as ak
import pandas as pd
from datetime import datetime
import os

def get_hs300etf_nav():
    try:
        # 获取沪深300ETF（510300）的日净值数据
        df = ak.fund_etf_hist_em(symbol="510300", period="daily", 
                                start_date="20240101", 
                                end_date=datetime.now().strftime("%Y%m%d"))
        
        # 重命名列
        df.columns = ['日期', '开盘', '收盘', '最高', '最低', '成交量', '成交额', '振幅', '涨跌幅', '涨跌额', '换手率']
        
        # 将日期设置为索引
        df.set_index('日期', inplace=True)
        
        # 创建输出目录
        output_dir = "/data"
        os.makedirs(output_dir, exist_ok=True)
        
        # 保存为CSV文件
        filename = os.path.join(output_dir, f"沪深300ETF_{datetime.now().strftime('%Y%m%d')}.csv")
        df.to_csv(filename, encoding='utf-8-sig')
        
        print(f"数据已保存至 {filename}")
        return df
        
    except Exception as e:
        print(f"获取数据时发生错误：{str(e)}")
        return None

if __name__ == "__main__":
    print("正在获取沪深300ETF数据...")
    df = get_hs300etf_nav()
    if df is not None:
        print("\n数据预览：")
        print(df.head()) 