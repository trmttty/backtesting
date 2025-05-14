"""
バックテストアプリケーションのメインモジュール
"""
from typing import Optional
import streamlit as st
from chart_manager import ChartManager
from ui_manager import UIManager
from backtest_manager import BacktestManager
import pandas as pd

class BacktestApp:
    """
    バックテストアプリケーションのメインクラス
    
    Attributes:
        ui_manager (UIManager): UI管理クラスのインスタンス
        chart_manager (ChartManager): チャート管理クラスのインスタンス
        backtest_manager (BacktestManager): バックテスト管理クラスのインスタンス
    """
    
    def __init__(self) -> None:
        """BacktestAppの初期化"""
        self.ui_manager = UIManager()
        self.chart_manager = ChartManager()
        self.backtest_manager = BacktestManager()

    def run(self) -> None:
        """
        アプリケーションの実行
        - サイドバーの設定
        - バックテスト実行ボタンの表示
        """
        self.ui_manager.setup_sidebar()
        if st.sidebar.button("バックテスト実行"):
            self.execute_backtest()

    def execute_backtest(self) -> None:
        """
        バックテストの実行
        - データの取得
        - バックテストの実行
        """
        with st.spinner("データを取得中..."):
            data = self.backtest_manager.get_data(
                self.ui_manager.symbol,
                self.ui_manager.start_date,
                self.ui_manager.end_date
            )
            
            if data is not None:
                self.run_backtest(data)
            else:
                st.error("データの取得に失敗しました。")

    def run_backtest(self, data: pd.DataFrame) -> None:
        """
        バックテストの実行と結果表示
        
        Args:
            data (pd.DataFrame): バックテスト用の価格データ
        """
        try:
            # 企業情報の取得
            company_name = self.backtest_manager.get_company_info(self.ui_manager.symbol)
            
            # バックテストの実行
            results = self.backtest_manager.execute_backtest(
                data,
                self.ui_manager.buy_strategy,
                self.ui_manager.strategy_params,
                self.ui_manager.initial_cash
            )
            
            # 結果の表示
            self.ui_manager.display_results(
                results,
                company_name,
                data,
                self.chart_manager
            )
        except Exception as e:
            st.error(f"バックテストの実行中にエラーが発生しました: {str(e)}")

if __name__ == "__main__":
    app = BacktestApp()
    app.run() 