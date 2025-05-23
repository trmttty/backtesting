# 📈 ストックバックテストアプリ

## 🚀 概要
このアプリケーションは、株式市場のバックテストを簡単に行うことができるStreamlitベースのツールです。直感的なUIで、あなたの取引戦略を過去のデータで検証できます。

## ✨ 主な機能
- 📊 インタラクティブなチャート表示
- 🔄 カスタマイズ可能な取引戦略
- 📈 詳細なパフォーマンス分析
- 💰 初期資金の設定
- 📅 柔軟な期間設定
- 🏢 企業情報の表示
- 🛡️ リスク管理機能
  - 損切り（Stop Loss）
  - 利確（Take Profit）
  - トレイリングストップ（Trailing Stop）

## 🛠️ 技術スタック
- Python 3.x
- Streamlit
- backtesting
- yfinance
- pandas
- plotly

## 🚀 始め方

### 1. 環境構築
```bash
# リポジトリのクローン
git clone [リポジトリURL]

# 仮想環境の作成と有効化
python -m venv venv
source venv/bin/activate  # Linuxの場合
# または
.\venv\Scripts\activate  # Windowsの場合

# 依存パッケージのインストール
pip install -r requirements.txt
```

### 2. アプリケーションの起動
```bash
streamlit run main.py
```

## 📝 使い方
1. サイドバーから株式シンボルを選択
2. バックテスト期間を設定
3. 取引戦略とパラメータを選択
4. リスク管理設定（オプション）
   - 損切り：損失を制限するための設定
   - 利確：利益を確定するための設定
   - トレイリングストップ：利益を保護しながら上昇トレンドに乗るための設定
5. 「バックテスト実行」ボタンをクリック
6. 結果を確認！

## 🎯 バックテスト戦略
現在実装されている戦略：
- 単純移動平均線クロスオーバー
- RSI（相対力指数）
- ボリンジャーバンド
- MACD（移動平均収束拡散指標）

## 🛡️ リスク管理機能
### 損切り（Stop Loss）
- 損失を制限するための機能
- 設定したパーセンテージ（1-20%）で自動的にポジションをクローズ

### 利確（Take Profit）
- 利益を確定するための機能
- 設定したパーセンテージ（1-50%）で自動的にポジションをクローズ

### トレイリングストップ（Trailing Stop）
- 利益を保護しながら上昇トレンドに乗るための機能
- 価格が上昇すると、ストップ価格も自動的に上昇
- 価格がストップ価格を下回ると自動的にポジションをクローズ
- 設定したパーセンテージ（1-20%）で利益を保護

## 🤝 貢献
プルリクエストやイシューの作成は大歓迎です！以下の手順で貢献できます：

1. このリポジトリをフォーク
2. 新しいブランチを作成 (`git checkout -b feature/amazing-feature`)
3. 変更をコミット (`git commit -m 'Add some amazing feature'`)
4. ブランチにプッシュ (`git push origin feature/amazing-feature`)
5. プルリクエストを作成

## 📄 ライセンス
このプロジェクトはMITライセンスの下で公開されています。詳細は[LICENSE](LICENSE)ファイルを参照してください。

## ⚠️ 免責事項
このアプリケーションは投資助言を提供するものではありません。バックテストの結果は過去のデータに基づいており、将来のパフォーマンスを保証するものではありません。投資判断は自己責任で行ってください。 