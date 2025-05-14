"""
バックテスト管理モジュール
"""
from typing import Dict, Optional, Type, Any
import streamlit as st
import yfinance as yf
import pandas as pd
from backtesting import Backtest
from backtest_strategy import (
    MovingAverageCrossStrategy,
    RSIStrategy,
    MACDStrategy,
    BollingerBandsStrategy
)

class BacktestManager:
    """
    バックテスト管理クラス
    
    Attributes:
        strategy_classes (Dict[str, Type]): 戦略クラスのマッピング
    """
    
    def __init__(self) -> None:
        """BacktestManagerの初期化"""
        self.strategy_classes: Dict[str, Type] = {
            "移動平均線クロスオーバー": MovingAverageCrossStrategy,
            "RSI": RSIStrategy,
            "MACD": MACDStrategy,
            "ボリンジャーバンド": BollingerBandsStrategy
        }

    @staticmethod
    @st.cache_data(ttl=3600)
    def get_data(symbol: str, start_date: str, end_date: str) -> Optional[pd.DataFrame]:
        """
        株価データの取得
        
        Args:
            symbol (str): 株式シンボル
            start_date (str): 開始日
            end_date (str): 終了日
            
        Returns:
            Optional[pd.DataFrame]: 取得した株価データ。取得に失敗した場合はNone
        """
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(start=start_date, end=end_date)
            if data.empty:
                st.error(f"データが見つかりませんでした: {symbol}")
                return None
            return data
        except Exception as e:
            st.error(f"データの取得中にエラーが発生しました: {str(e)}")
            return None

    def execute_backtest(
        self,
        data: pd.DataFrame,
        strategy_name: str,
        strategy_params: Dict[str, Any],
        initial_cash: float
    ) -> Any:
        """
        バックテストの実行
        
        Args:
            data (pd.DataFrame): バックテスト用の価格データ
            strategy_name (str): 使用する戦略の名前
            strategy_params (Dict[str, Any]): 戦略パラメータ
            initial_cash (float): 初期資金
            
        Returns:
            Any: バックテストの結果
            
        Raises:
            KeyError: 指定された戦略名が存在しない場合
        """
        if strategy_name not in self.strategy_classes:
            raise KeyError(f"指定された戦略が見つかりません: {strategy_name}")
            
        strategy_class = self.strategy_classes[strategy_name]
        strategy_params = dict(strategy_params)  # 破壊的変更を避ける
        
        # 基本パラメータの設定
        strategy_params['initial_cash'] = initial_cash
        
        # 損切り・利確の設定
        if 'stop_loss' in strategy_params:
            strategy_params['stop_loss'] = float(strategy_params['stop_loss'])
        if 'take_profit' in strategy_params:
            strategy_params['take_profit'] = float(strategy_params['take_profit'])
        
        bt = Backtest(
            data,
            strategy_class,
            cash=initial_cash,
            commission=0.002,
            exclusive_orders=True
        )
        return bt.run(**strategy_params)

    def get_company_info(self, symbol: str) -> str:
        """
        企業情報の取得
        
        Args:
            symbol (str): 株式シンボル
            
        Returns:
            str: 企業名。取得できない場合はシンボルを返す
        """
        ticker = yf.Ticker(symbol)
        return ticker.info.get('longName', symbol) 