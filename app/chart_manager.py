import plotly.graph_objects as go
from plotly.subplots import make_subplots

class ChartManager:
    def __init__(self):
        self.chart_height = 800
        self.chart_width = None  # use_container_widthを使用するためNone

    def create_price_chart(self, data, trades, strategy_params, buy_strategy):
        """株価チャートと指標を生成する"""
        fig = self._create_base_chart()
        self._add_candlestick(fig, data)
        self._add_technical_indicators(fig, data, strategy_params, buy_strategy)
        self._add_trade_markers(fig, trades)
        self._update_layout(fig)
        return fig

    def _create_base_chart(self):
        """基本チャートの作成"""
        return make_subplots(
            rows=3, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.05,
            row_heights=[0.6, 0.2, 0.2]
        )

    def _add_candlestick(self, fig, data):
        """ローソクチャートの追加"""
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

    def _add_technical_indicators(self, fig, data, strategy_params, buy_strategy):
        """技術指標の追加"""
        indicator_handlers = {
            "移動平均線クロスオーバー": self._add_moving_averages,
            "RSI": self._add_rsi,
            "MACD": self._add_macd,
            "ボリンジャーバンド": self._add_bollinger_bands
        }
        
        handler = indicator_handlers.get(buy_strategy)
        if handler:
            handler(fig, data, strategy_params)

    def _add_moving_averages(self, fig, data, params):
        """移動平均線の追加"""
        fast_ma = data['Close'].rolling(window=params['fast_period']).mean()
        slow_ma = data['Close'].rolling(window=params['slow_period']).mean()
        fig.add_trace(go.Scatter(x=data.index, y=fast_ma, 
                                name=f"短期MA({params['fast_period']})", 
                                line=dict(color='blue')), row=1, col=1)
        fig.add_trace(go.Scatter(x=data.index, y=slow_ma, 
                                name=f"長期MA({params['slow_period']})", 
                                line=dict(color='red')), row=1, col=1)

    def _add_rsi(self, fig, data, params):
        """RSIの追加"""
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

    def _add_macd(self, fig, data, params):
        """MACDの追加"""
        exp1 = data['Close'].ewm(span=params['fast_period'], adjust=False).mean()
        exp2 = data['Close'].ewm(span=params['slow_period'], adjust=False).mean()
        macd = exp1 - exp2
        signal = macd.ewm(span=params['signal_period'], adjust=False).mean()
        fig.add_trace(go.Scatter(x=data.index, y=macd, name='MACD', 
                                line=dict(color='blue')), row=2, col=1)
        fig.add_trace(go.Scatter(x=data.index, y=signal, name='Signal', 
                                line=dict(color='red')), row=2, col=1)

    def _add_bollinger_bands(self, fig, data, params):
        """ボリンジャーバンドの追加"""
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

    def _add_trade_markers(self, fig, trades):
        """取引マーカーの追加"""
        if trades is None or len(trades) == 0:
            return

        for _, trade in trades.iterrows():
            if trade['Size'] > 0:
                self._add_buy_marker(fig, trade)
            else:
                self._add_sell_marker(fig, trade)

    def _add_buy_marker(self, fig, trade):
        """買いマーカーの追加"""
        fig.add_trace(
            go.Scatter(
                x=[trade['EntryTime']],
                y=[trade['EntryPrice']],
                mode='markers',
                marker=dict(symbol='triangle-up', size=10, color='green'),
                name='買いシグナル'
            ),
            row=1, col=1
        )

    def _add_sell_marker(self, fig, trade):
        """売りマーカーの追加"""
        fig.add_trace(
            go.Scatter(
                x=[trade['ExitTime']],
                y=[trade['ExitPrice']],
                mode='markers',
                marker=dict(symbol='triangle-down', size=10, color='red'),
                name='売りシグナル'
            ),
            row=1, col=1
        )

    def _update_layout(self, fig):
        """チャートのレイアウト更新"""
        fig.update_layout(
            title='株価チャートと取引シグナル',
            xaxis_title='日付',
            yaxis_title='株価',
            height=self.chart_height,
            showlegend=True
        )

    def create_equity_chart(self, equity_curve):
        """エクイティカーブの作成"""
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=equity_curve.index,
            y=equity_curve.Equity,
            mode='lines',
            name='エクイティ'
        ))
        fig.update_layout(
            title="エクイティカーブ",
            xaxis_title="日付",
            yaxis_title="エクイティ",
            showlegend=True
        )
        return fig 