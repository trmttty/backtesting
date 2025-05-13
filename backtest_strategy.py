from backtesting import Strategy
from backtesting.lib import crossover
import pandas as pd
import numpy as np

class MovingAverageCrossStrategy(Strategy):
    """
    移動平均線クロスオーバー戦略
    """
    # パラメータの定義
    fast_period = 10  # 短期移動平均の期間
    slow_period = 30  # 長期移動平均の期間
    position_size = 100
    stop_loss = 0
    take_profit = 0
    
    def init(self):
        # 移動平均の計算
        self.fast_ma = self.I(self.calculate_ma, self.data.Close, self.fast_period)
        self.slow_ma = self.I(self.calculate_ma, self.data.Close, self.slow_period)
    
    def calculate_ma(self, prices, period):
        """移動平均を計算する関数"""
        return pd.Series(prices).rolling(period).mean()
    
    def next(self):
        size = self.position_size / 100  # %→比率
        price = self.data.Close[-1]
        sl = price - (price * self.stop_loss / 100) if self.stop_loss > 0 else None
        tp = price + (price * self.take_profit / 100) if self.take_profit > 0 else None
        # ポジションがない場合
        if not self.position:
            if crossover(self.fast_ma, self.slow_ma):
                self.buy(size=size, sl=sl, tp=tp)
        else:
            if crossover(self.slow_ma, self.fast_ma):
                self.position.close()

class RSIStrategy(Strategy):
    """
    RSI戦略
    """
    # パラメータの定義
    rsi_period = 14  # RSIの期間
    overbought = 70  # 買われすぎの閾値
    oversold = 30    # 売られすぎの閾値
    position_size = 100
    stop_loss = 0
    take_profit = 0
    
    def init(self):
        # RSIの計算
        self.rsi = self.I(self.calculate_rsi, self.data.Close, self.rsi_period)
    
    def calculate_rsi(self, prices, period):
        """RSIを計算する関数"""
        delta = pd.Series(prices).diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
    
    def next(self):
        size = self.position_size / 100
        price = self.data.Close[-1]
        sl = price - (price * self.stop_loss / 100) if self.stop_loss > 0 else None
        tp = price + (price * self.take_profit / 100) if self.take_profit > 0 else None
        # ポジションがない場合
        if not self.position:
            # RSIが売られすぎの閾値を下回った場合
            if self.rsi < self.oversold:
                self.buy(size=size, sl=sl, tp=tp)
        
        # ポジションがある場合
        else:
            # RSIが買われすぎの閾値を上回った場合
            if self.rsi > self.overbought:
                self.position.close()

class MACDStrategy(Strategy):
    """
    MACD戦略
    """
    # パラメータの定義
    fast_period = 12    # 短期EMAの期間
    slow_period = 26    # 長期EMAの期間
    signal_period = 9   # シグナル線の期間
    position_size = 100
    stop_loss = 0
    take_profit = 0
    
    def init(self):
        # MACDの計算
        self.macd = self.I(self.calculate_macd, self.data.Close)
        self.signal = self.I(self.calculate_signal, self.macd)
        self.histogram = self.I(self.calculate_histogram, self.macd, self.signal)
    
    def calculate_macd(self, prices):
        """MACDを計算する関数"""
        fast_ema = pd.Series(prices).ewm(span=self.fast_period, adjust=False).mean()
        slow_ema = pd.Series(prices).ewm(span=self.slow_period, adjust=False).mean()
        return fast_ema - slow_ema
    
    def calculate_signal(self, macd):
        """シグナル線を計算する関数"""
        return pd.Series(macd).ewm(span=self.signal_period, adjust=False).mean()
    
    def calculate_histogram(self, macd, signal):
        """ヒストグラムを計算する関数"""
        return macd - signal
    
    def next(self):
        size = self.position_size / 100
        price = self.data.Close[-1]
        sl = price - (price * self.stop_loss / 100) if self.stop_loss > 0 else None
        tp = price + (price * self.take_profit / 100) if self.take_profit > 0 else None
        # ポジションがない場合
        if not self.position:
            # MACDがシグナル線を上から下にクロス
            if crossover(self.macd, self.signal):
                self.buy(size=size, sl=sl, tp=tp)
        
        # ポジションがある場合
        else:
            # MACDがシグナル線を下から上にクロス
            if crossover(self.signal, self.macd):
                self.position.close()

class BollingerBandsStrategy(Strategy):
    """
    ボリンジャーバンド戦略
    """
    # パラメータの定義
    period = 20        # 移動平均の期間
    std_dev = 2        # 標準偏差の倍率
    position_size = 100
    stop_loss = 0
    take_profit = 0
    
    def init(self):
        # ボリンジャーバンドの計算
        self.middle_band = self.I(self.calculate_ma, self.data.Close, self.period)
        self.std = self.I(self.calculate_std, self.data.Close, self.period)
        self.upper_band = self.I(self.calculate_upper_band, self.middle_band, self.std)
        self.lower_band = self.I(self.calculate_lower_band, self.middle_band, self.std)
    
    def calculate_ma(self, prices, period):
        """移動平均を計算する関数"""
        return pd.Series(prices).rolling(period).mean()
    
    def calculate_std(self, prices, period):
        """標準偏差を計算する関数"""
        return pd.Series(prices).rolling(period).std()
    
    def calculate_upper_band(self, ma, std):
        """上限バンドを計算する関数"""
        return ma + (std * self.std_dev)
    
    def calculate_lower_band(self, ma, std):
        """下限バンドを計算する関数"""
        return ma - (std * self.std_dev)
    
    def next(self):
        size = self.position_size / 100
        price = self.data.Close[-1]
        sl = price - (price * self.stop_loss / 100) if self.stop_loss > 0 else None
        tp = price + (price * self.take_profit / 100) if self.take_profit > 0 else None
        # ポジションがない場合
        if not self.position:
            # 価格が下限バンドを下回った場合
            if self.data.Close[-1] < self.lower_band[-1]:
                self.buy(size=size, sl=sl, tp=tp)
        
        # ポジションがある場合
        else:
            # 価格が上限バンドを上回った場合
            if self.data.Close[-1] > self.upper_band[-1]:
                self.position.close() 