import streamlit as st
from datetime import datetime, timedelta

class UIManager:
    def __init__(self):
        self.setup_page_config()

    def setup_page_config(self):
        """ページ設定の初期化"""
        st.set_page_config(page_title="バックテストアプリ", layout="wide")
        st.title("バックテストアプリ")

    def setup_sidebar(self):
        """サイドバーの設定"""
        self.setup_symbol_input()
        self.setup_date_input()
        self.setup_strategy_selection()
        self.setup_risk_management()

    def setup_symbol_input(self):
        """シンボル入力の設定"""
        st.sidebar.header("パラメータ設定")
        self.symbol = st.sidebar.text_input("シンボル", "7974.T").strip().upper()

    def setup_date_input(self):
        """日付入力の設定"""
        today = datetime.now().date()
        default_start_date = today - timedelta(days=365)
        self.start_date = st.sidebar.date_input(
            "開始日", default_start_date, max_value=today
        )
        self.end_date = st.sidebar.date_input(
            "終了日", today, min_value=self.start_date, max_value=today
        )

    def setup_strategy_selection(self):
        """戦略選択の設定"""
        st.sidebar.header("取引ルール")
        self.buy_strategy = st.sidebar.selectbox(
            "買い戦略",
            ["移動平均線クロスオーバー", "RSI", "MACD", "ボリンジャーバンド"]
        )
        self.strategy_params = self.get_strategy_parameters()

    def setup_risk_management(self):
        """リスク管理の設定"""
        st.sidebar.header("リスク管理")
        self.initial_cash = st.sidebar.number_input(
            "初期資金", 10000, 1000000, 100000, step=10000
        )
        self.position_size = st.sidebar.slider("ポジションサイズ（%）", 1, 100, 100)
        self.strategy_params['position_size'] = self.position_size

        # 損切りと利確の設定を追加
        st.sidebar.subheader("損切り・利確設定")
        self.strategy_params['stop_loss'] = st.sidebar.slider(
            "損切り（%）", 1.0, 20.0, 5.0, 0.5
        )
        self.strategy_params['take_profit'] = st.sidebar.slider(
            "利確（%）", 1.0, 50.0, 10.0, 0.5
        )

    def get_strategy_parameters(self):
        """戦略パラメータの取得"""
        params = {}
        if self.buy_strategy == "移動平均線クロスオーバー":
            params['fast_period'] = st.sidebar.slider("短期移動平均期間", 5, 50, 10)
            params['slow_period'] = st.sidebar.slider("長期移動平均期間", 20, 100, 30)
        elif self.buy_strategy == "RSI":
            params['rsi_period'] = st.sidebar.slider("RSI期間", 5, 30, 14)
            params['overbought'] = st.sidebar.slider("買われすぎ閾値", 50, 90, 70)
            params['oversold'] = st.sidebar.slider("売られすぎ閾値", 10, 50, 30)
        elif self.buy_strategy == "MACD":
            params['fast_period'] = st.sidebar.slider("短期EMA期間", 5, 20, 12)
            params['slow_period'] = st.sidebar.slider("長期EMA期間", 20, 40, 26)
            params['signal_period'] = st.sidebar.slider("シグナル期間", 5, 15, 9)
        else:  # ボリンジャーバンド
            params['period'] = st.sidebar.slider("移動平均期間", 10, 50, 20)
            params['std_dev'] = st.sidebar.slider("標準偏差倍率", 1.0, 3.0, 2.0, 0.1)
        return params

    def display_results(self, results, company_name, data, chart_manager):
        """結果の表示"""
        self.display_company_info(company_name)
        self.display_performance_metrics(results)
        self.display_equity_curve(results, chart_manager)
        self.display_price_chart(data, results, chart_manager)
        self.display_trade_history(results)

    def display_company_info(self, company_name):
        """企業情報の表示"""
        st.write("### バックテスト結果")
        st.write(f"**企業名**: {company_name}")
        st.write(f"**シンボル**: {self.symbol}")

    def display_performance_metrics(self, results):
        """パフォーマンス指標の表示"""
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("総リターン", f"{results['Return [%]']:.2f}%")
        with col2:
            st.metric("シャープレシオ", f"{results['Sharpe Ratio']:.2f}")
        with col3:
            st.metric("最大ドローダウン", f"{results['Max. Drawdown [%]']:.2f}%")
        with col4:
            st.metric("勝率", f"{results['Win Rate [%]']:.2f}%")

    def display_equity_curve(self, results, chart_manager):
        """エクイティカーブの表示"""
        st.write("### エクイティカーブ")
        fig = chart_manager.create_equity_chart(results['_equity_curve'])
        st.plotly_chart(fig, use_container_width=True)

    def display_price_chart(self, data, results, chart_manager):
        """株価チャートの表示"""
        st.write("### 株価チャートと指標")
        trades = results['_trades']
        price_chart = chart_manager.create_price_chart(
            data, trades, self.strategy_params, self.buy_strategy
        )
        st.plotly_chart(price_chart, use_container_width=True)

    def display_trade_history(self, results):
        """取引履歴の表示"""
        st.write("### 取引履歴")
        trades = results['_trades']
        if len(trades) > 0:
            st.dataframe(trades)
        else:
            st.write("取引は行われませんでした。") 