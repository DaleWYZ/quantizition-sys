# 策略参数配置
STRATEGY_PARAMS = {
    'MA': {
        'short_window': 5,
        'long_window': 20
    },
    'RSI': {
        'period': 14,
        'overbought': 70,
        'oversold': 30
    },
    'MACD': {
        'fast_period': 12,
        'slow_period': 26,
        'signal_period': 9
    },
    'Bollinger': {
        'period': 20,
        'std_dev': 2
    }
}

# 回测参数
BACKTEST_PARAMS = {
    'initial_capital': 1000000,
    'start_date': '20240101',
    'commission_rate': 0.0003
} 