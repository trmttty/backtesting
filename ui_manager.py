"""
UI管理モジュール
"""
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import streamlit as st
import pandas as pd

class UIManager:
    """
    UI管理クラス
    
    Attributes:
        symbol (Optional[str]): 株式シンボル
        start_date (Optional[datetime]): バックテスト開始日
        end_date (Optional[datetime]): バックテスト終了日
        buy_strategy (Optional[str]): 選択された戦略
        strategy_params (Dict[str, Any]): 戦略パラメータ
        initial_cash (Optional[int]): 初期資金
    """
    
    def __init__(self) -> None:
        """UIManagerの初期化"""
        self.symbol = None
        self.start_date = None
        self.end_date = None
        self.buy_strategy = None
        self.strategy_params = {}
        self.initial_cash = None
        self.setup_page_config()

    def setup_page_config(self) -> None:
        """ページ設定の初期化"""
        st.set_page_config(page_title="バックテストアプリ", layout="wide")

    def setup_sidebar(self) -> None:
        """サイドバーの設定"""
        self.setup_symbol_input()
        self.setup_date_input()
        self.setup_strategy_selection()
        self.setup_risk_management()

    def setup_symbol_input(self) -> None:
        """シンボル入力の設定"""
        st.sidebar.header("パラメータ設定")
        self.symbol = st.sidebar.text_input("シンボル", "7974.T").strip().upper()

    def setup_date_input(self) -> None:
        """日付入力の設定"""
        today = datetime.now().date()
        default_start_date = today - timedelta(days=365)
        self.start_date = st.sidebar.date_input(
            "開始日", default_start_date, max_value=today
        )
        self.end_date = st.sidebar.date_input(
            "終了日", today, min_value=self.start_date, max_value=today
        )

    def setup_strategy_selection(self) -> None:
        """戦略選択の設定"""
        st.sidebar.header("取引ルール")
        self.buy_strategy = st.sidebar.selectbox(
            "戦略",
            ["移動平均線クロスオーバー", "RSI", "MACD", "ボリンジャーバンド"]
        )
        self.strategy_params = self.get_strategy_parameters()

    def setup_risk_management(self) -> None:
        """リスク管理の設定"""
        st.sidebar.subheader("損切り・利確設定（オプション）")
        
        # 損切り設定
        use_stop_loss = st.sidebar.checkbox("損切りを使用する", value=False)
        self.strategy_params['stop_loss'] = 0  # デフォルト値
        if use_stop_loss:
            self.strategy_params['stop_loss'] = st.sidebar.slider(
                "損切り（%）", 1.0, 20.0, 5.0, 0.5
            )
        
        # 利確設定
        use_take_profit = st.sidebar.checkbox("利確を使用する", value=False)
        self.strategy_params['take_profit'] = 0  # デフォルト値
        if use_take_profit:
            self.strategy_params['take_profit'] = st.sidebar.slider(
                "利確（%）", 1.0, 50.0, 10.0, 0.5
            )

        # トレイリングストップ設定
        use_trailing_stop = st.sidebar.checkbox("トレイリングストップを使用する", value=False)
        self.strategy_params['use_trailing_stop'] = use_trailing_stop
        self.strategy_params['trailing_stop_pct'] = 0  # デフォルト値
        if use_trailing_stop:
            self.strategy_params['trailing_stop_pct'] = st.sidebar.slider(
                "トレイリングストップ（%）", 1.0, 20.0, 5.0, 0.5
            )

        # 初期資金の設定
        st.sidebar.header("初期資金")
        self.initial_cash = st.sidebar.number_input(
            "初期資金", 10000, 1000000, 100000, step=10000
        )

    def get_strategy_parameters(self) -> Dict[str, Any]:
        """
        戦略パラメータの取得
        
        Returns:
            Dict[str, Any]: 戦略パラメータ
        """
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

    def display_results(
        self,
        results: Any,
        company_name: str,
        data: pd.DataFrame,
        chart_manager: Any
    ) -> None:
        """
        バックテスト結果の表示
        
        Args:
            results (Any): バックテスト結果
            company_name (str): 企業名
            data (pd.DataFrame): 株価データ
            chart_manager (Any): チャート管理クラスのインスタンス
        """
        # 企業情報の表示
        st.title(f"{company_name} ({self.symbol})")

        # 通貨単位の設定
        currency = "円" if ".T" in self.symbol else "ドル" if "." not in self.symbol else "現地通貨"

        # バックテスト結果の表示
        st.header("バックテスト結果")
        initial_cash = self.initial_cash
        final_cash = int(results['_equity_curve'].Equity.iloc[-1])
        diff = final_cash - initial_cash
        
        # 1段目
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("総リターン", f"{results['Return [%]']:.2f}%")
        with col2:
            st.metric("シャープレシオ", f"{results['Sharpe Ratio']:.2f}")
        with col3:
            st.metric("最大ドローダウン", f"{results['Max. Drawdown [%]']:.2f}%")
        with col4:
            st.metric("勝率", f"{results['Win Rate [%]']:.2f}%")
            
        # 2段目
        trade_count = len(results._trades)
        col5, col6, col7, col8 = st.columns(4)
        with col5:
            st.metric("取引回数", f"{trade_count}回")
        with col6:
            st.metric("初期資金", f"{initial_cash:,}{currency}")
        with col7:
            st.metric("最終資金", f"{final_cash:,}{currency}")
        with col8:
            st.metric("増減", f"{diff:+,}{currency}")

        # 株価チャートと指標の表示
        st.markdown(
            f"<div style='font-size:1.5rem; color:white; font-weight:bold;'>"
            f"買い戦略：{self.buy_strategy}</div>",
            unsafe_allow_html=True
        )
        price_chart = chart_manager.create_price_chart(
            data, results._trades, self.strategy_params, self.buy_strategy,
            title=f"株価チャート（{self.symbol}）"
        )
        st.plotly_chart(price_chart, use_container_width=True)

        # エクイティカーブの表示
        equity_chart = chart_manager.create_equity_chart(
            results['_equity_curve'],
            title=f"エクイティカーブ（{self.symbol}）"
        )
        st.plotly_chart(equity_chart, use_container_width=True)

        # 取引履歴の表示
        st.markdown("<br>", unsafe_allow_html=True)
        st.header("取引履歴")
        if len(results._trades) > 0:
            trades_df = pd.DataFrame([
                {
                    "取引No.": i + 1,
                    "購入日": trade['EntryTime'].strftime("%Y-%m-%d"),
                    "購入価格": f"{round(trade['EntryPrice'])}{currency}",
                    "購入数量": int(abs(trade['Size'])),
                    "売却日": trade['ExitTime'].strftime("%Y-%m-%d"),
                    "売却価格": f"{round(trade['ExitPrice'])}{currency}",
                    "損益": f"{round(trade['PnL'])}{currency}",
                    "損益率": f"{trade['PnL'] / (trade['EntryPrice'] * abs(trade['Size'])) * 100:.2f}%"
                }
                for i, (_, trade) in enumerate(results._trades.iterrows())
            ])
            st.dataframe(trades_df, use_container_width=True)
        else:
            st.info("取引履歴はありません") 