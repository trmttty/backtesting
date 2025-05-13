import streamlit as st
import pandas as pd
import yfinance as yf
from backtesting import Backtest
from datetime import datetime, timedelta
import plotly.graph_objects as go
from backtest_strategy import (
    MovingAverageCrossStrategy,
    RSIStrategy,
    MACDStrategy,
    BollingerBandsStrategy
)

st.set_page_config(page_title="バックテストアプリ", layout="wide")
st.title("バックテストアプリ")

# サイドバーでパラメータを設定
st.sidebar.header("パラメータ設定")

# シンボル入力
symbol = st.sidebar.text_input("シンボル", "7974.T").strip().upper()

# 期間設定
today = datetime.now().date()
default_start_date = today - timedelta(days=365)
start_date = st.sidebar.date_input("開始日", default_start_date, max_value=today)
end_date = st.sidebar.date_input("終了日", today, min_value=start_date, max_value=today)

# 戦略の選択
st.sidebar.header("取引ルール")

# 買い戦略の選択
buy_strategy = st.sidebar.selectbox(
    "買い戦略",
    ["移動平均線クロスオーバー", "RSI", "MACD", "ボリンジャーバンド"]
)

# 買い戦略のパラメータ設定
if buy_strategy == "移動平均線クロスオーバー":
    fast_period = st.sidebar.slider("短期移動平均期間", 5, 50, 10)
    slow_period = st.sidebar.slider("長期移動平均期間", 20, 100, 30)
    strategy_class = MovingAverageCrossStrategy
    strategy_params = {
        'fast_period': fast_period,
        'slow_period': slow_period
    }
elif buy_strategy == "RSI":
    rsi_period = st.sidebar.slider("RSI期間", 5, 30, 14)
    overbought = st.sidebar.slider("買われすぎ閾値", 50, 90, 70)
    oversold = st.sidebar.slider("売られすぎ閾値", 10, 50, 30)
    strategy_class = RSIStrategy
    strategy_params = {
        'rsi_period': rsi_period,
        'overbought': overbought,
        'oversold': oversold
    }
elif buy_strategy == "MACD":
    fast_period = st.sidebar.slider("短期EMA期間", 5, 20, 12)
    slow_period = st.sidebar.slider("長期EMA期間", 20, 40, 26)
    signal_period = st.sidebar.slider("シグナル期間", 5, 15, 9)
    strategy_class = MACDStrategy
    strategy_params = {
        'fast_period': fast_period,
        'slow_period': slow_period,
        'signal_period': signal_period
    }
else:  # ボリンジャーバンド
    period = st.sidebar.slider("移動平均期間", 10, 50, 20)
    std_dev = st.sidebar.slider("標準偏差倍率", 1.0, 3.0, 2.0, 0.1)
    strategy_class = BollingerBandsStrategy
    strategy_params = {
        'period': period,
        'std_dev': std_dev
    }

# 損切り設定
stop_loss = st.sidebar.slider("損切り（%）", 0, 20, 5)

# 利確設定
take_profit = st.sidebar.slider("利確（%）", 0, 50, 20)

# リスク管理パラメータ
st.sidebar.header("リスク管理")
initial_cash = st.sidebar.number_input("初期資金", 10000, 1000000, 100000, step=10000)
position_size = st.sidebar.slider("ポジションサイズ（%）", 1, 100, 100)

# strategy_paramsにリスク管理パラメータを追加
strategy_params['position_size'] = position_size

# データ取得
@st.cache_data(ttl=3600)
def get_data(symbol, start_date, end_date):
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

# バックテストの実行
if st.sidebar.button("バックテスト実行"):
    with st.spinner("データを取得中..."):
        data = get_data(symbol, start_date, end_date)
        
        if data is not None:
            # 企業情報の取得
            ticker = yf.Ticker(symbol)
            company_name = ticker.info.get('longName', symbol)
            
            # バックテストの実行
            bt = Backtest(
                data,
                strategy_class,
                cash=initial_cash,
                commission=0.002,
                exclusive_orders=True
            )
            
            # 損切りと利確の設定
            if stop_loss > 0:
                strategy_params['stop_loss'] = stop_loss
            if take_profit > 0:
                strategy_params['take_profit'] = take_profit
            
            results = bt.run(**strategy_params)
            
            # 結果の表示
            st.write("### バックテスト結果")
            st.write(f"**企業名**: {company_name}")
            st.write(f"**シンボル**: {symbol}")
            
            # パフォーマンス指標
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("総リターン", f"{results['Return [%]']:.2f}%")
            with col2:
                st.metric("シャープレシオ", f"{results['Sharpe Ratio']:.2f}")
            with col3:
                st.metric("最大ドローダウン", f"{results['Max. Drawdown [%]']:.2f}%")
            with col4:
                st.metric("勝率", f"{results['Win Rate [%]']:.2f}%")
            
            # エクイティカーブの表示
            st.write("### エクイティカーブ")
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=results['_equity_curve'].index,
                y=results['_equity_curve'].Equity,
                mode='lines',
                name='エクイティ'
            ))
            fig.update_layout(
                title="エクイティカーブ",
                xaxis_title="日付",
                yaxis_title="エクイティ",
                showlegend=True
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # 取引履歴の表示
            st.write("### 取引履歴")
            trades = results['_trades']
            if len(trades) > 0:
                # DataFrameの列名を確認（デバッグ用表示を削除）
                # st.write("取引データの列名:", trades.columns)
                # データフレームを直接表示
                st.dataframe(trades)
            else:
                st.write("取引は行われませんでした。")
            
            # 詳細な統計情報
            st.write("### 詳細な統計情報")
            stats = pd.DataFrame(results).drop(['_equity_curve', '_trades'])
            st.dataframe(stats)
            