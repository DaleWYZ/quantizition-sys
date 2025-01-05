import akshare as ak
import pandas as pd
from datetime import datetime
import os
from strategies import MAStrategy, RSIStrategy, MACDStrategy, BollingerStrategy
import warnings
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/data/strategy.log'),
        logging.StreamHandler()
    ]
)

def get_etf_nav(symbol, name):
    try:
        # 获取ETF的日净值数据
        df = ak.fund_etf_hist_em(symbol=symbol, period="daily", 
                                start_date="20240101", 
                                end_date=datetime.now().strftime("%Y%m%d"))
        
        if df.empty:
            print(f"警告：获取到的{name}数据为空")
            return None
            
        # 重命名列
        df.columns = ['日期', '开盘', '收盘', '最高', '最低', '成交量', '成交额', '振幅', '涨跌幅', '涨跌额', '换手率']
        
        # 将日期设置为索引
        df.set_index('日期', inplace=True)
        
        # 创建输出目录
        output_dir = "/data"
        os.makedirs(output_dir, exist_ok=True)
        
        # 保存为CSV文件
        filename = os.path.join(output_dir, f"{name}_{datetime.now().strftime('%Y%m%d')}.csv")
        df.to_csv(filename, encoding='utf-8-sig')
        
        print(f"{name}数据已保存至 {filename}")
        return df
        
    except Exception as e:
        print(f"获取{name}数据时发生错误：{str(e)}")
        return None

def get_hs300etf_nav():
    return get_etf_nav("510300", "沪深300ETF")

def get_zz500etf_nav():
    return get_etf_nav("510500", "中证500ETF")

if __name__ == "__main__":
    logging.info("开始执行策略分析...")
    
    # 获取ETF数据
    df_hs300 = get_hs300etf_nav()
    df_zz500 = get_zz500etf_nav()
    
    if df_hs300 is not None and df_zz500 is not None:
        print("\n开始策略分析...")
        
        # 创建策略实例
        strategies = {
            'MA策略': MAStrategy(df_hs300, df_zz500),
            'RSI策略': RSIStrategy(df_hs300, df_zz500),
            'MACD策略': MACDStrategy(df_hs300, df_zz500),
            '布林带策略': BollingerStrategy(df_hs300, df_zz500)
        }
        
        # 测试每个策略
        for name, strategy in strategies.items():
            print(f"\n测试{name}...")
            strategy.generate_signals()
            results = strategy.backtest()
            
            print(f"\n{name}回测结果：")
            for key, value in results.items():
                print(f"{key}: {value:.2f}")
            
            strategy.plot_results(name)
            print(f"\n{name}分析结果已保存至 /data/{name}_results.png") 