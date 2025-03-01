import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt

class ETFStrategy:
    def __init__(self, hs300_data, zz500_data):
        self.hs300 = hs300_data
        self.zz500 = zz500_data
        self.signals = pd.DataFrame(index=hs300_data.index)
        self.positions = pd.DataFrame(index=hs300_data.index)
        
    def calculate_indicators(self):
        # 计算相对强度指标 (RSI)
        self.hs300['收盘_变化'] = self.hs300['收盘'].diff()
        self.zz500['收盘_变化'] = self.zz500['收盘'].diff()
        
        # 计算移动平均线
        self.hs300['MA5'] = self.hs300['收盘'].rolling(window=5).mean()
        self.hs300['MA20'] = self.hs300['收盘'].rolling(window=20).mean()
        self.zz500['MA5'] = self.zz500['收盘'].rolling(window=5).mean()
        self.zz500['MA20'] = self.zz500['收盘'].rolling(window=20).mean()
        
        # 计算相对强度比率
        self.signals['强度比'] = self.hs300['收盘'] / self.zz500['收盘']
        
    def generate_signals(self):
        # 初始化信号列
        self.signals['hs300_signal'] = 0
        self.signals['zz500_signal'] = 0
        
        # 生成交易信号
        # 当5日均线上穿20日均线时买入，下穿时卖出
        self.signals.loc[self.hs300['MA5'] > self.hs300['MA20'], 'hs300_signal'] = 1
        self.signals.loc[self.hs300['MA5'] < self.hs300['MA20'], 'hs300_signal'] = -1
        
        self.signals.loc[self.zz500['MA5'] > self.zz500['MA20'], 'zz500_signal'] = 1
        self.signals.loc[self.zz500['MA5'] < self.zz500['MA20'], 'zz500_signal'] = -1
        
        # 根据相对强度调整仓位
        strength_threshold = self.signals['强度比'].mean()
        self.signals.loc[self.signals['强度比'] > strength_threshold, 'hs300_signal'] *= 1.2
        self.signals.loc[self.signals['强度比'] < strength_threshold, 'zz500_signal'] *= 1.2
        
    def backtest(self, initial_capital=1000000):
        # 初始化资金和持仓
        self.positions['hs300_pos'] = self.signals['hs300_signal'].shift(1)
        self.positions['zz500_pos'] = self.signals['zz500_signal'].shift(1)
        
        # 计算每日收益
        self.positions['hs300_returns'] = self.positions['hs300_pos'] * self.hs300['收盘'].pct_change()
        self.positions['zz500_returns'] = self.positions['zz500_pos'] * self.zz500['收盘'].pct_change()
        
        # 计算组合收益
        self.positions['total_returns'] = self.positions['hs300_returns'] + self.positions['zz500_returns']
        self.positions['cumulative_returns'] = (1 + self.positions['total_returns']).cumprod()
        
        # 计算策略评估指标
        total_return = (self.positions['cumulative_returns'].iloc[-1] - 1) * 100
        annual_return = total_return / len(self.positions) * 252
        sharpe_ratio = np.sqrt(252) * self.positions['total_returns'].mean() / self.positions['total_returns'].std()
        max_drawdown = (self.positions['cumulative_returns'] / self.positions['cumulative_returns'].cummax() - 1).min() * 100
        
        return {
            '总收益率(%)': total_return,
            '年化收益率(%)': annual_return,
            '夏普比率': sharpe_ratio,
            '最大回撤(%)': max_drawdown
        }
    
    def plot_results(self):
        plt.figure(figsize=(12, 8))
        plt.plot(self.positions['cumulative_returns'] * 100 - 100, label='策略收益率(%)')
        plt.plot(self.hs300['收盘'].pct_change().cumsum() * 100, label='沪深300收益率(%)')
        plt.plot(self.zz500['收盘'].pct_change().cumsum() * 100, label='中证500收益率(%)')
        plt.legend()
        plt.title('策略回测结果')
        plt.xlabel('日期')
        plt.ylabel('收益率(%)')
        plt.grid(True)
        
        # 保存图表
        plt.savefig('/data/strategy_results.png')
        plt.close() 