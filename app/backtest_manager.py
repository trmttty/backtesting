import streamlit as st
import yfinance as yf
from backtesting import Backtest
from app.backtest_strategy import (
    MovingAverageCrossStrategy,
    RSIStrategy,
    MACDStrategy,
    BollingerBandsStrategy
)

class BacktestManager:
    def __init__(self):
        self.strategy_classes = {
            "移動平均線クロスオーバー": MovingAverageCrossStrategy,
            "RSI": RSIStrategy,
            "MACD": MACDStrategy,
            "ボリンジャーバンド": BollingerBandsStrategy
        }

    @staticmethod
    @st.cache_data(ttl=3600)
    def get_data(symbol, start_date, end_date):
        """データの取得"""
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

    def execute_backtest(self, data, strategy_name, strategy_params, initial_cash):
        """バックテストの実行"""
        strategy_class = self.strategy_classes[strategy_name]
        bt = Backtest(
            data,
            strategy_class,
            cash=initial_cash,
            commission=0.002,
            exclusive_orders=True
        )
        return bt.run(**strategy_params)

    def get_company_info(self, symbol):
        """企業情報の取得"""
        ticker = yf.Ticker(symbol)
        return ticker.info.get('longName', symbol) 