"""
バックテスト戦略モジュール
"""
from typing import Optional, Union, List
from backtesting import Strategy
from backtesting.lib import crossover
import pandas as pd
import numpy as np

class BaseStrategy(Strategy):
    """
    基本戦略クラス
    
    Attributes:
        initial_cash (int): 初期資金
        position_size (int): ポジションサイズ（100%固定）
        stop_loss (float): 損切り設定（%）
        take_profit (float): 利確設定（%）
    """
    initial_cash = 100000  # 初期資金
    position_size = 100    # ポジションサイズ（100%固定）
    stop_loss = 0         # 損切り設定
    take_profit = 0       # 利確設定

    def init(self) -> None:
        """
        戦略の初期化
        初期資金とリスク管理の設定を行う
        """
        self.initial_cash = getattr(self, 'initial_cash', 100000)
        self.position_size = getattr(self, 'position_size', 100)  # 100%固定
        self.stop_loss = getattr(self, 'stop_loss', 0)
        self.take_profit = getattr(self, 'take_profit', 0)

    def should_buy(self) -> bool:
        """
        買いシグナルを生成するメソッド
        子クラスで実装する必要がある
        
        Returns:
            bool: 買いシグナルが発生した場合はTrue
        """
        raise NotImplementedError("should_buy method must be implemented in child class")

    def should_sell(self) -> bool:
        """
        売りシグナルを生成するメソッド
        子クラスで実装する必要がある
        
        Returns:
            bool: 売りシグナルが発生した場合はTrue
        """
        raise NotImplementedError("should_sell method must be implemented in child class")

    def next(self) -> None:
        """
        次の取引を実行するメソッド
        買いシグナルと売りシグナルに基づいて取引を実行する
        """
        price = self.data.Close[-1]
        size = int(self.initial_cash // price)  # 初期資金を100%使用
        
        # ポジションがない場合の買いシグナル
        if not self.position and self.should_buy() and size > 0:
            # stop_lossとtake_profitの値を取得
            stop_loss_pct = self.stop_loss if hasattr(self, 'stop_loss') else 0
            take_profit_pct = self.take_profit if hasattr(self, 'take_profit') else 0
            
            # 損切り・利確の設定（値が0より大きい場合のみ設定）
            sl = price - (price * stop_loss_pct / 100) if stop_loss_pct > 0 else None
            tp = price + (price * take_profit_pct / 100) if take_profit_pct > 0 else None
            
            # 注文の実行
            self.buy(size=size, sl=sl, tp=tp)
        
        # ポジションがある場合の売りシグナル
        elif self.position and self.should_sell():
            self.position.close()

class MovingAverageCrossStrategy(BaseStrategy):
    """
    移動平均線クロスオーバー戦略
    
    Attributes:
        fast_period (int): 短期移動平均の期間
        slow_period (int): 長期移動平均の期間
        stop_loss (float): 損切り設定（%）
        take_profit (float): 利確設定（%）
    """
    fast_period = 10  # 短期移動平均の期間
    slow_period = 30  # 長期移動平均の期間
    stop_loss = 0     # 損切り設定
    take_profit = 0   # 利確設定
    
    def init(self) -> None:
        """戦略の初期化"""
        super().init()
        self.fast_ma = self.I(self.calculate_ma, self.data.Close, self.fast_period)
        self.slow_ma = self.I(self.calculate_ma, self.data.Close, self.slow_period)
    
    def calculate_ma(self, prices: List[float], period: int) -> pd.Series:
        """
        移動平均を計算する
        
        Args:
            prices (List[float]): 価格データ
            period (int): 期間
            
        Returns:
            pd.Series: 移動平均
        """
        return pd.Series(prices).rolling(period).mean()
    
    def should_buy(self) -> bool:
        """
        買いシグナルを判定する
        
        Returns:
            bool: 短期移動平均が長期移動平均を上回った場合True
        """
        return crossover(self.fast_ma, self.slow_ma)
    
    def should_sell(self) -> bool:
        """
        売りシグナルを判定する
        
        Returns:
            bool: 長期移動平均が短期移動平均を上回った場合True
        """
        return crossover(self.slow_ma, self.fast_ma)

class RSIStrategy(BaseStrategy):
    """
    RSI戦略
    
    Attributes:
        rsi_period (int): RSIの期間
        overbought (int): 買われすぎの閾値
        oversold (int): 売られすぎの閾値
        stop_loss (float): 損切り設定（%）
        take_profit (float): 利確設定（%）
    """
    rsi_period = 14  # RSIの期間
    overbought = 70  # 買われすぎの閾値
    oversold = 30    # 売られすぎの閾値
    stop_loss = 0    # 損切り設定
    take_profit = 0  # 利確設定
    
    def init(self) -> None:
        """戦略の初期化"""
        super().init()
        self.rsi = self.I(self.calculate_rsi, self.data.Close, self.rsi_period)
    
    def calculate_rsi(self, prices: List[float], period: int) -> pd.Series:
        """
        RSIを計算する
        
        Args:
            prices (List[float]): 価格データ
            period (int): 期間
            
        Returns:
            pd.Series: RSI
        """
        delta = pd.Series(prices).diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
    
    def should_buy(self) -> bool:
        """
        買いシグナルを判定する
        
        Returns:
            bool: RSIが売られすぎ閾値を下回った場合True
        """
        return self.rsi[-1] < self.oversold
    
    def should_sell(self) -> bool:
        """
        売りシグナルを判定する
        
        Returns:
            bool: RSIが買われすぎ閾値を上回った場合True
        """
        return self.rsi[-1] > self.overbought

class MACDStrategy(BaseStrategy):
    """
    MACD戦略
    
    Attributes:
        fast_period (int): 短期EMAの期間
        slow_period (int): 長期EMAの期間
        signal_period (int): シグナル線の期間
        stop_loss (float): 損切り設定（%）
        take_profit (float): 利確設定（%）
    """
    fast_period = 12    # 短期EMAの期間
    slow_period = 26    # 長期EMAの期間
    signal_period = 9   # シグナル線の期間
    stop_loss = 0       # 損切り設定
    take_profit = 0     # 利確設定
    
    def init(self) -> None:
        """戦略の初期化"""
        super().init()
        self.macd = self.I(self.calculate_macd, self.data.Close)
        self.signal = self.I(self.calculate_signal, self.macd)
    
    def calculate_macd(self, prices: List[float]) -> pd.Series:
        """
        MACDを計算する
        
        Args:
            prices (List[float]): 価格データ
            
        Returns:
            pd.Series: MACD
        """
        fast_ema = pd.Series(prices).ewm(span=self.fast_period, adjust=False).mean()
        slow_ema = pd.Series(prices).ewm(span=self.slow_period, adjust=False).mean()
        return fast_ema - slow_ema
    
    def calculate_signal(self, macd: pd.Series) -> pd.Series:
        """
        シグナル線を計算する
        
        Args:
            macd (pd.Series): MACD
            
        Returns:
            pd.Series: シグナル線
        """
        return pd.Series(macd).ewm(span=self.signal_period, adjust=False).mean()
    
    def should_buy(self) -> bool:
        """
        買いシグナルを判定する
        
        Returns:
            bool: MACDがシグナル線を上回った場合True
        """
        return crossover(self.macd, self.signal)
    
    def should_sell(self) -> bool:
        """
        売りシグナルを判定する
        
        Returns:
            bool: シグナル線がMACDを上回った場合True
        """
        return crossover(self.signal, self.macd)

class BollingerBandsStrategy(BaseStrategy):
    """
    ボリンジャーバンド戦略
    
    Attributes:
        period (int): 移動平均の期間
        std_dev (float): 標準偏差の倍率
        stop_loss (float): 損切り設定（%）
        take_profit (float): 利確設定（%）
    """
    period = 20        # 移動平均の期間
    std_dev = 2        # 標準偏差の倍率
    stop_loss = 0      # 損切り設定
    take_profit = 0    # 利確設定
    
    def init(self) -> None:
        """戦略の初期化"""
        super().init()
        self.middle_band = self.I(self.calculate_ma, self.data.Close, self.period)
        self.std = self.I(self.calculate_std, self.data.Close, self.period)
        self.upper_band = self.I(self.calculate_upper_band, self.middle_band, self.std)
        self.lower_band = self.I(self.calculate_lower_band, self.middle_band, self.std)
    
    def calculate_ma(self, prices: List[float], period: int) -> pd.Series:
        """
        移動平均を計算する
        
        Args:
            prices (List[float]): 価格データ
            period (int): 期間
            
        Returns:
            pd.Series: 移動平均
        """
        return pd.Series(prices).rolling(period).mean()
    
    def calculate_std(self, prices: List[float], period: int) -> pd.Series:
        """
        標準偏差を計算する
        
        Args:
            prices (List[float]): 価格データ
            period (int): 期間
            
        Returns:
            pd.Series: 標準偏差
        """
        return pd.Series(prices).rolling(period).std()
    
    def calculate_upper_band(self, ma: pd.Series, std: pd.Series) -> pd.Series:
        """
        上限バンドを計算する
        
        Args:
            ma (pd.Series): 移動平均
            std (pd.Series): 標準偏差
            
        Returns:
            pd.Series: 上限バンド
        """
        return ma + (std * self.std_dev)
    
    def calculate_lower_band(self, ma: pd.Series, std: pd.Series) -> pd.Series:
        """
        下限バンドを計算する
        
        Args:
            ma (pd.Series): 移動平均
            std (pd.Series): 標準偏差
            
        Returns:
            pd.Series: 下限バンド
        """
        return ma - (std * self.std_dev)
    
    def should_buy(self) -> bool:
        """
        買いシグナルを判定する
        
        Returns:
            bool: 価格が下限バンドを下回った場合True
        """
        return self.data.Close[-1] < self.lower_band[-1]
    
    def should_sell(self) -> bool:
        """
        売りシグナルを判定する
        
        Returns:
            bool: 価格が上限バンドを上回った場合True
        """
        return self.data.Close[-1] > self.upper_band[-1] 