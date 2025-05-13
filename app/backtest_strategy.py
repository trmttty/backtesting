from backtesting import Strategy
from backtesting.lib import crossover
import pandas as pd
import numpy as np

class BaseStrategy(Strategy):
    """
    基本戦略クラス
    """
    position_size = 100
    stop_loss = 0
    take_profit = 0

    def should_buy(self):
        """
        買いシグナルを生成するメソッド
        子クラスで実装する必要がある
        """
        raise NotImplementedError("should_buy method must be implemented in child class")

    def next(self):
        size = self.position_size / 100
        if not self.position and self.should_buy():
            price = self.data.Close[-1]
            sl = price - (price * self.stop_loss / 100) if self.stop_loss > 0 else None
            tp = price + (price * self.take_profit / 100) if self.take_profit > 0 else None
            self.buy(size=size, sl=sl, tp=tp)

class MovingAverageCrossStrategy(BaseStrategy):
    """
    移動平均線クロスオーバー戦略
    """
    fast_period = 10  # 短期移動平均の期間
    slow_period = 30  # 長期移動平均の期間
    stop_loss = 0     # 損切り設定
    take_profit = 0   # 利確設定
    
    def init(self):
        self.fast_ma = self.I(self.calculate_ma, self.data.Close, self.fast_period)
        self.slow_ma = self.I(self.calculate_ma, self.data.Close, self.slow_period)
    
    def calculate_ma(self, prices, period):
        return pd.Series(prices).rolling(period).mean()
    
    def should_buy(self):
        return crossover(self.fast_ma, self.slow_ma)

class RSIStrategy(BaseStrategy):
    """
    RSI戦略
    """
    rsi_period = 14  # RSIの期間
    overbought = 70  # 買われすぎの閾値
    oversold = 30    # 売られすぎの閾値
    stop_loss = 0    # 損切り設定
    take_profit = 0  # 利確設定
    
    def init(self):
        self.rsi = self.I(self.calculate_rsi, self.data.Close, self.rsi_period)
    
    def calculate_rsi(self, prices, period):
        delta = pd.Series(prices).diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
    
    def should_buy(self):
        return self.rsi[-1] < self.oversold

class MACDStrategy(BaseStrategy):
    """
    MACD戦略
    """
    fast_period = 12    # 短期EMAの期間
    slow_period = 26    # 長期EMAの期間
    signal_period = 9   # シグナル線の期間
    stop_loss = 0       # 損切り設定
    take_profit = 0     # 利確設定
    
    def init(self):
        self.macd = self.I(self.calculate_macd, self.data.Close)
        self.signal = self.I(self.calculate_signal, self.macd)
    
    def calculate_macd(self, prices):
        fast_ema = pd.Series(prices).ewm(span=self.fast_period, adjust=False).mean()
        slow_ema = pd.Series(prices).ewm(span=self.slow_period, adjust=False).mean()
        return fast_ema - slow_ema
    
    def calculate_signal(self, macd):
        return pd.Series(macd).ewm(span=self.signal_period, adjust=False).mean()
    
    def should_buy(self):
        return crossover(self.macd, self.signal)

class BollingerBandsStrategy(BaseStrategy):
    """
    ボリンジャーバンド戦略
    """
    period = 20        # 移動平均の期間
    std_dev = 2        # 標準偏差の倍率
    stop_loss = 0      # 損切り設定
    take_profit = 0    # 利確設定
    
    def init(self):
        self.middle_band = self.I(self.calculate_ma, self.data.Close, self.period)
        self.std = self.I(self.calculate_std, self.data.Close, self.period)
        self.lower_band = self.I(self.calculate_lower_band, self.middle_band, self.std)
    
    def calculate_ma(self, prices, period):
        return pd.Series(prices).rolling(period).mean()
    
    def calculate_std(self, prices, period):
        return pd.Series(prices).rolling(period).std()
    
    def calculate_lower_band(self, ma, std):
        return ma - (std * self.std_dev)
    
    def should_buy(self):
        return self.data.Close[-1] < self.lower_band[-1] 