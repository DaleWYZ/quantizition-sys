import unittest
import pandas as pd
import numpy as np

class TestStrategies(unittest.TestCase):
    def setUp(self):
        # 创建测试数据
        self.test_data = pd.DataFrame({
            '收盘': np.random.random(100) * 100,
            '开盘': np.random.random(100) * 100,
            '最高': np.random.random(100) * 100,
            '最低': np.random.random(100) * 100
        })
        
    def test_ma_strategy(self):
        strategy = MAStrategy(self.test_data, self.test_data)
        strategy.generate_signals()
        self.assertIsNotNone(strategy.signals) 