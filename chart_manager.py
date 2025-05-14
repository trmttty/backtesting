"""
チャート管理モジュール
"""
from typing import Dict, Any, Optional
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

class ChartManager:
    """
    チャート管理クラス
    
    Attributes:
        chart_height (int): チャートの高さ
        chart_width (Optional[int]): チャートの幅（Noneの場合はコンテナ幅に合わせる）
    """
    
    def __init__(self) -> None:
        """ChartManagerの初期化"""
        self.chart_height = 1000
        self.chart_width = None  # use_container_widthを使用するためNone

    def create_price_chart(
        self,
        data: pd.DataFrame,
        trades: pd.DataFrame,
        strategy_params: Dict[str, Any],
        buy_strategy: str,
        title: Optional[str] = None
    ) -> go.Figure:
        """
        株価チャートと指標を生成する
        
        Args:
            data (pd.DataFrame): 株価データ
            trades (pd.DataFrame): 取引データ
            strategy_params (Dict[str, Any]): 戦略パラメータ
            buy_strategy (str): 使用する戦略の名前
            title (Optional[str]): チャートのタイトル
            
        Returns:
            go.Figure: 生成されたチャート
        """
        fig = self._create_base_chart()
        self._add_candlestick(fig, data)
        self._add_technical_indicators(fig, data, strategy_params, buy_strategy)
        self._add_trade_markers(fig, trades)
        self._update_layout(fig, title=title)
        return fig

    def _create_base_chart(self) -> go.Figure:
        """
        基本チャートの作成
        
        Returns:
            go.Figure: 基本チャート
        """
        return make_subplots(
            rows=3, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.05,
            row_heights=[0.6, 0.2, 0.2]
        )

    def _add_candlestick(self, fig: go.Figure, data: pd.DataFrame) -> None:
        """
        ローソクチャートの追加
        
        Args:
            fig (go.Figure): チャート
            data (pd.DataFrame): 株価データ
        """
        fig.add_trace(
            go.Candlestick(
                x=data.index,
                open=data['Open'],
                high=data['High'],
                low=data['Low'],
                close=data['Close'],
                name='株価'
            ),
            row=1, col=1
        )

    def _add_technical_indicators(
        self,
        fig: go.Figure,
        data: pd.DataFrame,
        strategy_params: Dict[str, Any],
        buy_strategy: str
    ) -> None:
        """
        技術指標の追加
        
        Args:
            fig (go.Figure): チャート
            data (pd.DataFrame): 株価データ
            strategy_params (Dict[str, Any]): 戦略パラメータ
            buy_strategy (str): 使用する戦略の名前
        """
        indicator_handlers = {
            "移動平均線クロスオーバー": self._add_moving_averages,
            "RSI": self._add_rsi,
            "MACD": self._add_macd,
            "ボリンジャーバンド": self._add_bollinger_bands
        }
        
        handler = indicator_handlers.get(buy_strategy)
        if handler:
            handler(fig, data, strategy_params)

    def _add_moving_averages(
        self,
        fig: go.Figure,
        data: pd.DataFrame,
        params: Dict[str, Any]
    ) -> None:
        """
        移動平均線の追加
        
        Args:
            fig (go.Figure): チャート
            data (pd.DataFrame): 株価データ
            params (Dict[str, Any]): 戦略パラメータ
        """
        fast_ma = data['Close'].rolling(window=params['fast_period']).mean()
        slow_ma = data['Close'].rolling(window=params['slow_period']).mean()
        fig.add_trace(go.Scatter(x=data.index, y=fast_ma, 
                                name=f"短期MA({params['fast_period']})", 
                                line=dict(color='blue')), row=1, col=1)
        fig.add_trace(go.Scatter(x=data.index, y=slow_ma, 
                                name=f"長期MA({params['slow_period']})", 
                                line=dict(color='red')), row=1, col=1)

    def _add_rsi(
        self,
        fig: go.Figure,
        data: pd.DataFrame,
        params: Dict[str, Any]
    ) -> None:
        """
        RSIの追加
        
        Args:
            fig (go.Figure): チャート
            data (pd.DataFrame): 株価データ
            params (Dict[str, Any]): 戦略パラメータ
        """
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=params['rsi_period']).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=params['rsi_period']).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        fig.add_trace(go.Scatter(x=data.index, y=rsi, name='RSI', 
                                line=dict(color='purple')), row=2, col=1)
        fig.add_hline(y=params['overbought'], line_dash="dash", 
                     line_color="red", row=2, col=1)
        fig.add_hline(y=params['oversold'], line_dash="dash", 
                     line_color="green", row=2, col=1)

    def _add_macd(
        self,
        fig: go.Figure,
        data: pd.DataFrame,
        params: Dict[str, Any]
    ) -> None:
        """
        MACDの追加
        
        Args:
            fig (go.Figure): チャート
            data (pd.DataFrame): 株価データ
            params (Dict[str, Any]): 戦略パラメータ
        """
        exp1 = data['Close'].ewm(span=params['fast_period'], adjust=False).mean()
        exp2 = data['Close'].ewm(span=params['slow_period'], adjust=False).mean()
        macd = exp1 - exp2
        signal = macd.ewm(span=params['signal_period'], adjust=False).mean()
        fig.add_trace(go.Scatter(x=data.index, y=macd, name='MACD', 
                                line=dict(color='blue')), row=2, col=1)
        fig.add_trace(go.Scatter(x=data.index, y=signal, name='Signal', 
                                line=dict(color='red')), row=2, col=1)

    def _add_bollinger_bands(
        self,
        fig: go.Figure,
        data: pd.DataFrame,
        params: Dict[str, Any]
    ) -> None:
        """
        ボリンジャーバンドの追加
        
        Args:
            fig (go.Figure): チャート
            data (pd.DataFrame): 株価データ
            params (Dict[str, Any]): 戦略パラメータ
        """
        ma = data['Close'].rolling(window=params['period']).mean()
        std = data['Close'].rolling(window=params['period']).std()
        upper = ma + (std * params['std_dev'])
        lower = ma - (std * params['std_dev'])
        fig.add_trace(go.Scatter(x=data.index, y=ma, name='MA', 
                                line=dict(color='blue')), row=1, col=1)
        fig.add_trace(go.Scatter(x=data.index, y=upper, name='Upper Band', 
                                line=dict(color='red')), row=1, col=1)
        fig.add_trace(go.Scatter(x=data.index, y=lower, name='Lower Band', 
                                line=dict(color='green')), row=1, col=1)

    def _add_trade_markers(self, fig: go.Figure, trades: pd.DataFrame) -> None:
        """
        取引マーカーの追加
        
        Args:
            fig (go.Figure): チャート
            trades (pd.DataFrame): 取引データ
        """
        if trades is None or len(trades) == 0:
            return

        for _, trade in trades.iterrows():
            # エントリー（買いシグナル）
            self._add_buy_marker(fig, trade)
            # イグジット（売りシグナル）
            self._add_sell_marker(fig, trade)

    def _add_buy_marker(self, fig: go.Figure, trade: pd.Series) -> None:
        """
        買いマーカーの追加
        
        Args:
            fig (go.Figure): チャート
            trade (pd.Series): 取引データ
        """
        fig.add_trace(
            go.Scatter(
                x=[trade['EntryTime']],
                y=[trade['EntryPrice']],
                mode='markers',
                marker=dict(symbol='triangle-up', size=15, color='yellow'),
                name='買いシグナル'
            ),
            row=1, col=1
        )

    def _add_sell_marker(self, fig: go.Figure, trade: pd.Series) -> None:
        """
        売りマーカーの追加
        
        Args:
            fig (go.Figure): チャート
            trade (pd.Series): 取引データ
        """
        fig.add_trace(
            go.Scatter(
                x=[trade['ExitTime']],
                y=[trade['ExitPrice']],
                mode='markers',
                marker=dict(symbol='triangle-down', size=15, color='purple'),
                name='売りシグナル'
            ),
            row=1, col=1
        )

    def _update_layout(self, fig: go.Figure, title: Optional[str] = None) -> None:
        """
        チャートのレイアウト更新
        
        Args:
            fig (go.Figure): チャート
            title (Optional[str]): チャートのタイトル
        """
        fig.update_layout(
            title=title,
            xaxis_title='日付',
            yaxis_title='株価',
            height=self.chart_height,
            showlegend=True
        )

    def create_equity_chart(
        self,
        equity_curve: pd.DataFrame,
        title: Optional[str] = None
    ) -> go.Figure:
        """
        エクイティカーブの作成
        
        Args:
            equity_curve (pd.DataFrame): エクイティカーブデータ
            title (Optional[str]): チャートのタイトル
            
        Returns:
            go.Figure: 生成されたチャート
        """
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=equity_curve.index,
            y=equity_curve.Equity,
            mode='lines',
            name='エクイティ'
        ))
        fig.update_layout(
            title=title,
            xaxis_title="日付",
            yaxis_title="エクイティ",
            showlegend=True
        )
        return fig 