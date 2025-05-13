import streamlit as st
from app.chart_manager import ChartManager
from app.ui_manager import UIManager
from app.backtest_manager import BacktestManager

class BacktestApp:
    def __init__(self):
        self.ui_manager = UIManager()
        self.chart_manager = ChartManager()
        self.backtest_manager = BacktestManager()

    def run(self):
        """アプリケーションの実行"""
        self.ui_manager.setup_sidebar()
        if st.sidebar.button("バックテスト実行"):
            self.execute_backtest()

    def execute_backtest(self):
        """バックテストの実行"""
        with st.spinner("データを取得中..."):
            data = self.backtest_manager.get_data(
                self.ui_manager.symbol,
                self.ui_manager.start_date,
                self.ui_manager.end_date
            )
            
            if data is not None:
                self.run_backtest(data)

    def run_backtest(self, data):
        """バックテストの実行と結果表示"""
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

if __name__ == "__main__":
    app = BacktestApp()
    app.run() 