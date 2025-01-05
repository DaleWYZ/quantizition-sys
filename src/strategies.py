import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import talib
from abc import ABC, abstractmethod
import time
import logging

class BaseStrategy(ABC):
    def __init__(self, hs300_data, zz500_data):
        self.hs300 = hs300_data.copy()
        self.zz500 = zz500_data.copy()
        self.signals = pd.DataFrame(index=hs300_data.index)
        self.positions = pd.DataFrame(index=hs300_data.index)
        
        # 预计算常用的技术指标
        self._calculate_common_indicators()
        
    def _calculate_common_indicators(self):
        """预计算常用技术指标，避免重复计算"""
        # 计算移动平均线
        for df in [self.hs300, self.zz500]:
            df['MA5'] = df['收盘'].rolling(window=5).mean()
            df['MA20'] = df['收盘'].rolling(window=20).mean()
        
    @abstractmethod
    def generate_signals(self):
        """每个策略类必须实现的信号生成方法"""
        pass
    
    def calculate_indicators(self):
        """计算基础指标"""
        # 计算相对强度比率
        self.signals['强度比'] = self.hs300['收盘'] / self.zz500['收盘']
        
    def backtest(self, initial_capital=1000000):
        start_time = time.time()
        
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
        
        execution_time = time.time() - start_time
        logging.info(f"策略回测耗时: {execution_time:.2f}秒")
        
        return {
            '总收益率(%)': total_return,
            '年化收益率(%)': annual_return,
            '夏普比率': sharpe_ratio,
            '最大回撤(%)': max_drawdown
        }
    
    def plot_results(self, strategy_name):
        plt.figure(figsize=(12, 8))
        plt.plot(self.positions['cumulative_returns'] * 100 - 100, label='策略收益率(%)')
        plt.plot(self.hs300['收盘'].pct_change().cumsum() * 100, label='沪深300收益率(%)')
        plt.plot(self.zz500['收盘'].pct_change().cumsum() * 100, label='中证500收益率(%)')
        plt.legend()
        plt.title(f'{strategy_name}回测结果')
        plt.xlabel('日期')
        plt.ylabel('收益率(%)')
        plt.grid(True)
        
        # 保存图表
        plt.savefig(f'/data/{strategy_name}_results.png')
        plt.close()

class MAStrategy(BaseStrategy):
    """移动平均线策略"""
    def generate_signals(self):
        # 计算移动平均线
        self.hs300['MA5'] = self.hs300['收盘'].rolling(window=5).mean()
        self.hs300['MA20'] = self.hs300['收盘'].rolling(window=20).mean()
        self.zz500['MA5'] = self.zz500['收盘'].rolling(window=5).mean()
        self.zz500['MA20'] = self.zz500['收盘'].rolling(window=20).mean()
        
        # 初始化信号
        self.signals['hs300_signal'] = 0
        self.signals['zz500_signal'] = 0
        
        # 生成交易信号
        self.signals.loc[self.hs300['MA5'] > self.hs300['MA20'], 'hs300_signal'] = 1
        self.signals.loc[self.hs300['MA5'] < self.hs300['MA20'], 'hs300_signal'] = -1
        self.signals.loc[self.zz500['MA5'] > self.zz500['MA20'], 'zz500_signal'] = 1
        self.signals.loc[self.zz500['MA5'] < self.zz500['MA20'], 'zz500_signal'] = -1
        
        # 根据相对强度调整仓位
        self.calculate_indicators()
        strength_threshold = self.signals['强度比'].mean()
        self.signals.loc[self.signals['强度比'] > strength_threshold, 'hs300_signal'] *= 1.2
        self.signals.loc[self.signals['强度比'] < strength_threshold, 'zz500_signal'] *= 1.2

class RSIStrategy(BaseStrategy):
    """RSI策略"""
    def generate_signals(self):
        # 计算RSI指标
        self.hs300['RSI'] = talib.RSI(self.hs300['收盘'], timeperiod=14)
        self.zz500['RSI'] = talib.RSI(self.zz500['收盘'], timeperiod=14)
        
        # 初始化信号
        self.signals['hs300_signal'] = 0
        self.signals['zz500_signal'] = 0
        
        # 生成交易信号 (RSI > 70 超买，RSI < 30 超卖)
        self.signals.loc[self.hs300['RSI'] < 30, 'hs300_signal'] = 1
        self.signals.loc[self.hs300['RSI'] > 70, 'hs300_signal'] = -1
        self.signals.loc[self.zz500['RSI'] < 30, 'zz500_signal'] = 1
        self.signals.loc[self.zz500['RSI'] > 70, 'zz500_signal'] = -1

class MACDStrategy(BaseStrategy):
    """MACD策略"""
    def generate_signals(self):
        # 计算MACD指标
        for df in [self.hs300, self.zz500]:
            macd, signal, hist = talib.MACD(df['收盘'])
            df['MACD'] = macd
            df['MACD_SIGNAL'] = signal
            df['MACD_HIST'] = hist
        
        # 初始化信号
        self.signals['hs300_signal'] = 0
        self.signals['zz500_signal'] = 0
        
        # 生成交易信号
        self.signals.loc[self.hs300['MACD'] > self.hs300['MACD_SIGNAL'], 'hs300_signal'] = 1
        self.signals.loc[self.hs300['MACD'] < self.hs300['MACD_SIGNAL'], 'hs300_signal'] = -1
        self.signals.loc[self.zz500['MACD'] > self.zz500['MACD_SIGNAL'], 'zz500_signal'] = 1
        self.signals.loc[self.zz500['MACD'] < self.zz500['MACD_SIGNAL'], 'zz500_signal'] = -1

class BollingerStrategy(BaseStrategy):
    """布林带策略"""
    def generate_signals(self):
        # 计算布林带
        for df in [self.hs300, self.zz500]:
            df['BB_UPPER'], df['BB_MIDDLE'], df['BB_LOWER'] = talib.BBANDS(
                df['收盘'], timeperiod=20, nbdevup=2, nbdevdn=2
            )
        
        # 初始化信号
        self.signals['hs300_signal'] = 0
        self.signals['zz500_signal'] = 0
        
        # 生成交易信号
        self.signals.loc[self.hs300['收盘'] < self.hs300['BB_LOWER'], 'hs300_signal'] = 1
        self.signals.loc[self.hs300['收盘'] > self.hs300['BB_UPPER'], 'hs300_signal'] = -1
        self.signals.loc[self.zz500['收盘'] < self.zz500['BB_LOWER'], 'zz500_signal'] = 1
        self.signals.loc[self.zz500['收盘'] > self.zz500['BB_UPPER'], 'zz500_signal'] = -1